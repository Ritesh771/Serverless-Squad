# HomeServe Pro (HouseServe Hub)

HomeServe Pro is a multi-role service booking platform that connects customers with verified vendors. This repository contains a Django backend (REST API, WebSocket support via Django Channels, Celery background tasks) and a React + TypeScript frontend (Vite). The system implements role-based access control, digital signatures, Stripe payments, OTP verification, and audit logging.

This document provides a concise, professional guide for developers and operators: project overview, architecture, local development, configuration, testing, deployment notes, and contribution guidelines.

## Table of Contents

- Overview
- Features
- Architecture and technologies
- Getting started
  - Prerequisites
  - Backend (Django) setup
  - Frontend (React) setup
- Configuration
- Running tests
- Deployment notes
- Project structure
- Contributing
- License
- Contact

## Overview

HomeServe Pro is designed for organisations that need a secure, auditable, and scalable platform to manage on-demand home services. It supports multiple user roles (Customer, Vendor, Onboard Manager, Ops Manager, Super Admin) and includes features for bookings, digital signatures, payments, notifications, and analytics.

## Features

- Role-based access control with JWT authentication and optional OTP verification for vendor onboarding
- REST API built with Django REST Framework
- Real-time updates using Django Channels (WebSockets)
- Background processing with Celery
- Stripe integration for payments
- Digital signature flow using SHA-256 hashing for integrity
- Audit logging for important system actions
- React + TypeScript frontend (Vite) with modern UI patterns

## Architecture and technologies

- Backend: Python, Django, Django REST Framework, Django Channels, Celery
- Database: SQLite for development (configurable to PostgreSQL/MySQL for production)
- Caching/Queue: Redis (used for Celery broker and OTP caching)
- Frontend: React 18, TypeScript, Vite, Tailwind CSS
- Authentication: JWT (access + refresh), OTP via Twilio (optional)
- Payments: Stripe

## Getting started

The following steps describe local development setup on macOS or Linux. Adapt venv commands for Windows as needed.

### Prerequisites

- Python 3.10+
- Node.js 16+ and npm or yarn
- Redis (for Celery and OTP caching)
- A Stripe account for payment testing (test keys)

### Backend (Django) setup

1. Create and activate a Python virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

2. Install Python dependencies

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and set required environment variables. Example minimal values:

```
SECRET_KEY=your-django-secret
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
REDIS_URL=redis://localhost:6379/1
```

4. Apply database migrations and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. (Optional) Populate sample data

```bash
python datacreate/create_sample_data.py
```

6. Start the Django development server

```bash
python manage.py runserver
```

API: http://localhost:8000/
Admin: http://localhost:8000/admin/

For ASGI (WebSocket) development behavior, run with uvicorn:

```bash
uvicorn homeserve_pro.asgi:application --host 0.0.0.0 --port 8000
```

Start a Celery worker in a separate terminal when background tasks are required:

```bash
celery -A homeserve_pro worker -l info
```

### Frontend (React + Vite) setup

1. Change to the `src` directory (frontend)

```bash
cd src
```

2. Install dependencies and start the development server

```bash
npm install
npm run dev
```

The frontend typically runs at http://localhost:5173/.

## Configuration

- Manage secrets and environment variables via a `.env` file for local development and a secrets manager for production.
- For production use PostgreSQL and set `DATABASE_URL` accordingly.
- Configure `STRIPE_WEBHOOK_SECRET` and your webhook endpoint when using Stripe webhooks.
- Configure Twilio credentials if SMS/OTP flows are required.

## Running tests

Run Django unit tests with:

```bash
python manage.py test
```

The repository includes additional integration and system-level scripts under the `test/` directory. Use them as needed for higher-level verification.

## Deployment notes

- Use a production ASGI server (uvicorn or daphne) behind a reverse proxy (nginx) to support WebSockets.
- Use a process manager (systemd, supervisord) to run the Django application, Celery workers, and other services.
- Enable TLS and set appropriate `ALLOWED_HOSTS` in production settings.
- For scaling: database (Postgres), caching (Redis), and a managed message broker are recommended.
- Consider containerising the application with Docker for reproducible deployments.

## Project structure (high level)

- `homeserve_pro/` — Django project configuration, ASGI/WGI entrypoints
- `core/` — Core Django app containing models, views, serializers, services
- `datacreate/` — Data population and utility scripts
- `src/` — Frontend React + TypeScript application (Vite)
- `test/` — Test and integration scripts
- `requirements.txt` — Python dependencies
- `package.json` — Frontend tooling and scripts

## Team

This project was developed by Serverless Squad.

- **Developer and Team Lead**: Ritesh N - [Portfolio](https://riteshn.me/)
- **Developer**: Pannaga J A - [Portfolio](https://pannagaja.vercel.app/)
- **Team Members**: Ruthu Parinika V N, Shashank G S
- **Email**: riturithesh66@gmail.com
- **GitHub Repository**: [https://github.com/Ritesh771/Serverless-Squad](https://github.com/Ritesh771/Serverless-Squad)

## Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repository and create a descriptive feature branch.
2. Write tests for new behavior and ensure existing tests pass.
3. Open a pull request with a clear description of the change and rationale.

Please follow the repository's code style and add or update tests for new features or fixes.

## License

This repository does not include a license file. Add a `LICENSE` file to make the licensing terms explicit.

## Contact

For questions about development or deployment, please open an issue in this repository or contact the maintainers via the repository issue tracker.
