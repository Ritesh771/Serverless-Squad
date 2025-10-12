import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText, Download, Calendar } from 'lucide-react';
import { toast } from 'sonner';

const reports = [
  { name: 'User Activity Report', description: 'Detailed user engagement metrics', period: 'Monthly', format: 'CSV/PDF' },
  { name: 'Financial Report', description: 'Revenue and transaction summary', period: 'Monthly', format: 'Excel/PDF' },
  { name: 'Vendor Performance', description: 'Vendor ratings and completion stats', period: 'Monthly', format: 'PDF' },
  { name: 'System Health Report', description: 'Technical metrics and uptime', period: 'Weekly', format: 'PDF' },
  { name: 'Security Audit', description: 'Security events and compliance', period: 'Monthly', format: 'PDF' },
];

export default function AdminReports() {
  const handleExport = (reportName: string) => {
    toast.success(`Exporting ${reportName}...`);
  };

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Reports</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Generate and export system reports</p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {reports.map((report, index) => (
          <Card key={index} className="card-elevated">
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

                  <div className="flex gap-6 text-sm text-muted-foreground ml-8">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {report.period}
                    </div>
                    <div>Format: {report.format}</div>
                  </div>
                </div>

                <Button onClick={() => handleExport(report.name)} className="w-full sm:w-auto">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
