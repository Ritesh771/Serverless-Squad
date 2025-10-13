"""
Test script for DocuSign integration
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')

# Setup Django
django.setup()

def test_docusign_service():
    """Test the DocuSign service"""
    try:
        from core.docusign_service import get_docusign_service
        print("✓ DocuSign service import successful")
        
        # Try to get the service instance
        docusign_service = get_docusign_service()
        if docusign_service:
            print("✓ DocuSign service instance created")
        else:
            print("⚠ DocuSign service not available (missing configuration)")
            
    except Exception as e:
        print(f"✗ Error testing DocuSign service: {e}")
        
def test_signature_model():
    """Test the Signature model with DocuSign fields"""
    try:
        from core.models import Signature
        print("✓ Signature model import successful")
        
        # Check if DocuSign fields exist
        fields = [f.name for f in Signature._meta.get_fields()]
        if 'docusign_envelope_id' in fields and 'docusign_signing_url' in fields:
            print("✓ DocuSign fields found in Signature model")
        else:
            print("✗ DocuSign fields missing from Signature model")
            
    except Exception as e:
        print(f"✗ Error testing Signature model: {e}")

def test_signature_service():
    """Test the Signature service"""
    try:
        from core.signature_service import SignatureService
        print("✓ Signature service import successful")
        
        # Check if handle_docusign_webhook method exists
        if hasattr(SignatureService, 'handle_docusign_webhook'):
            print("✓ handle_docusign_webhook method found in SignatureService")
        else:
            print("✗ handle_docusign_webhook method missing from SignatureService")
            
    except Exception as e:
        print(f"✗ Error testing Signature service: {e}")

if __name__ == "__main__":
    print("Testing DocuSign Integration...\n")
    
    test_docusign_service()
    print()
    
    test_signature_model()
    print()
    
    test_signature_service()
    print()
    
    print("DocuSign integration test completed.")