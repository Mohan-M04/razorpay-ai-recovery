"""
Deterministic safety gates and stopping rules for compliant recovery workflows.
Enforces non-negotiable constraints to prevent spamming and regulatory violations.
"""

from datetime import datetime, timedelta
from typing import Tuple

from src.models import SubscriptionRecord, SubscriptionState


class SafetyGates:
    MAX_TOTAL_RETRIES = 3
    MIN_CONTACT_COOLDOWN_HOURS = 24
    MAX_VOICE_ATTEMPTS = 2

    @classmethod
    def can_auto_retry(cls, sub: SubscriptionRecord) -> Tuple[bool, str]:
        """
        Validates whether an automated payment retry is permitted.
        Stopping rules:
        - Max 3 total retries
        - No retries if customer opted out or requested cancellation
        - No retries if already in terminal state
        """
        if sub.opted_out:
            return False, "HALT_OPT_OUT: Customer has opted out or requested cancellation."

        if sub.state in (SubscriptionState.RECOVERED, SubscriptionState.CANCELLED, SubscriptionState.STOPPED):
            return False, f"HALT_TERMINAL_STATE: Subscription is already in '{sub.state.value}' state."

        if sub.attempt_count >= cls.MAX_TOTAL_RETRIES:
            return False, f"HALT_MAX_RETRIES: Reached maximum limit of {cls.MAX_TOTAL_RETRIES} retries."

        if sub.failure_reason == "card_expired":
            return False, "HALT_CARD_EXPIRED: Automated retries disabled for expired cards without token update."

        return True, "ALLOWED: Safety criteria passed for automated retry."

    @classmethod
    def can_contact_customer(
        cls, sub: SubscriptionRecord, current_time: datetime
    ) -> Tuple[bool, str]:
        """
        Enforces communication safety rules:
        - Strict 24h cooldown between customer outreach touchpoints
        - Immediate hard stop on refusal / opt-out
        """
        if sub.opted_out:
            return False, "HALT_OPT_OUT: Customer explicitly refused or opted out. Never re-contact."

        if sub.state in (SubscriptionState.RECOVERED, SubscriptionState.CANCELLED, SubscriptionState.STOPPED):
            return False, f"HALT_TERMINAL_STATE: Subscription is in '{sub.state.value}' state."

        if sub.last_contact_at is not None:
            cooldown_delta = timedelta(hours=cls.MIN_CONTACT_COOLDOWN_HOURS)
            elapsed = current_time - sub.last_contact_at
            if elapsed < cooldown_delta:
                remaining_hours = (cooldown_delta - elapsed).total_seconds() / 3600.0
                return (
                    False,
                    f"HALT_COOLDOWN: 24h contact cooldown active ({remaining_hours:.1f} hours remaining).",
                )

        return True, "ALLOWED: Safety criteria passed for customer contact."

    @classmethod
    def can_voice_outreach(
        cls, sub: SubscriptionRecord, current_time: datetime
    ) -> Tuple[bool, str]:
        """
        Validates voice outreach:
        - Max 2 voice attempts per subscription
        - Enforces contact cooldown and opt-out rules
        """
        contact_allowed, reason = cls.can_contact_customer(sub, current_time)
        if not contact_allowed:
            return False, reason

        if sub.voice_attempts >= cls.MAX_VOICE_ATTEMPTS:
            return (
                False,
                f"HALT_VOICE_CAP: Maximum limit of {cls.MAX_VOICE_ATTEMPTS} voice attempts reached. Escalate to human team.",
            )

        return True, "ALLOWED: Voice outreach permitted."
