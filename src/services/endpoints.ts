// API Endpoints configuration

export const ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    FORGOT_PASSWORD: '/api/auth/forgot-password',
    LOGOUT: '/api/auth/logout',
  },

  // Customer
  CUSTOMER: {
    BOOKINGS: '/api/customer/bookings',
    BOOKING: (id: string) => `/api/customer/bookings/${id}`,
    CREATE_BOOKING: '/api/customer/bookings',
    PROFILE: '/api/customer/profile',
  },

  // Vendor
  VENDOR: {
    JOBS: '/api/vendor/jobs',
    JOB: (id: string) => `/api/vendor/jobs/${id}`,
    AVAILABILITY: '/api/vendor/availability',
    EARNINGS: '/api/vendor/earnings',
    TRANSACTIONS: '/api/vendor/transactions',
    PROFILE: '/api/vendor/profile',
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
    ANALYTICS: '/api/ops/analytics',
  },

  // Admin
  ADMIN: {
    USERS: '/api/admin/users',
    ROLES: '/api/admin/roles',
    AUDIT_LOGS: '/api/admin/audit-logs',
    SETTINGS: '/api/admin/settings',
    REPORTS: '/api/admin/reports',
  },

  // Common
  NOTIFICATIONS: '/api/notifications',
  CHAT: '/api/chat',
};

export default ENDPOINTS;
