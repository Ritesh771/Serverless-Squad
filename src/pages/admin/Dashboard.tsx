import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Shield, Activity, DollarSign } from 'lucide-react';

export default function AdminDashboard() {
  const systemStats = [
    { label: 'System Status', value: 'Operational', color: 'text-success' },
    { label: 'Server Load', value: '45%', color: 'text-primary' },
    { label: 'Active Sessions', value: '342', color: 'text-primary' },
    { label: 'API Response', value: '120ms', color: 'text-success' },
  ];

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Admin Dashboard</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">System-wide management and monitoring</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Users"
          value="2,847"
          icon={Users}
          trend={{ value: 12, isPositive: true }}
          description="All roles"
        />
        <DashboardCard
          title="Security Alerts"
          value="0"
          icon={Shield}
          description="Last 24 hours"
        />
        <DashboardCard
          title="Platform Activity"
          value="98%"
          icon={Activity}
          trend={{ value: 5, isPositive: true }}
          description="Uptime"
        />
        <DashboardCard
          title="Total Revenue"
          value="$458K"
          icon={DollarSign}
          trend={{ value: 18, isPositive: true }}
          description="This month"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>System Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {systemStats.map((stat, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">{stat.label}</span>
                  <span className={`font-medium ${stat.color}`}>{stat.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Recent Admin Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div className="p-3 border border-border rounded-lg">
                <p className="font-medium">User role updated</p>
                <p className="text-xs text-muted-foreground">Admin John • 2 hours ago</p>
              </div>
              <div className="p-3 border border-border rounded-lg">
                <p className="font-medium">System settings changed</p>
                <p className="text-xs text-muted-foreground">Admin Sarah • 5 hours ago</p>
              </div>
              <div className="p-3 border border-border rounded-lg">
                <p className="font-medium">Security scan completed</p>
                <p className="text-xs text-muted-foreground">System • 1 day ago</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
