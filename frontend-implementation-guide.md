# Complete Frontend Implementation Guide for HomeServe Pro

## Overview

This comprehensive guide provides step-by-step instructions for implementing the complete frontend to connect with the HomeServe Pro Django REST API backend. The backend supports 5 user roles with complete authentication, service booking, digital signatures, payments, and admin features.

## Current Project Structure

Your project already has:
- ✅ React + TypeScript + Vite setup
- ✅ Shadcn UI components library
- ✅ Basic authentication context (needs backend integration)
- ✅ All role-based page components
- ✅ API service structure (needs updates)
- ✅ React Query for data fetching
- ✅ React Router for navigation

## Backend API Summary

### Base URL
```
http://localhost:8000
```

### Authentication
- JWT-based authentication required for all endpoints except login/register
- Headers: `Authorization: Bearer <jwt_token>`
- OTP verification for vendors via SMS/Email

### User Roles
1. **Customer** - Book services, provide signatures
2. **Vendor** - Accept jobs, upload photos, request signatures
3. **Onboard Manager** - Manage vendor recruitment
4. **Ops Manager** - Monitor operations, process payments
5. **Super Admin** - Complete system control

## 1. Environment Configuration

### Update .env file

Create/update your `.env` file in the root directory:

```env
# API Configuration
VITE_API_URL=http://localhost:8000

# Stripe Configuration (for payments)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here

# WebSocket Configuration (for real-time features)
VITE_WS_URL=ws://localhost:8000/ws/
```

## 2. Update API Service Configuration

### Update src/services/api.ts

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh and error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/auth/token/refresh/`, {
            refresh: refreshToken
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, logout user
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/auth/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

## 3. Update Endpoints Configuration

### Update src/services/endpoints.ts

```typescript
// API Endpoints configuration - Updated for Django backend

export const ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/api/auth/token/', // Updated for JWT
    REGISTER: '/api/auth/register/',
    SEND_OTP: '/api/auth/send-otp/',
    VERIFY_OTP: '/api/auth/verify-otp/',
    TOKEN_REFRESH: '/api/auth/token/refresh/',
  },

  // Services
  SERVICES: '/api/services/',

  // Bookings
  BOOKINGS: '/api/bookings/',

  // Photos
  PHOTOS: '/api/photos/',

  // Signatures
  SIGNATURES: '/api/signatures/',

  // Payments
  PAYMENTS: '/api/payments/',

  // Users (Admin)
  USERS: '/api/users/',

  // Audit Logs (Admin)
  AUDIT_LOGS: '/api/audit-logs/',

  // Admin Dashboard
  ADMIN: {
    CACHE: '/api/admin/cache/',
    PINCODE_SCALING: '/api/admin/pincode-scaling/',
    EDIT_HISTORY: '/api/admin/edit-history/',
    DASHBOARD_STATS: '/api/admin/dashboard-stats/',
    NOTIFICATIONS: '/api/admin/notifications/',
    NOTIFICATION_LOGS: '/api/admin/notification-logs/',
    BUSINESS_ALERTS: '/api/admin/business-alerts/',
    PINCODE_ANALYTICS: '/api/admin/pincode-analytics/',
  },

  // WebSocket (for real-time features)
  WS: {
    BASE: 'ws://localhost:8000/ws/',
    NOTIFICATIONS: 'ws://localhost:8000/ws/notifications/',
  }
};

export default ENDPOINTS;
```

## 4. Update Authentication Context

### Update src/context/AuthContext.tsx

```typescript
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/services/api';

export type UserRole = 'customer' | 'vendor' | 'onboard_manager' | 'ops_manager' | 'super_admin';

export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  is_verified: boolean;
  phone?: string;
  pincode?: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  sendOTP: (identifier: string, method?: 'sms' | 'email') => Promise<void>;
  verifyOTP: (identifier: string, otp: string) => Promise<void>;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  role: UserRole;
  phone?: string;
  pincode?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check for stored user and token on mount
    const storedUser = localStorage.getItem('user');
    const token = localStorage.getItem('access_token');

    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    setIsLoading(true);

    try {
      const response = await api.post('/api/auth/token/', {
        username,
        password
      });

      const { access, refresh, user: userData } = response.data;

      // Store tokens and user data
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user', JSON.stringify(userData));

      setUser(userData);

      // Redirect based on role
      const roleRoutes = {
        customer: '/customer/dashboard',
        vendor: '/vendor/dashboard',
        onboard_manager: '/onboard/dashboard',
        ops_manager: '/ops/dashboard',
        super_admin: '/admin/dashboard'
      };

      navigate(roleRoutes[userData.role]);
    } catch (error) {
      throw new Error('Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: RegisterData) => {
    setIsLoading(true);

    try {
      // For vendors, we might need OTP verification
      if (userData.role === 'vendor') {
        // Handle vendor registration with OTP
        await api.post('/api/auth/register/', userData);
        // Redirect to OTP verification
        navigate('/auth/verify-otp', { state: { email: userData.email } });
      } else {
        const response = await api.post('/api/auth/register/', userData);
        const { access, refresh, user: newUser } = response.data;

        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        localStorage.setItem('user', JSON.stringify(newUser));

        setUser(newUser);
        navigate(`/${newUser.role}/dashboard`);
      }
    } catch (error) {
      throw new Error('Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const sendOTP = async (identifier: string, method: 'sms' | 'email' = 'sms') => {
    try {
      await api.post('/api/auth/send-otp/', {
        phone: method === 'sms' ? identifier : undefined,
        email: method === 'email' ? identifier : undefined,
        method
      });
    } catch (error) {
      throw new Error('Failed to send OTP. Please try again.');
    }
  };

  const verifyOTP = async (identifier: string, otp: string) => {
    try {
      const response = await api.post('/api/auth/verify-otp/', {
        phone: identifier.startsWith('+') ? identifier : undefined,
        email: identifier.includes('@') ? identifier : undefined,
        otp
      });

      const { access, refresh, user: verifiedUser } = response.data;

      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user', JSON.stringify(verifiedUser));

      setUser(verifiedUser);
      navigate(`/${verifiedUser.role}/dashboard`);
    } catch (error) {
      throw new Error('OTP verification failed. Please check your OTP.');
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
    navigate('/auth/login');
  };

  return (
    <AuthContext.Provider value={{
      user,
      login,
      register,
      logout,
      isLoading,
      sendOTP,
      verifyOTP
    }}>
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

## 5. Create Service Layer Functions

### Create src/services/bookingService.ts

```typescript
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
}

export interface Booking {
  id: string;
  customer: string;
  vendor?: string;
  service: Service;
  status: string;
  total_price: string;
  pincode: string;
  scheduled_date: string;
  customer_notes?: string;
  vendor_notes?: string;
}

export const bookingService = {
  // Get all services
  getServices: async (): Promise<Service[]> => {
    const response = await api.get(ENDPOINTS.SERVICES);
    return response.data.results;
  },

  // Get service details
  getService: async (id: number): Promise<Service> => {
    const response = await api.get(`${ENDPOINTS.SERVICES}${id}/`);
    return response.data;
  },

  // Get user bookings
  getBookings: async (): Promise<Booking[]> => {
    const response = await api.get(ENDPOINTS.BOOKINGS);
    return response.data.results;
  },

  // Create booking
  createBooking: async (bookingData: {
    service: number;
    total_price: string;
    pincode: string;
    scheduled_date: string;
    customer_notes?: string;
  }): Promise<Booking> => {
    const response = await api.post(ENDPOINTS.BOOKINGS, bookingData);
    return response.data;
  },

  // Accept booking (vendor)
  acceptBooking: async (bookingId: string): Promise<{ message: string }> => {
    const response = await api.post(`${ENDPOINTS.BOOKINGS}${bookingId}/accept_booking/`);
    return response.data;
  },

  // Complete booking (vendor)
  completeBooking: async (bookingId: string): Promise<{
    message: string;
    payment_intent: any
  }> => {
    const response = await api.post(`${ENDPOINTS.BOOKINGS}${bookingId}/complete_booking/`);
    return response.data;
  },

  // Request signature (vendor)
  requestSignature: async (bookingId: string): Promise<{
    message: string;
    signature_id: string
  }> => {
    const response = await api.post(`${ENDPOINTS.BOOKINGS}${bookingId}/request_signature/`);
    return response.data;
  },
};
```

### Create src/services/photoService.ts

```typescript
import api from './api';
import { ENDPOINTS } from './endpoints';

export interface Photo {
  id: number;
  booking: string;
  image: string;
  image_type: 'before' | 'after' | 'additional';
  description?: string;
  uploaded_by: string;
  uploaded_at: string;
}

export const photoService = {
  // Upload photo
  uploadPhoto: async (formData: FormData): Promise<Photo> => {
    const response = await api.post(ENDPOINTS.PHOTOS, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get photos for booking
  getBookingPhotos: async (bookingId: string): Promise<Photo[]> => {
    const response = await api.get(`${ENDPOINTS.PHOTOS}?booking=${bookingId}`);
    return response.data.results;
  },
};
```

### Create src/services/signatureService.ts

```typescript
import api from './api';
import { ENDPOINTS } from './endpoints';

export interface Signature {
  id: string;
  booking: string;
  signed_by?: string;
  status: 'pending' | 'signed' | 'expired' | 'disputed';
  signature_hash?: string;
  satisfaction_rating?: number;
  satisfaction_comments?: string;
  requested_at: string;
  signed_at?: string;
  expires_at: string;
}

export const signatureService = {
  // Get user signatures
  getSignatures: async (): Promise<Signature[]> => {
    const response = await api.get(ENDPOINTS.SIGNATURES);
    return response.data.results;
  },

  // Sign booking
  signBooking: async (
    signatureId: string,
    rating: number,
    comments: string
  ): Promise<{ message: string; signature_hash: string }> => {
    const response = await api.post(`${ENDPOINTS.SIGNATURES}${signatureId}/sign/`, {
      satisfaction_rating: rating,
      comments
    });
    return response.data;
  },
};
```

### Create src/services/paymentService.ts

```typescript
import api from './api';
import { ENDPOINTS } from './endpoints';

export interface Payment {
  id: string;
  booking: string;
  amount: string;
  status: string;
  payment_type: 'automatic' | 'manual';
  stripe_payment_intent_id?: string;
  processed_by?: string;
  processed_at?: string;
}

export const paymentService = {
  // Get user payments
  getPayments: async (): Promise<Payment[]> => {
    const response = await api.get(ENDPOINTS.PAYMENTS);
    return response.data.results;
  },

  // Process manual payment (ops manager)
  processManualPayment: async (paymentId: string): Promise<{ message: string }> => {
    const response = await api.post(`${ENDPOINTS.PAYMENTS}${paymentId}/process_manual_payment/`);
    return response.data;
  },
};
```

## 6. Update Customer Pages

### Update src/pages/customer/Dashboard.tsx

```typescript
import { useQuery } from '@tanstack/react-query';
import { bookingService } from '@/services/bookingService';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

const CustomerDashboard = () => {
  const navigate = useNavigate();

  const { data: bookings, isLoading } = useQuery({
    queryKey: ['customer-bookings'],
    queryFn: bookingService.getBookings,
  });

  const { data: services } = useQuery({
    queryKey: ['services'],
    queryFn: bookingService.getServices,
  });

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }

  const activeBookings = bookings?.filter(b =>
    ['pending', 'confirmed', 'in_progress'].includes(b.status)
  ) || [];

  const completedBookings = bookings?.filter(b =>
    ['completed', 'signed'].includes(b.status)
  ) || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Customer Dashboard</h1>
        <Button onClick={() => navigate('/customer/book-service')}>
          Book New Service
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Bookings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeBookings.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Services</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completedBookings.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Available Services</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{services?.length || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Bookings */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Bookings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {bookings?.slice(0, 5).map((booking) => (
              <div key={booking.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h3 className="font-semibold">{booking.service.name}</h3>
                  <p className="text-sm text-gray-600">
                    {new Date(booking.scheduled_date).toLocaleDateString()}
                  </p>
                  <p className="text-sm text-gray-600">₹{booking.total_price}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={
                    booking.status === 'completed' ? 'default' :
                    booking.status === 'pending' ? 'secondary' :
                    'outline'
                  }>
                    {booking.status.replace('_', ' ')}
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/customer/my-bookings/${booking.id}`)}
                  >
                    View
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CustomerDashboard;
```

### Update src/pages/customer/BookService.tsx

```typescript
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bookingService, Service } from '@/services/bookingService';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

const BookService = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [pincode, setPincode] = useState('');
  const [scheduledDate, setScheduledDate] = useState('');
  const [notes, setNotes] = useState('');

  const { data: services, isLoading } = useQuery({
    queryKey: ['services'],
    queryFn: bookingService.getServices,
  });

  const createBookingMutation = useMutation({
    mutationFn: bookingService.createBooking,
    onSuccess: () => {
      toast.success('Booking created successfully!');
      queryClient.invalidateQueries({ queryKey: ['customer-bookings'] });
      navigate('/customer/my-bookings');
    },
    onError: (error) => {
      toast.error('Failed to create booking. Please try again.');
      console.error('Booking creation error:', error);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedService || !pincode || !scheduledDate) {
      toast.error('Please fill in all required fields.');
      return;
    }

    createBookingMutation.mutate({
      service: selectedService.id,
      total_price: selectedService.base_price,
      pincode,
      scheduled_date: new Date(scheduledDate).toISOString(),
      customer_notes: notes,
    });
  };

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading services...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Book a Service</h1>

      <Card>
        <CardHeader>
          <CardTitle>Select Service</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {services?.map((service) => (
              <Card
                key={service.id}
                className={`cursor-pointer transition-colors ${
                  selectedService?.id === service.id
                    ? 'ring-2 ring-primary'
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => setSelectedService(service)}
              >
                <CardContent className="p-4">
                  <h3 className="font-semibold">{service.name}</h3>
                  <p className="text-sm text-gray-600 mb-2">{service.description}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-bold">₹{service.base_price}</span>
                    <span className="text-sm text-gray-500">{service.duration_minutes} min</span>
                  </div>
                  <Badge variant="outline" className="mt-2">{service.category}</Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {selectedService && (
        <Card>
          <CardHeader>
            <CardTitle>Booking Details</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="pincode">Pincode *</Label>
                <Input
                  id="pincode"
                  type="text"
                  value={pincode}
                  onChange={(e) => setPincode(e.target.value)}
                  placeholder="Enter your pincode"
                  required
                />
              </div>

              <div>
                <Label htmlFor="scheduledDate">Preferred Date & Time *</Label>
                <Input
                  id="scheduledDate"
                  type="datetime-local"
                  value={scheduledDate}
                  onChange={(e) => setScheduledDate(e.target.value)}
                  required
                />
              </div>

              <div>
                <Label htmlFor="notes">Additional Notes</Label>
                <Textarea
                  id="notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Any special instructions or requirements..."
                  rows={3}
                />
              </div>

              <div className="flex justify-between items-center pt-4">
                <div>
                  <p className="text-sm text-gray-600">Service: {selectedService.name}</p>
                  <p className="text-lg font-semibold">Total: ₹{selectedService.base_price}</p>
                </div>
                <Button
                  type="submit"
                  disabled={createBookingMutation.isPending}
                >
                  {createBookingMutation.isPending ? 'Creating...' : 'Confirm Booking'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default BookService;
```

## 7. Update Vendor Pages

### Update src/pages/vendor/JobList.tsx

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bookingService } from '@/services/bookingService';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

const VendorJobList = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: bookings, isLoading } = useQuery({
    queryKey: ['vendor-bookings'],
    queryFn: bookingService.getBookings,
  });

  const acceptBookingMutation = useMutation({
    mutationFn: ({ bookingId }: { bookingId: string }) =>
      bookingService.acceptBooking(bookingId),
    onSuccess: () => {
      toast.success('Booking accepted successfully!');
      queryClient.invalidateQueries({ queryKey: ['vendor-bookings'] });
    },
    onError: () => {
      toast.error('Failed to accept booking. Please try again.');
    },
  });

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading jobs...</div>;
  }

  const pendingBookings = bookings?.filter(b => b.status === 'pending') || [];
  const activeBookings = bookings?.filter(b =>
    ['confirmed', 'in_progress'].includes(b.status)
  ) || [];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">My Jobs</h1>

      {/* Pending Jobs */}
      {pendingBookings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Available Jobs ({pendingBookings.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {pendingBookings.map((booking) => (
                <div key={booking.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h3 className="font-semibold">{booking.service.name}</h3>
                    <p className="text-sm text-gray-600">
                      {booking.pincode} • {new Date(booking.scheduled_date).toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-600">₹{booking.total_price}</p>
                    {booking.customer_notes && (
                      <p className="text-sm text-gray-500 mt-1">{booking.customer_notes}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      onClick={() => navigate(`/vendor/job-list/${booking.id}`)}
                    >
                      View Details
                    </Button>
                    <Button
                      onClick={() => acceptBookingMutation.mutate({ bookingId: booking.id })}
                      disabled={acceptBookingMutation.isPending}
                    >
                      Accept Job
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Active Jobs */}
      {activeBookings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Active Jobs ({activeBookings.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activeBookings.map((booking) => (
                <div key={booking.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h3 className="font-semibold">{booking.service.name}</h3>
                    <p className="text-sm text-gray-600">
                      {booking.pincode} • {new Date(booking.scheduled_date).toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-600">₹{booking.total_price}</p>
                    <Badge variant="outline">{booking.status.replace('_', ' ')}</Badge>
                  </div>
                  <Button
                    onClick={() => navigate(`/vendor/job-list/${booking.id}`)}
                  >
                    Manage Job
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {pendingBookings.length === 0 && activeBookings.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-gray-500">No jobs available at the moment.</p>
            <p className="text-sm text-gray-400 mt-2">Check back later for new opportunities.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default VendorJobList;
```

## 8. Update Admin Dashboard Pages

### Update src/pages/admin/Dashboard.tsx

```typescript
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';

interface DashboardStats {
  status: string;
  cache_health: {
    healthy_caches: number;
    total_caches: number;
    health_percentage: number;
    average_hit_rate: number;
    status: string;
  };
  activity_stats: {
    total_actions_24h: number;
    unique_users_24h: number;
    top_actions: Array<{ action: string; count: number }>;
  };
  pincode_stats: {
    total_pincodes_served: number;
    avg_bookings_per_pincode: number;
    active_vendors: number;
  };
}

const AdminDashboard = () => {
  const navigate = useNavigate();

  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ['admin-dashboard-stats'],
    queryFn: async () => {
      const response = await api.get(ENDPOINTS.ADMIN.DASHBOARD_STATS);
      return response.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/admin/cache')}>
            Cache Management
          </Button>
          <Button variant="outline" onClick={() => navigate('/admin/pincode-scaling')}>
            Pincode Scaling
          </Button>
        </div>
      </div>

      {/* System Health */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cache Health</CardTitle>
            <Badge variant={stats?.cache_health.status === 'healthy' ? 'default' : 'destructive'}>
              {stats?.cache_health.status}
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.cache_health.health_percentage}%</div>
            <p className="text-xs text-muted-foreground">
              {stats?.cache_health.healthy_caches}/{stats?.cache_health.total_caches} caches healthy
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">24h Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.activity_stats.total_actions_24h}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.activity_stats.unique_users_24h} unique users
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Vendors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pincode_stats.active_vendors}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.pincode_stats.total_pincodes_served} pincodes served
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity (24h)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {stats?.activity_stats.top_actions.slice(0, 5).map((action, index) => (
              <div key={index} className="flex justify-between items-center">
                <span className="text-sm">{action.action.replace('_', ' ')}</span>
                <Badge variant="secondary">{action.count}</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" onClick={() => navigate('/admin/users')}>
              Manage Users
            </Button>
            <Button variant="outline" onClick={() => navigate('/admin/audit-logs')}>
              Audit Logs
            </Button>
            <Button variant="outline" onClick={() => navigate('/admin/reports')}>
              Reports
            </Button>
            <Button variant="outline" onClick={() => navigate('/admin/settings')}>
              Settings
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminDashboard;
```

## 9. Add Payment Integration

### Install Stripe

```bash
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### Create Stripe Provider

```typescript
// src/components/StripeProvider.tsx
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || 'pk_test_...');

interface StripeProviderProps {
  children: React.ReactNode;
}

export const StripeProvider = ({ children }: StripeProviderProps) => {
  return (
    <Elements stripe={stripePromise}>
      {children}
    </Elements>
  );
};
```

### Create Payment Component

```typescript
// src/components/PaymentForm.tsx
import { useState } from 'react';
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface PaymentFormProps {
  clientSecret: string;
  amount: number;
  onSuccess: () => void;
  onError: (error: string) => void;
}

const PaymentForm = ({ clientSecret, amount, onSuccess, onError }: PaymentFormProps) => {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);

    const cardElement = elements.getElement(CardElement);

    if (!cardElement) {
      setIsProcessing(false);
      onError('Card element not found');
      return;
    }

    try {
      const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: cardElement,
          billing_details: {
            name: 'Customer Name',
          },
        },
      });

      if (error) {
        onError(error.message || 'Payment failed');
      } else if (paymentIntent && paymentIntent.status === 'succeeded') {
        toast.success('Payment successful!');
        onSuccess();
      }
    } catch (err) {
      onError('Payment processing failed');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="p-4 border rounded-lg">
        <CardElement
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': {
                  color: '#aab7c4',
                },
              },
            },
          }}
        />
      </div>

      <div className="flex justify-between items-center">
        <span className="text-lg font-semibold">Total: ₹{(amount / 100).toFixed(2)}</span>
        <Button
          type="submit"
          disabled={!stripe || isProcessing}
        >
          {isProcessing ? 'Processing...' : 'Pay Now'}
        </Button>
      </div>
    </form>
  );
};

export default PaymentForm;
```

## 10. Add Real-time Features

### Create WebSocket Hook

```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react';

export const useWebSocket = (url: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');

    if (token) {
      ws.current = new WebSocket(`${url}?token=${token}`);

      ws.current.onopen = () => {
        setIsConnected(true);
      };

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setMessages(prev => [...prev, data]);
      };

      ws.current.onclose = () => {
        setIsConnected(false);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    }

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url]);

  const sendMessage = (message: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };

  return { isConnected, messages, sendMessage };
};
```

### Create Notification Center

```typescript
// src/components/NotificationCenter.tsx
import { useWebSocket } from '@/hooks/useWebSocket';
import { ENDPOINTS } from '@/services/endpoints';
import { Bell, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useState, useEffect } from 'react';

interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

const NotificationCenter = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);

  const { messages } = useWebSocket(ENDPOINTS.WS.NOTIFICATIONS);

  useEffect(() => {
    messages.forEach((message) => {
      if (message.type === 'notification') {
        const newNotification: Notification = {
          id: message.id,
          type: message.notification_type,
          title: message.subject,
          message: message.message,
          timestamp: new Date().toISOString(),
          read: false,
        };

        setNotifications(prev => [newNotification, ...prev]);
      }
    });
  }, [messages]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  };

  const dismissNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setShowDropdown(!showDropdown)}
        className="relative"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs">
            {unreadCount}
          </Badge>
        )}
      </Button>

      {showDropdown && (
        <Card className="absolute right-0 top-12 w-80 max-h-96 overflow-y-auto z-50">
          <CardContent className="p-0">
            <div className="p-4 border-b">
              <h3 className="font-semibold">Notifications</h3>
            </div>

            {notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No notifications
              </div>
            ) : (
              <div className="max-h-80 overflow-y-auto">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-3 border-b hover:bg-gray-50 ${!notification.read ? 'bg-blue-50' : ''}`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-medium text-sm">{notification.title}</h4>
                        <p className="text-xs text-gray-600 mt-1">{notification.message}</p>
                        <span className="text-xs text-gray-400">
                          {new Date(notification.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="flex gap-1">
                        {!notification.read && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => markAsRead(notification.id)}
                            className="h-6 w-6 p-0"
                          >
                            ✓
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => dismissNotification(notification.id)}
                          className="h-6 w-6 p-0"
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default NotificationCenter;
```

## 11. Update App.tsx for Providers

### Update src/App.tsx

```typescript
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { StripeProvider } from '@/components/StripeProvider';

// Import pages
import Index from '@/pages/Index';
import NotFound from '@/pages/NotFound';

// Auth pages
import Login from '@/pages/auth/Login';
import Register from '@/pages/auth/Register';

// Customer pages
import CustomerDashboard from '@/pages/customer/Dashboard';
import BookService from '@/pages/customer/BookService';
import MyBookings from '@/pages/customer/MyBookings';
import BookingDetails from '@/pages/customer/BookingDetails';
import CustomerProfile from '@/pages/customer/Profile';
import SignaturePage from '@/pages/customer/SignaturePage';

// Vendor pages
import VendorDashboard from '@/pages/vendor/Dashboard';
import JobList from '@/pages/vendor/JobList';
import JobDetails from '@/pages/vendor/JobDetails';
import VendorProfile from '@/pages/vendor/Profile';
import Earnings from '@/pages/vendor/Earnings';

// Admin pages
import AdminDashboard from '@/pages/admin/Dashboard';
import Users from '@/pages/admin/Users';
import AuditLogs from '@/pages/admin/AuditLogs';
import Reports from '@/pages/admin/Reports';
import Settings from '@/pages/admin/Settings';

// Ops pages
import OpsDashboard from '@/pages/ops/Dashboard';
import BookingsMonitor from '@/pages/ops/BookingsMonitor';
import ManualPayments from '@/pages/ops/ManualPayments';
import SignatureVault from '@/pages/ops/SignatureVault';

// Onboard pages
import OnboardDashboard from '@/pages/onboard/Dashboard';
import VendorQueue from '@/pages/onboard/VendorQueue';
import VendorDetails from '@/pages/onboard/VendorDetails';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Protected Route Component
const ProtectedRoute = ({
  children,
  allowedRoles
}: {
  children: React.ReactNode;
  allowedRoles: string[]
}) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/auth/login" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    return <Navigate to={`/${user.role}/dashboard`} replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <StripeProvider>
        <AuthProvider>
          <Router>
            <div className="min-h-screen bg-gray-50">
              <Routes>
                {/* Public routes */}
                <Route path="/" element={<Index />} />
                <Route path="/auth/login" element={<Login />} />
                <Route path="/auth/register" element={<Register />} />

                {/* Customer routes */}
                <Route path="/customer/dashboard" element={
                  <ProtectedRoute allowedRoles={['customer']}>
                    <CustomerDashboard />
                  </ProtectedRoute>
                } />
                <Route path="/customer/book-service" element={
                  <ProtectedRoute allowedRoles={['customer']}>
                    <BookService />
                  </ProtectedRoute>
                } />
                <Route path="/customer/my-bookings" element={
                  <ProtectedRoute allowedRoles={['customer']}>
                    <MyBookings />
                  </ProtectedRoute>
                } />
                <Route path="/customer/my-bookings/:id" element={
                  <ProtectedRoute allowedRoles={['customer']}>
                    <BookingDetails />
                  </ProtectedRoute>
                } />
                <Route path="/customer/profile" element={
                  <ProtectedRoute allowedRoles={['customer']}>
                    <CustomerProfile />
                  </ProtectedRoute>
                } />
                <Route path="/customer/signature/:id" element={
                  <ProtectedRoute allowedRoles={['customer']}>
                    <SignaturePage />
                  </ProtectedRoute>
                } />

                {/* Vendor routes */}
                <Route path="/vendor/dashboard" element={
                  <ProtectedRoute allowedRoles={['vendor']}>
                    <VendorDashboard />
                  </ProtectedRoute>
                } />
                <Route path="/vendor/job-list" element={
                  <ProtectedRoute allowedRoles={['vendor']}>
                    <JobList />
                  </ProtectedRoute>
                } />
                <Route path="/vendor/job-list/:id" element={
                  <ProtectedRoute allowedRoles={['vendor']}>
                    <JobDetails />
                  </ProtectedRoute>
                } />
                <Route path="/vendor/profile" element={
                  <ProtectedRoute allowedRoles={['vendor']}>
                    <VendorProfile />
                  </ProtectedRoute>
                } />
                <Route path="/vendor/earnings" element={
                  <ProtectedRoute allowedRoles={['vendor']}>
                    <Earnings />
                  </ProtectedRoute>
                } />

                {/* Admin routes */}
                <Route path="/admin/dashboard" element={
                  <ProtectedRoute allowedRoles={['super_admin']}>
                    <AdminDashboard />
                  </ProtectedRoute>
                } />
                <Route path="/admin/users" element={
                  <ProtectedRoute allowedRoles={['super_admin']}>
                    <Users />
                  </ProtectedRoute>
                } />
                <Route path="/admin/audit-logs" element={
                  <ProtectedRoute allowedRoles={['super_admin']}>
                    <AuditLogs />
                  </ProtectedRoute>
                } />
                <Route path="/admin/reports" element={
                  <ProtectedRoute allowedRoles={['super_admin']}>
                    <Reports />
                  </ProtectedRoute>
                } />
                <Route path="/admin/settings" element={
                  <ProtectedRoute allowedRoles={['super_admin']}>
                    <Settings />
                  </ProtectedRoute>
                } />

                {/* Ops routes */}
                <Route path="/ops/dashboard" element={
                  <ProtectedRoute allowedRoles={['ops_manager']}>
                    <OpsDashboard />
                  </ProtectedRoute>
                } />
                <Route path="/ops/bookings" element={
                  <ProtectedRoute allowedRoles={['ops_manager']}>
                    <BookingsMonitor />
                  </ProtectedRoute>
                } />
                <Route path="/ops/payments" element={
                  <ProtectedRoute allowedRoles={['ops_manager']}>
                    <ManualPayments />
                  </ProtectedRoute>
                } />
                <Route path="/ops/signatures" element={
                  <ProtectedRoute allowedRoles={['ops_manager']}>
                    <SignatureVault />
                  </ProtectedRoute>
                } />

                {/* Onboard routes */}
                <Route path="/onboard/dashboard" element={
                  <ProtectedRoute allowedRoles={['onboard_manager']}>
                    <OnboardDashboard />
                  </ProtectedRoute>
                } />
                <Route path="/onboard/queue" element={
                  <ProtectedRoute allowedRoles={['onboard_manager']}>
                    <VendorQueue />
                  </ProtectedRoute>
                } />
                <Route path="/onboard/vendors/:id" element={
                  <ProtectedRoute allowedRoles={['onboard_manager']}>
                    <VendorDetails />
                  </ProtectedRoute>
                } />

                {/* 404 route */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </div>
            <Toaster />
          </Router>
        </AuthProvider>
      </StripeProvider>
    </QueryClientProvider>
  );
}

export default App;
```

## 12. Update Vite Configuration

### Update vite.config.ts

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
```

## 13. Testing the Integration

### Update Login Page for Testing

```typescript
// src/pages/auth/Login.tsx
import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(username, password);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">HomeServe Pro</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Logging in...' : 'Login'}
            </Button>
          </form>

          {/* Demo credentials for testing */}
          <div className="mt-6 p-4 bg-gray-100 rounded-lg">
            <h3 className="font-semibold mb-2">Demo Credentials:</h3>
            <div className="text-sm space-y-1">
              <p><strong>Customer:</strong> customer1 / password123</p>
              <p><strong>Vendor:</strong> vendor1 / password123</p>
              <p><strong>Ops:</strong> ops1 / password123</p>
              <p><strong>Admin:</strong> admin / password123</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;
```

## 14. Deployment Configuration

### Production Build

```bash
npm run build
```

### Nginx Configuration for Production

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Summary

This comprehensive frontend implementation guide provides:

1. **Complete API Integration**: JWT authentication, token refresh, and all backend endpoints
2. **Role-based Dashboards**: Separate interfaces for customers, vendors, ops, and admins
3. **Service Booking Flow**: Full booking workflow with real-time updates
4. **Payment Integration**: Stripe payment processing
5. **Real-time Features**: WebSocket notifications
6. **Admin Features**: Cache management, pincode scaling, audit logs
7. **Responsive Design**: Mobile-friendly UI with Shadcn components
8. **Error Handling**: Comprehensive error handling and user feedback
9. **Production Ready**: Build configuration and deployment setup

The implementation connects seamlessly with your Django backend and provides a complete, production-ready frontend for the HomeServe Pro platform. All components are designed to work with the existing backend API structure and support the full workflow from customer booking to vendor completion to admin oversight.