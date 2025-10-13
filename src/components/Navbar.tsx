import { Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/context/AuthContext';
import { NotificationDropdown } from '@/components/NotificationDropdown';
import type { User } from '@/services/authService';

export const Navbar = () => {
  const { user } = useAuth();

  // Helper function to get display name safely
  const getDisplayName = (user: User) => {
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    if (user.first_name) {
      return user.first_name;
    }
    if (user.username) {
      return user.username;
    }
    return user.email || 'User';
  };

  // Helper function to get avatar initial safely
  const getAvatarInitial = (user: User) => {
    const displayName = getDisplayName(user);
    return displayName.charAt(0).toUpperCase();
  };

  return (
    <header className="h-24 bg-card border-b border-border px-4 md:px-6 flex items-center justify-between">
      {/* Search - Hidden on mobile, visible on md+ */}
      <div className="hidden md:flex flex-1 max-w-md">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search..."
            className="pl-10"
          />
        </div>
      </div>

      {/* Mobile spacer for menu button */}
      <div className="md:hidden w-12"></div>

      {/* Right side */}
      <div className="flex items-center gap-2 md:gap-3 ml-auto">
        <NotificationDropdown />

        <div className="hidden sm:block h-8 w-px bg-border" />

        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-semibold">
            {user ? getAvatarInitial(user) : 'U'}
          </div>
          <span className="hidden sm:block text-sm font-medium">{user ? getDisplayName(user) : 'User'}</span>
        </div>
      </div>
    </header>
  );
};