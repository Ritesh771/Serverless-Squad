import api from './api';
import { ENDPOINTS } from './endpoints';

export interface VendorSearchResult {
  id: number;
  name: string;
  email: string;
  phone: string;
  pincode: string;
  rating: number;
  total_jobs: number;
  availability: {
    day_of_week: number;
    start_time: string;
    end_time: string;
  } | null;
  travel_time: number;
  distance_km: number;
  primary_service_area: string;
}

export interface VendorSearchResponse {
  vendors: VendorSearchResult[];
  total_vendors: number;
  pincode: string;
  demand_index: number;
}

export interface VendorApplication {
  id: string;
  user: number;
  user_email: string;
  user_phone: string;
  status: 'pending' | 'approved' | 'rejected';
  documents: any;
  experience_years: number;
  skills: string[];
  preferred_pincodes: string[];
  ai_risk_score?: number;
  ai_flags?: any;
  submitted_at: string;
  reviewed_at?: string;
  reviewed_by?: number;
}

export interface VendorAvailability {
  id: number;
  vendor: number;
  vendor_name: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  is_active: boolean;
  primary_pincode: string;
  service_area_pincodes: string[];
  preferred_buffer_minutes: number;
  created_at: string;
  updated_at: string;
}

export interface VendorEarnings {
  total_earnings: number;
  pending_earnings: number;
  completed_jobs: number;
  average_rating: number;
  earnings_by_month: Array<{
    month: string;
    earnings: number;
    jobs: number;
  }>;
}

export interface VendorPerformance {
  id: number;
  vendor: number;
  total_jobs: number;
  completed_jobs: number;
  cancelled_jobs: number;
  total_ratings: number;
  rating_sum: number;
  disputes_raised: number;
  disputes_against: number;
  on_time_completions: number;
  total_completions: number;
  bonus_points: number;
  tier: 'bronze' | 'silver' | 'gold';
  last_calculated: string;
  created_at: string;
  vendor_name: string;
  avg_rating: number;
  completion_rate: number;
  on_time_rate: number;
  dispute_rate: number;
}

export interface VendorDashboardData {
  stats: {
    total_jobs: number;
    completed_jobs: number;
    pending_jobs: number;
    cancelled_jobs: number;
    total_earnings: number;
    pending_earnings: number;
    average_rating: number;
    completion_rate: number;
  };
  performance_metrics: {
    completion_rate: number;
    average_response_time: number;
    customer_satisfaction: number;
    signature_success_rate: number;
    total_jobs: number;
    on_time_percentage: number;
  };
  todays_schedule: Array<{
    id: string;
    service_name: string;
    customer_name: string;
    scheduled_time: string;
    status: string;
    pincode: string;
    estimated_duration: number;
  }>;
  recent_activity: Array<{
    id: string;
    type: 'booking' | 'payment' | 'signature';
    description: string;
    timestamp: string;
    amount?: number;
  }>;
}

export interface VendorJob {
  id: string;
  service_name: string;
  customer_name: string;
  customer_phone: string;
  scheduled_date: string;
  scheduled_time: string;
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled';
  pincode: string;
  address: string;
  estimated_duration: number;
  travel_time_to_location: number;
  travel_time_from_location: number;
  buffer_before: number;
  buffer_after: number;
  total_estimated_time: number;
  photos: Array<{
    id: string;
    url: string;
    photo_type: 'before' | 'after' | 'during';
    uploaded_at: string;
  }>;
  signature_requested: boolean;
  signature_status?: 'pending' | 'signed' | 'expired' | 'disputed';
}

export interface VendorEarningsSummary {
  summary: {
    total_earnings: number;
    pending_earnings: number;
    completed_jobs: number;
    average_rating: number;
  };
  earnings_by_month: Array<{
    month: string;
    earnings: number;
    jobs: number;
  }>;
  recent_transactions: Array<{
    id: string;
    booking_id: string;
    service: string;
    amount: number;
    status: string;
    release_date?: string;
    created_at: string;
  }>;
}

export interface SignatureLog {
  id: string;
  booking: {
    id: string;
    service: {
      name: string;
    };
  };
  customer: {
    get_full_name: string;
  };
  status: 'pending' | 'signed' | 'expired' | 'disputed';
  signature_hash?: string;
  satisfaction_rating?: number;
  requested_at: string;
  signed_at?: string;
  expires_at: string;
}

export interface AuditLog {
  id: string;
  user: string;
  action: string;
  timestamp: string;
  old_values: Record<string, string | number | boolean | null>;
  new_values: Record<string, string | number | boolean | null>;
}

export const vendorService = {
  // Search vendors by pincode
  async searchVendors(
    pincode: string,
    serviceId?: number
  ): Promise<VendorSearchResponse> {
    const params: any = { pincode };
    if (serviceId) {
      params.service_id = serviceId;
    }

    const { data } = await api.get(ENDPOINTS.VENDOR.SEARCH, { params });
    return data;
  },

  // Get vendor applications (Onboard Manager)
  async getApplications(status?: string): Promise<VendorApplication[]> {
    const params = status ? { status } : {};
    const { data } = await api.get(ENDPOINTS.VENDOR.APPLICATIONS, { params });
    return data.results || data;
  },

  // Get vendor application details
  async getApplication(id: string): Promise<VendorApplication> {
    const { data } = await api.get(ENDPOINTS.VENDOR.APPLICATION_DETAIL(id));
    return data;
  },

  // Approve vendor application
  async approveApplication(id: string): Promise<{ message: string }> {
    const { data } = await api.post(ENDPOINTS.VENDOR.APPROVE_APPLICATION(id));
    return data;
  },

  // Reject vendor application
  async rejectApplication(id: string, reason: string): Promise<{ message: string }> {
    const { data } = await api.post(ENDPOINTS.VENDOR.REJECT_APPLICATION(id), { reason });
    return data;
  },

  // Get vendor availability
  async getAvailability(): Promise<VendorAvailability[]> {
    const { data } = await api.get(ENDPOINTS.VENDOR.AVAILABILITY);
    return data.results || data;
  },

  // Create/update vendor availability
  async updateAvailability(availability: Partial<VendorAvailability>): Promise<VendorAvailability> {
    const { data } = await api.post(ENDPOINTS.VENDOR.AVAILABILITY, availability);
    return data;
  },

  // Get vendor earnings
  async getEarnings(): Promise<VendorEarnings> {
    const { data } = await api.get(ENDPOINTS.VENDOR.EARNINGS);
    return data;
  },

  // Get vendor performance metrics
  async getPerformance(): Promise<VendorPerformance> {
    const { data } = await api.get(ENDPOINTS.VENDOR.PERFORMANCE);
    return data;
  },

  // Get vendor dashboard data
  async getDashboard(): Promise<VendorDashboardData> {
    const { data } = await api.get(ENDPOINTS.VENDOR.DASHBOARD);
    return data;
  },

  // Get vendor jobs for job management
  async getJobs(status?: string): Promise<VendorJob[]> {
    const params = status ? { status } : {};
    const { data } = await api.get(ENDPOINTS.VENDOR.JOB_MANAGEMENT, { params });
    return data.jobs || data;
  },

  // Accept a job
  async acceptJob(jobId: string): Promise<{ message: string }> {
    const { data } = await api.post(`${ENDPOINTS.VENDOR.JOB_MANAGEMENT}${jobId}/accept/`);
    return data;
  },

  // Decline a job
  async declineJob(jobId: string, reason: string): Promise<{ message: string }> {
    const { data } = await api.post(`${ENDPOINTS.VENDOR.JOB_MANAGEMENT}${jobId}/decline/`, { reason });
    return data;
  },

  // Start a job (mark as in progress)
  async startJob(jobId: string): Promise<{ message: string }> {
    const { data } = await api.post(`${ENDPOINTS.VENDOR.JOB_MANAGEMENT}${jobId}/start/`);
    return data;
  },

  // Complete a job
  async completeJob(jobId: string): Promise<{ message: string }> {
    const { data } = await api.post(`${ENDPOINTS.VENDOR.JOB_MANAGEMENT}${jobId}/complete/`);
    return data;
  },

  // Upload photos for a job
  async uploadPhotos(jobId: string, photos: FormData): Promise<{ message: string }> {
    const { data } = await api.post(`${ENDPOINTS.VENDOR.JOB_MANAGEMENT}${jobId}/upload_photos/`, photos, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  // Request signature for a completed job
  async requestSignature(jobId: string): Promise<{ message: string }> {
    const { data } = await api.post(`${ENDPOINTS.VENDOR.JOB_MANAGEMENT}${jobId}/request_signature/`);
    return data;
  },

  // Get vendor earnings summary
  async getEarningsSummary(): Promise<VendorEarningsSummary> {
    const { data } = await api.get(ENDPOINTS.VENDOR.EARNINGS_SUMMARY);
    return data;
  },
};

// Onboard Manager Service
export const onboardService = {
  // Get vendor applications
  async getApplications(status?: string): Promise<VendorApplication[]> {
    const params = status ? { status } : {};
    const { data } = await api.get(ENDPOINTS.VENDOR.APPLICATIONS, { params });
    return data.results || data;
  },

  // Get vendor application details
  async getApplication(id: string): Promise<VendorApplication> {
    const { data } = await api.get(ENDPOINTS.VENDOR.APPLICATION_DETAIL(id));
    return data;
  },

  // Approve vendor application
  async approveApplication(id: string): Promise<{ message: string }> {
    const { data } = await api.post(ENDPOINTS.VENDOR.APPROVE_APPLICATION(id));
    return data;
  },

  // Reject vendor application
  async rejectApplication(id: string, reason: string): Promise<{ message: string }> {
    const { data } = await api.post(ENDPOINTS.VENDOR.REJECT_APPLICATION(id), { reason });
    return data;
  },

  // Get signature logs for a vendor application (for compliance)
  async getSignatureLogs(applicationId: string): Promise<SignatureLog[]> {
    try {
      const { data } = await api.get(`/api/vendor-applications/${applicationId}/signature_logs/`);
      return data.signatures || [];
    } catch (error) {
      console.error('Failed to fetch signature logs:', error);
      return [];
    }
  },

  // Get edit history for a vendor application (audit trail)
  async getEditHistory(applicationId: string): Promise<AuditLog[]> {
    try {
      const { data } = await api.get(`/api/vendor-applications/${applicationId}/edit_history/`);
      return data.audit_logs || data;
    } catch (error) {
      console.error('Failed to fetch edit history:', error);
      return [];
    }
  },

  // Update vendor application (edit-only mode with audit logging)
  async updateApplication(id: string, updates: Partial<VendorApplication>): Promise<VendorApplication> {
    const { data } = await api.patch(ENDPOINTS.VENDOR.APPLICATION_DETAIL(id), updates);
    return data;
  },
};