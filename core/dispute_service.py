from django.utils import timezone
from django.db.models import Q
from django.utils import timezone
from .models import Dispute, Booking, User, Signature, BusinessAlert, DisputeMessage
from .utils import AuditLogger
from .notification_service import NotificationService
import logging
import uuid
from datetime import timedelta
from typing import Dict, List, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class AdvancedDisputeService:
    """
    Enhanced dispute resolution with AI-powered suggestions and smart escalation
    """
    
    @staticmethod
    def auto_resolve_disputes(dispute):
        """
        AI-powered dispute resolution suggestions
        Currently rule-based, ready for ML enhancement
        """
        try:
            # Get dispute context
            context = AdvancedDisputeService._analyze_dispute_context(dispute)
            
            # Generate resolution suggestions
            suggestions = AdvancedDisputeService._generate_resolution_suggestions(dispute, context)
            
            # Check if auto-resolution is possible
            auto_resolution = AdvancedDisputeService._check_auto_resolution_eligibility(dispute, context)
            
            result = {
                'dispute_id': str(dispute.id),
                'context_analysis': context,
                'resolution_suggestions': suggestions,
                'auto_resolution': auto_resolution,
                'confidence_score': AdvancedDisputeService._calculate_confidence_score(dispute, suggestions),
                'generated_at': timezone.now().isoformat()
            }
            
            logger.info(f"Auto-resolution analysis completed for dispute {dispute.id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze dispute {dispute.id}: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def escalation_matrix(dispute):
        """
        Smart escalation based on severity, type, and context
        """
        try:
            escalation_rules = {
                'immediate_escalation': [],
                'escalate_in_24h': [],
                'escalate_in_48h': [],
                'no_escalation_needed': []
            }
            
            # Check immediate escalation conditions
            if dispute.severity == 'critical':
                escalation_rules['immediate_escalation'].append({
                    'reason': 'Critical severity level',
                    'escalate_to': 'super_admin',
                    'action': 'Immediate attention required'
                })
            
            if dispute.dispute_type == 'payment_issue' and hasattr(dispute.booking, 'payment'):
                payment_amount = float(dispute.booking.payment.amount)
                if payment_amount > 5000:  # High-value disputes
                    escalation_rules['immediate_escalation'].append({
                        'reason': f'High-value payment dispute (₹{payment_amount})',
                        'escalate_to': 'super_admin',
                        'action': 'Finance team involvement required'
                    })
            
            # Check vendor performance history
            vendor_history = AdvancedDisputeService._get_vendor_dispute_history(dispute.vendor)
            if vendor_history['dispute_rate'] > 15:  # More than 15% dispute rate
                escalation_rules['escalate_in_24h'].append({
                    'reason': f'Vendor has high dispute rate ({vendor_history["dispute_rate"]}%)',
                    'escalate_to': 'ops_manager',
                    'action': 'Vendor performance review required'
                })
            
            # Check resolution timeline
            dispute_age_hours = (timezone.now() - dispute.created_at).total_seconds() / 3600
            if dispute_age_hours > 48 and dispute.status == 'investigating':
                escalation_rules['escalate_in_24h'].append({
                    'reason': 'Dispute unresolved for >48 hours',
                    'escalate_to': 'ops_manager',
                    'action': 'Priority resolution required'
                })
            
            # Customer satisfaction impact
            if dispute.dispute_type in ['service_quality', 'vendor_behavior']:
                escalation_rules['escalate_in_48h'].append({
                    'reason': 'Customer satisfaction impact',
                    'escalate_to': 'ops_manager',
                    'action': 'Quality assurance review'
                })
            
            # If no escalation needed
            if not any(escalation_rules[key] for key in ['immediate_escalation', 'escalate_in_24h', 'escalate_in_48h']):
                escalation_rules['no_escalation_needed'].append({
                    'reason': 'Standard dispute resolution process adequate',
                    'action': 'Continue with assigned mediator'
                })
            
            return {
                'dispute_id': str(dispute.id),
                'escalation_matrix': escalation_rules,
                'recommended_action': AdvancedDisputeService._get_recommended_escalation_action(escalation_rules),
                'analysis_timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate escalation matrix for dispute {dispute.id}: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def _analyze_dispute_context(dispute):
        """Analyze dispute context for resolution suggestions"""
        context = {
            'dispute_type': dispute.dispute_type,
            'severity': dispute.severity,
            'booking_value': float(dispute.booking.total_price),
            'service_type': dispute.booking.service.name,
            'vendor_experience': AdvancedDisputeService._get_vendor_experience(dispute.vendor),
            'customer_history': AdvancedDisputeService._get_customer_history(dispute.customer),
            'has_photos': bool(dispute.booking.photos.exists()),
            'signature_status': getattr(dispute.booking, 'signature', None) and dispute.booking.signature.status or 'none'
        }
        
        return context
    
    @staticmethod
    def _generate_resolution_suggestions(dispute, context):
        """Generate smart resolution suggestions based on context"""
        suggestions = []
        
        # Service quality disputes
        if dispute.dispute_type == 'service_quality':
            if context['has_photos']:
                suggestions.append({
                    'type': 'evidence_review',
                    'suggestion': 'Review before/after photos for service quality assessment',
                    'priority': 'high',
                    'estimated_resolution_time': '2-4 hours'
                })
            
            if context['booking_value'] < 1000:
                suggestions.append({
                    'type': 'partial_refund',
                    'suggestion': f'Consider 25-50% refund (₹{context["booking_value"] * 0.25:.0f}-{context["booking_value"] * 0.5:.0f})',
                    'priority': 'medium',
                    'estimated_resolution_time': '1-2 hours'
                })
            else:
                suggestions.append({
                    'type': 'service_redo',
                    'suggestion': 'Offer free service redo with different vendor',
                    'priority': 'high',
                    'estimated_resolution_time': '4-8 hours'
                })
        
        # Payment disputes
        elif dispute.dispute_type == 'payment_issue':
            suggestions.append({
                'type': 'payment_verification',
                'suggestion': 'Verify payment processing logs and Stripe records',
                'priority': 'critical',
                'estimated_resolution_time': '1-2 hours'
            })
            
            if context['signature_status'] != 'signed':
                suggestions.append({
                    'type': 'signature_review',
                    'suggestion': 'Payment hold justified - signature not completed',
                    'priority': 'high',
                    'estimated_resolution_time': '30 minutes'
                })
        
        # Vendor behavior disputes
        elif dispute.dispute_type == 'vendor_behavior':
            vendor_exp = context['vendor_experience']
            if vendor_exp['total_jobs'] < 10:
                suggestions.append({
                    'type': 'vendor_training',
                    'suggestion': 'New vendor - provide additional training and monitoring',
                    'priority': 'medium',
                    'estimated_resolution_time': '2-4 hours'
                })
            
            suggestions.append({
                'type': 'compensation',
                'suggestion': f'Provide service credit of ₹{context["booking_value"] * 0.5:.0f}',
                'priority': 'medium',
                'estimated_resolution_time': '1-2 hours'
            })
        
        return suggestions
    
    @staticmethod
    def _check_auto_resolution_eligibility(dispute, context):
        """Check if dispute can be auto-resolved"""
        auto_resolution = {
            'eligible': False,
            'reason': 'Manual review required',
            'suggested_action': None
        }
        
        # Low-value, simple disputes can be auto-resolved
        if (context['booking_value'] < 500 and 
            dispute.dispute_type in ['booking_cancellation'] and
            dispute.severity in ['low', 'medium']):
            
            auto_resolution = {
                'eligible': True,
                'reason': 'Low-value, simple dispute eligible for auto-resolution',
                'suggested_action': {
                    'action': 'full_refund',
                    'amount': context['booking_value'],
                    'message': 'Automatic refund processed for booking cancellation'
                }
            }
        
        return auto_resolution
    
    @staticmethod
    def _calculate_confidence_score(dispute, suggestions):
        """Calculate confidence score for resolution suggestions"""
        base_score = 70
        
        # Increase confidence based on available evidence
        if hasattr(dispute.booking, 'photos') and dispute.booking.photos.exists():
            base_score += 10
        
        if dispute.customer_evidence:
            base_score += 10
        
        if dispute.vendor_evidence:
            base_score += 10
        
        # Decrease confidence for complex disputes
        if dispute.severity == 'critical':
            base_score -= 15
        
        if dispute.dispute_type in ['payment_issue', 'vendor_behavior']:
            base_score -= 10
        
        return min(95, max(30, base_score))
    
    @staticmethod
    def _get_vendor_dispute_history(vendor):
        """Get vendor's dispute history for analysis"""
        if not vendor:
            return {'total_jobs': 0, 'disputes': 0, 'dispute_rate': 0}
        
        from django.apps import apps
        Booking = apps.get_model('core', 'Booking')
        Dispute = apps.get_model('core', 'Dispute')
        
        total_jobs = Booking.objects.filter(vendor=vendor, status__in=['completed', 'signed']).count()
        disputes = Dispute.objects.filter(vendor=vendor).count()
        
        dispute_rate = (disputes / total_jobs * 100) if total_jobs > 0 else 0
        
        return {
            'total_jobs': total_jobs,
            'disputes': disputes,
            'dispute_rate': round(dispute_rate, 2)
        }
    
    @staticmethod
    def _get_vendor_experience(vendor):
        """Get vendor experience metrics"""
        if not vendor:
            return {'total_jobs': 0, 'completion_rate': 0, 'avg_rating': 0}
        
        from django.apps import apps
        Booking = apps.get_model('core', 'Booking')
        
        total_jobs = Booking.objects.filter(vendor=vendor).count()
        completed_jobs = Booking.objects.filter(vendor=vendor, status__in=['completed', 'signed']).count()
        
        completion_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Get average rating (simplified)
        avg_rating = 4.2  # Placeholder - would calculate from signatures
        
        return {
            'total_jobs': total_jobs,
            'completion_rate': round(completion_rate, 2),
            'avg_rating': avg_rating
        }
    
    @staticmethod
    def _get_customer_history(customer):
        """Get customer booking history"""
        from django.apps import apps
        Booking = apps.get_model('core', 'Booking')
        
        total_bookings = Booking.objects.filter(customer=customer).count()
        completed_bookings = Booking.objects.filter(customer=customer, status__in=['completed', 'signed']).count()
        
        return {
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'is_frequent_customer': total_bookings > 5
        }
    
    @staticmethod
    def _get_recommended_escalation_action(escalation_rules):
        """Get the most urgent escalation action"""
        if escalation_rules['immediate_escalation']:
            return {
                'urgency': 'immediate',
                'action': escalation_rules['immediate_escalation'][0],
                'timeline': 'Now'
            }
        elif escalation_rules['escalate_in_24h']:
            return {
                'urgency': 'high',
                'action': escalation_rules['escalate_in_24h'][0],
                'timeline': 'Within 24 hours'
            }
        elif escalation_rules['escalate_in_48h']:
            return {
                'urgency': 'medium',
                'action': escalation_rules['escalate_in_48h'][0],
                'timeline': 'Within 48 hours'
            }
        else:
            return {
                'urgency': 'low',
                'action': escalation_rules['no_escalation_needed'][0],
                'timeline': 'No escalation needed'
            }


class DisputeResolutionService:
    """Service for handling disputes and conflicts"""
    
    @staticmethod
    def create_dispute(booking, customer, dispute_type, title, description, evidence=None):
        """
        Create a new dispute for a booking
        
        Args:
            booking: Booking object
            customer: Customer user object
            dispute_type: Type of dispute
            title: Dispute title
            description: Dispute description
            evidence: Customer evidence (photos, documents)
        """
        try:
            # Check if dispute already exists for this booking
            existing_dispute = Dispute.objects.filter(
                booking=booking,
                status__in=['open', 'investigating', 'mediation']
            ).first()
            
            if existing_dispute:
                logger.warning(f"Dispute already exists for booking {booking.id}")
                return existing_dispute
            
            # Determine severity based on dispute type
            severity_mapping = {
                'service_quality': 'high',
                'payment_issue': 'critical',
                'signature_refusal': 'high',
                'vendor_behavior': 'medium',
                'customer_behavior': 'medium',
                'booking_cancellation': 'low',
                'other': 'medium'
            }
            
            severity = severity_mapping.get(dispute_type, 'medium')
            
            # Create dispute
            dispute = Dispute.objects.create(
                booking=booking,
                customer=customer,
                vendor=booking.vendor,
                dispute_type=dispute_type,
                title=title,
                description=description,
                customer_evidence=evidence,
                severity=severity
            )
            
            # Update booking status
            booking.status = 'disputed'
            booking.save()
            
            # Create initial system message
            DisputeResolutionService._create_system_message(
                dispute,
                f"Dispute created by {customer.get_full_name()}: {title}"
            )
            
            # Create business alert
            alert_data = {
                'dispute_id': str(dispute.id),
                'booking_id': str(booking.id),
                'dispute_type': dispute_type,
                'customer': customer.get_full_name(),
                'vendor': booking.vendor.get_full_name() if booking.vendor else 'N/A',
                'severity': severity
            }
            
            BusinessAlert.objects.create(
                alert_type='dispute_created',
                severity=severity,
                title=f"New Dispute: {title}",
                description=f"Customer {customer.get_full_name()} created a dispute for booking {booking.id}",
                related_booking=booking,
                metadata=alert_data
            )
            
            # Auto-assign mediator based on dispute type and severity
            mediator = DisputeResolutionService._auto_assign_mediator(dispute)
            if mediator:
                dispute.assign_mediator(mediator)
            
            # Send notifications
            DisputeResolutionService._send_dispute_notifications(dispute, 'created')
            
            # Log audit trail
            AuditLogger.log_action(
                user=customer,
                action='dispute_created',
                resource_type='Dispute',
                resource_id=str(dispute.id),
                new_values={'dispute_type': dispute_type, 'title': title}
            )
            
            logger.info(f"Dispute created: {dispute.id} for booking {booking.id}")
            return dispute
            
        except Exception as e:
            logger.error(f"Failed to create dispute: {str(e)}")
            return None
    
    @staticmethod
    def _auto_assign_mediator(dispute):
        """Auto-assign appropriate mediator based on dispute type and severity"""
        try:
            # Get available mediators (ops managers and super admins)
            mediators = User.objects.filter(
                role__in=['ops_manager', 'super_admin'],
                is_active=True
            )
            
            if not mediators.exists():
                return None
            
            # Priority assignment logic
            if dispute.severity in ['critical', 'high']:
                # Assign to super admin first for critical/high severity
                super_admin = mediators.filter(role='super_admin').first()
                if super_admin:
                    return super_admin
            
            # Assign to ops manager with least active disputes
            ops_managers = mediators.filter(role='ops_manager')
            if ops_managers.exists():
                # Find ops manager with least active disputes
                least_busy_manager = None
                min_disputes = float('inf')
                
                for manager in ops_managers:
                    active_disputes = Dispute.objects.filter(
                        assigned_mediator=manager,
                        status__in=['investigating', 'mediation']
                    ).count()
                    
                    if active_disputes < min_disputes:
                        min_disputes = active_disputes
                        least_busy_manager = manager
                
                return least_busy_manager
            
            # Fallback to any available mediator
            return mediators.first()
            
        except Exception as e:
            logger.error(f"Failed to auto-assign mediator: {str(e)}")
            return None
    
    @staticmethod
    def add_vendor_response(dispute_id, vendor, evidence=None, response_notes=""):
        """Add vendor response to dispute"""
        try:
            dispute = Dispute.objects.get(id=dispute_id, vendor=vendor)
            
            # Update vendor evidence
            dispute.vendor_evidence = evidence
            
            # Add response to resolution notes
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            vendor_response = f"\n[{timestamp}] Vendor Response:\n{response_notes}\n"
            dispute.resolution_notes += vendor_response
            
            dispute.save()
            
            # Send notification to mediator
            if dispute.assigned_mediator:
                DisputeResolutionService._send_dispute_notifications(dispute, 'vendor_responded')
            
            logger.info(f"Vendor response added to dispute {dispute_id}")
            return True
            
        except Dispute.DoesNotExist:
            logger.error(f"Dispute {dispute_id} not found or unauthorized")
            return False
        except Exception as e:
            logger.error(f"Failed to add vendor response: {str(e)}")
            return False
    
    @staticmethod
    def resolve_dispute(dispute_id, mediator, resolution_notes, resolution_amount=None, evidence=None):
        """Resolve a dispute with mediator decision"""
        try:
            dispute = Dispute.objects.get(id=dispute_id, assigned_mediator=mediator)
            
            # Resolve the dispute
            dispute.resolve(resolution_notes, resolution_amount, evidence)
            
            # Create system message
            DisputeResolutionService._create_system_message(
                dispute,
                f"Dispute resolved by {mediator.get_full_name()}"
            )
            
            # Handle payment if resolution amount is specified
            if resolution_amount and resolution_amount > 0:
                DisputeResolutionService._process_dispute_payment(dispute, resolution_amount)
            
            # Send resolution notifications
            DisputeResolutionService._send_dispute_notifications(dispute, 'resolved')
            
            # Log audit trail
            AuditLogger.log_action(
                user=mediator,
                action='dispute_resolved',
                resource_type='Dispute',
                resource_id=str(dispute.id),
                new_values={'resolution_notes': resolution_notes, 'amount': resolution_amount}
            )
            
            logger.info(f"Dispute {dispute_id} resolved by {mediator.username}")
            return True
            
        except Dispute.DoesNotExist:
            logger.error(f"Dispute {dispute_id} not found or unauthorized")
            return False
        except Exception as e:
            logger.error(f"Failed to resolve dispute: {str(e)}")
            return False
    
    @staticmethod
    def escalate_dispute(dispute_id, escalated_by, escalated_to, reason):
        """Escalate dispute to higher authority"""
        try:
            dispute = Dispute.objects.get(id=dispute_id)
            
            # Check authorization
            if escalated_by.role not in ['ops_manager', 'super_admin']:
                return False
            
            dispute.escalate(escalated_to, reason)
            
            # Create system message
            DisputeResolutionService._create_system_message(
                dispute,
                f"Dispute escalated to {escalated_to.get_full_name()}: {reason}"
            )
            
            # Send escalation notifications
            DisputeResolutionService._send_dispute_notifications(dispute, 'escalated')
            
            # Log audit trail
            AuditLogger.log_action(
                user=escalated_by,
                action='dispute_escalated',
                resource_type='Dispute',
                resource_id=str(dispute.id),
                new_values={'escalated_to': escalated_to.username, 'reason': reason}
            )
            
            logger.info(f"Dispute {dispute_id} escalated to {escalated_to.username}")
            return True
            
        except Dispute.DoesNotExist:
            logger.error(f"Dispute {dispute_id} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to escalate dispute: {str(e)}")
            return False
    
    @staticmethod
    def _process_dispute_payment(dispute, amount):
        """Process refund/compensation payment for dispute resolution"""
        try:
            # This would integrate with payment service for actual refund processing
            # For now, we'll create a payment record
            from .models import Payment
            
            payment = Payment.objects.create(
                booking=dispute.booking,
                amount=amount,
                status='processing',
                payment_type='manual',
                processed_by=dispute.assigned_mediator
            )
            
            # In a real implementation, this would call Stripe refund API
            payment.status = 'completed'
            payment.processed_at = timezone.now()
            payment.save()
            
            logger.info(f"Dispute resolution payment processed: ₹{amount} for dispute {dispute.id}")
            
        except Exception as e:
            logger.error(f"Failed to process dispute payment: {str(e)}")
    
    @staticmethod
    def _send_dispute_notifications(dispute, event_type):
        """Send notifications for dispute events"""
        try:
            participants = [dispute.customer]
            if dispute.vendor:
                participants.append(dispute.vendor)
            if dispute.assigned_mediator:
                participants.append(dispute.assigned_mediator)
            
            subject_mapping = {
                'created': f'Dispute Created: {dispute.title}',
                'assigned': f'Dispute Assigned: {dispute.title}',
                'vendor_responded': f'Vendor Response: {dispute.title}',
                'resolved': f'Dispute Resolved: {dispute.title}',
                'escalated': f'Dispute Escalated: {dispute.title}'
            }
            
            subject = subject_mapping.get(event_type, f'Dispute Update: {dispute.title}')
            
            for participant in participants:
                try:
                    # Create personalized message based on role
                    if participant == dispute.customer:
                        role_context = "as the customer who raised this dispute"
                    elif participant == dispute.vendor:
                        role_context = "as the vendor involved in this dispute"
                    else:
                        role_context = "as the assigned mediator"
                    
                    message = f"""
                    Hello {participant.get_full_name()},
                    
                    There has been an update to dispute {dispute.id} {role_context}.
                    
                    Dispute Details:
                    - Title: {dispute.title}
                    - Type: {dispute.get_dispute_type_display()}
                    - Status: {dispute.get_status_display()}
                    - Booking: {dispute.booking.id}
                    
                    Event: {event_type.replace('_', ' ').title()}
                    
                    Please log in to your dashboard to view more details.
                    
                    Best regards,
                    HomeServe Pro Team
                    """
                    
                    # Send email notification
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[participant.email],
                        fail_silently=True
                    )
                    
                except Exception as participant_error:
                    logger.error(f"Failed to send dispute notification to {participant.email}: {str(participant_error)}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to send dispute notifications: {str(e)}")
    
    @staticmethod
    def send_message(dispute_id, sender, content, message_type='text', attachment=None, recipient=None):
        """Send a message in a dispute"""
        try:
            dispute = Dispute.objects.get(id=dispute_id)

            # Check permissions
            if sender not in [dispute.customer, dispute.vendor, dispute.assigned_mediator] and \
               sender.role not in ['ops_manager', 'super_admin']:
                return {
                    'success': False,
                    'error': 'Unauthorized to send messages in this dispute'
                }

            # Determine recipient
            if not recipient:
                if sender == dispute.customer:
                    recipient = dispute.vendor or dispute.assigned_mediator
                elif sender == dispute.vendor:
                    recipient = dispute.customer or dispute.assigned_mediator
                else:
                    # Mediator/admin sending message
                    recipient = dispute.customer if dispute.customer != sender else dispute.vendor

            message = DisputeMessage.objects.create(
                dispute=dispute,
                sender=sender,
                recipient=recipient,
                message_type=message_type,
                content=content,
                attachment=attachment
            )

            # Mark dispute as active if it was resolved
            if dispute.status == 'resolved':
                dispute.status = 'open'
                dispute.save()

            # Send real-time notification
            DisputeResolutionService._notify_message_sent(message)

            return {
                'success': True,
                'message': message
            }

        except Dispute.DoesNotExist:
            return {
                'success': False,
                'error': 'Dispute not found'
            }
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def mark_messages_read(dispute_id, user):
        """Mark all unread messages in a dispute as read for a user"""
        try:
            dispute = Dispute.objects.get(id=dispute_id)

            # Check if user is party to this dispute
            if user not in [dispute.customer, dispute.vendor, dispute.assigned_mediator] and \
               user.role not in ['ops_manager', 'super_admin']:
                return {
                    'success': False,
                    'error': 'Unauthorized to view this dispute'
                }

            unread_messages = DisputeMessage.objects.filter(
                dispute=dispute,
                recipient=user,
                is_read=False
            )

            for message in unread_messages:
                message.mark_as_read(user)

            return {
                'success': True,
                'marked_count': unread_messages.count()
            }

        except Dispute.DoesNotExist:
            return {
                'success': False,
                'error': 'Dispute not found'
            }
        except Exception as e:
            logger.error(f"Failed to mark messages as read: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_dispute_messages(dispute_id, user, page=1, page_size=50):
        """Get paginated messages for a dispute"""
        try:
            dispute = Dispute.objects.get(id=dispute_id)

            # Check permissions
            if user not in [dispute.customer, dispute.vendor, dispute.assigned_mediator] and \
               user.role not in ['ops_manager', 'super_admin']:
                return {
                    'success': False,
                    'error': 'Unauthorized to view this dispute'
                }

            messages = DisputeMessage.objects.filter(dispute=dispute).order_by('-created_at')

            # Pagination
            start = (page - 1) * page_size
            end = start + page_size
            paginated_messages = messages[start:end]

            return {
                'success': True,
                'messages': list(paginated_messages),
                'total_count': messages.count(),
                'page': page,
                'page_size': page_size,
                'has_more': messages.count() > end
            }

        except Dispute.DoesNotExist:
            return {
                'success': False,
                'error': 'Dispute not found'
            }
        except Exception as e:
            logger.error(f"Failed to get dispute messages: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def _create_system_message(dispute, content):
        """Create a system message in the dispute"""
        try:
            DisputeMessage.objects.create(
                dispute=dispute,
                sender=None,  # System messages have no sender
                message_type='system',
                content=content
            )
        except Exception as e:
            logger.error(f"Failed to create system message: {str(e)}")

    @staticmethod
    def _notify_message_sent(message):
        """Send real-time notification about new message"""
        try:
            if message.recipient:
                NotificationService.send_notification(
                    recipient=message.recipient,
                    notification_type='dispute_message',
                    subject=f"New message in dispute: {message.dispute.title}",
                    message=f"You have received a new message in dispute #{message.dispute.id}",
                    metadata={
                        'dispute_id': str(message.dispute.id),
                        'message_id': str(message.id),
                        'sender_name': message.sender.get_full_name() if message.sender else 'System'
                    }
                )
        except Exception as e:
            logger.error(f"Failed to notify message: {str(e)}")


# Singleton instance
dispute_service = DisputeResolutionService()