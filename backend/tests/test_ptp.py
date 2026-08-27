"""
Unit tests for Promise-to-Pay (PTP) tracker.
"""

from datetime import datetime, timedelta
import pytest

from src.models import SubscriptionRecord, FailureReason, SubscriptionState, Channel
from src.db import Database
from src.audit import AuditLogger
from src.ptp_tracker import PromiseToPayTracker


@pytest.fixture
def ptp_env():
    db = Database(":memory:")
    audit = AuditLogger(db)
    tracker = PromiseToPayTracker(db, audit)
    return db, audit, tracker


def test_record_and_fulfill_promise(ptp_env):
    db, audit, tracker = ptp_env
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_ptp_01",
        customer_id="cust_ptp_01",
        amount=1999.0,
        currency="INR",
        failure_reason=FailureReason.INSUFFICIENT_FUNDS,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919811223344",
        language_pref="Hinglish",
        state=SubscriptionState.VOICE_ESCALATED,
    )
    db.save_subscription(sub)

    due_date = now + timedelta(days=3)
    ptp = tracker.record_promise(sub, due_date, now)

    assert ptp.status == "pending"
    assert sub.state == SubscriptionState.PTP_ACTIVE

    # Simulate payment fulfilled on due date
    result = tracker.evaluate_ptp_settlement(sub, payment_verified=True, current_time=due_date)
    assert result == "fulfilled"
    assert sub.state == SubscriptionState.RECOVERED
    assert sub.recovered_channel == Channel.PTP


def test_broken_promise(ptp_env):
    db, audit, tracker = ptp_env
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_ptp_02",
        customer_id="cust_ptp_02",
        amount=2499.0,
        currency="INR",
        failure_reason=FailureReason.INSUFFICIENT_FUNDS,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919811223344",
        language_pref="Hinglish",
        state=SubscriptionState.VOICE_ESCALATED,
    )
    db.save_subscription(sub)

    due_date = now + timedelta(days=2)
    tracker.record_promise(sub, due_date, now)

    # 48 hours after due date with no payment verified
    past_due = due_date + timedelta(hours=36)
    result = tracker.evaluate_ptp_settlement(sub, payment_verified=False, current_time=past_due)
    assert result == "broken"
    assert sub.state == SubscriptionState.STOPPED


def test_ptp_reminder_scheduling(ptp_env):
    db, audit, tracker = ptp_env
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_ptp_03",
        customer_id="cust_ptp_03",
        amount=499.0,
        currency="INR",
        failure_reason=FailureReason.INSUFFICIENT_FUNDS,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919811223344",
        language_pref="Hinglish",
        state=SubscriptionState.VOICE_ESCALATED,
    )
    db.save_subscription(sub)

    due_date = now + timedelta(days=2)
    tracker.record_promise(sub, due_date, now)

    # Check reminder 36 hours before due date (should not send yet)
    sent_early = tracker.send_followup_reminder(sub, now + timedelta(hours=12))
    assert not sent_early

    # Check reminder 12 hours before due date (within 24h window -> should send)
    sent_on_time = tracker.send_followup_reminder(sub, due_date - timedelta(hours=12))
    assert sent_on_time
