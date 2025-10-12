import api from './api';
import { ENDPOINTS } from './endpoints';

export interface Vendor {
  id: number;
  name: string;
  email: string;
  phone: string;
  pincode: string;
  rating: number;
  total_jobs: number;
  availability: {
    day_of_week: string;
    start_time: string;
    end_time: string;
  } | null;
  travel_time: number;
  distance_km: number;
  primary_service_area: string;
}

export interface VendorSearchResponse {
  vendors: Vendor[];
  total_vendors: number;
  pincode: string;
  demand_index: number;
}

export interface DemandDetails {
  level: string;
  demand_ratio: number;
  total_bookings: number;
  pending_bookings: number;
}

export interface SupplyDetails {
  level: string;
  available_vendors: number;
  busy_vendors: number;
  effective_vendors: number;
}

export interface PerformanceDetails {
  completion_rate: number;
  avg_satisfaction: number;
  has_data: boolean;
}

export interface DynamicPriceBreakdown {
  base_price: number;
  final_price: number;
  price_change_percent: number;
  factors: {
    demand: {
      level: string;
      multiplier: number;
      details: DemandDetails;
    };
    supply: {
      level: string;
      multiplier: number;
      details: SupplyDetails;
    };
    time: {
      factors: string[];
      multiplier: number;
    };
    performance: {
      multiplier: number;
      details: PerformanceDetails;
    };
  };
  total_multiplier: number;
  surge_info: {
    level: number;
    label: string;
    reasons: string[];
  };
}

export interface PricingSuggestions {
  current_price: DynamicPriceBreakdown;
  cheapest_date: string;
  cheapest_price: number;
  savings: number;
  best_times: Record<string, string>;
  recommendations: Array<{
    type: string;
    message: string;
    savings: number;
  }>;
}

export interface Photo {
  id: string;
  image: string;
  image_type: 'before' | 'after' | 'additional';
  description: string;
  uploaded_at: string;
  uploaded_by: {
    id: string;
    name: string;
  };
}

export const vendorService = {
  /**
   * Search vendors by pincode
   * @param pincode - The pincode to search vendors in
   * @param serviceId - Optional service ID to filter vendors
   * @returns Promise with vendor search results
   */
  searchVendors: async (pincode: string, serviceId?: number): Promise<VendorSearchResponse> => {
    try {
      const params: Record<string, string | number> = { pincode };
      if (serviceId) {
        params.service_id = serviceId;
      }
      
      const response = await api.get(ENDPOINTS.VENDOR.SEARCH, { params });
      return response.data;
    } catch (error) {
      throw new Error('Failed to search vendors');
    }
  },

  /**
   * Get vendor details by ID
   * @param vendorId - The ID of the vendor
   * @returns Promise with vendor details
   */
  getVendor: async (vendorId: number): Promise<Vendor> => {
    try {
      const response = await api.get(`/api/users/${vendorId}/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch vendor details');
    }
  },
};

// Add new interface for signature logs
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

export const onboardService = {
  /**
   * Get signature logs for a vendor application
   * @param applicationId - The ID of the vendor application
   * @returns Promise with signature logs
   */
  getSignatureLogs: async (applicationId: string): Promise<SignatureLog[]> => {
    try {
      const response = await api.get(`/api/onboard/vendors/${applicationId}/signature_logs/`);
      return response.data.signatures || [];
    } catch (error) {
      throw new Error('Failed to fetch signature logs');
    }
  },

  /**
   * Get edit history for a vendor application
   * @param applicationId - The ID of the vendor application
   * @returns Promise with edit history
   */
  getEditHistory: async (applicationId: string): Promise<AuditLog[]> => {
    try {
      const response = await api.get(`/api/onboard/vendors/${applicationId}/edit_history/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch edit history');
    }
  },
};

export const pricingService = {
  /**
   * Calculate dynamic price for a service
   * @param serviceId - The service ID
   * @param pincode - The customer pincode
   * @param scheduledDatetime - Optional scheduled datetime
   * @returns Promise with dynamic price breakdown
   */
  calculatePrice: async (
    serviceId: number, 
    pincode: string, 
    scheduledDatetime?: string
  ): Promise<DynamicPriceBreakdown> => {
    try {
      const params: Record<string, string | number> = {
        service_id: serviceId,
        pincode
      };
      
      if (scheduledDatetime) {
        params.scheduled_datetime = scheduledDatetime;
      }
      
      const response = await api.get(ENDPOINTS.PRICING.CALCULATE, { params });
      return response.data;
    } catch (error) {
      throw new Error('Failed to calculate dynamic price');
    }
  },

  /**
   * Get pricing suggestions for a service
   * @param serviceId - The service ID
   * @param pincode - The customer pincode
   * @returns Promise with pricing suggestions
   */
  getPriceSuggestions: async (
    serviceId: number, 
    pincode: string
  ): Promise<PricingSuggestions> => {
    try {
      const response = await api.post(ENDPOINTS.PRICING.PREDICT, {
        service_id: serviceId,
        pincode,
        days: 7
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to get pricing suggestions');
    }
  },
};

export const photoService = {
  /**
   * Upload photos for a booking
   * @param bookingId - The booking ID
   * @param photos - Array of photo files
   * @param imageType - Type of photos (before/after/additional)
   * @param description - Optional description
   * @returns Promise with upload results
   */
  uploadPhotos: async (
    bookingId: string,
    photos: File[],
    imageType: 'before' | 'after' | 'additional',
    description?: string
  ): Promise<Photo[]> => {
    try {
      const formData = new FormData();
      
      photos.forEach((photo) => {
        formData.append('images', photo);
      });
      
      formData.append('booking', bookingId);
      formData.append('image_type', imageType);
      if (description) {
        formData.append('description', description);
      }
      
      const response = await api.post('/api/photos/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return Array.isArray(response.data) ? response.data : [response.data];
    } catch (error) {
      throw new Error('Failed to upload photos');
    }
  },

  /**
   * Get photos for a booking
   * @param bookingId - The booking ID
   * @returns Promise with photos
   */
  getBookingPhotos: async (bookingId: string): Promise<Photo[]> => {
    try {
      const response = await api.get('/api/photos/', {
        params: { booking: bookingId }
      });
      return response.data.results || response.data;
    } catch (error) {
      throw new Error('Failed to fetch booking photos');
    }
  },
};