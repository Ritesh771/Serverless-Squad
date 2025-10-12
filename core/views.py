from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import User, Service, Booking, Photo, Signature, Payment, AuditLog
from .serializers import (
    UserSerializer, ServiceSerializer, BookingSerializer,
    PhotoSerializer, SignatureSerializer, PaymentSerializer, AuditLogSerializer
)
from .permissions import (
    IsCustomer, IsVendor, IsOnboardManager, IsOpsManager, 
    IsSuperAdmin, IsAdminUser, IsOwnerOrAdmin
)
from .utils import AuditLogger
from .payment_service import PaymentService
from .signature_service import SignatureService


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
            serializer.save(customer=self.request.user)
        AuditLogger.log_action(
            user=self.request.user,
            action='create',
            resource_type='Booking',
            resource_id=serializer.instance.id,
            request=self.request
        )
    
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