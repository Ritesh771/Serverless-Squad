// API Endpoints configuration - Updated to match Django backend

export const ENDPOINTS = {
  // Auth Endpoints
  AUTH: {
    LOGIN: '/auth/login/',
    REFRESH: '/auth/refresh/',
    SEND_OTP: '/auth/send-otp/',
    VERIFY_OTP: '/auth/verify-otp/',
    VENDOR_SEND_OTP: '/auth/vendor/send-otp/',
    VENDOR_VERIFY_OTP: '/auth/vendor/verify-otp/',
  },

  // Services
  SERVICES: {
    LIST: '/api/services/',
    DETAIL: (id: number) => `/api/services/${id}/`,
  },

  // Bookings
  BOOKINGS: {
    LIST: '/api/bookings/',
    CREATE: '/api/bookings/',
    DETAIL: (id: string) => `/api/bookings/${id}/`,
    UPDATE: (id: string) => `/api/bookings/${id}/`,
    ACCEPT: (id: string) => `/api/bookings/${id}/accept_booking/`,
    COMPLETE: (id: string) => `/api/bookings/${id}/complete_booking/`,
    REQUEST_SIGNATURE: (id: string) => `/api/bookings/${id}/request_signature/`,
  },

  // Photos
  PHOTOS: {
    LIST: '/api/photos/',
    UPLOAD: '/api/photos/',
    DELETE: (id: number) => `/api/photos/${id}/`,
  },

  // Signatures
  SIGNATURES: {
    LIST: '/api/signatures/',
    DETAIL: (id: string) => `/api/signatures/${id}/`,
    SIGN: (id: string) => `/api/signatures/${id}/sign/`,
  },

  // Payments
  PAYMENTS: {
    LIST: '/api/payments/',
    DETAIL: (id: string) => `/api/payments/${id}/`,
    PROCESS_MANUAL: (id: string) => `/api/payments/${id}/process_manual_payment/`,
  },

  // Addresses
  ADDRESSES: {
    LIST: '/api/addresses/',
    CREATE: '/api/addresses/',
    DETAIL: (id: string) => `/api/addresses/${id}/`,
    UPDATE: (id: string) => `/api/addresses/${id}/`,
    DELETE: (id: string) => `/api/addresses/${id}/`,
    SET_DEFAULT: (id: string) => `/api/addresses/${id}/set_default/`,
  },

  // Users (Admin)
  USERS: {
    LIST: '/api/users/',
    DETAIL: (id: number) => `/api/users/${id}/`,
    UPDATE: (id: number) => `/api/users/${id}/`,
  },

  // Vendor Features
  VENDOR: {
    SEARCH: '/api/vendor-search/',
    AVAILABILITY: '/api/vendor-availability/',
    APPLICATIONS: '/api/vendor-applications/',
    APPLICATION_DETAIL: (id: string) => `/api/vendor-applications/${id}/`,
    APPROVE_APPLICATION: (id: string) => `/api/vendor-applications/${id}/approve/`,
    REJECT_APPLICATION: (id: string) => `/api/vendor-applications/${id}/reject/`,
    EARNINGS: '/api/vendor-earnings/',
    PERFORMANCE: '/api/vendor-performance/',
  },

  // Dynamic Pricing
  PRICING: {
    GET: '/api/dynamic-pricing/',
    PREDICT: '/api/dynamic-pricing/',
  },

  // Smart Scheduling
  SCHEDULING: {
    AVAILABLE_SLOTS: '/api/smart-scheduling/',
    OPTIMAL_SLOT: '/api/smart-scheduling/',
    VENDOR_OPTIMIZATION: '/api/vendor-optimization/',
  },

  // Travel Time
  TRAVEL: {
    CALCULATE: '/api/travel-time/',
  },

  // Disputes
  DISPUTES: {
    LIST: '/api/disputes/',
    CREATE: '/api/disputes/create_dispute/',
    DETAIL: (id: string) => `/api/disputes/${id}/`,
    MESSAGES: (id: string) => `/api/disputes/${id}/messages/`,
    SEND_MESSAGE: (id: string) => `/api/disputes/${id}/send_message/`,
    MARK_READ: (id: string) => `/api/disputes/${id}/mark_read/`,
    RESOLVE: (id: string) => `/api/disputes/${id}/resolve/`,
  },

  // Audit Logs (Admin)
  AUDIT: {
    LIST: '/api/audit-logs/',
    DETAIL: (id: number) => `/api/audit-logs/${id}/`,
  },

  // Admin Dashboard
  ADMIN: {
    CACHE_STATS: '/admin-dashboard/cache/',
    CLEAR_CACHE: '/admin-dashboard/cache/',
    PINCODE_SCALING: '/admin-dashboard/pincode-scaling/data/',
    EDIT_HISTORY: '/admin-dashboard/edit-history/',
    EXPORT_HISTORY: '/admin-dashboard/edit-history/export/',
    DASHBOARD_STATS: '/admin-dashboard/dashboard/stats/',
    NOTIFICATIONS: '/admin-dashboard/notifications/',
    NOTIFICATION_LOGS: '/admin-dashboard/notifications/logs/',
    BUSINESS_ALERTS: '/admin-dashboard/notifications/alerts/',
    PINCODE_ANALYTICS: '/admin-dashboard/analytics/pincode/',
  },

  // Advanced AI Features
  AI: {
    PINCODE_ANALYTICS: '/api/pincode-ai-analytics/',
    DISPUTE_RESOLUTION: (id: string) => `/api/advanced-dispute-resolution/${id}/`,
    VENDOR_BONUS: '/api/advanced-vendor-bonus/',
  },

  // Chat/AI Assistant
  CHAT: {
    MESSAGE: '/api/chat/',
  },
};