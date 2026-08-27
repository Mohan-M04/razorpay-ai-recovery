"""
Promise-to-Pay (PTP) tracker for managing customer pay-later commitments.
Tracks due dates, schedules follow-up reminders, and monitors conversion rates.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from src.db import Database
from src.models import PromiseToPay, SubscriptionRecord, SubscriptionState, Channel
from src.audit import AuditLogger


class PromiseToPayTracker:
    def __init__(self, db: Database, audit: AuditLogger):
        self.db = db
        self.audit = audit

    def record_promise(
        self,
        sub: SubscriptionRecord,
        due_date: datetime,
        current_time: datetime,
    ) -> PromiseToPay:
        """Records a customer's explicit commitment to pay by a specific date."""
        ptp_id = f"ptp_{sub.subscription_id}_{int(current_time.timestamp())}"
        ptp = PromiseToPay(
            ptp_id=ptp_id,
            subscription_id=sub.subscription_id,
            due_date=due_date,
            amount=sub.amount,
            created_at=current_time,
            status="pending",
            reminder_sent=False,
        )
        self.db.save_ptp(ptp)

        old_state = sub.state.value
        sub.state = SubscriptionState.PTP_ACTIVE
        sub.next_action_at = due_date
        self.db.save_subscription(sub)

        self.audit.log(
            subscription_id=sub.subscription_id,
            actor="PTP_TRACKER",
            action="RECORD_PROMISE_TO_PAY",
            reason=f"Customer committed to pay INR {sub.amount:.2f} by {due_date.strftime('%Y-%m-%d')}.",
            state_from=old_state,
            state_to=sub.state.value,
            metadata={"due_date": due_date.isoformat(), "amount": sub.amount},
        )
        return ptp

    def send_followup_reminder(
        self,
        sub: SubscriptionRecord,
        current_time: datetime,
    ) -> bool:
        """
        Sends a polite WhatsApp / SMS payment link reminder 24h prior to or on the due date.
        """
        ptp = self.db.get_ptp(sub.subscription_id)
        if not ptp or ptp.status != "pending" or ptp.reminder_sent:
            return False

        # If within 24h of due date
        time_to_due = (ptp.due_date - current_time).total_seconds()
        if time_to_due <= 86400:  # <= 24 hours
            ptp.reminder_sent = True
            self.db.save_ptp(ptp)

            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="PTP_TRACKER",
                action="SEND_PTP_REMINDER",
                reason=f"Sent friendly due-date reminder for promise due on {ptp.due_date.strftime('%Y-%m-%d')}.",
                state_from=sub.state.value,
                state_to=sub.state.value,
                metadata={"ptp_id": ptp.ptp_id, "amount": ptp.amount},
            )
            return True

        return False

    def evaluate_ptp_settlement(
        self,
        sub: SubscriptionRecord,
        payment_verified: bool,
        current_time: datetime,
    ) -> str:
        """
        Evaluates whether the promise converted or was broken.
        Returns: 'fulfilled' | 'broken' | 'pending'
        """
        ptp = self.db.get_ptp(sub.subscription_id)
        if not ptp:
            return "no_ptp"

        if payment_verified:
            ptp.status = "fulfilled"
            self.db.save_ptp(ptp)

            old_state = sub.state.value
            sub.state = SubscriptionState.RECOVERED
            sub.recovered_channel = Channel.PTP
            sub.recovered_at = current_time
            self.db.save_subscription(sub)

            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="PTP_TRACKER",
                action="PTP_FULFILLED",
                reason=f"Customer honored pay-later commitment. Recovered INR {sub.amount:.2f}.",
                state_from=old_state,
                state_to=sub.state.value,
                metadata={"recovered_amount": sub.amount, "channel": "ptp"},
            )
            return "fulfilled"

        # If past due date by more than 24h grace period without payment
        if current_time > (ptp.due_date + timedelta(hours=24)):
            ptp.status = "broken"
            self.db.save_ptp(ptp)

            old_state = sub.state.value
            sub.state = SubscriptionState.STOPPED
            self.db.save_subscription(sub)

            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="PTP_TRACKER",
                action="PTP_BROKEN",
                reason=f"Payment commitment of INR {sub.amount:.2f} due on {ptp.due_date.strftime('%Y-%m-%d')} lapsed.",
                state_from=old_state,
                state_to=sub.state.value,
                metadata={"ptp_id": ptp.ptp_id},
            )
            return "broken"

        return "pending"
