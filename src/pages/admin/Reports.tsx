import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { FileText, Download, Calendar as CalendarIcon, Loader2, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { useQuery } from '@tanstack/react-query';
import { adminService } from '@/services/adminService';
import { Loader } from '@/components/Loader';
import { format } from 'date-fns';

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  formats: string[];
  requiresDateRange: boolean;
}

const reportTemplates: ReportTemplate[] = [
  { 
    id: 'user_activity', 
    name: 'User Activity Report', 
    description: 'Detailed user engagement and platform usage metrics', 
    category: 'Users',
    formats: ['CSV', 'PDF'],
    requiresDateRange: true
  },
  { 
    id: 'financial', 
    name: 'Financial Report', 
    description: 'Revenue, transactions, and payment analytics', 
    category: 'Finance',
    formats: ['Excel', 'PDF'],
    requiresDateRange: true
  },
  { 
    id: 'vendor_performance', 
    name: 'Vendor Performance', 
    description: 'Vendor ratings, completion stats, and earnings', 
    category: 'Vendors',
    formats: ['PDF', 'CSV'],
    requiresDateRange: true
  },
  { 
    id: 'booking_analytics', 
    name: 'Booking Analytics', 
    description: 'Service booking trends and completion rates', 
    category: 'Operations',
    formats: ['PDF', 'Excel'],
    requiresDateRange: true
  },
  { 
    id: 'pincode_analytics', 
    name: 'Pincode Analytics', 
    description: 'Geographic performance and demand patterns', 
    category: 'Analytics',
    formats: ['PDF'],
    requiresDateRange: true
  },
  { 
    id: 'audit_logs', 
    name: 'Audit Logs', 
    description: 'System activity and security audit trail', 
    category: 'Security',
    formats: ['CSV', 'PDF'],
    requiresDateRange: true
  },
];

export default function AdminReports() {
  const [selectedReport, setSelectedReport] = useState<string>('');
  const [dateFrom, setDateFrom] = useState<Date>();
  const [dateTo, setDateTo] = useState<Date>();
  const [format, setFormat] = useState<string>('');
  const [isExporting, setIsExporting] = useState(false);

  // Fetch dashboard stats for quick overview
  const { data: dashboardStats, isLoading } = useQuery({
    queryKey: ['admin-dashboard-stats'],
    queryFn: adminService.getDashboardStats,
  });

  const handleExport = async (reportId: string) => {
    if (!selectedReport) {
      toast.error('Please select a report');
      return;
    }

    if (!format) {
      toast.error('Please select an export format');
      return;
    }

    setIsExporting(true);
    
    try {
      let exportData;
      
      switch (reportId) {
        case 'audit_logs':
          exportData = await adminService.exportEditHistory({
            start_date: dateFrom?.toISOString().split('T')[0],
            end_date: dateTo?.toISOString().split('T')[0],
            format: format.toLowerCase(),
          });
          break;
        case 'pincode_analytics':
          exportData = await adminService.getPincodeAnalytics({
            date_from: dateFrom?.toISOString().split('T')[0],
            date_to: dateTo?.toISOString().split('T')[0],
          });
          break;
        default:
          // For other reports, we would call specific backend endpoints
          throw new Error('Report type not yet implemented');
      }

      // Create and download file
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
        type: format === 'PDF' ? 'application/pdf' : 'text/csv' 
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedReport}-${new Date().toISOString().split('T')[0]}.${format.toLowerCase()}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast.success('Report exported successfully');
    } catch (error) {
      toast.error('Failed to export report');
      console.error('Export error:', error);
    } finally {
      setIsExporting(false);
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
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Reports & Analytics</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Generate and export comprehensive system reports</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="card-elevated">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Users</p>
                <p className="text-lg font-semibold">{dashboardStats?.user_stats?.total_users || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="card-elevated">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-success/10 rounded-lg">
                <CalendarIcon className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Bookings Today</p>
                <p className="text-lg font-semibold">{dashboardStats?.booking_stats?.total_today || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="card-elevated">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-warning/10 rounded-lg">
                <AlertCircle className="h-5 w-5 text-warning" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Pending Signatures</p>
                <p className="text-lg font-semibold">{dashboardStats?.signature_stats?.pending || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Report Configuration */}
      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Report Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Select Report</label>
              <Select value={selectedReport} onValueChange={setSelectedReport}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a report type" />
                </SelectTrigger>
                <SelectContent>
                  {reportTemplates.map((template) => (
                    <SelectItem key={template.id} value={template.id}>
                      {template.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Export Format</label>
              <Select value={format} onValueChange={setFormat}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose format" />
                </SelectTrigger>
                <SelectContent>
                  {selectedReport && reportTemplates.find(r => r.id === selectedReport)?.formats.map((fmt) => (
                    <SelectItem key={fmt} value={fmt}>{fmt}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {selectedReport && reportTemplates.find(r => r.id === selectedReport)?.requiresDateRange && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">From Date</label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className="w-full justify-start text-left font-normal">
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {dateFrom ? format(dateFrom, "PPP") : "Select date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={dateFrom}
                      onSelect={setDateFrom}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">To Date</label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className="w-full justify-start text-left font-normal">
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {dateTo ? format(dateTo, "PPP") : "Select date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={dateTo}
                      onSelect={setDateTo}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
            </div>
          )}

          <Button 
            onClick={() => handleExport(selectedReport)} 
            disabled={!selectedReport || !format || isExporting}
            className="w-full"
          >
            {isExporting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Exporting...
              </>
            ) : (
              <>
                <Download className="mr-2 h-4 w-4" />
                Export Report
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Available Reports */}
      <div className="grid grid-cols-1 gap-4">
        {reportTemplates.map((report) => (
          <Card key={report.id} className="card-elevated">
            <CardContent className="p-4 md:p-6">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-primary" />
                    <div>
                      <h3 className="font-semibold">{report.name}</h3>
                      <p className="text-sm text-muted-foreground">{report.description}</p>
                    </div>
                  </div>

                  <div className="flex gap-6 text-sm text-muted-foreground ml-8 flex-wrap">
                    <div className="flex items-center gap-1">
                      <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded">
                        {report.category}
                      </span>
                    </div>
                    <div>Formats: {report.formats.join(', ')}</div>
                    {report.requiresDateRange && (
                      <div className="flex items-center gap-1">
                        <CalendarIcon className="h-3 w-3" />
                        Date range required
                      </div>
                    )}
                  </div>
                </div>

                <Button 
                  onClick={() => {
                    setSelectedReport(report.id);
                    setFormat(report.formats[0]);
                  }}
                  variant="outline"
                  className="w-full sm:w-auto"
                >
                  Configure
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
