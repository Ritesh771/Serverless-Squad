import { useState, useEffect } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DollarSign, TrendingUp, Calendar, ArrowUpRight, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { vendorService } from '@/services/vendorService';
import { toast } from 'sonner';

interface Earning {
  id: string;
  amount: string;
  status: 'pending' | 'approved' | 'released' | 'on_hold';
  booking_service: string;
  customer_name: string;
  created_at: string;
  remarks: string;
}

interface EarningsSummary {
  total_earnings: number;
  pending_earnings: number;
  recent_earnings: Earning[];
}

export default function VendorEarnings() {
  // Fetch earnings summary using the new vendor service
  const { data: earningsSummary, isLoading, error } = useQuery({
    queryKey: ['vendor-earnings-summary'],
    queryFn: () => vendorService.getEarningsSummary(),
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'text-success';
      case 'pending': return 'text-warning';
      case 'cancelled': return 'text-destructive';
      default: return 'text-muted-foreground';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'paid': return 'Paid';
      case 'pending': return 'Pending';
      case 'cancelled': return 'Cancelled';
      default: return status;
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-center">
          <p className="text-destructive mb-4">Failed to load earnings data</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-primary text-primary-foreground rounded"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Earnings</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Track your payments and transactions</p>
        {/* Removed live updates indicator to fix WebSocket issues */}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Earnings"
          value={`$${earningsSummary?.summary?.total_earnings?.toFixed(2) || '0.00'}`}
          icon={DollarSign}
          description="All time"
        />
        <DashboardCard
          title="This Month"
          value={`$${((earningsSummary?.summary?.total_earnings || 0) * 0.2).toFixed(2)}`}
          icon={TrendingUp}
          trend={{ value: 12, isPositive: true }}
        />
        <DashboardCard
          title="Pending Payouts"
          value={`$${earningsSummary?.summary?.pending_earnings?.toFixed(2) || '0.00'}`}
          icon={Calendar}
          description="Pending approval"
        />
        <DashboardCard
          title="This Week"
          value={`$${((earningsSummary?.summary?.total_earnings || 0) * 0.05).toFixed(2)}`}
          icon={ArrowUpRight}
          trend={{ value: 8, isPositive: true }}
        />
      </div>

      {/* Transactions */}
      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {earningsSummary?.recent_transactions?.map((transaction) => (
              <Link
                key={transaction.id}
                to={`/vendor/earnings/${transaction.id}`}
                className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted transition-colors"
              >
                <div>
                  <p className="font-medium">{transaction.service}</p>
                  <p className="text-sm text-muted-foreground">
                    Booking #{transaction.booking_id} • {new Date(transaction.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-primary">${transaction.amount.toFixed(2)}</p>
                  <span className={`text-xs ${getStatusColor(transaction.status)}`}>
                    {getStatusText(transaction.status)}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}