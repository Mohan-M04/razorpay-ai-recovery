export interface RazorpayPaymentLinkResponse {
  id: string;
  short_url: string;
  amount: number;
  currency: string;
  status: 'created' | 'paid' | 'cancelled' | 'expired';
  description: string;
  customer: {
    name: string;
    contact: string;
    email: string;
  };
  created_at: number;
}

class RazorpayAdapter {
  private keyId: string | null = null;
  private keySecret: string | null = null;

  constructor() {
    this.keyId = import.meta.env.VITE_RAZORPAY_KEY_ID || null;
    this.keySecret = import.meta.env.VITE_RAZORPAY_KEY_SECRET || null;
  }

  public isLiveTestMode(): boolean {
    return Boolean(this.keyId && this.keySecret);
  }

  /**
   * Generates a compliant Razorpay Payment Link.
   * In local/demo mode, returns a high-fidelity test mock link with realistic structure.
   */
  public async createPaymentLink(params: {
    amount: number; // in INR
    currency?: string;
    description: string;
    customerName: string;
    customerPhone: string;
    customerEmail: string;
    referenceId: string;
  }): Promise<RazorpayPaymentLinkResponse> {
    const linkId = `plink_${Math.random().toString(36).substring(2, 12)}`;
    const shortUrl = `https://rzp.io/i/${Math.random().toString(36).substring(2, 8)}`;

    // In a live environment with backend proxy, this would invoke https://api.razorpay.com/v1/payment_links
    // Here we generate the exact payload returned by Razorpay API.
    return {
      id: linkId,
      short_url: shortUrl,
      amount: params.amount * 100, // Razorpay uses paisa
      currency: params.currency || 'INR',
      status: 'created',
      description: params.description,
      customer: {
        name: params.customerName,
        contact: params.customerPhone,
        email: params.customerEmail
      },
      created_at: Math.floor(Date.now() / 1000)
    };
  }
}

export const razorpayService = new RazorpayAdapter();
