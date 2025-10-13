import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, Calendar, User, FileText, Hash, FileSignature, Loader2, AlertCircle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { vendorService } from '@/services/vendorService';
import { toast } from 'sonner';

export default function TransactionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  // Fetch earnings summary to get transaction data
  const { data: earningsSummary, isLoading, error } = useQuery({
    queryKey: ['vendor-earnings-summary'],
    queryFn: () => vendorService.getEarningsSummary(),
  });

  // Find the specific transaction
  const transaction = earningsSummary?.recent_transactions?.find(
    (t: any) => t.id === id
  );

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'paid': return 'bg-success text-success-foreground';
      case 'pending': return 'bg-warning text-warning-foreground';
      case 'cancelled': return 'bg-destructive text-destructive-foreground';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error || !transaction) {
    return (
      <div className="p-4">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-destructive mb-4" />
          <h3 className="mt-2 text-lg font-semibold">Transaction Not Found</h3>
          <p className="text-muted-foreground">The transaction you're looking for doesn't exist or you don't have access to it.</p>
          <Button onClick={() => navigate(-1)} className="mt-4">
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-6">
      <Button variant="ghost" onClick={() => navigate(-1)}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back
      </Button>

      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Transaction Details</h1>
          <p className="text-muted-foreground mt-1">ID: #{transaction.id}</p>
        </div>
        <Badge className={getStatusColor(transaction.status)}>
          {transaction.status}
        </Badge>
      </div>

      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Payment Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Transaction Date</p>
                  <p className="text-sm text-muted-foreground">
                    {new Date(transaction.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <User className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Customer</p>
                  <p className="text-sm text-muted-foreground">Customer #{transaction.booking_id}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Service</p>
                  <p className="text-sm text-muted-foreground">{transaction.service}</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Amount</p>
                <p className="text-3xl font-bold text-primary">${transaction.amount.toFixed(2)}</p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">Payment Method</p>
                <p className="font-medium">Bank Transfer</p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">Booking ID</p>
                <p className="font-medium">{transaction.booking_id}</p>
              </div>
            </div>
          </div>

          <div className="p-4 bg-muted rounded-lg">
            <div className="flex items-start gap-3">
              <Hash className="h-5 w-5 text-primary mt-0.5" />
              <div className="flex-1">
                <p className="font-medium mb-1">Transaction ID</p>
                <code className="text-xs text-muted-foreground break-all">
                  {transaction.id}
                </code>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Payment Process Information */}
      <Card className="card-elevated">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileSignature className="h-5 w-5 text-primary" />
            Payment Process
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            This payment was automatically released after the customer confirmed service completion with a digital signature. 
            No action was required from the vendor. All payments are processed securely through our payment gateway.
          </p>
        </CardContent>
      </Card>

      <div className="flex gap-3">
        <Button variant="outline">Download Receipt</Button>
        <Button variant="outline">Report Issue</Button>
      </div>
    </div>
  );
}