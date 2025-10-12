import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DollarSign, Calendar, User, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

const mockPayments = [
  { id: '1', vendor: 'John Smith', customer: 'Jane Doe', booking: 'BK-12345', amount: '$80', date: '2025-01-15', reason: 'Signature verification pending' },
  { id: '2', vendor: 'Sarah Johnson', customer: 'Bob Wilson', booking: 'BK-12346', amount: '$100', date: '2025-01-14', reason: 'Customer dispute' },
  { id: '3', vendor: 'Mike Davis', customer: 'Alice Brown', booking: 'BK-12347', amount: '$120', date: '2025-01-13', reason: 'Quality assurance check' },
];

export default function ManualPayments() {
  const handleApprove = (id: string) => {
    // TODO: Connect to backend API
    toast.success('Payment approved and released to vendor');
  };

  const handleReject = (id: string) => {
    // TODO: Connect to backend API
    toast.error('Payment rejected');
  };

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Manual Payment Approvals</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">Review and process payment holds</p>
      </div>

      {/* Payments */}
      <div className="grid grid-cols-1 gap-4">
        {mockPayments.map((payment) => (
          <Card key={payment.id} className="card-elevated">
            <CardContent className="p-4 md:p-6">
              <div className="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-4">
                <div className="space-y-4 flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold">Payment Hold #{payment.id}</h3>
                    <Badge variant="secondary">
                      <AlertTriangle className="h-3 w-3 mr-1" />
                      Pending Review
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-start gap-2">
                      <User className="h-4 w-4 text-primary mt-0.5" />
                      <div>
                        <p className="text-muted-foreground">Vendor</p>
                        <p className="font-medium">{payment.vendor}</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-2">
                      <User className="h-4 w-4 text-primary mt-0.5" />
                      <div>
                        <p className="text-muted-foreground">Customer</p>
                        <p className="font-medium">{payment.customer}</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-2">
                      <Calendar className="h-4 w-4 text-primary mt-0.5" />
                      <div>
                        <p className="text-muted-foreground">Date</p>
                        <p className="font-medium">{payment.date}</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-2">
                      <DollarSign className="h-4 w-4 text-primary mt-0.5" />
                      <div>
                        <p className="text-muted-foreground">Amount</p>
                        <p className="font-medium text-primary text-lg">{payment.amount}</p>
                      </div>
                    </div>
                  </div>

                  <div className="p-3 bg-warning/10 rounded-lg border border-warning/20">
                    <p className="text-sm">
                      <span className="font-medium">Hold Reason:</span> {payment.reason}
                    </p>
                  </div>
                </div>

                <div className="flex flex-col gap-2 w-full lg:w-auto lg:ml-6">
                  <Button onClick={() => handleApprove(payment.id)} className="w-full lg:w-auto">
                    Approve Payment
                  </Button>
                  <Button variant="outline" onClick={() => handleReject(payment.id)} className="w-full lg:w-auto">
                    Reject
                  </Button>
                  <Button variant="outline" size="sm" className="w-full lg:w-auto">
                    View Booking
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
