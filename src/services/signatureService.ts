import api from './api';
import { ENDPOINTS } from './endpoints';

export interface Signature {
  id: string;
  booking: string;
  signed_by?: number;
  status: 'pending' | 'signed' | 'expired' | 'disputed' | 'rejected';
  signature_hash?: string;
  signature_data?: any;
  satisfaction_rating?: number;
  satisfaction_comments?: string;
  requested_at: string;
  signed_at?: string;
  expires_at: string;
  docusign_envelope_id?: string;
  docusign_signing_url?: string;
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

  // Request signature from vendor
  async requestSignature(bookingId: string): Promise<{ message: string; signature_id: string }> {
    const { data } = await api.post(ENDPOINTS.ENHANCED_SIGNATURES, {
      action: 'request_signature_with_photos',
      booking_id: bookingId,
    });
    return data;
  },

  // Get DocuSign signing URL
  async getDocuSignUrl(signatureId: string): Promise<{ signing_url: string }> {
    // This would be implemented to get the DocuSign signing URL
    // For now, we'll return a placeholder
    throw new Error('DocuSign integration not fully implemented in frontend');
  },
};