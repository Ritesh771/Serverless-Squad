from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Service, Booking, Photo, Signature, Payment, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'created_at']
    list_filter = ['role', 'is_verified', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'pincode', 'is_available', 'is_verified')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'pincode')}),
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'duration_minutes', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category']
    ordering = ['name']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'vendor', 'service', 'status', 'total_price', 'scheduled_date']
    list_filter = ['status', 'scheduled_date', 'created_at']
    search_fields = ['customer__username', 'vendor__username', 'service__name', 'pincode']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['booking', 'image_type', 'uploaded_by', 'uploaded_at']
    list_filter = ['image_type', 'uploaded_at']
    search_fields = ['booking__id', 'uploaded_by__username']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'status', 'signed_by', 'satisfaction_rating', 'requested_at']
    list_filter = ['status', 'satisfaction_rating', 'requested_at']
    search_fields = ['booking__id', 'signed_by__username']
    ordering = ['-requested_at']
    readonly_fields = ['id', 'signature_hash', 'requested_at', 'signed_at', 'expires_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'status', 'payment_type', 'processed_at']
    list_filter = ['status', 'payment_type', 'created_at']
    search_fields = ['booking__id', 'stripe_payment_intent_id']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource_type', 'resource_id', 'timestamp']
    list_filter = ['action', 'resource_type', 'timestamp']
    search_fields = ['user__username', 'resource_type', 'resource_id']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing
    
    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion
