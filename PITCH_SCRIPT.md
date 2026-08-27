# 🎙️ Master 5-Minute Pitch Script: RazorRecover AI (Full-Stack)
**Razorpay AI Buildathon 2026 — Track 03: AI Revenue Recovery**

> **Target Duration:** 4:30 – 5:00 minutes  
> **Tools Recommended:** Loom, OBS Studio, or Windows Screen Recorder (`Win + G`).  
> **Setup:**
> 1. Browser tab open to: `http://localhost:3000` (Frontend Dashboard)
> 2. VS Code terminal open to: `razorpay-ai-recovery/backend`

---

### [0:00 – 0:45] The Problem & The Vision
**[Camera: Facecam]**
> *"Hi everyone, my name is Mohan, and this is my submission for the Razorpay AI Buildathon under Track 03: AI Revenue Recovery.*
>
> *In Indian recurring subscription commerce, merchants lose 15 to 30 percent of their revenue every month to silent payment degradation. But payment failures are almost never intentional cancellations: it's an end-of-month cashflow delay, an expired card token, a temporary NPCI banking switch timeout, or a bank decline.*
>
> *Traditional gateways just log the error code and drop the customer. I built **RazorRecover AI** — a complete full-stack recovery platform that combines a Python deterministic state machine, a Hinglish voice assistant, and a React executive dashboard to recover lost revenue autonomously."*

---

### [0:45 – 1:30] Full-Stack Architecture & Safety
**[Screen Share: ARCHITECTURE.md or README.md in VS Code]**
> *"Before demoing the product, let's talk about the evaluation bar.*
>
> *In financial operations, unbounded LLM agents that can take arbitrary actions are dangerous. That's why RazorRecover AI is built as a **hybrid state machine with deterministic guardrails**.*
>
> *Every failure is categorized into four operational archetypes: expired cards get self-serve update links without automated retries; low-balance debits get a 48-hour cooldown; switch timeouts get a 30-minute fast retry; and bank declines escalate to our Hinglish voice assistant.*
>
> *We enforce four strict stopping rules: a maximum of 3 retries, a 24-hour contact cooldown, a 2-call cap on voice outreach, and an immediate hard stop whenever a customer opts out or asks to cancel."*

---

### [1:30 – 3:00] Part 1: The Executive Dashboard Demo
**[Screen Share: Browser at http://localhost:3000]**
> *"Let's look at the frontend dashboard.*
>
> *(Click: 'Run AI Diagnosis')*
>
> *Here we have loaded a batch of failed transactions. When I run AI Diagnosis, the engine classifies each failure in milliseconds. You can see our starting state: over ₹5 Lakhs at risk.*
>
> *(Click on a transaction row in the table to open the modal)*
>
> *Let's inspect this transaction. In the modal, you see the customer persona, the raw gateway error, the AI diagnostic explanation, the simulated WhatsApp message with a secure Razorpay payment link, and our policy guardrails all marked PASSED.*
>
> *(Click: 'Simulate Customer Recovery')*
>
> *When customers pay their recovery links or automated retries succeed, our KPI counters update live. Over ₹4.6 Lakhs recovered with a 60% conversion rate!"*

---

### [3:00 – 4:15] Part 2: Python Backend, Tests & Hinglish Voice Agent
**[Screen Share: VS Code Terminal in backend/]**
> *"Now let's switch to the Python backend that powers this engine.*
>
> *(Run: `.\test.bat`)*
>
> *Here you can see our automated test suite: 18 out of 18 unit tests passing in 0.12 seconds, verifying retry logic, safety gates, audit trail immutability, and sentence limits.*
>
> *(Run: `.\benchmark.bat`)*
>
> *Next, our evaluation harness runs over a 200-record held-out batch. It outputs a complete breakdown: ₹4,61,578 recovered across automated retries, self-serve card updates, voice recovery, and Promise-to-Pay tracking — with zero stopping-rule violations and 100% compliance.*
>
> *(Run: `.\run.bat` -> option 2)*
>
> *Finally, here is our 'RazorPay Recovery' voice assistant. When a customer says 'Salary 2 din baad aayegi', the assistant speaks warm, polite Hinglish, records a Promise-to-Pay due date, confirms it back, and queues an automated reminder without any harassment."*

---

### [4:15 – 5:00] Conclusion & Why Razorpay
**[Camera: Facecam]**
> *"RazorRecover AI bridges the gap between AI autonomy and strict financial compliance. It turns payment operations from a cost center into a direct revenue driver for Indian businesses.*
>
> *Both the complete Python backend and the React frontend are published on my GitHub with full documentation and tests.*
>
> *I am super excited about the opportunity to join Razorpay as an AI Builder Intern in Bangalore this September and build autonomous fintech systems that power millions of Indian merchants.*
>
> *Thank you so much!"*
