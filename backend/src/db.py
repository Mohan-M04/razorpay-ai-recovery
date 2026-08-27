"""
SQLite database manager for persistent state, promises-to-pay, and audit trails.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from src.models import (
    SubscriptionRecord,
    PromiseToPay,
    AuditLogEntry,
    FailureReason,
    SubscriptionState,
    Channel,
)


class Database:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._shared_conn = None
        if db_path == ":memory:":
            self._shared_conn = sqlite3.connect(":memory:")
            self._shared_conn.row_factory = sqlite3.Row
            self._shared_conn.execute("PRAGMA foreign_keys = ON;")
        else:
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def get_connection(self) -> sqlite3.Connection:
        if self._shared_conn is not None:
            return self._shared_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_schema(self) -> None:
        with self.get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS subscriptions (
                    subscription_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    failure_reason TEXT NOT NULL,
                    attempt_count INTEGER NOT NULL,
                    last_attempt_at TEXT NOT NULL,
                    customer_contact TEXT NOT NULL,
                    language_pref TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    merchant_name TEXT NOT NULL,
                    plan_name TEXT NOT NULL,
                    state TEXT NOT NULL,
                    recovered_channel TEXT,
                    recovered_at TEXT,
                    voice_attempts INTEGER DEFAULT 0,
                    last_contact_at TEXT,
                    next_action_at TEXT,
                    card_update_token TEXT,
                    opted_out INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS promises_to_pay (
                    ptp_id TEXT PRIMARY KEY,
                    subscription_id TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    reminder_sent INTEGER DEFAULT 0,
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    log_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    subscription_id TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    state_from TEXT NOT NULL,
                    state_to TEXT NOT NULL,
                    metadata TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS voice_interactions (
                    interaction_id TEXT PRIMARY KEY,
                    subscription_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    customer_statement TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    detected_intent TEXT NOT NULL,
                    action_taken TEXT NOT NULL,
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
                );

                CREATE INDEX IF NOT EXISTS idx_subs_state ON subscriptions(state);
                CREATE INDEX IF NOT EXISTS idx_audit_sub ON audit_logs(subscription_id);
                CREATE INDEX IF NOT EXISTS idx_ptp_sub ON promises_to_pay(subscription_id);
                """
            )

    def save_subscription(self, sub: SubscriptionRecord) -> None:
        with self.get_connection() as conn:
            d = sub.to_dict()
            fields = ", ".join(d.keys())
            placeholders = ", ".join([f":{k}" for k in d.keys()])
            sql = f"""
                INSERT OR REPLACE INTO subscriptions ({fields})
                VALUES ({placeholders})
            """
            conn.execute(sql, d)

    def save_subscriptions_batch(self, subs: List[SubscriptionRecord]) -> None:
        with self.get_connection() as conn:
            for sub in subs:
                d = sub.to_dict()
                fields = ", ".join(d.keys())
                placeholders = ", ".join([f":{k}" for k in d.keys()])
                sql = f"""
                    INSERT OR REPLACE INTO subscriptions ({fields})
                    VALUES ({placeholders})
                """
                conn.execute(sql, d)

    def get_subscription(self, subscription_id: str) -> Optional[SubscriptionRecord]:
        with self.get_connection() as conn:
            cur = conn.execute(
                "SELECT * FROM subscriptions WHERE subscription_id = ?",
                (subscription_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return self._row_to_sub(row)

    def get_all_subscriptions(self) -> List[SubscriptionRecord]:
        with self.get_connection() as conn:
            cur = conn.execute("SELECT * FROM subscriptions ORDER BY subscription_id")
            return [self._row_to_sub(r) for r in cur.fetchall()]

    def log_audit(self, entry: AuditLogEntry) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO audit_logs (
                    log_id, timestamp, subscription_id, actor, action,
                    reason, state_from, state_to, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.log_id,
                    entry.timestamp.isoformat(),
                    entry.subscription_id,
                    entry.actor,
                    entry.action,
                    entry.reason,
                    entry.state_from,
                    entry.state_to,
                    json.dumps(entry.metadata),
                ),
            )

    def get_audit_logs(self, subscription_id: Optional[str] = None) -> List[AuditLogEntry]:
        with self.get_connection() as conn:
            if subscription_id:
                cur = conn.execute(
                    "SELECT * FROM audit_logs WHERE subscription_id = ? ORDER BY timestamp ASC",
                    (subscription_id,),
                )
            else:
                cur = conn.execute("SELECT * FROM audit_logs ORDER BY timestamp ASC")
            results = []
            for r in cur.fetchall():
                results.append(
                    AuditLogEntry(
                        log_id=r["log_id"],
                        timestamp=datetime.fromisoformat(r["timestamp"]),
                        subscription_id=r["subscription_id"],
                        actor=r["actor"],
                        action=r["action"],
                        reason=r["reason"],
                        state_from=r["state_from"],
                        state_to=r["state_to"],
                        metadata=json.loads(r["metadata"]),
                    )
                )
            return results

    def save_ptp(self, ptp: PromiseToPay) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO promises_to_pay (
                    ptp_id, subscription_id, due_date, amount, created_at, status, reminder_sent
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ptp.ptp_id,
                    ptp.subscription_id,
                    ptp.due_date.isoformat(),
                    ptp.amount,
                    ptp.created_at.isoformat(),
                    ptp.status,
                    1 if ptp.reminder_sent else 0,
                ),
            )

    def get_ptp(self, subscription_id: str) -> Optional[PromiseToPay]:
        with self.get_connection() as conn:
            cur = conn.execute(
                "SELECT * FROM promises_to_pay WHERE subscription_id = ?",
                (subscription_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return PromiseToPay(
                ptp_id=row["ptp_id"],
                subscription_id=row["subscription_id"],
                due_date=datetime.fromisoformat(row["due_date"]),
                amount=row["amount"],
                created_at=datetime.fromisoformat(row["created_at"]),
                status=row["status"],
                reminder_sent=bool(row["reminder_sent"]),
            )

    def log_voice_interaction(
        self,
        interaction_id: str,
        subscription_id: str,
        customer_statement: str,
        agent_response: str,
        detected_intent: str,
        action_taken: str,
    ) -> None:
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO voice_interactions (
                    interaction_id, subscription_id, timestamp,
                    customer_statement, agent_response, detected_intent, action_taken
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    interaction_id,
                    subscription_id,
                    datetime.now().isoformat(),
                    customer_statement,
                    agent_response,
                    detected_intent,
                    action_taken,
                ),
            )

    def _row_to_sub(self, r: sqlite3.Row) -> SubscriptionRecord:
        return SubscriptionRecord(
            subscription_id=r["subscription_id"],
            customer_id=r["customer_id"],
            amount=r["amount"],
            currency=r["currency"],
            failure_reason=FailureReason(r["failure_reason"]),
            attempt_count=r["attempt_count"],
            last_attempt_at=datetime.fromisoformat(r["last_attempt_at"]),
            customer_contact=r["customer_contact"],
            language_pref=r["language_pref"],
            customer_name=r["customer_name"],
            merchant_name=r["merchant_name"],
            plan_name=r["plan_name"],
            state=SubscriptionState(r["state"]),
            recovered_channel=Channel(r["recovered_channel"]) if r["recovered_channel"] else None,
            recovered_at=datetime.fromisoformat(r["recovered_at"]) if r["recovered_at"] else None,
            voice_attempts=r["voice_attempts"],
            last_contact_at=datetime.fromisoformat(r["last_contact_at"]) if r["last_contact_at"] else None,
            next_action_at=datetime.fromisoformat(r["next_action_at"]) if r["next_action_at"] else None,
            card_update_token=r["card_update_token"],
            opted_out=bool(r["opted_out"]),
        )
