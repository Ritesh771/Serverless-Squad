import { useState } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, UserCheck, UserX, Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import { useQuery } from '@tanstack/react-query';
import { adminService } from '@/services/adminService';
import { Loader } from '@/components/Loader';

interface VendorApplication {
  id: string;
  name: string;
  service: string;
  date: string;
  status: string;
  ai_flag?: boolean;
  flag_reason?: string;
}

export default function OnboardDashboard() {
  // Fetch live dashboard data from backend
  const { data: liveDashboardData, isLoading, error } = useQuery({
    queryKey: ['onboard-live-dashboard'],
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
        <h1 className="text-2xl md:text-3xl font-bold">Onboarding Dashboard</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage vendor applications and approvals</p>
        {/* Removed live updates indicator to fix superadmin login issues */}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <DashboardCard
          title="Pending Applications"
          value={liveDashboardData?.data?.onboarding_stats?.pending_applications?.toString() || "0"}
          icon={Clock}
          description="Awaiting review"
        />
        <DashboardCard
          title="Flagged Applications"
          value={liveDashboardData?.data?.onboarding_stats?.flagged_applications?.toString() || "0"}
          icon={AlertTriangle}
          description="Require attention"
        />
        <DashboardCard
          title="Approved Today"
          value={liveDashboardData?.data?.onboarding_stats?.approved_today?.toString() || "0"}
          icon={UserCheck}
          trend={{ value: 15, isPositive: true }}
        />
        <DashboardCard
          title="Total Vendors"
          value={liveDashboardData?.data?.vendor_stats?.total?.toString() || "0"}
          icon={Users}
          description="Active vendors"
        />
        <DashboardCard
          title="Available Vendors"
          value={liveDashboardData?.data?.vendor_stats?.available?.toString() || "0"}
          icon={UserCheck}
          description="Currently available"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Applications */}
        <Card className="lg:col-span-2 card-elevated">
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
            <Link to="/onboard/vendor-queue">
              <button className="w-full mt-4 px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors text-sm">
                View Vendor Queue
              </button>
            </Link>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link to="/onboard/vendor-queue">
              <button className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
                Review Queue
              </button>
            </Link>
            <Link to="/onboard/vendor-queue?flagged_only=true">
              <button className="w-full px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors">
                View Flagged Applications
              </button>
            </Link>
            <Link to="/onboard/approved-vendors">
              <button className="w-full px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors">
                Approved Vendors
              </button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}