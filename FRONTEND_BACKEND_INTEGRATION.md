# Frontend-Backend Integration Complete Guide

## ✅ Integration Status

### Completed Integrations:

1. **API Services** ✅
   - [`bookingService.ts`](src/services/bookingService.ts) - Complete CRUD for bookings and services
   - [`photoService.ts`](src/services/photoService.ts) - Photo upload and management
   - [`signatureService.ts`](src/services/signatureService.ts) - Digital signature workflow
   - [`pricingService.ts`](src/services/pricingService.ts) - Dynamic pricing calculations
   - [`schedulingService.ts`](src/services/schedulingService.ts) - Smart slot booking
   - [`addressService.ts`](src/services/addressService.ts) - Address management
   - [`paymentService.ts`](src/services/paymentService.ts) - Payment processing
   - [`disputeService.ts`](src/services/disputeService.ts) - Dispute resolution
   - [`vendorService.ts`](src/services/vendorService.ts) - Vendor operations
   - [`adminService.ts`](src/services/adminService.ts) - Admin dashboard features

2. **Authentication** ✅
   - JWT-based authentication with automatic token refresh
   - OTP verification for customers and vendors
   - Role-based access control (5 roles)
   - Protected routes implementation

3. **API Configuration** ✅
   - Centralized endpoints configuration
   - Axios interceptors for auth and error handling
   - Automatic token refresh on 401 errors

## 🚀 Quick Start Guide

### 1. Environment Setup

Create a `.env` file in the root directory:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# WebSocket URL (for real-time features)
VITE_WS_URL=ws://localhost:8000/ws

# Stripe Configuration (for payments)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
```

### 2. Backend Server

Ensure Django backend is running:

```bash
# Start Django development server
python manage.py runserver 8000

# Start Redis (for caching and WebSocket)
redis-server

# Start Celery worker (for async tasks)
celery -A homeserve_pro worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A homeserve_pro beat --loglevel=info
```

### 3. Frontend Development Server

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

## 📋 Complete Workflow Implementation

### Customer Journey

#### 1. Registration & Login

```typescript
import { useAuth } from '@/context/AuthContext';

const { login, register } = useAuth();

// Standard login
await login('customer1', 'password123');

// Register new customer
await register({
  username: 'newcustomer',
  email: 'customer@example.com',
  password: 'secure123',
  role: 'customer',
  phone: '+919876543210',
  pincode: '110001'
});

// OTP-based login
await sendOTP('customer@example.com', 'email');
await verifyOTP('customer@example.com', '123456', 'email');
```

#### 2. Service Search & Booking

```typescript
import { bookingService } from '@/services/bookingService';
import { pricingService } from '@/services/pricingService';
import { vendorService } from '@/services/vendorService';

// Get all services
const services = await bookingService.getServices();

// Get dynamic pricing
const pricing = await pricingService.getDynamicPrice(
  1, // service ID
  '110001', // pincode
  '2025-10-15T18:00:00Z' // scheduled time
);

// Get price predictions for 7 days
const predictions = await pricingService.getPricePredictions(1, '110001', 7);

// Search vendors in area
const vendorResults = await vendorService.searchVendors('110001', 1);

// Create booking
const booking = await bookingService.createBooking({
  service: 1,
  pincode: '110001',
  scheduled_date: '2025-10-15T10:00:00Z',
  customer_notes: 'Please arrive on time',
  total_price: pricing.pricing.final_price.toString()
});
```

#### 3. Track Booking Status

```typescript
// Get all my bookings
const bookings = await bookingService.getBookings();

// Get specific booking
const booking = await bookingService.getBooking('booking-uuid');

// Filter by status
const activeBookings = await bookingService.getBookings({ status: 'in_progress' });
```

#### 4. Service Completion & Signature

```typescript
import { signatureService } from '@/services/signatureService';
import { photoService } from '@/services/photoService';

// View photos uploaded by vendor
const photos = await photoService.getPhotos('booking-uuid');

// Get pending signatures
const signatures = await signatureService.getSignatures();

// Sign to confirm satisfaction
await signatureService.signBooking(
  'signature-uuid',
  5, // rating
  'Excellent service, very professional!'
);
```

### Vendor Workflow

#### 1. Vendor Registration with OTP

```typescript
import { useAuth } from '@/context/AuthContext';

// Send OTP to vendor's phone
await sendOTP('+919876543210', 'sms');

// Verify OTP to complete registration
await verifyOTP('+919876543210', '123456', 'sms');
```

#### 2. Job Management

```typescript
// Get available jobs
const pendingJobs = await bookingService.getBookings({ status: 'pending' });

// Accept a job
await bookingService.acceptBooking('booking-uuid');

// Update job status
await bookingService.updateBooking('booking-uuid', {
  status: 'in_progress',
  vendor_notes: 'On my way'
});
```

#### 3. Complete Job & Upload Photos

```typescript
import { photoService } from '@/services/photoService';

// Upload before photos
await photoService.uploadPhoto(
  'booking-uuid',
  'before',
  beforeImageFile,
  'Initial condition'
);

// Upload after photos
await photoService.uploadPhoto(
  'booking-uuid',
  'after',
  afterImageFile,
  'Work completed'
);

// Mark booking as complete
await bookingService.completeBooking('booking-uuid');
```

#### 4. Request Customer Signature

```typescript
// Request signature from customer
const result = await bookingService.requestSignature('booking-uuid');
console.log('Signature ID:', result.signature_id);

// Customer receives email/SMS with signature link
// Payment released after customer signs
```

#### 5. Vendor Availability & Earnings

```typescript
import { vendorService } from '@/services/vendorService';

// Get/update availability
const availability = await vendorService.getAvailability();

await vendorService.updateAvailability({
  day_of_week: 1, // Monday
  start_time: '09:00:00',
  end_time: '18:00:00',
  primary_pincode: '110001',
  service_area_pincodes: ['110001', '110002', '110003']
});

// Get earnings
const earnings = await vendorService.getEarnings();

// Get performance metrics
const performance = await vendorService.getPerformance();
```

### Onboard Manager Workflow

```typescript
import { vendorService } from '@/services/vendorService';

// Get pending vendor applications
const applications = await vendorService.getApplications('pending');

// Get application details
const application = await vendorService.getApplication('application-uuid');

// Approve vendor
await vendorService.approveApplication('application-uuid');

// Reject vendor with reason
await vendorService.rejectApplication(
  'application-uuid',
  'Documents incomplete'
);
```

### Ops Manager Workflow

```typescript
import { bookingService } from '@/services/bookingService';
import { signatureService } from '@/services/signatureService';
import { paymentService } from '@/services/paymentService';
import { disputeService } from '@/services/disputeService';

// Monitor all bookings
const allBookings = await bookingService.getBookings();

// Check pending signatures
const pendingSignatures = await signatureService.getSignatures();

// Process manual payment
await paymentService.processManualPayment('payment-uuid');

// Handle disputes
const disputes = await disputeService.getDisputes();

// Resolve dispute
await disputeService.resolveDispute(
  'dispute-uuid',
  'Refund issued to customer',
  100 // resolution amount
);
```

### Super Admin Workflow

```typescript
import { adminService } from '@/services/adminService';

// Get dashboard stats
const stats = await adminService.getDashboardStats();

// Cache management
const cacheStats = await adminService.getCacheStats();
await adminService.clearCache('all');

// Pincode scaling analytics
const pincodeData = await adminService.getPincodeScalingData({
  service_type: 'plumbing',
  days_back: 30
});

// Edit history (audit trail)
const editHistory = await adminService.getEditHistory({
  model: 'Booking',
  action: 'update',
  start_date: '2025-10-01T00:00:00Z',
  end_date: '2025-10-12T23:59:59Z'
});

// Export edit history
const exportData = await adminService.exportEditHistory({
  model: 'Booking'
});

// Notification management
const notificationStats = await adminService.getNotificationStats();
const notificationLogs = await adminService.getNotificationLogs({
  type: 'signature_request',
  status: 'sent'
});

// Business alerts
const businessAlerts = await adminService.getBusinessAlerts({
  status: 'active',
  severity: 'critical'
});

// Pincode analytics
const pincodeAnalytics = await adminService.getPincodeAnalytics({
  pincode: '110001',
  date_from: '2025-10-01',
  date_to: '2025-10-12'
});
```

## 🔧 Advanced Features

### 1. Dynamic Pricing Implementation

```typescript
// In BookService component
const [dynamicPrice, setDynamicPrice] = useState(null);

useEffect(() => {
  const fetchPrice = async () => {
    if (selectedService && pincode && scheduledDate) {
      const pricing = await pricingService.getDynamicPrice(
        selectedService.id,
        pincode,
        scheduledDate
      );
      setDynamicPrice(pricing);
    }
  };
  
  fetchPrice();
}, [selectedService, pincode, scheduledDate]);

// Display price breakdown
<div className="price-breakdown">
  <p>Base Price: ₹{dynamicPrice.pricing.base_price}</p>
  <p>Demand Factor: {dynamicPrice.pricing.factors.demand.multiplier}x</p>
  <p>Supply Factor: {dynamicPrice.pricing.factors.supply.multiplier}x</p>
  <p>Time Factor: {dynamicPrice.pricing.factors.time.multiplier}x</p>
  <p className="final-price">
    Final Price: ₹{dynamicPrice.pricing.final_price}
  </p>
</div>
```

### 2. Smart Scheduling

```typescript
import { schedulingService } from '@/services/schedulingService';

// Get available time slots
const slots = await schedulingService.getAvailableSlots(
  vendorId,
  serviceId,
  customerPincode,
  preferredDate
);

// Get optimal booking suggestion
const optimalSlot = await schedulingService.getOptimalSlot(
  vendorId,
  serviceId,
  customerPincode,
  preferredDate
);

// For vendor: Get schedule optimization
const optimization = await schedulingService.getVendorOptimization('2025-10-15');
```

### 3. Dispute Management

```typescript
import { disputeService } from '@/services/disputeService';

// Customer raises dispute
const dispute = await disputeService.createDispute(
  'booking-uuid',
  'quality_issue',
  'Service not completed properly',
  'The AC is still not cooling after repair'
);

// View dispute messages
const messages = await disputeService.getMessages('dispute-uuid');

// Send message
await disputeService.sendMessage(
  'dispute-uuid',
  'Here are the photos of the issue',
  'file',
  imageFile
);

// Mark messages as read
await disputeService.markMessagesRead('dispute-uuid');
```

### 4. Real-time Updates (WebSocket)

```typescript
// Example WebSocket integration (to be implemented)
import useWebSocket from '@/hooks/useWebSocket';

const { subscribe, send } = useWebSocket('ws://localhost:8000/ws/notifications/');

useEffect(() => {
  const unsubscribe = subscribe('booking_status_change', (data) => {
    console.log('Booking status updated:', data);
    // Refresh booking data
  });

  return unsubscribe;
}, []);
```

## 📊 Data Models Reference

### Booking Model
```typescript
interface Booking {
  id: string;
  customer: number;
  vendor?: number;
  service: number;
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'signed' | 'cancelled';
  total_price: string;
  pincode: string;
  scheduled_date: string;
  customer_notes?: string;
  vendor_notes?: string;
  // Smart buffering fields
  estimated_service_duration_minutes?: number;
  travel_time_to_location_minutes?: number;
  buffer_before_minutes?: number;
  buffer_after_minutes?: number;
  dynamic_price_breakdown?: any;
}
```

### Signature Model
```typescript
interface Signature {
  id: string;
  booking: string;
  status: 'pending' | 'signed' | 'expired' | 'disputed';
  signature_hash?: string;
  satisfaction_rating?: number;
  satisfaction_comments?: string;
  requested_at: string;
  signed_at?: string;
  expires_at: string; // 48 hours from request
}
```

## 🔐 Role-Based Access

### Role Permissions Matrix

| Feature | Customer | Vendor | Onboard Manager | Ops Manager | Super Admin |
|---------|----------|--------|-----------------|-------------|-------------|
| Create Booking | ✅ | ❌ | ❌ | ❌ | ✅ |
| Accept Booking | ❌ | ✅ | ❌ | ❌ | ✅ |
| Upload Photos | ❌ | ✅ | ❌ | ❌ | ✅ |
| Request Signature | ❌ | ✅ | ❌ | ❌ | ✅ |
| Sign Booking | ✅ | ❌ | ❌ | ❌ | ✅ |
| Approve Vendors | ❌ | ❌ | ✅ | ❌ | ✅ |
| Process Payments | ❌ | ❌ | ❌ | ✅ | ✅ |
| Resolve Disputes | ❌ | ❌ | ❌ | ✅ | ✅ |
| View Audit Logs | ❌ | ❌ | ❌ | ❌ | ✅ |
| Clear Cache | ❌ | ❌ | ❌ | ❌ | ✅ |

## 🐛 Error Handling

All service functions throw errors that should be caught:

```typescript
try {
  const booking = await bookingService.createBooking(data);
  toast.success('Booking created successfully!');
} catch (error) {
  console.error('Booking error:', error);
  toast.error(error.message || 'Failed to create booking');
}
```

## 🔄 State Management with React Query

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Fetch data
const { data, isLoading, error } = useQuery({
  queryKey: ['bookings'],
  queryFn: bookingService.getBookings,
});

// Mutate data
const queryClient = useQueryClient();
const mutation = useMutation({
  mutationFn: bookingService.createBooking,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['bookings'] });
    toast.success('Booking created!');
  },
});
```

## 📝 Next Steps

1. **Test Each Workflow:**
   - Run through customer booking flow end-to-end
   - Test vendor job acceptance and completion
   - Verify signature request and signing process
   - Test admin dashboard features

2. **UI Polish:**
   - Add loading states for all async operations
   - Implement proper error boundaries
   - Add success/error toast notifications
   - Improve form validation

3. **Real-time Features:**
   - Implement WebSocket connections
   - Add live booking status updates
   - Real-time notifications for signature requests

4. **Testing:**
   - Write unit tests for services
   - Add integration tests for workflows
   - Test role-based access control

## 🆘 Troubleshooting

### Common Issues:

1. **401 Unauthorized:**
   - Check if token is stored correctly
   - Verify token hasn't expired
   - Ensure Authorization header is set

2. **CORS Errors:**
   - Backend must allow frontend origin
   - Check Django CORS settings

3. **404 Not Found:**
   - Verify endpoint URLs match backend
   - Check API version compatibility

4. **Network Errors:**
   - Ensure backend server is running
   - Check VITE_API_URL in .env

## 📚 Additional Resources

- [Backend API Documentation](COMPLETE_API_ENDPOINTS.md)
- [Frontend Integration Guide](FRONTEND_INTEGRATION_GUIDE.md)
- [Admin Features Documentation](Implementaion plan/ADMIN_FEATURES_API_DOCS.md)
- [Dynamic Pricing Documentation](Implementaion plan/DYNAMIC_PRICING_DOCS.md)
- [Notification System Documentation](Implementaion plan/NOTIFICATION_SYSTEM_DOCS.md)

---

**Status:** ✅ Complete Integration Ready
**Last Updated:** 2025-10-13
**Version:** 1.0.0
