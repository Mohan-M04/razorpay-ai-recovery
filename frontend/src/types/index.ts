export type FailureCode = 
  | 'INSUFFICIENT_FUNDS'
  | 'BANK_DOWNTIME'
  | 'GATEWAY_TIMEOUT'
  | 'MANDATE_EXPIRED'
  | 'USER_DROP_OFF'
  | 'CARD_EXPIRED'
  | 'LIMIT_EXCEEDED';

export type PaymentMethod = 'UPI' | 'CARD' | 'NETBANKING' | 'MANDATE';

export type RecoveryStrategyType = 
  | 'SMART_RETRY_BACKOFF'
  | 'PAYDAY_NUDGE_PAYMENT_LINK'
  | 'INSTANT_MANDATE_RENEWAL'
  | 'WHATSAPP_ASSISTED_CHECKOUT'
  | 'GRACEFUL_DEAL_EXPIRY_ALERT'
  | 'ESCALATE_TO_HUMAN';

export type TransactionStatus = 
  | 'FAILED'
  | 'DIAGNOSING'
  | 'IN_RECOVERY'
  | 'RECOVERED'
  | 'STOPPED'
  | 'ESCALATED';

export interface CustomerProfile {
  id: string;
  name: string;
  phone: string;
  email: string;
  loyaltyTier: 'VIP' | 'REGULAR' | 'NEW';
  pastSuccessfulTransactions: number;
  salaryDayEstimate: number; // Day of month 1-31
}

export interface FailedPaymentEvent {
  id: string;
  merchantId: string;
  merchantName: string;
  merchantCategory: 'SaaS' | 'D2C E-commerce' | 'EdTech' | 'Subscription / OTT' | 'Fintech B2B';
  amount: number; // in INR
  currency: 'INR';
  paymentMethod: PaymentMethod;
  failureCode: FailureCode;
  rawFailureMessage: string;
  timestamp: string;
  customer: CustomerProfile;
  attemptCount: number;
  status: TransactionStatus;
  recoveryPlan?: RecoveryPlan;
  recoveredAt?: string;
  recoveryPaymentLinkId?: string;
}

export interface GuardrailCheck {
  id: string;
  ruleName: string;
  passed: boolean;
  details: string;
}

export interface RecoveryPlan {
  strategy: RecoveryStrategyType;
  diagnosis: string;
  confidenceScore: number; // 0 to 1
  actionSummary: string;
  scheduledDelayMinutes: number;
  channel: 'AUTOMATED_API_RETRY' | 'WHATSAPP' | 'SMS' | 'EMAIL' | 'HUMAN_SUPPORT';
  messageTemplate?: {
    greeting: string;
    body: string;
    ctaText: string;
    paymentLinkUrl: string;
  };
  maxAllowedAttempts: number;
  currentAttempt: number;
  guardrails: GuardrailCheck[];
}

export interface AuditLogEntry {
  id: string;
  transactionId: string;
  timestamp: string;
  action: string;
  actor: 'SYSTEM_EVENT' | 'AI_REASONER' | 'GUARDRAIL_ENGINE' | 'RAZORPAY_API' | 'CUSTOMER_SIMULATOR';
  details: string;
  stateFrom: TransactionStatus;
  stateTo: TransactionStatus;
  metadata?: Record<string, any>;
}

export interface BatchMetrics {
  totalTransactions: number;
  totalAtRiskINR: number;
  totalRecoveredINR: number;
  recoveryRatePercent: number;
  interventionsActive: number;
  stoppedByGuardrails: number;
  escalatedToHuman: number;
  byCategory: Record<string, { atRisk: number; recovered: number }>;
  byFailureCode: Record<string, { count: number; recovered: number }>;
}
