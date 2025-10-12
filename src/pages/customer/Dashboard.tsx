import { DashboardCard } from '@/components/DashboardCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function CustomerDashboard() {
  const recentBookings = [
    { id: '1', service: 'Plumbing Repair', date: '2025-01-15', status: 'Pending', vendor: 'John Smith' },
    { id: '2', service: 'AC Maintenance', date: '2025-01-10', status: 'Completed', vendor: 'Sarah Johnson' },
    { id: '3', service: 'Electrical Inspection', date: '2025-01-08', status: 'Signed', vendor: 'Mike Davis' },
  ];

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-foreground">Welcome Back!</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage your home service bookings</p>
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
                      className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                        booking.status === 'Completed'
                          ? 'bg-success/10 text-success'
                          : booking.status === 'Pending'
                          ? 'bg-warning/10 text-warning'
                          : 'bg-primary/10 text-primary'
                      }`}
                    >
                      {booking.status}
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
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
