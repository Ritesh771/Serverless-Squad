# HomeServe Pro (HouseServe Hub) - Full-Stack Service Booking Platform<<<<<<< HEAD

# HomeServe Pro (INSTAFIX) - Complete Backend

🚀 **A comprehensive role-based web platform for home service management with AI integration, digital signatures, automated payment processing, and modern React frontend.**

🚀 **A comprehensive role-based web platform backend for home service management with AI integration, digital signatures, and automated payment processing.**

## 🏗️ Architecture Overview

## 🏗️ Architecture Overview

This is a full-stack application consisting of:

- **Backend**: Django REST Framework with real-time WebSockets### Tech Stack

- **Frontend**: React 18 with TypeScript and modern UI components- **Backend Framework**: Django REST Framework (DRF)

- **Database**: SQLite (configurable to PostgreSQL/MySQL)- **Database**: SQLite (easily configurable to PostgreSQL/MySQL)

- **Authentication**: JWT + OTP for Vendors (Twilio)- **Authentication**: JWT + OTP for Vendors (Twilio)

- **Payments**: Stripe Integration- **Payments**: Stripe Integration

- **Real-time**: Django Channels (WebSockets)- **Real-time**: Django Channels (WebSockets)

- **Background Tasks**: Celery + Redis- **Background Tasks**: Celery + Redis

- **File Storage**: Local Media (configurable to AWS S3)

### System Roles (5 Total)- **Digital Signatures**: SHA-256 Hash with Mock API

1. **Customer** - Book services, provide signatures, make payments

2. **Vendor** - Accept bookings, upload photos, request signatures### System Roles (5 Total)

3. **Onboard Manager** - Manage vendor onboarding1. **Customer** - Book services, provide signatures, make payments

4. **Ops Manager** - Monitor operations, process manual payments2. **Vendor** - Accept bookings, upload photos, request signatures

5. **Super Admin** - Full system control and audit trails3. **Onboard Manager** - Manage vendor onboarding

4. **Ops Manager** - Monitor operations, process manual payments

## 📊 Database Schema5. **Super Admin** - Full system control and audit trails



| Table | Description | Key Features |## 📊 Database Schema

|-------|-------------|-------------|

| `User` | All users with roles | Role-based permissions, OTP verification || Table | Description | Key Features |

| `Service` | Available services | Pricing, categories, duration ||-------|-------------|-------------|

| `Booking` | Service bookings | Status tracking, vendor assignment || `User` | All users with roles | Role-based permissions, OTP verification |

| `Photo` | Before/after images | AI quality comparison ready || `Service` | Available services | Pricing, categories, duration |

| `Signature` | Digital satisfaction signatures | SHA-256 hashing, 48h expiry || `Booking` | Service bookings | Status tracking, vendor assignment |

| `Payment` | Stripe payment records | Auto/manual processing || `Photo` | Before/after images | AI quality comparison ready |

| `AuditLog` | All system actions | Immutable audit trail || `Signature` | Digital satisfaction signatures | SHA-256 hashing, 48h expiry |

| `Payment` | Stripe payment records | Auto/manual processing |

## 🔄 Core Workflow| `AuditLog` | All system actions | Immutable audit trail |



### 1. Customer Books Service## 🔄 Core Workflow

```

POST /api/bookings/### 1. Customer Books Service

{```

  "service_id": 1,POST /api/bookings/

  "pincode": "110001",{

  "scheduled_date": "2024-01-15T10:00:00Z"  \"service_id\": 1,

}  \"pincode\": \"110001\",

```  \"scheduled_date\": \"2024-01-15T10:00:00Z\"

}

### 2. Vendor Accepts & Completes```

```

POST /api/bookings/{id}/accept_booking/### 2. Vendor Accepts & Completes

POST /api/bookings/{id}/complete_booking/```

```POST /api/bookings/{id}/accept_booking/

POST /api/bookings/{id}/complete_booking/

### 3. Digital Signature Request```

```

POST /api/bookings/{id}/request_signature/### 3. Digital Signature Request

``````

POST /api/bookings/{id}/request_signature/

### 4. Customer Signs with Satisfaction```

```

POST /api/signatures/{id}/sign/### 4. Customer Signs with Satisfaction

{```

  "satisfaction_rating": 5,POST /api/signatures/{id}/sign/

  "comments": "Excellent service!"{

}  \"satisfaction_rating\": 5,

```  \"comments\": \"Excellent service!\"

}

### 5. Automatic Payment Release```

- Triggered when signature is verified

- Stripe payment captured automatically### 5. Automatic Payment Release

- Booking marked as "signed"- Triggered when signature is verified

- Stripe payment captured automatically

## 🔐 Authentication & Permissions- Booking marked as \"signed\"



### JWT Authentication## 🔐 Authentication & Permissions

```bash

# Login### JWT Authentication

POST /auth/login/```bash

{# Login

  "username": "customer1",POST /auth/login/

  "password": "password123"{

}  \"username\": \"customer1\",

  \"password\": \"password123\"

# Response}

{

  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",# Response

  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",{

  "user": {  \"access\": \"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...\",

    "id": 1,  \"refresh\": \"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...\",

    "username": "customer1",  \"user\": {

    "role": "customer"    \"id\": 1,

  }    \"username\": \"customer1\",

}    \"role\": \"customer\"

```  }

}

### OTP Verification for Vendors```

```bash

# Send OTP### OTP Verification for Vendors

POST /auth/send-otp/```bash

{"phone": "+919876543210"}# Send OTP

POST /auth/send-otp/

# Verify OTP{\"phone\": \"+919876543210\"}

POST /auth/verify-otp/

{# Verify OTP

  "phone": "+919876543210",POST /auth/verify-otp/

  "otp": "123456"{

}  \"phone\": \"+919876543210\",

```  \"otp\": \"123456\"

}

## 🛠️ API Endpoints```



### Core Resources## 🛠️ API Endpoints

| Endpoint | Description | Permissions |

|----------|-------------|-------------|### Core Resources

| `/api/users/` | User management | Admin only || Endpoint | Description | Permissions |

| `/api/services/` | Available services | All authenticated ||----------|-------------|-------------|

| `/api/bookings/` | Service bookings | Role-based filtered || `/api/users/` | User management | Admin only |

| `/api/photos/` | Before/after photos | Booking participants || `/api/services/` | Available services | All authenticated |

| `/api/signatures/` | Digital signatures | Booking participants || `/api/bookings/` | Service bookings | Role-based filtered |

| `/api/payments/` | Payment records | Role-based filtered || `/api/photos/` | Before/after photos | Booking participants |

| `/api/audit-logs/` | System audit trail | Super Admin only || `/api/signatures/` | Digital signatures | Booking participants |

| `/api/payments/` | Payment records | Role-based filtered |

### Authentication| `/api/audit-logs/` | System audit trail | Super Admin only |

| Endpoint | Description |

|----------|-------------|### Authentication

| `/auth/login/` | JWT token authentication || Endpoint | Description |

| `/auth/refresh/` | Refresh JWT token ||----------|-------------|

| `/auth/send-otp/` | Send OTP for vendor verification || `/auth/login/` | JWT token authentication |

| `/auth/verify-otp/` | Verify OTP and activate vendor || `/auth/refresh/` | Refresh JWT token |

| `/auth/send-otp/` | Send OTP for vendor verification |

## ⚡ Real-time Features (WebSockets)| `/auth/verify-otp/` | Verify OTP and activate vendor |



### Booking Updates## ⚡ Real-time Features (WebSockets)

```javascript

// Connect to booking updates### Booking Updates

const ws = new WebSocket('ws://localhost:8000/ws/bookings/booking-id/');```javascript

// Connect to booking updates

// Receive real-time status updatesconst ws = new WebSocket('ws://localhost:8000/ws/bookings/booking-id/');

ws.onmessage = function(event) {

    const data = JSON.parse(event.data);// Receive real-time status updates

    console.log('Booking update:', data.message);ws.onmessage = function(event) {

};    const data = JSON.parse(event.data);

```    console.log('Booking update:', data.message);

};

### User Notifications```

```javascript

// Connect to user notifications### User Notifications

const ws = new WebSocket('ws://localhost:8000/ws/notifications/user-id/');```javascript

```// Connect to user notifications

const ws = new WebSocket('ws://localhost:8000/ws/notifications/user-id/');

## 💳 Payment Integration```



### Stripe Configuration## 💳 Payment Integration

```python

# .env file### Stripe Configuration

STRIPE_PUBLISHABLE_KEY=pk_test_...```python

STRIPE_SECRET_KEY=sk_test_...# .env file

STRIPE_WEBHOOK_SECRET=whsec_...STRIPE_PUBLISHABLE_KEY=pk_test_...

```STRIPE_SECRET_KEY=sk_test_...

STRIPE_WEBHOOK_SECRET=whsec_...

### Payment Flow```

1. **Booking Completion** → Create Payment Intent

2. **Signature Verification** → Automatic Capture### Payment Flow

3. **Manual Override** → Admin Processing1. **Booking Completion** → Create Payment Intent

2. **Signature Verification** → Automatic Capture

## ✍️ Digital Signature System3. **Manual Override** → Admin Processing



### Smart Signature Vault## ✍️ Digital Signature System

- **SHA-256 Hashing** for tamper-proof signatures

- **48-hour expiry** for signature requests### Smart Signature Vault

- **Satisfaction ratings** (1-5 scale) required- **SHA-256 Hashing** for tamper-proof signatures

- **Automatic payment trigger** on signature- **48-hour expiry** for signature requests

- **Satisfaction ratings** (1-5 scale) required

### Hash Generation- **Automatic payment trigger** on signature

```python

signature_string = f"{booking_id}_{customer_id}_{signed_at}_{rating}"### Hash Generation

signature_hash = hashlib.sha256(signature_string.encode()).hexdigest()```python

```signature_string = f\"{booking_id}_{customer_id}_{signed_at}_{rating}\"

signature_hash = hashlib.sha256(signature_string.encode()).hexdigest()

## 📋 Admin Interface```



### Django Admin Dashboard## 📋 Admin Interface

- **URL**: `http://localhost:8000/admin/`

- **Credentials**: `admin` / `admin123`### Django Admin Dashboard

- **Features**:- **URL**: `http://localhost:8000/admin/`

  - Complete user management- **Credentials**: `admin` / `admin123`

  - Booking oversight- **Features**:

  - Payment processing  - Complete user management

  - Audit trail viewing  - Booking oversight

  - System analytics  - Payment processing

  - Audit trail viewing

## 🚀 Quick Start  - System analytics



### Backend Setup (Django)## 🚀 Quick Start



1. **Setup Environment**### 1. Setup Environment

```bash```bash

# Clone and navigate# Clone and navigate

cd Serverless-Squadcd Serverless-Squad



# Create virtual environment# Create virtual environment

python -m venv venvpython -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activatesource venv/bin/activate  # On Windows: venv\\Scripts\\activate



# Install dependencies# Install dependencies

pip install -r requirements.txtpip install -r requirements.txt

``````



2. **Database Setup**### 2. Database Setup

```bash```bash

# Run migrations# Run migrations

python manage.py migratepython manage.py migrate



# Create admin user# Create admin user

python manage.py shell -c "from core.models import User; User.objects.create_superuser('admin', 'admin@homeservepro.com', 'admin123', role='super_admin')"python manage.py shell -c \"from core.models import User; User.objects.create_superuser('admin', 'admin@homeservepro.com', 'admin123', role='super_admin')\"



# Create sample data# Create sample data

python create_sample_data.pypython create_sample_data.py

``````



3. **Start Backend Server**### 3. Start Server

```bash```bash

# Start Django server# Start Django server

python manage.py runserverpython manage.py runserver



# Server will be available at:# Server will be available at:

# 🌐 API: http://localhost:8000/# 🌐 API: http://localhost:8000/

# 📋 Admin: http://localhost:8000/admin/# 📋 Admin: http://localhost:8000/admin/

``````



### Frontend Setup (React)### 4. Test APIs

```bash

1. **Install Dependencies**# Run API tests

```bashpython test_api.py

# Navigate to project root```

npm install

```## 🧪 Sample Test Data



2. **Development Server**### Users Created

```bash| Username | Role | Password | Phone |

npm run dev|----------|------|----------|-------|

# Application will be available at http://localhost:5173| `admin` | Super Admin | `admin123` | - |

```| `customer1` | Customer | `password123` | +919876543210 |

| `vendor1` | Vendor | `password123` | +919876543212 |

3. **Build for Production**| `onboard_mgr` | Onboard Manager | `password123` | - |

```bash| `ops_mgr` | Ops Manager | `password123` | - |

npm run build

```### Services Available

- AC Repair (₹500)

## 🧪 Sample Test Data- Plumbing Service (₹400) 

- Electrical Work (₹600)

### Users Created- House Cleaning (₹300)

| Username | Role | Password | Phone |- Appliance Repair (₹450)

|----------|------|----------|-------|

| `admin` | Super Admin | `admin123` | - |## 🔒 Security Features

| `customer1` | Customer | `password123` | +919876543210 |

| `vendor1` | Vendor | `password123` | +919876543212 |### Role-Based Access Control (RBAC)

| `onboard_mgr` | Onboard Manager | `password123` | - |- **Field-level permissions** in serializers

| `ops_mgr` | Ops Manager | `password123` | - |- **Object-level permissions** for data access

- **Action-based permissions** for API endpoints

### Services Available

- AC Repair (₹500)### Audit Trail

- Plumbing Service (₹400)- **Immutable logging** of all actions

- Electrical Work (₹600)- **IP address tracking** and user agent logging

- House Cleaning (₹300)- **Edit-only policy** - no deletions allowed

- Appliance Repair (₹450)- **Complete change history** with old/new values



## 🔒 Security Features### Data Protection

- **JWT token authentication** with refresh mechanism

### Role-Based Access Control (RBAC)- **Password validation** and secure hashing

- **Field-level permissions** in serializers- **OTP verification** for sensitive roles

- **Object-level permissions** for data access- **SHA-256 signature hashing** for integrity

- **Action-based permissions** for API endpoints

## 📈 Performance & Scalability

### Audit Trail

- **Immutable logging** of all actions### Database Optimization

- **IP address tracking** and user agent logging- **Indexed fields** for fast queries

- **Edit-only policy** - no deletions allowed- **Role-based filtering** at database level

- **Complete change history** with old/new values- **Pagination** for large datasets

- **Optimized queries** with select_related/prefetch_related

### Data Protection

- **JWT token authentication** with refresh mechanism### Caching Strategy

- **Password validation** and secure hashing- **Redis caching** for OTP storage

- **OTP verification** for sensitive roles- **Query caching** for frequently accessed data

- **SHA-256 signature hashing** for integrity- **Session caching** for user data



## 📈 Performance & Scalability### Background Tasks

- **Celery integration** for async processing

### Database Optimization- **Signature expiry checks** via scheduled tasks

- **Indexed fields** for fast queries- **Email/SMS notifications** via background workers

- **Role-based filtering** at database level

- **Pagination** for large datasets## 🌐 Production Deployment

- **Optimized queries** with select_related/prefetch_related

### Environment Configuration

### Caching Strategy```bash

- **Redis caching** for OTP storage# Production settings

- **Query caching** for frequently accessed dataDEBUG=False

- **Session caching** for user dataALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DATABASE_URL=postgresql://user:pass@localhost/homeservepro

### Background TasksREDIS_URL=redis://localhost:6379/1

- **Celery integration** for async processing

- **Signature expiry checks** via scheduled tasks# External Services

- **Email/SMS notifications** via background workersTWILIO_ACCOUNT_SID=your_twilio_sid

STRIPE_SECRET_KEY=sk_live_...

## 🌐 Production Deployment```



### Environment Configuration### ASGI Server

```bash```bash

# Production settings# Install production server

DEBUG=Falsepip install gunicorn uvicorn

ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DATABASE_URL=postgresql://user:pass@localhost/homeservepro# Run with ASGI (for WebSockets)

REDIS_URL=redis://localhost:6379/1uvicorn homeserve_pro.asgi:application --host 0.0.0.0 --port 8000

```

# External Services

TWILIO_ACCOUNT_SID=your_twilio_sid### Docker Deployment

STRIPE_SECRET_KEY=sk_live_...```dockerfile

```# Dockerfile example

FROM python:3.11

### ASGI ServerWORKDIR /app

```bashCOPY requirements.txt .

# Install production serverRUN pip install -r requirements.txt

pip install gunicorn uvicornCOPY . .

EXPOSE 8000

# Run with ASGI (for WebSockets)CMD [\"uvicorn\", \"homeserve_pro.asgi:application\", \"--host\", \"0.0.0.0\"]

uvicorn homeserve_pro.asgi:application --host 0.0.0.0 --port 8000```

```

## 🔮 Future Enhancements

### Docker Deployment

```dockerfile### AI Integration Ready

# Dockerfile example- **Photo quality comparison** (TensorFlow.js hooks)

FROM python:3.11- **Demand forecasting** (ML model endpoints)

WORKDIR /app- **Smart scheduling** (Google Maps + AI)

COPY requirements.txt .- **Chatbot integration** (NLP ready)

RUN pip install -r requirements.txt

COPY . .### Pincode Intelligence

EXPOSE 8000- **Dynamic pricing** based on demand

CMD ["uvicorn", "homeserve_pro.asgi:application", "--host", "0.0.0.0"]- **Vendor distribution** optimization

```- **Service availability** prediction



## 🔮 Future Enhancements### Advanced Features

- **Real-time chat** between customers and vendors

### AI Integration Ready- **Video call integration** for consultations

- **Photo quality comparison** (TensorFlow.js hooks)- **IoT device integration** for smart home services

- **Demand forecasting** (ML model endpoints)- **Blockchain integration** for enhanced signature security

- **Smart scheduling** (Google Maps + AI)

- **Chatbot integration** (NLP ready)## 📞 Support & Contribution



### Pincode Intelligence### API Documentation

- **Dynamic pricing** based on demand- **Swagger/OpenAPI** integration ready

- **Vendor distribution** optimization- **Postman collection** available

- **Service availability** prediction- **Interactive API explorer** at `/api/docs/`



### Advanced Features### Development

- **Real-time chat** between customers and vendors```bash

- **Video call integration** for consultations# Install dev dependencies

- **IoT device integration** for smart home servicespip install django-extensions ipython

- **Blockchain integration** for enhanced signature security

# Use Django shell with IPython

## 📞 Support & Contributionpython manage.py shell_plus



### API Documentation# Run specific tests

- **Swagger/OpenAPI** integration readypython manage.py test core.tests

- **Postman collection** available```

- **Interactive API explorer** at `/api/docs/`

## 📊 System Statistics

### Development

```bash**✅ Backend Implementation Complete**

# Install dev dependencies

pip install django-extensions ipython- **7 Models** with full relationships

- **20+ API Endpoints** with role-based access

# Use Django shell with IPython- **5 User Roles** with granular permissions

python manage.py shell_plus- **WebSocket Support** for real-time updates

- **Stripe Integration** for payments

# Run specific tests- **Digital Signatures** with SHA-256 hashing

python manage.py test core.tests- **Complete Audit Trail** for all actions

```- **OTP Verification** for vendors

- **Django Admin** interface configured

## 📊 System Statistics- **Sample Data** and API testing included



**✅ Full-Stack Implementation Complete**---



- **7 Models** with full relationships🎉 **HomeServe Pro backend is production-ready with enterprise-grade features, security, and scalability!**

- **20+ API Endpoints** with role-based access=======

- **5 User Roles** with granular permissions# HouseServe Hub

- **WebSocket Support** for real-time updates

- **Stripe Integration** for paymentsA comprehensive multi-role service booking platform connecting customers with verified vendors.

- **Digital Signatures** with SHA-256 hashing

- **Complete Audit Trail** for all actions## Table of Contents

- **OTP Verification** for vendors

- **Django Admin** interface configured- [Overview](#overview)

- **React Frontend** with modern UI- [Features](#features)

- **Sample Data** and API testing included- [User Roles](#user-roles)

- [Technologies Used](#technologies-used)

---- [Getting Started](#getting-started)

  - [Prerequisites](#prerequisites)

🎉 **HomeServe Pro is production-ready with enterprise-grade features, security, and scalability!**  - [Installation](#installation)
  - [Development](#development)
- [Project Structure](#project-structure)
- [Available Scripts](#available-scripts)
- [Deployment](#deployment)

## Overview

HouseServe Hub is a full-featured service booking platform designed to connect customers with verified service providers. The platform supports multiple user roles, each with specific functionalities tailored to their needs.

## Features

- Multi-role authentication and authorization
- Service booking and management
- Real-time chat functionality
- Digital signature capabilities
- Analytics and reporting
- Responsive design for all devices
- Role-based dashboards
- User profile management

## User Roles

The platform supports 5 distinct user roles:

1. **Customer**
   - Book services
   - Manage bookings
   - Communicate with vendors
   - View booking history
   - Digital signature for completed services

2. **Vendor**
   - View assigned jobs
   - Manage calendar
   - Track earnings
   - Communicate with customers
   - Update job status

3. **Onboard**
   - Vendor verification and approval
   - Manage vendor queue
   - Review vendor applications

4. **Ops (Operations)**
   - Monitor all bookings
   - Manage manual payments
   - Access signature vault
   - View analytics

5. **Admin**
   - User management
   - Role management
   - Audit logs
   - Ethics monitoring
   - System settings

## Technologies Used

This project is built with modern web technologies:

- **Frontend Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **State Management**: React Query
- **UI Components**: shadcn/ui with Radix UI primitives
- **Styling**: Tailwind CSS
- **Form Handling**: React Hook Form with Zod validation
- **Icons**: Lucide React
- **Charts**: Recharts
- **Date Handling**: date-fns
- **Notifications**: Sonner

## Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn package manager

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```bash
   cd houseserve-hub
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

### Development

To start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173` (or the port shown in your terminal).

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui components
│   └── ...             # Custom components
├── context/            # React context providers
├── hooks/              # Custom React hooks
├── lib/                # Utility functions
├── pages/              # Page components organized by role
│   ├── admin/          # Admin role pages
│   ├── auth/           # Authentication pages
│   ├── customer/       # Customer role pages
│   ├── onboard/        # Onboard role pages
│   ├── ops/            # Operations role pages
│   └── vendor/         # Vendor role pages
├── services/           # API service files
└── App.tsx             # Main application component
```

## Available Scripts

- `npm run dev` - Starts the development server
- `npm run build` - Builds the production-ready application
- `npm run build:dev` - Builds the development version
- `npm run lint` - Runs ESLint to check for code issues
- `npm run preview` - Previews the built application locally

## Deployment

To deploy the application:

1. Build the production version:
   ```bash
   npm run build
   ```

2. The built files will be in the `dist/` directory, which can be deployed to any static hosting service.

## Authentication

The application uses a mock authentication system for demonstration purposes. In a production environment, this would be connected to a backend API.

Demo credentials:
- Customer: customer@serviceplatform.com / demo123
- Vendor: vendor@serviceplatform.com / demo123
- Onboard: onboard@serviceplatform.com / demo123
- Ops: ops@serviceplatform.com / demo123
- Admin: admin@serviceplatform.com / demo123
>>>>>>> 72c2c7641e3417847b173b68ed79df93f70ac2cf
