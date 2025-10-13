import base64
import json
from django.conf import settings
from django.utils import timezone
from .models import Signature, Booking
import logging

logger = logging.getLogger(__name__)

try:
    from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs, Recipients
    DOCUSIGN_AVAILABLE = True
except ImportError:
    DOCUSIGN_AVAILABLE = False
    logger.warning("DocuSign SDK not available. Install docusign-esign to enable DocuSign integration.")


class DocuSignService:
    """Service for handling DocuSign integration"""
    
    def __init__(self):
        if not DOCUSIGN_AVAILABLE:
            raise Exception("DocuSign SDK not available. Please install docusign-esign package.")
            
        self.client_id = getattr(settings, 'DOCUSIGN_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'DOCUSIGN_CLIENT_SECRET', '')
        self.account_id = getattr(settings, 'DOCUSIGN_ACCOUNT_ID', '')
        self.base_path = getattr(settings, 'DOCUSIGN_BASE_PATH', 'https://demo.docusign.net/restapi')
        self.redirect_uri = getattr(settings, 'DOCUSIGN_REDIRECT_URI', 'http://localhost:3000/callback')
        
        # Check if required settings are available
        if not all([self.client_id, self.client_secret, self.account_id]):
            raise Exception("DocuSign configuration is incomplete. Please check your environment variables.")
    
    def create_signature_envelope(self, booking, customer_email, customer_name):
        """
        Create a DocuSign envelope for service satisfaction confirmation
        """
        try:
            # Create envelope definition
            envelope_definition = EnvelopeDefinition(
                email_subject=f"Service Satisfaction Confirmation - Booking {booking.id}"
            )
            
            # Generate document content
            document_content = self._generate_document_content(booking)
            
            # Add document to envelope
            document = Document(
                document_base64=base64.b64encode(document_content.encode('utf-8')).decode('ascii'),
                name="Service Satisfaction Confirmation",
                file_extension="pdf",
                document_id="1"
            )
            envelope_definition.documents = [document]
            
            # Add signer
            signer = Signer(
                email=customer_email,
                name=customer_name,
                recipient_id="1",
                routing_order="1"
            )
            
            # Add signature tab
            sign_here = SignHere(
                document_id="1",
                page_number="1",
                recipient_id="1",
                tab_label="SignHere",
                x_position="200",
                y_position="200"
            )
            
            signer.tabs = Tabs(sign_here_tabs=[sign_here])
            envelope_definition.recipients = Recipients(signers=[signer])
            envelope_definition.status = "sent"
            
            # Create API client
            api_client = ApiClient()
            api_client.host = self.base_path
            
            # TODO: Add proper authentication here
            # This is a placeholder - in production, you would need to implement OAuth2 authentication
            # api_client.set_default_header("Authorization", "Bearer " + access_token)
            
            # Create envelope
            envelopes_api = EnvelopesApi(api_client)
            results = envelopes_api.create_envelope(self.account_id, envelope_definition=envelope_definition)
            
            logger.info(f"DocuSign envelope created successfully for booking {booking.id}")
            return results.envelope_id
            
        except Exception as e:
            logger.error(f"Failed to create DocuSign envelope for booking {booking.id}: {str(e)}")
            raise
    
    def _generate_document_content(self, booking):
        """
        Generate the PDF document content for the signature request
        """
        content = f"""
        SERVICE SATISFACTION CONFIRMATION
        
        Booking ID: {booking.id}
        Service: {booking.service.name}
        Date: {booking.scheduled_date.strftime('%Y-%m-%d %H:%M') if booking.scheduled_date else 'N/A'}
        Vendor: {booking.vendor.get_full_name() if booking.vendor else 'N/A'}
        
        Service Details:
        {booking.service.description if booking.service.description else 'No description available'}
        
        Customer Declaration:
        
        I confirm that the service was completed to my satisfaction and I am happy with the work performed.
        I understand that by signing this document, I am confirming my satisfaction with the service and
        authorizing payment to be released to the service provider.
        
        Customer Name: ________________________________
        
        Signature: ________________________________
        
        Date: ________________________________
        """
        return content
    
    def get_envelope_status(self, envelope_id):
        """
        Get the status of a DocuSign envelope
        """
        try:
            api_client = ApiClient()
            api_client.host = self.base_path
            
            # TODO: Add proper authentication here
            envelopes_api = EnvelopesApi(api_client)
            envelope = envelopes_api.get_envelope(self.account_id, envelope_id)
            
            return {
                'status': envelope.status,
                'envelope_id': envelope.envelope_id,
                'created_date': envelope.created_date_time,
                'sent_date': envelope.sent_date_time,
                'completed_date': envelope.completed_date_time
            }
            
        except Exception as e:
            logger.error(f"Failed to get envelope status for {envelope_id}: {str(e)}")
            raise
    
    def handle_webhook_event(self, payload):
        """
        Handle DocuSign webhook events
        """
        try:
            # Parse webhook payload
            if isinstance(payload, str):
                payload = json.loads(payload)
            
            envelope_id = payload.get('envelopeId')
            status = payload.get('status')
            envelope_status = payload.get('envelopeStatus', '')
            
            logger.info(f"Received DocuSign webhook event - Envelope ID: {envelope_id}, Status: {status}")
            
            # Find signature by DocuSign envelope ID
            try:
                signature = Signature.objects.get(docusign_envelope_id=envelope_id)
                
                # Update signature based on envelope status
                if status == 'completed' or envelope_status == 'completed':
                    signature.status = 'signed'
                    signature.signed_at = timezone.now()
                    
                    # Store comprehensive signature data for hashing
                    signature.signature_data = {
                        'envelope_id': envelope_id,
                        'signed_via': 'docusign',
                        'signed_at': signature.signed_at.isoformat(),
                        'booking_id': str(signature.booking.id),
                        'customer_id': str(signature.booking.customer.id),
                        'vendor_id': str(signature.booking.vendor.id) if signature.booking.vendor else None,
                        'service_name': signature.booking.service.name,
                        'envelope_status': status
                    }
                    
                    signature.save()  # This will generate the SHA-256 hash
                    
                    # Trigger automatic payment processing
                    from .payment_service import PaymentService
                    PaymentService.process_automatic_payment(signature.booking)
                    
                    logger.info(f"Signature {signature.id} marked as signed via DocuSign")
                    
                elif status == 'declined' or envelope_status == 'declined':
                    signature.status = 'rejected'
                    signature.save()
                    
                    logger.info(f"Signature {signature.id} marked as rejected via DocuSign")
                    
                elif status == 'voided' or envelope_status == 'voided':
                    signature.status = 'expired'
                    signature.save()
                    
                    logger.info(f"Signature {signature.id} marked as expired via DocuSign")
                
                # Send WebSocket notification
                try:
                    from .signature_service import SignatureService
                    SignatureService._send_signature_notification('signature_completed', signature.booking, signature)
                except Exception as e:
                    logger.error(f"Error sending WebSocket notification: {str(e)}")
                
                return True
                
            except Signature.DoesNotExist:
                logger.warning(f"Signature not found for DocuSign envelope ID: {envelope_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing DocuSign webhook event: {str(e)}")
            raise


# Global instance
docusign_service = None

def get_docusign_service():
    """
    Get singleton instance of DocuSignService
    """
    global docusign_service
    if docusign_service is None:
        try:
            docusign_service = DocuSignService()
        except Exception as e:
            logger.error(f"Failed to initialize DocuSignService: {str(e)}")
            docusign_service = None
    return docusign_service