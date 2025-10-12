import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, Calendar, MapPin } from 'lucide-react';
import { Link } from 'react-router-dom';

const mockBookings = [
  { id: '1', service: 'Plumbing Repair', vendor: 'John Smith', date: '2025-01-15', address: '123 Main St', status: 'Pending', price: '$80' },
  { id: '2', service: 'AC Maintenance', vendor: 'Sarah Johnson', date: '2025-01-10', address: '456 Oak Ave', status: 'Completed', price: '$120' },
  { id: '3', service: 'Electrical Inspection', vendor: 'Mike Davis', date: '2025-01-08', address: '789 Pine Rd', status: 'Signed', price: '$100' },
  { id: '4', service: 'Carpentry Work', vendor: 'Emma Wilson', date: '2025-01-05', address: '321 Elm St', status: 'Completed', price: '$150' },
];

export default function MyBookings() {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const filteredBookings = mockBookings.filter((booking) => {
    const matchesSearch = booking.service.toLowerCase().includes(search.toLowerCase()) ||
      booking.vendor.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || booking.status.toLowerCase() === filter.toLowerCase();
    return matchesSearch && matchesFilter;
  });

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
            {filteredBookings.map((booking) => (
              <Card key={booking.id} className="card-elevated hover:shadow-lg transition-shadow">
                <CardContent className="p-4 md:p-6">
                  <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                    <div className="space-y-3 flex-1">
                      <div>
                        <h3 className="text-lg font-semibold">{booking.service}</h3>
                        <p className="text-sm text-muted-foreground">Vendor: {booking.vendor}</p>
                      </div>

                      <div className="flex gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          {booking.date}
                        </div>
                        <div className="flex items-center gap-1">
                          <MapPin className="h-4 w-4" />
                          {booking.address}
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <span
                          className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                            booking.status === 'Completed'
                              ? 'bg-success/10 text-success'
                              : booking.status === 'Pending'
                              ? 'bg-warning/10 text-warning'
                              : 'bg-primary/10 text-primary'
                          }`}
                        >
                          {booking.status}
                        </span>
                        <span className="text-sm font-semibold text-primary">{booking.price}</span>
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
            ))}
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
