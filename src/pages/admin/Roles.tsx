import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Shield, Users, UserCheck, Briefcase, Settings } from 'lucide-react';

const roles = [
  { name: 'Customer', icon: Users, count: 1842, color: 'text-primary', permissions: ['Book services', 'View bookings', 'Sign documents'] },
  { name: 'Vendor', icon: Briefcase, count: 347, color: 'text-primary', permissions: ['Accept jobs', 'Upload photos', 'Request signatures'] },
  { name: 'Onboard', icon: UserCheck, count: 8, color: 'text-primary', permissions: ['Review vendors', 'Approve applications', 'Manage queue'] },
  { name: 'Operations', icon: Settings, count: 12, color: 'text-primary', permissions: ['Monitor bookings', 'Approve payments', 'View analytics'] },
  { name: 'Admin', icon: Shield, count: 5, color: 'text-primary', permissions: ['Full system access', 'User management', 'Security settings'] },
];

export default function AdminRoles() {
  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Role Management</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Configure roles and permissions</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {roles.map((role) => (
          <Card key={role.name} className="card-elevated">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <role.icon className={`h-5 w-5 ${role.color}`} />
                  </div>
                  <div>
                    <CardTitle>{role.name}</CardTitle>
                    <p className="text-sm text-muted-foreground">{role.count} users</p>
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  Edit
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div>
                <p className="text-sm font-medium mb-2">Permissions:</p>
                <div className="flex flex-wrap gap-2">
                  {role.permissions.map((permission, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {permission}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
