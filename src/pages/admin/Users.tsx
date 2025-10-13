import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Mail, Calendar, Loader2, AlertCircle, Shield, UserCheck, Briefcase, Users, Settings } from 'lucide-react';
import { toast } from 'sonner';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';
import { Loader } from '@/components/Loader';

interface User {
  id: number;
  email: string;
  role: string;
  is_active: boolean;
  date_joined: string;
  last_login?: string;
  phone_number?: string;
  first_name?: string;
  last_name?: string;
}

export default function AdminUsers() {
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const queryClient = useQueryClient();

  // Fetch users from backend
  const { data: usersData, isLoading, error } = useQuery({
    queryKey: ['admin-users', { search, roleFilter, statusFilter }],
    queryFn: () => api.get(ENDPOINTS.USERS.LIST, {
      params: {
        search: search || undefined,
        role: roleFilter && roleFilter !== 'all' ? roleFilter : undefined,
        is_active: statusFilter === 'active' ? true : statusFilter === 'inactive' ? false : undefined,
      }
    }).then(res => res.data),
  });

  const users = usersData?.results || [];
  const totalUsers = usersData?.count || 0;

  // User role update mutation
  const updateUserRoleMutation = useMutation({
    mutationFn: ({ userId, newRole }: { userId: number; newRole: string }) =>
      api.patch(ENDPOINTS.USERS.UPDATE(userId), { role: newRole }),
    onSuccess: () => {
      toast.success('User role updated successfully');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
    onError: () => {
      toast.error('Failed to update user role');
    },
  });

  // User status update mutation
  const updateUserStatusMutation = useMutation({
    mutationFn: ({ userId, isActive }: { userId: number; isActive: boolean }) =>
      api.patch(ENDPOINTS.USERS.UPDATE(userId), { is_active: isActive }),
    onSuccess: (_, variables) => {
      toast.success(`User ${variables.isActive ? 'activated' : 'deactivated'} successfully`);
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
    onError: () => {
      toast.error('Failed to update user status');
    },
  });

  const filteredUsers = users.filter((user: User) =>
    user.email.toLowerCase().includes(search.toLowerCase()) ||
    user.first_name?.toLowerCase().includes(search.toLowerCase()) ||
    user.last_name?.toLowerCase().includes(search.toLowerCase())
  );

  const handleRoleChange = (userId: number, newRole: string) => {
    updateUserRoleMutation.mutate({ userId, newRole });
  };

  const handleStatusChange = (userId: number, isActive: boolean) => {
    updateUserStatusMutation.mutate({ userId, isActive });
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'super_admin': return Shield;
      case 'onboard_manager': return UserCheck;
      case 'ops_manager': return Settings;
      case 'vendor': return Briefcase;
      default: return Users;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'super_admin': return 'bg-red-100 text-red-800';
      case 'onboard_manager': return 'bg-blue-100 text-blue-800';
      case 'ops_manager': return 'bg-green-100 text-green-800';
      case 'vendor': return 'bg-purple-100 text-purple-800';
      case 'customer': return 'bg-gray-100 text-gray-800';
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
          <AlertCircle className="mx-auto h-12 w-12 text-destructive" />
          <h3 className="mt-2 text-lg font-semibold">Error Loading Users</h3>
          <p className="text-muted-foreground">Please try refreshing the page</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">User Management</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">
            View and manage all platform users ({totalUsers} total)
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search users..."
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        
        <Select value={roleFilter} onValueChange={setRoleFilter}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="All Roles" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Roles</SelectItem>
            <SelectItem value="customer">Customer</SelectItem>
            <SelectItem value="vendor">Vendor</SelectItem>
            <SelectItem value="onboard_manager">Onboard Manager</SelectItem>
            <SelectItem value="ops_manager">Ops Manager</SelectItem>
            <SelectItem value="super_admin">Super Admin</SelectItem>
          </SelectContent>
        </Select>

        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="All Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Users */}
      <div className="grid grid-cols-1 gap-4">
        {filteredUsers.map((user: User) => {
          const RoleIcon = getRoleIcon(user.role);
          const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'Unknown';
          
          return (
            <Card key={user.id} className="card-elevated">
              <CardContent className="p-4 md:p-6">
                <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                  <div className="space-y-3 flex-1">
                    <div className="flex items-center gap-3 flex-wrap">
                      <div className="flex items-center gap-2">
                        <RoleIcon className="h-4 w-4 text-muted-foreground" />
                        <h3 className="text-lg font-semibold">{fullName}</h3>
                      </div>
                      <Badge className={user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                      <Badge className={getRoleColor(user.role)}>
                        {user.role.replace('_', ' ')}
                      </Badge>
                    </div>

                    <div className="flex gap-6 text-sm text-muted-foreground flex-wrap">
                      <div className="flex items-center gap-1">
                        <Mail className="h-4 w-4" />
                        {user.email}
                      </div>
                      {user.phone_number && (
                        <div className="flex items-center gap-1">
                          <span>📞</span>
                          {user.phone_number}
                        </div>
                      )}
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        Joined {new Date(user.date_joined).toLocaleDateString()}
                      </div>
                      {user.last_login && (
                        <div className="flex items-center gap-1">
                          <span>🕒</span>
                          Last login: {new Date(user.last_login).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
                    <Select
                      value={user.role}
                      onValueChange={(newRole) => handleRoleChange(user.id, newRole)}
                      disabled={updateUserRoleMutation.isPending}
                    >
                      <SelectTrigger className="w-full sm:w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="customer">Customer</SelectItem>
                        <SelectItem value="vendor">Vendor</SelectItem>
                        <SelectItem value="onboard_manager">Onboard</SelectItem>
                        <SelectItem value="ops_manager">Ops</SelectItem>
                        <SelectItem value="super_admin">Super Admin</SelectItem>
                      </SelectContent>
                    </Select>
                    
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => handleStatusChange(user.id, !user.is_active)}
                      disabled={updateUserStatusMutation.isPending}
                      className="w-full sm:w-auto"
                    >
                      {updateUserStatusMutation.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : user.is_active ? (
                        'Deactivate'
                      ) : (
                        'Activate'
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {filteredUsers.length === 0 && !isLoading && (
        <div className="text-center py-8">
          <Users className="mx-auto h-12 w-12 text-muted-foreground" />
          <h3 className="mt-2 text-lg font-semibold">No users found</h3>
          <p className="text-muted-foreground">Try adjusting your search or filter criteria</p>
        </div>
      )}
    </div>
  );
}
