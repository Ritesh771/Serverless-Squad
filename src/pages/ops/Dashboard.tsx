import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MapPin, Calendar, CheckCircle, AlertTriangle } from 'lucide-react';

export default function OpsDashboard() {
  const activeJobs = [
    { id: '1', service: 'Plumbing', vendor: 'John Smith', customer: 'Jane Doe', location: 'New York', status: 'in-progress' },
    { id: '2', service: 'Electrical', vendor: 'Sarah Johnson', customer: 'Bob Wilson', location: 'Los Angeles', status: 'assigned' },
    { id: '3', service: 'HVAC', vendor: 'Mike Davis', customer: 'Alice Brown', location: 'Chicago', status: 'pending' },
  ];

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Operations Dashboard</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Monitor and manage all platform operations</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Active Jobs"
          value="24"
          icon={Calendar}
          description="Currently in progress"
        />
        <DashboardCard
          title="Pending Signatures"
          value="8"
          icon={CheckCircle}
          description="Awaiting customer sign-off"
        />
        <DashboardCard
          title="Payment Holds"
          value="5"
          icon={AlertTriangle}
          description="Requiring review"
        />
        <DashboardCard
          title="Success Rate"
          value="96%"
          icon={CheckCircle}
          trend={{ value: 3, isPositive: true }}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Jobs Map Placeholder */}
        <Card className="lg:col-span-2 card-elevated">
          <CardHeader>
            <CardTitle>Active Jobs by Location</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80 bg-muted rounded-lg flex items-center justify-center">
              <div className="text-center">
                <MapPin className="h-12 w-12 text-primary mx-auto mb-2" />
                <p className="text-muted-foreground">Map visualization would appear here</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {activeJobs.map((job) => (
                <div key={job.id} className="p-3 border border-border rounded-lg">
                  <p className="font-medium text-sm">{job.service}</p>
                  <p className="text-xs text-muted-foreground">{job.vendor} → {job.customer}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-muted-foreground">{job.location}</span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        job.status === 'in-progress'
                          ? 'bg-primary/10 text-primary'
                          : job.status === 'assigned'
                          ? 'bg-success/10 text-success'
                          : 'bg-warning/10 text-warning'
                      }`}
                    >
                      {job.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
