# HomeServe Pro API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All API endpoints (except login/register) require JWT authentication.

### Headers
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

## API Endpoints

### Authentication Endpoints

#### Login
```http
POST /auth/login/
Content-Type: application/json

{
  \"username\": \"customer1\",
  \"password\": \"password123\"
}
```

**Response:**
```json
{
  \"access\": \"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...\",
  \"refresh\": \"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...\",
  \"user\": {
    \"id\": 1,
    \"username\": \"customer1\",
    \"role\": \"customer\",
    \"is_verified\": true
  }
}
```

#### Send OTP (for vendors)
```http
POST /auth/send-otp/
Content-Type: application/json

{
  \"phone\": \"+919876543210\"
}
```

#### Verify OTP
```http
POST /auth/verify-otp/
Content-Type: application/json

{
  \"phone\": \"+919876543210\",
  \"otp\": \"123456\"
}
```

### Services

#### List All Services
```http
GET /api/services/
Authorization: Bearer <token>
```

**Response:**
```json
{
  \"count\": 5,
  \"results\": [
    {
      \"id\": 1,
      \"name\": \"AC Repair\",
      \"description\": \"Air conditioning repair and maintenance\",
      \"base_price\": \"500.00\",
      \"category\": \"Appliance\",
      \"duration_minutes\": 120,
      \"is_active\": true
    }
  ]
}
```

#### Get Service Details
```http
GET /api/services/{id}/
Authorization: Bearer <token>
```

### Bookings

#### Create Booking (Customer)
```http
POST /api/bookings/
Authorization: Bearer <token>
Content-Type: application/json

{
  \"service\": 1,
  \"total_price\": \"500.00\",
  \"pincode\": \"110001\",
  \"scheduled_date\": \"2024-01-15T10:00:00Z\",
  \"customer_notes\": \"Please arrive on time\"
}
```

#### List My Bookings
```http
GET /api/bookings/
Authorization: Bearer <token>
```

#### Accept Booking (Vendor)
```http
POST /api/bookings/{id}/accept_booking/
Authorization: Bearer <vendor_token>
```

#### Complete Booking (Vendor)
```http
POST /api/bookings/{id}/complete_booking/
Authorization: Bearer <vendor_token>
```

**Response:**
```json
{
  \"message\": \"Booking completed successfully\",
  \"payment_intent\": {
    \"id\": \"pi_mock_booking_id\",
    \"client_secret\": \"pi_mock_booking_id_secret\",
    \"amount\": 50000,
    \"status\": \"requires_payment_method\"
  }
}
```

#### Request Signature (Vendor)
```http
POST /api/bookings/{id}/request_signature/
Authorization: Bearer <vendor_token>
```

### Photos

#### Upload Photo
```http
POST /api/photos/
Authorization: Bearer <token>
Content-Type: multipart/form-data

booking: 1
image_type: before
image: <file>
description: Before starting work
```

#### List Photos for Booking
```http
GET /api/photos/?booking={booking_id}
Authorization: Bearer <token>
```

### Signatures

#### List My Signatures
```http
GET /api/signatures/
Authorization: Bearer <token>
```

#### Sign Booking (Customer)
```http
POST /api/signatures/{id}/sign/
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  \"satisfaction_rating\": 5,
  \"comments\": \"Excellent service, very professional!\"
}
```

**Response:**
```json
{
  \"message\": \"Booking signed successfully\",
  \"signature_hash\": \"a1b2c3d4e5f6789012345678901234567890abcdef\"
}
```

### Payments

#### List Payments
```http
GET /api/payments/
Authorization: Bearer <token>
```

#### Process Manual Payment (Ops Manager)
```http
POST /api/payments/{id}/process_manual_payment/
Authorization: Bearer <ops_manager_token>
```

### Users (Admin Only)

#### List Users
```http
GET /api/users/
Authorization: Bearer <admin_token>
```

#### Filter Users by Role
```http
GET /api/users/?role=vendor
Authorization: Bearer <admin_token>
```

### Audit Logs (Super Admin Only)

#### View Audit Trail
```http
GET /api/audit-logs/
Authorization: Bearer <super_admin_token>
```

#### Filter by Action
```http
GET /api/audit-logs/?action=signature_sign
Authorization: Bearer <super_admin_token>
```

## Stripe Payment Integration

### Payment Intent Creation
When a booking is completed, a Stripe Payment Intent is automatically created:

```javascript
// Frontend integration example
const stripe = Stripe('pk_test_51RywjnGe3NmlcQxAnHkCg3M6DHS5gIYXIszN6Df6jaC0YEVcFUT0mFfEQRFiSJfCalB5lHe3j7rAL5T7AhDdeZ7I00cJAgPnc2');

// After booking completion
fetch('/api/bookings/123/complete_booking/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  const { client_secret } = data.payment_intent;
  
  // Use the client_secret to confirm payment on frontend
  stripe.confirmCardPayment(client_secret, {
    payment_method: {
      card: cardElement,
      billing_details: {
        name: 'Customer Name',
      },
    }
  });
});
```

### Webhook Configuration
For production, configure webhook endpoint:
```
Webhook URL: https://yourdomain.com/api/webhooks/stripe/
Webhook Secret: whsec_1d48c06de7d9e3354f3acf8bf5fb785fb24623e4144ce86b5861af140a42bc18
```

## Email Notifications & OTP

### Enhanced OTP Support
The system now supports both SMS and Email OTP:

#### Send OTP via Email
```bash
curl -X POST http://localhost:8000/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "method": "email"
  }'
```

#### Send OTP via SMS
```bash
curl -X POST http://localhost:8000/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "method": "sms"
  }'
```

#### Verify OTP (Email or Phone)
```bash
curl -X POST http://localhost:8000/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp": "123456"
  }'
```

### SMTP Configuration
Configure email settings in .env:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

**Note**: Use App Passwords for Gmail, not your regular password.

### Signature Request Email
When a vendor requests a signature, customers receive:
- HTML formatted email with service details
- Secure signature link with 48-hour expiry
- Booking information and provider details
- Professional email template

## Configuration Summary

### .env File Setup
```env
# Stripe Configuration (CONFIGURED)
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# Email Configuration (TO BE CONFIGURED)
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password

# Twilio Configuration (OPTIONAL)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890
```

## Error Responses

### Authentication Error
```json
{
  \"detail\": \"Given token not valid for any token type\",
  \"code\": \"token_not_valid\",
  \"messages\": [
    {
      \"token_class\": \"AccessToken\",
      \"token_type\": \"access\",
      \"message\": \"Token is invalid or expired\"
    }
  ]
}
```

### Permission Error
```json
{
  \"detail\": \"You do not have permission to perform this action.\"
}
```

### Validation Error
```json
{
  \"field_name\": [
    \"This field is required.\"
  ]
}
```

## Rate Limiting
- No rate limiting implemented in development
- In production, implement Django-ratelimit for API protection

## Sample cURL Commands

### Login
```bash
curl -X POST http://localhost:8000/auth/login/ \\n  -H \"Content-Type: application/json\" \\n  -d '{\"username\": \"customer1\", \"password\": \"password123\"}'
```

### Create Booking
```bash
curl -X POST http://localhost:8000/api/bookings/ \\n  -H \"Authorization: Bearer YOUR_TOKEN\" \\n  -H \"Content-Type: application/json\" \\n  -d '{
    \"service\": 1,
    \"total_price\": \"500.00\",
    \"pincode\": \"110001\",
    \"scheduled_date\": \"2024-01-15T10:00:00Z\"
  }'
```

### Sign Booking
```bash
curl -X POST http://localhost:8000/api/signatures/1/sign/ \\n  -H \"Authorization: Bearer YOUR_CUSTOMER_TOKEN\" \\n  -H \"Content-Type: application/json\" \\n  -d '{
    \"satisfaction_rating\": 5,
    \"comments\": \"Great service!\"
  }'
```

---

**Note**: Replace `YOUR_TOKEN`, `YOUR_CUSTOMER_TOKEN`, etc. with actual JWT tokens obtained from the login endpoint.