import { useState } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Shield, Activity, DollarSign } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { toast } from 'sonner';

interface SystemStat {
  label: string;
  value: string;
  color: string;
}

interface AdminAction {
  id: string;
  action: string;
  admin: string;
  timestamp: string;
}

export default function AdminDashboard() {
  const [systemStats, setSystemStats] = useState<SystemStat[]>([
    { label: 'System Status', value: 'Operational', color: 'text-success' },
    { label: 'Server Load', value: '45%', color: 'text-primary' },
    { label: 'Active Sessions', value: '342', color: 'text-primary' },
    { label: 'API Response', value: '120ms', color: 'text-success' },
  ]);

  const [recentActions, setRecentActions] = useState<AdminAction[]>([
    { id: '1', action: 'User role updated', admin: 'John', timestamp: '2 hours ago' },
    { id: '2', action: 'System settings changed', admin: 'Sarah', timestamp: '5 hours ago' },
    { id: '3', action: 'Security scan completed', admin: 'System', timestamp: '1 day ago' },
  ]);

  // WebSocket connection for real-time updates
  const { isConnected } = useWebSocket((data) => {
    if (data.type === 'system_health_update') {
      // Update system stats in real-time
      setSystemStats(prev => prev.map(stat => 
        stat.label === (data.stat_label as string)
          ? { ...stat, value: data.stat_value as string, color: (data.stat_color as string) || stat.color } 
          : stat
      ));
    } else if (data.type === 'admin_action') {
      // Add new admin action to the list
      const newAction: AdminAction = {
        id: data.action_id as string,
        action: data.action_description as string,
        admin: data.admin_name as string,
        timestamp: 'Just now'
      };
      
      setRecentActions(prev => [newAction, ...prev.slice(0, 2)]);
      
      // Show notification
      toast.info('Admin action performed', {
        description: `${data.admin_name as string}: ${data.action_description as string}`
      });
    } else if (data.type === 'security_alert') {
      // Show security alert notification
      toast.error('Security Alert', {
        description: data.alert_message as string
      });
      
      // Update security stats
      setSystemStats(prev => prev.map(stat => 
        stat.label === 'Security Alerts' 
          ? { ...stat, value: (data.alert_count as number).toString(), color: 'text-destructive' } 
          : stat
      ));
    }
  });

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
              {recentActions.map((action) => (
                <div key={action.id} className="p-3 border border-border rounded-lg">
                  <p className="font-medium">{action.action}</p>
                  <p className="text-xs text-muted-foreground">Admin {action.admin} • {action.timestamp}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}