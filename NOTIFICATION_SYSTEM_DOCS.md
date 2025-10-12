# Automated Messaging & Business Alerts System

## Overview

This system implements comprehensive automated messaging and business alerts for HomeServe Pro, including:

1. **Pincode-Based Messaging**: Location-based notifications and promotions
2. **Automated Business Alerts**: System monitoring and critical alerts
3. **Real-time Notifications**: Email, SMS, and WebSocket support

## Features Implemented

### 3a. Pincode-Based Messaging

#### High Demand Notifications
- **Trigger**: When pincode has >5 bookings or >3 bookings per vendor
- **Recipients**: Available vendors in the area
- **Content**: Demand statistics, earnings potential
- **Schedule**: Daily at 9:00 AM

#### Vendor Bonus Alerts
- **Trigger**: Very high demand areas (>8 bookings, <3 vendors)
- **Recipients**: All vendors in the area
- **Content**: 15% bonus offer details
- **Schedule**: Daily at 10:00 AM

#### Location-Based Promotions
- **Trigger**: Low activity areas (<3 bookings)
- **Recipients**: Customers in the area
- **Content**: 25% weekend discount offers
- **Schedule**: Mon, Wed, Fri at 11:00 AM

### 3b. Automated Business Alerts

#### Pending Signature Alerts
- **Trigger**: Signatures pending >24 hours
- **Recipients**: Ops Managers, Super Admins
- **Severity**: High (48+ hours = Critical)
- **Schedule**: Every hour

#### Payment Hold Alerts
- **Trigger**: Payments on hold >24 hours
- **Recipients**: Ops Managers, Finance team
- **Content**: Total amount, affected payments
- **Schedule**: Every 2 hours

#### Booking Timeout Alerts
- **Trigger**: Bookings overdue >24 hours
- **Recipients**: Ops Managers
- **Severity**: Critical (48+ hours)
- **Schedule**: Every 3 hours

#### Vendor Completion Reminders
- **Trigger**: Services due soon or overdue
- **Recipients**: Individual vendors
- **Content**: Service details, urgency
- **Schedule**: 8 AM, 2 PM, 6 PM

## Database Models

### NotificationLog
Tracks all sent notifications with delivery status:
```python
- recipient: User receiving notification
- notification_type: otp, signature_request, pincode_alert, etc.
- method: email, sms, websocket
- status: sent, delivered, failed, pending
- subject, message: Content
- metadata: Additional context data
```

### PincodeAnalytics
Daily analytics for location-based insights:
```python
- pincode, date: Location and time
- booking metrics: total, pending, completed, cancelled
- vendor metrics: available, active
- performance metrics: response time, completion time, satisfaction
- revenue metrics: total, average booking value
- alert flags: track what alerts were sent
```

### BusinessAlert
System alerts requiring attention:
```python
- alert_type: booking_timeout, pending_signature, payment_hold
- severity: low, medium, high, critical
- status: active, acknowledged, resolved, ignored
- assigned_to, resolved_by: User assignments
- metadata: Related data and context
```

## API Endpoints

### Admin Dashboard Endpoints

#### Notification Management
```http
GET /admin-dashboard/notifications/
POST /admin-dashboard/notifications/
```
- View notification statistics
- Manually trigger tasks

#### Notification Logs
```http
GET /admin-dashboard/notifications/logs/
?page=1&per_page=20&type=demand_notification&status=sent
```
- Filter and paginate notification history

#### Business Alerts
```http
GET /admin-dashboard/notifications/alerts/
?status=active&severity=critical
```
- View and manage business alerts

#### Pincode Analytics
```http
GET /admin-dashboard/analytics/pincode/
?pincode=560001&date_from=2024-01-01&date_to=2024-01-07
```
- View location-based analytics data

## Celery Tasks

### Analytics Generation
```python
@shared_task
def generate_pincode_analytics()
```
- Runs daily at 1:00 AM
- Calculates metrics for all active pincodes
- Stores data for decision making

### Messaging Tasks
```python
@shared_task
def send_pincode_demand_alerts()
def send_vendor_bonus_alerts()
def send_promotional_campaigns()
```
- Location-based messaging automation
- Triggered by analytics thresholds

### Monitoring Tasks
```python
@shared_task
def check_pending_signatures()
def check_payment_holds()
def check_booking_timeouts()
def send_vendor_completion_reminders()
```
- Continuous system monitoring
- Escalating alert severities

## Setup Instructions

### 1. Install Dependencies
```bash
pip install django-celery-beat django-timezone-field python-crontab
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Set Up Periodic Tasks
```bash
python manage.py setup_periodic_tasks
```

### 4. Start Celery Services
```bash
# Terminal 1: Start Redis (if not running)
redis-server

# Terminal 2: Start Celery Worker
celery -A homeserve_pro worker --loglevel=info

# Terminal 3: Start Celery Beat (Scheduler)
celery -A homeserve_pro beat --loglevel=info
```

### 5. Configure Email/SMS
Set environment variables:
```bash
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
```

## Usage Examples

### Manual Task Triggers
```python
# In Django shell or admin API
from core.tasks import generate_pincode_analytics
task = generate_pincode_analytics.delay()
print(f"Task ID: {task.id}")
```

### Custom Notifications
```python
from core.notification_service import NotificationService

# Send custom promotion
promotion_data = {
    'subject': 'Special Weekend Offer!',
    'title': 'Flash Sale',
    'offer_text': '30% OFF',
    'expiry_date': '2024-12-31'
}
NotificationService.location_based_promotions('560001', promotion_data)
```

### Business Alerts
```python
# Create custom business alert
from core.models import BusinessAlert
alert = BusinessAlert.objects.create(
    alert_type='system_error',
    severity='critical',
    title='Database Connection Issue',
    description='Unable to connect to payment gateway'
)
```

## Monitoring & Maintenance

### Task Monitoring
- Django Admin → Periodic Tasks → View scheduled tasks
- Django Admin → Task Results → View execution history
- Logs: Check `homeserve_pro.log` for detailed task logs

### Notification Analytics
- Admin Dashboard → Notifications → View success rates
- Filter logs by type, method, status
- Track engagement and delivery rates

### Alert Management
- Admin Dashboard → Alerts → Manage active alerts
- Assign alerts to team members
- Track resolution times

### Performance Optimization
- Regular cleanup: Old notifications auto-deleted after 90 days
- Cache analytics: Pincode data cached for performance
- Queue management: Different queues for different task types

## Troubleshooting

### Common Issues

1. **Tasks not executing**
   - Check Redis connection
   - Verify Celery worker is running
   - Check task registration in settings

2. **Notifications not sending**
   - Verify email/SMS credentials
   - Check notification logs for errors
   - Test with DEBUG=True for detailed logs

3. **Missing analytics data**
   - Run manual analytics generation
   - Check for data in Booking/User models
   - Verify pincode data consistency

### Debug Commands
```bash
# Test notification system
python manage.py shell
>>> from core.tasks import test_notification_system
>>> test_notification_system.delay()

# Check periodic tasks
python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> print(PeriodicTask.objects.filter(enabled=True).count())

# Manual analytics generation
python manage.py shell
>>> from core.tasks import generate_pincode_analytics
>>> result = generate_pincode_analytics.delay()
>>> print(result.get())
```

## Security Considerations

- All admin endpoints require authentication
- Role-based access control (super_admin, ops_manager)
- Sensitive data masked in logs
- Rate limiting on notification sending
- Audit trails for all actions

## Scalability Notes

- Task queues can be distributed across multiple workers
- Analytics data can be archived for long-term storage
- Notification templates can be customized per region
- Alert thresholds can be configured per pincode
- Integration ready for push notifications and in-app messaging

## Future Enhancements

1. **Machine Learning Integration**
   - Predictive demand forecasting
   - Optimal pricing suggestions
   - Customer preference learning

2. **Advanced Segmentation**
   - Customer behavior analysis
   - Vendor performance scoring
   - Dynamic bonus calculations

3. **Real-time Dashboard**
   - Live notification metrics
   - Interactive pincode maps
   - Alert response tracking

4. **Mobile App Integration**
   - Push notifications
   - In-app messaging
   - Location-based offers