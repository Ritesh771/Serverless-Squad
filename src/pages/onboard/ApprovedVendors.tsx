import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, MapPin, Star } from 'lucide-react';

const mockVendors = [
  { id: '1', name: 'John Smith', service: 'Plumbing', location: 'New York', rating: 4.9, jobs: 127, approvedDate: '2024-12-01' },
  { id: '2', name: 'Sarah Johnson', service: 'Electrical', location: 'Los Angeles', rating: 4.8, jobs: 93, approvedDate: '2024-11-15' },
  { id: '3', name: 'Mike Davis', service: 'HVAC', location: 'Chicago', rating: 4.7, jobs: 156, approvedDate: '2024-10-20' },
  { id: '4', name: 'Emma Wilson', service: 'Carpentry', location: 'Houston', rating: 4.9, jobs: 84, approvedDate: '2024-12-10' },
];

export default function ApprovedVendors() {
  const [search, setSearch] = useState('');

  const filteredVendors = mockVendors.filter((vendor) =>
    vendor.name.toLowerCase().includes(search.toLowerCase()) ||
    vendor.service.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Approved Vendors</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">View all active vendors in the platform</p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search vendors..."
          className="pl-10"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Vendors */}
      <div className="grid grid-cols-1 gap-4">
        {filteredVendors.map((vendor) => (
          <Card key={vendor.id} className="card-elevated hover:shadow-lg transition-shadow">
            <CardContent className="p-4 md:p-6">
              <div className="space-y-3">
                <div className="flex items-center gap-3 flex-wrap">
                  <h3 className="text-base md:text-lg font-semibold">{vendor.name}</h3>
                  <Badge className="bg-success text-success-foreground">
                    Active
                  </Badge>
                </div>

                <div className="flex flex-col sm:flex-row sm:gap-4 gap-2 text-sm text-muted-foreground">
                  <div>
                    <span className="font-medium">Service:</span> {vendor.service}
                  </div>
                  <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    {vendor.location}
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row sm:gap-6 gap-2 text-sm">
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 fill-warning text-warning" />
                    <span className="font-medium">{vendor.rating}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Jobs:</span>{' '}
                    <span className="font-medium">{vendor.jobs}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Approved:</span>{' '}
                    <span className="font-medium">{vendor.approvedDate}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
