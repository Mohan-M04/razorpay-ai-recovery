"""
Unit tests for the Retry Sequencer state machine.
"""

from datetime import datetime, timedelta
import pytest

from src.models import SubscriptionRecord, FailureReason, SubscriptionState, Channel
from src.db import Database
from src.audit import AuditLogger
from src.mock_gateway import MockRazorpayClient
from src.sequencer import RetrySequencer


@pytest.fixture
def env():
    db = Database(":memory:")
    audit = AuditLogger(db)
    gateway = MockRazorpayClient(seed=999)
    sequencer = RetrySequencer(db, audit, gateway)
    return db, audit, gateway, sequencer


def test_card_expired_prompts_update_without_auto_retry(env):
    db, audit, gateway, sequencer = env
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_test_card",
        customer_id="cust_01",
        amount=799.0,
        currency="INR",
        failure_reason=FailureReason.CARD_EXPIRED,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919811111111",
        language_pref="Hinglish",
    )
    db.save_subscription(sub)

    # Initial action
    sequencer.schedule_initial_action(sub, now)
    assert sub.card_update_token is not None
    assert sub.state == SubscriptionState.IN_RETRY_SCHEDULE

    # Automated retry should be blocked by safety gates
    success = sequencer.execute_auto_retry(sub, now + timedelta(hours=1))
    assert not success
    assert sub.attempt_count == 1  # Should not increment retry count


def test_insufficient_funds_schedules_48h_retry(env):
    db, audit, gateway, sequencer = env
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_test_funds",
        customer_id="cust_02",
        amount=1499.0,
        currency="INR",
        failure_reason=FailureReason.INSUFFICIENT_FUNDS,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919822222222",
        language_pref="Hinglish",
    )
    db.save_subscription(sub)

    sequencer.schedule_initial_action(sub, now)
    assert sub.next_action_at == now + timedelta(hours=48)
    assert sub.state == SubscriptionState.IN_RETRY_SCHEDULE


def test_gateway_timeout_schedules_30m_retry(env):
    db, audit, gateway, sequencer = env
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_test_timeout",
        customer_id="cust_03",
        amount=2999.0,
        currency="INR",
        failure_reason=FailureReason.GATEWAY_TIMEOUT,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919833333333",
        language_pref="English",
    )
    db.save_subscription(sub)

    sequencer.schedule_initial_action(sub, now)
    assert sub.next_action_at == now + timedelta(minutes=30)
    assert sub.state == SubscriptionState.IN_RETRY_SCHEDULE


def test_bank_declined_escalates_to_voice_immediately(env):
    db, audit, gateway, sequencer = env
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_test_declined",
        customer_id="cust_04",
        amount=4999.0,
        currency="INR",
        failure_reason=FailureReason.BANK_DECLINED,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919844444444",
        language_pref="Hinglish",
    )
    db.save_subscription(sub)

    sequencer.schedule_initial_action(sub, now)
    assert sub.state == SubscriptionState.VOICE_ESCALATED
