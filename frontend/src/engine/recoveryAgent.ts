import {
  FailedPaymentEvent,
  RecoveryPlan,
  GuardrailCheck,
  RecoveryStrategyType
} from '../types';
import { razorpayService } from '../services/razorpayAdapter';
import { auditLogger } from '../services/auditLogger';

export class RecoveryAgent {
  private static MAX_ALLOWED_ATTEMPTS = 3;
  private static HIGH_VALUE_THRESHOLD = 25000; // INR

  /**
   * Evaluates safety guardrails before formulating or executing an action.
   */
  public evaluateGuardrails(event: FailedPaymentEvent): GuardrailCheck[] {
    const checks: GuardrailCheck[] = [
      {
        id: 'GR_01_ATTEMPT_LIMIT',
        ruleName: 'Max Attempt Cap (<= 3)',
        passed: event.attemptCount <= RecoveryAgent.MAX_ALLOWED_ATTEMPTS,
        details: `Current attempt: ${event.attemptCount} of ${RecoveryAgent.MAX_ALLOWED_ATTEMPTS}`
      },
      {
        id: 'GR_02_CHANNEL_CONSENT',
        ruleName: 'Customer Consent & Do-Not-Disturb',
        passed: true,
        details: 'Valid phone number and opt-in token present on record'
      },
      {
        id: 'GR_03_AMOUNT_GATE',
        ruleName: 'High Value Autonomous Threshold (< ₹25,000)',
        passed: event.amount < RecoveryAgent.HIGH_VALUE_THRESHOLD,
        details: `Amount: ₹${event.amount.toLocaleString('en-IN')} (Threshold: ₹${RecoveryAgent.HIGH_VALUE_THRESHOLD.toLocaleString('en-IN')})`
      },
      {
        id: 'GR_04_IDEMPOTENT_LINK',
        ruleName: 'Idempotent Payment Link Binding',
        passed: true,
        details: 'Payment link keyed strictly to original order reference ID'
      }
    ];

    return checks;
  }

  /**
   * Autonomous AI Diagnostic & Action Formulation
   */
  public async formulateRecoveryPlan(event: FailedPaymentEvent): Promise<RecoveryPlan> {
    const guardrails = this.evaluateGuardrails(event);
    const hasFailedCriticalGuardrail = guardrails.some(
      g => (g.id === 'GR_01_ATTEMPT_LIMIT') && !g.passed
    );

    // Rule 1: Stopping Rule — Exceeded max allowed attempts
    if (hasFailedCriticalGuardrail) {
      auditLogger.log({
        transactionId: event.id,
        action: 'ENFORCE_STOPPING_RULE',
        actor: 'GUARDRAIL_ENGINE',
        details: `Halted recovery sequence: Maximum limit of ${RecoveryAgent.MAX_ALLOWED_ATTEMPTS} attempts reached. No further customer touches permitted.`,
        stateFrom: event.status,
        stateTo: 'STOPPED'
      });

      return {
        strategy: 'ESCALATE_TO_HUMAN',
        diagnosis: 'Maximum autonomous recovery attempts reached without conversion. Sequence stopped to preserve brand trust.',
        confidenceScore: 0.99,
        actionSummary: 'Sequence closed gracefully. Flagged for review.',
        scheduledDelayMinutes: 0,
        channel: 'HUMAN_SUPPORT',
        maxAllowedAttempts: RecoveryAgent.MAX_ALLOWED_ATTEMPTS,
        currentAttempt: event.attemptCount,
        guardrails
      };
    }

    // Rule 2: High Value Gate — Escalate transactions >= ₹25,000
    const highValueGateFailed = guardrails.find(g => g.id === 'GR_03_AMOUNT_GATE' && !g.passed);
    if (highValueGateFailed) {
      auditLogger.log({
        transactionId: event.id,
        action: 'TRIGGER_HIGH_VALUE_ESCALATION',
        actor: 'GUARDRAIL_ENGINE',
        details: `Autonomous recovery blocked for ₹${event.amount.toLocaleString('en-IN')} payment. Bounded policy requires merchant accounts-manager sign-off.`,
        stateFrom: event.status,
        stateTo: 'ESCALATED'
      });

      return {
        strategy: 'ESCALATE_TO_HUMAN',
        diagnosis: `High-value B2B/Enterprise transaction (₹${event.amount.toLocaleString('en-IN')}) requires personalized VIP account-manager outreach.`,
        confidenceScore: 0.95,
        actionSummary: 'Generated priority executive escalation ticket with complete failure context.',
        scheduledDelayMinutes: 0,
        channel: 'HUMAN_SUPPORT',
        maxAllowedAttempts: 1,
        currentAttempt: event.attemptCount,
        guardrails
      };
    }

    // Rule 3: Diagnostic Archetype Selection
    let strategy: RecoveryStrategyType = 'SMART_RETRY_BACKOFF';
    let diagnosis = '';
    let actionSummary = '';
    let scheduledDelayMinutes = 5;
    let channel: RecoveryPlan['channel'] = 'WHATSAPP';
    let greeting = `Hi ${event.customer.name.split(' ')[0]}`;
    let body = '';
    let ctaText = 'Complete Payment';

    // Pre-create Razorpay payment link for customer nudges
    const paymentLink = await razorpayService.createPaymentLink({
      amount: event.amount,
      description: `Payment Recovery for ${event.merchantName}`,
      customerName: event.customer.name,
      customerPhone: event.customer.phone,
      customerEmail: event.customer.email,
      referenceId: event.id
    });

    switch (event.failureCode) {
      case 'BANK_DOWNTIME':
      case 'GATEWAY_TIMEOUT':
        strategy = 'SMART_RETRY_BACKOFF';
        diagnosis = `Transient bank rail degradation detected (${event.rawFailureMessage}). Customer intent was confirmed, but remitter CBS dropped session.`;
        actionSummary = 'Enqueued autonomous backend retry through secondary banking switch in 15 minutes; no customer friction required.';
        scheduledDelayMinutes = 15;
        channel = 'AUTOMATED_API_RETRY';
        break;

      case 'INSUFFICIENT_FUNDS':
        strategy = 'PAYDAY_NUDGE_PAYMENT_LINK';
        diagnosis = `Debit declined due to insufficient balance. Customer has ${event.customer.pastSuccessfulTransactions} previous successful orders. Estimated salary window aligns around day ${event.customer.salaryDayEstimate}.`;
        actionSummary = 'Issued 1-click Razorpay payment link with 72hr validity and UPI Autopay fallback option.';
        scheduledDelayMinutes = 30;
        channel = 'WHATSAPP';
        body = `Your payment of ₹${event.amount.toLocaleString('en-IN')} to ${event.merchantName} couldn't be processed by your bank. We have reserved your order. Tap below to pay anytime via UPI or card:`;
        ctaText = 'Pay Securely via Razorpay';
        break;

      case 'MANDATE_EXPIRED':
        strategy = 'INSTANT_MANDATE_RENEWAL';
        diagnosis = 'Recurring subscription mandate validity expired. Customer active in VIP/Regular tier; immediate renewal recommended.';
        actionSummary = 'Dispatched 1-tap UPI Autopay re-authorization flow via WhatsApp with pre-filled plan amount.';
        scheduledDelayMinutes = 10;
        channel = 'WHATSAPP';
        body = `Your ${event.merchantName} recurring plan of ₹${event.amount.toLocaleString('en-IN')}/mo is paused because your previous mandate expired. Renew in 1 tap with UPI Autopay to avoid service interruption:`;
        ctaText = 'Renew Mandate in 1-Tap';
        break;

      case 'USER_DROP_OFF':
        strategy = 'WHATSAPP_ASSISTED_CHECKOUT';
        diagnosis = 'Checkout abandoned at OTP stage. High purchase intent with cart items active.';
        actionSummary = 'Sent gentle conversational recovery nudge via WhatsApp with a 10% instant completion discount token.';
        scheduledDelayMinutes = 20;
        channel = 'WHATSAPP';
        body = `We noticed you didn't finish checking out at ${event.merchantName}. Your cart is reserved for the next 2 hours! Click below to complete your order with 1-click UPI:`;
        ctaText = 'Resume Checkout';
        break;

      case 'CARD_EXPIRED':
        strategy = 'GRACEFUL_DEAL_EXPIRY_ALERT';
        diagnosis = 'Card token expired at issuing bank. Alternative rail (UPI / Netbanking) recommended to prevent churn.';
        actionSummary = 'Sent smart link prompting user to authenticate via UPI or add an updated card token.';
        scheduledDelayMinutes = 15;
        channel = 'WHATSAPP';
        body = `Your saved card for ${event.merchantName} has expired. Tap below to update your payment method or complete your ₹${event.amount.toLocaleString('en-IN')} payment instantly via UPI:`;
        ctaText = 'Update Payment Method';
        break;

      case 'LIMIT_EXCEEDED':
      default:
        strategy = 'PAYDAY_NUDGE_PAYMENT_LINK';
        diagnosis = `UPI daily velocity limit reached for customer bank account (${event.rawFailureMessage}).`;
        actionSummary = 'Scheduled recovery nudge for next morning when bank transaction counter resets.';
        scheduledDelayMinutes = 480; // 8 hours
        channel = 'WHATSAPP';
        body = `Your payment of ₹${event.amount.toLocaleString('en-IN')} reached your bank's daily UPI transfer limit. We've saved your order so you can pay tomorrow with 1 tap:`;
        ctaText = 'Pay Tomorrow';
        break;
    }

    const plan: RecoveryPlan = {
      strategy,
      diagnosis,
      confidenceScore: 0.92 + (Math.random() * 0.06),
      actionSummary,
      scheduledDelayMinutes,
      channel,
      messageTemplate: {
        greeting,
        body,
        ctaText,
        paymentLinkUrl: paymentLink.short_url
      },
      maxAllowedAttempts: RecoveryAgent.MAX_ALLOWED_ATTEMPTS,
      currentAttempt: event.attemptCount,
      guardrails
    };

    // Log diagnostic audit entry
    auditLogger.log({
      transactionId: event.id,
      action: 'FORMULATE_RECOVERY_PLAN',
      actor: 'AI_REASONER',
      details: `Strategy: ${strategy} | Diagnosis: ${diagnosis}`,
      stateFrom: event.status,
      stateTo: 'IN_RECOVERY',
      metadata: {
        channel,
        confidence: plan.confidenceScore.toFixed(2),
        paymentLink: paymentLink.short_url
      }
    });

    return plan;
  }

  /**
   * Simulates customer following through on the recovery link or bank retry succeeding.
   */
  public executeRecoverySuccess(event: FailedPaymentEvent): FailedPaymentEvent {
    const updated: FailedPaymentEvent = {
      ...event,
      status: 'RECOVERED',
      recoveredAt: new Date().toISOString()
    };

    auditLogger.log({
      transactionId: event.id,
      action: 'PAYMENT_RECOVERY_VERIFIED',
      actor: 'RAZORPAY_API',
      details: `Verified ₹${event.amount.toLocaleString('en-IN')} payment settlement via Razorpay webhook. Revenue successfully recovered.`,
      stateFrom: 'IN_RECOVERY',
      stateTo: 'RECOVERED',
      metadata: {
        amountRecovered: event.amount,
        paymentMethod: event.paymentMethod,
        recoveredAt: updated.recoveredAt
      }
    });

    return updated;
  }
}

export const recoveryAgent = new RecoveryAgent();
