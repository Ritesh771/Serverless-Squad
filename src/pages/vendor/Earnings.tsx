import { useState, useEffect } from 'react';
import { DashboardCard } from '@/components/DashboardCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DollarSign, TrendingUp, Calendar, ArrowUpRight, Loader2, FileSignature } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '@/services/api';
import { toast } from 'sonner';
import { useWebSocket } from '@/hooks/useWebSocket';

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
  const [summary, setSummary] = useState<EarningsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEarningsSummary();
  }, []);

  // WebSocket connection for real-time updates
  const { isConnected } = useWebSocket((data) => {
    if (data.type === 'earning_update') {
      // Update earnings in real-time
      if (summary) {
        const updatedEarnings = summary.recent_earnings.map(earning => 
          earning.id === (data.earning_id as string)
            ? { ...earning, status: data.status as 'pending' | 'approved' | 'released' | 'on_hold', remarks: data.remarks as string }
            : earning
        );
        
        setSummary({
          ...summary,
          recent_earnings: updatedEarnings,
          pending_earnings: data.pending_earnings as number || summary.pending_earnings,
          total_earnings: data.total_earnings as number || summary.total_earnings
        });
        
        // Show notification
        toast.info('Earning status updated', {
          description: `Payment for ${data.booking_service as string} is now ${data.status as string}`
        });
      }
    } else if (data.type === 'new_earning') {
      // Add new earning to the list
      if (summary) {
        const newEarning: Earning = {
          id: data.earning_id as string,
          amount: data.amount as string,
          status: data.status as 'pending' | 'approved' | 'released' | 'on_hold',
          booking_service: data.booking_service as string,
          customer_name: data.customer_name as string,
          created_at: new Date().toISOString(),
          remarks: data.remarks as string
        };
        
        setSummary({
          ...summary,
          recent_earnings: [newEarning, ...summary.recent_earnings.slice(0, 4)],
          total_earnings: summary.total_earnings + parseFloat(data.amount as string)
        });
        
        // Show notification
        toast.success('New earning added', {
          description: `Payment for ${data.booking_service as string}: $${data.amount as string}`
        });
      }
    }
  });

  const fetchEarningsSummary = async () => {
    try {
      const response = await api.get('/api/earnings/summary/');
      setSummary(response.data);
    } catch (error) {
      toast.error('Failed to load earnings summary');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'released': return 'text-success';
      case 'approved': return 'text-info';
      case 'pending': return 'text-warning';
      case 'on_hold': return 'text-destructive';
      default: return 'text-muted-foreground';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'released': return 'Released';
      case 'approved': return 'Approved';
      case 'pending': return 'Pending';
      case 'on_hold': return 'On Hold';
      default: return status;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Earnings</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Track your payments and transactions</p>
        {isConnected && (
          <div className="flex items-center gap-2 mt-2 text-sm text-success">
            <div className="h-2 w-2 rounded-full bg-success animate-pulse"></div>
            <span>Live updates connected</span>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="Total Earnings"
          value={`$${summary?.total_earnings.toFixed(2) || '0.00'}`}
          icon={DollarSign}
          description="All time"
        />
        <DashboardCard
          title="This Month"
          value={`$${(summary?.total_earnings || 0 * 0.2).toFixed(2)}`}
          icon={TrendingUp}
          trend={{ value: 12, isPositive: true }}
        />
        <DashboardCard
          title="Pending Payouts"
          value={`$${summary?.pending_earnings.toFixed(2) || '0.00'}`}
          icon={Calendar}
          description="Pending approval"
        />
        <DashboardCard
          title="This Week"
          value={`$${(summary?.total_earnings || 0 * 0.05).toFixed(2)}`}
          icon={ArrowUpRight}
          trend={{ value: 8, isPositive: true }}
        />
      </div>

      {/* Payment Information Notice */}
      <Card className="card-elevated">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileSignature className="h-5 w-5 text-primary" />
            Payment Process
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Payments are automatically released after customer signature confirmation. 
            No action required from vendors. All earnings are processed through our secure payment system.
          </p>
        </CardContent>
      </Card>

      {/* Transactions */}
      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {summary?.recent_earnings.map((earning) => (
              <Link
                key={earning.id}
                to={`/vendor/earnings/${earning.id}`}
                className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted transition-colors"
              >
                <div>
                  <p className="font-medium">{earning.booking_service}</p>
                  <p className="text-sm text-muted-foreground">
                    {earning.customer_name} • {new Date(earning.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-primary">${parseFloat(earning.amount).toFixed(2)}</p>
                  <span className={`text-xs ${getStatusColor(earning.status)}`}>
                    {getStatusText(earning.status)}
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