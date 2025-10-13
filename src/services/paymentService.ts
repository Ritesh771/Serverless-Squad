import api from './api';
import { ENDPOINTS } from './endpoints';

export interface Payment {
  id: string;
  booking: string;
  amount: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'refunded';
  payment_type: 'automatic' | 'manual';
  stripe_payment_intent_id?: string;
  stripe_charge_id?: string;
  processed_by?: number;
  processed_at?: string;
  created_at: string;
  updated_at: string;
}

export const paymentService = {
  // Get user payments
  async getPayments(): Promise<Payment[]> {
    const { data } = await api.get(ENDPOINTS.PAYMENTS.LIST);
    return data.results || data;
  },

  // Get payment details
  async getPayment(id: string): Promise<Payment> {
    const { data } = await api.get(ENDPOINTS.PAYMENTS.DETAIL(id));
    return data;
  },

  // Process manual payment (ops manager)
  async processManualPayment(paymentId: string): Promise<{ message: string }> {
    const { data } = await api.post(ENDPOINTS.PAYMENTS.PROCESS_MANUAL(paymentId));
    return data;
  },
};
