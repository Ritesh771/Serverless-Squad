import api from './api';
import { ENDPOINTS } from './endpoints';

export interface Dispute {
  id: string;
  booking: string;
  customer: number;
  vendor?: number;
  customer_name?: string;
  vendor_name?: string;
  dispute_type: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'in_progress' | 'resolved' | 'escalated' | 'closed';
  customer_evidence?: any;
  vendor_evidence?: any;
  resolution_notes?: string;
  resolution_amount?: string;
  assigned_mediator?: number;
  assigned_mediator_name?: string;
  escalated_to?: number;
  created_at: string;
  resolved_at?: string;
  messages_count?: number;
}

export interface DisputeMessage {
  id: string;
  dispute: string;
  sender: number;
  sender_name: string;
  recipient?: number;
  recipient_name?: string;
  message_type: 'text' | 'file' | 'system';
  content: string;
  attachment_name?: string;
  attachment_url?: string;
  is_read: boolean;
  created_at: string;
  is_mine?: boolean;
}

export const disputeService = {
  // Create dispute
  async createDispute(
    bookingId: string,
    disputeType: string,
    title: string,
    description: string,
    evidence?: any
  ): Promise<Dispute> {
    const { data } = await api.post(ENDPOINTS.DISPUTES.CREATE, {
      booking_id: bookingId,
      dispute_type: disputeType,
      title,
      description,
      evidence,
    });
    return data;
  },

  // Get all disputes
  async getDisputes(): Promise<Dispute[]> {
    const { data } = await api.get(ENDPOINTS.DISPUTES.LIST);
    return data.results || data;
  },

  // Get dispute details
  async getDispute(disputeId: string): Promise<Dispute> {
    const { data } = await api.get(ENDPOINTS.DISPUTES.DETAIL(disputeId));
    return data;
  },

  // Get dispute messages
  async getMessages(
    disputeId: string,
    page: number = 1,
    pageSize: number = 50
  ): Promise<{
    messages: DisputeMessage[];
    total_count: number;
    page: number;
    page_size: number;
    has_more: boolean;
  }> {
    const { data } = await api.get(ENDPOINTS.DISPUTES.MESSAGES(disputeId), {
      params: { page, page_size: pageSize },
    });
    return data;
  },

  // Send message
  async sendMessage(
    disputeId: string,
    content: string,
    messageType: 'text' | 'file' = 'text',
    attachment?: File
  ): Promise<DisputeMessage> {
    const formData = new FormData();
    formData.append('content', content);
    formData.append('message_type', messageType);
    if (attachment) {
      formData.append('attachment', attachment);
    }

    const { data } = await api.post(ENDPOINTS.DISPUTES.SEND_MESSAGE(disputeId), formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data.message;
  },

  // Mark messages as read
  async markMessagesRead(disputeId: string): Promise<{ marked_count: number }> {
    const { data } = await api.post(ENDPOINTS.DISPUTES.MARK_READ(disputeId));
    return data;
  },

  // Resolve dispute (Admin)
  async resolveDispute(
    disputeId: string,
    resolutionNotes: string,
    resolutionAmount?: number,
    evidence?: any
  ): Promise<Dispute> {
    const { data } = await api.post(ENDPOINTS.DISPUTES.RESOLVE(disputeId), {
      resolution_notes: resolutionNotes,
      resolution_amount: resolutionAmount,
      evidence,
    });
    return data;
  },
};
