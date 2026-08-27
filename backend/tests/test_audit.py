"""
Unit tests for the SQLite audit trail and logging system.
"""

from datetime import datetime
import pytest

from src.db import Database
from src.audit import AuditLogger


def test_audit_trail_logging_and_retrieval():
    db = Database(":memory:")
    audit = AuditLogger(db)

    now = datetime(2026, 8, 27, 10, 0, 0)
    entry1 = audit.log(
        subscription_id="sub_aud_01",
        actor="SEQUENCER",
        action="SCHEDULE_RETRY_30M",
        reason="Gateway timeout observed.",
        state_from="pending",
        state_to="in_retry_schedule",
        metadata={"gateway": "HDFC_SWITCH"},
        timestamp=now,
    )

    entry2 = audit.log(
        subscription_id="sub_aud_01",
        actor="RAZORPAY_GATEWAY",
        action="PAYMENT_CAPTURED",
        reason="Automated retry succeeded.",
        state_from="in_retry_schedule",
        state_to="recovered",
        metadata={"amount": 1499.0},
        timestamp=now,
    )

    logs = audit.get_logs("sub_aud_01")
    assert len(logs) == 2
    assert logs[0].action == "SCHEDULE_RETRY_30M"
    assert logs[0].metadata.get("gateway") == "HDFC_SWITCH"
    assert logs[1].action == "PAYMENT_CAPTURED"
    assert logs[1].state_to == "recovered"


def test_audit_trail_query_by_subscription_isolation():
    db = Database(":memory:")
    audit = AuditLogger(db)

    audit.log(
        subscription_id="sub_A",
        actor="SEQUENCER",
        action="ACTION_A",
        reason="Reason A",
        state_from="pending",
        state_to="in_retry_schedule",
    )
    audit.log(
        subscription_id="sub_B",
        actor="VOICE_AGENT",
        action="ACTION_B",
        reason="Reason B",
        state_from="pending",
        state_to="voice_escalated",
    )

    logs_a = audit.get_logs("sub_A")
    logs_b = audit.get_logs("sub_B")

    assert len(logs_a) == 1
    assert logs_a[0].subscription_id == "sub_A"
    assert len(logs_b) == 1
    assert logs_b[0].subscription_id == "sub_B"
