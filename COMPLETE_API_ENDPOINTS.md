# HomeServe Pro - Complete API Endpoints Reference

## Quick Reference Index

- [Authentication](#authentication-endpoints)
- [User Management](#user-management-endpoints)
- [Services](#service-endpoints)
- [Bookings](#booking-endpoints)
- [Photos](#photo-endpoints)
- [Signatures](#signature-endpoints)
- [Payments](#payment-endpoints)
- [Addresses](#address-endpoints)
- [Vendor Features](#vendor-endpoints)
- [Dynamic Pricing](#dynamic-pricing-endpoints)
- [Smart Scheduling](#smart-scheduling-endpoints)
- [Travel Time](#travel-time-endpoints)
- [Disputes](#dispute-endpoints)
- [Vendor Applications](#vendor-application-endpoints)
- [Earnings](#earnings-endpoints)
- [Performance Metrics](#performance-metrics-endpoints)
- [Admin Dashboard](#admin-dashboard-endpoints)
- [Advanced AI Features](#advanced-ai-features-endpoints)
- [Analytics](#analytics-endpoints)
- [Chat/AI Assistant](#chat-endpoints)
- [WebSocket](#websocket-endpoints)

---

## Authentication Endpoints

### Standard Login
```http
POST /auth/login/
Content-Type: application/json

Request:
{
  "username": "customer1",
  "password": "password123"
}

Response: 200 OK
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "customer1",
    "email": "customer1@example.com",
    "role": "customer",
    "is_verified": true
  }
}
```

### Refresh Token
```http
POST /auth/refresh/
Content-Type: application/json

Request:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response: 200 OK
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Send OTP (Email or SMS)
```http
POST /auth/send-otp/
Content-Type: application/json

Request (Email):
{
  "email": "user@example.com",
  "method": "email"
}

Request (SMS):
{
  "phone": "+919876543210",
  "method": "sms"
}

Response: 200 OK
{
  "message": "OTP sent successfully via email",
  "method": "email",
  "otp_sent": true
}
```

### Verify OTP
```http
POST /auth/verify-otp/
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "otp": "123456"
}

Response: 200 OK
{
  "message": "OTP verified successfully",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user@example.com",
    "role": "customer",
    "is_verified": true
  }
}
```

### Vendor OTP Login
```http
POST /auth/vendor/send-otp/
Content-Type: application/json

Request:
{
  "phone": "+919876543210",
  "method": "sms"
}

POST /auth/vendor/verify-otp/
Content-Type: application/json

Request:
{
  "phone": "+919876543210",
  "otp": "123456"
}
```

---

## User Management Endpoints

### List Users (Admin)
```http
GET /api/users/
Authorization: Bearer <admin_token>

Query Parameters:
- role: filter by role (customer, vendor, etc.)
- is_verified: filter by verification status
- pincode: filter by pincode

Response: 200 OK
{
  "count": 50,
  "next": "http://localhost:8000/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "customer1",
      "email": "customer1@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "customer",
      "phone": "+919876543210",
      "pincode": "110001",
      "is_available": false,
      "is_verified": true
    }
  ]
}
```

### Get User Details
```http
GET /api/users/{id}/
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "username": "customer1",
  "email": "customer1@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "customer",
  "phone": "+919876543210",
  "pincode": "110001",
  "is_available": false,
  "is_verified": true
}
```

---

## Service Endpoints

### List All Services
```http
GET /api/services/
Authorization: Bearer <token>

Query Parameters:
- category: filter by category

Response: 200 OK
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "AC Repair",
      "description": "Air conditioning repair and maintenance",
      "base_price": "500.00",
      "category": "Appliance",
      "duration_minutes": 120,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Service Details
```http
GET /api/services/{id}/
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "name": "AC Repair",
  "description": "Air conditioning repair and maintenance",
  "base_price": "500.00",
  "category": "Appliance",
  "duration_minutes": 120,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## Booking Endpoints

### List Bookings
```http
GET /api/bookings/
Authorization: Bearer <token>

Query Parameters:
- status: filter by status (pending, confirmed, completed, etc.)
- pincode: filter by pincode
- scheduled_date: filter by scheduled date

Response: 200 OK
{
  "count": 25,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "customer": 1,
      "customer_name": "John Doe",
      "vendor": 2,
      "vendor_name": "Jane Smith",
      "service": 1,
      "service_name": "AC Repair",
      "status": "confirmed",
      "total_price": "500.00",
      "pincode": "110001",
      "scheduled_date": "2024-01-15T10:00:00Z",
      "completion_date": null,
      "customer_notes": "Please arrive on time",
      "vendor_notes": "",
      "created_at": "2024-01-10T08:30:00Z",
      "updated_at": "2024-01-10T09:00:00Z",
      "estimated_service_duration_minutes": 120,
      "travel_time_to_location_minutes": 30,
      "travel_time_from_location_minutes": 30,
      "buffer_before_minutes": 15,
      "buffer_after_minutes": 15,
      "actual_start_time": "2024-01-15T09:15:00Z",
      "actual_end_time": "2024-01-15T12:45:00Z",
      "dynamic_price_breakdown": {
        "base_price": 500.00,
        "surge_multiplier": 1.0,
        "final_price": 500.00,
        "demand_level": "normal"
      }
    }
  ]
}
```

### Create Booking (Customer)
```http
POST /api/bookings/
Authorization: Bearer <customer_token>
Content-Type: application/json

Request:
{
  "service": 1,
  "pincode": "110001",
  "scheduled_date": "2024-01-15T10:00:00Z",
  "customer_notes": "Please arrive on time"
}

Response: 201 Created
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer": 1,
  "service": 1,
  "status": "pending",
  "total_price": "550.00",
  "pincode": "110001",
  "scheduled_date": "2024-01-15T10:00:00Z",
  "customer_notes": "Please arrive on time",
  "created_at": "2024-01-10T08:30:00Z"
}
```

### Get Booking Details
```http
GET /api/bookings/{id}/
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer": 1,
  "customer_name": "John Doe",
  "vendor": 2,
  "vendor_name": "Jane Smith",
  "service": 1,
  "service_name": "AC Repair",
  "status": "confirmed",
  "total_price": "500.00",
  "pincode": "110001",
  "scheduled_date": "2024-01-15T10:00:00Z"
}
```

### Accept Booking (Vendor)
```http
POST /api/bookings/{id}/accept_booking/
Authorization: Bearer <vendor_token>

Response: 200 OK
{
  "message": "Booking accepted successfully"
}
```

### Complete Booking (Vendor)
```http
POST /api/bookings/{id}/complete_booking/
Authorization: Bearer <vendor_token>

Response: 200 OK
{
  "message": "Booking completed successfully",
  "payment_intent": {
    "id": "pi_mock_booking_id",
    "client_secret": "pi_mock_booking_id_secret",
    "amount": 50000,
    "status": "requires_payment_method"
  }
}
```

### Request Signature (Vendor)
```http
POST /api/bookings/{id}/request_signature/
Authorization: Bearer <vendor_token>

Response: 200 OK
{
  "message": "Signature requested successfully",
  "signature_id": "650e8400-e29b-41d4-a716-446655440000"
}
```

### Update Booking
```http
PATCH /api/bookings/{id}/
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "vendor_notes": "Will arrive 10 minutes early",
  "status": "in_progress"
}

Response: 200 OK
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "vendor_notes": "Will arrive 10 minutes early",
  "status": "in_progress"
}
```

---

## Photo Endpoints

### List Photos
```http
GET /api/photos/
Authorization: Bearer <token>

Query Parameters:
- booking: filter by booking ID

Response: 200 OK
{
  "count": 4,
  "results": [
    {
      "id": 1,
      "booking": "550e8400-e29b-41d4-a716-446655440000",
      "image": "http://localhost:8000/media/photos/2024/01/15/before_image.jpg",
      "image_type": "before",
      "description": "Before starting work",
      "uploaded_by": 2,
      "uploaded_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Upload Photo
```http
POST /api/photos/
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
- booking: 550e8400-e29b-41d4-a716-446655440000
- image_type: before
- image: <file>
- description: Before starting work

Response: 201 Created
{
  "id": 1,
  "booking": "550e8400-e29b-41d4-a716-446655440000",
  "image": "http://localhost:8000/media/photos/2024/01/15/before_image.jpg",
  "image_type": "before",
  "description": "Before starting work",
  "uploaded_by": 2,
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

### Delete Photo
```http
DELETE /api/photos/{id}/
Authorization: Bearer <token>

Response: 204 No Content
```

---

## Signature Endpoints

### List Signatures
```http
GET /api/signatures/
Authorization: Bearer <token>

Response: 200 OK
{
  "count": 5,
  "results": [
    {
      "id": "650e8400-e29b-41d4-a716-446655440000",
      "booking": "550e8400-e29b-41d4-a716-446655440000",
      "signed_by": 1,
      "status": "signed",
      "signature_hash": "a1b2c3d4e5f6...",
      "satisfaction_rating": 5,
      "satisfaction_comments": "Excellent service!",
      "requested_at": "2024-01-15T12:00:00Z",
      "signed_at": "2024-01-15T14:00:00Z",
      "expires_at": "2024-01-17T12:00:00Z"
    }
  ]
}
```

### Sign Booking (Customer)
```http
POST /api/signatures/{id}/sign/
Authorization: Bearer <customer_token>
Content-Type: application/json

Request:
{
  "satisfaction_rating": 5,
  "comments": "Excellent service, very professional!"
}

Response: 200 OK
{
  "message": "Booking signed successfully",
  "signature_hash": "a1b2c3d4e5f6789012345678901234567890abcdef"
}
```

---

## Payment Endpoints

### List Payments
```http
GET /api/payments/
Authorization: Bearer <token>

Response: 200 OK
{
  "count": 10,
  "results": [
    {
      "id": "750e8400-e29b-41d4-a716-446655440000",
      "booking": "550e8400-e29b-41d4-a716-446655440000",
      "amount": "500.00",
      "status": "completed",
      "payment_type": "automatic",
      "stripe_payment_intent_id": "pi_abc123",
      "stripe_charge_id": "ch_xyz789",
      "processed_by": 3,
      "processed_at": "2024-01-15T15:00:00Z",
      "created_at": "2024-01-15T14:00:00Z",
      "updated_at": "2024-01-15T15:00:00Z"
    }
  ]
}
```

### Process Manual Payment (Ops Manager)
```http
POST /api/payments/{id}/process_manual_payment/
Authorization: Bearer <ops_manager_token>

Response: 200 OK
{
  "message": "Payment processed successfully"
}
```

---

## Address Endpoints

### List Addresses
```http
GET /api/addresses/
Authorization: Bearer <customer_token>

Query Parameters:
- is_default: filter by default status

Response: 200 OK
{
  "count": 3,
  "results": [
    {
      "id": "850e8400-e29b-41d4-a716-446655440000",
      "label": "Home",
      "address_line": "123 Main Street, Apartment 4B",
      "pincode": "110001",
      "lat": "28.7041",
      "lng": "77.1025",
      "is_default": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create Address
```http
POST /api/addresses/
Authorization: Bearer <customer_token>
Content-Type: application/json

Request:
{
  "label": "Office",
  "address_line": "456 Business Park, Floor 3",
  "pincode": "110002",
  "lat": "28.7141",
  "lng": "77.1125",
  "is_default": false
}

Response: 201 Created
{
  "id": "950e8400-e29b-41d4-a716-446655440000",
  "label": "Office",
  "address_line": "456 Business Park, Floor 3",
  "pincode": "110002",
  "lat": "28.7141",
  "lng": "77.1125",
  "is_default": false,
  "created_at": "2024-01-10T08:30:00Z",
  "updated_at": "2024-01-10T08:30:00Z"
}
```

### Set Default Address
```http
POST /api/addresses/{id}/set_default/
Authorization: Bearer <customer_token>

Response: 200 OK
{
  "message": "Default address updated successfully"
}
```

---

## Vendor Endpoints

### Vendor Availability
```http
GET /api/vendor-availability/
Authorization: Bearer <vendor_token>

Response: 200 OK
{
  "count": 7,
  "results": [
    {
      "id": 1,
      "vendor": 2,
      "vendor_name": "Jane Smith",
      "day_of_week": 1,
      "start_time": "09:00:00",
      "end_time": "18:00:00",
      "is_active": true,
      "primary_pincode": "110001",
      "service_area_pincodes": ["110001", "110002", "110003"],
      "preferred_buffer_minutes": 15,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}

POST /api/vendor-availability/
Authorization: Bearer <vendor_token>
Content-Type: application/json

Request:
{
  "day_of_week": 1,
  "start_time": "09:00:00",
  "end_time": "18:00:00",
  "primary_pincode": "110001",
  "service_area_pincodes": ["110001", "110002"],
  "preferred_buffer_minutes": 15
}
```

### Vendor Search
```http
GET /api/vendor-search/
Authorization: Bearer <token>

Query Parameters:
- pincode: required
- service_id: optional

Response: 200 OK
{
  "vendors": [
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane@example.com",
      "phone": "+919876543210",
      "pincode": "110001",
      "rating": 4.5,
      "total_jobs": 25,
      "availability": {
        "day_of_week": 1,
        "start_time": "09:00:00",
        "end_time": "18:00:00"
      },
      "travel_time": 30,
      "distance_km": 10,
      "primary_service_area": "110001"
    }
  ],
  "total_vendors": 5,
  "pincode": "110001",
  "demand_index": 5.5
}
```

---

## Dynamic Pricing Endpoints

### Get Dynamic Price
```http
GET /api/dynamic-pricing/
Authorization: Bearer <token>

Query Parameters:
- service_id: required
- pincode: required
- scheduled_datetime: optional (ISO format)

Response: 200 OK
{
  "service": {
    "id": 1,
    "name": "AC Repair",
    "category": "Appliance"
  },
  "pincode": "110001",
  "pricing": {
    "base_price": 500.00,
    "surge_multiplier": 1.2,
    "final_price": 600.00,
    "demand_level": "high",
    "factors": {
      "time_based_multiplier": 1.0,
      "demand_based_multiplier": 1.15,
      "vendor_availability_multiplier": 1.05
    },
    "breakdown": {
      "base": 500.00,
      "surge": 100.00,
      "total": 600.00
    }
  },
  "timestamp": "2024-01-10T08:30:00Z"
}
```

### Get Price Predictions
```http
POST /api/dynamic-pricing/
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "service_id": 1,
  "pincode": "110001",
  "days": 7
}

Response: 200 OK
{
  "service": {
    "id": 1,
    "name": "AC Repair",
    "category": "Appliance",
    "base_price": 500.00
  },
  "pincode": "110001",
  "predictions": [
    {
      "date": "2024-01-11",
      "predicted_price": 550.00,
      "surge_multiplier": 1.1,
      "confidence": 0.85,
      "demand_level": "normal"
    },
    {
      "date": "2024-01-12",
      "predicted_price": 625.00,
      "surge_multiplier": 1.25,
      "confidence": 0.78,
      "demand_level": "high"
    }
  ],
  "timestamp": "2024-01-10T08:30:00Z"
}
```

---

## Smart Scheduling Endpoints

### Get Available Time Slots
```http
GET /api/smart-scheduling/
Authorization: Bearer <token>

Query Parameters:
- vendor_id: required
- service_id: required
- customer_pincode: required
- preferred_date: required (YYYY-MM-DD)

Response: 200 OK
{
  "available_slots": [
    {
      "start_time": "2024-01-15T09:00:00Z",
      "end_time": "2024-01-15T12:00:00Z",
      "is_available": true,
      "score": 8.5,
      "travel_time_minutes": 30,
      "buffer_time_minutes": 15
    },
    {
      "start_time": "2024-01-15T14:00:00Z",
      "end_time": "2024-01-15T17:00:00Z",
      "is_available": true,
      "score": 7.2,
      "travel_time_minutes": 30,
      "buffer_time_minutes": 15
    }
  ],
  "total_slots": 5
}
```

### Get Optimal Booking Suggestion
```http
POST /api/smart-scheduling/
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "vendor_id": 2,
  "service_id": 1,
  "customer_pincode": "110001",
  "preferred_date": "2024-01-15"
}

Response: 200 OK
{
  "optimal_slot": {
    "recommended_time": "2024-01-15T09:00:00Z",
    "score": 8.5,
    "reasoning": "Best time based on vendor availability and minimal travel time",
    "travel_time_minutes": 30,
    "estimated_duration_minutes": 120
  }
}
```

### Vendor Schedule Optimization
```http
GET /api/vendor-optimization/
Authorization: Bearer <vendor_token>

Query Parameters:
- date: required (YYYY-MM-DD)

Response: 200 OK
{
  "optimization_date": "2024-01-15",
  "total_bookings": 3,
  "total_duration_minutes": 360,
  "total_travel_time_minutes": 90,
  "efficiency_score": 7.8,
  "suggestions": [
    {
      "type": "route_optimization",
      "message": "Consider rearranging bookings to minimize travel time",
      "potential_savings_minutes": 20
    }
  ]
}
```

---

## Travel Time Endpoints

### Get Travel Time
```http
GET /api/travel-time/
Authorization: Bearer <token>

Query Parameters:
- from_pincode: required
- to_pincode: required

Response: 200 OK
{
  "from_pincode": "110001",
  "to_pincode": "110002",
  "duration_minutes": 30,
  "distance_km": 10.5,
  "estimated_traffic_multiplier": 1.2,
  "cached": true
}
```

---

## Dispute Endpoints

### List Disputes
```http
GET /api/disputes/
Authorization: Bearer <token>

Response: 200 OK
{
  "count": 5,
  "results": [
    {
      "id": "a50e8400-e29b-41d4-a716-446655440000",
      "title": "Service not completed properly",
      "dispute_type": "quality_issue",
      "severity": "medium",
      "status": "open",
      "customer_name": "John Doe",
      "vendor_name": "Jane Smith",
      "assigned_mediator_name": "Admin User",
      "created_at": "2024-01-15T16:00:00Z",
      "messages_count": 3
    }
  ]
}
```

### Create Dispute
```http
POST /api/disputes/create_dispute/
Authorization: Bearer <customer_token>
Content-Type: application/json

Request:
{
  "booking_id": "550e8400-e29b-41d4-a716-446655440000",
  "dispute_type": "quality_issue",
  "title": "Service not completed properly",
  "description": "The AC is still not cooling properly after the repair",
  "evidence": {
    "photos": ["url1", "url2"],
    "notes": "Temperature still 30°C"
  }
}

Response: 201 Created
{
  "id": "a50e8400-e29b-41d4-a716-446655440000",
  "booking": "550e8400-e29b-41d4-a716-446655440000",
  "dispute_type": "quality_issue",
  "title": "Service not completed properly",
  "status": "open",
  "created_at": "2024-01-15T16:00:00Z"
}
```

### Get Dispute Messages
```http
GET /api/disputes/{id}/messages/
Authorization: Bearer <token>

Query Parameters:
- page: optional (default: 1)
- page_size: optional (default: 50)

Response: 200 OK
{
  "messages": [
    {
      "id": "b50e8400-e29b-41d4-a716-446655440000",
      "sender_name": "John Doe",
      "recipient_name": "Jane Smith",
      "message_type": "text",
      "content": "The AC is still not working",
      "is_read": true,
      "created_at": "2024-01-15T16:30:00Z",
      "is_mine": true
    }
  ],
  "total_count": 3,
  "page": 1,
  "page_size": 50,
  "has_more": false
}
```

### Send Dispute Message
```http
POST /api/disputes/{id}/send_message/
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
- content: "I will revisit and fix the issue"
- message_type: "text"
- attachment: <file> (optional)

Response: 201 Created
{
  "id": "c50e8400-e29b-41d4-a716-446655440000",
  "sender_name": "Jane Smith",
  "content": "I will revisit and fix the issue",
  "created_at": "2024-01-15T17:00:00Z"
}
```

### Resolve Dispute (Admin)
```http
POST /api/disputes/{id}/resolve/
Authorization: Bearer <ops_manager_token>
Content-Type: application/json

Request:
{
  "resolution_notes": "Vendor agreed to revisit and fix the issue",
  "resolution_amount": 100.00,
  "evidence": {
    "resolution_type": "partial_refund"
  }
}

Response: 200 OK
{
  "id": "a50e8400-e29b-41d4-a716-446655440000",
  "status": "resolved",
  "resolution_notes": "Vendor agreed to revisit and fix the issue",
  "resolved_at": "2024-01-15T18:00:00Z"
}
```

---

## Vendor Application Endpoints

### List Applications
```http
GET /api/vendor-applications/
Authorization: Bearer <onboard_manager_token>

Response: 200 OK
{
  "count": 10,
  "results": [
    {
      "id": "d50e8400-e29b-41d4-a716-446655440000",
      "applicant_name": "New Vendor",
      "application_type": "new_vendor",
      "full_name": "New Vendor Name",
      "primary_service_category": "Appliance",
      "status": "pending",
      "submitted_at": "2024-01-10T08:00:00Z",
      "documents_count": 3,
      "is_complete": true
    }
  ]
}
```

### Submit Application (Vendor)
```http
POST /api/vendor-applications/{id}/submit/
Authorization: Bearer <vendor_token>

Response: 200 OK
{
  "id": "d50e8400-e29b-41d4-a716-446655440000",
  "status": "submitted"
}
```

### Review Application (Onboard Manager)
```http
POST /api/vendor-applications/{id}/review/
Authorization: Bearer <onboard_manager_token>
Content-Type: application/json

Request:
{
  "decision": "approve",
  "notes": "All documents verified"
}

Response: 200 OK
{
  "id": "d50e8400-e29b-41d4-a716-446655440000",
  "status": "approved",
  "reviewed_at": "2024-01-12T10:00:00Z"
}
```

---

## Earnings Endpoints

### List Earnings (Vendor)
```http
GET /api/earnings/
Authorization: Bearer <vendor_token>

Query Parameters:
- status: filter by status (pending, released, on_hold)

Response: 200 OK
{
  "count": 15,
  "results": [
    {
      "id": "e50e8400-e29b-41d4-a716-446655440000",
      "vendor": 2,
      "vendor_name": "Jane Smith",
      "booking": "550e8400-e29b-41d4-a716-446655440000",
      "booking_service": "AC Repair",
      "customer_name": "John Doe",
      "amount": "400.00",
      "status": "released",
      "release_date": "2024-01-20T00:00:00Z",
      "processed_by": 3,
      "processed_at": "2024-01-18T10:00:00Z",
      "created_at": "2024-01-15T15:00:00Z"
    }
  ]
}
```

### Earnings Summary (Vendor)
```http
GET /api/earnings/summary/
Authorization: Bearer <vendor_token>

Response: 200 OK
{
  "total_earnings": 5000.00,
  "pending_earnings": 800.00,
  "recent_earnings": [
    {
      "id": "e50e8400-e29b-41d4-a716-446655440000",
      "amount": "400.00",
      "status": "released"
    }
  ]
}
```

### Release Payment (Ops Manager)
```http
POST /api/earnings/{id}/release_payment/
Authorization: Bearer <ops_manager_token>

Response: 200 OK
{
  "message": "Payment released successfully",
  "earning_id": "e50e8400-e29b-41d4-a716-446655440000"
}
```

---

## Performance Metrics Endpoints

### Get Performance Summary (Vendor)
```http
GET /api/performance-metrics/summary/
Authorization: Bearer <vendor_token>

Response: 200 OK
{
  "id": "f50e8400-e29b-41d4-a716-446655440000",
  "vendor": 2,
  "vendor_name": "Jane Smith",
  "avg_rating": 4.5,
  "completion_rate": 95.5,
  "on_time_rate": 92.0,
  "dispute_rate": 2.5,
  "tier": "gold",
  "bonus_points": 850,
  "last_calculated": "2024-01-15T00:00:00Z"
}
```

---

## Admin Dashboard Endpoints

### Cache Management

#### Get Cache Stats
```http
GET /admin-dashboard/cache/
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "status": "success",
  "cache_stats": {
    "default": {
      "name": "default",
      "backend": "RedisCache",
      "timeout": 300,
      "redis_version": "7.0.0",
      "used_memory": "2.5M",
      "connected_clients": 5,
      "keyspace_hits": 1250,
      "keyspace_misses": 150,
      "hit_rate_percentage": 89.29,
      "total_keys": 450
    },
    "overall_health": {
      "healthy_caches": 4,
      "total_caches": 4,
      "health_percentage": 100.0,
      "average_hit_rate": 85.5,
      "status": "healthy"
    }
  },
  "timestamp": "2024-01-15T10:00:00Z"
}
```

#### Clear Cache
```http
POST /admin-dashboard/cache/
Authorization: Bearer <admin_token>
Content-Type: application/json

Request:
{
  "cache_type": "all"
}

Response: 200 OK
{
  "status": "success",
  "message": "Cache \"all\" cleared successfully",
  "result": {
    "cleared": ["default", "sessions", "search_results", "api_data"],
    "errors": []
  }
}
```

### Pincode Scaling Data
```http
GET /admin-dashboard/pincode-scaling/data/
Authorization: Bearer <admin_token>

Query Parameters:
- service_type: optional
- days_back: optional (default: 30)

Response: 200 OK
{
  "status": "success",
  "data": [
    {
      "pincode": "110001",
      "total_bookings": 45,
      "completed_bookings": 38,
      "pending_bookings": 5,
      "cancelled_bookings": 2,
      "completion_rate": 84.44,
      "cancellation_rate": 4.44,
      "available_vendors": 8,
      "demand_intensity": 5.63,
      "estimated_wait_time_hours": 0.6,
      "zone_status": "optimal",
      "heat_intensity": 56.3
    }
  ],
  "summary": {
    "total_pincodes": 25,
    "total_bookings": 1250,
    "total_vendors": 85,
    "high_demand_zones": 3,
    "optimal_zones": 18
  }
}
```

### Edit History
```http
GET /admin-dashboard/edit-history/
Authorization: Bearer <super_admin_token>

Query Parameters:
- model: filter by model type
- user: filter by username
- action: filter by action type
- start_date: filter by start date
- end_date: filter by end date
- page: pagination
- page_size: items per page

Response: 200 OK
{
  "status": "success",
  "data": [
    {
      "id": 123,
      "user": "admin1",
      "user_role": "super_admin",
      "action": "update",
      "resource_type": "Booking",
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2024-01-15T10:30:00Z",
      "ip_address": "127.0.0.1",
      "old_values": {"status": "pending"},
      "new_values": {"status": "confirmed"},
      "diff": [
        {
          "field": "status",
          "old_value": "pending",
          "new_value": "confirmed",
          "change_type": "modified"
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 250,
    "total_pages": 13,
    "has_next": true,
    "has_previous": false
  }
}
```

### Dashboard Stats
```http
GET /admin-dashboard/dashboard/stats/
Authorization: Bearer <admin_token>

Response: 200 OK
{
  "status": "success",
  "cache_health": {
    "health_percentage": 100.0,
    "average_hit_rate": 85.5,
    "status": "healthy"
  },
  "activity_stats": {
    "total_actions_24h": 156,
    "unique_users_24h": 23,
    "top_actions": [
      {"action": "update", "count": 45},
      {"action": "create", "count": 38}
    ]
  },
  "pincode_stats": {
    "total_pincodes_served": 25,
    "avg_bookings_per_pincode": 50.0,
    "active_vendors": 85
  }
}
```

### Notification Management
```http
GET /admin-dashboard/notifications/
Authorization: Bearer <super_admin_token>

Response: 200 OK
{
  "status": "success",
  "notification_stats": {
    "total_sent_today": 45,
    "total_sent_week": 312,
    "success_rate_today": 95.56,
    "by_type_today": {
      "signature_request": 12,
      "payment_hold": 8,
      "booking_timeout": 3
    },
    "by_method_today": {
      "email": 30,
      "websocket": 15
    },
    "failed_today": 2
  },
  "business_alerts": {
    "active_alerts": 5,
    "critical_alerts": 1
  }
}

POST /admin-dashboard/notifications/
Content-Type: application/json

Request:
{
  "action": "send_bonus_alerts"
}

Response: 200 OK
{
  "status": "success",
  "message": "Bonus alerts task started. Task ID: abc-123-def",
  "task_id": "abc-123-def"
}
```

---

## Advanced AI Features Endpoints

### Pincode AI Analytics
```http
GET /api/pincode-ai-analytics/
Authorization: Bearer <admin_token>

Query Parameters:
- pincode: required
- days: optional (default: 30)

Response: 200 OK
{
  "status": "success",
  "pincode_analysis": {
    "pincode": "110001",
    "demand_forecast": {
      "next_7_days": [
        {"date": "2024-01-16", "predicted_bookings": 8, "confidence": 0.85}
      ],
      "trend": "increasing",
      "seasonal_factor": 1.15
    },
    "vendor_recommendations": {
      "optimal_vendor_count": 10,
      "current_vendor_count": 8,
      "shortage": 2
    },
    "pricing_insights": {
      "recommended_surge_multiplier": 1.2,
      "peak_hours": ["09:00-11:00", "14:00-16:00"]
    }
  },
  "timestamp": "2024-01-15T10:00:00Z"
}
```

### Advanced Dispute Resolution
```http
GET /api/advanced-dispute-resolution/{dispute_id}/
Authorization: Bearer <ops_manager_token>

Response: 200 OK
{
  "status": "success",
  "dispute_id": "a50e8400-e29b-41d4-a716-446655440000",
  "resolution_analysis": {
    "recommended_action": "partial_refund",
    "confidence": 0.82,
    "reasoning": "Pattern matches similar resolved cases",
    "suggested_amount": 100.00
  },
  "escalation_analysis": {
    "should_escalate": false,
    "escalation_score": 3.2,
    "factors": ["low_severity", "vendor_responsive"]
  }
}
```

### Advanced Vendor Bonus
```http
GET /api/advanced-vendor-bonus/
Authorization: Bearer <vendor_token>

Query Parameters:
- vendor_id: optional (admin only)
- days: optional (default: 30)

Response: 200 OK
{
  "status": "success",
  "vendor_bonus_analysis": {
    "performance_score": 8.5,
    "predicted_bonus": 850.00,
    "bonus_breakdown": {
      "quality_bonus": 300.00,
      "efficiency_bonus": 250.00,
      "customer_satisfaction_bonus": 300.00
    },
    "improvement_suggestions": [
      "Reduce average completion time by 10 minutes",
      "Increase customer satisfaction rating to 4.8"
    ]
  }
}
```

---

## Analytics Endpoints

### Dispute Analytics
```http
GET /api/analytics/disputes/
Authorization: Bearer <ops_manager_token>

Query Parameters:
- days: optional (default: 30)

Response: 200 OK
{
  "total_disputes": 25,
  "by_status": {
    "open": 5,
    "in_progress": 8,
    "resolved": 12
  },
  "by_type": {
    "quality_issue": 10,
    "payment_dispute": 8,
    "signature_refusal": 7
  },
  "average_resolution_time_hours": 48.5,
  "resolution_rate": 80.0
}
```

### Vendor Onboarding Analytics
```http
GET /api/analytics/vendor-onboarding/
Authorization: Bearer <onboard_manager_token>

Response: 200 OK
{
  "total_applications": 45,
  "by_status": {
    "pending": 12,
    "submitted": 8,
    "approved": 20,
    "rejected": 5
  },
  "average_review_time_days": 3.5,
  "approval_rate": 80.0
}
```

---

## Chat Endpoints

### Chat Query
```http
POST /api/chat/query/
Content-Type: application/json

Request:
{
  "user_id": 1,
  "role": "customer",
  "message": "Track my bookings"
}

Response: 200 OK
{
  "response": "Here are your recent bookings:\n\n• AC Repair - Confirmed\n  Scheduled for: 2024-01-15 10:00\n  Booking ID: 550e8400-e29b-41d4-a716-446655440000"
}
```

### Chat Context
```http
GET /api/chat/context/
Query Parameters:
- user_id: required
- role: required

Response: 200 OK
{
  "context": {
    "role": "customer",
    "suggested_actions": [
      "Track my bookings",
      "Approve signature for completed service",
      "View booking details"
    ],
    "recent_activities": [
      {
        "type": "booking",
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "service": "AC Repair",
        "status": "Confirmed",
        "date": "2024-01-15T10:00:00Z"
      }
    ]
  }
}
```

---

## WebSocket Endpoints

### Booking Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/bookings/{booking_id}/?token=<jwt_token>');

// Message Format
{
  "type": "booking_status_change",
  "data": {
    "booking_id": "550e8400-e29b-41d4-a716-446655440000",
    "old_status": "pending",
    "new_status": "confirmed",
    "timestamp": "2024-01-15T10:00:00Z"
  }
}
```

### User Notifications
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications/{user_id}/?token=<jwt_token>');

// Message Format
{
  "type": "signature_request",
  "data": {
    "signature_id": "650e8400-e29b-41d4-a716-446655440000",
    "booking_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Signature requested for AC Repair",
    "timestamp": "2024-01-15T12:00:00Z"
  }
}
```

### Chat WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/{user_id}/{role}/?token=<jwt_token>');

// Send Message
ws.send(JSON.stringify({
  "type": "chat_message",
  "message": "What are my pending jobs?"
}));

// Receive Response
{
  "type": "chat_response",
  "data": {
    "message": "You have 3 pending jobs...",
    "timestamp": "2024-01-15T10:00:00Z"
  }
}
```

### Live Status Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/status/{user_id}/{role}/?token=<jwt_token>');

// Message Format
{
  "type": "status_update",
  "data": {
    "user_id": 1,
    "is_online": true,
    "last_seen": "2024-01-15T10:00:00Z"
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "service_id and pincode are required"
}
```

### 401 Unauthorized
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "error": "Booking not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "An unexpected error occurred",
  "details": "Error message details"
}
```

---

## Rate Limiting & Best Practices

1. **Pagination**: Most list endpoints support pagination with `page` and `page_size` parameters
2. **Filtering**: Use query parameters to filter results
3. **Authentication**: Always include JWT token in Authorization header
4. **WebSockets**: Reconnect automatically on disconnection
5. **Error Handling**: Check response status codes and handle errors gracefully
6. **Caching**: Cache GET requests where appropriate
7. **File Uploads**: Use `multipart/form-data` content type for file uploads
8. **Date Formats**: Use ISO 8601 format for dates (YYYY-MM-DDTHH:MM:SSZ)

---

This comprehensive guide covers all API endpoints in the HomeServe Pro system. Use this as a reference when integrating the frontend application.
