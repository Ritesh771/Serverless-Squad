import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Shield, Users, UserCheck, Briefcase, Settings, Edit, Save, X, Loader2, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';
import { Loader } from '@/components/Loader';

interface Role {
  id: string;
  name: string;
  display_name: string;
  description: string;
  permissions: string[];
  user_count: number;
  is_active: boolean;
}

interface RolePermission {
  id: string;
  name: string;
  description: string;
  category: string;
}

const roleDefinitions = [
  {
    id: 'customer',
    name: 'Customer',
    icon: Users,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    description: 'End users who book and receive services'
  },
  {
    id: 'vendor',
    name: 'Vendor',
    icon: Briefcase,
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    description: 'Service providers who deliver services to customers'
  },
  {
    id: 'onboard_manager',
    name: 'Onboard Manager',
    icon: UserCheck,
    color: 'text-purple-600',
    bgColor: 'bg-purple-100',
    description: 'Manages vendor onboarding and application approval'
  },
  {
    id: 'ops_manager',
    name: 'Ops Manager',
    icon: Settings,
    color: 'text-orange-600',
    bgColor: 'bg-orange-100',
    description: 'Monitors operations and manages platform activities'
  },
  {
    id: 'super_admin',
    name: 'Super Admin',
    icon: Shield,
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    description: 'Full system access and administrative control'
  }
];

const allPermissions: RolePermission[] = [
  // Customer permissions
  { id: 'book_service', name: 'Book Service', description: 'Create new service bookings', category: 'Booking' },
  { id: 'view_bookings', name: 'View Bookings', description: 'Access personal booking history', category: 'Booking' },
  { id: 'manage_profile', name: 'Manage Profile', description: 'Update personal information', category: 'Profile' },
  { id: 'manage_addresses', name: 'Manage Addresses', description: 'Add and edit service addresses', category: 'Profile' },
  { id: 'sign_documents', name: 'Sign Documents', description: 'Digital signature for service completion', category: 'Signature' },
  
  // Vendor permissions
  { id: 'accept_jobs', name: 'Accept Jobs', description: 'Accept or decline service bookings', category: 'Job Management' },
  { id: 'upload_photos', name: 'Upload Photos', description: 'Upload before/after service photos', category: 'Job Management' },
  { id: 'request_signatures', name: 'Request Signatures', description: 'Request customer satisfaction signatures', category: 'Signature' },
  { id: 'manage_availability', name: 'Manage Availability', description: 'Set working hours and availability', category: 'Schedule' },
  { id: 'view_earnings', name: 'View Earnings', description: 'Access earnings and payment history', category: 'Finance' },
  
  // Onboard Manager permissions
  { id: 'review_vendors', name: 'Review Vendors', description: 'Review vendor applications and documents', category: 'Onboarding' },
  { id: 'approve_applications', name: 'Approve Applications', description: 'Approve or reject vendor applications', category: 'Onboarding' },
  { id: 'manage_vendor_queue', name: 'Manage Vendor Queue', description: 'Manage vendor application queue', category: 'Onboarding' },
  
  // Ops Manager permissions
  { id: 'monitor_bookings', name: 'Monitor Bookings', description: 'Monitor all platform bookings and activities', category: 'Operations' },
  { id: 'approve_payments', name: 'Approve Payments', description: 'Approve and release payments to vendors', category: 'Finance' },
  { id: 'view_analytics', name: 'View Analytics', description: 'Access platform analytics and reports', category: 'Analytics' },
  { id: 'manage_disputes', name: 'Manage Disputes', description: 'Handle customer and vendor disputes', category: 'Operations' },
  
  // Super Admin permissions
  { id: 'full_system_access', name: 'Full System Access', description: 'Complete system administration', category: 'System' },
  { id: 'manage_users', name: 'Manage Users', description: 'Create, edit, and manage all users', category: 'User Management' },
  { id: 'manage_roles', name: 'Manage Roles', description: 'Create and modify role permissions', category: 'User Management' },
  { id: 'system_settings', name: 'System Settings', description: 'Configure system-wide settings', category: 'System' },
  { id: 'view_audit_logs', name: 'View Audit Logs', description: 'Access system audit logs', category: 'Security' },
];

export default function AdminRoles() {
  const [editingRole, setEditingRole] = useState<string | null>(null);
  const [rolePermissions, setRolePermissions] = useState<Record<string, boolean>>({});
  const queryClient = useQueryClient();

  // Fetch roles and permissions from backend
  const { data: rolesData, isLoading, error } = useQuery({
    queryKey: ['admin-roles'],
    queryFn: async () => {
      // In a real implementation, this would fetch from backend
      // For now, we'll simulate the data structure
      const usersResponse = await api.get(ENDPOINTS.USERS.LIST);
      const users = usersResponse.data.results || [];
      
      // Count users by role
      const roleCounts = users.reduce((acc: Record<string, number>, user: any) => {
        acc[user.role] = (acc[user.role] || 0) + 1;
        return acc;
      }, {});

      return roleDefinitions.map(roleDef => ({
        id: roleDef.id,
        name: roleDef.name,
        display_name: roleDef.name,
        description: roleDef.description,
        permissions: getDefaultPermissions(roleDef.id),
        user_count: roleCounts[roleDef.id] || 0,
        is_active: true
      }));
    },
  });

  function getDefaultPermissions(roleId: string): string[] {
    const rolePermissionMap: Record<string, string[]> = {
      'customer': ['book_service', 'view_bookings', 'manage_profile', 'manage_addresses', 'sign_documents'],
      'vendor': ['accept_jobs', 'upload_photos', 'request_signatures', 'manage_availability', 'view_earnings'],
      'onboard_manager': ['review_vendors', 'approve_applications', 'manage_vendor_queue'],
      'ops_manager': ['monitor_bookings', 'approve_payments', 'view_analytics', 'manage_disputes'],
      'super_admin': ['full_system_access', 'manage_users', 'manage_roles', 'system_settings', 'view_audit_logs']
    };
    return rolePermissionMap[roleId] || [];
  }

  // Update role permissions mutation
  const updateRoleMutation = useMutation({
    mutationFn: async ({ roleId, permissions }: { roleId: string; permissions: string[] }) => {
      // In a real implementation, this would update the backend
      toast.success('Role permissions updated successfully');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-roles'] });
      setEditingRole(null);
    },
    onError: () => {
      toast.error('Failed to update role permissions');
    },
  });

  const handleEditRole = (role: Role) => {
    setEditingRole(role.id);
    // Initialize permissions state
    const permissionsState: Record<string, boolean> = {};
    allPermissions.forEach(permission => {
      permissionsState[permission.id] = role.permissions.includes(permission.id);
    });
    setRolePermissions(permissionsState);
  };

  const handleSaveRole = () => {
    if (!editingRole) return;
    
    const selectedPermissions = Object.entries(rolePermissions)
      .filter(([_, enabled]) => enabled)
      .map(([permissionId, _]) => permissionId);
    
    updateRoleMutation.mutate({
      roleId: editingRole,
      permissions: selectedPermissions
    });
  };

  const getRoleIcon = (roleId: string) => {
    const roleDef = roleDefinitions.find(r => r.id === roleId);
    return roleDef?.icon || Users;
  };

  const getRoleColor = (roleId: string) => {
    const roleDef = roleDefinitions.find(r => r.id === roleId);
    return roleDef?.color || 'text-gray-600';
  };

  const getRoleBgColor = (roleId: string) => {
    const roleDef = roleDefinitions.find(r => r.id === roleId);
    return roleDef?.bgColor || 'bg-gray-100';
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
          <h3 className="mt-2 text-lg font-semibold">Error Loading Roles</h3>
          <p className="text-muted-foreground">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Role Management</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Configure roles and permissions for system access</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {rolesData?.map((role: Role) => {
          const RoleIcon = getRoleIcon(role.id);
          const roleColor = getRoleColor(role.id);
          const roleBgColor = getRoleBgColor(role.id);
          
          return (
            <Card key={role.id} className="card-elevated">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`h-10 w-10 rounded-lg ${roleBgColor} flex items-center justify-center`}>
                      <RoleIcon className={`h-5 w-5 ${roleColor}`} />
                    </div>
                    <div>
                      <CardTitle>{role.display_name}</CardTitle>
                      <p className="text-sm text-muted-foreground">{role.user_count} users</p>
                    </div>
                  </div>
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleEditRole(role)}
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        Edit
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                      <DialogHeader>
                        <DialogTitle>Edit {role.display_name} Permissions</DialogTitle>
                      </DialogHeader>
                      
                      <div className="space-y-4">
                        <p className="text-sm text-muted-foreground">{role.description}</p>
                        
                        <div className="space-y-4">
                          {Object.values(allPermissions.reduce((acc, permission) => {
                            if (!acc[permission.category]) {
                              acc[permission.category] = [];
                            }
                            acc[permission.category].push(permission);
                            return acc;
                          }, {} as Record<string, RolePermission[]>)).map((categoryPermissions, index) => (
                            <div key={index} className="space-y-2">
                              <h4 className="font-medium text-sm">{categoryPermissions[0].category}</h4>
                              <div className="space-y-2 ml-4">
                                {categoryPermissions.map((permission) => (
                                  <div key={permission.id} className="flex items-center justify-between">
                                    <div className="space-y-1">
                                      <Label className="text-sm font-medium">{permission.name}</Label>
                                      <p className="text-xs text-muted-foreground">{permission.description}</p>
                                    </div>
                                    <Switch
                                      checked={rolePermissions[permission.id] || false}
                                      onCheckedChange={(checked) => 
                                        setRolePermissions(prev => ({ ...prev, [permission.id]: checked }))
                                      }
                                    />
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                        
                        <div className="flex justify-end gap-2 pt-4">
                          <Button variant="outline" onClick={() => setEditingRole(null)}>
                            <X className="h-4 w-4 mr-1" />
                            Cancel
                          </Button>
                          <Button 
                            onClick={handleSaveRole}
                            disabled={updateRoleMutation.isPending}
                          >
                            {updateRoleMutation.isPending ? (
                              <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                            ) : (
                              <Save className="h-4 w-4 mr-1" />
                            )}
                            Save Changes
                          </Button>
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              <CardContent>
                <div>
                  <p className="text-sm font-medium mb-2">Permissions ({role.permissions.length}):</p>
                  <div className="flex flex-wrap gap-2">
                    {role.permissions.map((permissionId) => {
                      const permission = allPermissions.find(p => p.id === permissionId);
                      return (
                        <Badge key={permissionId} variant="secondary" className="text-xs">
                          {permission?.name || permissionId}
                        </Badge>
                      );
                    })}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
