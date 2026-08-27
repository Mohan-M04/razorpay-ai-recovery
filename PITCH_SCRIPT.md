# 🎙️ 5-Minute Pitch Video Script: RazorRecover AI
**Razorpay AI Buildathon — Track 03: AI Revenue Recovery**

> **Target Duration:** Exactly 4:30 – 5:00 minutes  
> **Tools Recommended:** Loom, OBS Studio, or Google Meet recording.  
> **Setup:** Have the dashboard running locally at `http://localhost:3000`.

---

### [0:00 – 0:45] The Hook & The Problem
**[Camera: Facecam]**
> *"Hi everyone, my name is Mohan, and this is my submission for the Razorpay AI Buildathon under Track 03: AI Revenue Recovery.*
>
> *Every single day, Indian merchants lose 15 to 30 percent of their top-line revenue to silent payment degradation. But here is the key insight: payment failure is almost never a clean, binary event. Sometimes it's a transient NPCI bank timeout. Sometimes an auto-debit fails simply because it occurred three days before payday. Sometimes a high-intent customer gets distracted at the 3DS OTP screen.*
>
> *Traditional payment gateways do one thing: they log the error code and abandon the merchant. I built **RazorRecover AI** to close that loop — transforming payment failures from lost revenue into autonomous, bounded recovery workflows."*

---

### [0:45 – 1:30] Architecture & The Bounded Bar
**[Screen Share: Architecture Diagram in ARCHITECTURE.md or README.md]**
> *"Before jumping into the demo, I want to talk about how RazorRecover AI approaches the evaluation bar.*
>
> *In fintech, unbounded LLM agents that can do anything are dangerous. An agent could hallucinate unauthorized discounts or spam customers repeatedly. That's why RazorRecover AI is built as a **hybrid state machine with deterministic guardrails**.*
>
> *When a failure occurs, our AI Reasoner diagnoses the root cause based on error payloads, customer transaction history, and temporal patterns. But before any action is executed, it must pass through four strict guardrails: a 3-touch attempt cap, compliance checks, idempotent link generation, and a high-value gate that routes any transaction over ₹25,000 to a human VIP account manager.*
>
> *Every decision and state transition is captured in an immutable audit trail."*

---

### [1:30 – 3:30] Live Interactive Product Demo
**[Screen Share: Browser showing http://localhost:3000]**
> *"Let's see this in action live on the dashboard.*
>
> *(Click: 'New Batch - 60 Events')*
>
> *Here we have loaded a batch of 60 synthetic payment failures across real Indian merchant archetypes — SaaS, D2C, and EdTech. You can see our starting state: over ₹3,40,000 in revenue currently at risk.*
>
> *(Click: 'Run AI Diagnosis')*
>
> *Watch as the engine diagnoses all 60 events in under 2 seconds. Look at how it categorized them:*
> - *For bank switch timeouts, it scheduled a quiet automated retry through a secondary gateway switch.*
> - *For insufficient funds, it identified the customer's regular buying history and generated a 1-click Razorpay payment link scheduled near their salary window.*
> - *For high-value B2B orders over ₹25,000, our guardrail kicked in and moved them to 'Escalated' for human handling.*
>
> *(Click on a transaction row in the table)*
>
> *Let's drill down into this payment of ₹2,999. In the modal, you can see the complete picture: the customer's past order count, the raw gateway error, the AI diagnosis with a 94% confidence score, the exact simulated WhatsApp message containing a secure Razorpay payment link, and the full audit trail.*
>
> *(Click: 'Simulate Customer Payment')*
>
> *When the customer clicks that link and pays, Razorpay webhooks confirm the settlement, transitioning the transaction to 'Recovered'.*
>
> *(Close modal and Click: 'Simulate Customer Recovery')*
>
> *Across the entire batch, you can see our KPI metrics update live. We recovered over ₹2,20,000 — achieving a **66% recovery rate**, while strictly halting 4 sequences that reached the max-attempt policy to protect merchant brand reputation."*

---

### [3:30 – 4:30] Audit Trail & Compliance Rigor
**[Screen Share: Modal Audit Trail or Click 'Export Audit Trail']**
> *"Razorpay's prompt made one thing very clear: 'Don't just identify the problem. Show measured money recovered across a batch, with compliant escalation, stopping rules, and an audit trail.'*
>
> *If we look at the exported audit log, every single event is tracked with ISO timestamps, actors, previous state, new state, and policy justification. Merchants have full observability. Regulators have full compliance evidence. And most importantly, not a single rupee is charged without explicit user authorization."*

---

### [4:30 – 5:00] Conclusion & Why Razorpay
**[Camera: Facecam]**
> *"RazorRecover AI turns payment operations from a cost center into a direct revenue driver. It's built with TypeScript, modular architecture, and integrates directly with Razorpay's Payment Links and Optimizer rails.*
>
> *I'm thrilled about the opportunity to join Razorpay as an AI Builder Intern in Bangalore this September to bring systems like this into production for over 10 million Indian businesses.*
>
> *Thank you, and I look forward to the technical panel!"*
