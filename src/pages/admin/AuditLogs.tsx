import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Calendar, User, FileText } from 'lucide-react';

const mockLogs = [
  { id: '1', action: 'User login', user: 'john@example.com', timestamp: '2025-01-15 10:30:00', type: 'auth', details: 'Successful login from 192.168.1.1' },
  { id: '2', action: 'Payment processed', user: 'system', timestamp: '2025-01-15 10:25:00', type: 'payment', details: 'Payment BK-12345 processed successfully' },
  { id: '3', action: 'User role updated', user: 'admin@homeserve.com', timestamp: '2025-01-15 09:15:00', type: 'admin', details: 'Changed role from customer to vendor' },
  { id: '4', action: 'Signature verified', user: 'system', timestamp: '2025-01-15 08:45:00', type: 'signature', details: 'Digital signature hash verified on blockchain' },
];

export default function AdminAuditLogs() {
  const [search, setSearch] = useState('');

  const filteredLogs = mockLogs.filter((log) =>
    log.action.toLowerCase().includes(search.toLowerCase()) ||
    log.user.toLowerCase().includes(search.toLowerCase())
  );

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      auth: 'bg-primary/10 text-primary',
      payment: 'bg-success/10 text-success',
      admin: 'bg-warning/10 text-warning',
      signature: 'bg-primary/10 text-primary',
    };
    return colors[type] || 'bg-muted text-muted-foreground';
  };

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Audit Logs</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Append-only system activity log</p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search logs..."
          className="pl-10"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Logs */}
      <div className="grid grid-cols-1 gap-3">
        {filteredLogs.map((log) => (
          <Card key={log.id} className="card-elevated">
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-3">
                    <FileText className="h-4 w-4 text-primary" />
                    <h4 className="font-medium">{log.action}</h4>
                    <Badge className={getTypeColor(log.type)}>
                      {log.type}
                    </Badge>
                  </div>

                  <div className="flex gap-6 text-sm text-muted-foreground ml-7">
                    <div className="flex items-center gap-1">
                      <User className="h-3 w-3" />
                      {log.user}
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {log.timestamp}
                    </div>
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
    </div>
  );
}
