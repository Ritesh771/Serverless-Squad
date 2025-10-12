"""
Admin URLs for Cache Management, Pincode Scaling, and Edit History features
"""

from django.urls import path
from .admin_views import (
    CacheManagementView,
    pincode_scaling_data,
    edit_history_diff_viewer,
    export_edit_history,
    admin_dashboard_stats,
    notification_management,
    notification_logs,
    business_alerts,
    pincode_analytics_view
)

app_name = 'admin_dashboard'

urlpatterns = [
    # Cache Management Interface
    path('cache/', CacheManagementView.as_view(), name='cache_management'),
    path('cache/stats/', CacheManagementView.as_view(), name='cache_stats'),
    
    # Pincode Scaling Map Visualization
    path('pincode-scaling/', pincode_scaling_data, name='pincode_scaling'),
    path('pincode-scaling/data/', pincode_scaling_data, name='pincode_scaling_data'),
    
    # Global Edit History Diff Viewer
    path('edit-history/', edit_history_diff_viewer, name='edit_history'),
    path('edit-history/export/', export_edit_history, name='export_edit_history'),
    
    # Admin Dashboard Overview
    path('dashboard/stats/', admin_dashboard_stats, name='dashboard_stats'),
    
    # Notification Management
    path('notifications/', notification_management, name='notification_management'),
    path('notifications/logs/', notification_logs, name='notification_logs'),
    path('notifications/alerts/', business_alerts, name='business_alerts'),
    path('analytics/pincode/', pincode_analytics_view, name='pincode_analytics'),
]