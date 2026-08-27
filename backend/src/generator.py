"""
Seeded, reproducible synthetic data generator producing 200 failed subscription records.
"""

import random
from datetime import datetime, timedelta
from typing import List

from src.models import SubscriptionRecord, FailureReason, SubscriptionState

INDIAN_FIRST_NAMES = [
    "Aarav", "Aditi", "Rohan", "Priya", "Vikram", "Sneha", "Kabir", "Ananya",
    "Arjun", "Tanvi", "Nikhil", "Pooja", "Karthik", "Divya", "Manish", "Shreya",
    "Siddharth", "Meera", "Gaurav", "Neha", "Rahul", "Isha", "Deepak", "Ritu",
    "Abhishek", "Kavita", "Amit", "Swati", "Suresh", "Sunita", "Harsh", "Simran",
]

INDIAN_LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Iyer", "Reddy", "Nair", "Mehta", "Gupta",
    "Chatterjee", "Deshmukh", "Kulkarni", "Bose", "Menon", "Singh", "Chopra",
    "Rao", "Joshi", "Bhat", "Saxena", "Mishra", "Pandey", "Agarwal", "Mukherjee",
]

MERCHANTS_AND_PLANS = [
    ("StreamFlix India", "Premium 4K Ultra", 799.0),
    ("Klassmate Learning", "Annual EdTech Pro", 4999.0),
    ("CultFitness Live", "Monthly Unlimited Pass", 1499.0),
    ("CloudScale SaaS", "Developer Monthly Tier", 2999.0),
    ("DailyNews Premium", "Annual Digital All-Access", 999.0),
    ("B2B InvoiceDesk", "Enterprise Team License", 14999.0),
    ("MusicBeats VIP", "Family Hi-Fi Plan", 499.0),
]


def generate_subscription_batch(
    count: int = 200,
    seed: int = 42,
    base_time: datetime = None
) -> List[SubscriptionRecord]:
    """
    Generates a reproducible, seeded batch of failed subscription records.

    Distribution:
    - insufficient_funds: 35%
    - gateway_timeout: 25%
    - bank_declined: 25%
    - card_expired: 15%
    """
    rng = random.Random(seed)
    if base_time is None:
        base_time = datetime(2026, 8, 27, 12, 0, 0)

    failure_reasons = (
        [FailureReason.INSUFFICIENT_FUNDS] * 35
        + [FailureReason.GATEWAY_TIMEOUT] * 25
        + [FailureReason.BANK_DECLINED] * 25
        + [FailureReason.CARD_EXPIRED] * 15
    )

    languages = ["Hinglish", "Hinglish", "Hinglish", "Hindi", "English"]

    records: List[SubscriptionRecord] = []

    for i in range(count):
        sub_id = f"sub_{100000 + i}"
        cust_id = f"cust_{200000 + i}"
        first_name = rng.choice(INDIAN_FIRST_NAMES)
        last_name = rng.choice(INDIAN_LAST_NAMES)
        full_name = f"{first_name} {last_name}"

        merchant_name, plan_name, default_amount = rng.choice(MERCHANTS_AND_PLANS)
        
        # Jitter amount slightly around plan tiers
        amount = default_amount
        failure_reason = rng.choice(failure_reasons)
        lang = rng.choice(languages)

        phone_suffix = rng.randint(10000000, 99999999)
        customer_contact = f"+9198{phone_suffix}"

        # Stagger last attempt between 1 to 72 hours before base_time
        hours_ago = rng.randint(1, 72)
        last_attempt = base_time - timedelta(hours=hours_ago)

        # Initial attempt count (1 for fresh failure)
        attempt_count = 1

        record = SubscriptionRecord(
            subscription_id=sub_id,
            customer_id=cust_id,
            amount=amount,
            currency="INR",
            failure_reason=failure_reason,
            attempt_count=attempt_count,
            last_attempt_at=last_attempt,
            customer_contact=customer_contact,
            language_pref=lang,
            customer_name=full_name,
            merchant_name=merchant_name,
            plan_name=plan_name,
            state=SubscriptionState.PENDING,
            recovered_channel=None,
            recovered_at=None,
            voice_attempts=0,
            last_contact_at=None,
            next_action_at=None,
            card_update_token=None,
            opted_out=False,
        )
        records.append(record)

    return records
