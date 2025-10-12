import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, Users, DollarSign, MapPin } from 'lucide-react';

export default function OpsAnalytics() {
  const pincodeStats = [
    { pincode: '10001', jobs: 45, revenue: '$3,600' },
    { pincode: '90001', jobs: 38, revenue: '$3,040' },
    { pincode: '60601', jobs: 32, revenue: '$2,560' },
    { pincode: '77001', jobs: 28, revenue: '$2,240' },
  ];

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Analytics</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Platform performance and insights</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Jobs"
          value="1,284"
          icon={TrendingUp}
          trend={{ value: 15, isPositive: true }}
          description="This month"
        />
        <DashboardCard
          title="Active Users"
          value="342"
          icon={Users}
          trend={{ value: 8, isPositive: true }}
          description="Online now"
        />
        <DashboardCard
          title="Revenue"
          value="$98,540"
          icon={DollarSign}
          trend={{ value: 23, isPositive: true }}
          description="This month"
        />
        <DashboardCard
          title="Completion Rate"
          value="96%"
          icon={TrendingUp}
          trend={{ value: 2, isPositive: true }}
          description="Last 30 days"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Jobs by Pincode</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {pincodeStats.map((stat) => (
                <div key={stat.pincode} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-primary" />
                      <span className="font-medium">{stat.pincode}</span>
                    </div>
                    <div className="flex gap-4">
                      <span className="text-muted-foreground">{stat.jobs} jobs</span>
                      <span className="font-medium text-primary">{stat.revenue}</span>
                    </div>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full"
                      style={{ width: `${(stat.jobs / 50) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Service Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center text-muted-foreground">
              Chart visualization would appear here
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
