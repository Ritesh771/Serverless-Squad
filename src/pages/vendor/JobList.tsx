import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar, MapPin, DollarSign, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bookingService } from '@/services/bookingService';
import { Loader } from '@/components/Loader';
import { toast } from 'sonner';
import { AlertCircle } from 'lucide-react';

export default function VendorJobList() {
  const queryClient = useQueryClient();

  // Fetch vendor's bookings
  const { data: bookings, isLoading, error } = useQuery({
    queryKey: ['vendor-bookings'],
    queryFn: () => bookingService.getBookings(),
  });

  // Accept booking mutation
  const acceptBookingMutation = useMutation({
    mutationFn: bookingService.acceptBooking,
    onSuccess: () => {
      toast.success('Job accepted successfully!');
      queryClient.invalidateQueries({ queryKey: ['vendor-bookings'] });
    },
    onError: () => {
      toast.error('Failed to accept job');
    },
  });

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-destructive" />
          <h3 className="mt-2 text-lg font-semibold">Error Loading Jobs</h3>
          <p className="text-muted-foreground">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  // Separate bookings by status
  const pendingJobs = bookings?.filter(b => b.status === 'pending') || [];
  const activeJobs = bookings?.filter(b => ['confirmed', 'in_progress'].includes(b.status)) || [];
  const completedJobs = bookings?.filter(b => ['completed', 'signed'].includes(b.status)) || [];
  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">My Jobs</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage your assigned service jobs</p>
      </div>

      {/* Available Jobs (Pending) */}
      {pendingJobs.length > 0 && (
        <Card>
          <CardContent className="p-4 md:p-6">
            <h2 className="text-xl font-semibold mb-4">Available Jobs ({pendingJobs.length})</h2>
            <div className="grid grid-cols-1 gap-4">
              {pendingJobs.map((job) => (
                <Card key={job.id} className="border border-primary/20">
                  <CardContent className="p-4">
                    <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                      <div className="space-y-3 flex-1">
                        <div className="flex items-center gap-3">
                          <h3 className="text-lg font-semibold">{job.service_name || `Service #${job.service}`}</h3>
                          <Badge variant="secondary">New Job</Badge>
                        </div>

                        <p className="text-sm text-muted-foreground">Customer: {job.customer_name || `Customer #${job.customer}`}</p>

                        <div className="flex gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4" />
                            {new Date(job.scheduled_date).toLocaleDateString()}
                          </div>
                          <div className="flex items-center gap-1">
                            <MapPin className="h-4 w-4" />
                            {job.pincode}
                          </div>
                          <div className="flex items-center gap-1">
                            <DollarSign className="h-4 w-4" />
                            ₹{job.total_price}
                          </div>
                        </div>

                        {job.customer_notes && (
                          <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                            Note: {job.customer_notes}
                          </p>
                        )}
                      </div>

                      <div className="flex gap-2">
                        <Link to={`/vendor/job-list/${job.id}`}>
                          <Button variant="outline">View Details</Button>
                        </Link>
                        <Button 
                          onClick={() => acceptBookingMutation.mutate(job.id)}
                          disabled={acceptBookingMutation.isPending}
                        >
                          {acceptBookingMutation.isPending ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            'Accept Job'
                          )}
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Active Jobs */}
      {activeJobs.length > 0 && (
        <Card>
          <CardContent className="p-4 md:p-6">
            <h2 className="text-xl font-semibold mb-4">Active Jobs ({activeJobs.length})</h2>
            <div className="grid grid-cols-1 gap-4">
              {activeJobs.map((job) => (
                <Card key={job.id} className="card-elevated hover:shadow-lg transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                      <div className="space-y-3 flex-1">
                        <div className="flex items-center gap-3">
                          <h3 className="text-lg font-semibold">{job.service_name || `Service #${job.service}`}</h3>
                          <Badge
                            variant={job.status === 'in_progress' ? 'default' : 'secondary'}
                          >
                            {job.status.replace('_', ' ')}
                          </Badge>
                        </div>

                        <p className="text-sm text-muted-foreground">Customer: {job.customer_name || `Customer #${job.customer}`}</p>

                        <div className="flex gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4" />
                            {new Date(job.scheduled_date).toLocaleDateString()}
                          </div>
                          <div className="flex items-center gap-1">
                            <MapPin className="h-4 w-4" />
                            {job.pincode}
                          </div>
                          <div className="flex items-center gap-1">
                            <DollarSign className="h-4 w-4" />
                            ₹{job.total_price}
                          </div>
                        </div>
                      </div>

                      <Link to={`/vendor/job-list/${job.id}`} className="w-full md:w-auto">
                        <Button className="w-full md:w-auto">Manage Job</Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* No jobs message */}
      {pendingJobs.length === 0 && activeJobs.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Active Jobs</h3>
            <p className="text-muted-foreground">No jobs available at the moment. Check back later for new opportunities.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );

}
