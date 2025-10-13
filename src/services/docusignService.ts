import api from './api';
import { ENDPOINTS } from './endpoints';

export interface DocuSignEnvelope {
  envelopeId: string;
  status: string;
  createdDate: string;
  sentDate?: string;
  completedDate?: string;
}

export const docusignService = {
  // Create a DocuSign envelope for a booking
  async createEnvelope(bookingId: string): Promise<DocuSignEnvelope> {
    try {
      const { data } = await api.post(ENDPOINTS.DOCUSIGN.ENVELOPES, {
        booking_id: bookingId,
      });
      return data;
    } catch (error) {
      throw new Error(`Failed to create DocuSign envelope: ${error}`);
    }
  },

  // Get envelope status
  async getEnvelopeStatus(envelopeId: string): Promise<DocuSignEnvelope> {
    try {
      const { data } = await api.get(ENDPOINTS.DOCUSIGN.ENVELOPE_STATUS(envelopeId));
      return data;
    } catch (error) {
      throw new Error(`Failed to get envelope status: ${error}`);
    }
  },

  // Redirect to DocuSign signing URL
  redirectToSigning(envelopeId: string): void {
    // In a real implementation, this would redirect to the DocuSign signing ceremony
    const signingUrl = `https://demo.docusign.net/signing/start/${envelopeId}`;
    window.open(signingUrl, '_blank');
  },
};