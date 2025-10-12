import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Clock, XCircle, AlertCircle, DollarSign } from 'lucide-react';

interface PaymentTimelineProps {
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'refunded' | 'on_hold';
  amount: number;
  requestedAt: string;
  processedAt?: string;
  releasedAt?: string;
  holdReason?: string;
}

export const PaymentTimeline = ({ 
  status, 
  amount, 
  requestedAt, 
  processedAt, 
  releasedAt,
  holdReason 
}: PaymentTimelineProps) => {
  const getStatusInfo = () => {
    switch (status) {
      case 'pending':
        return {
          icon: <Clock className="h-5 w-5 text-warning" />,
          label: 'Payment Requested',
          description: 'Payment request sent to customer',
          color: 'warning'
        };
      case 'processing':
        return {
          icon: <Clock className="h-5 w-5 text-blue-500" />,
          label: 'Processing',
          description: 'Payment is being processed',
          color: 'info'
        };
      case 'completed':
        return {
          icon: <CheckCircle className="h-5 w-5 text-success" />,
          label: 'Payment Released',
          description: 'Payment successfully transferred to vendor',
          color: 'success'
        };
      case 'failed':
        return {
          icon: <XCircle className="h-5 w-5 text-destructive" />,
          label: 'Payment Failed',
          description: 'Payment processing failed',
          color: 'destructive'
        };
      case 'refunded':
        return {
          icon: <DollarSign className="h-5 w-5 text-muted-foreground" />,
          label: 'Refunded',
          description: 'Payment refunded to customer',
          color: 'secondary'
        };
      case 'on_hold':
        return {
          icon: <AlertCircle className="h-5 w-5 text-yellow-500" />,
          label: 'On Hold',
          description: 'Payment held for review',
          color: 'warning'
        };
      default:
        return {
          icon: <Clock className="h-5 w-5 text-muted-foreground" />,
          label: 'Unknown',
          description: 'Payment status unknown',
          color: 'secondary'
        };
    }
  };

  const statusInfo = getStatusInfo();

  // Timeline steps
  const steps = [
    {
      id: 'requested',
      title: 'Payment Requested',
      description: 'Payment requested after service completion',
      completed: true,
      icon: <CheckCircle className="h-5 w-5 text-success" />,
      date: requestedAt
    },
    {
      id: 'processing',
      title: 'Processing',
      description: 'Payment is being processed',
      completed: status !== 'pending',
      icon: status !== 'pending' ? 
        <CheckCircle className="h-5 w-5 text-success" /> : 
        <Clock className="h-5 w-5 text-muted-foreground" />,
      date: processedAt
    },
    {
      id: 'released',
      title: 'Payment Released',
      description: 'Payment transferred to vendor account',
      completed: status === 'completed',
      icon: status === 'completed' ? 
        <CheckCircle className="h-5 w-5 text-success" /> : 
        <Clock className="h-5 w-5 text-muted-foreground" />,
      date: releasedAt
    }
  ];

  return (
    <Card className="card-elevated">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <DollarSign className="h-5 w-5" />
          Payment Status
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Current Status */}
        <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
          <div className="flex items-center gap-3">
            {statusInfo.icon}
            <div>
              <p className="font-medium">{statusInfo.label}</p>
              <p className="text-sm text-muted-foreground">{statusInfo.description}</p>
            </div>
          </div>
          <Badge 
            variant={
              statusInfo.color === 'success' ? 'success' :
              statusInfo.color === 'warning' ? 'warning' :
              statusInfo.color === 'destructive' ? 'destructive' : 'secondary'
            }
          >
            ${amount.toFixed(2)}
          </Badge>
        </div>

        {/* Timeline */}
        <div className="space-y-4">
          {steps.map((step, index) => (
            <div key={step.id} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className={`p-2 rounded-full ${
                  step.completed ? 'bg-success/10' : 'bg-muted'
                }`}>
                  {step.icon}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-0.5 h-12 mt-1 ${
                    step.completed ? 'bg-success' : 'bg-border'
                  }`} />
                )}
              </div>
              <div className="pb-4 flex-1">
                <p className={`font-medium ${step.completed ? 'text-foreground' : 'text-muted-foreground'}`}>
                  {step.title}
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  {step.description}
                </p>
                {step.date && (
                  <p className="text-xs text-muted-foreground mt-2">
                    {new Date(step.date).toLocaleString()}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Additional info for special statuses */}
        {status === 'on_hold' && holdReason && (
          <div className="p-3 bg-warning/10 border border-warning/20 rounded-lg">
            <p className="text-sm font-medium text-warning">Payment On Hold</p>
            <p className="text-sm text-warning mt-1">{holdReason}</p>
            <p className="text-xs text-warning/80 mt-2">
              Our team is reviewing this payment. You will be notified once it's processed.
            </p>
          </div>
        )}

        {status === 'failed' && (
          <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
            <p className="text-sm font-medium text-destructive">Payment Failed</p>
            <p className="text-sm text-destructive mt-1">
              There was an issue processing your payment. Please contact support.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};