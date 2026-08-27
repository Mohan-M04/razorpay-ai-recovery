"""
Hinglish voice recovery agent executing STT -> LLM Reasoner -> TTS pipeline.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

from src.models import SubscriptionRecord, SubscriptionState, Channel
from src.db import Database
from src.audit import AuditLogger
from src.mock_gateway import MockRazorpayClient
from src.ptp_tracker import PromiseToPayTracker
from src.safety_gates import SafetyGates
from src.voice_agent.stt_tts import SpeechToText, TextToSpeech, AudioPayload
from src.voice_agent.hinglish_prompts import (
    generate_initial_greeting,
    detect_customer_intent,
    generate_dialogue_turn,
)


@dataclass
class VoiceCallResult:
    subscription_id: str
    customer_transcript: str
    agent_response_text: str
    detected_intent: str
    action_taken: str
    agent_audio: AudioPayload
    state_after: SubscriptionState
    ptp_due_date: Optional[datetime] = None


class VoiceRecoveryAgent:
    """
    Polite, professional Hinglish voice recovery assistant for Indian customers.
    """

    def __init__(
        self,
        db: Database,
        audit: AuditLogger,
        gateway: MockRazorpayClient,
        ptp_tracker: PromiseToPayTracker,
    ):
        self.db = db
        self.audit = audit
        self.gateway = gateway
        self.ptp_tracker = ptp_tracker
        self.stt = SpeechToText()
        self.tts = TextToSpeech()

    def start_call(
        self, sub: SubscriptionRecord, current_time: datetime
    ) -> Optional[AudioPayload]:
        """
        Validates safety gates and generates the initial warm opening greeting.
        """
        allowed, reason = SafetyGates.can_voice_outreach(sub, current_time)
        if not allowed:
            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="SAFETY_GATES",
                action="BLOCK_VOICE_OUTREACH",
                reason=reason,
                state_from=sub.state.value,
                state_to=sub.state.value,
            )
            return None

        # Increment voice touch counter & record contact timestamp
        sub.voice_attempts += 1
        sub.last_contact_at = current_time
        old_state = sub.state.value
        sub.state = SubscriptionState.VOICE_ESCALATED
        self.db.save_subscription(sub)

        greeting = generate_initial_greeting(
            customer_name=sub.customer_name,
            amount=sub.amount,
            merchant_name=sub.merchant_name,
            plan_name=sub.plan_name,
        )

        self.audit.log(
            subscription_id=sub.subscription_id,
            actor="VOICE_AGENT",
            action="DISPATCH_VOICE_GREETING",
            reason=f"Initiated voice recovery call (Attempt {sub.voice_attempts}).",
            state_from=old_state,
            state_to=sub.state.value,
            metadata={"greeting": greeting, "voice_attempt": sub.voice_attempts},
        )

        return self.tts.synthesize(greeting)

    def process_customer_turn(
        self,
        sub: SubscriptionRecord,
        customer_audio_or_text: str | AudioPayload,
        current_time: datetime,
    ) -> VoiceCallResult:
        """
        Executes STT -> Intent Classification -> Policy Enforcement -> Response Generation -> TTS.
        """
        # Step 1: STT Transcription
        transcript = self.stt.transcribe(customer_audio_or_text)

        # Step 2: Intent Classification
        intent, entities = detect_customer_intent(transcript)

        # Pre-create payment link for SMS / WhatsApp fulfillment
        plink = self.gateway.create_payment_link(
            subscription_id=sub.subscription_id,
            amount=sub.amount,
            customer_name=sub.customer_name,
            customer_contact=sub.customer_contact,
            description=f"Subscription renewal for {sub.merchant_name}",
        )

        # Step 3: Dialogue Generation
        response_text, ptp_date, action_code = generate_dialogue_turn(
            intent=intent,
            customer_name=sub.customer_name,
            amount=sub.amount,
            merchant_name=sub.merchant_name,
            payment_link_url=plink["short_url"],
            entities=entities,
            current_time=current_time,
        )

        old_state = sub.state.value

        # Step 4: Handle State Transitions & Business Logic
        if intent == "OPT_OUT_CANCEL":
            sub.opted_out = True
            sub.state = SubscriptionState.STOPPED
            self.db.save_subscription(sub)

            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="VOICE_AGENT",
                action="ENFORCE_HARD_STOP_OPT_OUT",
                reason="Customer requested cancellation or refused contact. Marked STOPPED.",
                state_from=old_state,
                state_to=sub.state.value,
            )

        elif intent == "PROMISE_TO_PAY" and ptp_date:
            self.ptp_tracker.record_promise(sub, ptp_date, current_time)

        elif intent == "UPDATE_CARD":
            sub.card_update_token = plink["id"]
            self.db.save_subscription(sub)
            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="VOICE_AGENT",
                action="SEND_CARD_UPDATE_LINK",
                reason="Dispatched self-serve card update link to customer WhatsApp/SMS.",
                state_from=old_state,
                state_to=sub.state.value,
                metadata={"payment_link": plink["short_url"]},
            )

        elif intent in ("RETRY_NOW", "REQUEST_LINK", "GENERAL_QUERY"):
            # Attempt immediate link / card capture
            # In simulation, we record link dispatch
            self.audit.log(
                subscription_id=sub.subscription_id,
                actor="VOICE_AGENT",
                action="SEND_RECOVERY_PAYMENT_LINK",
                reason="Sent 1-click Razorpay payment link to customer contact.",
                state_from=old_state,
                state_to=sub.state.value,
                metadata={"payment_link": plink["short_url"]},
            )

        # Step 5: TTS Synthesis
        audio_output = self.tts.synthesize(response_text)

        # Record voice interaction
        self.db.log_voice_interaction(
            interaction_id=f"vint_{sub.subscription_id}_{int(current_time.timestamp())}",
            subscription_id=sub.subscription_id,
            customer_statement=transcript,
            agent_response=response_text,
            detected_intent=intent,
            action_taken=action_code,
        )

        return VoiceCallResult(
            subscription_id=sub.subscription_id,
            customer_transcript=transcript,
            agent_response_text=response_text,
            detected_intent=intent,
            action_taken=action_code,
            agent_audio=audio_output,
            state_after=sub.state,
            ptp_due_date=ptp_date,
        )
