from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, date
from .models import (
    User, Service, Booking, Photo, Signature, Payment, AuditLog,
    VendorAvailability, TravelTimeCache
)
from .serializers import (
    UserSerializer, ServiceSerializer, BookingSerializer,
    PhotoSerializer, SignatureSerializer, PaymentSerializer, AuditLogSerializer,
    VendorAvailabilitySerializer
)
from .permissions import (
    IsCustomer, IsVendor, IsOnboardManager, IsOpsManager, 
    IsSuperAdmin, IsAdminUser, IsOwnerOrAdmin
)
from .utils import AuditLogger
from .payment_service import PaymentService
from .signature_service import SignatureService
from .scheduling_service import scheduling_service
from .travel_service import travel_service
from .dynamic_pricing_service import DynamicPricingService


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'is_verified', 'pincode']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return User.objects.all()
        elif user.role in ['onboard_manager', 'ops_manager']:
            return User.objects.filter(role__in=['customer', 'vendor'])
        else:
            return User.objects.filter(id=user.id)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'pincode', 'scheduled_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Booking.objects.filter(customer=user)
        elif user.role == 'vendor':
            return Booking.objects.filter(vendor=user)
        elif user.role in ['ops_manager', 'super_admin']:
            return Booking.objects.all()
        else:
            return Booking.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role == 'customer':
            booking = serializer.save(customer=self.request.user)
            
            # Apply smart buffering if vendor is assigned
            if booking.vendor and booking.pincode:
                self._apply_smart_buffering(booking)
            
        AuditLogger.log_action(
            user=self.request.user,
            action='create',
            resource_type='Booking',
            resource_id=booking.id,
            request=self.request
        )
    
    def _apply_smart_buffering(self, booking):
        """Apply smart buffering calculations to a booking"""
        try:
            # Get travel time to customer location
            vendor_pincode = booking.vendor.pincode
            if not vendor_pincode:
                # Try to get from vendor availability
                availability = VendorAvailability.objects.filter(
                    vendor=booking.vendor, is_active=True
                ).first()
                if availability:
                    vendor_pincode = availability.primary_pincode
            
            if vendor_pincode:
                travel_data = travel_service.get_travel_time(vendor_pincode, booking.pincode)
                booking.travel_time_to_location_minutes = travel_data['duration_minutes']
                
                # For return trip, assume same travel time (could be optimized later)
                booking.travel_time_from_location_minutes = travel_data['duration_minutes']
            
            # Set estimated service duration from service model
            booking.estimated_service_duration_minutes = booking.service.duration_minutes
            
            # Get vendor's preferred buffer time
            availability = VendorAvailability.objects.filter(
                vendor=booking.vendor, is_active=True
            ).first()
            
            if availability:
                booking.buffer_before_minutes = availability.preferred_buffer_minutes
                booking.buffer_after_minutes = availability.preferred_buffer_minutes
            
            booking.save()
            
        except Exception as e:
            # Log error but don't fail the booking creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Smart buffering failed for booking {booking.id}: {e}")
    
    @action(detail=True, methods=['post'], permission_classes=[IsVendor])
    def accept_booking(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk, status='pending')
        booking.vendor = request.user
        booking.status = 'confirmed'
        booking.save()
        
        AuditLogger.log_action(
            user=request.user, action='update', resource_type='Booking',
            resource_id=booking.id, request=request
        )
        
        return Response({'message': 'Booking accepted successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsVendor])
    def complete_booking(self, request, pk=None):
        """Mark booking as completed by vendor"""
        booking = get_object_or_404(Booking, pk=pk, vendor=request.user, status='in_progress')
        booking.status = 'completed'
        booking.completion_date = timezone.now()
        booking.save()
        
        # Create payment intent
        payment_intent = PaymentService.create_payment_intent(booking)
        
        return Response({
            'message': 'Booking completed successfully',
            'payment_intent': payment_intent
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsVendor])
    def request_signature(self, request, pk=None):
        """Request customer signature for completed booking"""
        booking = get_object_or_404(Booking, pk=pk, vendor=request.user)
        
        signature = SignatureService.request_signature(booking, request.user)
        if signature:
            return Response({
                'message': 'Signature requested successfully',
                'signature_id': signature.id
            })
        else:
            return Response(
                {'error': 'Failed to request signature'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Photo.objects.filter(booking__customer=user)
        elif user.role == 'vendor':
            return Photo.objects.filter(booking__vendor=user)
        elif user.role in ['ops_manager', 'super_admin']:
            return Photo.objects.all()
        return Photo.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class SignatureViewSet(viewsets.ModelViewSet):
    queryset = Signature.objects.all()
    serializer_class = SignatureSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Signature.objects.filter(booking__customer=user)
        elif user.role == 'vendor':
            return Signature.objects.filter(booking__vendor=user)
        elif user.role in ['ops_manager', 'super_admin']:
            return Signature.objects.all()
        return Signature.objects.none()
    
    @action(detail=True, methods=['post'], permission_classes=[IsCustomer])
    def sign(self, request, pk=None):
        """Sign booking with satisfaction rating"""
        satisfaction_rating = request.data.get('satisfaction_rating')
        comments = request.data.get('comments', '')
        
        if not satisfaction_rating or not (1 <= int(satisfaction_rating) <= 5):
            return Response(
                {'error': 'Satisfaction rating (1-5) is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        signature = SignatureService.sign_booking(
            pk, request.user, int(satisfaction_rating), comments
        )
        
        if signature:
            return Response({
                'message': 'Booking signed successfully',
                'signature_hash': signature.signature_hash
            })
        else:
            return Response(
                {'error': 'Failed to sign booking'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ops_manager', 'super_admin']:
            return Payment.objects.all()
        elif user.role == 'vendor':
            return Payment.objects.filter(booking__vendor=user)
        elif user.role == 'customer':
            return Payment.objects.filter(booking__customer=user)
        return Payment.objects.none()
    
    @action(detail=True, methods=['post'], permission_classes=[IsOpsManager])
    def process_manual_payment(self, request, pk=None):
        """Process manual payment by ops manager"""
        payment = get_object_or_404(Payment, pk=pk)
        
        success = PaymentService.process_manual_payment(payment.id, request.user)
        
        if success:
            return Response({'message': 'Payment processed successfully'})
        else:
            return Response(
                {'error': 'Failed to process payment'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'action', 'resource_type']


class VendorAvailabilityViewSet(viewsets.ModelViewSet):
    """Manage vendor availability schedules"""
    serializer_class = VendorAvailabilitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'vendor':
            return VendorAvailability.objects.filter(vendor=self.request.user)
        elif self.request.user.role in ['ops_manager', 'super_admin']:
            return VendorAvailability.objects.all()
        return VendorAvailability.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role == 'vendor':
            serializer.save(vendor=self.request.user)


class SmartSchedulingAPIView(APIView):
    """Smart scheduling endpoints for intelligent booking"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get available time slots for a vendor and service"""
        vendor_id = request.query_params.get('vendor_id')
        service_id = request.query_params.get('service_id')
        customer_pincode = request.query_params.get('customer_pincode')
        preferred_date = request.query_params.get('preferred_date')
        
        if not all([vendor_id, service_id, customer_pincode, preferred_date]):
            return Response(
                {'error': 'Missing required parameters: vendor_id, service_id, customer_pincode, preferred_date'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            preferred_date_obj = datetime.strptime(preferred_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            available_slots = scheduling_service.get_available_time_slots(
                int(vendor_id), int(service_id), customer_pincode, preferred_date_obj
            )
            
            return Response({
                'available_slots': available_slots,
                'total_slots': len(available_slots)
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Get optimal booking suggestion"""
        vendor_id = request.data.get('vendor_id')
        service_id = request.data.get('service_id')
        customer_pincode = request.data.get('customer_pincode')
        preferred_date = request.data.get('preferred_date')
        
        if not all([vendor_id, service_id, customer_pincode, preferred_date]):
            return Response(
                {'error': 'Missing required parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            preferred_date_obj = datetime.strptime(preferred_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            optimal_slot = scheduling_service.suggest_optimal_booking_time(
                int(vendor_id), int(service_id), customer_pincode, preferred_date_obj
            )
            
            if optimal_slot:
                return Response({'optimal_slot': optimal_slot})
            else:
                return Response(
                    {'message': 'No available slots found for the specified date'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VendorScheduleOptimizationAPIView(APIView):
    """Vendor schedule optimization and analytics"""
    permission_classes = [IsVendor]
    
    def get(self, request):
        """Get schedule optimization for vendor's specific date"""
        optimization_date = request.query_params.get('date')
        
        if not optimization_date:
            return Response(
                {'error': 'Date parameter is required (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date_obj = datetime.strptime(optimization_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            optimization = scheduling_service.optimize_vendor_schedule(
                request.user.id, date_obj
            )
            return Response(optimization)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TravelTimeAPIView(APIView):
    """Travel time calculation endpoints"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get travel time between two pincodes"""
        from_pincode = request.query_params.get('from_pincode')
        to_pincode = request.query_params.get('to_pincode')
        
        if not all([from_pincode, to_pincode]):
            return Response(
                {'error': 'Both from_pincode and to_pincode are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            travel_data = travel_service.get_travel_time(from_pincode, to_pincode)
            return Response(travel_data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DynamicPricingAPIView(APIView):
    """Real-time dynamic pricing based on demand and supply"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dynamic price for a service in a pincode"""
        service_id = request.query_params.get('service_id')
        pincode = request.query_params.get('pincode')
        scheduled_datetime = request.query_params.get('scheduled_datetime')
        
        if not all([service_id, pincode]):
            return Response(
                {'error': 'service_id and pincode are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = Service.objects.get(id=service_id, is_active=True)
        except Service.DoesNotExist:
            return Response(
                {'error': 'Service not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Parse scheduled datetime if provided
        scheduled_dt = None
        if scheduled_datetime:
            try:
                scheduled_dt = datetime.fromisoformat(scheduled_datetime.replace('Z', '+00:00'))
            except ValueError:
                return Response(
                    {'error': 'Invalid datetime format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            # Calculate dynamic price
            pricing_data = DynamicPricingService.calculate_dynamic_price(
                service, pincode, scheduled_dt
            )
            
            return Response({
                'service': {
                    'id': service.id,
                    'name': service.name,
                    'category': service.category
                },
                'pincode': pincode,
                'pricing': pricing_data,
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Get price predictions for multiple days"""
        service_id = request.data.get('service_id')
        pincode = request.data.get('pincode')
        days = request.data.get('days', 7)
        
        if not all([service_id, pincode]):
            return Response(
                {'error': 'service_id and pincode are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = Service.objects.get(id=service_id, is_active=True)
        except Service.DoesNotExist:
            return Response(
                {'error': 'Service not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Get price predictions
            predictions = DynamicPricingService.get_price_prediction(
                service, pincode, int(days)
            )
            
            return Response({
                'service': {
                    'id': service.id,
                    'name': service.name,
                    'category': service.category,
                    'base_price': float(service.base_price)
                },
                'pincode': pincode,
                'predictions': predictions,
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )