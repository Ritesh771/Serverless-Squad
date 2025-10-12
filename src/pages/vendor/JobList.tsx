import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar, MapPin, DollarSign } from 'lucide-react';
import { Link } from 'react-router-dom';

const mockJobs = [
  { id: '1', customer: 'John Doe', service: 'Plumbing', date: '2025-01-15', address: '123 Main St', status: 'assigned', payment: '$80' },
  { id: '2', customer: 'Jane Smith', service: 'Electrical', date: '2025-01-16', address: '456 Oak Ave', status: 'in-progress', payment: '$100' },
  { id: '3', customer: 'Bob Wilson', service: 'HVAC', date: '2025-01-17', address: '789 Pine Rd', status: 'assigned', payment: '$120' },
];

export default function VendorJobList() {
  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">My Jobs</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage your assigned service jobs</p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {mockJobs.map((job) => (
          <Card key={job.id} className="card-elevated hover:shadow-lg transition-shadow">
            <CardContent className="p-4 md:p-6">
              <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                <div className="space-y-3 flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold">{job.service}</h3>
                    <Badge
                      variant={job.status === 'in-progress' ? 'default' : 'secondary'}
                    >
                      {job.status.replace('-', ' ')}
                    </Badge>
                  </div>

                  <p className="text-sm text-muted-foreground">Customer: {job.customer}</p>

                  <div className="flex gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      {job.date}
                    </div>
                    <div className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      {job.address}
                    </div>
                    <div className="flex items-center gap-1">
                      <DollarSign className="h-4 w-4" />
                      {job.payment}
                    </div>
                  </div>
                </div>

                <Link to={`/vendor/job-list/${job.id}`} className="w-full md:w-auto">
                  <Button className="w-full md:w-auto">View Details</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
