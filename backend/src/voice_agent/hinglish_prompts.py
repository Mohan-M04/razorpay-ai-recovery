"""
Hinglish dialogue generation, intent classification, and system prompt templates
for the 'RazorPay Recovery' voice assistant persona.
"""

import re
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional

SYSTEM_PROMPT = """
You are "RazorPay Recovery," a polite, professional AI voice assistant that helps
customers recover failed subscription payments. You speak warm, friendly Hinglish
(mix of Hindi and English) appropriate for an Indian customer.

Your job: explain that a payment failed, offer a clear solution (update card, retry
now, or pay later), and handle objections calmly. Never pressure, guilt, or harass.

Rules:
- Always start by greeting and stating the customer's name and the failed amount.
- Offer exactly one clear next step at a time.
- If the customer agrees to update their card, confirm and end with a thank-you.
- If the customer says they'll pay later, record a promise-to-pay with a due date
  and confirm the date back to them.
- If the customer refuses or asks to stop, immediately thank them, mark the case
  as STOPPED, and never re-contact. Do not argue.
- Keep responses under 3 sentences. End every call with a polite closing.
- Never invent payment details; only reference data provided to you.
"""


def detect_customer_intent(utterance: str) -> Tuple[str, Dict[str, Any]]:
    """
    Classifies customer spoken intent using robust pattern recognition.
    Returns (intent, extracted_entities).
    """
    text = utterance.lower()

    # Rule 1: Refusal / Opt-out / Stop / Cancel
    if any(k in text for k in [
        "cancel", "band karo", "stop", "call mat karo", "don't call",
        "nahi chahiye", "do not call", "mat karo", "refuse", "not interested"
    ]):
        return "OPT_OUT_CANCEL", {}

    # Rule 2: Promise to Pay / Pay later / Salary delay
    ptp_match = re.search(r"(\d+)\s*(din|day|tarikh|date)", text)
    if any(k in text for k in [
        "pay later", "baad me", "baad mein", "salary", "kal", "tomorrow",
        "2 din", "parso", "agle hafte", "next week", "tarikh", "1st"
    ]):
        days_ahead = 3
        if "kal" in text or "tomorrow" in text:
            days_ahead = 1
        elif "parso" in text or "2 din" in text:
            days_ahead = 2
        elif "agle hafte" in text or "next week" in text:
            days_ahead = 7
        elif ptp_match:
            try:
                days_ahead = max(1, min(14, int(ptp_match.group(1))))
            except ValueError:
                days_ahead = 3
        return "PROMISE_TO_PAY", {"days_ahead": days_ahead}

    # Rule 3: Card Update
    if any(k in text for k in [
        "update card", "card expire", "card change", "naya card", "new card",
        "dusra card", "card update"
    ]):
        return "UPDATE_CARD", {}

    # Rule 4: Send Link (WhatsApp / SMS)
    if any(k in text for k in [
        "whatsapp", "link bhej", "send link", "sms", "message kar do", "link de do"
    ]):
        return "REQUEST_LINK", {}

    # Rule 5: Retry now
    if any(k in text for k in [
        "retry", "abhi kar do", "pay now", "try again", "chalo retry karo",
        "dobara try", "abhi pay"
    ]):
        return "RETRY_NOW", {}

    # Rule 6: Ask for details
    if any(k in text for k in [
        "kaunsa", "what subscription", "kiska payment", "kisko", "details",
        "why failed", "kyu fail"
    ]):
        return "ASK_DETAILS", {}

    return "GENERAL_QUERY", {}


def generate_initial_greeting(
    customer_name: str,
    amount: float,
    merchant_name: str,
    plan_name: str,
) -> str:
    """
    Initial opening utterance adhering to:
    - Greet by name
    - State failed amount
    - Exactly 1 clear solution
    - Under 3 sentences
    """
    first_name = customer_name.split()[0]
    return (
        f"Namaste {first_name} ji! Main Razorpay se call kar raha hoon, aapke {merchant_name} "
        f"ke INR {amount:.0f} subscription payment mein bank ki taraf se issue aaya tha. "
        f"Kya hum ise abhi retry karein, ya aap WhatsApp par payment link lena chahenge?"
    )


def generate_dialogue_turn(
    intent: str,
    customer_name: str,
    amount: float,
    merchant_name: str,
    payment_link_url: str,
    entities: Dict[str, Any],
    current_time: datetime,
) -> Tuple[str, Optional[datetime], str]:
    """
    Generates dialogue adhering strictly to persona rules:
    - Under 3 sentences
    - Polite closing
    - Single next step
    - No harassment
    Returns (response_text, due_date_if_ptp, action_code).
    """
    first_name = customer_name.split()[0]

    if intent == "OPT_OUT_CANCEL":
        response = (
            f"Bilkul {first_name} ji, maine aapki request note kar li hai aur subscription stop kar diya hai. "
            f"Aapko aage se is baare mein koi call nahi aayegi. Razorpay se judne ke liye dhanyavaad!"
        )
        return response, None, "ACTION_OPT_OUT"

    elif intent == "PROMISE_TO_PAY":
        days = entities.get("days_ahead", 3)
        due_date = current_time + timedelta(days=days)
        formatted_date = due_date.strftime("%d %B")
        response = (
            f"Theek hai {first_name} ji, maine note kar liya hai ki aap {formatted_date} tak pay kar denge. "
            f"Hum us din aapko ek soft reminder link bhej denge. Aapka bahut-bahut dhanyavaad!"
        )
        return response, due_date, "ACTION_PTP"

    elif intent == "UPDATE_CARD":
        response = (
            f"Zaroor {first_name} ji, maine aapke registered number par card update ka secure Razorpay link bhej diya hai. "
            f"Aap wahan naya card add kar sakte hain taaki service uninterrupted rahe. Thank you so much!"
        )
        return response, None, "ACTION_CARD_UPDATE_LINK"

    elif intent == "REQUEST_LINK":
        response = (
            f"Ji bilkul {first_name} ji, maine turant aapke WhatsApp par payment link bhej diya hai: {payment_link_url}. "
            f"Aap UPI ya card se 1-minute mein pay kar sakte hain. Have a great day!"
        )
        return response, None, "ACTION_SEND_LINK"

    elif intent == "RETRY_NOW":
        response = (
            f"Bahut badhiya {first_name} ji, main turant payment retry initiate kar raha hoon. "
            f"Aapke pass bank se OTP aayega, kripya use verify kar lijiye. Thank you!"
        )
        return response, None, "ACTION_RETRY_NOW"

    elif intent == "ASK_DETAILS":
        response = (
            f"Ji {first_name} ji, yeh aapke {merchant_name} ke monthly subscription ke INR {amount:.0f} ka payment hai. "
            f"Kya aap chahenge ki main aapko WhatsApp par complete invoice aur payment link bhej doon?"
        )
        return response, None, "ACTION_EXPLAIN_AND_OFFER_LINK"

    else:
        response = (
            f"Samajh gaya {first_name} ji. Main aapki suvidha ke liye WhatsApp par link bhej deta hoon taaki aap araam se pay kar sakein. "
            f"Koi aur sahayata chahiye toh batayein, dhanyavaad!"
        )
        return response, None, "ACTION_SEND_LINK"
