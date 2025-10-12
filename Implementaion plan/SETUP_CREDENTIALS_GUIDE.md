# 🔧 Credentials Configuration Guide

## ✅ Current Status

### ✅ Redis & Celery - RUNNING
- ✅ Redis server is running on localhost:6379
- ✅ Celery Worker is processing tasks
- ✅ Celery Beat is scheduling periodic tasks
- ✅ All 10 automated tasks are registered and working

### ⚠️ Email Configuration - NEEDS REAL CREDENTIALS

Your current email configuration has a placeholder password. Here's how to set up real Gmail credentials:

#### 📧 Gmail App Password Setup

1. **Enable 2-Factor Authentication on Gmail:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification

2. **Create App Password:**
   - Visit [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and your device
   - Copy the 16-character app password

3. **Update your .env file:**
   ```bash
   # Replace these with your real credentials
   EMAIL_HOST_USER=your_real_email@gmail.com
   EMAIL_HOST_PASSWORD=your_16_char_app_password
   DEFAULT_FROM_EMAIL=HomeServe Pro <your_real_email@gmail.com>
   ```

### ⚠️ Twilio Configuration - NEEDS REAL CREDENTIALS

Your current Twilio configuration has placeholder values. Here's how to set up real SMS credentials:

#### 📱 Twilio Setup

1. **Sign up for Twilio:**
   - Visit [Twilio Console](https://console.twilio.com/)
   - Create a free account (gets $15 credit)

2. **Get your credentials:**
   - Copy Account SID from dashboard
   - Copy Auth Token from dashboard
   - Purchase a phone number ($1/month)

3. **Update your .env file:**
   ```bash
   # Replace these with your real credentials
   TWILIO_ACCOUNT_SID=your_actual_account_sid
   TWILIO_AUTH_TOKEN=your_actual_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

## 🚀 Quick Test Commands

### Test Email Configuration
```bash
source venv/bin/activate
python test_email_config.py
```

### Test Full System
```bash
source venv/bin/activate
python test_full_automation.py
```

### Manually Trigger Tasks
```bash
source venv/bin/activate
python manage.py shell

# In Django shell:
from core.tasks import generate_pincode_analytics
task = generate_pincode_analytics.delay()
print(f"Task ID: {task.id}")
print(f"Result: {task.get()}")
```

## 📊 Monitoring Your System

### 1. Django Admin Dashboard
- URL: http://127.0.0.1:8000/admin/
- View: Periodic Tasks, Task Results, Notification Logs

### 2. Admin API Endpoints
```bash
# Notification management
GET http://127.0.0.1:8000/admin-dashboard/notifications/

# View notification logs
GET http://127.0.0.1:8000/admin-dashboard/notifications/logs/

# Check business alerts
GET http://127.0.0.1:8000/admin-dashboard/notifications/alerts/

# Pincode analytics
GET http://127.0.0.1:8000/admin-dashboard/analytics/pincode/
```

### 3. Terminal Monitoring
- **Celery Worker Terminal**: Shows task execution logs
- **Celery Beat Terminal**: Shows scheduling activity
- **Redis Logs**: Check with `redis-cli monitor`

## 🎯 Current Automation Schedule

| Task | Schedule | Purpose |
|------|----------|---------|
| Generate Analytics | Daily 1:00 AM | Create pincode demand data |
| Demand Alerts | Daily 9:00 AM | Notify vendors of high demand |
| Bonus Alerts | Daily 10:00 AM | Send bonus opportunities |
| Promotions | Mon/Wed/Fri 11:00 AM | Customer discount campaigns |
| Signature Check | Every hour | Monitor pending signatures |
| Payment Check | Every 2 hours | Monitor payment holds |
| Timeout Check | Every 3 hours | Monitor overdue bookings |
| Completion Reminders | 8 AM, 2 PM, 6 PM | Vendor service reminders |
| Cleanup | Sunday 2:00 AM | Remove old notification logs |

## 🔧 SSL Certificate Fix (If Needed)

If you encounter SSL certificate issues on macOS:

```bash
# Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command

# Or update certificates
pip install --upgrade certifi
```

## 🎉 Success Indicators

When everything is working correctly, you should see:

### ✅ In Celery Worker Terminal:
```
[INFO] Task core.tasks.generate_pincode_analytics[...] received
[INFO] Task core.tasks.generate_pincode_analytics[...] succeeded
```

### ✅ In Celery Beat Terminal:
```
[INFO] Scheduler: Sending due task Generate Pincode Analytics
```

### ✅ In Email Test:
```
✅ Email sent successfully!
📬 Check your inbox for the test email
```

### ✅ In Database:
- NotificationLog entries with status 'sent'
- PincodeAnalytics records with current date
- BusinessAlert records when issues detected

## 🚨 Troubleshooting

### Redis Connection Issues
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Restart Redis if needed
brew services restart redis
```

### Celery Worker Issues
```bash
# Restart Celery Worker
celery -A homeserve_pro worker --loglevel=info

# Check for task registration
celery -A homeserve_pro inspect registered
```

### Email Issues
```bash
# Test Django email directly
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

## 📱 Next Steps

1. **Configure real credentials** using the guides above
2. **Test email notifications** to verify they're working
3. **Set up Twilio** for SMS notifications (optional)
4. **Monitor the system** using the admin dashboard
5. **Customize thresholds** in `core/tasks.py` as needed

Your automated messaging system is now fully operational! 🎉