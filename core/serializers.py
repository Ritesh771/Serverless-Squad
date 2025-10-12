from rest_framework import serializers
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Service, Booking, Photo, Signature, Payment, AuditLog, VendorAvailability


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'phone', 'pincode', 'is_available', 'is_verified']
        read_only_fields = ['id']


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
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    dynamic_price_breakdown = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
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
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'uploaded_at']


class SignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields = '__all__'
        read_only_fields = ['id', 'signature_hash', 'requested_at', 'signed_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'


class VendorAvailabilitySerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.get_full_name', read_only=True)
    
    class Meta:
        model = VendorAvailability
        fields = '__all__'
        read_only_fields = ['vendor', 'created_at', 'updated_at']