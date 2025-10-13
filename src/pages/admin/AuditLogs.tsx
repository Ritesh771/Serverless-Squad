import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Calendar, User, FileText, Download, Filter, Loader2, AlertCircle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { adminService } from '@/services/adminService';
import { Loader } from '@/components/Loader';
import { toast } from 'sonner';

interface AuditLog {
  id: number;
  action: string;
  user: string;
  timestamp: string;
  model: string;
  details: string;
  ip_address?: string;
  user_agent?: string;
}

interface AuditLogsResponse {
  data: AuditLog[];
  pagination: {
    total_count: number;
  };
}

export default function AdminAuditLogs() {
  const [search, setSearch] = useState('');
  const [modelFilter, setModelFilter] = useState('all');
  const [actionFilter, setActionFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Fetch audit logs from backend
  const { data: auditData, isLoading, error } = useQuery<AuditLogsResponse>({
    queryKey: ['audit-logs', { search, modelFilter, actionFilter, page, pageSize }],
    queryFn: () => adminService.getEditHistory({
      model: modelFilter !== 'all' ? modelFilter : undefined,
      action: actionFilter !== 'all' ? actionFilter : undefined,
      page,
      page_size: pageSize,
    }) as Promise<AuditLogsResponse>,
  });

  const auditLogs = auditData?.data || [];
  const totalPages = Math.ceil((auditData?.pagination?.total_count || 0) / pageSize);

  const handleExport = async () => {
    try {
      const exportData = await adminService.exportEditHistory({
        model: modelFilter !== 'all' ? modelFilter : undefined,
        action: actionFilter !== 'all' ? actionFilter : undefined,
      });
      
      // Create and download CSV file
      const blob = new Blob([exportData as BlobPart], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast.success('Audit logs exported successfully');
    } catch (error) {
      toast.error('Failed to export audit logs');
    }
  };

  const filteredLogs = auditLogs.filter((log: AuditLog) =>
    log.action.toLowerCase().includes(search.toLowerCase()) ||
    log.user.toLowerCase().includes(search.toLowerCase()) ||
    log.details.toLowerCase().includes(search.toLowerCase())
  );

  const getTypeColor = (model: string) => {
    const colors: Record<string, string> = {
      'User': 'bg-primary/10 text-primary',
      'Booking': 'bg-success/10 text-success',
      'Payment': 'bg-warning/10 text-warning',
      'Signature': 'bg-blue-100 text-blue-800',
      'VendorApplication': 'bg-purple-100 text-purple-800',
      'Dispute': 'bg-red-100 text-red-800',
      'Service': 'bg-green-100 text-green-800',
    };
    return colors[model] || 'bg-muted text-muted-foreground';
  };

  const getActionColor = (action: string) => {
    const colors: Record<string, string> = {
      'CREATE': 'bg-green-100 text-green-800',
      'UPDATE': 'bg-blue-100 text-blue-800',
      'DELETE': 'bg-red-100 text-red-800',
      'LOGIN': 'bg-purple-100 text-purple-800',
      'LOGOUT': 'bg-gray-100 text-gray-800',
    };
    return colors[action] || 'bg-muted text-muted-foreground';
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
          <AlertCircle className="mx-auto h-12 w-12 text-destructive" />
          <h3 className="mt-2 text-lg font-semibold">Error Loading Audit Logs</h3>
          <p className="text-muted-foreground">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">Audit Logs</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">Append-only system activity log</p>
        </div>
        <Button onClick={handleExport} variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Export CSV
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search logs..."
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        
        <Select value={modelFilter} onValueChange={setModelFilter}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="All Models" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Models</SelectItem>
            <SelectItem value="User">User</SelectItem>
            <SelectItem value="Booking">Booking</SelectItem>
            <SelectItem value="Payment">Payment</SelectItem>
            <SelectItem value="Signature">Signature</SelectItem>
            <SelectItem value="VendorApplication">Vendor Application</SelectItem>
            <SelectItem value="Dispute">Dispute</SelectItem>
          </SelectContent>
        </Select>

        <Select value={actionFilter} onValueChange={setActionFilter}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="All Actions" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Actions</SelectItem>
            <SelectItem value="CREATE">Create</SelectItem>
            <SelectItem value="UPDATE">Update</SelectItem>
            <SelectItem value="DELETE">Delete</SelectItem>
            <SelectItem value="LOGIN">Login</SelectItem>
            <SelectItem value="LOGOUT">Logout</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Logs */}
      <div className="grid grid-cols-1 gap-3">
        {filteredLogs.map((log: AuditLog) => (
          <Card key={log.id} className="card-elevated">
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-3 flex-wrap">
                    <FileText className="h-4 w-4 text-primary" />
                    <h4 className="font-medium">{log.action}</h4>
                    <Badge className={getTypeColor(log.model)}>
                      {log.model}
                    </Badge>
                    <Badge className={getActionColor(log.action)}>
                      {log.action}
                    </Badge>
                  </div>

                  <div className="flex gap-6 text-sm text-muted-foreground ml-7 flex-wrap">
                    <div className="flex items-center gap-1">
                      <User className="h-3 w-3" />
                      {log.user}
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {new Date(log.timestamp).toLocaleString()}
                    </div>
                    {log.ip_address && (
                      <div className="flex items-center gap-1">
                        <span className="text-xs">IP: {log.ip_address}</span>
                      </div>
                    )}
                  </div>

                  <p className="text-sm text-muted-foreground ml-7">
                    {log.details}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
          >
            Next
          </Button>
        </div>
      )}

      {filteredLogs.length === 0 && !isLoading && (
        <div className="text-center py-8">
          <FileText className="mx-auto h-12 w-12 text-muted-foreground" />
          <h3 className="mt-2 text-lg font-semibold">No audit logs found</h3>
          <p className="text-muted-foreground">Try adjusting your search or filter criteria</p>
        </div>
      )}
    </div>
  );
}