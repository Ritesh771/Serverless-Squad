import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, UserCheck, UserX, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function OnboardDashboard() {
  const recentApplications = [
    { id: '1', name: 'Mike Johnson', service: 'Plumbing', date: '2025-01-15', status: 'pending' },
    { id: '2', name: 'Sarah Williams', service: 'Electrical', date: '2025-01-14', status: 'pending' },
    { id: '3', name: 'Tom Davis', service: 'HVAC', date: '2025-01-13', status: 'under-review' },
  ];

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Onboarding Dashboard</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage vendor applications and approvals</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Pending Applications"
          value="12"
          icon={Clock}
          description="Awaiting review"
        />
        <DashboardCard
          title="Under Review"
          value="5"
          icon={Users}
          description="Being processed"
        />
        <DashboardCard
          title="Approved This Month"
          value="23"
          icon={UserCheck}
          trend={{ value: 15, isPositive: true }}
        />
        <DashboardCard
          title="Rejection Rate"
          value="8%"
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
                    <span className="inline-block px-2 py-1 rounded text-xs font-medium bg-warning/10 text-warning">
                      {app.status.replace('-', ' ')}
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
              <button className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary-hover transition-colors">
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
