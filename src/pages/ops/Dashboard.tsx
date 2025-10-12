import { useState, useEffect } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MapPin, Calendar, CheckCircle, AlertTriangle, Users, TrendingUp } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { toast } from 'sonner';
import { PincodeHeatmap } from '@/components/PincodeHeatmap';

interface ActiveJob {
  id: string;
  service: string;
  vendor: string;
  customer: string;
  location: string;
  status: string;
}

export default function OpsDashboard() {
  const [activeJobs, setActiveJobs] = useState<ActiveJob[]>([
    { id: '1', service: 'Plumbing', vendor: 'John Smith', customer: 'Jane Doe', location: 'New York', status: 'in-progress' },
    { id: '2', service: 'Electrical', vendor: 'Sarah Johnson', customer: 'Bob Wilson', location: 'Los Angeles', status: 'assigned' },
    { id: '3', service: 'HVAC', vendor: 'Mike Davis', customer: 'Alice Brown', location: 'Chicago', status: 'pending' },
  ]);

  const [stats, setStats] = useState({
    activeJobs: 24,
    pendingSignatures: 8,
    paymentHolds: 5,
    successRate: 96
  });

  // WebSocket connection for real-time updates
  const { isConnected } = useWebSocket((data) => {
    if (data.type === 'booking_status_update') {
      // Update active jobs list
      setActiveJobs(prev => prev.map(job => 
        job.id === (data.booking_id as string)
          ? { ...job, status: data.status as string } 
          : job
      ));
      
      // Show notification
      toast.info(`Booking status updated`, {
        description: `${data.service_name as string || 'Service'} is now ${data.status as string}`
      });
    } else if (data.type === 'signature_completed') {
      // Update stats when signature is completed
      setStats(prev => ({
        ...prev,
        pendingSignatures: Math.max(0, prev.pendingSignatures - 1)
      }));
      
      toast.success('Customer signature completed', {
        description: `Booking ${data.booking_id as string} signed`
      });
    } else if (data.type === 'new_booking') {
      // Add new booking to active jobs
      const newJob: ActiveJob = {
        id: data.booking_id as string,
        service: data.service_name as string,
        vendor: (data.vendor_name as string) || 'Pending',
        customer: data.customer_name as string,
        location: (data.location as string) || 'Unknown',
        status: 'pending'
      };
      
      setActiveJobs(prev => [newJob, ...prev]);
      
      // Update stats
      setStats(prev => ({
        ...prev,
        activeJobs: prev.activeJobs + 1
      }));
      
      toast.info('New booking created', {
        description: `${data.service_name as string} for ${data.customer_name as string}`
      });
    }
  });

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Operations Dashboard</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Monitor and manage all platform operations</p>
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
          title="Active Jobs"
          value={stats.activeJobs.toString()}
          icon={Calendar}
          description="Currently in progress"
        />
        <DashboardCard
          title="Pending Signatures"
          value={stats.pendingSignatures.toString()}
          icon={CheckCircle}
          description="Awaiting customer sign-off"
        />
        <DashboardCard
          title="Payment Holds"
          value={stats.paymentHolds.toString()}
          icon={AlertTriangle}
          description="Requiring review"
        />
        <DashboardCard
          title="Success Rate"
          value={`${stats.successRate}%`}
          icon={CheckCircle}
          trend={{ value: 3, isPositive: true }}
          description="Last 30 days"
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
                      {job.status.replace('-', ' ')}
                    </span>
                  </div>
                </div>
              ))}
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