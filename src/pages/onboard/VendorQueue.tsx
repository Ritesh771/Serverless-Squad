import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Calendar, MapPin } from 'lucide-react';
import { Link } from 'react-router-dom';

const mockApplications = [
  { id: '1', name: 'Mike Johnson', service: 'Plumbing', location: 'New York', date: '2025-01-15', status: 'pending', experience: '5 years' },
  { id: '2', name: 'Sarah Williams', service: 'Electrical', location: 'Los Angeles', date: '2025-01-14', status: 'under-review', experience: '8 years' },
  { id: '3', name: 'Tom Davis', service: 'HVAC', location: 'Chicago', date: '2025-01-13', status: 'pending', experience: '3 years' },
  { id: '4', name: 'Emily Brown', service: 'Carpentry', location: 'Houston', date: '2025-01-12', status: 'pending', experience: '6 years' },
];

export default function VendorQueue() {
  const [search, setSearch] = useState('');

  const filteredApplications = mockApplications.filter((app) =>
    app.name.toLowerCase().includes(search.toLowerCase()) ||
    app.service.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Vendor Application Queue</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Review and process vendor applications</p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search applications..."
          className="pl-10"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Applications */}
      <div className="grid grid-cols-1 gap-4">
        {filteredApplications.map((app) => (
          <Card key={app.id} className="card-elevated hover:shadow-lg transition-shadow">
            <CardContent className="p-4 md:p-6">
              <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                <div className="space-y-3 flex-1">
                  <div className="flex items-center gap-3 flex-wrap">
                    <h3 className="text-base md:text-lg font-semibold">{app.name}</h3>
                    <Badge variant={app.status === 'under-review' ? 'default' : 'secondary'}>
                      {app.status.replace('-', ' ')}
                    </Badge>
                  </div>

                  <div className="flex flex-col sm:flex-row sm:gap-4 gap-2 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <span className="font-medium">Service:</span> {app.service}
                    </div>
                    <div className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      {app.location}
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      {app.date}
                    </div>
                  </div>

                  <div className="text-sm">
                    <span className="text-muted-foreground">Experience: </span>
                    <span className="font-medium">{app.experience}</span>
                  </div>
                </div>

                <Link to={`/onboard/vendor-queue/${app.id}`} className="w-full md:w-auto">
                  <Button className="w-full md:w-auto">Review</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
