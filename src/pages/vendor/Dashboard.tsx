import { useState, useEffect } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Calendar, DollarSign, Clock, CheckCircle, User, Camera, FileSignature, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';
import { VendorPayoutPanel } from '@/components/VendorPayoutPanel';
import { vendorService, VendorDashboardData } from '@/services/vendorService';

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
  const [dashboardData, setDashboardData] = useState<VendorDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load dashboard data on component mount
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await vendorService.getDashboard();
      setDashboardData(data);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data');
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  // Toggle availability status
  const toggleAvailability = async (checked: boolean) => {
    setIsAvailable(checked);
    
    try {
      // Update via API
      await api.patch(ENDPOINTS.USERS.PROFILE, {
        is_available: checked
      });
      
      toast.success(`You are now ${checked ? 'available' : 'unavailable'} for new jobs`);
    } catch (error) {
      toast.error('Failed to update availability');
      setIsAvailable(!checked); // Revert the toggle
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading dashboard...</span>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <p className="text-destructive mb-4">{error || 'Failed to load dashboard'}</p>
        <Button onClick={loadDashboardData}>Retry</Button>
      </div>
    );
  }

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
          value={dashboardData.stats.total_jobs.toString()}
          icon={Calendar}
          description={`${dashboardData.stats.completed_jobs} completed, ${dashboardData.stats.pending_jobs} pending`}
        />
        <DashboardCard
          title="Total Earnings"
          value={`$${dashboardData.stats.total_earnings.toFixed(2)}`}
          icon={DollarSign}
          trend={{ value: 12, isPositive: true }}
        />
        <DashboardCard
          title="Pending Jobs"
          value={dashboardData.stats.pending_jobs.toString()}
          icon={Clock}
          description="Awaiting completion"
        />
        <DashboardCard
          title="Completion Rate"
          value={`${(dashboardData.stats.completion_rate * 100).toFixed(1)}%`}
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
                {dashboardData.todays_schedule.length === 0 ? (
                  <p className="text-muted-foreground text-center py-4">No jobs scheduled for today</p>
                ) : (
                  dashboardData.todays_schedule.map((job) => (
                    <div
                      key={job.id}
                      className="flex items-center justify-between p-4 border border-border rounded-lg"
                    >
                      <div>
                        <p className="font-medium">{job.service_name}</p>
                        <p className="text-sm text-muted-foreground">Customer: {job.customer_name}</p>
                        <p className="text-xs text-muted-foreground">{job.pincode}</p>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        <p className="font-medium text-primary">{job.scheduled_time}</p>
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full ${
                              job.status === 'in_progress'
                                ? 'bg-primary/10 text-primary'
                                : job.status === 'completed'
                                ? 'bg-success/10 text-success'
                                : job.status === 'confirmed'
                                ? 'bg-warning/10 text-warning'
                                : 'bg-secondary/10 text-secondary'
                            }`}
                          >
                            {job.status.replace('_', ' ')}
                          </span>
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
                  ))
                )}
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
                  <span className="font-medium">{dashboardData.stats.average_rating.toFixed(1)}/5.0</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div className="bg-primary h-2 rounded-full" style={{ width: `${(dashboardData.stats.average_rating / 5) * 100}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-muted-foreground">Jobs Completed</span>
                  <span className="font-medium">{dashboardData.stats.completed_jobs}</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div className="bg-success h-2 rounded-full" style={{ width: `${(dashboardData.stats.completed_jobs / dashboardData.stats.total_jobs) * 100}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-muted-foreground">Completion Rate</span>
                  <span className="font-medium">{(dashboardData.performance_metrics.completion_rate * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div className="bg-warning h-2 rounded-full" style={{ width: `${dashboardData.performance_metrics.completion_rate * 100}%` }} />
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