"""
Retry Sequencer state machine coordinating failure-reason-based scheduling,
automated retries, card update prompts, and voice escalation.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from src.models import (
    SubscriptionRecord,
    SubscriptionState,
    FailureReason,
    Channel,
)
from src.db import Database
from src.audit import AuditLogger
from src.mock_gateway import MockRazorpayClient
from src.safety_gates import SafetyGates


class RetrySequencer:
    """
    Manages the lifecycle and state machine of failed subscriptions.
    Policies:
    - card_expired: Dispatches self-serve card update link; zero automated retries.
    - insufficient_funds: Schedules retry after 48h (funds replenishment).
    - gateway_timeout: Schedules fast retry after 30 minutes (switch recovery).
    - bank_declined: Immediately escalates to voice outreach / customer clarification.
    """

    def __init__(
        self,
        db: Database,
        audit: AuditLogger,
        gateway: MockRazorpayClient,
    ):
        self.db = db
        self.audit = audit
        self.gateway = gateway

    def schedule_initial_action(
        self, sub: SubscriptionRecord, current_time: datetime
    ) -> SubscriptionRecord:
        """
        Determines the next scheduled action based strictly on the failure reason.
        """
        old_state = sub.state.value

        if sub.failure_reason == FailureReason.CARD_EXPIRED:
            # Prompt card update immediately; no automated retries
            plink = self.gateway.create_payment_link(
                subscription_id=sub.subscription_id,
                amount=sub.amount,
                customer_name=sub.customer_name,
                customer_contact=sub.customer_contact,
                description=f"Update expired card for {sub.merchant_name}",
            )
            sub.card_update_token = plink["id"]
            sub.state = SubscriptionState.IN_RETRY_SCHEDULE
            sub.next_action_at = current_time + timedelta(hours=24)
            sub.last_contact_at = current_time

            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="SEQUENCER",
                action="PROMPT_CARD_UPDATE",
                reason="Card expired. Automated retries disabled; dispatched secure card update link.",
                state_from=old_state,
                state_to=sub.state.value,
                metadata={"payment_link": plink["short_url"]},
                timestamp=current_time,
            )

        elif sub.failure_reason == FailureReason.INSUFFICIENT_FUNDS:
            sub.state = SubscriptionState.IN_RETRY_SCHEDULE
            sub.next_action_at = current_time + timedelta(hours=48)

            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="SEQUENCER",
                action="SCHEDULE_RETRY_48H",
                reason="Insufficient funds. Scheduled automated retry after 48h backoff.",
                state_from=old_state,
                state_to=sub.state.value,
                metadata={"scheduled_for": sub.next_action_at.isoformat()},
                timestamp=current_time,
            )

        elif sub.failure_reason == FailureReason.GATEWAY_TIMEOUT:
            sub.state = SubscriptionState.IN_RETRY_SCHEDULE
            sub.next_action_at = current_time + timedelta(minutes=30)

            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="SEQUENCER",
                action="SCHEDULE_RETRY_30M",
                reason="Gateway timeout. Scheduled fast automated retry in 30 minutes.",
                state_from=old_state,
                state_to=sub.state.value,
                metadata={"scheduled_for": sub.next_action_at.isoformat()},
                timestamp=current_time,
            )

        elif sub.failure_reason == FailureReason.BANK_DECLINED:
            sub.state = SubscriptionState.VOICE_ESCALATED
            sub.next_action_at = current_time

            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="SEQUENCER",
                action="ESCALATE_TO_VOICE",
                reason="Bank declined mandate. Immediate escalation to voice recovery outreach.",
                state_from=old_state,
                state_to=sub.state.value,
                timestamp=current_time,
            )

        self.db.save_subscription(sub)
        return sub

    def execute_auto_retry(
        self, sub: SubscriptionRecord, current_time: datetime
    ) -> bool:
        """
        Attempts an automated charge via the mock payment gateway if safety rules pass.
        """
        can_retry, reason = SafetyGates.can_auto_retry(sub)
        if not can_retry:
            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="SAFETY_GATES",
                action="BLOCK_AUTO_RETRY",
                reason=reason,
                state_from=sub.state.value,
                state_to=sub.state.value,
                timestamp=current_time,
            )
            if "MAX_RETRIES" in reason:
                old_state = sub.state.value
                sub.state = SubscriptionState.VOICE_ESCALATED
                self.db.save_subscription(sub)
                self.audit.log(
                    subscription_id=sub.subscription_id,
                    actor="SEQUENCER",
                    action="ESCALATE_AFTER_MAX_RETRIES",
                    reason="Max automated retries exhausted. Escalating to voice recovery channel.",
                    state_from=old_state,
                    state_to=sub.state.value,
                    timestamp=current_time,
                )
            return False

        sub.attempt_count += 1
        sub.last_attempt_at = current_time

        result = self.gateway.charge_subscription(
            subscription_id=sub.subscription_id,
            amount=sub.amount,
            failure_reason=sub.failure_reason.value,
            attempt_number=sub.attempt_count,
        )

        old_state = sub.state.value

        if result.get("success"):
            sub.state = SubscriptionState.RECOVERED
            sub.recovered_channel = Channel.AUTO_RETRY
            sub.recovered_at = current_time
            self.db.save_subscription(sub)

            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="RAZORPAY_GATEWAY",
                action="PAYMENT_CAPTURED",
                reason=f"Automated retry #{sub.attempt_count} succeeded. Recovered INR {sub.amount:.2f}.",
                state_from=old_state,
                state_to=sub.state.value,
                metadata={"payment_id": result.get("payment_id"), "channel": "auto_retry"},
                timestamp=current_time,
            )
            return True
        else:
            # Failed retry
            if sub.attempt_count >= SafetyGates.MAX_TOTAL_RETRIES:
                sub.state = SubscriptionState.VOICE_ESCALATED
                self.audit.log(
                    subscription_id=sub.subscription_id,
                    actor="RAZORPAY_GATEWAY",
                    action="PAYMENT_FAILED_ESCALATE_VOICE",
                    reason=f"Retry #{sub.attempt_count} failed ({result.get('error_code')}). Max retries reached; escalating to voice.",
                    state_from=old_state,
                    state_to=sub.state.value,
                    metadata={"error": result.get("error_description")},
                    timestamp=current_time,
                )
            else:
                # Schedule next retry with 24h backoff
                sub.next_action_at = current_time + timedelta(hours=24)
                self.audit.log(
                    subscription_id=sub.subscription_id,
                    actor="RAZORPAY_GATEWAY",
                    action="PAYMENT_RETRY_FAILED",
                    reason=f"Retry #{sub.attempt_count} failed ({result.get('error_code')}). Rescheduled in 24h.",
                    state_from=old_state,
                    state_to=sub.state.value,
                    metadata={"error": result.get("error_description")},
                    timestamp=current_time,
                )
            self.db.save_subscription(sub)
            return False
