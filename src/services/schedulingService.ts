import api from './api';
import { ENDPOINTS } from './endpoints';

export interface TimeSlot {
  start_time: string;
  end_time: string;
  is_available: boolean;
  score?: number;
  travel_time_minutes?: number;
  buffer_time_minutes?: number;
}

export interface OptimalSlot {
  recommended_time: string;
  score: number;
  reasoning: string;
  travel_time_minutes: number;
  estimated_duration_minutes: number;
}

export const schedulingService = {
  // Get available time slots
  async getAvailableSlots(
    vendorId: number,
    serviceId: number,
    customerPincode: string,
    preferredDate: string
  ): Promise<{ available_slots: TimeSlot[]; total_slots: number }> {
    const { data } = await api.get(ENDPOINTS.SCHEDULING.AVAILABLE_SLOTS, {
      params: {
        vendor_id: vendorId,
        service_id: serviceId,
        customer_pincode: customerPincode,
        preferred_date: preferredDate,
      },
    });
    return data;
  },

  // Get optimal booking suggestion
  async getOptimalSlot(
    vendorId: number,
    serviceId: number,
    customerPincode: string,
    preferredDate: string
  ): Promise<OptimalSlot | null> {
    const { data } = await api.post(ENDPOINTS.SCHEDULING.OPTIMAL_SLOT, {
      vendor_id: vendorId,
      service_id: serviceId,
      customer_pincode: customerPincode,
      preferred_date: preferredDate,
    });
    return data.optimal_slot;
  },

  // Get vendor schedule optimization
  async getVendorOptimization(date: string): Promise<any> {
    const { data } = await api.get(ENDPOINTS.SCHEDULING.VENDOR_OPTIMIZATION, {
      params: { date },
    });
    return data;
  },
};
