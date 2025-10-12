import { useState } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, UserCheck, UserX, Clock, CheckCircle, XCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useWebSocket } from '@/hooks/useWebSocket';
import { toast } from 'sonner';

interface VendorApplication {
  id: string;
  name: string;
  service: string;
  date: string;
  status: string;
}

export default function OnboardDashboard() {
  const [recentApplications, setRecentApplications] = useState<VendorApplication[]>([
    { id: '1', name: 'Mike Johnson', service: 'Plumbing', date: '2025-01-15', status: 'pending' },
    { id: '2', name: 'Sarah Williams', service: 'Electrical', date: '2025-01-14', status: 'pending' },
    { id: '3', name: 'Tom Davis', service: 'HVAC', date: '2025-01-13', status: 'under-review' },
  ]);

  const [stats, setStats] = useState({
    pending: 12,
    underReview: 5,
    approved: 23,
    rejectionRate: 8
  });

  // WebSocket connection for real-time updates
  const { isConnected } = useWebSocket((data) => {
    if (data.type === 'vendor_application_update') {
      // Update application status
      setRecentApplications(prev => prev.map(app => 
        app.id === (data.application_id as string)
          ? { ...app, status: data.status as string } 
          : app
      ));
      
      // Show notification
      toast.info(`Application status updated`, {
        description: `${data.vendor_name as string}'s application is now ${data.status as string}`
      });
    } else if (data.type === 'new_vendor_application') {
      // Add new application to the list
      const newApp: VendorApplication = {
        id: data.application_id as string,
        name: data.vendor_name as string,
        service: data.service_type as string,
        date: new Date().toISOString().split('T')[0],
        status: 'pending'
      };
      
      setRecentApplications(prev => [newApp, ...prev.slice(0, 2)]);
      
      // Update stats
      setStats(prev => ({
        ...prev,
        pending: prev.pending + 1
      }));
      
      toast.info('New vendor application received', {
        description: `${data.vendor_name as string} applied for ${data.service_type as string}`
      });
    } else if (data.type === 'vendor_approved') {
      // Update stats when vendor is approved
      setStats(prev => ({
        ...prev,
        pending: Math.max(0, prev.pending - 1),
        approved: prev.approved + 1
      }));
      
      toast.success('Vendor approved successfully', {
        description: `${data.vendor_name as string} has been approved`
      });
    } else if (data.type === 'vendor_rejected') {
      // Update stats when vendor is rejected
      setStats(prev => ({
        ...prev,
        pending: Math.max(0, prev.pending - 1),
        rejectionRate: Math.min(100, prev.rejectionRate + 1)
      }));
      
      toast.info('Vendor application rejected', {
        description: `${data.vendor_name as string}'s application was rejected`
      });
    }
  });

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Onboarding Dashboard</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage vendor applications and approvals</p>
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
          title="Pending Applications"
          value={stats.pending.toString()}
          icon={Clock}
          description="Awaiting review"
        />
        <DashboardCard
          title="Under Review"
          value={stats.underReview.toString()}
          icon={Users}
          description="Being processed"
        />
        <DashboardCard
          title="Approved This Month"
          value={stats.approved.toString()}
          icon={UserCheck}
          trend={{ value: 15, isPositive: true }}
        />
        <DashboardCard
          title="Rejection Rate"
          value={`${stats.rejectionRate}%`}
          icon={UserX}
          description="Last 30 days"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Applications */}
        <Card className="lg:col-span-2 card-elevated">
          <CardHeader>
            <CardTitle>Recent Applications</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentApplications.map((app) => (
                <Link
                  key={app.id}
                  to={`/onboard/vendor-queue/${app.id}`}
                  className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted transition-colors"
                >
                  <div>
                    <p className="font-medium">{app.name}</p>
                    <p className="text-sm text-muted-foreground">{app.service}</p>
                  </div>
                  <div className="text-right">
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                      app.status === 'pending'
                        ? 'bg-warning/10 text-warning'
                        : app.status === 'under-review'
                        ? 'bg-primary/10 text-primary'
                        : app.status === 'approved'
                        ? 'bg-success/10 text-success'
                        : 'bg-destructive/10 text-destructive'
                    }`}>
                      {app.status === 'approved' ? (
                        <>
                          <CheckCircle className="h-3 w-3" />
                          {app.status.replace('-', ' ')}
                        </>
                      ) : app.status === 'rejected' ? (
                        <>
                          <XCircle className="h-3 w-3" />
                          {app.status.replace('-', ' ')}
                        </>
                      ) : (
                        app.status.replace('-', ' ')
                      )}
                    </span>
                    <p className="text-xs text-muted-foreground mt-1">{app.date}</p>
                  </div>
                </Link>
              ))}
            </div>
            <Link to="/onboard/vendor-queue">
              <button className="w-full mt-4 px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors text-sm">
                View All Applications
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