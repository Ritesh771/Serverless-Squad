import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Calendar, User, FileText, Hash } from 'lucide-react';

export default function TransactionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const transaction = {
    id,
    date: '2025-01-15',
    customer: 'John Doe',
    service: 'Plumbing Repair',
    amount: '$80',
    status: 'Completed',
    paymentMethod: 'Bank Transfer',
    transactionHash: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
    bookingId: 'BK-12345',
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Button variant="ghost" onClick={() => navigate(-1)}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back
      </Button>

      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Transaction Details</h1>
          <p className="text-muted-foreground mt-1">ID: #{transaction.id}</p>
        </div>
        <Badge className="bg-success text-success-foreground">
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
                  <p className="text-sm text-muted-foreground">{transaction.date}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <User className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Customer</p>
                  <p className="text-sm text-muted-foreground">{transaction.customer}</p>
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
                <p className="text-3xl font-bold text-primary">{transaction.amount}</p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">Payment Method</p>
                <p className="font-medium">{transaction.paymentMethod}</p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">Booking ID</p>
                <p className="font-medium">{transaction.bookingId}</p>
              </div>
            </div>
          </div>

          <div className="p-4 bg-muted rounded-lg">
            <div className="flex items-start gap-3">
              <Hash className="h-5 w-5 text-primary mt-0.5" />
              <div className="flex-1">
                <p className="font-medium mb-1">Blockchain Verification Hash</p>
                <code className="text-xs text-muted-foreground break-all">
                  {transaction.transactionHash}
                </code>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-3">
        <Button variant="outline">Download Receipt</Button>
        <Button variant="outline">Report Issue</Button>
      </div>
    </div>
  );
}
