from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ServiceViewSet, BookingViewSet,
    PhotoViewSet, SignatureViewSet, PaymentViewSet, AuditLogViewSet,
    VendorAvailabilityViewSet, SmartSchedulingAPIView,
    VendorScheduleOptimizationAPIView, TravelTimeAPIView, DynamicPricingAPIView
)
from .auth_views import CustomTokenObtainPairView, send_otp, verify_otp
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'photos', PhotoViewSet)
router.register(r'signatures', SignatureViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'vendor-availability', VendorAvailabilityViewSet, basename='vendoravailability')

urlpatterns = [
    # Authentication URLs
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/send-otp/', send_otp, name='send_otp'),
    path('auth/verify-otp/', verify_otp, name='verify_otp'),
    
    # Smart Scheduling APIs
    path('api/smart-scheduling/', SmartSchedulingAPIView.as_view(), name='smart-scheduling'),
    path('api/vendor-optimization/', VendorScheduleOptimizationAPIView.as_view(), name='vendor-optimization'),
    path('api/travel-time/', TravelTimeAPIView.as_view(), name='travel-time'),
    
    # Dynamic Pricing API
    path('api/dynamic-pricing/', DynamicPricingAPIView.as_view(), name='dynamic-pricing'),
    
    # API URLs
    path('api/', include(router.urls)),
    
    # Admin Dashboard URLs
    path('admin-dashboard/', include('core.admin_urls')),
]