import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';
import { Loader } from '@/components/Loader';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';

interface Address {
  id: string;
  label: string;
  address_line: string;
  pincode: string;
  is_default: boolean;
}

interface UserProfile {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  pincode: string;
}

export default function CustomerProfile() {
  const { user, setUser } = useAuth();
  const queryClient = useQueryClient();
  const [profile, setProfile] = useState<UserProfile>({
    id: '',
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    pincode: ''
  });

  // Fetch current user profile
  const { data: userProfile, isLoading, error } = useQuery({
    queryKey: ['user-profile'],
    queryFn: async () => {
      const { data } = await api.get('/api/users/me/');
      return data;
    }
  });

  // Sync fetched data with local state
  useEffect(() => {
    if (userProfile) {
      setProfile({
        id: userProfile.id.toString(),
        username: userProfile.username,
        email: userProfile.email,
        first_name: userProfile.first_name || '',
        last_name: userProfile.last_name || '',
        phone: userProfile.phone || '',
        pincode: userProfile.pincode || ''
      });
    }
  }, [userProfile]);

  // Show error toast
  useEffect(() => {
    if (error) {
      toast.error('Failed to load profile');
    }
  }, [error]);

  // Fetch addresses
  const { data: addresses = [] } = useQuery({
    queryKey: ['addresses'],
    queryFn: async () => {
      const { data } = await api.get(ENDPOINTS.ADDRESSES.LIST);
      return data.results || data;
    }
  });

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: async (updateData: Partial<UserProfile>) => {
      const { data } = await api.patch('/api/users/me/', updateData);
      return data;
    },
    onSuccess: (data) => {
      // Update auth context
      const updatedUser = { ...user, ...data };
      if (setUser) {
        setUser(updatedUser);
      }
      localStorage.setItem('user', JSON.stringify(updatedUser));
      
      // Update profile state
      setProfile({
        id: data.id.toString(),
        username: data.username,
        email: data.email,
        first_name: data.first_name || '',
        last_name: data.last_name || '',
        phone: data.phone || '',
        pincode: data.pincode || ''
      });
      
      // Invalidate queries
      queryClient.invalidateQueries({ queryKey: ['user-profile'] });
      
      toast.success('Profile updated successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update profile');
    }
  });

  const handleSaveProfile = async () => {
    const updateData = {
      first_name: profile.first_name,
      last_name: profile.last_name,
      phone: profile.phone,
      pincode: profile.pincode
    };
    
    updateProfileMutation.mutate(updateData);
  };

  const handleCancel = () => {
    if (userProfile) {
      setProfile({
        id: userProfile.id.toString(),
        username: userProfile.username,
        email: userProfile.email,
        first_name: userProfile.first_name || '',
        last_name: userProfile.last_name || '',
        phone: userProfile.phone || '',
        pincode: userProfile.pincode || ''
      });
    }
  };

  const handleSavePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement password change functionality
    toast.success('Password change functionality will be implemented');
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">My Profile</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Manage your account information</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Avatar */}
        <Card className="card-elevated">
          <CardContent className="pt-6 flex flex-col items-center">
            <Avatar className="h-24 w-24 mb-4">
              <AvatarFallback className="text-2xl bg-primary text-primary-foreground">
                {profile.first_name?.charAt(0).toUpperCase() || 'U'}
              </AvatarFallback>
            </Avatar>
            <h3 className="font-semibold text-lg">{profile.first_name} {profile.last_name}</h3>
            <p className="text-sm text-muted-foreground capitalize">Customer</p>
            
          </CardContent>
        </Card>

        {/* Profile Form */}
        <Card className="lg:col-span-2 card-elevated">
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name">First Name</Label>
                <Input
                  id="first_name"
                  value={profile.first_name}
                  onChange={(e) => setProfile({...profile, first_name: e.target.value})}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="last_name">Last Name</Label>
                <Input
                  id="last_name"
                  value={profile.last_name}
                  onChange={(e) => setProfile({...profile, last_name: e.target.value})}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({...profile, email: e.target.value})}
                  disabled
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  type="tel"
                  placeholder="+1 234 567 8900"
                  value={profile.phone}
                  onChange={(e) => setProfile({...profile, phone: e.target.value})}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="pincode">Default Pincode</Label>
                <Input
                  id="pincode"
                  placeholder="123456"
                  value={profile.pincode}
                  onChange={(e) => setProfile({...profile, pincode: e.target.value})}
                />
              </div>
            </div>

            <Separator />

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={handleCancel} disabled={updateProfileMutation.isPending}>
                Cancel
              </Button>
              <Button onClick={handleSaveProfile} disabled={updateProfileMutation.isPending}>
                {updateProfileMutation.isPending ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Password Change */}
      
    </div>
  );
}