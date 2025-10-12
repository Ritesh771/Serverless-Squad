# HouseServe Hub

A comprehensive multi-role service booking platform connecting customers with verified vendors.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [User Roles](#user-roles)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
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