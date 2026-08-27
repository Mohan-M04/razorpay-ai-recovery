"""
Unit tests for safety gates and stopping rules.
"""

from datetime import datetime, timedelta
import pytest

from src.models import SubscriptionRecord, FailureReason, SubscriptionState
from src.safety_gates import SafetyGates


def test_max_three_retries_stopping_rule():
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_safety_retry",
        customer_id="cust_01",
        amount=999.0,
        currency="INR",
        failure_reason=FailureReason.INSUFFICIENT_FUNDS,
        attempt_count=3,  # Already at 3
        last_attempt_at=now,
        customer_contact="+919812345678",
        language_pref="Hinglish",
    )

    can_retry, reason = SafetyGates.can_auto_retry(sub)
    assert not can_retry
    assert "HALT_MAX_RETRIES" in reason


def test_twenty_four_hour_contact_cooldown():
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_cooldown",
        customer_id="cust_02",
        amount=1499.0,
        currency="INR",
        failure_reason=FailureReason.BANK_DECLINED,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919812345678",
        language_pref="Hinglish",
        last_contact_at=now - timedelta(hours=10),  # Contacted 10h ago
    )

    can_contact, reason = SafetyGates.can_contact_customer(sub, current_time=now)
    assert not can_contact
    assert "HALT_COOLDOWN" in reason

    # After 25 hours, contact should be permitted
    can_contact_later, _ = SafetyGates.can_contact_customer(sub, current_time=now + timedelta(hours=15))
    assert can_contact_later


def test_max_voice_attempts():
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_voice_cap",
        customer_id="cust_03",
        amount=4999.0,
        currency="INR",
        failure_reason=FailureReason.BANK_DECLINED,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919812345678",
        language_pref="Hinglish",
        voice_attempts=2,  # Already called twice
        last_contact_at=now - timedelta(hours=30),  # Cooldown passed
    )

    can_voice, reason = SafetyGates.can_voice_outreach(sub, current_time=now)
    assert not can_voice
    assert "HALT_VOICE_CAP" in reason


def test_hard_stop_on_opt_out():
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_opt_out",
        customer_id="cust_04",
        amount=799.0,
        currency="INR",
        failure_reason=FailureReason.INSUFFICIENT_FUNDS,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919812345678",
        language_pref="Hinglish",
        opted_out=True,
    )

    can_retry, reason1 = SafetyGates.can_auto_retry(sub)
    assert not can_retry
    assert "HALT_OPT_OUT" in reason1

    can_contact, reason2 = SafetyGates.can_contact_customer(sub, now)
    assert not can_contact
    assert "HALT_OPT_OUT" in reason2
