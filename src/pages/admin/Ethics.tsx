import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Search, AlertTriangle, Calendar, Image as ImageIcon, Loader2, Eye, CheckCircle, XCircle, Loader } from 'lucide-react';
import { toast } from 'sonner';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminService } from '@/services/adminService';

interface EthicsFlag {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  booking_id: string;
  vendor_name: string;
  customer_name: string;
  created_at: string;
  reason: string;
  ai_score: number;
  status: 'pending' | 'under_review' | 'resolved' | 'dismissed';
  evidence?: string[];
  resolution_notes?: string;
  resolved_by?: string;
  resolved_at?: string;
}

export default function AdminEthics() {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [selectedFlag, setSelectedFlag] = useState<EthicsFlag | null>(null);
  const [resolutionNotes, setResolutionNotes] = useState('');
  const queryClient = useQueryClient();

  // Fetch AI ethics flags from backend
  const { data: flagsData, isLoading, error } = useQuery({
    queryKey: ['admin-ethics-flags', { search, filter }],
    queryFn: async () => {
      // In a real implementation, this would fetch from backend
      // For now, we'll simulate the data structure
      const businessAlerts = await adminService.getBusinessAlerts({
        type: 'ethics_flag',
        status: filter === 'all' ? undefined : filter,
        per_page: 50,
      });
      
      // Transform business alerts to ethics flags format
      return businessAlerts?.results?.map((alert: any) => ({
        id: alert.id.toString(),
        type: alert.alert_type || 'general',
        severity: alert.severity || 'medium',
        booking_id: alert.booking_id || 'N/A',
        vendor_name: alert.vendor_name || 'Unknown',
        customer_name: alert.customer_name || 'Unknown',
        created_at: alert.created_at,
        reason: alert.description || 'No reason provided',
        ai_score: alert.ai_score || 0,
        status: alert.status || 'pending',
        evidence: alert.evidence || [],
        resolution_notes: alert.resolution_notes,
        resolved_by: alert.resolved_by,
        resolved_at: alert.resolved_at,
      })) || [];
    },
  });

  // Resolve flag mutation
  const resolveFlagMutation = useMutation({
    mutationFn: async ({ flagId, action, notes }: { flagId: string; action: 'resolve' | 'dismiss'; notes: string }) => {
      // In a real implementation, this would update the backend
      await new Promise(resolve => setTimeout(resolve, 1000));
      return { flagId, action, notes };
    },
    onSuccess: () => {
      toast.success('Flag action completed successfully');
      queryClient.invalidateQueries({ queryKey: ['admin-ethics-flags'] });
      setSelectedFlag(null);
      setResolutionNotes('');
    },
    onError: () => {
      toast.error('Failed to process flag action');
    },
  });

  const handleResolveFlag = (flag: EthicsFlag, action: 'resolve' | 'dismiss') => {
    setSelectedFlag(flag);
  };

  const handleConfirmAction = () => {
    if (!selectedFlag) return;
    
    resolveFlagMutation.mutate({
      flagId: selectedFlag.id,
      action: 'resolve',
      notes: resolutionNotes,
    });
  };

  const handleDismissFlag = (flag: EthicsFlag) => {
    resolveFlagMutation.mutate({
      flagId: flag.id,
      action: 'dismiss',
      notes: 'Flag dismissed by admin',
    });
  };

  const filteredFlags = flagsData?.filter((flag: EthicsFlag) => {
    const matchesSearch =
      flag.booking_id.toLowerCase().includes(search.toLowerCase()) ||
      flag.vendor_name.toLowerCase().includes(search.toLowerCase()) ||
      flag.customer_name.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || flag.status === filter;
    return matchesSearch && matchesFilter;
  }) || [];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-blue-100 text-blue-800';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved': return 'bg-green-100 text-green-800';
      case 'under_review': return 'bg-blue-100 text-blue-800';
      case 'dismissed': return 'bg-gray-100 text-gray-800';
      case 'pending': return 'bg-orange-100 text-orange-800';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-center">
          <AlertTriangle className="mx-auto h-12 w-12 text-destructive" />
          <h3 className="mt-2 text-lg font-semibold">Error Loading Ethics Flags</h3>
          <p className="text-muted-foreground">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">AI Ethics & Flags</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">
          Track and review AI-flagged issues and ethical concerns
        </p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by booking ID, vendor, or customer..."
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        
        <Select value={filter} onValueChange={setFilter}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Flags</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="under_review">Under Review</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
            <SelectItem value="dismissed">Dismissed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Flags List */}
      <div className="grid grid-cols-1 gap-4">
        {filteredFlags.map((flag: EthicsFlag) => (
          <Card key={flag.id} className="card-elevated">
            <CardContent className="p-4 md:p-6">
              <div className="space-y-4">
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3">
                  <div className="flex-1 space-y-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-base md:text-lg font-semibold">
                        Booking {flag.booking_id}
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
                        <span className="font-medium">{flag.vendor_name}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Customer:</span>{' '}
                        <span className="font-medium">{flag.customer_name}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3 text-muted-foreground" />
                        <span className="text-muted-foreground">
                          {new Date(flag.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">AI Score:</span>{' '}
                        <span className="font-medium">{flag.ai_score}%</span>
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
                      {flag.evidence && flag.evidence.length > 0 && (
                        <div className="mt-2">
                          <span className="font-medium text-sm">Evidence:</span>
                          <div className="flex flex-wrap gap-2 mt-1">
                            {flag.evidence.map((evidence, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {evidence}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {flag.resolution_notes && (
                      <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                        <p className="text-sm text-green-800">
                          <span className="font-medium">Resolution Notes:</span> {flag.resolution_notes}
                        </p>
                        {flag.resolved_by && (
                          <p className="text-xs text-green-600 mt-1">
                            Resolved by {flag.resolved_by} on {new Date(flag.resolved_at || '').toLocaleDateString()}
                          </p>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col gap-2 w-full sm:w-auto">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button size="sm" className="w-full sm:w-auto">
                          <Eye className="h-4 w-4 mr-1" />
                          Review Details
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Flag Details - {flag.booking_id}</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="font-medium">Severity:</span>
                              <Badge className={`ml-2 ${getSeverityColor(flag.severity)}`}>
                                {flag.severity}
                              </Badge>
                            </div>
                            <div>
                              <span className="font-medium">Status:</span>
                              <Badge className={`ml-2 ${getStatusColor(flag.status)}`}>
                                {flag.status.replace('_', ' ')}
                              </Badge>
                            </div>
                            <div>
                              <span className="font-medium">AI Score:</span> {flag.ai_score}%
                            </div>
                            <div>
                              <span className="font-medium">Created:</span> {new Date(flag.created_at).toLocaleString()}
                            </div>
                          </div>
                          
                          <div>
                            <Label className="font-medium">Reason:</Label>
                            <p className="text-sm text-muted-foreground mt-1">{flag.reason}</p>
                          </div>

                          {flag.status === 'pending' && (
                            <div className="space-y-3">
                              <Label htmlFor="resolutionNotes">Resolution Notes</Label>
                              <Textarea
                                id="resolutionNotes"
                                placeholder="Add notes about how this flag was resolved..."
                                value={resolutionNotes}
                                onChange={(e) => setResolutionNotes(e.target.value)}
                                rows={3}
                              />
                              <div className="flex gap-2">
                                <Button 
                                  onClick={() => handleResolveFlag(flag, 'resolve')}
                                  disabled={resolveFlagMutation.isPending}
                                  className="flex-1"
                                >
                                  <CheckCircle className="h-4 w-4 mr-1" />
                                  Resolve
                                </Button>
                                <Button 
                                  variant="outline"
                                  onClick={() => handleDismissFlag(flag)}
                                  disabled={resolveFlagMutation.isPending}
                                  className="flex-1"
                                >
                                  <XCircle className="h-4 w-4 mr-1" />
                                  Dismiss
                                </Button>
                              </div>
                            </div>
                          )}
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredFlags.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <AlertTriangle className="mx-auto h-12 w-12 text-muted-foreground" />
          <h3 className="mt-2 text-lg font-semibold">No flags found</h3>
          <p className="text-muted-foreground">Try adjusting your search or filter criteria</p>
        </div>
      )}
    </div>
  );
}
