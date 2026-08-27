"""
Domain models, enums, and data transfer objects for AI Revenue Recovery.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class FailureReason(str, Enum):
    CARD_EXPIRED = "card_expired"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    BANK_DECLINED = "bank_declined"
    GATEWAY_TIMEOUT = "gateway_timeout"


class SubscriptionState(str, Enum):
    PENDING = "pending"
    IN_RETRY_SCHEDULE = "in_retry_schedule"
    VOICE_ESCALATED = "voice_escalated"
    PTP_ACTIVE = "ptp_active"
    RECOVERED = "recovered"
    STOPPED = "stopped"
    CANCELLED = "cancelled"


class Channel(str, Enum):
    AUTO_RETRY = "auto_retry"
    VOICE = "voice"
    PTP = "ptp"
    CARD_UPDATE = "card_update"


@dataclass
class SubscriptionRecord:
    subscription_id: str
    customer_id: str
    amount: float
    currency: str
    failure_reason: FailureReason
    attempt_count: int
    last_attempt_at: datetime
    customer_contact: str
    language_pref: str
    customer_name: str = "Valued Customer"
    merchant_name: str = "Razorpay Merchant"
    plan_name: str = "Standard Subscription"
    state: SubscriptionState = SubscriptionState.PENDING
    recovered_channel: Optional[Channel] = None
    recovered_at: Optional[datetime] = None
    voice_attempts: int = 0
    last_contact_at: Optional[datetime] = None
    next_action_at: Optional[datetime] = None
    card_update_token: Optional[str] = None
    opted_out: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscription_id": self.subscription_id,
            "customer_id": self.customer_id,
            "amount": self.amount,
            "currency": self.currency,
            "failure_reason": self.failure_reason.value if isinstance(self.failure_reason, FailureReason) else self.failure_reason,
            "attempt_count": self.attempt_count,
            "last_attempt_at": self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            "customer_contact": self.customer_contact,
            "language_pref": self.language_pref,
            "customer_name": self.customer_name,
            "merchant_name": self.merchant_name,
            "plan_name": self.plan_name,
            "state": self.state.value if isinstance(self.state, SubscriptionState) else self.state,
            "recovered_channel": self.recovered_channel.value if self.recovered_channel else None,
            "recovered_at": self.recovered_at.isoformat() if self.recovered_at else None,
            "voice_attempts": self.voice_attempts,
            "last_contact_at": self.last_contact_at.isoformat() if self.last_contact_at else None,
            "next_action_at": self.next_action_at.isoformat() if self.next_action_at else None,
            "card_update_token": self.card_update_token,
            "opted_out": 1 if self.opted_out else 0,
        }


@dataclass
class PromiseToPay:
    ptp_id: str
    subscription_id: str
    due_date: datetime
    amount: float
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # "pending", "fulfilled", "broken"
    reminder_sent: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ptp_id": self.ptp_id,
            "subscription_id": self.subscription_id,
            "due_date": self.due_date.isoformat(),
            "amount": self.amount,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "reminder_sent": 1 if self.reminder_sent else 0,
        }


@dataclass
class AuditLogEntry:
    log_id: str
    timestamp: datetime
    subscription_id: str
    actor: str
    action: str
    reason: str
    state_from: str
    state_to: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_id": self.log_id,
            "timestamp": self.timestamp.isoformat(),
            "subscription_id": self.subscription_id,
            "actor": self.actor,
            "action": self.action,
            "reason": self.reason,
            "state_from": self.state_from,
            "state_to": self.state_to,
            "metadata": self.metadata,
        }
