# 📐 System Architecture Specification: RazorRecover AI
**Track 03: AI Revenue Recovery — Razorpay AI Buildathon 2026**

---

## 1. Executive Summary

RazorRecover AI is designed as a **hybrid deterministic/autonomous state machine** for payment failure mitigation. In financial transactions, unbounded LLM agent autonomy presents severe operational and brand risks (e.g. infinite retries, harassing customers, generating unauthorized discounts).

RazorRecover AI solves this by decoupling:
1. **The Diagnostic Layer (AI Reasoner):** Interprets noisy gateway failure messages, customer transaction history, and temporal indicators to formulate an optimal recovery hypothesis.
2. **The Guardrail Layer (Deterministic Policy Engine):** Hard boundaries enforced in code that strictly gate, throttle, or halt any monetary action before execution.
3. **The Execution Layer (Tool Rail):** Direct integration with Razorpay test APIs and customer communication channels.
4. **The Audit Layer (Immutable Event Store):** Structured logging of state transitions, reasoning strings, and verification proofs.

---

## 2. State Machine & Lifecycle Transitions

Every payment event adheres to a strict directed acyclic graph (DAG) of state transitions:

```
                  ┌──────────────────────────────┐
                  │  WEBHOOK INGESTION (FAILED)  │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │      EVALUATE GUARDRAILS     │
                  └──────┬───────────────┬───────┘
                         │               │
            [Violated]   │               │   [Passed]
                         ▼               ▼
          ┌────────────────────┐   ┌───────────────────────────┐
          │  HALT / ESCALATE   │   │   AI DIAGNOSTIC REASONER  │
          │ (STOPPED/ESCALATED)│   └─────────────┬─────────────┘
          └────────────────────┘                 │
                                                 ▼
                                   ┌───────────────────────────┐
                                   │  DISPATCH RECOVERY PLAY   │
                                   │       (IN_RECOVERY)       │
                                   └─────────────┬─────────────┘
                                                 │
                                ┌────────────────┴────────────────┐
                                │                                 │
                     [Customer Pays / Retry OK]      [Link Expires / Max Attempts]
                                ▼                                 ▼
                   ┌─────────────────────────┐       ┌─────────────────────────┐
                   │    VERIFIED SETTLEMENT  │       │     GRACEFUL STOP       │
                   │       (RECOVERED)       │       │        (STOPPED)        │
                   └─────────────────────────┘       └─────────────────────────┘
```

### State Definitions:
* **`FAILED`:** Raw payment failure webhook captured from Razorpay gateway rail.
* **`DIAGNOSING`:** AI analyzing error payload, customer persona, and temporal context.
* **`IN_RECOVERY`:** Bounded action executed (retry scheduled, WhatsApp payment link dispatched).
* **`RECOVERED`:** Webhook confirms settlement of original order or associated payment link.
* **`STOPPED`:** Recovery sequence terminated gracefully (opt-out, expiration, or maximum attempt cap reached).
* **`ESCALATED`:** Transaction value exceeds autonomous policy threshold ($\ge$ ₹25,000); transferred to human merchant account manager.

---

## 3. Failure Classification & Recovery Archetypes

| Failure Code | Underlying Root Cause | Recovery Archetype | Primary Channel | Safety Limit |
|---|---|---|---|---|
| `BANK_DOWNTIME` | Remitter CBS switch degraded or NPCI timeout | `SMART_RETRY_BACKOFF` | Automated Gateway Switch | Max 2 retries with 15m exponential backoff |
| `INSUFFICIENT_FUNDS` | Temporary liquidity constraint | `PAYDAY_NUDGE_PAYMENT_LINK` | WhatsApp + Razorpay Link | 1 link, 72-hour expiry, scheduled near salary window |
| `MANDATE_EXPIRED` | UPI Autopay / e-NACH validity ended | `INSTANT_MANDATE_RENEWAL` | WhatsApp 1-Tap Auth | Pre-filled mandate registration token |
| `USER_DROP_OFF` | Abandoned at 3DS OTP verification | `WHATSAPP_ASSISTED_CHECKOUT` | WhatsApp Conversational | Reserved cart token, 2-hour window |
| `CARD_EXPIRED` | Card token invalidated by issuer | `GRACEFUL_DEAL_EXPIRY_ALERT` | SMS / WhatsApp | Prompt to switch to UPI / Netbanking |
| `LIMIT_EXCEEDED` | Daily UPI transfer velocity cap reached | `PAYDAY_NUDGE_PAYMENT_LINK` | WhatsApp (Next Day Nudge) | Scheduled 8 hours later on counter reset |

---

## 4. Policy Guardrails & Compliance Enforcements

RazorRecover AI enforces 5 non-negotiable guardrails:

```typescript
export class RecoveryAgent {
  private static MAX_ALLOWED_ATTEMPTS = 3;
  private static HIGH_VALUE_THRESHOLD = 25000; // INR
  // ...
}
```

1. **`GR_01_ATTEMPT_LIMIT`:** Maximum of 3 autonomous customer touches across all channels. Any further touches violate brand safety and trigger `ENFORCE_STOPPING_RULE`.
2. **`GR_02_CHANNEL_CONSENT`:** Verification that customer has not opted out via TRAI DND regulations or previous opt-out payloads.
3. **`GR_03_AMOUNT_GATE`:** Transactions $\ge$ ₹25,000 are structurally prevented from receiving automated nudges; an executive escalation ticket is created for human handling.
4. **`GR_04_IDEMPOTENT_LINK`:** Payment links are cryptographically keyed to the exact order ID to prevent multiple debits for a single purchase.
5. **`GR_05_DEFENSE_ONLY`:** No automated charging without explicit user-initiated authorization (following RBI 2FA directives).

---

## 5. Razorpay Integration Architecture

The service interacts with Razorpay's modern rails:
* **Payment Links API (`/v1/payment_links`):** Generates short URLs with SMS/WhatsApp notifications and automatic reminders.
* **Smart Routing (Optimizer):** Bypasses degraded banking rails during `SMART_RETRY_BACKOFF` flows.
* **Webhooks:** Ingests `payment.failed`, `payment_link.paid`, `mandate.failed`, and `settlement.created`.

---

## 6. Audit Trail Schema & Observability

Every action is stored as a tamper-evident audit record:
```json
{
  "id": "aud_k9x2m4p",
  "transactionId": "pay_98a7s6d5",
  "timestamp": "2026-08-27T22:30:00.000Z",
  "action": "FORMULATE_RECOVERY_PLAN",
  "actor": "AI_REASONER",
  "details": "Strategy: PAYDAY_NUDGE_PAYMENT_LINK | Diagnosis: Debit declined due to insufficient balance...",
  "stateFrom": "FAILED",
  "stateTo": "IN_RECOVERY",
  "metadata": {
    "channel": "WHATSAPP",
    "confidence": "0.94",
    "paymentLink": "https://rzp.io/i/8x9f2a"
  }
}
```

These logs can be exported as standard JSON or streamed into ClickHouse/Snowflake for regulatory and compliance audits.
