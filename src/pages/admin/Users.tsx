import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Mail, Calendar } from 'lucide-react';
import { toast } from 'sonner';

const mockUsers = [
  { id: '1', name: 'John Smith', email: 'john@example.com', role: 'vendor', status: 'active', joined: '2024-11-15' },
  { id: '2', name: 'Jane Doe', email: 'jane@example.com', role: 'customer', status: 'active', joined: '2024-12-01' },
  { id: '3', name: 'Mike Johnson', email: 'mike@example.com', role: 'vendor', status: 'suspended', joined: '2024-10-20' },
  { id: '4', name: 'Sarah Williams', email: 'sarah@example.com', role: 'ops', status: 'active', joined: '2024-09-15' },
];

export default function AdminUsers() {
  const [search, setSearch] = useState('');

  const filteredUsers = mockUsers.filter((user) =>
    user.name.toLowerCase().includes(search.toLowerCase()) ||
    user.email.toLowerCase().includes(search.toLowerCase())
  );

  const handleSuspend = (id: string) => {
    toast.success('User suspended');
  };

  const handleReactivate = (id: string) => {
    toast.success('User reactivated');
  };

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">User Management</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">View and manage all platform users</p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search users..."
          className="pl-10"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Users */}
      <div className="grid grid-cols-1 gap-4">
        {filteredUsers.map((user) => (
          <Card key={user.id} className="card-elevated">
            <CardContent className="p-4 md:p-6">
              <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                <div className="space-y-3 flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold">{user.name}</h3>
                    <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                      {user.status}
                    </Badge>
                    <Badge variant="outline" className="capitalize">
                      {user.role}
                    </Badge>
                  </div>

                  <div className="flex gap-6 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Mail className="h-4 w-4" />
                      {user.email}
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      Joined {user.joined}
                    </div>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
                  {user.status === 'active' ? (
                    <Button variant="outline" size="sm" onClick={() => handleSuspend(user.id)} className="w-full sm:w-auto">
                      Suspend
                    </Button>
                  ) : (
                    <Button variant="outline" size="sm" onClick={() => handleReactivate(user.id)} className="w-full sm:w-auto">
                      Reactivate
                    </Button>
                  )}
                  <Button variant="outline" size="sm" className="w-full sm:w-auto">
                    View Details
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
