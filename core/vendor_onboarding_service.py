from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import VendorApplication, VendorDocument, User, AuditLog
from .notification_service import NotificationService
from .vendor_ai_service import vendor_ai_service
from .utils import AuditLogger
import logging

logger = logging.getLogger(__name__)


class VendorOnboardingService:
    """Service for managing vendor onboarding applications"""

    
    def create_application(applicant_data, applicant):
        """Create a new vendor application"""
        try:
            # Check if user already has an application
            existing_app = VendorApplication.objects.filter(
                applicant=applicant,
                status__in=['draft', 'submitted', 'under_review', 'additional_info_required']
            ).first()

            if existing_app:
                return {
                    'success': False,
                    'error': 'You already have a pending application',
                    'application': existing_app
                }

            application = VendorApplication.objects.create(
                applicant=applicant,
                **applicant_data
            )

            # Run AI analysis on the application
            ai_result = vendor_ai_service.analyze_vendor_application(application)
            
            if ai_result.get('should_flag', False):
                application.ai_flag = True
                application.flag_reason = '; '.join(ai_result.get('flag_reasons', []))
                application.flagged_at = timezone.now()
                application.save()
                
                # Log the AI flag in audit logs
                AuditLogger.log_action(
                    user=None,  # System action
                    action='vendor_application_flagged',
                    resource_type='VendorApplication',
                    resource_id=str(application.id),
                    new_values={
                        'ai_flag': True,
                        'flag_reason': application.flag_reason,
                        'risk_score': ai_result.get('risk_score', 0)
                    }
                )

            logger.info(f"Vendor application created for user {applicant.username}")
            return {
                'success': True,
                'application': application
            }

        except Exception as e:
            logger.error(f"Failed to create vendor application: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    
    def submit_application(application_id, applicant):
        """Submit an application for review"""
        try:
            application = VendorApplication.objects.get(
                id=application_id,
                applicant=applicant
            )

            if application.status != 'draft':
                return {
                    'success': False,
                    'error': 'Application is not in draft status'
                }

            # Check if application is complete
            if not application.is_complete():
                return {
                    'success': False,
                    'error': 'Application is incomplete. Please upload all required documents.'
                }

            application.submit_application()

            # Send notification to onboard managers
            VendorOnboardingService._notify_onboard_managers(application)

            return {
                'success': True,
                'application': application
            }

        except VendorApplication.DoesNotExist:
            return {
                'success': False,
                'error': 'Application not found'
            }
        except Exception as e:
            logger.error(f"Failed to submit vendor application: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    
    def upload_document(application_id, document_data, uploaded_by):
        """Upload a document for an application"""
        try:
            application = VendorApplication.objects.get(id=application_id)

            # Check permissions
            if uploaded_by != application.applicant and uploaded_by.role not in ['onboard_manager', 'super_admin']:
                return {
                    'success': False,
                    'error': 'Unauthorized to upload documents for this application'
                }

            # Check if document type already exists
            existing_doc = VendorDocument.objects.filter(
                application=application,
                document_type=document_data['document_type']
            ).first()

            if existing_doc:
                # Delete old file
                if existing_doc.document_file:
                    existing_doc.document_file.delete()

                # Update existing document
                for key, value in document_data.items():
                    setattr(existing_doc, key, value)
                existing_doc.status = 'pending'  # Reset status for re-review
                existing_doc.uploaded_by = uploaded_by
                existing_doc.save()

                document = existing_doc
            else:
                # Create new document
                document_data['application'] = application
                document_data['uploaded_by'] = uploaded_by
                document = VendorDocument.objects.create(**document_data)

            logger.info(f"Document uploaded: {document.document_name} for application {application_id}")
            return {
                'success': True,
                'document': document
            }

        except VendorApplication.DoesNotExist:
            return {
                'success': False,
                'error': 'Application not found'
            }
        except Exception as e:
            logger.error(f"Failed to upload document: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    
    def review_application(application_id, reviewer, status, review_notes='', rejection_reason=''):
        """Review a vendor application"""
        try:
            application = VendorApplication.objects.get(id=application_id)

            # Check permissions
            if reviewer.role not in ['onboard_manager', 'super_admin']:
                return {
                    'success': False,
                    'error': 'Unauthorized to review applications'
                }

            application.review_application(reviewer, status, review_notes, rejection_reason)

            # Send notification to applicant
            VendorOnboardingService._notify_applicant(application)

            return {
                'success': True,
                'application': application
            }

        except VendorApplication.DoesNotExist:
            return {
                'success': False,
                'error': 'Application not found'
            }
        except Exception as e:
            logger.error(f"Failed to review application: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    
    def review_document(document_id, reviewer, status, review_notes='', rejection_reason=''):
        """Review a vendor document"""
        try:
            document = VendorDocument.objects.get(id=document_id)

            # Check permissions
            if reviewer.role not in ['onboard_manager', 'super_admin']:
                return {
                    'success': False,
                    'error': 'Unauthorized to review documents'
                }

            document.review_document(reviewer, status, review_notes, rejection_reason)

            # Check if application is now complete
            application = document.application
            if application.is_complete() and application.status == 'additional_info_required':
                application.status = 'under_review'
                application.save()

            return {
                'success': True,
                'document': document
            }

        except VendorDocument.DoesNotExist:
            return {
                'success': False,
                'error': 'Document not found'
            }
        except Exception as e:
            logger.error(f"Failed to review document: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    
    def get_application_stats():
        """Get application statistics for dashboard"""
        stats = {
            'total_applications': VendorApplication.objects.count(),
            'pending_review': VendorApplication.objects.filter(status='submitted').count(),
            'under_review': VendorApplication.objects.filter(status='under_review').count(),
            'additional_info_required': VendorApplication.objects.filter(status='additional_info_required').count(),
            'approved': VendorApplication.objects.filter(status='approved').count(),
            'rejected': VendorApplication.objects.filter(status='rejected').count(),
            'completion_rate': 0
        }

        # Calculate completion rate
        total_submitted = stats['pending_review'] + stats['under_review'] + stats['additional_info_required'] + stats['approved'] + stats['rejected']
        if total_submitted > 0:
            completed = stats['approved'] + stats['rejected']
            stats['completion_rate'] = round((completed / total_submitted) * 100, 2)

        return stats

    
    def _notify_onboard_managers(application):
        """Notify onboard managers about new application"""
        try:
            onboard_managers = User.objects.filter(
                role='onboard_manager',
                is_active=True
            )

            subject = f"New Vendor Application: {application.full_name}"
            message = f"""
            A new vendor application has been submitted by {application.full_name}.

            Application Type: {application.get_application_type_display()}
            Primary Service: {application.primary_service_category}
            Location: {application.city}, {application.state}

            Please review the application and required documents.
            """

            for manager in onboard_managers:
                NotificationService.send_notification(
                    recipient=manager,
                    notification_type='vendor_application_submitted',
                    subject=subject,
                    message=message,
                    metadata={
                        'application_id': str(application.id),
                        'applicant_name': application.full_name
                    }
                )

        except Exception as e:
            logger.error(f"Failed to notify onboard managers: {str(e)}")

    
    def _notify_applicant(application):
        """Notify applicant about application status change"""
        try:
            status_messages = {
                'approved': f"Congratulations! Your vendor application has been approved. You can now start accepting bookings.",
                'rejected': f"Your vendor application has been rejected. Reason: {application.rejection_reason}",
                'additional_info_required': "Your vendor application requires additional information. Please check your dashboard for details."
            }

            subject = f"Vendor Application Update: {application.get_status_display()}"
            message = status_messages.get(application.status, f"Your application status has been updated to: {application.get_status_display()}")

            if application.review_notes:
                message += f"\n\nReview Notes: {application.review_notes}"

            NotificationService.send_notification(
                recipient=application.applicant,
                notification_type='vendor_application_reviewed',
                subject=subject,
                message=message,
                metadata={
                    'application_id': str(application.id),
                    'status': application.status
                }
            )

        except Exception as e:
            logger.error(f"Failed to notify applicant: {str(e)}")


