# 🛡️ RazorRecover AI — Full-Stack Subscription Revenue Recovery System
> **Built for the Razorpay AI Buildathon 2026 — Track 03: AI Revenue Recovery**  
> *"Don’t just identify the problem. Show measured money recovered across a batch, with compliant escalation, stopping rules, and an audit trail."*

[![Buildathon Track](https://img.shields.io/badge/Razorpay_Buildathon-Track_03:_Revenue_Recovery-0C2340?style=for-the-badge&logo=razorpay)](https://razorpay.com/buildathon/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![React 19](https://img.shields.io/badge/React-19.0-61DAFB?style=for-the-badge&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Unit Tests](https://img.shields.io/badge/Unit_Tests-18%2F18_Passing-10B981?style=for-the-badge)]()
[![Safety Compliance](https://img.shields.io/badge/Safety_Compliance-100%25_Audited-3B82F6?style=for-the-badge)]()

---

## 🎯 Executive Overview

In Indian recurring subscription commerce (SaaS, OTT, EdTech, Fitness, D2C Subscriptions), **payment failure is not an intentional cancellation — it is an operational leak**:
* **`insufficient_funds` (35%):** Debits trigger 2-3 days prior to the customer's monthly salary date.
* **`gateway_timeout` (25%):** Temporary banking switch or NPCI UPI timeout.
* **`bank_declined` (25%):** Issuer mandate security checks requiring conversational re-authorization.
* **`card_expired` (15%):** Card token expired without updated payment details.

**RazorRecover AI is a production-ready, full-stack revenue recovery system** combining:
1. 🐍 **Python Core Engine (`/backend`):** A finite state machine retry sequencer, deterministic safety gates, an append-only SQLite audit trail, a **Promise-to-Pay (PTP) tracker**, and a polite **Hinglish voice recovery agent ("RazorPay Recovery")**.
2. 🌐 **Executive Visual Dashboard (`/frontend`):** A modern dark-mode React/TypeScript application visualizing live failure feeds, real-time KPI metrics, guardrail matrices, and an interactive payment simulator.

---

## 📊 Benchmark Evaluation Results (200-Record Held-Out Batch)

Tested across a reproducible, seeded batch of 200 failed subscription records (`seed=42`) representing 7 Indian merchant categories:

| Metric | Benchmark Result | Evaluation Standard | Status |
|---|---|---|---|
| **Batch Size** | **200 records** | Held-out evaluation batch | ✅ Complete |
| **Total Revenue at Risk** | **₹7,64,300.00** | Across 7 enterprise merchants | 🛡️ Monitored |
| **Total Revenue Recovered** | **₹4,61,578.00** | Multi-channel recovery | 🟢 **Recovered** |
| **Net Recovery Conversion Rate** | **60.39%** | Target &gt; 50% | 🚀 **Exceeded** |
| **Subscriptions Saved** | **122 / 200** | Retained recurring customers | 📈 High Retention |
| **Stopping-Rule Violations** | **0 (Zero)** | 100% compliant safety gates | 🔒 Audited |
| **Unnecessary Contacts** | **0 (Zero)** | Zero touches in cooldown or post-recovery | ⏱️ Compliant |
| **Safety Gate Compliance** | **100.0%** | Hard stopping rules verified | 🛡️ Verified |

### Multi-Channel Breakdown:
* **Automated Smart Retries:** **66.8%** of recovered revenue (₹3,08,320 recovered across 80 subscriptions via 30m/48h backoff).
* **Self-Serve Card Updates:** **16.1%** of recovered revenue (₹74,281 recovered across 19 subscriptions via 1-click token update links).
* **Hinglish Voice Recovery Agent:** **15.1%** of recovered revenue (₹69,683 recovered across 17 subscriptions resolving bank declines).
* **Promise-to-Pay (PTP) Tracker:** **2.0%** of recovered revenue (₹9,294 recovered across 6 subscriptions honored on salary day).

---

## 🏗️ System Architecture

```
                                  FULL-STACK ARCHITECTURE
                                  
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │                  FRONTEND: Executive Recovery Dashboard                     │
   │           (React 19 + TypeScript + Vite 6 + Tailwind CSS)                   │
   │   - Real-time KPI Cards (Revenue at Risk, Recovered, Recovery Rate %)       │
   │   - Interactive Batch Runner & Processing Stream                            │
   │   - Transaction Drill-down Modal with Audit Trail & WhatsApp Nudge Preview  │
   └──────────────────────────────────────┬──────────────────────────────────────┘
                                          │
                                          ▼
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │                  BACKEND: Deterministic Recovery Engine                     │
   │                        (Python 3.12 + SQLite)                               │
   ├─────────────────────────────────────────────────────────────────────────────┤
   │  1. Reason-Based Retry Sequencer:                                           │
   │     - card_expired       --> Self-serve card update link (no auto-retries)  │
   │     - insufficient_funds --> 48h backoff retry (salary cycle)               │
   │     - gateway_timeout    --> 30-minute fast automated switch retry          │
   │     - bank_declined      --> Immediate voice outreach escalation            │
   │                                                                             │
   │  2. "RazorPay Recovery" Hinglish Voice Agent (STT -> LLM -> TTS):           │
   │     - Warm, polite Hinglish (< 3 sentences per turn with polite closing)    │
   │     - Exactly one clear next step at a time                                 │
   │     - Promise-to-Pay (PTP) tracker with automated due-date reminders        │
   │     - Hard stop on refusal / opt-out (marked STOPPED, never re-contact)     │
   │                                                                             │
   │  3. Deterministic Safety Gates:                                             │
   │     - Max 3 total retries per subscription                                  │
   │     - 24-hour minimum contact cooldown between outreach attempts            │
   │     - Max 2 voice call attempts                                             │
   │     - Immutable append-only SQLite audit trail                              │
   └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎙️ Voice Agent Persona & Rules ("RazorPay Recovery")

```
Persona: "RazorPay Recovery" — polite, professional, warm Hinglish assistant.
Job: Explain failed payment, offer exactly one clear solution, handle objections calmly.
```

### Strict Operational Rules:
1. **Personalized Opening:** Always greets by customer name, stating the exact failed amount and merchant.
2. **One Next Step at a Time:** Never confuses or overwhelms the customer.
3. **Promise-to-Pay Integration:** If customer says they'll pay later (e.g. *"Salary 2 din baad aayegi"*), confirms the due date and registers it in the PTP tracker.
4. **Hard Stop on Refusal:** If customer says *"Cancel kar do"*, *"Band karo"*, or *"Call mat karo"*, immediately thanks them, marks the subscription `STOPPED`, and **never re-contacts**.
5. **Sentence Cap:** Responses are strictly under 3 sentences with a polite closing (*"Dhanyavaad / Thank you"*).
6. **Zero Hallucination:** Only references data provided in the subscription payload.

---

## 🧪 Unit Tests: 18 / 18 Passing

```bash
$ cd backend
$ .\test.bat

tests/test_audit.py::test_audit_trail_logging_and_retrieval PASSED       [  5%]
tests/test_audit.py::test_audit_trail_query_by_subscription_isolation PASSED [ 11%]
tests/test_ptp.py::test_record_and_fulfill_promise PASSED                [ 16%]
tests/test_ptp.py::test_broken_promise PASSED                            [ 22%]
tests/test_ptp.py::test_ptp_reminder_scheduling PASSED                   [ 27%]
tests/test_safety_gates.py::test_max_three_retries_stopping_rule PASSED  [ 33%]
tests/test_safety_gates.py::test_twenty_four_hour_contact_cooldown PASSED [ 38%]
tests/test_safety_gates.py::test_max_voice_attempts PASSED               [ 44%]
tests/test_safety_gates.py::test_hard_stop_on_opt_out PASSED             [ 50%]
tests/test_sequencer.py::test_card_expired_prompts_update_without_auto_retry PASSED [ 55%]
tests/test_sequencer.py::test_insufficient_funds_schedules_48h_retry PASSED [ 61%]
tests/test_sequencer.py::test_gateway_timeout_schedules_30m_retry PASSED [ 66%]
tests/test_sequencer.py::test_bank_declined_escalates_to_voice_immediately PASSED [ 72%]
tests/test_voice_agent.py::test_greeting_compliance PASSED               [ 77%]
tests/test_voice_agent.py::test_opt_out_hard_stop PASSED                 [ 83%]
tests/test_voice_agent.py::test_promise_to_pay_dialogue PASSED           [ 88%]
tests/test_voice_agent.py::test_card_update_dialogue PASSED              [ 94%]
tests/test_voice_agent.py::test_response_sentence_count_limit PASSED     [100%]

============================= 18 passed in 0.12s ==============================
```

---

## 🚀 Quickstart & How to Run

### 1. Run the Python Backend & Benchmarks
```powershell
cd backend
.\benchmark.bat     # Runs 200-record benchmark table
.\test.bat          # Runs all 18 unit tests
.\run.bat           # Interactive Hinglish voice assistant demo
```

### 2. Run the Visual Web Dashboard
```powershell
cd frontend
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

## 📂 Monorepo Directory Structure

```
razorpay-ai-recovery/
├── backend/
│   ├── src/
│   │   ├── models.py           # Dataclasses & Enums
│   │   ├── db.py               # SQLite manager
│   │   ├── generator.py        # Seeded 200-record synthetic generator
│   │   ├── mock_gateway.py     # Deterministic Razorpay test client
│   │   ├── sequencer.py        # State machine retry sequencer
│   │   ├── safety_gates.py     # 24h cooldown & stopping rules
│   │   ├── ptp_tracker.py      # Promise-to-Pay tracker
│   │   ├── voice_agent/        # Hinglish voice assistant pipeline & prompts
│   │   ├── audit.py            # Immutable audit trail
│   │   ├── evaluation.py       # Benchmark evaluation harness
│   │   └── cli.py              # Interactive terminal CLI
│   ├── tests/                  # 18 pytest unit tests
│   ├── run.bat                 # Interactive voice demo launcher
│   ├── test.bat                # Unit test runner
│   └── benchmark.bat           # Evaluation benchmark runner
├── frontend/
│   ├── src/                    # React 19 dashboard components
│   ├── index.html              # Web entrypoint
│   ├── package.json            # Vite 6 + Tailwind CSS dependencies
│   └── vite.config.ts          # Bundler config
├── ARCHITECTURE.md             # In-depth architectural & compliance doc
├── PITCH_SCRIPT.md             # Timed 5-minute video presentation script
└── README.md                   # Full-stack documentation
```

---

## 📜 Submission Details
* **Author:** Mohan & Antigravity
* **Buildathon Track:** Track 03 — AI Revenue Recovery
* **Target Role:** Razorpay AI Builder Intern (Bangalore, from September)
