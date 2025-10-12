import { useState } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Calendar, DollarSign, Clock, CheckCircle } from 'lucide-react';

export default function VendorDashboard() {
  const [isAvailable, setIsAvailable] = useState(true);

  const upcomingJobs = [
    { id: '1', customer: 'Jane Doe', service: 'Plumbing', time: '10:00 AM', address: '123 Main St' },
    { id: '2', customer: 'Bob Smith', service: 'Electrical', time: '2:00 PM', address: '456 Oak Ave' },
  ];

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">Vendor Dashboard</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage your jobs and earnings</p>
        </div>

        <Card className="card-elevated w-full md:w-auto">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Switch
                checked={isAvailable}
                onCheckedChange={setIsAvailable}
                id="availability"
              />
              <Label htmlFor="availability" className="cursor-pointer">
                <span className="font-medium">
                  {isAvailable ? 'Available' : 'Unavailable'}
                </span>
                <p className="text-xs text-muted-foreground">
                  Toggle to accept new jobs
                </p>
              </Label>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Today's Jobs"
          value="3"
          icon={Calendar}
          description="2 completed, 1 pending"
        />
        <DashboardCard
          title="This Week Earnings"
          value="$1,240"
          icon={DollarSign}
          trend={{ value: 12, isPositive: true }}
        />
        <DashboardCard
          title="Pending Jobs"
          value="5"
          icon={Clock}
          description="Awaiting completion"
        />
        <DashboardCard
          title="Completion Rate"
          value="98%"
          icon={CheckCircle}
          description="Last 30 days"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upcoming Jobs */}
        <Card className="lg:col-span-2 card-elevated">
          <CardHeader>
            <CardTitle>Today's Schedule</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {upcomingJobs.map((job) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between p-4 border border-border rounded-lg"
                >
                  <div>
                    <p className="font-medium">{job.service}</p>
                    <p className="text-sm text-muted-foreground">Customer: {job.customer}</p>
                    <p className="text-xs text-muted-foreground">{job.address}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-primary">{job.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">Rating</span>
                <span className="font-medium">4.9/5.0</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-primary h-2 rounded-full" style={{ width: '98%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">Jobs Completed</span>
                <span className="font-medium">127</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-success h-2 rounded-full" style={{ width: '85%' }} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
