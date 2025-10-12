import { Bell, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/context/AuthContext';

export const Navbar = () => {
  const { user } = useAuth();

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
        <Button variant="ghost" size="icon" className="relative h-9 w-9 md:h-10 md:w-10">
          <Bell className="h-4 w-4 md:h-5 md:w-5" />
          <span className="absolute top-1 right-1 h-2 w-2 bg-destructive rounded-full" />
        </Button>

        <div className="hidden sm:block h-8 w-px bg-border" />

        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-semibold">
            {user?.name.charAt(0).toUpperCase()}
          </div>
          <span className="hidden sm:block text-sm font-medium">{user?.name}</span>
        </div>
      </div>
    </header>
  );
};
