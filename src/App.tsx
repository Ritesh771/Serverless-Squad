import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import { Sidebar } from "@/components/Sidebar";
import { Navbar } from "@/components/Navbar";
import { ChatBot } from "@/components/ChatBot";

// Auth pages
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import ForgotPassword from "./pages/auth/ForgotPassword";

// Customer pages
import CustomerDashboard from "./pages/customer/Dashboard";
import BookService from "./pages/customer/BookService";
import MyBookings from "./pages/customer/MyBookings";
import BookingDetails from "./pages/customer/BookingDetails";
import SignaturePage from "./pages/customer/SignaturePage";
import CustomerProfile from "./pages/customer/Profile";

// Vendor pages
import VendorDashboard from "./pages/vendor/Dashboard";
import VendorCalendar from "./pages/vendor/Calendar";
import VendorJobList from "./pages/vendor/JobList";
import VendorJobDetails from "./pages/vendor/JobDetails";
import VendorEarnings from "./pages/vendor/Earnings";
import VendorTransactionDetails from "./pages/vendor/TransactionDetails";
import VendorProfile from "./pages/vendor/Profile";

// Onboard pages
import OnboardDashboard from "./pages/onboard/Dashboard";
import VendorQueue from "./pages/onboard/VendorQueue";
import VendorDetails from "./pages/onboard/VendorDetails";
import ApprovedVendors from "./pages/onboard/ApprovedVendors";

// Ops pages
import OpsDashboard from "./pages/ops/Dashboard";
import BookingsMonitor from "./pages/ops/BookingsMonitor";
import SignatureVault from "./pages/ops/SignatureVault";
import ManualPayments from "./pages/ops/ManualPayments";
import OpsAnalytics from "./pages/ops/Analytics";

// Admin pages
import AdminDashboard from "./pages/admin/Dashboard";
import AdminUsers from "./pages/admin/Users";
import AdminRoles from "./pages/admin/Roles";
import AdminAuditLogs from "./pages/admin/AuditLogs";
import AdminEthics from "./pages/admin/Ethics";
import AdminReports from "./pages/admin/Reports";
import AdminSettings from "./pages/admin/Settings";

import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/auth/login" />;
  }

  return (
    <div className="flex h-screen w-full">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-y-auto bg-background">
          {children}
        </main>
        <ChatBot />
      </div>
    </div>
  );
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/auth/login" element={user ? <Navigate to={`/${user.role.replace('_', '-')}/dashboard`} /> : <Login />} />
      <Route path="/auth/register" element={user ? <Navigate to={`/${user.role.replace('_', '-')}/dashboard`} /> : <Register />} />
      <Route path="/auth/forgot-password" element={<ForgotPassword />} />

      {/* Customer routes */}
      <Route path="/customer/dashboard" element={<ProtectedLayout><CustomerDashboard /></ProtectedLayout>} />
      <Route path="/customer/book-service" element={<ProtectedLayout><BookService /></ProtectedLayout>} />
      <Route path="/customer/my-bookings" element={<ProtectedLayout><MyBookings /></ProtectedLayout>} />
      <Route path="/customer/my-bookings/:id" element={<ProtectedLayout><BookingDetails /></ProtectedLayout>} />
      <Route path="/customer/signature/:id" element={<ProtectedLayout><SignaturePage /></ProtectedLayout>} />
      <Route path="/customer/profile" element={<ProtectedLayout><CustomerProfile /></ProtectedLayout>} />

      {/* Vendor routes */}
      <Route path="/vendor/dashboard" element={<ProtectedLayout><VendorDashboard /></ProtectedLayout>} />
      <Route path="/vendor/calendar" element={<ProtectedLayout><VendorCalendar /></ProtectedLayout>} />
      <Route path="/vendor/job-list" element={<ProtectedLayout><VendorJobList /></ProtectedLayout>} />
      <Route path="/vendor/job-list/:id" element={<ProtectedLayout><VendorJobDetails /></ProtectedLayout>} />
      <Route path="/vendor/earnings" element={<ProtectedLayout><VendorEarnings /></ProtectedLayout>} />
      <Route path="/vendor/earnings/:id" element={<ProtectedLayout><VendorTransactionDetails /></ProtectedLayout>} />
      <Route path="/vendor/profile" element={<ProtectedLayout><VendorProfile /></ProtectedLayout>} />

      {/* Onboard Manager routes (backend uses onboard_manager) */}
      <Route path="/onboard-manager/dashboard" element={<ProtectedLayout><OnboardDashboard /></ProtectedLayout>} />
      <Route path="/onboard-manager/vendor-queue" element={<ProtectedLayout><VendorQueue /></ProtectedLayout>} />
      <Route path="/onboard-manager/vendor-queue/:id" element={<ProtectedLayout><VendorDetails /></ProtectedLayout>} />
      <Route path="/onboard-manager/approved-vendors" element={<ProtectedLayout><ApprovedVendors /></ProtectedLayout>} />
      {/* Legacy onboard routes - redirect to onboard-manager */}
      <Route path="/onboard/*" element={<Navigate to="/onboard-manager/dashboard" replace />} />

      {/* Ops Manager routes (backend uses ops_manager) */}
      <Route path="/ops-manager/dashboard" element={<ProtectedLayout><OpsDashboard /></ProtectedLayout>} />
      <Route path="/ops-manager/bookings-monitor" element={<ProtectedLayout><BookingsMonitor /></ProtectedLayout>} />
      <Route path="/ops-manager/signature-vault" element={<ProtectedLayout><SignatureVault /></ProtectedLayout>} />
      <Route path="/ops-manager/manual-payments" element={<ProtectedLayout><ManualPayments /></ProtectedLayout>} />
      <Route path="/ops-manager/analytics" element={<ProtectedLayout><OpsAnalytics /></ProtectedLayout>} />
      {/* Legacy ops routes - redirect to ops-manager */}
      <Route path="/ops/*" element={<Navigate to="/ops-manager/dashboard" replace />} />

      {/* Super Admin routes (backend uses super_admin) */}
      <Route path="/super-admin/dashboard" element={<ProtectedLayout><AdminDashboard /></ProtectedLayout>} />
      <Route path="/super-admin/users" element={<ProtectedLayout><AdminUsers /></ProtectedLayout>} />
      <Route path="/super-admin/roles" element={<ProtectedLayout><AdminRoles /></ProtectedLayout>} />
      <Route path="/super-admin/audit-logs" element={<ProtectedLayout><AdminAuditLogs /></ProtectedLayout>} />
      <Route path="/super-admin/ethics" element={<ProtectedLayout><AdminEthics /></ProtectedLayout>} />
      <Route path="/super-admin/reports" element={<ProtectedLayout><AdminReports /></ProtectedLayout>} />
      <Route path="/super-admin/settings" element={<ProtectedLayout><AdminSettings /></ProtectedLayout>} />
      {/* Legacy admin routes - redirect to super-admin */}
      <Route path="/admin/*" element={<Navigate to="/super-admin/dashboard" replace />} />

      {/* Default redirects */}
      <Route path="/" element={<Navigate to="/auth/login" />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;