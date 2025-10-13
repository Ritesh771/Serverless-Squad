import api from './api';
import { ENDPOINTS } from './endpoints';

export interface Signature {
  id: string;
  booking: string;
  signed_by?: number;
  status: 'pending' | 'signed' | 'expired' | 'disputed';
  signature_hash?: string;
  signature_data?: any;
  satisfaction_rating?: number;
  satisfaction_comments?: string;
  requested_at: string;
  signed_at?: string;
  expires_at: string;
}

export const signatureService = {
  // Get all signatures for current user
  async getSignatures(): Promise<Signature[]> {
    const { data } = await api.get(ENDPOINTS.SIGNATURES.LIST);
    return data.results || data;
  },

  // Get signature details
  async getSignature(id: string): Promise<Signature> {
    const { data } = await api.get(ENDPOINTS.SIGNATURES.DETAIL(id));
    return data;
  },

  // Sign a booking
  async signBooking(
    signatureId: string,
    satisfactionRating: number,
    comments?: string
  ): Promise<{ message: string; signature_hash: string }> {
    const { data } = await api.post(ENDPOINTS.SIGNATURES.SIGN(signatureId), {
      satisfaction_rating: satisfactionRating,
      comments: comments || '',
    });
    return data;
  },
};
