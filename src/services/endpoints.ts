// API Endpoints configuration

export const ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    FORGOT_PASSWORD: '/api/auth/forgot-password',
    LOGOUT: '/api/auth/logout',
    SEND_OTP: '/api/auth/send-otp',
    VERIFY_OTP: '/api/auth/verify-otp',
  },

  // Customer
  CUSTOMER: {
    BOOKINGS: '/api/customer/bookings',
    BOOKING: (id: string) => `/api/customer/bookings/${id}`,
    CREATE_BOOKING: '/api/customer/bookings',
    PROFILE: '/api/customer/profile',
    ADDRESSES: '/api/addresses',
    ADDRESS: (id: string) => `/api/addresses/${id}`,
  },

  // Vendor
  VENDOR: {
    JOBS: '/api/vendor/jobs',
    JOB: (id: string) => `/api/vendor/jobs/${id}`,
    AVAILABILITY: '/api/vendor/availability',
    EARNINGS: '/api/vendor/earnings',
    TRANSACTIONS: '/api/vendor/transactions',
    PROFILE: '/api/vendor/profile',
    SEARCH: '/api/vendor-search',  // Add vendor search endpoint
  },

  // Services
  SERVICE: {
    PRICE: '/api/service/price',
    LIST: '/api/services',
  },

  // Signature
  SIGNATURE: {
    VERIFY: '/api/signature/verify',
    CREATE: '/api/signature/create',
    LIST: '/api/signature/list',
    SIGN: (id: string) => `/api/signatures/${id}/sign/`,
  },

  // Onboard
  ONBOARD: {
    QUEUE: '/api/onboard/queue',
    VENDOR: (id: string) => `/api/onboard/vendors/${id}`,
    APPROVE: (id: string) => `/api/onboard/vendors/${id}/approve`,
    REJECT: (id: string) => `/api/onboard/vendors/${id}/reject`,
    APPROVED: '/api/onboard/approved',
  },

  // Ops
  OPS: {
    BOOKINGS: '/api/ops/bookings',
    SIGNATURES: '/api/ops/signatures',
    PAYMENTS: '/api/ops/payments',
    DISPUTES: '/api/ops/disputes',
  },

  // Dynamic Pricing
  PRICING: {
    CALCULATE: '/api/dynamic-pricing/',
    PREDICT: '/api/dynamic-pricing/',
  },

  // Smart Scheduling
  SCHEDULING: {
    SMART: '/api/smart-scheduling/',
    OPTIMIZATION: '/api/vendor-optimization/',
  },

  // Travel Time
  TRAVEL: {
    TIME: '/api/travel-time/',
  },
};