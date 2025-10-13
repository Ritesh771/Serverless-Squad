from django.urls import path, include
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, AddressViewSet, ServiceViewSet, BookingViewSet,
    PhotoViewSet, SignatureViewSet, PaymentViewSet, AuditLogViewSet,
    VendorAvailabilityViewSet, SmartSchedulingAPIView,
    VendorScheduleOptimizationAPIView, TravelTimeAPIView, DynamicPricingAPIView,
    VendorSearchAPIView, DisputeViewSet, VendorApplicationViewSet, 
    EarningsViewSet, PerformanceMetricsViewSet,
    DisputeResolutionAPIView, VendorBonusAPIView, VendorAIAnalyticsAPIView,
    EnhancedSignatureAPIView, VendorDocumentViewSet,
    dispute_analytics, vendor_onboarding_analytics, chat_query, chat_context,
    current_user_profile,
    # Advanced Features APIs
    PincodeAIAnalyticsAPIView, AdvancedDisputeResolutionAPIView, AdvancedVendorBonusAPIView
)
from .auth_views import CustomTokenObtainPairView, send_otp, verify_otp, send_vendor_otp, verify_vendor_otp, register
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'photos', PhotoViewSet)
router.register(r'signatures', SignatureViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'vendor-availability', VendorAvailabilityViewSet, basename='vendoravailability')
router.register(r'vendor-applications', VendorApplicationViewSet, basename='vendorapplication')
router.register(r'vendor-documents', VendorDocumentViewSet, basename='vendordocument')
router.register(r'earnings', EarningsViewSet, basename='earnings')
router.register(r'performance-metrics', PerformanceMetricsViewSet, basename='performancemetrics')
router.register(r'disputes', DisputeViewSet, basename='dispute')

urlpatterns = [
    # Authentication URLs
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/register/', register, name='register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/send-otp/', send_otp, name='send_otp'),
    path('auth/verify-otp/', verify_otp, name='verify_otp'),
    path('auth/vendor/send-otp/', send_vendor_otp, name='send_vendor_otp'),
    path('auth/vendor/verify-otp/', verify_vendor_otp, name='verify_vendor_otp'),
    
    # User Profile
    path('api/users/me/', current_user_profile, name='current-user-profile'),
    
    # Vendor Search API
    path('api/vendor-search/', VendorSearchAPIView.as_view(), name='vendor-search'),
    
    # Smart Scheduling APIs
    path('api/smart-scheduling/', SmartSchedulingAPIView.as_view(), name='smart-scheduling'),
    path('api/vendor-optimization/', VendorScheduleOptimizationAPIView.as_view(), name='vendor-optimization'),
    path('api/travel-time/', TravelTimeAPIView.as_view(), name='travel-time'),
    
    # Dynamic Pricing API
    path('api/dynamic-pricing/', DynamicPricingAPIView.as_view(), name='dynamic-pricing'),
    
    # Enhanced APIs
    path('api/disputes/', DisputeResolutionAPIView.as_view(), name='dispute-resolution'),
    path('api/vendor-bonuses/', VendorBonusAPIView.as_view(), name='vendor-bonuses'),
    path('api/vendor-ai-analytics/', VendorAIAnalyticsAPIView.as_view(), name='vendor-ai-analytics'),
    path('api/enhanced-signatures/', EnhancedSignatureAPIView.as_view(), name='enhanced-signatures'),
    
    # Advanced Features APIs
    path('api/pincode-ai-analytics/', PincodeAIAnalyticsAPIView.as_view(), name='pincode-ai-analytics'),
    path('api/advanced-dispute-resolution/<uuid:dispute_id>/', AdvancedDisputeResolutionAPIView.as_view(), name='advanced-dispute-resolution'),
    path('api/advanced-vendor-bonus/', AdvancedVendorBonusAPIView.as_view(), name='advanced-vendor-bonus'),
    
    # Chatbot APIs
    path('api/chat/query/', chat_query, name='chat-query'),
    path('api/chat/context/', chat_context, name='chat-context'),
    
    # Analytics APIs
    path('api/analytics/disputes/', dispute_analytics, name='dispute-analytics'),
    path('api/analytics/vendor-onboarding/', vendor_onboarding_analytics, name='vendor-onboarding-analytics'),
    
    # API URLs
    path('api/', include(router.urls)),
    
    # Admin Dashboard URLs
    path('admin-dashboard/', include('core.admin_urls')),
]