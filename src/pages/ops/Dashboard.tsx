import { useState, useEffect } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MapPin, Calendar, CheckCircle, AlertTriangle, Users, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';
import { PincodeHeatmap } from '@/components/PincodeHeatmap';
import { useQuery } from '@tanstack/react-query';
import { adminService } from '@/services/adminService';
import { Loader } from '@/components/Loader';

interface ActiveJob {
  id: string;
  service: string;
  vendor: string;
  customer: string;
  location: string;
  status: string;
}

export default function OpsDashboard() {
  // Fetch live dashboard data from backend
  const { data: liveDashboardData, isLoading, error } = useQuery({
    queryKey: ['ops-live-dashboard'],
    queryFn: adminService.getLiveDashboardData,
    refetchInterval: 30000, // Refresh every 30 seconds
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
          <AlertTriangle className="mx-auto h-12 w-12 text-destructive" />
          <h3 className="mt-2 text-lg font-semibold">Error Loading Dashboard</h3>
          <p className="text-muted-foreground">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Operations Dashboard</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Monitor and manage all platform operations</p>
        {/* Removed live updates indicator to fix superadmin login issues */}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Active Jobs"
          value={liveDashboardData?.data?.booking_stats?.in_progress?.toString() || "0"}
          icon={Calendar}
          description="Currently in progress"
        />
        <DashboardCard
          title="Pending Signatures"
          value={liveDashboardData?.data?.signature_stats?.pending?.toString() || "0"}
          icon={CheckCircle}
          description="Awaiting customer sign-off"
        />
        <DashboardCard
          title="Payment Holds"
          value={liveDashboardData?.data?.payment_stats?.on_hold?.toString() || "0"}
          icon={AlertTriangle}
          description="Requiring review"
        />
        <DashboardCard
          title="Completion Rate"
          value={`${liveDashboardData?.data?.booking_stats?.completion_rate || 0}%`}
          icon={CheckCircle}
          trend={{ value: 3, isPositive: true }}
          description="Today"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Jobs Map */}
        <Card className="lg:col-span-2 card-elevated">
          <CardHeader>
            <CardTitle>Service Activity Heatmap</CardTitle>
          </CardHeader>
          <CardContent>
            <PincodeHeatmap />
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Recent System Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {liveDashboardData?.data?.recent_activities?.slice(0, 5).map((activity: any, index: number) => (
                <div key={index} className="p-3 border border-border rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-sm">{activity.action}</p>
                      <p className="text-xs text-muted-foreground">{activity.resource_type} by {activity.user}</p>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(activity.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              )) || (
                <div className="text-center py-4 text-muted-foreground">
                  No recent activity
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="card-elevated hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Users className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-medium">Vendor Management</p>
                <p className="text-sm text-muted-foreground">Approve and monitor vendors</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="card-elevated hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-success/10 rounded-lg">
                <CheckCircle className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="font-medium">Signature Vault</p>
                <p className="text-sm text-muted-foreground">View all signatures</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="card-elevated hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-warning/10 rounded-lg">
                <TrendingUp className="h-5 w-5 text-warning" />
              </div>
              <div>
                <p className="font-medium">Analytics</p>
                <p className="text-sm text-muted-foreground">Platform performance metrics</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}