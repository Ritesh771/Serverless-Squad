from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    """Permission class for customers only"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customer'


class IsVendor(BasePermission):
    """Permission class for vendors only"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'vendor'


class IsOnboardManager(BasePermission):
    """Permission class for onboard managers only"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'onboard_manager'


class IsOpsManager(BasePermission):
    """Permission class for ops managers only"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ops_manager'


class IsSuperAdmin(BasePermission):
    """Permission class for super admin only"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'


class IsAdminUser(BasePermission):
    """Permission class for any admin user"""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ['onboard_manager', 'ops_manager', 'super_admin']
        )


class IsVendorOrAdmin(BasePermission):
    """Permission class for vendors or admin users"""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ['vendor', 'onboard_manager', 'ops_manager', 'super_admin']
        )


class IsOwnerOrAdmin(BasePermission):
    """Permission class for object owners or admin users"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin users can access everything
        if request.user.role in ['onboard_manager', 'ops_manager', 'super_admin']:
            return True
        
        # Object-specific ownership checks
        if hasattr(obj, 'customer'):
            return obj.customer == request.user
        elif hasattr(obj, 'vendor'):
            return obj.vendor == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsDisputeParty(BasePermission):
    """Permission class for dispute parties (customer, vendor, mediator, or admin)"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin users can access all disputes
        if request.user.role in ['ops_manager', 'super_admin']:
            return True
        
        # Check if user is a party to this dispute
        if hasattr(obj, 'customer') and obj.customer == request.user:
            return True
        if hasattr(obj, 'vendor') and obj.vendor == request.user:
            return True
        if hasattr(obj, 'assigned_mediator') and obj.assigned_mediator == request.user:
            return True
        
        return False