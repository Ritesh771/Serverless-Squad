import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Booking, Signature
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class BookingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            logger.info(f"BookingConsumer connect called with scope: {self.scope}")
            self.booking_id = self.scope['url_route']['kwargs']['booking_id']
            self.booking_group_name = f'booking_{self.booking_id}'
            
            # Join booking group
            await self.channel_layer.group_add(
                self.booking_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"BookingConsumer connected for booking {self.booking_id}")
        except Exception as e:
            logger.error(f"Error in booking consumer connect: {str(e)}")
            await self.close()
    
    async def disconnect(self, close_code):
        # Leave booking group
        await self.channel_layer.group_discard(
            self.booking_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        # Handle incoming messages if needed
        pass
    
    async def booking_status_update(self, event):
        """Send booking status update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'booking_id': event['booking_id'],
            'status': event['status'],
            'timestamp': event['timestamp'],
            'message': event['message']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            logger.info(f"NotificationConsumer connect called with scope: {self.scope}")
            self.user_id = self.scope['url_route']['kwargs']['user_id']
            self.user_group_name = f'user_{self.user_id}'
            
            # Join user group
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"NotificationConsumer connected for user {self.user_id}")
        except Exception as e:
            logger.error(f"Error in notification consumer connect: {str(e)}")
            await self.close()
    
    async def disconnect(self, close_code):
        # Leave user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def user_notification(self, event):
        """Send notification to user WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_type': event['notification_type'],
            'data': event['data'],
            'timestamp': event['timestamp']
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            logger.info(f"ChatConsumer connect called with scope: {self.scope}")
            self.user_id = self.scope['url_route']['kwargs']['user_id']
            self.role = self.scope['url_route']['kwargs'].get('role', 'customer')
            self.chat_group_name = f'chat_{self.user_id}'
            
            # Join chat group
            await self.channel_layer.group_add(
                self.chat_group_name,
                self.channel_name
            )
            
            # Also join role-based group for admin notifications
            self.role_group_name = f'role_{self.role}'
            await self.channel_layer.group_add(
                self.role_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"ChatConsumer connected for user {self.user_id} with role {self.role}")
        except Exception as e:
            logger.error(f"Error in chat consumer connect: {str(e)}")
            await self.close()
    
    async def disconnect(self, close_code):
        # Leave chat group
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )
        
        # Leave role group
        await self.channel_layer.group_discard(
            self.role_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')
        message_data = text_data_json.get('data', {})
        
        if message_type == 'user_message':
            # Handle user message
            await self.handle_user_message(message_data)
        elif message_type == 'workflow_event':
            # Handle workflow event
            await self.handle_workflow_event(message_data)
    
    async def handle_user_message(self, message_data):
        # Process user message and send response
        response = await self.process_message(message_data)
        
        # Send response back to the user
        await self.send(text_data=json.dumps({
            'type': 'bot_response',
            'data': response
        }))
    
    async def handle_workflow_event(self, message_data):
        # Handle workflow events like signature requests, booking approvals, etc.
        event_type = message_data.get('event_type')
        user_id = message_data.get('user_id')
        role = message_data.get('role')
        
        try:
            user = await database_sync_to_async(User.objects.get)(id=user_id)
        except User.DoesNotExist:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'data': {'message': 'User not found'}
            }))
            return
        
        # Log workflow action
        try:
            from .utils import AuditLogger
            from django.contrib.auth.models import AnonymousUser
            
            # Log the action
            await database_sync_to_async(AuditLogger.log_action)(
                user=user,
                action=f'chat_{event_type}',
                resource_type='Chat',
                resource_id='chat_workflow',
                new_values=message_data
            )
        except Exception as e:
            logger.error(f"Error logging chat workflow action: {str(e)}")
        
        # Send notification to relevant users
        if event_type == 'signature_requested':
            await self.handle_signature_requested(message_data, user)
        elif event_type == 'signature_completed':
            await self.handle_signature_completed(message_data, user)
        elif event_type == 'booking_approved':
            await self.handle_booking_approved(message_data, user)
        elif event_type == 'vendor_approved':
            await self.handle_vendor_approved(message_data, user)
        elif event_type == 'track_bookings':
            await self.handle_track_bookings(message_data, user, role)
        elif event_type == 'upload_photos':
            await self.handle_upload_photos(message_data, user)
        elif event_type == 'request_signature':
            await self.handle_request_signature(message_data, user)
        elif event_type == 'approve_vendor':
            await self.handle_approve_vendor(message_data, user)
        elif event_type == 'monitor_signatures':
            await self.handle_monitor_signatures(message_data, user)
    
    async def handle_signature_requested(self, message_data, user):
        # Notify customer about signature request
        customer_id = message_data.get('customer_id')
        if customer_id:
            await self.channel_layer.group_send(
                f'chat_{customer_id}',
                {
                    'type': 'chat_notification',
                    'notification_type': 'signature_requested',
                    'data': message_data
                }
            )
    
    async def handle_signature_completed(self, message_data, user):
        # Notify vendor and admin about completed signature
        vendor_id = message_data.get('vendor_id')
        booking_id = message_data.get('booking_id')
        
        if vendor_id:
            await self.channel_layer.group_send(
                f'chat_{vendor_id}',
                {
                    'type': 'chat_notification',
                    'notification_type': 'signature_completed',
                    'data': message_data
                }
            )
        
        # Also notify ops managers
        await self.channel_layer.group_send(
            'role_ops_manager',
            {
                'type': 'chat_notification',
                'notification_type': 'signature_completed',
                'data': message_data
            }
        )
    
    async def handle_booking_approved(self, message_data, user):
        # Notify relevant parties about booking approval
        vendor_id = message_data.get('vendor_id')
        customer_id = message_data.get('customer_id')
        
        if vendor_id:
            await self.channel_layer.group_send(
                f'chat_{vendor_id}',
                {
                    'type': 'chat_notification',
                    'notification_type': 'booking_approved',
                    'data': message_data
                }
            )
        
        if customer_id:
            await self.channel_layer.group_send(
                f'chat_{customer_id}',
                {
                    'type': 'chat_notification',
                    'notification_type': 'booking_approved',
                    'data': message_data
                }
            )
    
    async def handle_vendor_approved(self, message_data, user):
        # Notify vendor about approval
        vendor_id = message_data.get('vendor_id')
        if vendor_id:
            await self.channel_layer.group_send(
                f'chat_{vendor_id}',
                {
                    'type': 'chat_notification',
                    'notification_type': 'vendor_approved',
                    'data': message_data
                }
            )
    
    async def handle_track_bookings(self, message_data, user, role):
        if role == 'customer':
            # Get customer's bookings
            bookings = await database_sync_to_async(list)(
                Booking.objects.filter(customer=user).order_by('-created_at')[:5]
            )
            
            response_text = "Here are your recent bookings:\n\n"
            if bookings:
                for booking in bookings:
                    response_text += f"• {booking.service.name} - {booking.get_status_display()}\n"
                    response_text += f"  Scheduled for: {booking.scheduled_date.strftime('%Y-%m-%d %H:%M')}\n"
                    response_text += f"  Booking ID: {booking.id}\n\n"
            else:
                response_text = "You don't have any bookings yet."
            
            await self.send(text_data=json.dumps({
                'type': 'bot_response',
                'data': {
                    'message': response_text,
                    'timestamp': message_data.get('timestamp')
                }
            }))
    
    async def handle_upload_photos(self, message_data, user):
        response_text = "To upload photos, go to the 'My Jobs' page, select a booking, and use the 'Upload Photos' option. You can upload 'before' and 'after' photos of your work."
        
        await self.send(text_data=json.dumps({
            'type': 'bot_response',
            'data': {
                'message': response_text,
                'timestamp': message_data.get('timestamp')
            }
        }))
    
    async def handle_request_signature(self, message_data, user):
        # Get completed bookings without signatures for this vendor
        bookings = await database_sync_to_async(list)(
            Booking.objects.filter(
                vendor=user, 
                status='completed'
            ).exclude(signature__isnull=False)[:3]
        )
        
        if not bookings:
            response_text = "You don't have any completed bookings that require signatures."
        else:
            response_text = "You can request signatures for these completed bookings:\n\n"
            for booking in bookings:
                response_text += f"• {booking.service.name} for {booking.customer.get_full_name()}\n"
                response_text += f"  Booking ID: {booking.id}\n"
                response_text += f"  Completed on: {booking.completion_date.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            response_text += "To request a signature, go to the booking details page and click 'Request Signature'."
        
        await self.send(text_data=json.dumps({
            'type': 'bot_response',
            'data': {
                'message': response_text,
                'timestamp': message_data.get('timestamp')
            }
        }))
    
    async def handle_approve_vendor(self, message_data, user):
        # Get pending vendors (only for admin/onboard roles)
        if user.role in ['admin', 'onboard_manager']:
            pending_vendors = await database_sync_to_async(list)(
                User.objects.filter(role='vendor', is_verified=False)[:5]
            )
            
            if not pending_vendors:
                response_text = "There are no pending vendor applications to approve."
            else:
                response_text = "Pending vendor applications:\n\n"
                for vendor in pending_vendors:
                    response_text += f"• {vendor.get_full_name()} ({vendor.username})\n"
                    response_text += f"  Email: {vendor.email}\n"
                    response_text += f"  Phone: {vendor.phone}\n"
                    response_text += f"  Joined: {vendor.date_joined.strftime('%Y-%m-%d')}\n\n"
                
                response_text += "To approve vendors, go to the 'Vendor Queue' page in the admin dashboard."
        else:
            response_text = "You don't have permission to approve vendors."
        
        await self.send(text_data=json.dumps({
            'type': 'bot_response',
            'data': {
                'message': response_text,
                'timestamp': message_data.get('timestamp')
            }
        }))
    
    async def handle_monitor_signatures(self, message_data, user):
        # Get pending signatures (only for admin/ops roles)
        if user.role in ['admin', 'ops_manager']:
            pending_signatures = await database_sync_to_async(list)(
                Signature.objects.filter(status='pending')[:5]
            )
            
            if not pending_signatures:
                response_text = "There are no pending signatures at the moment."
            else:
                response_text = "Pending signatures:\n\n"
                for signature in pending_signatures:
                    response_text += f"• Booking: {signature.booking.service.name}\n"
                    response_text += f"  Customer: {signature.booking.customer.get_full_name()}\n"
                    response_text += f"  Vendor: {signature.booking.vendor.get_full_name() if signature.booking.vendor else 'N/A'}\n"
                    response_text += f"  Requested: {signature.requested_at.strftime('%Y-%m-%d %H:%M')}\n"
                    response_text += f"  Expires: {signature.expires_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                
                response_text += "To manage signatures, go to the 'Signature Vault' page in the operations dashboard."
        else:
            response_text = "You don't have permission to monitor signatures."
        
        await self.send(text_data=json.dumps({
            'type': 'bot_response',
            'data': {
                'message': response_text,
                'timestamp': message_data.get('timestamp')
            }
        }))
    
    async def process_message(self, message_data):
        # This would integrate with the chat processing logic
        # For now, return a simple response
        return {
            'message': f"Received your message: {message_data.get('text', '')}",
            'timestamp': message_data.get('timestamp', '')
        }
    
    async def chat_notification(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_type': event['notification_type'],
            'data': event['data']
        }))


class LiveStatusConsumer(AsyncWebsocketConsumer):
    """Dedicated consumer for live booking status tracking"""
    
    async def connect(self):
        try:
            logger.info(f"LiveStatusConsumer connect called with scope: {self.scope}")
            self.user_id = self.scope['url_route']['kwargs']['user_id']
            self.role = self.scope['url_route']['kwargs'].get('role', 'customer')
            
            # For development, we'll be more permissive with authentication
            # In production, you should properly validate authentication
            user_authenticated = False
            if "user" in self.scope and self.scope["user"].is_authenticated:
                user_authenticated = True
                # Validate user ID matches authenticated user (for non-admin roles)
                if str(self.scope['user'].id) != str(self.user_id) and self.scope['user'].role not in ['admin', 'ops_manager']:
                    logger.warning(f"LiveStatusConsumer: User {self.scope['user'].id} attempted to connect as user {self.user_id}")
                    await self.close(code=4002)
                    return
            else:
                # For development, allow unauthenticated connections but log a warning
                logger.warning("LiveStatusConsumer: Unauthenticated connection attempt - allowing for development")
                user_authenticated = True  # Allow for development
            
            # Accept connection first
            await self.accept()
            logger.info(f"LiveStatusConsumer accepted connection for user {self.user_id} with role {self.role}")
            
            # Try to join groups - fail gracefully if channel layer not available
            try:
                # Join user-specific group for status updates
                self.user_status_group = f'status_user_{self.user_id}'
                await self.channel_layer.group_add(
                    self.user_status_group,
                    self.channel_name
                )
                
                # Join role-based group for bulk notifications
                self.role_status_group = f'status_role_{self.role}'
                await self.channel_layer.group_add(
                    self.role_status_group,
                    self.channel_name
                )
                logger.info(f"LiveStatusConsumer joined groups for user {self.user_id}")
            except Exception as e:
                logger.warning(f"Channel layer not available or error joining groups: {str(e)}, WebSocket will work in direct mode")
                
            # Send connection confirmation
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Connected to live status updates',
                'user_id': str(self.user_id),
                'role': self.role
            }))
        except Exception as e:
            logger.error(f"Error in live status consumer connect: {str(e)}")
            await self.close(code=4000)
    
    async def disconnect(self, close_code):
        try:
            # Leave user group
            await self.channel_layer.group_discard(
                self.user_status_group,
                self.channel_name
            )
        except Exception:
            pass  # Ignore errors if channel layer is not available
            
        try:
            # Leave role group
            await self.channel_layer.group_discard(
                self.role_status_group,
                self.channel_name
            )
        except Exception:
            pass  # Ignore errors if channel layer is not available
            
        logger.info(f"LiveStatusConsumer disconnected for user {self.user_id} with code {close_code}")
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_to_booking':
                await self.subscribe_to_booking(data.get('booking_id'))
            elif message_type == 'unsubscribe_from_booking':
                await self.unsubscribe_from_booking(data.get('booking_id'))
            else:
                # Echo unknown messages back to client for debugging
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}',
                    'received_data': data
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing message in LiveStatusConsumer: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error processing message: {str(e)}'
            }))
    
    async def subscribe_to_booking(self, booking_id):
        """Subscribe to status updates for a specific booking"""
        if booking_id:
            try:
                booking_group = f'status_booking_{booking_id}'
                await self.channel_layer.group_add(
                    booking_group,
                    self.channel_name
                )
                
                # Send confirmation
                await self.send(text_data=json.dumps({
                    'type': 'subscription_confirmed',
                    'booking_id': booking_id,
                    'message': f'Subscribed to status updates for booking {booking_id}'
                }))
            except Exception as e:
                logger.error(f"Error subscribing to booking {booking_id}: {str(e)}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Failed to subscribe to booking {booking_id}: {str(e)}'
                }))
    
    async def unsubscribe_from_booking(self, booking_id):
        """Unsubscribe from status updates for a specific booking"""
        if booking_id:
            try:
                booking_group = f'status_booking_{booking_id}'
                await self.channel_layer.group_discard(
                    booking_group,
                    self.channel_name
                )
                
                # Send confirmation
                await self.send(text_data=json.dumps({
                    'type': 'unsubscription_confirmed',
                    'booking_id': booking_id,
                    'message': f'Unsubscribed from status updates for booking {booking_id}'
                }))
            except Exception as e:
                logger.error(f"Error unsubscribing from booking {booking_id}: {str(e)}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Failed to unsubscribe from booking {booking_id}: {str(e)}'
                }))
    
    async def booking_status_update(self, event):
        """Send booking status update to WebSocket"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'booking_status_update',
                'booking_id': event['booking_id'],
                'status': event['status'],
                'previous_status': event.get('previous_status'),
                'timestamp': event['timestamp'],
                'message': event['message'],
                'eta_minutes': event.get('eta_minutes'),
                'vendor_location': event.get('vendor_location')
            }))
        except Exception as e:
            logger.error(f"Error sending booking status update: {str(e)}")
    
    async def booking_eta_update(self, event):
        """Send ETA update to WebSocket"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'booking_eta_update',
                'booking_id': event['booking_id'],
                'eta_minutes': event['eta_minutes'],
                'timestamp': event['timestamp'],
                'message': event['message']
            }))
        except Exception as e:
            logger.error(f"Error sending booking ETA update: {str(e)}")