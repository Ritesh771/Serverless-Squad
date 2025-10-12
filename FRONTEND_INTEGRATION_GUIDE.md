# HomeServe Pro - Complete Frontend Integration Guide

## Table of Contents
1. [Overview](#overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [API Integration Patterns](#api-integration-patterns)
4. [Role-Based Features](#role-based-features)
5. [WebSocket Integration](#websocket-integration)
6. [Complete API Reference](#complete-api-reference)
7. [State Management](#state-management)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)

---

## Overview

### Base Configuration

```typescript
// src/config/api.ts
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
};

// API Client Setup
import axios from 'axios';

const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor - Add JWT Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor - Handle Token Refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const { data } = await axios.post(`${API_CONFIG.BASE_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });

        localStorage.setItem('access_token', data.access);
        originalRequest.headers.Authorization = `Bearer ${data.access}`;

        return apiClient(originalRequest);
      } catch (refreshError) {
        // Redirect to login
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

---

## Authentication & Authorization

### 1. Login Flow

```typescript
// src/services/authService.ts
import apiClient from '@/config/api';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    username: string;
    email: string;
    role: 'customer' | 'vendor' | 'onboard_manager' | 'ops_manager' | 'super_admin';
    is_verified: boolean;
  };
}

export const authService = {
  // Standard Login
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const { data } = await apiClient.post('/auth/login/', credentials);
    
    // Store tokens
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  },

  // OTP-based Login (Email)
  async sendOTP(identifier: string, method: 'email' | 'sms' = 'email') {
    const payload = method === 'email' 
      ? { email: identifier, method: 'email' }
      : { phone: identifier, method: 'sms' };
    
    const { data } = await apiClient.post('/auth/send-otp/', payload);
    return data;
  },

  // Verify OTP
  async verifyOTP(identifier: string, otp: string, method: 'email' | 'sms' = 'email'): Promise<LoginResponse> {
    const payload = method === 'email'
      ? { email: identifier, otp }
      : { phone: identifier, otp };
    
    const { data } = await apiClient.post('/auth/verify-otp/', payload);
    
    // Store tokens
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  },

  // Vendor OTP Login
  async sendVendorOTP(identifier: string, method: 'email' | 'sms' = 'email') {
    const payload = method === 'email'
      ? { email: identifier, method: 'email' }
      : { phone: identifier, method: 'sms' };
    
    const { data } = await apiClient.post('/auth/vendor/send-otp/', payload);
    return data;
  },

  async verifyVendorOTP(identifier: string, otp: string, method: 'email' | 'sms' = 'email'): Promise<LoginResponse> {
    const payload = method === 'email'
      ? { email: identifier, otp }
      : { phone: identifier, otp };
    
    const { data } = await apiClient.post('/auth/vendor/verify-otp/', payload);
    
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  },

  // Logout
  logout() {
    localStorage.clear();
    window.location.href = '/login';
  },

  // Get Current User
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },
};
```

### 2. Protected Route Component

```typescript
// src/components/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { authService } from '@/services/authService';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles = [],
}) => {
  const user = authService.getCurrentUser();

  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

// Usage in App.tsx
<Route
  path="/customer/*"
  element={
    <ProtectedRoute allowedRoles={['customer']}>
      <CustomerDashboard />
    </ProtectedRoute>
  }
/>
```

---

## API Integration Patterns

### 1. Customer Booking Service

```typescript
// src/services/bookingService.ts
import apiClient from '@/config/api';

export interface Booking {
  id: string;
  customer: number;
  vendor?: number;
  service: number;
  service_name?: string;
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'signed' | 'cancelled' | 'disputed';
  total_price: string;
  pincode: string;
  scheduled_date: string;
  completion_date?: string;
  customer_notes?: string;
  vendor_notes?: string;
  created_at: string;
  updated_at: string;
  // Smart buffering fields
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
  total_price?: string; // Optional - will be calculated dynamically
}

export const bookingService = {
  // Get all bookings for current user
  async getBookings(filters?: { status?: string; pincode?: string }): Promise<Booking[]> {
    const { data } = await apiClient.get('/api/bookings/', { params: filters });
    return data.results || data;
  },

  // Get single booking
  async getBooking(id: string): Promise<Booking> {
    const { data } = await apiClient.get(`/api/bookings/${id}/`);
    return data;
  },

  // Create booking (Customer)
  async createBooking(booking: CreateBookingDTO): Promise<Booking> {
    const { data } = await apiClient.post('/api/bookings/', booking);
    return data;
  },

  // Accept booking (Vendor)
  async acceptBooking(id: string): Promise<{ message: string }> {
    const { data } = await apiClient.post(`/api/bookings/${id}/accept_booking/`);
    return data;
  },

  // Complete booking (Vendor)
  async completeBooking(id: string): Promise<{ message: string; payment_intent: any }> {
    const { data } = await apiClient.post(`/api/bookings/${id}/complete_booking/`);
    return data;
  },

  // Request signature (Vendor)
  async requestSignature(id: string): Promise<{ message: string; signature_id: string }> {
    const { data } = await apiClient.post(`/api/bookings/${id}/request_signature/`);
    return data;
  },

  // Update booking
  async updateBooking(id: string, updates: Partial<Booking>): Promise<Booking> {
    const { data } = await apiClient.patch(`/api/bookings/${id}/`, updates);
    return data;
  },

  // Cancel booking
  async cancelBooking(id: string): Promise<Booking> {
    const { data } = await apiClient.patch(`/api/bookings/${id}/`, { status: 'cancelled' });
    return data;
  },
};
```

### 2. Service Management

```typescript
// src/services/serviceService.ts
import apiClient from '@/config/api';

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

export const serviceService = {
  // Get all services
  async getServices(category?: string): Promise<Service[]> {
    const params = category ? { category } : {};
    const { data } = await apiClient.get('/api/services/', { params });
    return data.results || data;
  },

  // Get service by ID
  async getService(id: number): Promise<Service> {
    const { data } = await apiClient.get(`/api/services/${id}/`);
    return data;
  },

  // Get service categories
  async getCategories(): Promise<string[]> {
    const services = await this.getServices();
    return [...new Set(services.map(s => s.category))];
  },
};
```

### 3. Dynamic Pricing Service

```typescript
// src/services/pricingService.ts
import apiClient from '@/config/api';

export interface DynamicPricing {
  service: {
    id: number;
    name: string;
    category: string;
  };
  pincode: string;
  pricing: {
    base_price: number;
    surge_multiplier: number;
    final_price: number;
    demand_level: 'low' | 'normal' | 'high' | 'peak';
    factors: {
      time_based_multiplier: number;
      demand_based_multiplier: number;
      vendor_availability_multiplier: number;
    };
    breakdown: {
      base: number;
      surge: number;
      total: number;
    };
  };
  timestamp: string;
}

export interface PricePrediction {
  service: {
    id: number;
    name: string;
    category: string;
    base_price: number;
  };
  pincode: string;
  predictions: Array<{
    date: string;
    predicted_price: number;
    surge_multiplier: number;
    confidence: number;
    demand_level: string;
  }>;
  timestamp: string;
}

export const pricingService = {
  // Get dynamic price for a service
  async getDynamicPrice(
    serviceId: number,
    pincode: string,
    scheduledDatetime?: string
  ): Promise<DynamicPricing> {
    const params: any = { service_id: serviceId, pincode };
    if (scheduledDatetime) {
      params.scheduled_datetime = scheduledDatetime;
    }

    const { data } = await apiClient.get('/api/dynamic-pricing/', { params });
    return data;
  },

  // Get price predictions for multiple days
  async getPricePredictions(
    serviceId: number,
    pincode: string,
    days: number = 7
  ): Promise<PricePrediction> {
    const { data } = await apiClient.post('/api/dynamic-pricing/', {
      service_id: serviceId,
      pincode,
      days,
    });
    return data;
  },
};
```

### 4. Smart Scheduling Service

```typescript
// src/services/schedulingService.ts
import apiClient from '@/config/api';

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
    const { data } = await apiClient.get('/api/smart-scheduling/', {
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
    const { data } = await apiClient.post('/api/smart-scheduling/', {
      vendor_id: vendorId,
      service_id: serviceId,
      customer_pincode: customerPincode,
      preferred_date: preferredDate,
    });
    return data.optimal_slot;
  },

  // Get vendor schedule optimization
  async getVendorOptimization(date: string): Promise<any> {
    const { data } = await apiClient.get('/api/vendor-optimization/', {
      params: { date },
    });
    return data;
  },
};
```

### 5. Signature Service

```typescript
// src/services/signatureService.ts
import apiClient from '@/config/api';

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
    const { data } = await apiClient.get('/api/signatures/');
    return data.results || data;
  },

  // Sign a booking
  async signBooking(
    signatureId: string,
    satisfactionRating: number,
    comments?: string
  ): Promise<{ message: string; signature_hash: string }> {
    const { data } = await apiClient.post(`/api/signatures/${signatureId}/sign/`, {
      satisfaction_rating: satisfactionRating,
      comments: comments || '',
    });
    return data;
  },

  // Enhanced signature with photos
  async requestSignatureWithPhotos(
    bookingId: string,
    photoIds: string[]
  ): Promise<{ status: string; signature_id: string; message: string }> {
    const { data } = await apiClient.post('/api/enhanced-signatures/', {
      action: 'request_signature_with_photos',
      booking_id: bookingId,
      photo_ids: photoIds,
    });
    return data;
  },

  // Reject signature
  async rejectSignature(
    signatureId: string,
    reason: string,
    evidence?: any
  ): Promise<{ status: string; dispute_id: string }> {
    const { data } = await apiClient.post('/api/enhanced-signatures/', {
      action: 'reject_signature',
      signature_id: signatureId,
      reason,
      evidence,
    });
    return data;
  },
};
```

### 6. Photo Upload Service

```typescript
// src/services/photoService.ts
import apiClient from '@/config/api';

export interface Photo {
  id: number;
  booking: string;
  image: string;
  image_type: 'before' | 'after' | 'additional';
  description?: string;
  uploaded_by: number;
  uploaded_at: string;
}

export const photoService = {
  // Upload photo
  async uploadPhoto(
    bookingId: string,
    imageType: 'before' | 'after' | 'additional',
    file: File,
    description?: string
  ): Promise<Photo> {
    const formData = new FormData();
    formData.append('booking', bookingId);
    formData.append('image_type', imageType);
    formData.append('image', file);
    if (description) {
      formData.append('description', description);
    }

    const { data } = await apiClient.post('/api/photos/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  // Get photos for a booking
  async getPhotos(bookingId: string): Promise<Photo[]> {
    const { data } = await apiClient.get('/api/photos/', {
      params: { booking: bookingId },
    });
    return data.results || data;
  },

  // Delete photo
  async deletePhoto(photoId: number): Promise<void> {
    await apiClient.delete(`/api/photos/${photoId}/`);
  },
};
```

### 7. Vendor Search Service

```typescript
// src/services/vendorSearchService.ts
import apiClient from '@/config/api';

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

export const vendorSearchService = {
  // Search vendors by pincode
  async searchVendors(
    pincode: string,
    serviceId?: number
  ): Promise<{
    vendors: VendorSearchResult[];
    total_vendors: number;
    pincode: string;
    demand_index: number;
  }> {
    const params: any = { pincode };
    if (serviceId) {
      params.service_id = serviceId;
    }

    const { data } = await apiClient.get('/api/vendor-search/', { params });
    return data;
  },
};
```

### 8. Dispute Service

```typescript
// src/services/disputeService.ts
import apiClient from '@/config/api';

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
    const { data } = await apiClient.post('/api/disputes/create_dispute/', {
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
    const { data } = await apiClient.get('/api/disputes/');
    return data.results || data;
  },

  // Get dispute details
  async getDispute(disputeId: string): Promise<Dispute> {
    const { data } = await apiClient.get(`/api/disputes/${disputeId}/`);
    return data;
  },

  // Get dispute messages
  async getMessages(disputeId: string, page: number = 1, pageSize: number = 50): Promise<{
    messages: DisputeMessage[];
    total_count: number;
    page: number;
    page_size: number;
    has_more: boolean;
  }> {
    const { data } = await apiClient.get(`/api/disputes/${disputeId}/messages/`, {
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

    const { data } = await apiClient.post(
      `/api/disputes/${disputeId}/send_message/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return data.message;
  },

  // Mark messages as read
  async markMessagesRead(disputeId: string): Promise<{ marked_count: number }> {
    const { data } = await apiClient.post(`/api/disputes/${disputeId}/mark_read/`);
    return data;
  },

  // Resolve dispute (Admin)
  async resolveDispute(
    disputeId: string,
    resolutionNotes: string,
    resolutionAmount?: number,
    evidence?: any
  ): Promise<Dispute> {
    const { data } = await apiClient.post(`/api/disputes/${disputeId}/resolve/`, {
      resolution_notes: resolutionNotes,
      resolution_amount: resolutionAmount,
      evidence,
    });
    return data;
  },
};
```

### 9. Admin Services

```typescript
// src/services/adminService.ts
import apiClient from '@/config/api';

export const adminService = {
  // Cache Management
  async getCacheStats(): Promise<any> {
    const { data } = await apiClient.get('/admin-dashboard/cache/');
    return data;
  },

  async clearCache(cacheType: string = 'all'): Promise<any> {
    const { data } = await apiClient.post('/admin-dashboard/cache/', {
      cache_type: cacheType,
    });
    return data;
  },

  // Pincode Analytics
  async getPincodeScalingData(filters?: {
    service_type?: string;
    days_back?: number;
  }): Promise<any> {
    const { data } = await apiClient.get('/admin-dashboard/pincode-scaling/data/', {
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
  }): Promise<any> {
    const { data } = await apiClient.get('/admin-dashboard/edit-history/', {
      params: filters,
    });
    return data;
  },

  async exportEditHistory(filters?: any): Promise<any> {
    const { data } = await apiClient.post('/admin-dashboard/edit-history/export/', {
      format: 'csv',
      filters,
    });
    return data;
  },

  // Dashboard Stats
  async getDashboardStats(): Promise<any> {
    const { data } = await apiClient.get('/admin-dashboard/dashboard/stats/');
    return data;
  },

  // Notification Management
  async getNotificationStats(): Promise<any> {
    const { data } = await apiClient.get('/admin-dashboard/notifications/');
    return data;
  },

  async triggerManualTask(action: string): Promise<any> {
    const { data } = await apiClient.post('/admin-dashboard/notifications/', {
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
  }): Promise<any> {
    const { data } = await apiClient.get('/admin-dashboard/notifications/logs/', {
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
  }): Promise<any> {
    const { data } = await apiClient.get('/admin-dashboard/notifications/alerts/', {
      params: filters,
    });
    return data;
  },

  // Pincode Analytics View
  async getPincodeAnalytics(filters?: {
    pincode?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    per_page?: number;
  }): Promise<any> {
    const { data } = await apiClient.get('/admin-dashboard/analytics/pincode/', {
      params: filters,
    });
    return data;
  },

  // Advanced AI Features
  async getPincodeAIAnalytics(pincode: string, days: number = 30): Promise<any> {
    const { data } = await apiClient.get('/api/pincode-ai-analytics/', {
      params: { pincode, days },
    });
    return data;
  },

  async getAdvancedDisputeResolution(disputeId: string): Promise<any> {
    const { data } = await apiClient.get(`/api/advanced-dispute-resolution/${disputeId}/`);
    return data;
  },

  async getAdvancedVendorBonus(vendorId?: number, days: number = 30): Promise<any> {
    const params: any = { days };
    if (vendorId) {
      params.vendor_id = vendorId;
    }
    const { data } = await apiClient.get('/api/advanced-vendor-bonus/', { params });
    return data;
  },
};
```

---

## WebSocket Integration

### 1. WebSocket Service Setup

```typescript
// src/services/websocketService.ts
import { API_CONFIG } from '@/config/api';

export type WebSocketEventType =
  | 'booking_status_change'
  | 'signature_request'
  | 'payment_update'
  | 'chat_message'
  | 'notification';

export interface WebSocketMessage {
  type: WebSocketEventType;
  data: any;
  timestamp: string;
}

export class WebSocketService {
  private connections: Map<string, WebSocket> = new Map();
  private reconnectAttempts: Map<string, number> = new Map();
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;

  // Connect to booking updates
  connectToBooking(bookingId: string, onMessage: (message: WebSocketMessage) => void) {
    const key = `booking_${bookingId}`;
    const url = `${API_CONFIG.WS_URL}/ws/bookings/${bookingId}/`;
    this.connect(key, url, onMessage);
  }

  // Connect to user notifications
  connectToNotifications(userId: number, onMessage: (message: WebSocketMessage) => void) {
    const key = `notifications_${userId}`;
    const url = `${API_CONFIG.WS_URL}/ws/notifications/${userId}/`;
    this.connect(key, url, onMessage);
  },

  // Connect to chat
  connectToChat(
    userId: number,
    role: string,
    onMessage: (message: WebSocketMessage) => void
  ) {
    const key = `chat_${userId}_${role}`;
    const url = `${API_CONFIG.WS_URL}/ws/chat/${userId}/${role}/`;
    this.connect(key, url, onMessage);
  },

  // Connect to live status updates
  connectToStatus(
    userId: number,
    role: string,
    onMessage: (message: WebSocketMessage) => void
  ) {
    const key = `status_${userId}_${role}`;
    const url = `${API_CONFIG.WS_URL}/ws/status/${userId}/${role}/`;
    this.connect(key, url, onMessage);
  },

  // Generic connect method
  private connect(key: string, url: string, onMessage: (message: WebSocketMessage) => void) {
    // Close existing connection if any
    if (this.connections.has(key)) {
      this.disconnect(key);
    }

    const token = localStorage.getItem('access_token');
    const wsUrl = `${url}?token=${token}`;

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`WebSocket connected: ${key}`);
      this.reconnectAttempts.set(key, 0);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        onMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error on ${key}:`, error);
    };

    ws.onclose = () => {
      console.log(`WebSocket disconnected: ${key}`);
      this.connections.delete(key);

      // Attempt to reconnect
      const attempts = this.reconnectAttempts.get(key) || 0;
      if (attempts < this.maxReconnectAttempts) {
        this.reconnectAttempts.set(key, attempts + 1);
        setTimeout(() => {
          console.log(`Reconnecting to ${key} (attempt ${attempts + 1})`);
          this.connect(key, url, onMessage);
        }, this.reconnectDelay);
      }
    };

    this.connections.set(key, ws);
  }

  // Send message
  send(key: string, message: any) {
    const ws = this.connections.get(key);
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    } else {
      console.error(`WebSocket not connected: ${key}`);
    }
  }

  // Disconnect
  disconnect(key: string) {
    const ws = this.connections.get(key);
    if (ws) {
      ws.close();
      this.connections.delete(key);
      this.reconnectAttempts.delete(key);
    }
  }

  // Disconnect all
  disconnectAll() {
    this.connections.forEach((ws, key) => {
      this.disconnect(key);
    });
  }
}

export const websocketService = new WebSocketService();
```

### 2. React Hook for WebSocket

```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react';
import { websocketService, WebSocketMessage } from '@/services/websocketService';

export const useWebSocket = (
  type: 'booking' | 'notifications' | 'chat' | 'status',
  id: string | number,
  role?: string
) => {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const connectionKey = useRef<string>('');

  useEffect(() => {
    const handleMessage = (message: WebSocketMessage) => {
      setMessages((prev) => [...prev, message]);
      setIsConnected(true);
    };

    // Connect based on type
    if (type === 'booking') {
      connectionKey.current = `booking_${id}`;
      websocketService.connectToBooking(String(id), handleMessage);
    } else if (type === 'notifications') {
      connectionKey.current = `notifications_${id}`;
      websocketService.connectToNotifications(Number(id), handleMessage);
    } else if (type === 'chat' && role) {
      connectionKey.current = `chat_${id}_${role}`;
      websocketService.connectToChat(Number(id), role, handleMessage);
    } else if (type === 'status' && role) {
      connectionKey.current = `status_${id}_${role}`;
      websocketService.connectToStatus(Number(id), role, handleMessage);
    }

    return () => {
      if (connectionKey.current) {
        websocketService.disconnect(connectionKey.current);
      }
    };
  }, [type, id, role]);

  const sendMessage = (message: any) => {
    if (connectionKey.current) {
      websocketService.send(connectionKey.current, message);
    }
  };

  return { messages, isConnected, sendMessage };
};
```

---

## Role-Based Features

### Customer Features

```typescript
// src/pages/customer/Dashboard.tsx
import { useEffect, useState } from 'react';
import { bookingService, serviceService } from '@/services';

export const CustomerDashboard = () => {
  const [bookings, setBookings] = useState([]);
  const [services, setServices] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [bookingsData, servicesData] = await Promise.all([
        bookingService.getBookings(),
        serviceService.getServices(),
      ]);
      setBookings(bookingsData);
      setServices(servicesData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  return (
    <div className="customer-dashboard">
      {/* Dashboard content */}
    </div>
  );
};
```

### Vendor Features

```typescript
// src/pages/vendor/Jobs.tsx
import { useEffect, useState } from 'react';
import { bookingService, photoService } from '@/services';

export const VendorJobs = () => {
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const data = await bookingService.getBookings();
      setJobs(data);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    }
  };

  const handleAcceptJob = async (jobId: string) => {
    try {
      await bookingService.acceptBooking(jobId);
      await loadJobs(); // Reload
    } catch (error) {
      console.error('Failed to accept job:', error);
    }
  };

  const handleCompleteJob = async (jobId: string) => {
    try {
      const result = await bookingService.completeBooking(jobId);
      // Handle payment intent
      console.log('Payment intent created:', result.payment_intent);
      await loadJobs();
    } catch (error) {
      console.error('Failed to complete job:', error);
    }
  };

  const handleUploadPhoto = async (jobId: string, file: File, type: 'before' | 'after') => {
    try {
      await photoService.uploadPhoto(jobId, type, file);
      // Show success message
    } catch (error) {
      console.error('Failed to upload photo:', error);
    }
  };

  return (
    <div className="vendor-jobs">
      {/* Jobs list and actions */}
    </div>
  );
};
```

### Admin Features

```typescript
// src/pages/admin/Dashboard.tsx
import { useEffect, useState } from 'react';
import { adminService } from '@/services';

export const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [cacheHealth, setCacheHealth] = useState(null);

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      const [statsData, cacheData] = await Promise.all([
        adminService.getDashboardStats(),
        adminService.getCacheStats(),
      ]);
      setStats(statsData);
      setCacheHealth(cacheData.cache_stats.overall_health);
    } catch (error) {
      console.error('Failed to load admin stats:', error);
    }
  };

  const handleClearCache = async (cacheType: string) => {
    try {
      await adminService.clearCache(cacheType);
      await loadDashboardStats(); // Reload
    } catch (error) {
      console.error('Failed to clear cache:', error);
    }
  };

  return (
    <div className="admin-dashboard">
      {/* Admin dashboard content */}
    </div>
  );
};
```

---

## State Management

### Using React Context

```typescript
// src/context/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService, LoginResponse } from '@/services/authService';

interface AuthContextType {
  user: LoginResponse['user'] | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  loginWithOTP: (identifier: string, otp: string, method?: 'email' | 'sms') => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<LoginResponse['user'] | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const currentUser = authService.getCurrentUser();
    if (currentUser) {
      setUser(currentUser);
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    const response = await authService.login({ username, password });
    setUser(response.user);
  };

  const loginWithOTP = async (identifier: string, otp: string, method: 'email' | 'sms' = 'email') => {
    const response = await authService.verifyOTP(identifier, otp, method);
    setUser(response.user);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        loginWithOTP,
        logout,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

---

## Error Handling

```typescript
// src/utils/errorHandler.ts
import { AxiosError } from 'axios';
import { toast } from 'sonner';

export const handleApiError = (error: any): string => {
  if (error.response) {
    // Server responded with error
    const status = error.response.status;
    const data = error.response.data;

    switch (status) {
      case 400:
        // Validation errors
        if (typeof data === 'object' && !data.detail) {
          const errors = Object.entries(data)
            .map(([key, value]) => `${key}: ${value}`)
            .join(', ');
          return errors;
        }
        return data.detail || data.error || 'Invalid request';

      case 401:
        // Unauthorized
        toast.error('Session expired. Please login again.');
        localStorage.clear();
        window.location.href = '/login';
        return 'Unauthorized';

      case 403:
        return 'You do not have permission to perform this action';

      case 404:
        return data.error || 'Resource not found';

      case 500:
        return 'Server error. Please try again later.';

      default:
        return data.error || data.detail || 'An error occurred';
    }
  } else if (error.request) {
    // No response from server
    return 'Network error. Please check your connection.';
  } else {
    // Other errors
    return error.message || 'An unexpected error occurred';
  }
};

// Usage in components
try {
  await bookingService.createBooking(data);
  toast.success('Booking created successfully!');
} catch (error) {
  const errorMessage = handleApiError(error);
  toast.error(errorMessage);
}
```

---

## Best Practices

### 1. API Call Patterns

```typescript
// Always use try-catch
const fetchData = async () => {
  try {
    setLoading(true);
    const data = await apiService.getData();
    setData(data);
  } catch (error) {
    const errorMessage = handleApiError(error);
    toast.error(errorMessage);
  } finally {
    setLoading(false);
  }
};

// Use loading states
const [isLoading, setIsLoading] = useState(false);

// Show user feedback
toast.success('Action completed successfully!');
toast.error('Something went wrong');
toast.loading('Processing...');
```

### 2. Form Handling

```typescript
// Use React Hook Form for complex forms
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const bookingSchema = z.object({
  service: z.number(),
  pincode: z.string().min(6).max(10),
  scheduled_date: z.string(),
  customer_notes: z.string().optional(),
});

type BookingFormData = z.infer<typeof bookingSchema>;

const BookingForm = () => {
  const form = useForm<BookingFormData>({
    resolver: zodResolver(bookingSchema),
  });

  const onSubmit = async (data: BookingFormData) => {
    try {
      await bookingService.createBooking(data);
      toast.success('Booking created!');
    } catch (error) {
      toast.error(handleApiError(error));
    }
  };

  return <form onSubmit={form.handleSubmit(onSubmit)}>{/* Form fields */}</form>;
};
```

### 3. Real-time Updates

```typescript
// Combine WebSocket with polling for reliability
const useBookingUpdates = (bookingId: string) => {
  const { messages } = useWebSocket('booking', bookingId);
  const [booking, setBooking] = useState(null);

  // WebSocket updates
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.type === 'booking_status_change') {
        setBooking(lastMessage.data);
      }
    }
  }, [messages]);

  // Fallback polling
  useEffect(() => {
    const interval = setInterval(async () => {
      const data = await bookingService.getBooking(bookingId);
      setBooking(data);
    }, 30000); // Poll every 30 seconds

    return () => clearInterval(interval);
  }, [bookingId]);

  return booking;
};
```

### 4. Optimistic Updates

```typescript
// Update UI immediately, rollback on error
const handleAcceptBooking = async (bookingId: string) => {
  // Optimistic update
  setBookings((prev) =>
    prev.map((b) => (b.id === bookingId ? { ...b, status: 'confirmed' } : b))
  );

  try {
    await bookingService.acceptBooking(bookingId);
    toast.success('Booking accepted!');
  } catch (error) {
    // Rollback on error
    setBookings((prev) =>
      prev.map((b) => (b.id === bookingId ? { ...b, status: 'pending' } : b))
    );
    toast.error(handleApiError(error));
  }
};
```

---

## Complete Endpoint Reference

### Authentication
- `POST /auth/login/` - Standard login
- `POST /auth/refresh/` - Refresh JWT token
- `POST /auth/send-otp/` - Send OTP (email/SMS)
- `POST /auth/verify-otp/` - Verify OTP
- `POST /auth/vendor/send-otp/` - Vendor OTP
- `POST /auth/vendor/verify-otp/` - Vendor OTP verification

### Bookings
- `GET /api/bookings/` - List bookings
- `POST /api/bookings/` - Create booking
- `GET /api/bookings/{id}/` - Get booking details
- `PATCH /api/bookings/{id}/` - Update booking
- `POST /api/bookings/{id}/accept_booking/` - Accept (vendor)
- `POST /api/bookings/{id}/complete_booking/` - Complete (vendor)
- `POST /api/bookings/{id}/request_signature/` - Request signature

### Services
- `GET /api/services/` - List services
- `GET /api/services/{id}/` - Get service details

### Photos
- `GET /api/photos/` - List photos
- `POST /api/photos/` - Upload photo
- `DELETE /api/photos/{id}/` - Delete photo

### Signatures
- `GET /api/signatures/` - List signatures
- `POST /api/signatures/{id}/sign/` - Sign booking

### Dynamic Pricing
- `GET /api/dynamic-pricing/` - Get dynamic price
- `POST /api/dynamic-pricing/` - Price predictions

### Smart Scheduling
- `GET /api/smart-scheduling/` - Available slots
- `POST /api/smart-scheduling/` - Optimal slot suggestion
- `GET /api/vendor-optimization/` - Vendor schedule optimization

### Vendor Search
- `GET /api/vendor-search/` - Search vendors by pincode

### Disputes
- `GET /api/disputes/` - List disputes
- `POST /api/disputes/create_dispute/` - Create dispute
- `GET /api/disputes/{id}/messages/` - Get messages
- `POST /api/disputes/{id}/send_message/` - Send message
- `POST /api/disputes/{id}/resolve/` - Resolve dispute

### Admin Dashboard
- `GET /admin-dashboard/cache/` - Cache stats
- `POST /admin-dashboard/cache/` - Clear cache
- `GET /admin-dashboard/pincode-scaling/data/` - Pincode analytics
- `GET /admin-dashboard/edit-history/` - Edit history
- `GET /admin-dashboard/dashboard/stats/` - Dashboard stats
- `GET /admin-dashboard/notifications/` - Notification stats
- `POST /admin-dashboard/notifications/` - Trigger tasks
- `GET /admin-dashboard/notifications/logs/` - Notification logs
- `GET /admin-dashboard/notifications/alerts/` - Business alerts
- `GET /admin-dashboard/analytics/pincode/` - Pincode analytics

### Advanced AI Features
- `GET /api/pincode-ai-analytics/` - AI pincode analysis
- `GET /api/advanced-dispute-resolution/{id}/` - AI dispute resolution
- `GET /api/advanced-vendor-bonus/` - ML vendor bonus analysis

### WebSocket Endpoints
- `ws://localhost:8000/ws/bookings/{booking_id}/` - Booking updates
- `ws://localhost:8000/ws/notifications/{user_id}/` - User notifications
- `ws://localhost:8000/ws/chat/{user_id}/{role}/` - Chat messages
- `ws://localhost:8000/ws/status/{user_id}/{role}/` - Live status updates

---

## Testing Integration

```typescript
// Example: Testing API calls
import { describe, it, expect, vi } from 'vitest';
import { bookingService } from '@/services/bookingService';

describe('Booking Service', () => {
  it('should create a booking', async () => {
    const mockBooking = {
      service: 1,
      pincode: '110001',
      scheduled_date: '2024-01-15T10:00:00Z',
    };

    const result = await bookingService.createBooking(mockBooking);
    expect(result).toHaveProperty('id');
    expect(result.status).toBe('pending');
  });

  it('should handle errors', async () => {
    const invalidBooking = {
      service: 999, // Non-existent service
      pincode: '',
      scheduled_date: '',
    };

    await expect(bookingService.createBooking(invalidBooking)).rejects.toThrow();
  });
});
```

---

## Environment Variables

```env
# .env file
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
VITE_GOOGLE_MAPS_API_KEY=your_api_key_here
```

---

## Next Steps

1. **Authentication**: Implement login/register pages using `authService`
2. **Role Routing**: Set up protected routes for different user roles
3. **Dashboard**: Create role-specific dashboards
4. **WebSocket**: Integrate real-time updates for bookings and notifications
5. **Forms**: Build booking creation, photo upload, and signature forms
6. **Admin Panel**: Implement cache management, analytics, and monitoring
7. **Error Handling**: Add comprehensive error handling and user feedback
8. **Testing**: Write unit and integration tests for all services

This guide provides complete integration patterns for all backend features. Follow the patterns and examples to build a robust, production-ready frontend application.
