import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, Calendar, MapPin } from 'lucide-react';

const mockBookings = [
  { id: '1', customer: 'Jane Doe', vendor: 'John Smith', service: 'Plumbing', date: '2025-01-15', location: 'New York', status: 'in-progress', amount: '$80' },
  { id: '2', customer: 'Bob Wilson', vendor: 'Sarah Johnson', service: 'Electrical', date: '2025-01-16', location: 'Los Angeles', status: 'assigned', amount: '$100' },
  { id: '3', customer: 'Alice Brown', vendor: 'Mike Davis', service: 'HVAC', date: '2025-01-17', location: 'Chicago', status: 'pending', amount: '$120' },
  { id: '4', customer: 'Tom White', vendor: 'Emma Wilson', service: 'Carpentry', date: '2025-01-14', location: 'Houston', status: 'completed', amount: '$90' },
];

export default function BookingsMonitor() {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const filteredBookings = mockBookings.filter((booking) => {
    const matchesSearch =
      booking.customer.toLowerCase().includes(search.toLowerCase()) ||
      booking.vendor.toLowerCase().includes(search.toLowerCase()) ||
      booking.service.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || booking.status === filter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Bookings Monitor</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Real-time view of all platform bookings</p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search bookings..."
          className="pl-10"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Tabs */}
      <Tabs defaultValue="all" onValueChange={setFilter}>
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="assigned">Assigned</TabsTrigger>
          <TabsTrigger value="in-progress">In Progress</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
        </TabsList>

        <TabsContent value={filter} className="mt-6">
          <div className="grid grid-cols-1 gap-4">
            {filteredBookings.map((booking) => (
              <Card key={booking.id} className="card-elevated">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold">{booking.service}</h3>
                        <Badge
                          variant={
                            booking.status === 'completed'
                              ? 'default'
                              : 'secondary'
                          }
                        >
                          {booking.status.replace('-', ' ')}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
                        <div>
                          <span className="font-medium">Customer:</span> {booking.customer}
                        </div>
                        <div>
                          <span className="font-medium">Vendor:</span> {booking.vendor}
                        </div>
                      </div>

                      <div className="flex gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          {booking.date}
                        </div>
                        <div className="flex items-center gap-1">
                          <MapPin className="h-4 w-4" />
                          {booking.location}
                        </div>
                        <div className="font-medium text-primary">{booking.amount}</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
