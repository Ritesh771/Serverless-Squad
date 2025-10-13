from rest_framework import viewsets, status
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime, date
import json
import logging

logger = logging.getLogger(__name__)

from .models import (
    User, Service, Booking, Photo, Signature, Payment, AuditLog,
    VendorAvailability, TravelTimeCache, Dispute, VendorBonus,
    VendorApplication, VendorDocument, DisputeMessage, Address,
    Earnings, PerformanceMetrics, NotificationLog, PincodeAnalytics,
    BusinessAlert
)
from .serializers import (
    UserSerializer, ServiceSerializer, BookingSerializer,
    PhotoSerializer, SignatureSerializer, PaymentSerializer, AuditLogSerializer,
    VendorAvailabilitySerializer, VendorApplicationSerializer, VendorDocumentSerializer,
    VendorApplicationListSerializer, VendorDocumentUploadSerializer,
    DisputeSerializer, DisputeMessageSerializer, DisputeListSerializer,
    DisputeMessageListSerializer, AddressSerializer, EarningsSerializer,
    PerformanceMetricsSerializer
)
from .permissions import (
    IsCustomer, IsVendor, IsOnboardManager, IsOpsManager, 
    IsSuperAdmin, IsAdminUser, IsOwnerOrAdmin, IsDisputeParty
)
from .utils import AuditLogger
from .payment_service import PaymentService
from .signature_service import SignatureService
from .scheduling_service import scheduling_service
from .travel_service import travel_service
from .dynamic_pricing_service import DynamicPricingService
from .dispute_service import dispute_service, DisputeResolutionService
from .vendor_onboarding_service import VendorOnboardingService
from .vendor_bonus_service import VendorBonusService, AdvancedVendorBonusService
from .vendor_ai_service import vendor_ai_service
from .ai_services.pincode_ai import analyze_pincode_pulse
from .dispute_service import AdvancedDisputeService


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'is_verified', 'pincode']
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAdminUser]
        elif self.action == 'destroy':
            permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update']:
            # Allow users to update their own profile, admin can update any
            permission_classes = [IsAuthenticated]
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
    
    def perform_update(self, serializer):
        # Ensure users can only update their own profile unless they're admin
        user_to_update = self.get_object()
        requesting_user = self.request.user
        
        # Debug logging
        print(f"DEBUG: User {requesting_user.id} (role: {requesting_user.role}) trying to update user {user_to_update.id}")
        
        if requesting_user.role not in ['super_admin', 'onboard_manager', 'ops_manager']:
            if user_to_update.id != requesting_user.id:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You can only update your own profile")
        
        serializer.save()


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def current_user_profile(request):
    """
    Get or update current user's profile
    """
    user = request.user
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Only allow updating specific fields for profile
        allowed_fields = ['first_name', 'last_name', 'phone', 'pincode']
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        serializer = UserSerializer(user, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Log the action
            AuditLogger.log_action(
                user=request.user,
                action='update',
                resource_type='User',
                resource_id=user.id,
                request=request
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        
        # Send WebSocket notification
        try:
            self._send_booking_notification('booking_approved', booking)
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {str(e)}")
        
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
    
    def _send_booking_notification(self, event_type, booking):
        """Send WebSocket notification for booking events"""
        try:
            # Import here to avoid circular imports
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            
            # Prepare notification data
            notification_data = {
                'event_type': event_type,
                'booking_id': str(booking.id),
                'service_name': booking.service.name,
                'customer_id': str(booking.customer.id),
                'customer_name': booking.customer.get_full_name(),
                'vendor_id': str(booking.vendor.id) if booking.vendor else None,
                'vendor_name': booking.vendor.get_full_name() if booking.vendor else None,
                'status': booking.status,
                'timestamp': timezone.now().isoformat()
            }
            
            # Notify customer
            async_to_sync(channel_layer.group_send)(
                f'chat_{booking.customer.id}',
                {
                    'type': 'chat.notification',
                    'notification_type': event_type,
                    'data': notification_data
                }
            )
            
            # Notify vendor if exists
            if booking.vendor:
                async_to_sync(channel_layer.group_send)(
                    f'chat_{booking.vendor.id}',
                    {
                        'type': 'chat.notification',
                        'notification_type': event_type,
                        'data': notification_data
                    }
                )
            
            # Notify ops managers
            async_to_sync(channel_layer.group_send)(
                'role_ops_manager',
                {
                    'type': 'chat.notification',
                    'notification_type': event_type,
                    'data': notification_data
                }
            )
            
            logger.info(f"WebSocket notification sent for {event_type} on booking {booking.id}")
            
        except Exception as e:
            logger.error(f"Failed to send WebSocket notification: {str(e)}")


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


class DisputeResolutionAPIView(APIView):
    """Dispute resolution endpoints"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a new dispute"""
        action = request.data.get('action')
        
        if action == 'create_dispute':
            booking_id = request.data.get('booking_id')
            dispute_type = request.data.get('dispute_type')
            title = request.data.get('title')
            description = request.data.get('description')
            evidence = request.data.get('evidence')
            
            try:
                booking = Booking.objects.get(id=booking_id, customer=request.user)
                dispute = dispute_service.create_dispute(
                    booking, request.user, dispute_type, title, description, evidence
                )
                
                if dispute:
                    return Response({
                        'status': 'success',
                        'dispute_id': str(dispute.id),
                        'message': 'Dispute created successfully'
                    })
                else:
                    return Response({
                        'status': 'error',
                        'message': 'Failed to create dispute'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Booking.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Booking not found or unauthorized'
                }, status=status.HTTP_404_NOT_FOUND)
        
        elif action == 'add_vendor_response':
            dispute_id = request.data.get('dispute_id')
            evidence = request.data.get('evidence')
            response_notes = request.data.get('response_notes', '')
            
            success = dispute_service.add_vendor_response(
                dispute_id, request.user, evidence, response_notes
            )
            
            if success:
                return Response({
                    'status': 'success',
                    'message': 'Vendor response added successfully'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Failed to add vendor response'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        elif action == 'resolve_dispute':
            # Only for ops managers and super admins
            if request.user.role not in ['ops_manager', 'super_admin']:
                return Response({
                    'status': 'error',
                    'message': 'Unauthorized to resolve disputes'
                }, status=status.HTTP_403_FORBIDDEN)
            
            dispute_id = request.data.get('dispute_id')
            resolution_notes = request.data.get('resolution_notes')
            resolution_amount = request.data.get('resolution_amount')
            evidence = request.data.get('evidence')
            
            success = dispute_service.resolve_dispute(
                dispute_id, request.user, resolution_notes, resolution_amount, evidence
            )
            
            if success:
                return Response({
                    'status': 'success',
                    'message': 'Dispute resolved successfully'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Failed to resolve dispute'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'status': 'error',
            'message': 'Invalid action'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """Get dispute analytics"""
        if request.user.role not in ['ops_manager', 'super_admin']:
            return Response({
                'status': 'error',
                'message': 'Unauthorized'
            }, status=status.HTTP_403_FORBIDDEN)
        
        date_range_days = int(request.query_params.get('days', 30))
        analytics = dispute_service.get_dispute_analytics(date_range_days)
        
        return Response({
            'status': 'success',
            'analytics': analytics,
            'timestamp': timezone.now().isoformat()
        })


class VendorBonusAPIView(APIView):
    """Vendor bonus calculation and management endpoints"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Calculate vendor bonuses"""
        action = request.data.get('action')
        
        if action == 'calculate_monthly_bonuses':
            # Only for admins or the vendor themselves
            vendor_id = request.data.get('vendor_id')
            year = request.data.get('year', timezone.now().year)
            month = request.data.get('month', timezone.now().month)
            
            if request.user.role == 'vendor':
                vendor = request.user
            elif request.user.role in ['ops_manager', 'super_admin']:
                try:
                    vendor = User.objects.get(id=vendor_id, role='vendor')
                except User.DoesNotExist:
                    return Response({
                        'status': 'error',
                        'message': 'Vendor not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Unauthorized'
                }, status=status.HTTP_403_FORBIDDEN)
            
            bonuses = vendor_bonus_service.calculate_monthly_bonuses(vendor, year, month)
            
            return Response({
                'status': 'success',
                'bonuses': [
                    {
                        'id': str(bonus.id),
                        'type': bonus.get_bonus_type_display(),
                        'amount': float(bonus.amount),
                        'criteria': bonus.criteria_met,
                        'notes': bonus.notes
                    }
                    for bonus in bonuses
                ],
                'total_amount': sum(bonus.amount for bonus in bonuses)
            })
        
        elif action == 'calculate_surge_bonus':
            booking_id = request.data.get('booking_id')
            
            try:
                booking = Booking.objects.get(id=booking_id)
                
                # Check authorization
                if (request.user.role == 'vendor' and booking.vendor != request.user) or \
                   (request.user.role not in ['vendor', 'ops_manager', 'super_admin']):
                    return Response({
                        'status': 'error',
                        'message': 'Unauthorized'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                surge_bonus = vendor_bonus_service.calculate_real_time_surge_bonus(booking)
                
                return Response({
                    'status': 'success',
                    'surge_bonus': surge_bonus
                })
                
            except Booking.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Booking not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'status': 'error',
            'message': 'Invalid action'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """Get vendor bonus summary"""
        vendor_id = request.query_params.get('vendor_id')
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if request.user.role == 'vendor':
            vendor = request.user
        elif request.user.role in ['ops_manager', 'super_admin'] and vendor_id:
            try:
                vendor = User.objects.get(id=vendor_id, role='vendor')
            except User.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Vendor not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'status': 'error',
                'message': 'Unauthorized or missing vendor_id'
            }, status=status.HTTP_403_FORBIDDEN)
        
        summary = vendor_bonus_service.get_vendor_bonus_summary(
            vendor, 
            int(year) if year else None, 
            int(month) if month else None
        )
        
        return Response({
            'status': 'success',
            'vendor_id': vendor.id,
            'vendor_name': vendor.get_full_name(),
            'summary': summary,
            'timestamp': timezone.now().isoformat()
        })


class VendorAIAnalyticsAPIView(APIView):
    """AI-based vendor analytics and scoring endpoints"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get vendor AI score and analytics"""
        vendor_id = request.query_params.get('vendor_id')
        analysis_period = int(request.query_params.get('days', 90))
        
        if request.user.role == 'vendor':
            vendor = request.user
        elif request.user.role in ['ops_manager', 'super_admin'] and vendor_id:
            try:
                vendor = User.objects.get(id=vendor_id, role='vendor')
            except User.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Vendor not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'status': 'error',
                'message': 'Unauthorized or missing vendor_id'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Calculate vendor score
        score_data = vendor_ai_service.calculate_vendor_score(vendor, analysis_period)
        
        return Response({
            'status': 'success',
            'vendor_analytics': score_data,
            'timestamp': timezone.now().isoformat()
        })
    
    def post(self, request):
        """AI-based predictions and analysis"""
        action = request.data.get('action')
        
        if action == 'predict_service_duration':
            service_id = request.data.get('service_id')
            vendor_id = request.data.get('vendor_id')
            pincode = request.data.get('pincode')
            
            try:
                service = Service.objects.get(id=service_id)
                vendor = User.objects.get(id=vendor_id, role='vendor')
                
                prediction = vendor_ai_service.predict_service_duration(service, vendor, pincode)
                
                return Response({
                    'status': 'success',
                    'prediction': prediction
                })
                
            except (Service.DoesNotExist, User.DoesNotExist) as e:
                return Response({
                    'status': 'error',
                    'message': f'Resource not found: {str(e)}'
                }, status=status.HTTP_404_NOT_FOUND)
        
        elif action == 'detect_fraud':
            booking_id = request.data.get('booking_id')
            
            # Only allow admins to run fraud detection
            if request.user.role not in ['ops_manager', 'super_admin']:
                return Response({
                    'status': 'error',
                    'message': 'Unauthorized'
                }, status=status.HTTP_403_FORBIDDEN)
            
            try:
                booking = Booking.objects.get(id=booking_id)
                fraud_analysis = vendor_ai_service.detect_fraudulent_patterns(booking)
                
                return Response({
                    'status': 'success',
                    'fraud_analysis': fraud_analysis
                })
                
            except Booking.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Booking not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'status': 'error',
            'message': 'Invalid action'
        }, status=status.HTTP_400_BAD_REQUEST)


# Enhanced signature endpoints
class EnhancedSignatureAPIView(APIView):
    """Enhanced signature endpoints with photo analysis"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Enhanced signature request with photo analysis"""
        action = request.data.get('action')
        
        if action == 'request_signature_with_photos':
            booking_id = request.data.get('booking_id')
            photo_ids = request.data.get('photo_ids', [])
            
            try:
                booking = Booking.objects.get(id=booking_id, vendor=request.user)
                
                # Verify photos exist and belong to this booking
                photos = Photo.objects.filter(
                    id__in=photo_ids,
                    booking=booking
                )
                
                if photos.count() < 2:  # Need at least before and after
                    return Response({
                        'status': 'error',
                        'message': 'At least 2 photos (before/after) are required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Request signature (existing functionality)
                signature = SignatureService.request_signature(booking, request.user)
                
                if signature:
                    return Response({
                        'status': 'success',
                        'signature_id': str(signature.id),
                        'message': 'Signature requested with photos'
                    })
                else:
                    return Response({
                        'status': 'error',
                        'message': 'Failed to request signature'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Booking.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Booking not found or unauthorized'
                }, status=status.HTTP_404_NOT_FOUND)
        
        elif action == 'reject_signature':
            # Customer rejecting signature - create dispute
            signature_id = request.data.get('signature_id')
            reason = request.data.get('reason')
            evidence = request.data.get('evidence')
            
            try:
                signature = Signature.objects.get(id=signature_id, booking__customer=request.user)
                
                # Create dispute instead of signing
                dispute = dispute_service.create_dispute(
                    signature.booking,
                    request.user,
                    'signature_refusal',
                    f'Signature rejection: {reason}',
                    f'Customer rejected signature for booking {signature.booking.id}. Reason: {reason}',
                    evidence
                )
                
                if dispute:
                    # Update signature status
                    signature.status = 'disputed'
                    signature.save()
                    
                    return Response({
                        'status': 'success',
                        'dispute_id': str(dispute.id),
                        'message': 'Signature rejected and dispute created'
                    })
                else:
                    return Response({
                        'status': 'error',
                        'message': 'Failed to create dispute'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Signature.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Signature not found or unauthorized'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'status': 'error',
            'message': 'Invalid action'
        }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def chat_query(request):
    """Handle chat queries and return AI/workflow responses"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        role = data.get('role')
        message = data.get('message')
        
        if not all([user_id, role, message]):
            return JsonResponse({'error': 'Missing required fields: user_id, role, message'}, status=400)
        
        # Get user object
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Process message based on role
        response = process_chat_message(user, role, message)
        
        # Log chat action
        AuditLogger.log_action(
            user=user,
            action='chat_query',
            resource_type='Chat',
            resource_id='chat_query',
            new_values={'message': message, 'response': response}
        )
        
        return JsonResponse({'response': response})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        # Log error action
        try:
            AuditLogger.log_action(
                user=request.user if hasattr(request, 'user') else None,
                action='chat_query_error',
                resource_type='Chat',
                resource_id='chat_query',
                new_values={'error': str(e)}
            )
        except:
            pass
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
def chat_context(request):
    """Provide role-specific context for chat suggestions"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        user_id = request.GET.get('user_id')
        role = request.GET.get('role')
        
        if not all([user_id, role]):
            return JsonResponse({'error': 'Missing required parameters: user_id, role'}, status=400)
        
        # Get user object
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Get context based on role
        context = get_role_context(user, role)
        
        # Log context request
        AuditLogger.log_action(
            user=user,
            action='chat_context',
            resource_type='Chat',
            resource_id='chat_context',
            new_values={'role': role}
        )
        
        return JsonResponse({'context': context})
        
    except Exception as e:
        logger.error(f"Error getting chat context: {str(e)}")
        # Log error action
        try:
            AuditLogger.log_action(
                user=request.user if hasattr(request, 'user') else None,
                action='chat_context_error',
                resource_type='Chat',
                resource_id='chat_context',
                new_values={'error': str(e)}
            )
        except:
            pass
        return JsonResponse({'error': 'Internal server error'}, status=500)


def process_chat_message(user, role, message):
    """Process chat message based on user role and return appropriate response"""
    message_lower = message.lower()
    
    # Handle predefined workflow commands
    if role == 'customer':
        if 'track' in message_lower and 'booking' in message_lower:
            return handle_customer_track_bookings(user)
        elif 'approve' in message_lower and 'signature' in message_lower:
            return handle_customer_approve_signature(user, message)
        elif 'booking' in message_lower and 'detail' in message_lower:
            return handle_customer_booking_details(user, message)
        elif 'my bookings' in message_lower or 'list bookings' in message_lower:
            return handle_customer_track_bookings(user)
    
    elif role == 'vendor':
        if 'upload' in message_lower and 'photo' in message_lower:
            return handle_vendor_upload_photos(user, message)
        elif 'request' in message_lower and 'signature' in message_lower:
            return handle_vendor_request_signature(user, message)
        elif 'calendar' in message_lower or 'schedule' in message_lower:
            return handle_vendor_calendar(user)
        elif 'pending' in message_lower and 'job' in message_lower:
            return handle_vendor_pending_jobs(user)
        elif 'my jobs' in message_lower or 'list jobs' in message_lower:
            return handle_vendor_pending_jobs(user)
    
    elif role in ['admin', 'onboard_manager', 'ops_manager']:
        if 'approve' in message_lower and 'vendor' in message_lower:
            return handle_admin_approve_vendor(user, message)
        elif 'monitor' in message_lower and 'signature' in message_lower:
            return handle_admin_monitor_signatures(user)
        elif 'resolve' in message_lower and 'dispute' in message_lower:
            return handle_admin_resolve_dispute(user, message)
        elif 'pending vendors' in message_lower or 'vendor queue' in message_lower:
            return handle_admin_approve_vendor(user, message)
        elif 'signature' in message_lower and 'pending' in message_lower:
            return handle_admin_monitor_signatures(user)
    
    # Handle workflow action commands
    if message == 'track_bookings':
        if role == 'customer':
            return handle_customer_track_bookings(user)
    elif message == 'view_booking_details':
        if role == 'customer':
            return handle_customer_booking_details(user, "")
    elif message == 'upload_photos':
        if role == 'vendor':
            return handle_vendor_upload_photos(user, "")
    elif message == 'request_signature':
        if role == 'vendor':
            return handle_vendor_request_signature(user, "")
    elif message == 'approve_vendor':
        if role in ['admin', 'onboard_manager']:
            return handle_admin_approve_vendor(user, "")
    elif message == 'monitor_signatures':
        if role in ['admin', 'ops_manager']:
            return handle_admin_monitor_signatures(user)
    
    # Default AI-like response for unrecognized queries
    return generate_ai_response(message, role)


def get_role_context(user, role):
    """Get role-specific context for chat suggestions"""
    context = {
        'role': role,
        'suggested_actions': [],
        'recent_activities': []
    }
    
    if role == 'customer':
        # Get customer's bookings
        bookings = Booking.objects.filter(customer=user).order_by('-created_at')[:5]
        context['suggested_actions'] = [
            'Track my bookings',
            'Approve signature for completed service',
            'View booking details'
        ]
        context['recent_activities'] = [
            {
                'type': 'booking',
                'id': str(booking.id),
                'service': booking.service.name,
                'status': booking.get_status_display(),
                'date': booking.scheduled_date.isoformat()
            }
            for booking in bookings
        ]
    
    elif role == 'vendor':
        # Get vendor's bookings
        bookings = Booking.objects.filter(vendor=user).order_by('-created_at')[:5]
        context['suggested_actions'] = [
            'Upload photos for service',
            'Request signature from customer',
            'View my calendar',
            'Check pending jobs'
        ]
        context['recent_activities'] = [
            {
                'type': 'booking',
                'id': str(booking.id),
                'service': booking.service.name,
                'status': booking.get_status_display(),
                'date': booking.scheduled_date.isoformat()
            }
            for booking in bookings
        ]
    
    elif role in ['admin', 'onboard_manager', 'ops_manager']:
        # Get pending vendors for onboard managers
        if role == 'onboard_manager':
            pending_vendors = User.objects.filter(role='vendor', is_verified=False)[:5]
            context['suggested_actions'] = [
                'Approve pending vendors',
                'Review vendor applications',
                'View vendor queue'
            ]
            context['recent_activities'] = [
                {
                    'type': 'vendor_application',
                    'id': str(vendor.id),
                    'name': vendor.get_full_name(),
                    'date': vendor.date_joined.isoformat()
                }
                for vendor in pending_vendors
            ]
        else:
            # For ops managers and admins
            pending_signatures = Signature.objects.filter(status='pending')[:5]
            context['suggested_actions'] = [
                'Monitor pending signatures',
                'Resolve customer disputes',
                'View system analytics'
            ]
            context['recent_activities'] = [
                {
                    'type': 'signature',
                    'id': str(signature.id),
                    'booking_id': str(signature.booking.id),
                    'customer': signature.booking.customer.get_full_name(),
                    'date': signature.requested_at.isoformat()
                }
                for signature in pending_signatures
            ]
    
    return context


# Workflow handlers for each role
def handle_customer_track_bookings(user):
    """Handle customer request to track bookings"""
    bookings = Booking.objects.filter(customer=user).order_by('-created_at')[:5]
    
    if not bookings:
        return "You don't have any bookings yet. Would you like to book a service?"
    
    response = "Here are your recent bookings:\n\n"
    for booking in bookings:
        response += f"• {booking.service.name} - {booking.get_status_display()}\n"
        response += f"  Scheduled for: {booking.scheduled_date.strftime('%Y-%m-%d %H:%M')}\n"
        response += f"  Booking ID: {booking.id}\n\n"
    
    return response


def handle_customer_approve_signature(user, message):
    """Handle customer request to approve signature"""
    # Extract booking ID from message if provided
    # In a real implementation, this would parse the message to find booking ID
    return "To approve a signature, please visit the 'My Bookings' page and click on 'Sign' for the completed service. You'll be asked to provide a satisfaction rating (1-5) and any comments."


def handle_customer_booking_details(user, message):
    """Handle customer request for booking details"""
    # Extract booking ID from message if provided
    return "To view booking details, please go to the 'My Bookings' page and click on any booking to see its details including service information, scheduled time, and status."


def handle_vendor_upload_photos(user, message):
    """Handle vendor request to upload photos"""
    return "To upload photos, go to the 'My Jobs' page, select a booking, and use the 'Upload Photos' option. You can upload 'before' and 'after' photos of your work."


def handle_vendor_request_signature(user, message):
    """Handle vendor request to request signature"""
    # Get completed bookings without signatures
    bookings = Booking.objects.filter(
        vendor=user, 
        status='completed'
    ).exclude(signature__isnull=False)[:3]
    
    if not bookings:
        return "You don't have any completed bookings that require signatures."
    
    response = "You can request signatures for these completed bookings:\n\n"
    for booking in bookings:
        response += f"• {booking.service.name} for {booking.customer.get_full_name()}\n"
        response += f"  Booking ID: {booking.id}\n"
        response += f"  Completed on: {booking.completion_date.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    response += "To request a signature, go to the booking details page and click 'Request Signature'."
    return response


def handle_vendor_calendar(user):
    """Handle vendor request to view calendar"""
    return "To view your calendar, go to the 'Calendar' page where you can see all your scheduled bookings and their statuses."


def handle_vendor_pending_jobs(user):
    """Handle vendor request to check pending jobs"""
    pending_bookings = Booking.objects.filter(
        vendor=user,
        status__in=['confirmed', 'in_progress']
    ).order_by('scheduled_date')
    
    if not pending_bookings:
        return "You don't have any pending jobs at the moment."
    
    response = "Your pending jobs:\n\n"
    for booking in pending_bookings:
        response += f"• {booking.service.name} for {booking.customer.get_full_name()}\n"
        response += f"  Status: {booking.get_status_display()}\n"
        response += f"  Scheduled for: {booking.scheduled_date.strftime('%Y-%m-%d %H:%M')}\n"
        response += f"  Booking ID: {booking.id}\n\n"
    
    return response


def handle_admin_approve_vendor(user, message):
    """Handle admin request to approve vendor"""
    pending_vendors = User.objects.filter(role='vendor', is_verified=False)[:5]
    
    if not pending_vendors:
        return "There are no pending vendor applications to approve."
    
    response = "Pending vendor applications:\n\n"
    for vendor in pending_vendors:
        response += f"• {vendor.get_full_name()} ({vendor.username})\n"
        response += f"  Email: {vendor.email}\n"
        response += f"  Phone: {vendor.phone}\n"
        response += f"  Joined: {vendor.date_joined.strftime('%Y-%m-%d')}\n\n"
    
    response += "To approve vendors, go to the 'Vendor Queue' page in the admin dashboard."
    return response


def handle_admin_monitor_signatures(user):
    """Handle admin request to monitor signatures"""
    pending_signatures = Signature.objects.filter(status='pending')[:5]
    
    if not pending_signatures:
        return "There are no pending signatures at the moment."
    
    response = "Pending signatures:\n\n"
    for signature in pending_signatures:
        response += f"• Booking: {signature.booking.service.name}\n"
        response += f"  Customer: {signature.booking.customer.get_full_name()}\n"
        response += f"  Vendor: {signature.booking.vendor.get_full_name() if signature.booking.vendor else 'N/A'}\n"
        response += f"  Requested: {signature.requested_at.strftime('%Y-%m-%d %H:%M')}\n"
        response += f"  Expires: {signature.expires_at.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    response += "To manage signatures, go to the 'Signature Vault' page in the operations dashboard."
    return response


def handle_admin_resolve_dispute(user, message):
    """Handle admin request to resolve dispute"""
    disputed_bookings = Booking.objects.filter(status='disputed')[:5]
    
    if not disputed_bookings:
        return "There are no disputed bookings at the moment."
    
    response = "Disputed bookings:\n\n"
    for booking in disputed_bookings:
        response += f"• {booking.service.name}\n"
        response += f"  Customer: {booking.customer.get_full_name()}\n"
        response += f"  Vendor: {booking.vendor.get_full_name() if booking.vendor else 'N/A'}\n"
        response += f"  Disputed on: {booking.updated_at.strftime('%Y-%m-%d %H:%M')}\n"
        response += f"  Booking ID: {booking.id}\n\n"
    
    response += "To resolve disputes, go to the 'Disputes' section in the admin dashboard."
    return response


"""
API Views for Vendor Onboarding and Dispute Resolution
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from .models import VendorApplication, VendorDocument, DisputeMessage
from .serializers import (
    VendorApplicationSerializer, VendorDocumentSerializer,
    VendorApplicationListSerializer, VendorDocumentUploadSerializer,
    DisputeSerializer, DisputeMessageSerializer, DisputeListSerializer,
    DisputeMessageListSerializer
)
from .vendor_onboarding_service import VendorOnboardingService
from .permissions import IsDisputeParty


class VendorApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for vendor application management"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'ai_flag']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['onboard_manager', 'super_admin']:
            queryset = VendorApplication.objects.all()
            
            # Filter by flagged applications if requested
            flagged_only = self.request.query_params.get('flagged_only', False)
            if flagged_only:
                queryset = queryset.filter(ai_flag=True)
                
            return queryset
        elif user.role == 'vendor':
            return VendorApplication.objects.filter(vendor=user)
        return VendorApplication.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return VendorApplicationListSerializer
        elif self.action in ['upload_document', 'review']:
            return VendorDocumentUploadSerializer
        return VendorApplicationSerializer

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

    def update(self, request, *args, **kwargs):
        """Override update to implement edit-only mode with audit logging"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Store old values for audit logging
        old_values = {}
        for field in request.data.keys():
            if hasattr(instance, field):
                old_values[field] = getattr(instance, field)
        
        # Perform the update
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Log the edit in audit logs
        new_values = {}
        for field in request.data.keys():
            if hasattr(instance, field):
                new_values[field] = getattr(instance, field)
        
        from .utils import AuditLogger
        AuditLogger.log_action(
            user=request.user,
            action='update',
            resource_type='VendorApplication',
            resource_id=str(instance.id),
            old_values=old_values,
            new_values=new_values,
            request=request
        )
        
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsVendor])
    def submit(self, request, pk=None):
        """Submit vendor application for review"""
        application = self.get_object()

        if application.vendor != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )

        result = VendorOnboardingService.submit_application(application.id, request.user)
        if result['success']:
            serializer = self.get_serializer(application)
            return Response(serializer.data)
        return Response(
            {'error': result.get('error', 'Submission failed')},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, (IsOnboardManager | IsSuperAdmin)])
    def review(self, request, pk=None):
        """Review and approve/reject vendor application"""
        application = self.get_object()
        reviewer = request.user
        decision = request.data.get('decision')  # 'approve' or 'reject'
        notes = request.data.get('notes', '')

        if decision not in ['approve', 'reject']:
            return Response(
                {'error': 'Invalid decision. Must be "approve" or "reject"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = VendorOnboardingService.review_application(
            application.id, reviewer, decision, notes
        )

        if result['success']:
            serializer = self.get_serializer(application)
            return Response(serializer.data)
        return Response(
            {'error': result.get('error', 'Review failed')},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsVendor])
    def upload_document(self, request, pk=None):
        """Upload document for vendor application"""
        application = self.get_object()

        if application.vendor != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )

        document_type = request.data.get('document_type')
        file = request.FILES.get('file')

        if not document_type or not file:
            return Response(
                {'error': 'document_type and file are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = VendorOnboardingService.upload_document(
            application.id, request.user, document_type, file
        )

        if result['success']:
            serializer = VendorDocumentSerializer(result['document'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'error': result.get('error', 'Upload failed')},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, (IsOnboardManager | IsSuperAdmin)])
    def flag_application(self, request, pk=None):
        """Manually flag an application as suspicious"""
        application = self.get_object()
        flag_reason = request.data.get('flag_reason', '')
        
        if not flag_reason:
            return Response(
                {'error': 'flag_reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Flag the application
        application.ai_flag = True
        application.flag_reason = flag_reason
        application.flagged_at = timezone.now()
        application.save()
        
        # Log the manual flag in audit logs
        from .utils import AuditLogger
        AuditLogger.log_action(
            user=request.user,
            action='vendor_application_flagged',
            resource_type='VendorApplication',
            resource_id=str(application.id),
            new_values={
                'ai_flag': True,
                'flag_reason': flag_reason,
                'manually_flagged': True
            }
        )
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, (IsOnboardManager | IsSuperAdmin)])
    def unflag_application(self, request, pk=None):
        """Remove flag from an application"""
        application = self.get_object()
        
        # Unflag the application
        application.ai_flag = False
        application.flag_reason = ''
        application.flagged_at = None
        application.save()
        
        # Log the unflag action in audit logs
        from .utils import AuditLogger
        AuditLogger.log_action(
            user=request.user,
            action='vendor_application_flagged',
            resource_type='VendorApplication',
            resource_id=str(application.id),
            new_values={
                'ai_flag': False,
                'flag_reason': '',
                'manually_unflagged': True
            }
        )
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, (IsOnboardManager | IsSuperAdmin)])
    def edit_history(self, request, pk=None):
        """Get edit history for a vendor application"""
        from .models import AuditLog
        
        # Get audit logs for this application
        audit_logs = AuditLog.objects.filter(
            resource_type='VendorApplication',
            resource_id=pk,
            action='update'
        ).order_by('-timestamp')
        
        # Serialize the audit logs
        from .serializers import AuditLogSerializer
        serializer = AuditLogSerializer(audit_logs, many=True)
        
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, (IsOnboardManager | IsSuperAdmin)])
    def signature_logs(self, request, pk=None):
        """Get signature logs for a vendor"""
        from .models import Signature, User
        
        try:
            # Get the vendor user
            vendor_app = self.get_object()
            if not vendor_app.vendor_account:
                return Response({'signatures': []})
                
            vendor_user = vendor_app.vendor_account
            
            # Get all signatures for this vendor
            signatures = Signature.objects.filter(
                booking__vendor=vendor_user
            ).select_related('booking', 'booking__customer').order_by('-requested_at')
            
            # Serialize the signatures
            from .serializers import SignatureSerializer
            serializer = SignatureSerializer(signatures, many=True)
            
            return Response({'signatures': serializer.data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VendorDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for vendor document management"""
    permission_classes = [IsAuthenticated]
    serializer_class = VendorDocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['onboard_manager', 'super_admin']:
            return VendorDocument.objects.all()
        elif user.role == 'vendor':
            return VendorDocument.objects.filter(application__vendor=user)
        return VendorDocument.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, (IsOnboardManager | IsSuperAdmin)])
    def verify(self, request, pk=None):
        """Verify or reject a vendor document"""
        document = self.get_object()
        reviewer = request.user
        is_verified = request.data.get('is_verified', False)
        rejection_reason = request.data.get('rejection_reason', '')

        result = VendorOnboardingService.verify_document(
            document.id, reviewer, is_verified, rejection_reason
        )

        if result['success']:
            serializer = self.get_serializer(document)
            return Response(serializer.data)
        return Response(
            {'error': result.get('error', 'Verification failed')},
            status=status.HTTP_400_BAD_REQUEST
        )


class DisputeViewSet(viewsets.ModelViewSet):
    """ViewSet for dispute management"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ops_manager', 'super_admin']:
            return Dispute.objects.all()
        elif user.role == 'vendor':
            return Dispute.objects.filter(
                Q(vendor=user) | Q(assigned_mediator=user)
            )
        elif user.role == 'customer':
            return Dispute.objects.filter(
                Q(customer=user) | Q(assigned_mediator=user)
            )
        return Dispute.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return DisputeListSerializer
        return DisputeSerializer

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsCustomer])
    def create_dispute(self, request):
        """Create a new dispute"""
        booking_id = request.data.get('booking_id')
        dispute_type = request.data.get('dispute_type')
        title = request.data.get('title')
        description = request.data.get('description')
        evidence = request.data.get('evidence', {})

        if not all([booking_id, dispute_type, title, description]):
            return Response(
                {'error': 'booking_id, dispute_type, title, and description are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            booking = Booking.objects.get(id=booking_id, customer=request.user)
        except Booking.DoesNotExist:
            return Response(
                {'error': 'Booking not found or unauthorized'},
                status=status.HTTP_404_NOT_FOUND
            )

        dispute = DisputeResolutionService.create_dispute(
            booking, request.user, dispute_type, title, description, evidence
        )

        if dispute:
            serializer = self.get_serializer(dispute)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'error': 'Failed to create dispute'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, (IsOpsManager | IsSuperAdmin)])
    def assign_mediator(self, request, pk=None):
        """Assign a mediator to a dispute"""
        dispute = self.get_object()
        mediator_id = request.data.get('mediator_id')

        if not mediator_id:
            return Response(
                {'error': 'mediator_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            mediator = User.objects.get(id=mediator_id, role__in=['ops_manager', 'super_admin'])
        except User.DoesNotExist:
            return Response(
                {'error': 'Mediator not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        result = DisputeResolutionService.assign_mediator(dispute.id, mediator)
        if result['success']:
            serializer = self.get_serializer(dispute)
            return Response(serializer.data)
        return Response(
            {'error': result.get('error', 'Assignment failed')},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsDisputeParty])
    def resolve(self, request, pk=None):
        """Resolve a dispute"""
        dispute = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        resolution_amount = request.data.get('resolution_amount')
        evidence = request.data.get('evidence', {})

        # Check if user can resolve this dispute
        user = request.user
        if user != dispute.assigned_mediator and user.role not in ['ops_manager', 'super_admin']:
            return Response(
                {'error': 'Unauthorized to resolve this dispute'},
                status=status.HTTP_403_FORBIDDEN
            )

        result = DisputeResolutionService.resolve_dispute(
            dispute.id, user, resolution_notes, resolution_amount, evidence
        )

        if result:
            serializer = self.get_serializer(dispute)
            return Response(serializer.data)
        return Response(
            {'error': 'Failed to resolve dispute'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, (IsOpsManager | IsSuperAdmin)])
    def escalate(self, request, pk=None):
        """Escalate a dispute"""
        dispute = self.get_object()
        escalated_to_id = request.data.get('escalated_to_id')
        reason = request.data.get('reason', '')

        if not escalated_to_id:
            return Response(
                {'error': 'escalated_to_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            escalated_to = User.objects.get(id=escalated_to_id, role__in=['ops_manager', 'super_admin'])
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        result = DisputeResolutionService.escalate_dispute(
            dispute.id, request.user, escalated_to, reason
        )

        if result:
            serializer = self.get_serializer(dispute)
            return Response(serializer.data)
        return Response(
            {'error': 'Failed to escalate dispute'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsDisputeParty])
    def messages(self, request, pk=None):
        """Get messages for a dispute"""
        dispute = self.get_object()
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))

        result = DisputeResolutionService.get_dispute_messages(
            dispute.id, request.user, page, page_size
        )

        if result['success']:
            serializer = DisputeMessageListSerializer(result['messages'], many=True)
            return Response({
                'messages': serializer.data,
                'total_count': result['total_count'],
                'page': result['page'],
                'page_size': result['page_size'],
                'has_more': result['has_more']
            })
        return Response(
            {'error': result.get('error', 'Failed to get messages')},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsDisputeParty])
    def send_message(self, request, pk=None):
        """Send a message in a dispute"""
        dispute = self.get_object()
        content = request.data.get('content')
        message_type = request.data.get('message_type', 'text')
        attachment = request.FILES.get('attachment')

        if not content and not attachment:
            return Response(
                {'error': 'content or attachment is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = DisputeResolutionService.send_message(
            dispute.id, request.user, content, message_type, attachment
        )

        if result['success']:
            serializer = DisputeMessageSerializer(result['message'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'error': result.get('error', 'Failed to send message')},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsDisputeParty])
    def mark_read(self, request, pk=None):
        """Mark messages as read"""
        dispute = self.get_object()

        result = DisputeResolutionService.mark_messages_read(dispute.id, request.user)

        if result['success']:
            return Response({
                'marked_count': result['marked_count']
            })
        return Response(
            {'error': result.get('error', 'Failed to mark messages as read')},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, (IsOpsManager | IsSuperAdmin)])
def dispute_analytics(request):
    """Get dispute analytics"""
    date_range_days = int(request.query_params.get('days', 30))

    analytics = DisputeResolutionService.get_dispute_analytics(date_range_days)
    return Response(analytics)


@api_view(['GET'])
@permission_classes([IsAuthenticated, (IsOnboardManager | IsSuperAdmin)])
def vendor_onboarding_analytics(request):
    """Get vendor onboarding analytics"""
    analytics = VendorOnboardingService.get_onboarding_analytics()
    return Response(analytics)


def generate_ai_response(message, role):
    """Generate AI-like response for general queries"""
    # This is a simple rule-based response generator
    # In a real implementation, this would connect to an AI service
    
    responses = {
        'hello': 'Hello! How can I help you today?',
        'hi': 'Hi there! What can I assist you with?',
        'help': 'I can help you with various tasks based on your role. Try asking about your bookings, service completion, or signature approvals.',
        'thanks': 'You\'re welcome! Is there anything else I can help you with?',
        'thank you': 'You\'re welcome! Let me know if you need any further assistance.'
    }
    
    message_lower = message.lower()
    for key, response in responses.items():
        if key in message_lower:
            return response
    
    # Default response
    role_prompts = {
        'customer': 'As a customer, you can ask me about your bookings, service completion, or signature approvals.',
        'vendor': 'As a vendor, you can ask me about your jobs, uploading photos, requesting signatures, or viewing your calendar.',
        'admin': 'As an admin, you can ask me about vendor approvals, monitoring signatures, or resolving disputes.',
        'onboard_manager': 'As an onboard manager, you can ask me about vendor applications or approval processes.',
        'ops_manager': 'As an operations manager, you can ask me about monitoring signatures, payments, or system analytics.'
    }
    
    return f"I understand you're asking about '{message}'. {role_prompts.get(role, 'I can help with various tasks in the system.')}"


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_default']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Address.objects.filter(user=user)
        elif user.role in ['ops_manager', 'super_admin']:
            return Address.objects.all()
        return Address.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[IsCustomer])
    def set_default(self, request, pk=None):
        """Set this address as the default address"""
        address = self.get_object()
        if address.user != request.user:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Set this address as default
        address.is_default = True
        address.save()
        
        # Unset other addresses as default
        Address.objects.filter(user=request.user, is_default=True).exclude(id=address.id).update(is_default=False)
        
        return Response({'message': 'Default address updated successfully'})


class EarningsViewSet(viewsets.ModelViewSet):
    queryset = Earnings.objects.all()
    serializer_class = EarningsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'vendor']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'vendor':
            return Earnings.objects.filter(vendor=user)
        elif user.role in ['ops_manager', 'super_admin']:
            return Earnings.objects.all()
        return Earnings.objects.none()
    
    @action(detail=True, methods=['post'], permission_classes=[IsOpsManager | IsSuperAdmin])
    def release_payment(self, request, pk=None):
        """Release payment to vendor"""
        earning = self.get_object()
        
        # Update earning status
        earning.status = 'released'
        earning.processed_by = request.user
        earning.processed_at = timezone.now()
        earning.save()
        
        # Update booking payment status
        if hasattr(earning.booking, 'payment'):
            earning.booking.payment.status = 'completed'
            earning.booking.payment.processed_by = request.user
            earning.booking.payment.processed_at = timezone.now()
            earning.booking.payment.save()
        
        # Log the action
        AuditLogger.log_action(
            user=request.user,
            action='payment_process',
            resource_type='Earnings',
            resource_id=earning.id,
            new_values={'status': 'released'}
        )
        
        return Response({
            'message': 'Payment released successfully',
            'earning_id': earning.id
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsVendor])
    def summary(self, request):
        """Get earnings summary for vendor"""
        vendor = request.user
        
        # Calculate total earnings
        from django.db.models import Sum
        total_earnings = Earnings.objects.filter(
            vendor=vendor, 
            status='released'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate pending earnings
        pending_earnings = Earnings.objects.filter(
            vendor=vendor, 
            status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get recent earnings
        recent_earnings = Earnings.objects.filter(vendor=vendor)[:5]
        
        serializer = EarningsSerializer(recent_earnings, many=True)
        
        return Response({
            'total_earnings': float(total_earnings),
            'pending_earnings': float(pending_earnings),
            'recent_earnings': serializer.data
        })


class PerformanceMetricsViewSet(viewsets.ModelViewSet):
    queryset = PerformanceMetrics.objects.all()
    serializer_class = PerformanceMetricsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tier', 'vendor']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'vendor':
            return PerformanceMetrics.objects.filter(vendor=user)
        elif user.role in ['ops_manager', 'super_admin']:
            return PerformanceMetrics.objects.all()
        return PerformanceMetrics.objects.none()
    
    @action(detail=False, methods=['get'], permission_classes=[IsVendor])
    def summary(self, request):
        """Get performance summary for vendor"""
        vendor = request.user
        
        # Get or create performance metrics
        metrics, created = PerformanceMetrics.objects.get_or_create(vendor=vendor)
        
        serializer = PerformanceMetricsSerializer(metrics)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsOpsManager | IsSuperAdmin])
    def calculate_all(self, request):
        """Calculate performance metrics for all vendors"""
        # This would be called by a cron job or manually
        vendors = User.objects.filter(role='vendor')
        
        for vendor in vendors:
            # Get or create performance metrics
            metrics, created = PerformanceMetrics.objects.get_or_create(vendor=vendor)
            
            # Recalculate bonus points
            metrics.calculate_bonus_points()
            metrics.save()
        
        return Response({
            'message': f'Performance metrics calculated for {vendors.count()} vendors'
        })


class VendorSearchAPIView(APIView):
    """Search vendors by pincode with availability and ratings"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Search vendors by pincode"""
        pincode = request.query_params.get('pincode')
        service_id = request.query_params.get('service_id')
        
        if not pincode:
            return Response(
                {'error': 'Pincode parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get available vendors in the pincode
            vendors = User.objects.filter(
                role='vendor',
                pincode=pincode,
                is_available=True,
                is_verified=True,
                is_active=True
            )
            
            # Filter by service if provided
            if service_id:
                try:
                    service = Service.objects.get(id=service_id)
                    # Filter vendors by checking if they have this service in their application
                    # Use a more flexible matching approach
                    vendor_applications = VendorApplication.objects.filter(
                        status='approved'
                    ).filter(
                        Q(service_category__icontains=service.name) |
                        Q(service_category__icontains=service.category) |
                        Q(service_category=service.name) |
                        Q(service_category=service.category)
                    ).values_list('vendor_account_id', flat=True)
                    vendors = vendors.filter(id__in=vendor_applications)
                except Service.DoesNotExist:
                    pass
            
            # Get vendor availability and ratings
            vendor_data = []
            for vendor in vendors:
                # Get vendor availability
                availability = VendorAvailability.objects.filter(
                    vendor=vendor,
                    is_active=True
                ).first()
                
                # Get vendor rating (mock for now, would be from completed bookings)
                # In a real implementation, this would be calculated from signature ratings
                rating = 4.5  # Mock rating
                
                # Get travel time from vendor's location to customer
                customer_pincode = request.user.pincode
                travel_data = {}
                if customer_pincode:
                    try:
                        travel_data = travel_service.get_travel_time(
                            vendor.pincode or (availability.primary_pincode if availability else pincode),
                            customer_pincode
                        )
                    except:
                        travel_data = {'duration_minutes': 30, 'distance_km': 10}
                
                vendor_data.append({
                    'id': vendor.id,
                    'name': vendor.get_full_name(),
                    'email': vendor.email,
                    'phone': vendor.phone,
                    'pincode': vendor.pincode,
                    'rating': rating,
                    'total_jobs': 25,  # Mock data
                    'availability': {
                        'day_of_week': availability.day_of_week if availability else None,
                        'start_time': availability.start_time if availability else None,
                        'end_time': availability.end_time if availability else None,
                    } if availability else None,
                    'travel_time': travel_data.get('duration_minutes', 30),
                    'distance_km': travel_data.get('distance_km', 10),
                    'primary_service_area': availability.primary_pincode if availability else pincode
                })
            
            # Sort by rating and travel time
            vendor_data.sort(key=lambda x: (-x['rating'], x['travel_time']))
            
            return Response({
                'vendors': vendor_data,
                'total_vendors': len(vendor_data),
                'pincode': pincode,
                'demand_index': self._calculate_demand_index(pincode)
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _calculate_demand_index(self, pincode):
        """Calculate demand index for a pincode"""
        try:
            from datetime import timedelta
            
            # Get analytics for the last 7 days
            week_ago = timezone.now().date() - timedelta(days=7)
            analytics = PincodeAnalytics.objects.filter(
                pincode=pincode,
                date__gte=week_ago
            )
            
            if analytics.exists():
                total_bookings = sum(a.total_bookings for a in analytics)
                available_vendors = sum(a.available_vendors for a in analytics) / len(analytics)
                
                if available_vendors > 0:
                    demand_ratio = total_bookings / available_vendors
                    # Normalize to 0-10 scale
                    return min(10, round(demand_ratio, 1))
            
            return 5  # Neutral demand index
        except:
            return 5  # Default demand index


# Advanced AI and ML Features API Endpoints

class PincodeAIAnalyticsAPIView(APIView):
    """Pincode Pulse Engine AI analytics endpoint"""
    permission_classes = [IsAuthenticated, (IsOpsManager | IsSuperAdmin)]
    
    def get(self, request):
        """Get AI-powered pincode analytics"""
        pincode = request.query_params.get('pincode')
        analysis_period = int(request.query_params.get('days', 30))
        
        if not pincode:
            return Response(
                {'error': 'pincode parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Use the Pincode AI Engine
            result = analyze_pincode_pulse(pincode, analysis_period)
            
            return Response({
                'status': 'success',
                'pincode_analysis': result,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Pincode AI analysis failed: {str(e)}")
            return Response(
                {'error': 'Failed to analyze pincode', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdvancedDisputeResolutionAPIView(APIView):
    """Advanced dispute resolution with AI suggestions"""
    permission_classes = [IsAuthenticated, (IsOpsManager | IsSuperAdmin)]
    
    def get(self, request, dispute_id):
        """Get AI-powered dispute resolution suggestions"""
        try:
            dispute = Dispute.objects.get(id=dispute_id)
            
            # Generate auto-resolution analysis
            resolution_analysis = AdvancedDisputeService.auto_resolve_disputes(dispute)
            
            # Generate escalation matrix
            escalation_analysis = AdvancedDisputeService.escalation_matrix(dispute)
            
            return Response({
                'status': 'success',
                'dispute_id': str(dispute.id),
                'resolution_analysis': resolution_analysis,
                'escalation_analysis': escalation_analysis,
                'timestamp': timezone.now().isoformat()
            })
            
        except Dispute.DoesNotExist:
            return Response(
                {'error': 'Dispute not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Dispute resolution analysis failed: {str(e)}")
            return Response(
                {'error': 'Failed to analyze dispute', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdvancedVendorBonusAPIView(APIView):
    """Advanced vendor bonus calculation with ML analytics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get ML-powered vendor bonus analysis"""
        vendor_id = request.query_params.get('vendor_id')
        analysis_period = int(request.query_params.get('days', 30))
        
        # Determine vendor based on role and parameters
        if request.user.role == 'vendor':
            vendor = request.user
        elif request.user.role in ['ops_manager', 'super_admin'] and vendor_id:
            try:
                vendor = User.objects.get(id=vendor_id, role='vendor')
            except User.DoesNotExist:
                return Response(
                    {'error': 'Vendor not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {'error': 'Unauthorized or missing vendor_id'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Use the Advanced Vendor Bonus Service
            result = AdvancedVendorBonusService.calculate_performance_bonuses(vendor, analysis_period)
            
            return Response({
                'status': 'success',
                'vendor_bonus_analysis': result,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Advanced vendor bonus analysis failed: {str(e)}")
            return Response(
                {'error': 'Failed to analyze vendor bonuses', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@csrf_exempt
@require_http_methods(["POST"])
def docusign_webhook(request):
    """Handle DocuSign webhook events"""
    try:
        # Get the payload
        payload = json.loads(request.body)
        
        # Handle the webhook event through the signature service
        result = SignatureService.handle_docusign_webhook(payload)
        
        if result:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to process webhook'}, status=400)
            
    except Exception as e:
        logger.error(f"Error processing DocuSign webhook: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)