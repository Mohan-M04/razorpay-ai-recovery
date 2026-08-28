"""
Unit tests for Hinglish voice recovery agent, persona rules, and dialogue constraints.
"""

from datetime import datetime
import pytest

from src.models import SubscriptionRecord, FailureReason, SubscriptionState
from src.db import Database
from src.audit import AuditLogger
from src.mock_gateway import MockRazorpayClient
from src.ptp_tracker import PromiseToPayTracker
from src.voice_agent.pipeline import VoiceRecoveryAgent
from src.voice_agent.hinglish_prompts import (
    generate_initial_greeting,
    detect_customer_intent,
    generate_dialogue_turn,
)


@pytest.fixture
def voice_env():
    db = Database(":memory:")
    audit = AuditLogger(db)
    gateway = MockRazorpayClient(seed=42)
    ptp_tracker = PromiseToPayTracker(db, audit)
    agent = VoiceRecoveryAgent(db, audit, gateway, ptp_tracker)
    return db, audit, gateway, ptp_tracker, agent


def test_greeting_compliance():
    name = "Aarav Sharma"
    amount = 1499.0
    merchant = "CultFitness Live"
    plan = "Monthly Unlimited Pass"

    greeting = generate_initial_greeting(name, amount, merchant, plan)

    # 1. Starts with greeting & customer name
    assert "Aarav" in greeting
    # 2. States failed amount
    assert "1499" in greeting
    # 3. Mentions merchant
    assert "CultFitness Live" in greeting
    # 4. Under 3 sentences
    sentences = [s for s in greeting.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    assert len(sentences) <= 3


def test_opt_out_hard_stop(voice_env):
    db, audit, gateway, ptp_tracker, agent = voice_env
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_voice_opt",
        customer_id="cust_01",
        amount=999.0,
        currency="INR",
        failure_reason=FailureReason.BANK_DECLINED,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919811112222",
        language_pref="Hinglish",
        customer_name="Priya Patel",
    )
    db.save_subscription(sub)

    # Customer refuses
    utterance = "Mujhe subscription cancel karna hai, call mat karo"
    res = agent.process_customer_turn(sub, utterance, now)

    assert res.detected_intent == "OPT_OUT_CANCEL"
    assert sub.opted_out is True
    assert sub.state == SubscriptionState.STOPPED
    assert "dhanyavaad" in res.agent_response_text.lower() or "thank" in res.agent_response_text.lower()


def test_promise_to_pay_dialogue(voice_env):
    db, audit, gateway, ptp_tracker, agent = voice_env
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_voice_ptp",
        customer_id="cust_02",
        amount=2999.0,
        currency="INR",
        failure_reason=FailureReason.BANK_DECLINED,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919811113333",
        language_pref="Hinglish",
        customer_name="Vikram Iyer",
    )
    db.save_subscription(sub)

    utterance = "Haan main 2 din baad pay kar dunga salary aane par"
    res = agent.process_customer_turn(sub, utterance, now)

    assert res.detected_intent == "PROMISE_TO_PAY"
    assert res.ptp_due_date is not None
    assert sub.state == SubscriptionState.PTP_ACTIVE
    assert "dhanyavaad" in res.agent_response_text.lower() or "thank" in res.agent_response_text.lower()


def test_card_update_dialogue(voice_env):
    db, audit, gateway, ptp_tracker, agent = voice_env
    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_voice_card",
        customer_id="cust_03",
        amount=799.0,
        currency="INR",
        failure_reason=FailureReason.BANK_DECLINED,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact="+919811114444",
        language_pref="Hinglish",
        customer_name="Rohan Verma",
    )
    db.save_subscription(sub)

    utterance = "Card expire ho gaya hai, link bhej do naya card add karunga"
    res = agent.process_customer_turn(sub, utterance, now)

    assert res.detected_intent in ("UPDATE_CARD", "REQUEST_LINK")
    assert sub.card_update_token is not None or "link" in res.agent_response_text.lower()


def test_response_sentence_count_limit():
    import re
    for intent in ["OPT_OUT_CANCEL", "PROMISE_TO_PAY", "UPDATE_CARD", "REQUEST_LINK", "RETRY_NOW"]:
        resp, _, _ = generate_dialogue_turn(
            intent=intent,
            customer_name="Sneha Reddy",
            amount=1499.0,
            merchant_name="CultFitness",
            payment_link_url="https://rzp.io/i/test",
            entities={"days_ahead": 3},
            current_time=datetime(2026, 8, 27, 10, 0, 0),
        )
        # Strip URL before sentence splitting so domain dot is not counted as sentence boundary
        clean_text = re.sub(r"https?://\S+", "[LINK]", resp)
        sentences = [s for s in clean_text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        assert len(sentences) <= 3, f"Intent {intent} returned {len(sentences)} sentences (exceeds limit 3)"


def test_multilingual_support():
    for lang in ["Kannada", "Telugu", "Tamil", "English"]:
        greeting = generate_initial_greeting(
            customer_name="Prajwal Gowda",
            amount=1499.0,
            merchant_name="CultFitness",
            plan_name="Monthly Pass",
            language=lang,
        )
        assert len(greeting) > 10
        assert "Prajwal" in greeting

        # Test opt-out in each language
        resp, _, action = generate_dialogue_turn(
            intent="OPT_OUT_CANCEL",
            customer_name="Prajwal Gowda",
            amount=1499.0,
            merchant_name="CultFitness",
            language=lang,
        )
        assert action == "ACTION_OPT_OUT"
        assert len(resp) > 10
