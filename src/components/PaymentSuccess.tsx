import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle, Download, Home, FileText } from 'lucide-react';
import { toast } from 'sonner';

interface PaymentSuccessProps {
  amount: number;
  paymentId: string;
  onDownloadInvoice: () => void;
}

export const PaymentSuccess = ({ amount, paymentId, onDownloadInvoice }: PaymentSuccessProps) => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [countdown, setCountdown] = useState(5);

  // Countdown timer for automatic redirect
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      navigate(`/customer/my-bookings/${id}`);
    }
  }, [countdown, navigate, id]);

  // Function to generate and download invoice
  const handleDownloadInvoice = () => {
    onDownloadInvoice();
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <Card className="animate-in fade-in slide-in-from-bottom-4 duration-500">
        <CardHeader>
          <div className="text-center">
            <div className="relative mx-auto mb-4">
              <CheckCircle className="h-20 w-20 text-success mx-auto" />
              <div className="absolute inset-0 h-20 w-20 animate-ping rounded-full bg-success/20"></div>
            </div>
            <CardTitle className="text-3xl font-bold text-success">Payment Successful!</CardTitle>
            <p className="text-muted-foreground mt-2">
              Thank you for your payment. Your transaction has been completed successfully.
            </p>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="bg-muted rounded-lg p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Transaction ID</p>
                <p className="font-mono text-sm break-all">#{paymentId.substring(0, 8)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Amount Paid</p>
                <p className="text-2xl font-bold">₹{(amount / 100).toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Date</p>
                <p>{new Date().toLocaleDateString()}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Time</p>
                <p>{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <Button onClick={handleDownloadInvoice} variant="outline" className="flex-1">
              <Download className="mr-2 h-4 w-4" />
              Download Invoice
            </Button>
            <Button onClick={() => navigate(`/customer/my-bookings/${id}`)} className="flex-1">
              <FileText className="mr-2 h-4 w-4" />
              View Booking
            </Button>
          </div>

          <div className="text-center pt-4">
            <p className="text-sm text-muted-foreground">
              Redirecting to booking details in {countdown} seconds...
            </p>
            <Button 
              variant="ghost" 
              onClick={() => navigate('/customer/dashboard')}
              className="mt-2"
            >
              <Home className="mr-2 h-4 w-4" />
              Go to Dashboard
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};