import { useState, useEffect } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Calendar, DollarSign, Clock, CheckCircle, User, Camera, FileSignature } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { toast } from 'sonner';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';
import { VendorPayoutPanel } from '@/components/VendorPayoutPanel';

interface Job {
  id: string;
  customer: string;
  service: string;
  time: string;
  address: string;
  status: string;
}

export default function VendorDashboard() {
  const [isAvailable, setIsAvailable] = useState(true);
  const [upcomingJobs, setUpcomingJobs] = useState<Job[]>([
    { id: '1', customer: 'Jane Doe', service: 'Plumbing', time: '10:00 AM', address: '123 Main St', status: 'scheduled' },
    { id: '2', customer: 'Bob Smith', service: 'Electrical', time: '2:00 PM', address: '456 Oak Ave', status: 'in_progress' },
  ]);

  // WebSocket connection for real-time updates
  const { isConnected, sendMessage } = useWebSocket((data) => {
    if (data.type === 'booking_status_update') {
      // Update job status in real-time
      setUpcomingJobs(prev => prev.map(job => 
        job.id === (data.booking_id as string)
          ? { ...job, status: data.status as string } 
          : job
      ));
      
      // Show notification
      toast.info(`Job status updated`, {
        description: `${data.service_name || 'Service'} is now ${data.status}`
      });
    } else if (data.type === 'new_booking') {
      // Add new booking to the list
      const newJob: Job = {
        id: data.booking_id as string,
        customer: data.customer_name as string,
        service: data.service_name as string,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        address: data.address as string,
        status: 'scheduled'
      };
      
      setUpcomingJobs(prev => [...prev, newJob]);
      
      toast.success('New booking assigned!', {
        description: `${data.service_name as string} for ${data.customer_name as string}`
      });
    }
  });

  // Toggle availability status
  const toggleAvailability = async (checked: boolean) => {
    setIsAvailable(checked);
    
    try {
      // Send availability update via WebSocket
      sendMessage({
        type: 'availability_update',
        is_available: checked
      });
      
      // Also update via API as fallback
      await api.post(ENDPOINTS.VENDOR.AVAILABILITY, {
        is_available: checked
      });
      
      toast.success(`You are now ${checked ? 'available' : 'unavailable'} for new jobs`);
    } catch (error) {
      toast.error('Failed to update availability');
      setIsAvailable(!checked); // Revert the toggle
    }
  };

  // Request signature for a completed job
  const requestSignature = async (jobId: string) => {
    try {
      sendMessage({
        type: 'request_signature',
        booking_id: jobId
      });
      
      toast.success('Signature request sent to customer');
      
      // Update job status locally
      setUpcomingJobs(prev => prev.map(job => 
        job.id === jobId 
          ? { ...job, status: 'signature_requested' } 
          : job
      ));
    } catch (error) {
      toast.error('Failed to request signature');
    }
  };

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">Vendor Dashboard</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage your jobs and earnings</p>
          {isConnected && (
            <div className="flex items-center gap-2 mt-2 text-sm text-success">
              <div className="h-2 w-2 rounded-full bg-success animate-pulse"></div>
              <span>Live updates connected</span>
            </div>
          )}
        </div>

        <Card className="card-elevated w-full md:w-auto">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Switch
                checked={isAvailable}
                onCheckedChange={toggleAvailability}
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
        <div className="lg:col-span-2 space-y-6">
          <Card className="card-elevated">
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
                    <div className="flex flex-col items-end gap-2">
                      <p className="font-medium text-primary">{job.time}</p>
                      <div className="flex items-center gap-2">
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${
                            job.status === 'in_progress'
                              ? 'bg-primary/10 text-primary'
                              : job.status === 'completed'
                              ? 'bg-success/10 text-success'
                              : job.status === 'signature_requested'
                              ? 'bg-warning/10 text-warning'
                              : 'bg-secondary/10 text-secondary'
                          }`}
                        >
                          {job.status.replace('_', ' ')}
                        </span>
                        {job.status === 'completed' && (
                          <Button 
                            size="sm" 
                            variant="outline" 
                            onClick={() => requestSignature(job.id)}
                            className="h-6 text-xs"
                          >
                            <FileSignature className="h-3 w-3 mr-1" />
                            Request Signature
                          </Button>
                        )}
                        {(job.status === 'completed' || job.status === 'in_progress') && (
                          <Button 
                            size="sm" 
                            variant="outline" 
                            className="h-6 text-xs"
                          >
                            <Camera className="h-3 w-3 mr-1" />
                            Photos
                          </Button>
                        )}
                      </div>
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

              <div className="pt-4">
                <h3 className="text-sm font-medium mb-2">Quick Actions</h3>
                <div className="space-y-2">
                  <Button className="w-full text-sm h-9">
                    <User className="h-4 w-4 mr-2" />
                    View Profile
                  </Button>
                  <Button variant="outline" className="w-full text-sm h-9">
                    <Calendar className="h-4 w-4 mr-2" />
                    Schedule
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Earnings Overview */}
        <VendorPayoutPanel />
      </div>
    </div>
  );
}