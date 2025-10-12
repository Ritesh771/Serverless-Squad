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
    
    def _str_(self):
        return f"{self.username} ({self.get_role_display()})"


class Address(models.Model):
    """Customer saved addresses"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, help_text="e.g., Home, Office, etc.")
    address_line = models.TextField()
    pincode = models.CharField(max_length=10)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def _str_(self):
        return f"{self.label}: {self.address_line[:30]}..."
    
    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)


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
    
    def _str_(self):
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
    
    STATUS_FLOW = {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['in_progress', 'cancelled'],
        'in_progress': ['completed'],
        'completed': ['signed', 'disputed'],
        'signed': [],
        'cancelled': [],
        'disputed': []
    }
    
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
    
    def _str_(self):
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
    
    def can_transition_to(self, new_status):
        """Check if booking can transition to new status"""
        return new_status in self.STATUS_FLOW.get(self.status, [])
    
    def save(self, *args, **kwargs):
        # Track status changes
        if self.pk is not None:
            # This is an update, check if status changed
            old_booking = Booking.objects.filter(pk=self.pk).first()
            previous_status = old_booking.status if old_booking else None
        else:
            # This is a new booking
            previous_status = None
        
        # Update calculated times
        self.update_calculated_times()
        
        # Save the booking
        super().save(*args, **kwargs)
        
        # Send status update notification if status changed
        if previous_status != self.status:
            # Import here to avoid circular imports
            try:
                from .status_service import BookingStatusService
                BookingStatusService.send_status_update(self, previous_status)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send status update: {str(e)}")


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
    
    def _str_(self):
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
            signature_string = f"{self.booking.id}{self.signed_by.id}{self.signed_at}_{self.satisfaction_rating}"
            self.signature_hash = hashlib.sha256(signature_string.encode()).hexdigest()
            
        super().save(*args, **kwargs)
    
    def _str_(self):
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
    
    def _str_(self):
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
    
    def _str_(self):
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
    
    def _str_(self):
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
    
    def _str_(self):
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
    
    def _str_(self):
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
    
    def _str_(self):
        return f"{self.from_pincode} → {self.to_pincode}: {self.duration_minutes}min ({self.distance_km}km)"
    
    def save(self, *args, **kwargs):
        # Mark as expired if older than 24 hours
        if self.calculated_at and (timezone.now() - self.calculated_at).days >= 1:
            self.is_expired = True
        super().save(*args, **kwargs)


class Dispute(models.Model):
    """Dispute resolution system for booking conflicts"""
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Under Investigation'),
        ('mediation', 'In Mediation'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated'),
        ('closed', 'Closed'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    DISPUTE_TYPE_CHOICES = [
        ('service_quality', 'Service Quality'),
        ('payment_issue', 'Payment Issue'),
        ('signature_refusal', 'Signature Refusal'),
        ('vendor_behavior', 'Vendor Behavior'),
        ('customer_behavior', 'Customer Behavior'),
        ('booking_cancellation', 'Booking Cancellation'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='disputes')
    signature = models.ForeignKey(Signature, on_delete=models.CASCADE, null=True, blank=True, related_name='disputes')
    
    # Disputants
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_disputes')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_disputes', null=True, blank=True)
    
    # Dispute details
    dispute_type = models.CharField(max_length=30, choices=DISPUTE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    customer_evidence = models.JSONField(null=True, blank=True, help_text="Customer's evidence including photos, documents")
    vendor_evidence = models.JSONField(null=True, blank=True, help_text="Vendor's evidence including photos, documents")
    
    # Resolution tracking
    assigned_mediator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mediated_disputes')
    resolution_notes = models.TextField(blank=True)
    resolution_evidence = models.JSONField(null=True, blank=True)
    resolution_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Refund or compensation amount")
    
    # Timeline
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Escalation
    escalated_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='escalated_disputes')
    escalation_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['dispute_type']),
            models.Index(fields=['assigned_mediator']),
            models.Index(fields=['created_at']),
        ]
    
    def _str_(self):
        return f"Dispute {self.id} - {self.title} ({self.get_status_display()})"
    
    def assign_mediator(self, mediator):
        """Assign a mediator to this dispute"""
        self.assigned_mediator = mediator
        self.assigned_at = timezone.now()
        self.status = 'investigating'
        self.save()
    
    def escalate(self, escalated_to, reason):
        """Escalate dispute to higher authority"""
        self.escalated_to = escalated_to
        self.escalation_reason = reason
        self.status = 'escalated'
        self.severity = 'critical'
        self.save()
    
    def resolve(self, resolution_notes, resolution_amount=None, evidence=None):
        """Resolve the dispute"""
        self.resolution_notes = resolution_notes
        self.resolution_amount = resolution_amount
        self.resolution_evidence = evidence
        self.resolved_at = timezone.now()
        self.status = 'resolved'
        self.save()
        
        # Update related booking if needed
        if self.booking.status == 'disputed':
            self.booking.status = 'completed'  # or appropriate status
            self.booking.save()


class VendorBonus(models.Model):
    """Vendor performance bonus tracking"""
    
    BONUS_TYPE_CHOICES = [
        ('performance', 'Performance Bonus'),
        ('surge', 'Surge Pricing Bonus'),
        ('completion_rate', 'High Completion Rate'),
        ('satisfaction', 'High Satisfaction Score'),
        ('monthly_incentive', 'Monthly Incentive'),
        ('referral', 'Referral Bonus'),
        ('special_campaign', 'Special Campaign'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('declined', 'Declined'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bonuses')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, related_name='bonuses')
    
    bonus_type = models.CharField(max_length=30, choices=BONUS_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    percentage = models.FloatField(null=True, blank=True, help_text="Bonus percentage if applicable")
    
    # Criteria and calculation
    criteria_met = models.JSONField(help_text="Criteria that qualified for this bonus")
    calculation_details = models.JSONField(help_text="How the bonus amount was calculated")
    
    # Approval and payment
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bonuses')
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    period_start = models.DateField(help_text="Performance period start date")
    period_end = models.DateField(help_text="Performance period end date")
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vendor', 'bonus_type']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def _str_(self):
        return f"{self.get_bonus_type_display()} - ₹{self.amount} for {self.vendor.get_full_name()}"
    
    def approve(self, approved_by):
        """Approve the bonus"""
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.status = 'approved'
        self.save()
    
    def mark_paid(self):
        """Mark bonus as paid"""
        self.paid_at = timezone.now()
        self.status = 'paid'
        self.save()


class Earnings(models.Model):
    """Track vendor earnings and payment status"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('released', 'Released'),
        ('on_hold', 'On Hold'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earnings')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='earning')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True)
    
    # Payment tracking
    release_date = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_earnings')
    processed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def _str_(self):
        return f"Earnings for {self.vendor.username} - {self.amount} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-set release date when status changes to released
        if self.status == 'released' and not self.release_date and self.pk:
            self.release_date = timezone.now()
        super().save(*args, **kwargs)


class PerformanceMetrics(models.Model):
    """Track vendor performance metrics for bonus calculation"""
    
    vendor = models.OneToOneField(User, on_delete=models.CASCADE, related_name='performance_metrics')
    
    # Job metrics
    total_jobs = models.PositiveIntegerField(default=0)
    completed_jobs = models.PositiveIntegerField(default=0)
    cancelled_jobs = models.PositiveIntegerField(default=0)
    
    # Rating metrics
    total_ratings = models.PositiveIntegerField(default=0)
    rating_sum = models.PositiveIntegerField(default=0)  # Sum of all ratings (1-5)
    
    # Dispute metrics
    disputes_raised = models.PositiveIntegerField(default=0)
    disputes_against = models.PositiveIntegerField(default=0)
    
    # Timing metrics
    on_time_completions = models.PositiveIntegerField(default=0)
    total_completions = models.PositiveIntegerField(default=0)
    
    # Bonus points
    bonus_points = models.PositiveIntegerField(default=0)
    tier = models.CharField(max_length=20, choices=[
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ], default='bronze')
    
    last_calculated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-bonus_points']
        indexes = [
            models.Index(fields=['vendor']),
            models.Index(fields=['bonus_points']),
            models.Index(fields=['tier']),
        ]
    
    def _str_(self):
        return f"Performance Metrics for {self.vendor.username}"
    
    @property
    def avg_rating(self):
        """Calculate average rating"""
        if self.total_ratings == 0:
            return 0
        return round(self.rating_sum / self.total_ratings, 2)
    
    @property
    def completion_rate(self):
        """Calculate job completion rate"""
        if self.total_jobs == 0:
            return 0
        return round((self.completed_jobs / self.total_jobs) * 100, 2)
    
    @property
    def on_time_rate(self):
        """Calculate on-time completion rate"""
        if self.total_completions == 0:
            return 0
        return round((self.on_time_completions / self.total_completions) * 100, 2)
    
    @property
    def dispute_rate(self):
        """Calculate dispute rate"""
        if self.completed_jobs == 0:
            return 0
        return round((self.disputes_against / self.completed_jobs) * 100, 2)
    
    def calculate_bonus_points(self):
        """Calculate bonus points based on performance metrics"""
        # Base points for completed jobs
        job_points = self.completed_jobs * 2
        
        # Rating points (10 points per average rating point)
        rating_points = int(self.avg_rating * 10) if self.avg_rating > 0 else 0
        
        # On-time completion bonus
        on_time_bonus = int(self.on_time_rate * 0.5) if self.on_time_rate > 80 else 0
        
        # Penalty for disputes
        dispute_penalty = self.disputes_against * 5
        
        # Calculate total points
        total_points = job_points + rating_points + on_time_bonus - dispute_penalty
        
        # Ensure points don't go below 0
        self.bonus_points = max(0, total_points)
        
        # Determine tier
        if self.bonus_points >= 90:
            self.tier = 'gold'
        elif self.bonus_points >= 70:
            self.tier = 'silver'
        else:
            self.tier = 'bronze'
        
        return self.bonus_points
    
    def update_metrics_from_booking(self, booking):
        """Update metrics based on a completed booking"""
        self.total_jobs += 1
        
        if booking.status == 'completed' or booking.status == 'signed':
            self.completed_jobs += 1
        
        # Update timing metrics
        if booking.status == 'completed' or booking.status == 'signed':
            self.total_completions += 1
        # Check if completed on time (simplified logic)
        if booking.completion_date and booking.completion_date <= booking.scheduled_date:
            self.on_time_completions += 1
        
        # Update rating if signature exists
        if hasattr(booking, 'signature') and booking.signature.satisfaction_rating:
            self.total_ratings += 1
            self.rating_sum += booking.signature.satisfaction_rating
        
        # Recalculate bonus points
        self.calculate_bonus_points()
        self.save()
    
    def update_for_dispute(self, is_vendor_dispute):
        """Update metrics when a dispute is raised"""
        if is_vendor_dispute:
            self.disputes_raised += 1
        else:
            self.disputes_against += 1
        
        # Recalculate bonus points
        self.calculate_bonus_points()
        self.save()


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
        ('dispute_created', 'Dispute Created'),
        ('dispute_assigned', 'Dispute Assigned'),
        ('dispute_resolved', 'Dispute Resolved'),
        ('bonus_calculated', 'Bonus Calculated'),
        ('bonus_approved', 'Bonus Approved'),
        ('vendor_application_submitted', 'Vendor Application Submitted'),
        ('vendor_application_reviewed', 'Vendor Application Reviewed'),
        ('vendor_application_flagged', 'Vendor Application Flagged by AI'),
        ('document_uploaded', 'Document Uploaded'),
        ('chat_message_sent', 'Chat Message Sent'),
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
    
    def _str_(self):
        return f"{self.user.username} - {self.get_action_display()} {self.resource_type} at {self.timestamp}"


class VendorApplication(models.Model):
    """Vendor onboarding application for verification and approval"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=17, validators=[RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in format: '+999999999'. Up to 15 digits allowed."
    )])
    pincode = models.CharField(max_length=10)
    service_category = models.CharField(max_length=50)
    experience = models.PositiveIntegerField(help_text="Years of experience")
    
    # Document fields - store file paths
    id_proof = models.CharField(max_length=255, help_text="ID proof document path")
    address_proof = models.CharField(max_length=255, help_text="Address proof document path")
    profile_photo = models.CharField(max_length=255, help_text="Profile photo path")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True, help_text="Reviewer remarks for rejection")
    
    # AI Flagging fields
    ai_flag = models.BooleanField(default=False, help_text="AI detected suspicious application")
    flag_reason = models.TextField(blank=True, help_text="Reason for AI flag")
    flagged_at = models.DateTimeField(null=True, blank=True, help_text="When the application was flagged by AI")
    
    # References
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    vendor_account = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendor_application')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['pincode']),
        ]
    
    def _str_(self):
        return f"Vendor Application: {self.name} ({self.status})"
    
    def save(self, *args, **kwargs):
        # If approved and no vendor account exists, create one
        if self.status == 'approved' and not self.vendor_account and self.pk:
            # Create vendor user account
            vendor_user = User.objects.create(
                username=f"vendor_{self.email.split('@')[0]}",
                email=self.email,
                first_name=self.name.split(' ')[0],
                last_name=' '.join(self.name.split(' ')[1:]) if len(self.name.split(' ')) > 1 else '',
                phone=self.phone,
                pincode=self.pincode,
                role='vendor',
                is_verified=True
            )
            self.vendor_account = vendor_user
            
            # Send notification
            try:
                from .notification_service import NotificationService
                NotificationService.send_otp_email(
                    self.email,
                    "Welcome to HomeServe Pro! Your vendor application has been approved.",
                    f"Dear {self.name},\n\nYour vendor application has been approved. You can now log in to your vendor dashboard.\n\nBest regards,\nHomeServe Pro Team"
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send vendor approval notification: {str(e)}")
        
        super().save(*args, **kwargs)


class VendorDocument(models.Model):
    """Documents uploaded during vendor onboarding"""

    DOCUMENT_TYPE_CHOICES = [
        ('id_proof', 'ID Proof'),
        ('address_proof', 'Address Proof'),
        ('business_registration', 'Business Registration'),
        ('gst_certificate', 'GST Certificate'),
        ('pan_card', 'PAN Card'),
        ('bank_statement', 'Bank Statement'),
        ('qualification_certificate', 'Qualification Certificate'),
        ('experience_certificate', 'Experience Certificate'),
        ('police_clearance', 'Police Clearance Certificate'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    application = models.ForeignKey(VendorApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    document_name = models.CharField(max_length=100)

    # File information
    document_file = models.FileField(upload_to='vendor_documents/%Y/%m/%d/')
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100)

    # Review information
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_documents')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)

    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['application', 'document_type']  # One document per type per application
        indexes = [
            models.Index(fields=['application', 'document_type']),
            models.Index(fields=['status']),
            models.Index(fields=['reviewed_by']),
        ]

    def _str_(self):
        return f"{self.application.full_name} - {self.get_document_type_display()} ({self.get_status_display()})"

    def review_document(self, reviewer, status, notes='', rejection_reason=''):
        """Review the document"""
        old_status = self.status
        self.status = status
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.review_notes = notes

        if status == 'rejected':
            self.rejection_reason = rejection_reason

        self.save()

        # Log the review
        from .utils import AuditLogger
        AuditLogger.log_action(
            user=reviewer,
            action='document_reviewed',
            resource_type='VendorDocument',
            resource_id=str(self.id),
            old_values={'status': old_status},
            new_values={'status': status, 'review_notes': notes}
        )


class DisputeMessage(models.Model):
    """Messages in dispute resolution chat"""

    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text Message'),
        ('image', 'Image'),
        ('document', 'Document'),
        ('system', 'System Message'),
    ]

    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)

    message_type = models.CharField(max_length=15, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField(blank=True)  # For text messages

    # File attachments (for image/document messages)
    attachment = models.FileField(upload_to='dispute_attachments/%Y/%m/%d/', null=True, blank=True)
    attachment_name = models.CharField(max_length=255, blank=True)
    attachment_size = models.PositiveIntegerField(null=True, blank=True, help_text="File size in bytes")
    attachment_mime_type = models.CharField(max_length=100, blank=True)

    # Message metadata
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # For escalation tracking
    escalated_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='escalated_messages')

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['dispute', 'created_at']),
            models.Index(fields=['sender', 'recipient']),
            models.Index(fields=['is_read']),
        ]

    def _str_(self):
        return f"Message in dispute {self.dispute.id} by {self.sender.username}"

    def mark_as_read(self, reader):
        """Mark message as read by recipient"""
        if not self.is_read and (reader == self.recipient or reader in [self.dispute.customer, self.dispute.vendor]):
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Log message creation
        from .utils import AuditLogger
        AuditLogger.log_action(
            user=self.sender,
            action='chat_message_sent',
            resource_type='DisputeMessage',
            resource_id=str(self.id),
            new_values={
                'dispute_id': str(self.dispute.id),
                'message_type': self.message_type,
                'recipient': self.recipient.username if self.recipient else None
            }
        )