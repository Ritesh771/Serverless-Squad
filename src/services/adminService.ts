import api from './api';
import { ENDPOINTS } from './endpoints';

export const adminService = {
  // Pincode Scaling Data
  async getPincodeScalingData(filters?: {
    service_type?: string;
    days_back?: number;
  }): Promise<unknown> {
    const { data } = await api.get(ENDPOINTS.ADMIN.PINCODE_SCALING, {
      params: filters,
    });
    return data;
  },

  // Edit History
  async getEditHistory(filters?: {
    model?: string;
    user?: string;
    action?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<unknown> {
    const { data } = await api.get(ENDPOINTS.ADMIN.EDIT_HISTORY, {
      params: filters,
    });
    return data;
  },

  async exportEditHistory(filters?: Record<string, unknown>): Promise<unknown> {
    const { data } = await api.post(ENDPOINTS.ADMIN.EXPORT_HISTORY, {
      format: 'csv',
      filters,
    });
    return data;
  },

  // Dashboard Stats
  async getDashboardStats(): Promise<unknown> {
    const { data } = await api.get(ENDPOINTS.ADMIN.DASHBOARD_STATS);
    return data;
  },

  // Notification Management
  async getNotificationStats(): Promise<unknown> {
    const { data } = await api.get(ENDPOINTS.ADMIN.NOTIFICATIONS);
    return data;
  },

  async triggerManualTask(action: string): Promise<unknown> {
    const { data } = await api.post(ENDPOINTS.ADMIN.NOTIFICATIONS, {
      action,
    });
    return data;
  },

  // Notification Logs
  async getNotificationLogs(filters?: {
    type?: string;
    method?: string;
    status?: string;
    recipient_id?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    per_page?: number;
  }): Promise<unknown> {
    const { data } = await api.get(ENDPOINTS.ADMIN.NOTIFICATION_LOGS, {
      params: filters,
    });
    return data;
  },

  // Business Alerts
  async getBusinessAlerts(filters?: {
    type?: string;
    severity?: string;
    status?: string;
    page?: number;
    per_page?: number;
  }): Promise<unknown> {
    const { data } = await api.get(ENDPOINTS.ADMIN.BUSINESS_ALERTS, {
      params: filters,
    });
    return data;
  },

  // Pincode Analytics
  async getPincodeAnalytics(filters?: {
    pincode?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    per_page?: number;
  }): Promise<unknown> {
    const { data } = await api.get(ENDPOINTS.ADMIN.PINCODE_ANALYTICS, {
      params: filters,
    });
    return data;
  },

  // Advanced AI Features
  async getPincodeAIAnalytics(pincode: string, days: number = 30): Promise<unknown> {
    const { data } = await api.get(ENDPOINTS.AI.PINCODE_ANALYTICS, {
      params: { pincode, days },
    });
    return data;
  },

  async getAdvancedDisputeResolution(disputeId: string): Promise<unknown> {
    const { data } = await api.get(ENDPOINTS.AI.DISPUTE_RESOLUTION(disputeId));
    return data;
  },

  async getAdvancedVendorBonus(vendorId?: number, days: number = 30): Promise<unknown> {
    const params: Record<string, unknown> = { days };
    if (vendorId) {
      params.vendor_id = vendorId;
    }
    const { data } = await api.get(ENDPOINTS.AI.VENDOR_BONUS, { params });
    return data;
  },
};