import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, AlertTriangle, Calendar, Image as ImageIcon } from 'lucide-react';

const mockFlags = [
  {
    id: '1',
    type: 'photo_quality',
    severity: 'high',
    booking: 'BK-12345',
    vendor: 'John Smith',
    customer: 'Jane Doe',
    date: '2025-01-15',
    reason: 'Before/after photos show insufficient quality difference',
    aiScore: 62,
    status: 'pending',
  },
  {
    id: '2',
    type: 'signature_delay',
    severity: 'medium',
    booking: 'BK-12346',
    vendor: 'Mike Davis',
    customer: 'Bob Wilson',
    date: '2025-01-14',
    reason: 'Signature requested 48 hours after job completion',
    aiScore: 75,
    status: 'resolved',
  },
  {
    id: '3',
    type: 'pricing_anomaly',
    severity: 'high',
    booking: 'BK-12347',
    vendor: 'Sarah Johnson',
    customer: 'Alice Brown',
    date: '2025-01-13',
    reason: 'Price significantly higher than area average for service',
    aiScore: 58,
    status: 'under_review',
  },
];

export default function AdminEthics() {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const filteredFlags = mockFlags.filter((flag) => {
    const matchesSearch =
      flag.booking.toLowerCase().includes(search.toLowerCase()) ||
      flag.vendor.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || flag.status === filter;
    return matchesSearch && matchesFilter;
  });

  const getSeverityColor = (severity: string) => {
    return severity === 'high'
      ? 'bg-destructive/10 text-destructive'
      : severity === 'medium'
      ? 'bg-warning/10 text-warning'
      : 'bg-muted text-muted-foreground';
  };

  const getStatusColor = (status: string) => {
    return status === 'resolved'
      ? 'bg-success/10 text-success'
      : status === 'under_review'
      ? 'bg-warning/10 text-warning'
      : 'bg-muted text-muted-foreground';
  };

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">AI Ethics & Flags</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">
          Track and review AI-flagged issues
        </p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search by booking ID or vendor..."
          className="pl-10"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Tabs */}
      <Tabs defaultValue="all" onValueChange={setFilter}>
        <TabsList className="flex-wrap h-auto">
          <TabsTrigger value="all">All Flags</TabsTrigger>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="under_review">Under Review</TabsTrigger>
          <TabsTrigger value="resolved">Resolved</TabsTrigger>
        </TabsList>

        <TabsContent value={filter} className="mt-6">
          <div className="grid grid-cols-1 gap-4">
            {filteredFlags.map((flag) => (
              <Card key={flag.id} className="card-elevated">
                <CardContent className="p-4 md:p-6">
                  <div className="space-y-4">
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3">
                      <div className="flex-1 space-y-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-base md:text-lg font-semibold">
                            Booking {flag.booking}
                          </h3>
                          <Badge className={getSeverityColor(flag.severity)}>
                            <AlertTriangle className="h-3 w-3 mr-1" />
                            {flag.severity}
                          </Badge>
                          <Badge className={getStatusColor(flag.status)}>
                            {flag.status.replace('_', ' ')}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                          <div>
                            <span className="text-muted-foreground">Vendor:</span>{' '}
                            <span className="font-medium">{flag.vendor}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Customer:</span>{' '}
                            <span className="font-medium">{flag.customer}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3 text-muted-foreground" />
                            <span className="text-muted-foreground">{flag.date}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">AI Score:</span>{' '}
                            <span className="font-medium">{flag.aiScore}%</span>
                          </div>
                        </div>

                        <div className="p-3 bg-muted rounded-lg">
                          <p className="text-sm">
                            <span className="font-medium">Flag Type:</span>{' '}
                            <span className="capitalize">
                              {flag.type.replace('_', ' ')}
                            </span>
                          </p>
                          <p className="text-sm mt-2">
                            <span className="font-medium">Reason:</span> {flag.reason}
                          </p>
                        </div>
                      </div>

                      <div className="flex flex-col gap-2 w-full sm:w-auto">
                        <Button size="sm" className="w-full sm:w-auto">
                          Review Details
                        </Button>
                        {flag.status === 'pending' && (
                          <>
                            <Button
                              variant="outline"
                              size="sm"
                              className="w-full sm:w-auto"
                            >
                              Escalate
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              className="w-full sm:w-auto"
                            >
                              Dismiss
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredFlags.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No flags found</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
