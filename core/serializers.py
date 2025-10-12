from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, Service, Booking, Photo, Signature, Payment, AuditLog, 
    VendorAvailability, Address, Dispute, VendorApplication, 
    VendorDocument, DisputeMessage, Earnings, PerformanceMetrics,
    NotificationLog, PincodeAnalytics, BusinessAlert, TravelTimeCache,
    VendorBonus
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'phone', 'pincode', 'is_available', 'is_verified']
        read_only_fields = ['id']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'label', 'address_line', 'pincode', 'lat', 'lng', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        # Ensure only one default address per user
        if attrs.get('is_default'):
            user = self.context['request'].user
            Address.objects.filter(user=user, is_default=True).exclude(
                id=getattr(self.instance, 'id', None)
            ).update(is_default=False)
        return attrs


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm',
                 'first_name', 'last_name', 'role', 'phone', 'pincode']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '_all_'


class BookingSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    dynamic_price_breakdown = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Booking
        fields = '_all_'
        read_only_fields = ['id', 'created_at', 'updated_at', 'customer']
    
    def get_dynamic_price_breakdown(self, obj):
        """Get dynamic pricing breakdown for this booking"""
        from .dynamic_pricing_service import DynamicPricingService
        
        if obj.service and obj.pincode:
            return DynamicPricingService.calculate_dynamic_price(
                obj.service, 
                obj.pincode, 
                obj.scheduled_date
            )
        return None
    
    def create(self, validated_data):
        """Auto-calculate dynamic price on booking creation"""
        from .dynamic_pricing_service import DynamicPricingService
        
        # Calculate dynamic price if not provided
        if 'total_price' not in validated_data or not validated_data.get('total_price'):
            service = validated_data.get('service')
            pincode = validated_data.get('pincode')
            scheduled_date = validated_data.get('scheduled_date')
            
            if service and pincode:
                pricing_data = DynamicPricingService.calculate_dynamic_price(
                    service, pincode, scheduled_date
                )
                validated_data['total_price'] = pricing_data['final_price']
            else:
                # Fallback to base price
                validated_data['total_price'] = service.base_price if service else 0
        
        return super().create(validated_data)


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '_all_'
        read_only_fields = ['uploaded_by', 'uploaded_at']


class SignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields = '_all_'
        read_only_fields = ['id', 'signature_hash', 'requested_at', 'signed_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '_all_'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '_all_'


class VendorAvailabilitySerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.get_full_name', read_only=True)
    
    class Meta:
        model = VendorAvailability
        fields = '_all_'
        read_only_fields = ['vendor', 'created_at', 'updated_at']


class EarningsSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.get_full_name', read_only=True)
    booking_service = serializers.CharField(source='booking.service.name', read_only=True)
    customer_name = serializers.CharField(source='booking.customer.get_full_name', read_only=True)
    
    class Meta:
        model = Earnings
        fields = '_all_'
        read_only_fields = ['id', 'created_at', 'updated_at', 'processed_by', 'processed_at', 'release_date']


class PerformanceMetricsSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.get_full_name', read_only=True)
    avg_rating = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    on_time_rate = serializers.SerializerMethodField()
    dispute_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = PerformanceMetrics
        fields = '_all_'
        read_only_fields = ['id', 'created_at', 'last_calculated']
    
    def get_avg_rating(self, obj):
        return obj.avg_rating
    
    def get_completion_rate(self, obj):
        return obj.completion_rate
    
    def get_on_time_rate(self, obj):
        return obj.on_time_rate
    
    def get_dispute_rate(self, obj):
        return obj.dispute_rate


class VendorApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorApplication
        fields = '_all_'
        read_only_fields = ['id', 'created_at', 'updated_at', 'reviewed_by', 'vendor_account', 'reviewed_at', 'ai_flag', 'flag_reason', 'flagged_at']
    
    def create(self, validated_data):
        # Set default status to pending
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class VendorApplicationListSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    reviewer_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    documents_count = serializers.SerializerMethodField(read_only=True)
    is_complete = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VendorApplication
        fields = [
            'id', 'applicant_name', 'application_type', 'full_name', 'primary_service_category',
            'status', 'submitted_at', 'reviewed_at', 'documents_count', 'is_complete', 'ai_flag', 'flag_reason', 'flagged_at'
        ]

    def get_documents_count(self, obj):
        return obj.documents.count()

    def get_is_complete(self, obj):
        return obj.is_complete()


class VendorDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    application_full_name = serializers.CharField(source='application.full_name', read_only=True)

    class Meta:
        model = VendorDocument
        fields = '_all_'
        read_only_fields = ['id', 'uploaded_by', 'reviewed_by', 'reviewed_at', 'created_at', 'updated_at']


class VendorDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorDocument
        fields = ['document_type', 'document_name', 'document_file']
        read_only_fields = ['id']

    def validate_document_file(self, value):
        # Validate file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 10MB")

        # Validate file type
        allowed_types = [
            'application/pdf',
            'image/jpeg',
            'image/jpg',
            'image/png',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]

        if hasattr(value, 'content_type') and value.content_type not in allowed_types:
            raise serializers.ValidationError("File type not supported. Allowed types: PDF, JPEG, PNG, DOC, DOCX")

        return value

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        validated_data['file_size'] = validated_data['document_file'].size
        validated_data['mime_type'] = validated_data['document_file'].content_type
        return super().create(validated_data)


class DisputeSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.get_full_name', read_only=True)
    assigned_mediator_name = serializers.CharField(source='assigned_mediator.get_full_name', read_only=True)
    escalated_to_name = serializers.CharField(source='escalated_to.get_full_name', read_only=True)
    messages_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Dispute
        fields = '_all_'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_messages_count(self, obj):
        return obj.messages.count()


class DisputeListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.get_full_name', read_only=True)
    assigned_mediator_name = serializers.CharField(source='assigned_mediator.get_full_name', read_only=True)
    messages_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Dispute
        fields = [
            'id', 'title', 'dispute_type', 'severity', 'status', 'customer_name', 'vendor_name',
            'assigned_mediator_name', 'created_at', 'messages_count'
        ]

    def get_messages_count(self, obj):
        return obj.messages.count()


class DisputeMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    dispute_title = serializers.CharField(source='dispute.title', read_only=True)

    class Meta:
        model = DisputeMessage
        fields = '_all_'
        read_only_fields = ['id', 'sender', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class DisputeMessageListSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    is_mine = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DisputeMessage
        fields = [
            'id', 'sender_name', 'recipient_name', 'message_type', 'content',
            'attachment_name', 'is_read', 'created_at', 'is_mine'
        ]

    def get_is_mine(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.sender


class DisputeResolutionSerializer(serializers.Serializer):
    resolution_notes = serializers.CharField(required=True)
    resolution_amount = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    evidence = serializers.JSONField(required=False)

    def validate_resolution_amount(self, value):
        if value and value < 0:
            raise serializers.ValidationError("Resolution amount cannot be negative")
        return value


class VendorApplicationReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('additional_info_required', 'Additional Info Required')
    ])
    review_notes = serializers.CharField(required=False)
    rejection_reason = serializers.CharField(required=False)

    def validate(self, attrs):
        if attrs['status'] == 'rejected' and not attrs.get('rejection_reason'):
            raise serializers.ValidationError("Rejection reason is required when rejecting an application")
        return attrs


class VendorDocumentReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ])
    review_notes = serializers.CharField(required=False)
    rejection_reason = serializers.CharField(required=False)

    def validate(self, attrs):
        if attrs['status'] == 'rejected' and not attrs.get('rejection_reason'):
            raise serializers.ValidationError("Rejection reason is required when rejecting a document")
        return attrs