"""
Deterministic, seeded mock payment gateway client simulating Razorpay Subscription & Payment APIs.
"""

import hashlib
import random
from typing import Dict, Any


class MockRazorpayClient:
    """
    Simulates Razorpay API endpoints for subscriptions, direct debits, and payment links.
    Guarantees deterministic behavior for testing based on seeded pseudo-random logic.
    """

    def __init__(self, seed: int = 1337):
        self.seed = seed
        self._rng = random.Random(seed)
        self.payment_links: Dict[str, Dict[str, Any]] = {}
        self.updated_cards: Dict[str, str] = {}

    def charge_subscription(
        self,
        subscription_id: str,
        amount: float,
        failure_reason: str,
        attempt_number: int,
    ) -> Dict[str, Any]:
        """
        Simulates an automated subscription charge retry.
        Deterministic probability:
        - gateway_timeout retry -> 82% success (transient switch issue resolved)
        - insufficient_funds retry after 48h -> 55% success (salary / funds replenished)
        - bank_declined direct retry -> 12% success (usually needs customer authorization)
        - card_expired direct retry -> 0% success (expired card cannot be charged)
        """
        # Create deterministic hash-based seed per subscription + attempt
        token = f"{self.seed}:{subscription_id}:{attempt_number}:{failure_reason}"
        hash_val = int(hashlib.sha256(token.encode()).hexdigest(), 16)
        prob = (hash_val % 10000) / 10000.0

        if failure_reason == "card_expired":
            # Direct retry on expired card always fails unless card token was updated
            if subscription_id in self.updated_cards:
                return {
                    "success": True,
                    "payment_id": f"pay_{hash_val % 10000000}",
                    "status": "captured",
                    "amount": amount,
                    "message": "Payment captured with updated card token",
                }
            return {
                "success": False,
                "error_code": "BAD_REQUEST_ERROR",
                "error_description": "Card has expired. Update payment method.",
            }

        elif failure_reason == "gateway_timeout":
            if prob < 0.82:
                return {
                    "success": True,
                    "payment_id": f"pay_{hash_val % 10000000}",
                    "status": "captured",
                    "amount": amount,
                    "message": "Payment captured successfully on secondary switch",
                }
            return {
                "success": False,
                "error_code": "GATEWAY_TIMEOUT",
                "error_description": "Acquiring bank timeout. Retry scheduled.",
            }

        elif failure_reason == "insufficient_funds":
            if prob < 0.55:
                return {
                    "success": True,
                    "payment_id": f"pay_{hash_val % 10000000}",
                    "status": "captured",
                    "amount": amount,
                    "message": "Account balance verified. Mandate executed.",
                }
            return {
                "success": False,
                "error_code": "INSUFFICIENT_FUNDS",
                "error_description": "Debit declined by customer bank due to low balance.",
            }

        elif failure_reason == "bank_declined":
            if prob < 0.12:
                return {
                    "success": True,
                    "payment_id": f"pay_{hash_val % 10000000}",
                    "status": "captured",
                    "amount": amount,
                    "message": "Bank approved mandate authorization.",
                }
            return {
                "success": False,
                "error_code": "BANK_DECLINED",
                "error_description": "Card issuer declined recurring transaction.",
            }

        return {"success": False, "error_code": "UNKNOWN_ERROR"}

    def create_payment_link(
        self,
        subscription_id: str,
        amount: float,
        customer_name: str,
        customer_contact: str,
        description: str,
    ) -> Dict[str, Any]:
        """Simulates Razorpay Payment Links API (/v1/payment_links)."""
        link_id = f"plink_{hashlib.md5(f'{subscription_id}:{amount}'.encode()).hexdigest()[:10]}"
        short_url = f"https://rzp.io/i/{link_id[6:]}"

        payload = {
            "id": link_id,
            "short_url": short_url,
            "subscription_id": subscription_id,
            "amount": int(amount * 100),  # in paise
            "currency": "INR",
            "status": "created",
            "description": description,
            "customer": {
                "name": customer_name,
                "contact": customer_contact,
            },
        }
        self.payment_links[link_id] = payload
        return payload

    def update_card_token(self, subscription_id: str, new_card_token: str) -> bool:
        """Simulates customer entering new card credentials."""
        self.updated_cards[subscription_id] = new_card_token
        return True
