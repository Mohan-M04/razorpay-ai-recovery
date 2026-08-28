"""
Interactive CLI for Razorpay AI Subscription Revenue Recovery.
Run benchmarks or experience the Hinglish voice assistant interactively.
"""

import sys
from datetime import datetime
from src.evaluation import EvaluationHarness
from src.generator import generate_subscription_batch
from src.models import SubscriptionRecord, FailureReason, SubscriptionState
from src.voice_agent.pipeline import VoiceRecoveryAgent
from src.ptp_tracker import PromiseToPayTracker
from src.mock_gateway import MockRazorpayClient
from src.audit import AuditLogger
from src.db import Database


def interactive_voice_demo():
    print("\n" + "=" * 70)
    print("   RAZORPAY RECOVERY: INTERACTIVE HINGLISH VOICE ASSISTANT DEMO")
    print("=" * 70)
    print("Scenario: A recurring payment of INR 1,499 for CultFitness Live failed.")
    print("Type your response in Hinglish or English (or 'exit' to quit).\n")

    db = Database(":memory:")
    audit = AuditLogger(db)
    gateway = MockRazorpayClient(seed=42)
    ptp_tracker = PromiseToPayTracker(db, audit)
    agent = VoiceRecoveryAgent(db, audit, gateway, ptp_tracker)

    print("\nSelect Language for Voice Outreach Demo:")
    print("1. Hinglish (Default)")
    print("2. Kannada (ಕನ್ನಡ)")
    print("3. Telugu (తెలుగు)")
    print("4. Tamil (தமிழ்)")
    print("5. English")
    lang_choice = input("Select Language (1-5, default 1): ").strip()
    lang_map = {
        "1": "Hinglish",
        "2": "Kannada",
        "3": "Telugu",
        "4": "Tamil",
        "5": "English",
    }
    selected_lang = lang_map.get(lang_choice, "Hinglish")

    names = {
        "Kannada": ("Prajwal Gowda", "+919876543211"),
        "Telugu": ("Venkat Reddy", "+919876543212"),
        "Tamil": ("Karthik Subramanian", "+919876543213"),
        "English": ("David Miller", "+919876543214"),
        "Hinglish": ("Aarav Sharma", "+919876543210"),
    }
    cust_name, cust_contact = names.get(selected_lang, ("Aarav Sharma", "+919876543210"))

    now = datetime(2026, 8, 27, 10, 0, 0)
    sub = SubscriptionRecord(
        subscription_id="sub_live_demo",
        customer_id="cust_demo_01",
        amount=1499.0,
        currency="INR",
        failure_reason=FailureReason.BANK_DECLINED,
        attempt_count=1,
        last_attempt_at=now,
        customer_contact=cust_contact,
        language_pref=selected_lang,
        customer_name=cust_name,
        merchant_name="CultFitness Live",
        plan_name="Monthly Unlimited Pass",
        state=SubscriptionState.VOICE_ESCALATED,
    )
    db.save_subscription(sub)

    audio = agent.start_call(sub, now)
    greeting = audit.get_logs(sub.subscription_id)[-1].metadata.get("greeting", "")
    print(f"\n🤖 [RazorPay Recovery ({selected_lang})]: {greeting}\n")

    while True:
        while True:
            try:
                user_input = input("👤 [Customer]: ").strip()
            except (KeyboardInterrupt, EOFError):
                return

            if not user_input or user_input.lower() in ("exit", "quit", "q"):
                print("\nCall ended.")
                return

            now = datetime.now()
            result = agent.process_customer_turn(sub, user_input, now)
            print(f"\n🤖 [RazorPay Recovery]: {result.agent_response_text}")
            print(f"   [Telemetry]: Intent={result.detected_intent} | Action={result.action_taken} | State={result.state_after.value}\n")

            if result.detected_intent == "OPT_OUT_CANCEL":
                print("🛑 [Stopping Rule Triggered]: Case marked STOPPED. Never re-contact.")
                break
            elif result.detected_intent == "PROMISE_TO_PAY":
                print(f"📅 [PTP Recorded]: Due date confirmed for {result.ptp_due_date.strftime('%d %B %Y')}. Automated reminder queued.")
                break
            elif result.action_taken in ("ACTION_CARD_UPDATE_LINK", "ACTION_SEND_LINK", "ACTION_RETRY_NOW"):
                print("✅ [Resolution Action Executed]: Payment link dispatched via Razorpay API. Sequence complete.")
                break

        print("-" * 70)
        cont = input("\n👉 Test another customer scenario? (Press Enter to continue, or 'q' to quit): ").strip()
        if cont.lower() in ("q", "quit", "exit", "n", "no"):
            print("Thanks for testing RazorPay Recovery!")
            break
        print(f"\n🤖 [RazorPay Recovery]: {greeting}\n")


def main():
    print("\nSelect an option:")
    print("1. Run 200-record benchmark evaluation harness")
    print("2. Interactive Hinglish voice assistant demo")
    choice = input("Enter choice (1/2): ").strip()

    if choice == "1":
        harness = EvaluationHarness(seed=42)
        rep = harness.run_benchmark(count=200)
        harness.print_report(rep)
    elif choice == "2":
        interactive_voice_demo()
    else:
        print("Invalid option. Exiting.")


if __name__ == "__main__":
    main()
