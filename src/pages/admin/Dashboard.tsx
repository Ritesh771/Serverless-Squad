import { useState } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Shield, Activity, DollarSign, AlertCircle } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { toast } from 'sonner';
import { useQuery } from '@tanstack/react-query';
import { adminService } from '@/services/adminService';
import { Loader } from '@/components/Loader';

export default function AdminDashboard() {
  // Fetch real dashboard stats from backend
  const { data: dashboardStats, isLoading, error } = useQuery({
    queryKey: ['admin-dashboard-stats'],
    queryFn: adminService.getDashboardStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch cache stats
  const { data: cacheStats } = useQuery({
    queryKey: ['admin-cache-stats'],
    queryFn: adminService.getCacheStats,
    refetchInterval: 60000, // Refresh every minute
  });

  // WebSocket connection for real-time updates
  const { isConnected } = useWebSocket((data) => {
    if (data.type === 'admin_action') {
      toast.info('Admin action performed', {
        description: `${data.admin_name as string}: ${data.action_description as string}`
      });
    } else if (data.type === 'security_alert') {
      toast.error('Security Alert', {
        description: data.alert_message as string
      });
    }
  });

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
        {isConnected && (
          <div className="flex items-center gap-2 mt-2 text-sm text-success">
            <div className="h-2 w-2 rounded-full bg-success animate-pulse"></div>
            <span>Live updates connected</span>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Users"
          value={dashboardStats?.activity_stats?.unique_users_24h?.toString() || "0"}
          icon={Users}
          description="Active users (24h)"
        />
        <DashboardCard
          title="Cache Health"
          value={`${cacheStats?.cache_health?.health_percentage?.toFixed(0) || "0"}%`}
          icon={Shield}
          description={`${cacheStats?.cache_health?.healthy_caches || 0}/${cacheStats?.cache_health?.total_caches || 0} healthy`}
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
        {/* System Health */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Cache Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Overall Health</span>
                <span className={`font-medium ${
                  (cacheStats?.cache_health?.health_percentage || 0) > 80 ? 'text-green-600' : 'text-yellow-600'
                }`}>
                  {cacheStats?.cache_health?.health_percentage?.toFixed(1) || 0}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Average Hit Rate</span>
                <span className="font-medium text-blue-600">
                  {cacheStats?.cache_health?.average_hit_rate?.toFixed(1) || 0}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Healthy Caches</span>
                <span className="font-medium text-green-600">
                  {cacheStats?.cache_health?.healthy_caches || 0}/{cacheStats?.cache_health?.total_caches || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Cache Status</span>
                <span className={`font-medium ${
                  cacheStats?.cache_health?.status === 'healthy' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {cacheStats?.cache_health?.status || 'Unknown'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Top Admin Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              {dashboardStats?.activity_stats?.top_actions?.map((action: any, index: number) => (
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