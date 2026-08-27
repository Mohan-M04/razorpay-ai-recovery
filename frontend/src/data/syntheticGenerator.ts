import { FailedPaymentEvent, FailureCode, PaymentMethod, CustomerProfile } from '../types';

const INDIAN_FIRST_NAMES = [
  'Aarav', 'Priya', 'Rohan', 'Ananya', 'Vikram', 'Sneha', 'Aditya', 'Meera',
  'Kabir', 'Tanvi', 'Rahul', 'Pooja', 'Arjun', 'Isha', 'Karthik', 'Divya',
  'Nikhil', 'Shreya', 'Siddharth', 'Ritu', 'Manish', 'Neha', 'Gaurav', 'Deepa'
];

const INDIAN_LAST_NAMES = [
  'Sharma', 'Verma', 'Patel', 'Iyer', 'Reddy', 'Nair', 'Mehta', 'Gupta',
  'Chatterjee', 'Deshmukh', 'Kulkarni', 'Bose', 'Menon', 'Singh', 'Chopra', 'Rao'
];

const MERCHANTS = [
  { name: 'FreshGrocer D2C', category: 'D2C E-commerce' as const, baseAmt: [899, 1499, 2999] },
  { name: 'Klassmate EdTech', category: 'EdTech' as const, baseAmt: [4999, 9999, 14999] },
  { name: 'CloudScale SaaS', category: 'SaaS' as const, baseAmt: [2499, 6999, 19999] },
  { name: 'StreamFlix OTT', category: 'Subscription / OTT' as const, baseAmt: [499, 799, 1199] },
  { name: 'LogiMatrix B2B', category: 'Fintech B2B' as const, baseAmt: [12500, 24000, 48000] },
  { name: 'UrbanFit Activewear', category: 'D2C E-commerce' as const, baseAmt: [1299, 2499, 3999] },
  { name: 'DataPulse Analytics', category: 'SaaS' as const, baseAmt: [3999, 8999, 28000] }
];

const FAILURE_METADATA: Record<FailureCode, { method: PaymentMethod; messages: string[] }> = {
  INSUFFICIENT_FUNDS: {
    method: 'UPI',
    messages: [
      'PSP_ERROR: U30 - Insufficient funds in customer bank account',
      'BANK_DECLINED: Balance check failed during auto-debit intent',
      'DEBIT_FAILED: Account balance lower than mandate transaction amount'
    ]
  },
  BANK_DOWNTIME: {
    method: 'UPI',
    messages: [
      'NPCI_TIMEOUT: Remitter bank CBS unresponsive during processing',
      'GATEWAY_ERROR: HDFC / SBI UPI switch experiencing 85% packet drop',
      'PSP_UNAVAILABLE: Axis Bank host down for scheduled maintenance'
    ]
  },
  GATEWAY_TIMEOUT: {
    method: 'NETBANKING',
    messages: [
      'TIMEOUT: Bank netbanking portal session expired before authorization',
      'HTTP_504: Gateway gateway timeout from partner acquiring bank',
      'AUTH_DELAY: Two-factor callback not received within 180 seconds'
    ]
  },
  MANDATE_EXPIRED: {
    method: 'MANDATE',
    messages: [
      'MANDATE_ERROR: e-NACH customer debit mandate expired on 2026-08-15',
      'RECURRING_FAILED: UPI Autopay mandate validity period lapsed',
      'INACTIVE_MANDATE: Maximum transaction count reached for recurring mandate'
    ]
  },
  USER_DROP_OFF: {
    method: 'CARD',
    messages: [
      'USER_ABANDONED: Customer dismissed Razorpay standard checkout iframe',
      'OTP_TIMEOUT: Customer did not enter 3D-Secure SMS OTP',
      'FLOW_CANCELLED: User clicked back button during payment selection'
    ]
  },
  CARD_EXPIRED: {
    method: 'CARD',
    messages: [
      'CARD_DECLINED: Card expiry date 07/26 is in the past',
      'AUTH_ERROR: Card flagged as expired by issuer bank',
      'TOKEN_INVALID: Saved card cryptogram expired, token update required'
    ]
  },
  LIMIT_EXCEEDED: {
    method: 'UPI',
    messages: [
      'LIMIT_EXCEEDED: Daily UPI transfer limit of INR 100,000 reached',
      'BANK_LIMIT: Single transaction threshold exceeded for new account',
      'POLICY_RESTRICTION: Beneficiary limit cap reached for today'
    ]
  }
};

export function generateSyntheticFailedBatch(count: number = 60): FailedPaymentEvent[] {
  const events: FailedPaymentEvent[] = [];
  const failureCodes: FailureCode[] = [
    'INSUFFICIENT_FUNDS', // High frequency (30%)
    'INSUFFICIENT_FUNDS',
    'BANK_DOWNTIME',      // 20%
    'BANK_DOWNTIME',
    'MANDATE_EXPIRED',    // 20%
    'USER_DROP_OFF',      // 15%
    'GATEWAY_TIMEOUT',    // 10%
    'CARD_EXPIRED',       // 5%
    'LIMIT_EXCEEDED'      // 5%
  ];

  const now = new Date();

  for (let i = 0; i < count; i++) {
    const firstName = INDIAN_FIRST_NAMES[i % INDIAN_FIRST_NAMES.length];
    const lastName = INDIAN_LAST_NAMES[(i * 3) % INDIAN_LAST_NAMES.length];
    const merchant = MERCHANTS[i % MERCHANTS.length];
    const failureCode = failureCodes[i % failureCodes.length];
    const meta = FAILURE_METADATA[failureCode];
    const amount = merchant.baseAmt[i % merchant.baseAmt.length];

    const pastTx = (i * 7) % 25;
    const loyaltyTier = pastTx > 12 ? 'VIP' : pastTx > 3 ? 'REGULAR' : 'NEW';

    const customer: CustomerProfile = {
      id: `cust_${Math.random().toString(36).substring(2, 9)}`,
      name: `${firstName} ${lastName}`,
      phone: `+91 98${Math.floor(10000000 + Math.random() * 90000000)}`,
      email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@example.com`,
      loyaltyTier,
      pastSuccessfulTransactions: pastTx,
      salaryDayEstimate: (i % 3 === 0) ? 1 : (i % 3 === 1) ? 5 : 28
    };

    // Stagger timestamps over past 24 hours
    const minutesAgo = Math.floor(Math.random() * 1440);
    const eventTime = new Date(now.getTime() - minutesAgo * 60 * 1000).toISOString();

    const rawMessage = meta.messages[i % meta.messages.length];

    events.push({
      id: `pay_${Math.random().toString(36).substring(2, 11)}`,
      merchantId: `acc_${merchant.name.toLowerCase().replace(/[^a-z]/g, '')}`,
      merchantName: merchant.name,
      merchantCategory: merchant.category,
      amount,
      currency: 'INR',
      paymentMethod: meta.method,
      failureCode,
      rawFailureMessage: rawMessage,
      timestamp: eventTime,
      customer,
      attemptCount: 1,
      status: 'FAILED'
    });
  }

  // Sort chronologically descending
  return events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
}
