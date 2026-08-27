"""
Audit trail logger providing immutable, structured operational tracking.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.models import AuditLogEntry


class AuditLogger:
    def __init__(self, db=None):
        self.db = db
        self.in_memory_logs: List[AuditLogEntry] = []

    def log(
        self,
        subscription_id: str,
        actor: str,
        action: str,
        reason: str,
        state_from: str,
        state_to: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> AuditLogEntry:
        """
        Creates and stores an immutable audit log entry.
        """
        if timestamp is None:
            timestamp = datetime.now()

        entry = AuditLogEntry(
            log_id=f"aud_{uuid.uuid4().hex[:10]}",
            timestamp=timestamp,
            subscription_id=subscription_id,
            actor=actor,
            action=action,
            reason=reason,
            state_from=state_from,
            state_to=state_to,
            metadata=metadata or {},
        )

        self.in_memory_logs.append(entry)

        if self.db is not None:
            self.db.log_audit(entry)

        return entry

    def get_logs(self, subscription_id: Optional[str] = None) -> List[AuditLogEntry]:
        if self.db is not None:
            return self.db.get_audit_logs(subscription_id)
        if subscription_id:
            return [l for l in self.in_memory_logs if l.subscription_id == subscription_id]
        return list(self.in_memory_logs)
