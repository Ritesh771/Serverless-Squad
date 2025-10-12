import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  DollarSign, 
  Calendar, 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  TrendingUp,
  Wallet
} from 'lucide-react';

interface Payout {
  id: string;
  amount: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  requestedAt: string;
  processedAt?: string;
  bookingId: string;
  customer: string;
}

export const VendorPayoutPanel = () => {
  const [payouts, setPayouts] = useState<Payout[]>([
    {
      id: '1',
      amount: 8000, // $80.00 in cents
      status: 'completed',
      requestedAt: '2025-01-15T10:30:00Z',
      processedAt: '2025-01-15T14:45:00Z',
      bookingId: 'BK-12345',
      customer: 'Jane Doe'
    },
    {
      id: '2',
      amount: 12000, // $120.00 in cents
      status: 'processing',
      requestedAt: '2025-01-14T09:15:00Z',
      bookingId: 'BK-12346',
      customer: 'Bob Wilson'
    },
    {
      id: '3',
      amount: 10000, // $100.00 in cents
      status: 'pending',
      requestedAt: '2025-01-13T11:20:00Z',
      bookingId: 'BK-12347',
      customer: 'Alice Brown'
    }
  ]);

  const totalEarnings = payouts
    .filter(p => p.status === 'completed')
    .reduce((sum, payout) => sum + payout.amount, 0);

  const pendingPayouts = payouts.filter(p => p.status === 'pending').length;
  const processingPayouts = payouts.filter(p => p.status === 'processing').length;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-success/10 text-success hover:bg-success/10"><CheckCircle className="h-3 w-3 mr-1" />Completed</Badge>;
      case 'processing':
        return <Badge className="bg-warning/10 text-warning hover:bg-warning/10"><Clock className="h-3 w-3 mr-1" />Processing</Badge>;
      case 'pending':
        return <Badge className="bg-secondary/10 text-secondary hover:bg-secondary/10"><Clock className="h-3 w-3 mr-1" />Pending</Badge>;
      case 'failed':
        return <Badge className="bg-destructive/10 text-destructive hover:bg-destructive/10"><AlertCircle className="h-3 w-3 mr-1" />Failed</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <Card className="card-elevated">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Wallet className="h-5 w-5 text-primary" />
          Earnings Overview
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Earnings Summary */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-primary/5 p-4 rounded-lg border border-primary/10">
            <div className="flex items-center gap-2 mb-1">
              <DollarSign className="h-4 w-4 text-primary" />
              <span className="text-sm text-muted-foreground">Total Earnings</span>
            </div>
            <p className="text-2xl font-bold text-primary">${(totalEarnings / 100).toFixed(2)}</p>
          </div>
          
          <div className="bg-warning/5 p-4 rounded-lg border border-warning/10">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="h-4 w-4 text-warning" />
              <span className="text-sm text-muted-foreground">Pending</span>
            </div>
            <p className="text-2xl font-bold text-warning">{pendingPayouts}</p>
          </div>
          
          <div className="bg-success/5 p-4 rounded-lg border border-success/10">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="h-4 w-4 text-success" />
              <span className="text-sm text-muted-foreground">Processing</span>
            </div>
            <p className="text-2xl font-bold text-success">{processingPayouts}</p>
          </div>
        </div>

        {/* Recent Payouts */}
        <div>
          <h4 className="font-medium mb-3">Recent Earnings</h4>
          <div className="space-y-3">
            {payouts.slice(0, 3).map((payout) => (
              <div key={payout.id} className="flex flex-col sm:flex-row sm:justify-between gap-2 p-3 border border-border rounded-lg">
                <div>
                  <p className="font-medium">${(payout.amount / 100).toFixed(2)}</p>
                  <p className="text-sm text-muted-foreground">Booking {payout.bookingId}</p>
                </div>
                <div className="text-right">
                  {getStatusBadge(payout.status)}
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatDate(payout.requestedAt)}
                  </p>
                </div>
              </div>
            ))}
          </div>
          
          {payouts.length === 0 && (
            <p className="text-center text-muted-foreground py-4">
              No earnings history yet
            </p>
          )}
        </div>

        {/* Payment Information Notice */}
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <span className="font-medium">Payment Information:</span> Payments are automatically released after 
            customer signature confirmation. No action required from vendors.
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );
};