import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Calendar, MapPin, AlertTriangle } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

interface VendorApplication {
  id: string;
  name: string;
  service: string;
  location: string;
  date: string;
  status: string;
  experience: string;
  ai_flag?: boolean;
  flag_reason?: string;
}

const mockApplications: VendorApplication[] = [
  { id: '1', name: 'Mike Johnson', service: 'Plumbing', location: 'New York', date: '2025-01-15', status: 'pending', experience: '5 years', ai_flag: true, flag_reason: 'Incomplete profile' },
  { id: '2', name: 'Sarah Williams', service: 'Electrical', location: 'Los Angeles', date: '2025-01-14', status: 'under-review', experience: '8 years' },
  { id: '3', name: 'Tom Davis', service: 'HVAC', location: 'Chicago', date: '2025-01-13', status: 'pending', experience: '3 years', ai_flag: true, flag_reason: 'Multiple applications' },
  { id: '4', name: 'Emily Brown', service: 'Carpentry', location: 'Houston', date: '2025-01-12', status: 'pending', experience: '6 years' },
];

export default function VendorQueue() {
  const [search, setSearch] = useState('');
  const location = useLocation();
  const flaggedOnly = new URLSearchParams(location.search).get('flagged_only') === 'true';

  const filteredApplications = mockApplications
    .filter((app) => {
      // Filter by flagged applications if requested
      if (flaggedOnly && !app.ai_flag) {
        return false;
      }
      
      // Filter by search term
      return (
        app.name.toLowerCase().includes(search.toLowerCase()) ||
        app.service.toLowerCase().includes(search.toLowerCase())
      );
    });

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Vendor Application Queue</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">
          {flaggedOnly ? 'Flagged applications requiring attention' : 'Review and process vendor applications'}
        </p>
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

      {/* Toggle for flagged applications */}
      <div className="flex items-center gap-2">
        <Link to={flaggedOnly ? '/onboard/vendor-queue' : '/onboard/vendor-queue?flagged_only=true'}>
          <Button variant={flaggedOnly ? 'default' : 'outline'} size="sm">
            <AlertTriangle className="h-4 w-4 mr-2" />
            {flaggedOnly ? 'Show All Applications' : 'Show Flagged Only'}
          </Button>
        </Link>
        {flaggedOnly && (
          <span className="text-sm text-muted-foreground">
            Showing {filteredApplications.length} flagged applications
          </span>
        )}
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
                    {app.ai_flag && (
                      <Badge variant="destructive" className="flex items-center gap-1">
                        <AlertTriangle className="h-3 w-3" />
                        Flagged
                      </Badge>
                    )}
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

                  {app.ai_flag && app.flag_reason && (
                    <div className="mt-2 p-2 bg-warning/10 rounded text-sm">
                      <span className="font-medium">Flag Reason:</span> {app.flag_reason}
                    </div>
                  )}
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