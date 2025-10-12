from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.db import transaction
from django.conf import settings
from .models import User
from .utils import OTPService, AuditLogger
from .notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view with role-based response"""
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                response.data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_verified': user.is_verified,
                }
                
                AuditLogger.log_action(
                    user=user, action='login', resource_type='User',
                    resource_id=user.id, request=request
                )
                
            except User.DoesNotExist:
                pass
        
        return response


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """Send OTP to phone number or email"""
    identifier = request.data.get('phone') or request.data.get('email')
    method = request.data.get('method', getattr(settings, 'OTP_METHOD', 'email'))  # Default to email
    
    if not identifier:
        return Response({'error': 'Phone number or email is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Determine method based on identifier if not specified
    if '@' in identifier and method not in ['sms', 'email']:
        method = 'email'
    elif method not in ['sms', 'email']:
        method = getattr(settings, 'OTP_METHOD', 'email')
    
    try:
        # Find user by phone or email
        if method == 'email':
            user = User.objects.get(email=identifier)
        else:
            user = User.objects.get(phone=identifier)
            
        # Send OTP using the notification service
        otp_result = NotificationService.send_and_store_otp(
            identifier=identifier,
            method=method,
            user_name=user.get_full_name()
        )
        
        if otp_result['success']:
            return Response({
                'message': f'OTP sent successfully via {method}',
                'method': method,
                'otp_sent': otp_result['otp_sent'],
                'otp': otp_result.get('otp')  # DEBUG only
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': f'Failed to send OTP via {method}',
                'method': method
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except User.DoesNotExist:
        # Create user if not exists (for registration flow)
        if request.data.get('create_user', False):
            try:
                with transaction.atomic():
                    user_data = {
                        'username': request.data.get('username', identifier.split('@')[0] if '@' in identifier else identifier),
                        'email': identifier if '@' in identifier else '',
                        'phone': identifier if '@' not in identifier else '',
                        'role': 'customer'
                    }
                    user = User.objects.create(**user_data)
                    
                    # Send OTP using the notification service
                    otp_result = NotificationService.send_and_store_otp(
                        identifier=identifier,
                        method=method,
                        user_name=user.get_full_name()
                    )
                    
                    if otp_result['success']:
                        return Response({
                            'message': f'User created and OTP sent successfully via {method}',
                            'method': method,
                            'otp_sent': otp_result['otp_sent'],
                            'otp': otp_result.get('otp')  # DEBUG only
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            'error': f'Failed to send OTP via {method}',
                            'method': method
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({'error': f'Failed to create user: {str(e)}'}, 
                               status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'User not found'}, 
                           status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP and activate user"""
    identifier = request.data.get('phone') or request.data.get('email')
    otp = request.data.get('otp')
    
    if not identifier or not otp:
        return Response({'error': 'Phone/Email and OTP required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find user by phone or email
        if '@' in identifier:
            user = User.objects.get(email=identifier)
        else:
            user = User.objects.get(phone=identifier)
        
        if NotificationService.verify_otp(identifier, otp):
            user.is_verified = True
            user.save()
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'OTP verified successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_verified': user.is_verified,
                }
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid OTP'}, 
                       status=status.HTTP_400_BAD_REQUEST)
            
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, 
                       status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_vendor_otp(request):
    """Send OTP to vendor phone number or email"""
    identifier = request.data.get('phone') or request.data.get('email')
    method = request.data.get('method', getattr(settings, 'OTP_METHOD', 'email'))  # Default to email
    
    if not identifier:
        return Response({'error': 'Phone number or email is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Determine method based on identifier if not specified
    if '@' in identifier and method not in ['sms', 'email']:
        method = 'email'
    elif method not in ['sms', 'email']:
        method = getattr(settings, 'OTP_METHOD', 'sms')
    
    try:
        # Find vendor user by phone or email
        if method == 'email':
            user = User.objects.get(email=identifier, role='vendor')
        else:
            user = User.objects.get(phone=identifier, role='vendor')
            
        # Send OTP using the notification service
        otp_result = NotificationService.send_and_store_otp(
            identifier=identifier,
            method=method,
            user_name=user.get_full_name()
        )
        
        if otp_result['success']:
            return Response({
                'message': f'OTP sent successfully via {method}',
                'method': method,
                'otp_sent': otp_result['otp_sent'],
                'otp': otp_result.get('otp')  # DEBUG only
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': f'Failed to send OTP via {method}',
                'method': method
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except User.DoesNotExist:
        return Response({'error': 'Vendor user not found'}, 
                       status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_vendor_otp(request):
    """Verify vendor OTP and login"""
    identifier = request.data.get('phone') or request.data.get('email')
    otp = request.data.get('otp')
    
    if not identifier or not otp:
        return Response({'error': 'Phone/Email and OTP required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find vendor user by phone or email
        if '@' in identifier:
            user = User.objects.get(email=identifier, role='vendor')
        else:
            user = User.objects.get(phone=identifier, role='vendor')
        
        if NotificationService.verify_otp(identifier, otp):
            user.is_verified = True
            user.save()
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'OTP verified successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_verified': user.is_verified,
                }
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid OTP'}, 
                       status=status.HTTP_400_BAD_REQUEST)
            
    except User.DoesNotExist:
        return Response({'error': 'Vendor user not found'}, 
                       status=status.HTTP_404_NOT_FOUND)