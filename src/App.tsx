import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import { Sidebar } from "@/components/Sidebar";
import { Navbar } from "@/components/Navbar";

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
import CustomerChat from "./pages/customer/Chat";
import CustomerProfile from "./pages/customer/Profile";

// Vendor pages
import VendorDashboard from "./pages/vendor/Dashboard";
import VendorCalendar from "./pages/vendor/Calendar";
import VendorJobList from "./pages/vendor/JobList";
import VendorJobDetails from "./pages/vendor/JobDetails";
import VendorEarnings from "./pages/vendor/Earnings";
import VendorTransactionDetails from "./pages/vendor/TransactionDetails";
import VendorChat from "./pages/vendor/Chat";
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
import OpsChat from "./pages/ops/Chat";

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
      </div>
    </div>
  );
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/auth/login" element={user ? <Navigate to={`/${user.role}/dashboard`} /> : <Login />} />
      <Route path="/auth/register" element={user ? <Navigate to={`/${user.role}/dashboard`} /> : <Register />} />
      <Route path="/auth/forgot-password" element={<ForgotPassword />} />

      {/* Customer routes */}
      <Route path="/customer/dashboard" element={<ProtectedLayout><CustomerDashboard /></ProtectedLayout>} />
      <Route path="/customer/book-service" element={<ProtectedLayout><BookService /></ProtectedLayout>} />
      <Route path="/customer/my-bookings" element={<ProtectedLayout><MyBookings /></ProtectedLayout>} />
      <Route path="/customer/my-bookings/:id" element={<ProtectedLayout><BookingDetails /></ProtectedLayout>} />
      <Route path="/customer/signature/:id" element={<ProtectedLayout><SignaturePage /></ProtectedLayout>} />
      <Route path="/customer/chat" element={<ProtectedLayout><CustomerChat /></ProtectedLayout>} />
      <Route path="/customer/profile" element={<ProtectedLayout><CustomerProfile /></ProtectedLayout>} />

      {/* Vendor routes */}
      <Route path="/vendor/dashboard" element={<ProtectedLayout><VendorDashboard /></ProtectedLayout>} />
      <Route path="/vendor/calendar" element={<ProtectedLayout><VendorCalendar /></ProtectedLayout>} />
      <Route path="/vendor/job-list" element={<ProtectedLayout><VendorJobList /></ProtectedLayout>} />
      <Route path="/vendor/job-list/:id" element={<ProtectedLayout><VendorJobDetails /></ProtectedLayout>} />
      <Route path="/vendor/earnings" element={<ProtectedLayout><VendorEarnings /></ProtectedLayout>} />
      <Route path="/vendor/earnings/:id" element={<ProtectedLayout><VendorTransactionDetails /></ProtectedLayout>} />
      <Route path="/vendor/chat" element={<ProtectedLayout><VendorChat /></ProtectedLayout>} />
      <Route path="/vendor/profile" element={<ProtectedLayout><VendorProfile /></ProtectedLayout>} />

      {/* Onboard routes */}
      <Route path="/onboard/dashboard" element={<ProtectedLayout><OnboardDashboard /></ProtectedLayout>} />
      <Route path="/onboard/vendor-queue" element={<ProtectedLayout><VendorQueue /></ProtectedLayout>} />
      <Route path="/onboard/vendor-queue/:id" element={<ProtectedLayout><VendorDetails /></ProtectedLayout>} />
      <Route path="/onboard/approved-vendors" element={<ProtectedLayout><ApprovedVendors /></ProtectedLayout>} />

      {/* Ops routes */}
      <Route path="/ops/dashboard" element={<ProtectedLayout><OpsDashboard /></ProtectedLayout>} />
      <Route path="/ops/bookings-monitor" element={<ProtectedLayout><BookingsMonitor /></ProtectedLayout>} />
      <Route path="/ops/signature-vault" element={<ProtectedLayout><SignatureVault /></ProtectedLayout>} />
      <Route path="/ops/manual-payments" element={<ProtectedLayout><ManualPayments /></ProtectedLayout>} />
      <Route path="/ops/analytics" element={<ProtectedLayout><OpsAnalytics /></ProtectedLayout>} />
      <Route path="/ops/chat" element={<ProtectedLayout><OpsChat /></ProtectedLayout>} />

      {/* Admin routes */}
      <Route path="/admin/dashboard" element={<ProtectedLayout><AdminDashboard /></ProtectedLayout>} />
      <Route path="/admin/users" element={<ProtectedLayout><AdminUsers /></ProtectedLayout>} />
      <Route path="/admin/roles" element={<ProtectedLayout><AdminRoles /></ProtectedLayout>} />
      <Route path="/admin/audit-logs" element={<ProtectedLayout><AdminAuditLogs /></ProtectedLayout>} />
      <Route path="/admin/ethics" element={<ProtectedLayout><AdminEthics /></ProtectedLayout>} />
      <Route path="/admin/reports" element={<ProtectedLayout><AdminReports /></ProtectedLayout>} />
      <Route path="/admin/settings" element={<ProtectedLayout><AdminSettings /></ProtectedLayout>} />

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
