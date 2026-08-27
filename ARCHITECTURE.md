# 📐 Full-Stack System Architecture: RazorRecover AI
**Track 03: AI Revenue Recovery — Razorpay AI Buildathon 2026**

---

## 1. Architectural Overview

RazorRecover AI is structured as a **full-stack fintech recovery platform** that balances autonomous AI conversational capabilities with strict deterministic boundaries:

```
+-------------------------------------------------------------------------+
|                  FRONTEND LAYER (React 19 + TypeScript)                 |
|  - Executive KPI Cards: Real-time Recovery Metrics, At-Risk Monitoring  |
|  - Interactive Batch Runner: Live Diagnostic Evaluation Feed            |
|  - Inspector Modal: Audit Trail Timeline, WhatsApp Nudge Previews       |
+------------------------------------+------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                 BACKEND & AGENT LAYER (Python 3.12 + SQLite)            |
|  - State Machine Sequencer: Reason-based retry scheduling               |
|  - Safety Gates: Max 3 retries, 24h cooldown, opt-out enforcement       |
|  - Promise-to-Pay (PTP) Tracker: Due date monitoring & reminder engine  |
|  - "RazorPay Recovery" Voice Assistant: STT -> LLM -> TTS pipeline      |
|  - Immutable Audit Logger: Append-only SQLite event store               |
+------------------------------------+------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                    RAZORPAY INTEGRATION & TEST RAILS                    |
|  - Razorpay Payment Links API (/v1/payment_links)                       |
|  - Optimizer Smart Routing Simulation                                   |
|  - Subscription Webhook Ingestion (/v1/subscriptions)                   |
+-------------------------------------------------------------------------+
```

---

## 2. Failure-Reason-Driven State Machine

The recovery engine categorizes payment failures into four distinct operational archetypes:

```
               ┌────────────────────────────────────────┐
               │    FAILED PAYMENT INGESTION (DB)       │
               └───────────────────┬────────────────────┘
                                   │
                      [Reason-Based Scheduling]
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│ IN_RETRY_SCHEDULE│       │ VOICE_ESCALATED  │       │  CARD_UPDATE     │
│ (timeout / funds)│       │ (bank_declined)  │       │  (card_expired)  │
└────────┬─────────┘       └────────┬─────────┘       └────────┬─────────┘
         │                          │                          │
    [Retry OK]                [Voice Turn]                [Link Paid]
         │                          │                          │
         ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│    RECOVERED     │       │    PTP_ACTIVE    │       │     STOPPED      │
│  (Channel: Auto) │       │   (Promise Due)  │       │(Opt-out/Max Try) │
└──────────────────┘       └──────────────────┘       └──────────────────┘
```

1. **`card_expired`:** Card tokens cannot be charged. The engine dispatches a secure 1-click Razorpay card update link and blocks all automated retry attempts.
2. **`insufficient_funds`:** Backoff retry scheduled for 48 hours later, aligning with consumer liquidity replenishment.
3. **`gateway_timeout`:** Fast automated retry scheduled for 30 minutes later, capturing remitter CBS switch recovery.
4. **`bank_declined`:** Escalated to conversational voice recovery to resolve issuer security blocks.

---

## 3. "RazorPay Recovery" Hinglish Voice Agent

The conversational assistant engages customers through a modular STT $\rightarrow$ LLM $\rightarrow$ TTS pipeline:

### Behavioral Guarantees:
* **Tone:** Polite, respectful Hinglish tailored for Indian digital consumers.
* **Greeting:** Opens with customer name, exact failed amount, and merchant name.
* **Single Focus:** Offers exactly one next step per turn.
* **Sentence Bound:** Strictly under 3 sentences per dialogue turn.
* **Promise-to-Pay (PTP):** Automatically parses customer pay-later commitments, registers due dates, and sets reminder hooks.
* **Opt-Out Compliance:** Any refusal (*"Cancel kar do"*, *"Call mat karo"*) immediately triggers `OPT_OUT_HARD_STOP`, marking the case `STOPPED` and permanently terminating contact.

---

## 4. Safety Gates & Honest Failure Modes

```python
class SafetyGates:
    MAX_TOTAL_RETRIES = 3
    MIN_CONTACT_COOLDOWN_HOURS = 24
    MAX_VOICE_ATTEMPTS = 2
```

1. **Max 3 Retries:** Hard stop to prevent bank retry penalties.
2. **24h Cooldown:** Zero touches permitted within 24 hours of prior contact.
3. **Max 2 Voice Calls:** Caps voice outreach to protect brand trust.
4. **Honest Failure Handling:** When all attempts are exhausted, cases are marked `STOPPED` and flagged for human merchant review. No infinite loops.

---

## 5. Audit Trail & Verification

Every action is persisted in SQLite with structured JSON metadata, actors, previous states, and timestamps:
```sql
CREATE TABLE audit_logs (
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
```
Audit trails are exportable via the web dashboard or CLI for compliance reviews.
