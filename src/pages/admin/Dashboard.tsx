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
  // Fetch real dashboard stats from backend
  const { data: dashboardStats, isLoading, error } = useQuery({
    queryKey: ['admin-dashboard-stats'],
    queryFn: adminService.getDashboardStats,
    refetchInterval: 30000, // Refresh every 30 seconds
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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <DashboardCard
          title="Total Users"
          value={dashboardStats?.activity_stats?.unique_users_24h?.toString() || "0"}
          icon={Users}
          description="Active users (24h)"
        />
        <DashboardCard
          title="Platform Activity"
          value={dashboardStats?.activity_stats?.total_actions_24h?.toString() || "0"}
          icon={Activity}
          description="Actions (24h)"
        />
        <DashboardCard
          title="Pincodes Served"
          value={dashboardStats?.pincode_stats?.total_pincodes_served?.toString() || "0"}
          icon={DollarSign}
          description="Active areas"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Top Admin Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              {dashboardStats?.activity_stats?.top_actions?.map((action: AdminAction, index: number) => (
                <div key={index} className="p-3 border border-border rounded-lg">
                  <p className="font-medium">{action.action}</p>
                  <p className="text-xs text-muted-foreground">{action.count} times today</p>
                </div>
              )) || (
                <div className="text-center py-4 text-muted-foreground">
                  No recent admin actions
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}