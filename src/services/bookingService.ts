import api from './api';
import { ENDPOINTS } from './endpoints';

export interface Service {
  id: number;
  name: string;
  description: string;
  base_price: string;
  category: string;
  duration_minutes: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Booking {
  id: string;
  customer: number;
  customer_name?: string;
  vendor?: number;
  vendor_name?: string;
  service: number;
  service_name?: string;
  service_details?: Service;
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'signed' | 'cancelled' | 'disputed';
  total_price: string;
  pincode: string;
  scheduled_date: string;
  completion_date?: string;
  customer_notes?: string;
  vendor_notes?: string;
  created_at: string;
  updated_at: string;
  estimated_service_duration_minutes?: number;
  travel_time_to_location_minutes?: number;
  travel_time_from_location_minutes?: number;
  buffer_before_minutes?: number;
  buffer_after_minutes?: number;
  actual_start_time?: string;
  actual_end_time?: string;
  dynamic_price_breakdown?: any;
}

export interface CreateBookingDTO {
  service: number;
  pincode: string;
  scheduled_date: string;
  customer_notes?: string;
  total_price?: string;
}

export const bookingService = {
  // Get all services
  async getServices(category?: string): Promise<Service[]> {
    const params = category ? { category } : {};
    const { data } = await api.get(ENDPOINTS.SERVICES.LIST, { params });
    return data.results || data;
  },

  // Get service by ID
  async getService(id: number): Promise<Service> {
    const { data } = await api.get(ENDPOINTS.SERVICES.DETAIL(id));
    return data;
  },

  // Get all bookings for current user
  async getBookings(filters?: { status?: string; pincode?: string }): Promise<Booking[]> {
    const { data } = await api.get(ENDPOINTS.BOOKINGS.LIST, { params: filters });
    return data.results || data;
  },

  // Get single booking
  async getBooking(id: string): Promise<Booking> {
    const { data } = await api.get(ENDPOINTS.BOOKINGS.DETAIL(id));
    return data;
  },

  // Create booking (Customer)
  async createBooking(booking: CreateBookingDTO): Promise<Booking> {
    const { data } = await api.post(ENDPOINTS.BOOKINGS.CREATE, booking);
    return data;
  },

  // Accept booking (Vendor)
  async acceptBooking(id: string): Promise<{ message: string }> {
    const { data } = await api.post(ENDPOINTS.BOOKINGS.ACCEPT(id));
    return data;
  },

  // Complete booking (Vendor)
  async completeBooking(id: string): Promise<{ message: string; payment_intent: any }> {
    const { data } = await api.post(ENDPOINTS.BOOKINGS.COMPLETE(id));
    return data;
  },

  // Request signature (Vendor)
  async requestSignature(id: string): Promise<{ message: string; signature_id: string }> {
    const { data } = await api.post(ENDPOINTS.BOOKINGS.REQUEST_SIGNATURE(id));
    return data;
  },

  // Update booking
  async updateBooking(id: string, updates: Partial<Booking>): Promise<Booking> {
    const { data } = await api.patch(ENDPOINTS.BOOKINGS.UPDATE(id), updates);
    return data;
  },

  // Cancel booking
  async cancelBooking(id: string): Promise<Booking> {
    const { data } = await api.patch(ENDPOINTS.BOOKINGS.UPDATE(id), { status: 'cancelled' });
    return data;
  },
};
