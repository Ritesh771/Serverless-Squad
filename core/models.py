from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from datetime import timedelta
import hashlib
import uuid


class User(AbstractUser):
    """Custom User model with role-based access"""
    
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('onboard_manager', 'Onboard Manager'),
        ('ops_manager', 'Ops Manager'),
        ('super_admin', 'Super Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    is_available = models.BooleanField(default=False)  # For vendors
    otp_secret = models.CharField(max_length=32, blank=True)  # For OTP verification
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Service(models.Model):
    """Available services that can be booked"""
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=50)
    duration_minutes = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Booking(models.Model):
    """Service booking record"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('signed', 'Signed & Verified'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_bookings')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_bookings', null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    pincode = models.CharField(max_length=10)
    
    scheduled_date = models.DateTimeField()
    completion_date = models.DateTimeField(null=True, blank=True)
    
    # Smart buffering fields
    estimated_service_duration_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Predicted service duration")
    travel_time_to_location_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Travel time to customer location")
    travel_time_from_location_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Travel time from customer location")
    buffer_before_minutes = models.PositiveIntegerField(default=15, help_text="Buffer time before service")
    buffer_after_minutes = models.PositiveIntegerField(default=15, help_text="Buffer time after service")
    
    # Calculated times for scheduling
    actual_start_time = models.DateTimeField(null=True, blank=True, help_text="When vendor should start traveling")
    actual_end_time = models.DateTimeField(null=True, blank=True, help_text="When vendor is free for next booking")
    
    customer_notes = models.TextField(blank=True)
    vendor_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Booking {self.id} - {self.service.name}"
    
    def calculate_total_duration_minutes(self):
        """Calculate total time slot needed including travel and buffers"""
        duration = self.estimated_service_duration_minutes or self.service.duration_minutes
        travel_to = self.travel_time_to_location_minutes or 0
        travel_from = self.travel_time_from_location_minutes or 0
        buffer_before = self.buffer_before_minutes or 0
        buffer_after = self.buffer_after_minutes or 0
        
        return travel_to + buffer_before + duration + buffer_after + travel_from
    
    def update_calculated_times(self):
        """Update actual start and end times based on travel and service duration"""
        if self.scheduled_date:
            # Actual start time = scheduled time - travel time - buffer before
            travel_time = self.travel_time_to_location_minutes or 0
            buffer_before = self.buffer_before_minutes or 0
            start_offset = timedelta(minutes=travel_time + buffer_before)
            self.actual_start_time = self.scheduled_date - start_offset
            
            # Actual end time = scheduled time + service duration + buffer after + travel from
            service_duration = self.estimated_service_duration_minutes or self.service.duration_minutes
            buffer_after = self.buffer_after_minutes or 0
            travel_from = self.travel_time_from_location_minutes or 0
            end_offset = timedelta(minutes=service_duration + buffer_after + travel_from)
            self.actual_end_time = self.scheduled_date + end_offset
    
    def save(self, *args, **kwargs):
        self.update_calculated_times()
        super().save(*args, **kwargs)


class Photo(models.Model):
    """Before/after images for bookings"""
    
    IMAGE_TYPE_CHOICES = [
        ('before', 'Before'),
        ('after', 'After'),
        ('additional', 'Additional'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/%Y/%m/%d/')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_image_type_display()} photo for {self.booking.id}"


class Signature(models.Model):
    """Digital satisfaction signature"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('signed', 'Signed'),
        ('expired', 'Expired'),
        ('disputed', 'Disputed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='signature')
    signed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    signature_hash = models.CharField(max_length=64, blank=True)  # SHA-256 hash
    signature_data = models.JSONField(null=True, blank=True)  # Store signature details
    
    satisfaction_rating = models.PositiveIntegerField(null=True, blank=True)  # 1-5 rating
    satisfaction_comments = models.TextField(blank=True)
    
    requested_at = models.DateTimeField(auto_now_add=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()  # 48 hours from request
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=48)
        
        if self.status == 'signed' and self.signature_data and not self.signature_hash:
            # Generate SHA-256 hash for tamper-proofing
            signature_string = f"{self.booking.id}_{self.signed_by.id}_{self.signed_at}_{self.satisfaction_rating}"
            self.signature_hash = hashlib.sha256(signature_string.encode()).hexdigest()
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Signature for booking {self.booking.id} - {self.get_status_display()}"


class Payment(models.Model):
    """Stripe payment information"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('on_hold', 'On Hold'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='automatic')
    
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    stripe_charge_id = models.CharField(max_length=200, blank=True)
    
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.id} - ₹{self.amount} ({self.get_status_display()})"


class NotificationLog(models.Model):
    """Track all notifications sent"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('otp', 'OTP Verification'),
        ('signature_request', 'Signature Request'),
        ('pincode_alert', 'Pincode Alert'),
        ('demand_notification', 'Demand Notification'),
        ('bonus_alert', 'Bonus Alert'),
        ('business_alert', 'Business Alert'),
        ('payment_hold', 'Payment Hold Alert'),
        ('booking_timeout', 'Booking Timeout'),
        ('pending_signature', 'Pending Signature Alert'),
        ('promotional', 'Promotional'),
    ]
    
    METHOD_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('websocket', 'WebSocket'),
        ('push', 'Push Notification'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_received')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    subject = models.CharField(max_length=200)
    message = models.TextField()
    metadata = models.JSONField(null=True, blank=True)  # Store additional data like pincode, booking_id, etc.
    
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['recipient', 'notification_type']),
            models.Index(fields=['method', 'status']),
            models.Index(fields=['sent_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} to {self.recipient.username} via {self.method}"


class PincodeAnalytics(models.Model):
    """Analytics data for pincode-based insights"""
    
    pincode = models.CharField(max_length=10, db_index=True)
    date = models.DateField(db_index=True)
    
    # Booking metrics
    total_bookings = models.PositiveIntegerField(default=0)
    pending_bookings = models.PositiveIntegerField(default=0)
    completed_bookings = models.PositiveIntegerField(default=0)
    cancelled_bookings = models.PositiveIntegerField(default=0)
    
    # Vendor metrics
    available_vendors = models.PositiveIntegerField(default=0)
    active_vendors = models.PositiveIntegerField(default=0)  # Vendors who took bookings
    
    # Performance metrics
    avg_response_time_minutes = models.FloatField(null=True, blank=True)
    avg_completion_time_hours = models.FloatField(null=True, blank=True)
    customer_satisfaction_avg = models.FloatField(null=True, blank=True)
    
    # Revenue metrics
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_booking_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Flags for automated alerts
    high_demand_alert_sent = models.BooleanField(default=False)
    low_vendor_alert_sent = models.BooleanField(default=False)
    promotional_alert_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['pincode', 'date']
        ordering = ['-date', 'pincode']
        indexes = [
            models.Index(fields=['pincode', 'date']),
            models.Index(fields=['total_bookings']),
            models.Index(fields=['available_vendors']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.pincode} on {self.date}"
    
    @property
    def demand_ratio(self):
        """Calculate demand to vendor ratio"""
        if self.available_vendors == 0:
            return float('inf')
        return self.total_bookings / self.available_vendors
    
    @property
    def is_high_demand(self):
        """Check if this pincode has high demand"""
        return self.demand_ratio > 3  # More than 3 bookings per vendor
    
    @property
    def is_low_vendor_count(self):
        """Check if this pincode has low vendor availability"""
        return self.available_vendors < 2  # Less than 2 vendors available


class BusinessAlert(models.Model):
    """Track business alerts and their resolution"""
    
    ALERT_TYPE_CHOICES = [
        ('booking_timeout', 'Booking Timeout'),
        ('pending_signature', 'Pending Signature'),
        ('payment_hold', 'Payment Hold'),
        ('low_vendor_count', 'Low Vendor Count'),
        ('high_demand', 'High Demand'),
        ('service_completion_reminder', 'Service Completion Reminder'),
        ('system_error', 'System Error'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('ignored', 'Ignored'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    metadata = models.JSONField(null=True, blank=True)  # Store related IDs, pincodes, etc.
    
    # Related objects (optional)
    related_booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    related_signature = models.ForeignKey(Signature, on_delete=models.CASCADE, null=True, blank=True)
    related_payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    
    # Resolution tracking
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_alerts')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_type', 'status']),
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['assigned_to']),
        ]
    
    def __str__(self):
        return f"{self.alert_type} - {self.title} ({self.severity})"


class VendorAvailability(models.Model):
    """Track vendor working hours and availability patterns"""
    
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Location preferences
    primary_pincode = models.CharField(max_length=10, help_text="Vendor's primary location")
    service_radius_km = models.PositiveIntegerField(default=25, help_text="Maximum travel distance in km")
    
    # Buffer preferences
    preferred_buffer_minutes = models.PositiveIntegerField(default=30, help_text="Preferred gap between bookings")
    max_travel_time_minutes = models.PositiveIntegerField(default=60, help_text="Maximum acceptable travel time")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['vendor', 'day_of_week', 'start_time']
        ordering = ['vendor', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.vendor.username} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class TravelTimeCache(models.Model):
    """Cache travel time calculations between pincodes"""
    
    from_pincode = models.CharField(max_length=10, db_index=True)
    to_pincode = models.CharField(max_length=10, db_index=True)
    
    # Travel time data
    distance_km = models.FloatField(help_text="Distance in kilometers")
    duration_minutes = models.PositiveIntegerField(help_text="Travel time in minutes")
    duration_in_traffic_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Travel time with traffic")
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    google_maps_api_used = models.BooleanField(default=True)
    confidence_score = models.FloatField(default=1.0, help_text="Accuracy confidence 0-1")
    
    # Cache expiry - data older than 24 hours should be refreshed
    is_expired = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['from_pincode', 'to_pincode']
        ordering = ['-calculated_at']
        indexes = [
            models.Index(fields=['from_pincode', 'to_pincode']),
            models.Index(fields=['calculated_at']),
        ]
    
    def __str__(self):
        return f"{self.from_pincode} → {self.to_pincode}: {self.duration_minutes}min ({self.distance_km}km)"
    
    def save(self, *args, **kwargs):
        # Mark as expired if older than 24 hours
        if self.calculated_at and (timezone.now() - self.calculated_at).days >= 1:
            self.is_expired = True
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    """Audit trail for all system actions"""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('signature_request', 'Signature Request'),
        ('signature_sign', 'Signature Sign'),
        ('payment_process', 'Payment Process'),
        ('status_change', 'Status Change'),
        ('cache_clear', 'Cache Clear'),
        ('notification_sent', 'Notification Sent'),
        ('alert_created', 'Alert Created'),
        ('alert_resolved', 'Alert Resolved'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50)  # Model name
    resource_id = models.CharField(max_length=100)  # Object ID
    
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} {self.resource_type} at {self.timestamp}"
