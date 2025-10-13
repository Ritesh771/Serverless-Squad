import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { loadStripe, Stripe, StripeElements, StripeCardElement } from '@stripe/stripe-js';
import { toast } from 'sonner';
import { bookingService } from '@/services/bookingService';
import api from '@/services/api';

interface StripePaymentFormProps {
  paymentId: string;
  amount: number;
  clientSecret: string;
  currency?: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const StripePaymentForm = ({ 
  paymentId, 
  amount, 
  clientSecret,
  currency = 'inr', 
  onSuccess,
  onCancel
}: StripePaymentFormProps) => {
  const [stripe, setStripe] = useState<Stripe | null>(null);
  const [elements, setElements] = useState<StripeElements | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isCardComplete, setIsCardComplete] = useState(false); // New state to track card completion
  const cardElementRef = useRef<StripeCardElement | null>(null);
  const formRef = useRef<HTMLFormElement>(null);

  // Initialize Stripe
  useEffect(() => {
    const initializeStripe = async () => {
      try {
        // In a real implementation, you would get this from your backend or environment variables
        const stripePromise = await loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || 'pk_test_51RywjnGe3NmlcQxAnHkCg3M6DHS5gIYXIszN6Df6jaC0YEVcFUT0mFfEQRFiSJfCalB5lHe3j7rAL5T7AhDdeZ7I00cJAgPnc2');
        setStripe(stripePromise);
      } catch (error) {
        console.error('Failed to initialize Stripe:', error);
        setErrorMessage('Failed to initialize payment system');
      }
    };

    initializeStripe();
  }, []);

  // Create Elements instance and card element
  useEffect(() => {
    if (stripe && !elements) {
      const elementsInstance = stripe.elements({
        appearance: {
          theme: 'stripe',
        },
      });
      setElements(elementsInstance);

      // Create card element
      const cardElement = elementsInstance.create('card', {
        style: {
          base: {
            fontSize: '16px',
            color: '#000',
            '::placeholder': {
              color: '#aab7c4',
            },
          },
          invalid: {
            color: '#9e2146',
          },
        },
      });
      
      cardElementRef.current = cardElement;
      
      // Listen for card element changes
      cardElement.on('change', (event) => {
        setIsCardComplete(event.complete || false);
        if (event.error) {
          setErrorMessage(event.error.message);
        } else {
          setErrorMessage(null);
        }
      });
    }
  }, [stripe, elements]);

  // Mount card element
  useEffect(() => {
    if (cardElementRef.current && formRef.current) {
      const cardContainer = formRef.current.querySelector('#card-element');
      if (cardContainer) {
        cardElementRef.current.mount('#card-element');
      }
    }
  }, [elements]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Handle mock payment
    if (clientSecret.startsWith('mock_')) {
      setIsProcessing(true);
      setPaymentStatus('processing');
      setErrorMessage(null);
      
      // Simulate payment processing delay
      setTimeout(() => {
        setPaymentStatus('success');
        toast.success('Payment successful!', {
          description: `Amount: ₹${(amount / 100).toFixed(2)}`
        });
        
        // Simulate backend notification
        setTimeout(() => {
          onSuccess?.();
        }, 1000);
      }, 2000);
      
      return;
    }
    
    if (!stripe || !elements || !cardElementRef.current || !clientSecret) {
      setErrorMessage('Payment system not initialized');
      return;
    }

    setIsProcessing(true);
    setPaymentStatus('processing');
    setErrorMessage(null);

    try {
      // Confirm the payment with the client secret
      const { error, paymentIntent } = await stripe.confirmCardPayment(
        clientSecret,
        {
          payment_method: {
            card: cardElementRef.current!,
            billing_details: {
              name: 'Customer Name',
            },
          },
        }
      );

      if (error) {
        throw new Error(error.message);
      }

      if (paymentIntent && paymentIntent.status === 'succeeded') {
        setPaymentStatus('success');
        toast.success('Payment successful!', {
          description: `Amount: ₹${(amount / 100).toFixed(2)}`
        });
        
        // Notify backend that payment was successful
        try {
          await api.post(`/api/payments/${paymentId}/confirm_payment/`, {
            payment_intent_id: paymentIntent.id,
            status: paymentIntent.status
          });
        } catch (backendError) {
          console.warn('Backend notification failed, but payment succeeded:', backendError);
          // Don't fail the payment if backend notification fails
        }
        
        onSuccess?.();
      } else {
        throw new Error('Payment processing failed');
      }
    } catch (error: unknown) {
      console.error('Payment error:', error);
      setPaymentStatus('error');
      const message = error instanceof Error ? error.message : 'Payment failed. Please try again.';
      setErrorMessage(message);
      toast.error('Payment failed', {
        description: message
      });
    } finally {
      setIsProcessing(false);
    }
  };

  if (paymentStatus === 'success') {
    return (
      <Card className="w-full max-w-md mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
        <CardContent className="pt-6">
          <div className="text-center">
            <div className="relative mx-auto mb-4">
              <CheckCircle className="h-16 w-16 text-success mx-auto" />
              <div className="absolute inset-0 h-16 w-16 animate-ping rounded-full bg-success/20"></div>
            </div>
            <h3 className="text-2xl font-bold mb-2 text-success">Payment Successful!</h3>
            <p className="text-muted-foreground mb-1">
              Your payment has been processed successfully.
            </p>
            <p className="text-lg font-semibold mb-4">
              Amount: ₹{(amount / 100).toFixed(2)}
            </p>
            <div className="bg-muted rounded-lg p-4 mb-4">
              <p className="text-sm text-muted-foreground">Transaction ID</p>
              <p className="font-mono text-sm break-all">{paymentId.substring(0, 8)}...</p>
            </div>
            <Button onClick={onSuccess} className="w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
              Continue
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Show error if no client secret
  if (!clientSecret) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardContent className="pt-6">
          <div className="text-center">
            <AlertCircle className="h-16 w-16 text-destructive mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Payment Error</h3>
            <p className="text-muted-foreground mb-4">
              Payment information is missing. Please contact support.
            </p>
            <Button onClick={onCancel} className="w-full">
              Back to Booking
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Complete Payment</CardTitle>
      </CardHeader>
      <CardContent>
        <form ref={formRef} onSubmit={handleSubmit} className="space-y-4">
          <div>
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-2">
              <Label htmlFor="card-element">Card Information</Label>
              <span className="text-sm text-muted-foreground">
                ₹{(amount / 100).toFixed(2)} {currency.toUpperCase()}
              </span>
            </div>
            <div 
              id="card-element" 
              className="p-3 border border-border rounded-lg bg-white"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Test card: 4242 4242 4242 4242 | Exp: Any future date | CVV: Any 3 digits
            </p>
          </div>

          {errorMessage && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          <div className="flex flex-col sm:flex-row gap-2 pt-2">
            <Button 
              type="button" 
              variant="outline" 
              onClick={onCancel}
              disabled={isProcessing}
              className="w-full"
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isProcessing || !isCardComplete} // Disable button until card is complete
              className="w-full"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                `Pay ₹${(amount / 100).toFixed(2)}`
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};