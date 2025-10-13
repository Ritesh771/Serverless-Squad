import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import type { User } from '@/services/authService';
import { useState, useEffect, ComponentType } from 'react';
import {
  LayoutDashboard,
  Calendar,
  ListChecks,
  DollarSign,
  User as UserIcon,
  BookOpen,
  Users,
  CheckCircle,
  MapPin,
  FileText,
  TrendingUp,
  Shield,
  Settings,
  BarChart3,
  LogOut,
  Home,
  ClipboardList,
  FileSignature,
  Menu,
  X,
  AlertTriangle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

interface NavItem {
  title: string;
  href: string;
  icon: ComponentType<{ className?: string }>;
}

const roleNavigation: Record<string, NavItem[]> = {
  customer: [
    { title: 'Dashboard', href: '/customer/dashboard', icon: LayoutDashboard },
    { title: 'Book Service', href: '/customer/book-service', icon: BookOpen },
    { title: 'My Bookings', href: '/customer/my-bookings', icon: ListChecks },
    { title: 'Profile', href: '/customer/profile', icon: UserIcon },
  ],
  vendor: [
    { title: 'Dashboard', href: '/vendor/dashboard', icon: LayoutDashboard },
    { title: 'Calendar', href: '/vendor/calendar', icon: Calendar },
    { title: 'Job List', href: '/vendor/job-list', icon: ListChecks },
    { title: 'Earnings', href: '/vendor/earnings', icon: DollarSign },
    { title: 'Profile', href: '/vendor/profile', icon: UserIcon },
  ],
  onboard_manager: [
    { title: 'Dashboard', href: '/onboard/dashboard', icon: LayoutDashboard },
    { title: 'Vendor Queue', href: '/onboard/vendor-queue', icon: Users },
    { title: 'Approved Vendors', href: '/onboard/approved-vendors', icon: CheckCircle },
  ],
  ops_manager: [
    { title: 'Dashboard', href: '/ops/dashboard', icon: LayoutDashboard },
    { title: 'Bookings Monitor', href: '/ops/bookings-monitor', icon: MapPin },
    { title: 'Signature Vault', href: '/ops/signature-vault', icon: FileSignature },
    { title: 'Manual Payments', href: '/ops/manual-payments', icon: DollarSign },
    { title: 'Analytics', href: '/ops/analytics', icon: TrendingUp },
  ],
  super_admin: [
    { title: 'Dashboard', href: '/admin/dashboard', icon: LayoutDashboard },
    { title: 'Users', href: '/admin/users', icon: Users },
    { title: 'Roles', href: '/admin/roles', icon: Shield },
    { title: 'Audit Logs', href: '/admin/audit-logs', icon: FileText },
    { title: 'Ethics & AI Flags', href: '/admin/ethics', icon: AlertTriangle },
    { title: 'Reports', href: '/admin/reports', icon: BarChart3 },
    { title: 'Settings', href: '/admin/settings', icon: Settings },
  ],
};

export const Sidebar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Close mobile menu on route change
    setIsMobileMenuOpen(false);
  }, [navigate]);

  if (!user) return null;

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

  const navItems = roleNavigation[user.role] || [];

  return (
    <>
      {/* Mobile Menu Button */}
      <Button
        variant="ghost"
        size="sm"
        className="fixed top-4 left-4 z-50 lg:hidden"
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
      >
        {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>

      {/* Overlay for mobile */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:sticky top-0 h-screen w-64 bg-card border-r border-border flex flex-col z-40 
          transition-transform duration-300 ease-in-out
          ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        {/* Logo */}
        <div className="p-6 mt-12 lg:mt-0">
          <div className="flex items-center gap-2">
            <Home className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold text-foreground">HomeServe Pro</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1 capitalize">{user.role} Portal</p>
        </div>

        <Separator />

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.href}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                }`
              }
            >
              <item.icon className="h-4 w-4" />
              <span>{item.title}</span>
            </NavLink>
          ))}
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-3 mb-3">
            <div className="h-10 w-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
              {getAvatarInitial(user)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">{getDisplayName(user)}</p>
              <p className="text-xs text-muted-foreground truncate">{user.email}</p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={logout}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </aside>
    </>
  );
};