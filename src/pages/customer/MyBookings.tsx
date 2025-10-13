import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, Calendar, MapPin, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { bookingService } from '@/services/bookingService';
import { toast } from 'sonner';
import { Loader } from '@/components/Loader';

export default function MyBookings() {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  // Fetch bookings from backend
  const { data: bookings, isLoading, error } = useQuery({
    queryKey: ['bookings'],
    queryFn: () => bookingService.getBookings(),
    onError: (error: any) => {
      toast.error('Failed to load bookings');
      console.error('Error loading bookings:', error);
    }
  });

  // Filter bookings based on search and filter
  const filteredBookings = (bookings || []).filter((booking) => {
    const serviceName = booking.service_name || booking.service_details?.name || '';
    const vendorName = booking.vendor_name || '';
    
    const matchesSearch = serviceName.toLowerCase().includes(search.toLowerCase()) ||
      vendorName.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || booking.status.toLowerCase() === filter.toLowerCase();
    return matchesSearch && matchesFilter;
  });

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'signed':
        return 'bg-success/10 text-success';
      case 'pending':
      case 'confirmed':
        return 'bg-warning/10 text-warning';
      case 'in_progress':
        return 'bg-blue-500/10 text-blue-600';
      case 'cancelled':
      case 'disputed':
        return 'bg-destructive/10 text-destructive';
      default:
        return 'bg-primary/10 text-primary';
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">My Bookings</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">Track and manage your service bookings</p>
        </div>
        <Link to="/customer/book-service" className="w-full sm:w-auto">
          <Button className="w-full sm:w-auto">Book New Service</Button>
        </Link>
      </div>

      {/* Search and Filter */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search bookings..."
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="all" onValueChange={setFilter}>
        <TabsList className="flex-wrap h-auto">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="signed">Signed</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
        </TabsList>

        <TabsContent value={filter} className="mt-6">
          <div className="grid grid-cols-1 gap-4">
            {filteredBookings.map((booking) => {
              const serviceName = booking.service_name || booking.service_details?.name || 'Service';
              const vendorName = booking.vendor_name || 'Not assigned';
              const scheduledDate = formatDate(booking.scheduled_date);
              const pincode = booking.pincode || 'N/A';
              
              return (
                <Card key={booking.id} className="card-elevated hover:shadow-lg transition-shadow">
                  <CardContent className="p-4 md:p-6">
                    <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                      <div className="space-y-3 flex-1">
                        <div>
                          <h3 className="text-lg font-semibold">{serviceName}</h3>
                          <p className="text-sm text-muted-foreground">Vendor: {vendorName}</p>
                        </div>

                        <div className="flex gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4" />
                            {scheduledDate}
                          </div>
                          <div className="flex items-center gap-1">
                            <MapPin className="h-4 w-4" />
                            {pincode}
                          </div>
                        </div>

                        <div className="flex items-center gap-3">
                          <span
                            className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                              getStatusColor(booking.status)
                            }`}
                          >
                            {booking.status.replace('_', ' ').charAt(0).toUpperCase() + booking.status.replace('_', ' ').slice(1)}
                          </span>
                          <span className="text-sm font-semibold text-primary">₹{booking.total_price}</span>
                        </div>
                      </div>

                      <Link to={`/customer/my-bookings/${booking.id}`} className="w-full md:w-auto">
                        <Button variant="outline" size="sm" className="w-full md:w-auto">
                          View Details
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {filteredBookings.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No bookings found</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}