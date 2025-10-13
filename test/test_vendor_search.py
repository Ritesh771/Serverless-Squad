#!/usr/bin/env python
"""Test vendor search endpoint"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')
django.setup()

from core.models import User, Service, VendorApplication, VendorAvailability

def test_vendor_search(pincode, service_id=None):
    """Test the vendor search logic"""
    print(f"\n{'='*60}")
    print(f"Testing Vendor Search for Pincode: {pincode}, Service ID: {service_id}")
    print(f"{'='*60}\n")
    
    try:
        # Get available vendors in the pincode
        vendors = User.objects.filter(
            role='vendor',
            pincode=pincode,
            is_available=True,
            is_verified=True,
            is_active=True
        )
        
        print(f"✓ Found {vendors.count()} vendors in pincode {pincode}")
        
        # Filter by service if provided
        if service_id:
            try:
                service = Service.objects.get(id=service_id)
                print(f"✓ Service: {service.name}")
                
                # Filter vendors by checking if they have this service in their application
                vendor_applications = VendorApplication.objects.filter(
                    status='approved',
                    service_category__icontains=service.name
                ).values_list('vendor_account_id', flat=True)
                
                print(f"✓ Found {len(vendor_applications)} vendor applications matching service")
                vendors = vendors.filter(id__in=vendor_applications)
                print(f"✓ Filtered to {vendors.count()} vendors with matching service")
                
            except Service.DoesNotExist:
                print(f"✗ Service with ID {service_id} not found")
                pass
        
        # Print vendor details
        print(f"\nVendors found:")
        for vendor in vendors:
            print(f"  - {vendor.get_full_name()} ({vendor.email}) - Pincode: {vendor.pincode}")
            
            # Check availability
            availability = VendorAvailability.objects.filter(
                vendor=vendor,
                is_active=True
            ).first()
            
            if availability:
                print(f"    Availability: {availability.day_of_week} {availability.start_time} - {availability.end_time}")
            else:
                print(f"    No availability set")
        
        print(f"\n{'='*60}")
        print(f"SUCCESS: Vendor search completed")
        print(f"{'='*60}\n")
        return True
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"ERROR: {str(e)}")
        print(f"{'='*60}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Test 1: Search without service filter
    print("\nTEST 1: Search all vendors in pincode 560028")
    test_vendor_search('560028')
    
    # Test 2: Search with service filter
    print("\nTEST 2: Search vendors with service filter")
    test_vendor_search('560028', service_id=1)
    
    # List all available data
    print("\n" + "="*60)
    print("AVAILABLE DATA")
    print("="*60)
    print(f"Total Vendors: {User.objects.filter(role='vendor').count()}")
    print(f"Total Services: {Service.objects.count()}")
    print(f"Approved Applications: {VendorApplication.objects.filter(status='approved').count()}")
    
    print("\nVendors by pincode:")
    for pincode in User.objects.filter(role='vendor').values_list('pincode', flat=True).distinct():
        count = User.objects.filter(role='vendor', pincode=pincode).count()
        print(f"  {pincode}: {count} vendors")
    
    print("\nServices:")
    for service in Service.objects.all()[:5]:
        print(f"  ID {service.id}: {service.name}")
