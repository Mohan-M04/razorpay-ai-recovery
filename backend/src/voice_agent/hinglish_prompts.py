"""
Multilingual dialogue generation, intent classification, and system prompt templates
for the 'RazorPay Recovery' voice assistant persona.
Supports Hinglish, Kannada (ಕನ್ನಡ), Telugu (తెలుగు), Tamil (தமிழ்), and English.
"""

import re
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional

SYSTEM_PROMPT = """
You are "RazorPay Recovery," a polite, professional AI voice assistant that helps
customers recover failed subscription payments across Indian languages (Hinglish,
Kannada, Telugu, Tamil, and English).

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
    Classifies customer spoken intent using robust multilingual pattern recognition
    across Hinglish, Kannada, Telugu, Tamil, and English.
    Returns (intent, extracted_entities).
    """
    text = utterance.lower()

    # Rule 1: Refusal / Opt-out / Stop / Cancel (All languages)
    if any(k in text for k in [
        # English / Hinglish
        "cancel", "band karo", "stop", "call mat karo", "don't call",
        "nahi chahiye", "do not call", "mat karo", "refuse", "not interested",
        # Kannada (ಕನ್ನಡ)
        "beda", "bekagilla", "call madbedi", "cancel madi", "stop madi", "bedave beda",
        # Telugu (తెలుగు)
        "vaddu", "kavalsina ledu", "call cheyyavaddhu", "cancel cheyandi", "stop cheyandi", "voddhu",
        # Tamil (தமிழ்)
        "vendaam", "thevaiyillai", "call pannadheenga", "cancel pannunga", "stop pannunga", "vendam"
    ]):
        return "OPT_OUT_CANCEL", {}

    # Rule 2: Promise to Pay / Pay later / Salary delay
    ptp_match = re.search(r"(\d+)\s*(din|day|tarikh|date|dina|rojulu|naal)", text)
    if any(k in text for k in [
        # Hinglish / English
        "pay later", "baad me", "baad mein", "salary", "kal", "tomorrow",
        "2 din", "parso", "agle hafte", "next week", "tarikh", "1st",
        # Kannada
        "naale", "erad dina", "salary bandhmele", "aamele pay", "pay madthini", "matte kodthini",
        # Telugu
        "repu", "rendu rojulu", "salary vachaka", "tarvatha pay", "pay chestha", "pay chesthanu",
        # Tamil
        "naalaiku", "rendu naal", "salary vandha", "aprom pay", "pay panren", "koodiya seekiram"
    ]):
        days_ahead = 3
        if any(k in text for k in ["kal", "tomorrow", "naale", "repu", "naalaiku"]):
            days_ahead = 1
        elif any(k in text for k in ["parso", "2 din", "erad dina", "rendu rojulu", "rendu naal"]):
            days_ahead = 2
        elif any(k in text for k in ["agle hafte", "next week"]):
            days_ahead = 7
        elif ptp_match:
            try:
                days_ahead = max(1, min(14, int(ptp_match.group(1))))
            except ValueError:
                days_ahead = 3
        return "PROMISE_TO_PAY", {"days_ahead": days_ahead}

    # Rule 3: Update card
    if any(k in text for k in [
        "card expire", "update card", "naya card", "change card", "new card", "expiry",
        "card update", "hosa card", "kotha card", "pudhu card"
    ]):
        return "UPDATE_CARD", {}

    # Rule 4: Send payment link / WhatsApp
    if any(k in text for k in [
        "link", "whatsapp", "bhej do", "send link", "upi", "sms",
        "kalsi", "pampandi", "anupunga", "send madi", "pampinchandi"
    ]):
        return "REQUEST_LINK", {}

    # Rule 5: Retry now
    if any(k in text for k in [
        "retry", "abhi try", "try now", "fir se", "try again",
        "ega retry", "ippude retry", "ippove retry"
    ]):
        return "RETRY_NOW", {}

    # Rule 6: Inquire about subscription details
    if any(k in text for k in ["kaunsa", "details", "kya hai", "what is this", "enu idhu", "enti idhi", "enna idhu"]):
        return "ASK_DETAILS", {}

    return "GENERAL_QUERY", {}


def generate_initial_greeting(
    customer_name: str,
    amount: float,
    merchant_name: str,
    plan_name: str,
    language: str = "Hinglish",
) -> str:
    """
    Generates the opening greeting customized to the customer's preferred language.
    Strictly follows persona rules:
    - Greets customer by name
    - Mentions failed amount and merchant
    - Offers single next step
    - Under 3 sentences
    """
    first_name = customer_name.split()[0]
    lang = language.lower()

    if "kannada" in lang:
        return (
            f"Namaskara {first_name} avare! Naanu Razorpay inda call maadtha idhini, "
            f"nimma {merchant_name} subscription INR {amount:.0f} payment bank kadeyinda issue aagide. "
            f"Eega retry maadla, athava WhatsApp nalli payment link kalsla?"
        )
    elif "telugu" in lang:
        return (
            f"Namaskaram {first_name} garu! Nenu Razorpay nunchi call chesthunnanu, "
            f"mee {merchant_name} subscription INR {amount:.0f} payment bank vaipu fail ayyindi. "
            f"Ippude retry cheddhaama, leda WhatsApp lo payment link pampinchamantara?"
        )
    elif "tamil" in lang:
        return (
            f"Vanakkam {first_name} avargale! Naan Razorpay-ilirundhu call panren, "
            f"ungal {merchant_name} subscription INR {amount:.0f} payment bank-la fail aayiduchu. "
            f"Ippove retry pannalama, illa WhatsApp-la payment link anupattuma?"
        )
    elif "english" in lang:
        return (
            f"Hello {first_name}! This is Razorpay calling regarding your {merchant_name} subscription payment of INR {amount:.0f} that failed recently. "
            f"Would you like us to retry the debit now, or send a secure payment link on WhatsApp?"
        )
    else:  # Default Hinglish
        return (
            f"Namaste {first_name} ji! Main Razorpay se call kar raha hoon, "
            f"aapke {merchant_name} ke INR {amount:.0f} subscription payment mein bank ki taraf se issue aaya tha. "
            f"Kya hum ise abhi retry karein, ya aap WhatsApp par payment link lena chahenge?"
        )


def generate_dialogue_turn(
    intent: str,
    customer_name: str,
    amount: float,
    merchant_name: str,
    payment_link_url: str = "https://rzp.io/i/recover",
    entities: Optional[Dict[str, Any]] = None,
    current_time: Optional[datetime] = None,
    language: str = "Hinglish",
) -> Tuple[str, Optional[datetime], str]:
    """
    Generates dialogue adhering strictly to persona rules:
    - Under 3 sentences
    - Polite closing
    - Single next step
    - No harassment
    - Localized in customer's preferred language
    Returns (response_text, due_date_if_ptp, action_code).
    """
    if entities is None:
        entities = {}
    if current_time is None:
        current_time = datetime.now()

    first_name = customer_name.split()[0]
    lang = language.lower()

    # -------------------------------------------------------------
    # 1. OPT-OUT / CANCEL (Immediate polite stop, never argue)
    # -------------------------------------------------------------
    if intent == "OPT_OUT_CANCEL":
        if "kannada" in lang:
            response = (
                f"Kanditha {first_name} avare, naanu nimma request note maadidini mattu subscription stop maadidini. "
                f"Mundhe nimge call barolla. Razorpay thalidadhakkagi dhanyavaadagalu!"
            )
        elif "telugu" in lang:
            response = (
                f"Tappakunda {first_name} garu, mee request note chesi subscription stop chesamu. "
                f"Inka meeku calls raavu. Razorpay tho unnanthuku dhanyavaadamulu!"
            )
        elif "tamil" in lang:
            response = (
                f"Kandippa {first_name} avargale, ungal request note panni subscription stop panniyaachu. "
                f"Ini call varaadhu. Razorpay-udan irundhadharku mikka nandri!"
            )
        elif "english" in lang:
            response = (
                f"Certainly {first_name}, I have noted your request and stopped the subscription. "
                f"You will not receive further calls. Thank you for choosing Razorpay!"
            )
        else:  # Hinglish
            response = (
                f"Bilkul {first_name} ji, maine aapki request note kar li hai aur subscription stop kar diya hai. "
                f"Aapko aage se is baare mein koi call nahi aayegi. Razorpay se judne ke liye dhanyavaad!"
            )
        return response, None, "ACTION_OPT_OUT"

    # -------------------------------------------------------------
    # 2. PROMISE TO PAY (Confirm date back, schedule soft reminder)
    # -------------------------------------------------------------
    elif intent == "PROMISE_TO_PAY":
        days = entities.get("days_ahead", 3)
        due_date = current_time + timedelta(days=days)
        formatted_date = due_date.strftime("%d %B")

        if "kannada" in lang:
            response = (
                f"Sarva {first_name} avare, neevu {formatted_date} olage pay maadthira antha note maadidini. "
                f"Aa dina naavu soft reminder link kalsuthivi. Thumba dhanyavaadagalu!"
            )
        elif "telugu" in lang:
            response = (
                f"Sare {first_name} garu, meeru {formatted_date} lopu pay chestharani note chesamu. "
                f"Aa roju meeku reminder link pampisthamu. Chala dhanyavaadamulu!"
            )
        elif "tamil" in lang:
            response = (
                f"Sari {first_name} avargale, neenga {formatted_date} kulla pay panniduveenga nu note panniyachu. "
                f"Aniku oru soft reminder link anupuvom. Mikka nandri!"
            )
        elif "english" in lang:
            response = (
                f"Understood {first_name}, I have recorded your commitment to pay by {formatted_date}. "
                f"We will send a gentle reminder link on that date. Thank you very much!"
            )
        else:  # Hinglish
            response = (
                f"Theek hai {first_name} ji, maine note kar liya hai ki aap {formatted_date} tak pay kar denge. "
                f"Hum us din aapko ek soft reminder link bhej denge. Aapka bahut-bahut dhanyavaad!"
            )
        return response, due_date, "ACTION_PTP"

    # -------------------------------------------------------------
    # 3. UPDATE CARD
    # -------------------------------------------------------------
    elif intent == "UPDATE_CARD":
        if "kannada" in lang:
            response = (
                f"Kanditha {first_name} avare, nimma number ge secure Razorpay card update link kalsidini. "
                f"Alli naya card add maadbahudu. Thumba dhanyavaadagalu!"
            )
        elif "telugu" in lang:
            response = (
                f"Tappakunda {first_name} garu, mee number ki secure Razorpay card update link pampinchanu. "
                f"Akkada kotha card add cheyavachu. Chala dhanyavaadamulu!"
            )
        elif "tamil" in lang:
            response = (
                f"Kandippa {first_name} avargale, ungal number-kku secure Razorpay card update link anupitten. "
                f"Anga pudhu card add pannikkalaam. Mikka nandri!"
            )
        elif "english" in lang:
            response = (
                f"Certainly {first_name}, I have dispatched a secure card update link to your registered mobile. "
                f"You can add your new card there to keep services active. Thank you!"
            )
        else:  # Hinglish
            response = (
                f"Zaroor {first_name} ji, maine aapke registered number par card update ka secure Razorpay link bhej diya hai. "
                f"Aap wahan naya card add kar sakte hain taaki service uninterrupted rahe. Thank you so much!"
            )
        return response, None, "ACTION_CARD_UPDATE_LINK"

    # -------------------------------------------------------------
    # 4. REQUEST LINK / WHATSAPP
    # -------------------------------------------------------------
    elif intent == "REQUEST_LINK":
        if "kannada" in lang:
            response = (
                f"Kanditha {first_name} avare, nimma WhatsApp ge payment link kalsidini: {payment_link_url}. "
                f"Neevu UPI athava card moolaka 1-minute nalli pay maadbahudu. Have a great day!"
            )
        elif "telugu" in lang:
            response = (
                f"Tappakunda {first_name} garu, mee WhatsApp ki payment link pampinchanu: {payment_link_url}. "
                f"Meeru 1-minute lo UPI leda card tho pay cheyavachu. Have a great day!"
            )
        elif "tamil" in lang:
            response = (
                f"Kandippa {first_name} avargale, ungal WhatsApp-kku payment link anupitten: {payment_link_url}. "
                f"Neenga 1-minute la UPI illa card moolam pay pannalaam. Have a great day!"
            )
        elif "english" in lang:
            response = (
                f"Certainly {first_name}, I have dispatched the payment link to your WhatsApp: {payment_link_url}. "
                f"You can complete payment in under a minute via UPI or card. Have a wonderful day!"
            )
        else:  # Hinglish
            response = (
                f"Ji bilkul {first_name} ji, maine turant aapke WhatsApp par payment link bhej diya hai: {payment_link_url}. "
                f"Aap UPI ya card se 1-minute mein pay kar sakte hain. Have a great day!"
            )
        return response, None, "ACTION_SEND_LINK"

    # -------------------------------------------------------------
    # 5. RETRY NOW
    # -------------------------------------------------------------
    elif intent == "RETRY_NOW":
        if "kannada" in lang:
            response = (
                f"Uttama {first_name} avare, naanu eegale payment retry initiate maadtha idhini. "
                f"Nimma bank inda OTP baruththe, dayavittu verify maadi. Thank you!"
            )
        elif "telugu" in lang:
            response = (
                f"Chala manchidi {first_name} garu, nenu ventane payment retry initiate chesthunnanu. "
                f"Mee bank nunchi OTP vasthundi, dayachesi verify cheyandi. Thank you!"
            )
        elif "tamil" in lang:
            response = (
                f"Romba nalladhu {first_name} avargale, naan ippove payment retry initiate panren. "
                f"Ungal bank-la irundhu OTP varum, adhaye verify pannunga. Thank you!"
            )
        elif "english" in lang:
            response = (
                f"Wonderful {first_name}, I am initiating the payment retry right away. "
                f"Please verify the bank OTP on your device when prompted. Thank you!"
            )
        else:  # Hinglish
            response = (
                f"Bahut badhiya {first_name} ji, main turant payment retry initiate kar raha hoon. "
                f"Aapke pass bank se OTP aayega, kripya use verify kar lijiye. Thank you!"
            )
        return response, None, "ACTION_RETRY_NOW"

    # -------------------------------------------------------------
    # 6. ASK DETAILS / FALLBACK
    # -------------------------------------------------------------
    elif intent == "ASK_DETAILS":
        if "kannada" in lang:
            response = (
                f"Haudhu {first_name} avare, idhu nimma {merchant_name} subscription INR {amount:.0f} payment. "
                f"Naanu nimma WhatsApp ge invoice mattu link kalsla?"
            )
        elif "telugu" in lang:
            response = (
                f"Avunu {first_name} garu, idi mee {merchant_name} subscription INR {amount:.0f} payment. "
                f"Mee WhatsApp ki invoice mariyu link pampinchamantara?"
            )
        elif "tamil" in lang:
            response = (
                f"Aam {first_name} avargale, idhu ungal {merchant_name} subscription INR {amount:.0f} payment. "
                f"Ungal WhatsApp-kku invoice mattrum link anupattuma?"
            )
        else:
            response = (
                f"Ji {first_name} ji, yeh aapke {merchant_name} ke monthly subscription ke INR {amount:.0f} ka payment hai. "
                f"Kya aap chahenge ki main aapko WhatsApp par complete invoice aur payment link bhej doon?"
            )
        return response, None, "ACTION_EXPLAIN_AND_OFFER_LINK"

    else:
        if "kannada" in lang:
            response = (
                f"Artha aayithu {first_name} avare, nimma anukoolakkagi WhatsApp nalli payment link kalsidini. "
                f"Bere enadru sahayaviddare thilisi, thumba dhanyavaadagalu!"
            )
        elif "telugu" in lang:
            response = (
                f"Ardhamaindi {first_name} garu, mee soukaryam kosam WhatsApp lo payment link pampinchanu. "
                f"Inkemaina sahayame kavala, chala dhanyavaadamulu!"
            )
        elif "tamil" in lang:
            response = (
                f"Purinjadhu {first_name} avargale, ungal vasadhikaga WhatsApp-la link anupitten. "
                f"Vera edhaavadhu help thevaiyaa, mikka nandri!"
            )
        else:
            response = (
                f"Samajh gaya {first_name} ji. Main aapki suvidha ke liye WhatsApp par link bhej deta hoon taaki aap araam se pay kar sakein. "
                f"Koi aur sahayata chahiye toh batayein, dhanyavaad!"
            )
        return response, None, "ACTION_SEND_LINK"
