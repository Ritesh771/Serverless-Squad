import { useState, useEffect } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar, Clock, CheckCircle, AlertCircle, FileSignature, Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useWebSocket } from '@/hooks/useWebSocket';
import { toast } from 'sonner';

interface Booking {
  id: string;
  service: string;
  date: string;
  status: string;
  vendor: string;
}

export default function CustomerDashboard() {
  const [recentBookings, setRecentBookings] = useState<Booking[]>([
    { id: '1', service: 'Plumbing Repair', date: '2025-01-15', status: 'Pending', vendor: 'John Smith' },
    { id: '2', service: 'AC Maintenance', date: '2025-01-10', status: 'Completed', vendor: 'Sarah Johnson' },
    { id: '3', service: 'Electrical Inspection', date: '2025-01-08', status: 'Signed', vendor: 'Mike Davis' },
  ]);

  // WebSocket connection for real-time updates
  const { isConnected } = useWebSocket((data) => {
    if (data.type === 'booking_status_update') {
      // Update booking status in real-time
      setRecentBookings(prev => prev.map(booking => 
        booking.id === data.booking_id 
          ? { ...booking, status: data.status } 
          : booking
      ));
      
      // Show notification
      toast.success(`Booking status updated to ${data.status}`, {
        description: `Service: ${data.service_name || 'Unknown service'}`
      });
    } else if (data.type === 'signature_completed') {
      // Update booking status when signature is completed
      setRecentBookings(prev => prev.map(booking => 
        booking.id === data.booking_id 
          ? { ...booking, status: 'Signed' } 
          : booking
      ));
      
      toast.success('Signature completed successfully!', {
        description: 'Payment will be processed shortly'
      });
    }
  });

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
          value="3"
          icon={Calendar}
          description="Services in progress"
        />
        <DashboardCard
          title="Pending"
          value="1"
          icon={Clock}
          description="Awaiting vendor assignment"
        />
        <DashboardCard
          title="Completed"
          value="8"
          icon={CheckCircle}
          description="Last 30 days"
        />
        <DashboardCard
          title="Total Spent"
          value="$1,240"
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
                        booking.status === 'Completed'
                          ? 'bg-success/10 text-success'
                          : booking.status === 'Pending'
                          ? 'bg-warning/10 text-warning'
                          : booking.status === 'Signed'
                          ? 'bg-primary/10 text-primary'
                          : 'bg-secondary/10 text-secondary'
                      }`}
                    >
                      {booking.status === 'Signed' ? (
                        <>
                          <Check className="h-3 w-3" />
                          {booking.status}
                        </>
                      ) : (
                        booking.status
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
                {recentBookings
                  .filter(booking => booking.status === 'Completed')
                  .map(booking => (
                    <Link 
                      key={booking.id} 
                      to={`/customer/signature/${booking.id}`}
                      className="flex items-center justify-between p-2 border border-border rounded hover:bg-muted"
                    >
                      <div className="flex items-center gap-2">
                        <FileSignature className="h-4 w-4 text-primary" />
                        <span className="text-sm">{booking.service}</span>
                      </div>
                      <Button size="sm" variant="outline">
                        Sign Now
                      </Button>
                    </Link>
                  ))}
                {recentBookings.filter(booking => booking.status === 'Completed').length === 0 && (
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