import { useState, useEffect } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar, Clock, CheckCircle, AlertCircle, FileSignature, Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useWebSocket } from '@/hooks/useWebSocket';
import { toast } from 'sonner';
import { useQuery } from '@tanstack/react-query';
import { bookingService, Booking } from '@/services/bookingService';
import { signatureService } from '@/services/signatureService';
import { Loader } from '@/components/Loader';

export default function CustomerDashboard() {
  // Fetch real booking data
  const { data: bookings, isLoading, error } = useQuery({
    queryKey: ['customer-bookings'],
    queryFn: bookingService.getBookings,
  });

  // Fetch pending signatures
  const { data: signatures } = useQuery({
    queryKey: ['customer-signatures'],
    queryFn: signatureService.getSignatures,
  });

  // Calculate dashboard statistics from real data
  const stats = {
    activeBookings: bookings?.filter(b => ['confirmed', 'in_progress'].includes(b.status)).length || 0,
    pendingBookings: bookings?.filter(b => b.status === 'pending').length || 0,
    completedBookings: bookings?.filter(b => ['completed', 'signed'].includes(b.status)).length || 0,
    totalSpent: bookings?.reduce((sum, b) => sum + parseFloat(b.total_price || '0'), 0) || 0,
  };

  const pendingSignatures = signatures?.filter(s => s.status === 'pending') || [];
  const recentBookings = bookings?.slice(0, 5) || [];

  // WebSocket connection for real-time updates
  const { isConnected } = useWebSocket((data) => {
    if (data.type === 'booking_status_update') {
      // Refresh bookings when status changes
      toast.success(`Booking status updated to ${data.status}`, {
        description: `Service: ${data.service_name || 'Unknown service'}`
      });
    } else if (data.type === 'signature_completed') {
      toast.success('Signature completed successfully!', {
        description: 'Payment will be processed shortly'
      });
    }
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
          <h3 className="mt-2 text-lg font-semibold">Error Loading Dashboard</h3>
          <p className="text-muted-foreground">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-foreground">Welcome Back!</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage your home service bookings</p>
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
          title="Active Bookings"
          value={stats.activeBookings.toString()}
          icon={Calendar}
          description="Services in progress"
        />
        <DashboardCard
          title="Pending"
          value={stats.pendingBookings.toString()}
          icon={Clock}
          description="Awaiting vendor assignment"
        />
        <DashboardCard
          title="Completed"
          value={stats.completedBookings.toString()}
          icon={CheckCircle}
          description="Last 30 days"
        />
        <DashboardCard
          title="Total Spent"
          value={`₹${stats.totalSpent.toFixed(2)}`}
          icon={AlertCircle}
          description="This month"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Bookings */}
        <Card className="lg:col-span-2 card-elevated">
          <CardHeader>
            <CardTitle>Recent Bookings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentBookings.map((booking) => (
                <Link
                  key={booking.id}
                  to={`/customer/my-bookings/${booking.id}`}
                  className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted transition-colors"
                >
                  <div>
                    <p className="font-medium">{booking.service}</p>
                    <p className="text-sm text-muted-foreground">Vendor: {booking.vendor}</p>
                  </div>
                  <div className="text-right">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                        booking.status === 'completed'
                          ? 'bg-success/10 text-success'
                          : booking.status === 'pending'
                          ? 'bg-warning/10 text-warning'
                          : booking.status === 'signed'
                          ? 'bg-primary/10 text-primary'
                          : 'bg-secondary/10 text-secondary'
                      }`}
                    >
                      {booking.status === 'signed' ? (
                        <>
                          <Check className="h-3 w-3" />
                          {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                        </>
                      ) : (
                        booking.status.charAt(0).toUpperCase() + booking.status.slice(1)
                      )}
                    </span>
                    <p className="text-xs text-muted-foreground mt-1">{booking.date}</p>
                  </div>
                </Link>
              ))}
            </div>
            <Link to="/customer/my-bookings">
              <Button variant="outline" className="w-full mt-4">
                View All Bookings
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="card-elevated">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link to="/customer/book-service">
              <Button className="w-full">Book New Service</Button>
            </Link>
            <Link to="/customer/my-bookings">
              <Button variant="outline" className="w-full">
                View My Bookings
              </Button>
            </Link>
            <Link to="/customer/chat">
              <Button variant="outline" className="w-full">
                Contact Support
              </Button>
            </Link>
            <div className="pt-2">
              <h3 className="text-sm font-medium mb-2">Pending Signatures</h3>
              <div className="space-y-2">
                {pendingSignatures.map(signature => {
                  const booking = bookings?.find(b => b.id === signature.booking);
                  return (
                    <Link 
                      key={signature.id} 
                      to={`/customer/signature/${signature.id}`}
                      className="flex items-center justify-between p-2 border border-border rounded hover:bg-muted"
                    >
                      <div className="flex items-center gap-2">
                        <FileSignature className="h-4 w-4 text-primary" />
                        <span className="text-sm">{booking?.service_name || 'Service'}</span>
                      </div>
                      <Button size="sm" variant="outline">
                        Sign Now
                      </Button>
                    </Link>
                  );
                })}
                {pendingSignatures.length === 0 && (
                  <p className="text-xs text-muted-foreground py-2">No pending signatures</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}