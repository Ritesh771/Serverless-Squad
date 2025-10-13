import { useState } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Activity, DollarSign, AlertCircle } from 'lucide-react';
// Removed useWebSocket import to fix WebSocket issues for superadmin role
import { toast } from 'sonner';
import { useQuery } from '@tanstack/react-query';
import { adminService } from '@/services/adminService';
import { Loader } from '@/components/Loader';

// Define type for admin actions
interface AdminAction {
  action: string;
  count: number;
}

export default function AdminDashboard() {
  // Fetch live dashboard data from backend
  const { data: liveDashboardData, isLoading, error } = useQuery({
    queryKey: ['admin-live-dashboard'],
    queryFn: adminService.getLiveDashboardData,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch basic dashboard stats as fallback
  const { data: dashboardStats } = useQuery({
    queryKey: ['admin-dashboard-stats'],
    queryFn: adminService.getDashboardStats,
    refetchInterval: 60000, // Refresh every minute
  });

  // Removed WebSocket connection for real-time updates to fix superadmin login issues

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-destructive" />
          <h3 className="mt-2 text-lg font-semibold">Error Loading Dashboard</h3>
          <p className="text-muted-foreground">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Admin Dashboard</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">System-wide management and monitoring</p>
        {/* Removed live updates indicator to fix superadmin login issues */}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Bookings Today"
          value={liveDashboardData?.data?.booking_stats?.total_today?.toString() || "0"}
          icon={Activity}
          description="Bookings created today"
        />
        <DashboardCard
          title="Pending Signatures"
          value={liveDashboardData?.data?.signature_stats?.pending?.toString() || "0"}
          icon={AlertCircle}
          description="Awaiting customer sign-off"
        />
        <DashboardCard
          title="Available Vendors"
          value={liveDashboardData?.data?.vendor_stats?.available?.toString() || "0"}
          icon={Users}
          description="Active vendors"
        />
        <DashboardCard
          title="Payment Holds"
          value={liveDashboardData?.data?.payment_stats?.on_hold?.toString() || "0"}
          icon={DollarSign}
          description="Requiring review"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Recent System Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              {liveDashboardData?.data?.recent_activities?.slice(0, 5).map((activity: any, index: number) => (
                <div key={index} className="p-3 border border-border rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{activity.action}</p>
                      <p className="text-xs text-muted-foreground">{activity.resource_type} by {activity.user}</p>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(activity.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              )) || (
                <div className="text-center py-4 text-muted-foreground">
                  No recent system activity
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* System Alerts */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Active Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              {liveDashboardData?.data?.alerts?.slice(0, 5).map((alert: any, index: number) => (
                <div key={index} className="p-3 border border-border rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{alert.title}</p>
                      <p className="text-xs text-muted-foreground">{alert.description}</p>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ${
                      alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                      alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {alert.severity}
                    </span>
                  </div>
                </div>
              )) || (
                <div className="text-center py-4 text-muted-foreground">
                  No active alerts
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}