import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { SignaturePad } from '@/components/SignaturePad';
import { PhotoReview } from '@/components/PhotoReview';
import { DisputeForm } from '@/components/DisputeForm';
import { StripePaymentForm } from '@/components/StripePaymentForm';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, AlertTriangle, AlertCircle, Loader2, Star, CreditCard } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';
import { bookingService } from '@/services/bookingService';

interface Photo {
  id: string;
  image: string;
  image_type: 'before' | 'after' | 'additional';
  description: string;
  uploaded_at: string;
  uploaded_by: {
    id: string;
    name: string;
  };
}

interface BookingDetails {
  id: string;
  service: {
    name: string;
  };
  vendor: {
    name: string;
  };
  total_price: number;
  status: string;
  photos: Photo[];
}

export default function SignaturePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [signature, setSignature] = useState<string | null>(null);
  const [booking, setBooking] = useState<BookingDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [photosViewed, setPhotosViewed] = useState(false);
  const [showDisputeForm, setShowDisputeForm] = useState(false);
  const [isSigning, setIsSigning] = useState(false);
  const [satisfactionRating, setSatisfactionRating] = useState(5);
  const [comments, setComments] = useState('');
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [paymentIntent, setPaymentIntent] = useState<any>(null);

  useEffect(() => {
    if (id) {
      fetchBookingDetails();
    }
  }, [id]);

  const fetchBookingDetails = async () => {
    try {
      // First get the signature details
      const signatureResponse = await api.get(`${ENDPOINTS.SIGNATURES.DETAIL(id!)}`);
      const signature = signatureResponse.data;
      
      // Then get the booking details
      const bookingResponse = await api.get(`${ENDPOINTS.BOOKINGS.DETAIL(signature.booking)}`);
      setBooking(bookingResponse.data);
    } catch (error) {
      toast.error('Failed to load signature details');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (signatureData: string) => {
    if (!photosViewed && booking?.photos && booking.photos.length > 0) {
      toast.error('Please review all photos before signing');
      return;
    }

    setSignature(signatureData);
    setIsSigning(true);
    
    try {
      const response = await api.post(`${ENDPOINTS.SIGNATURES.SIGN(id!)}`, {
        signature_data: signatureData,
        satisfaction_rating: satisfactionRating,
        comments: comments || 'Service completed to satisfaction'
      });
      
      toast.success('Signature saved successfully!');
      
      // Check if we need to collect payment
      if (booking && booking.total_price > 0) {
        // Get payment intent from backend
        try {
          const paymentResponse = await api.get(`${ENDPOINTS.BOOKINGS.DETAIL(booking.id)}`);
          const paymentData = paymentResponse.data.payment;
          
          if (paymentData && paymentData.stripe_payment_intent_id) {
            // Get the client secret from the payment intent
            const intentResponse = await api.post(ENDPOINTS.PAYMENTS.GET_CLIENT_SECRET, {
              payment_intent_id: paymentData.stripe_payment_intent_id
            });
            
            if (intentResponse.data.client_secret) {
              setPaymentIntent({
                client_secret: intentResponse.data.client_secret,
                amount: booking.total_price * 100, // Convert to paise
                payment_id: paymentData.id
              });
              setShowPaymentForm(true);
            } else {
              // No payment required or already processed
              setTimeout(() => {
                navigate(`/customer/my-bookings/${booking?.id}`);
              }, 1500);
            }
          } else {
            // No payment record, redirect
            setTimeout(() => {
              navigate(`/customer/my-bookings/${booking?.id}`);
            }, 1500);
          }
        } catch (paymentError) {
          console.error('Error getting payment intent:', paymentError);
          // If payment setup fails, still allow completion
          setTimeout(() => {
            navigate(`/customer/my-bookings/${booking?.id}`);
          }, 1500);
        }
      } else {
        // No payment required
        setTimeout(() => {
          navigate(`/customer/my-bookings/${booking?.id}`);
        }, 1500);
      }
    } catch (error) {
      toast.error('Failed to save signature');
      setIsSigning(false);
    } finally {
      setIsSigning(false);
    }
  };

  const handlePhotosViewed = () => {
    setPhotosViewed(true);
    toast.success('Photos reviewed. You can now proceed with signing.');
  };

  const handlePaymentSuccess = () => {
    toast.success('Payment completed successfully!');
    setTimeout(() => {
      navigate(`/customer/my-bookings/${booking?.id}`);
    }, 1500);
  };

  const handlePaymentCancel = () => {
    setShowPaymentForm(false);
    // Allow user to go back to booking details
    navigate(`/customer/my-bookings/${booking?.id}`);
  };

  const handleDisputeSubmitted = () => {
    setShowDisputeForm(false);
    toast.success('Dispute submitted successfully');
    // Refresh booking details to show updated status
    fetchBookingDetails();
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-6">
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
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

      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Job Completion Signature</h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">
          Please review and sign to confirm job completion
        </p>
      </div>

      {booking?.photos && booking.photos.length > 0 && (
        <Card className="card-elevated border-warning">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-warning">
              <AlertTriangle className="h-5 w-5" />
              Photo Review Required
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-warning">
              Please review all service photos before signing. You must view all photos to proceed.
            </p>
            {!photosViewed && (
              <Button 
                onClick={handlePhotosViewed} 
                className="mt-3"
                variant="outline"
              >
                Mark Photos as Reviewed
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {showDisputeForm ? (
        <DisputeForm 
          bookingId={id!} 
          onDisputeSubmitted={handleDisputeSubmitted}
          onCancel={() => setShowDisputeForm(false)}
        />
      ) : showPaymentForm && paymentIntent ? (
        <StripePaymentForm
          paymentId={paymentIntent.payment_id}
          amount={paymentIntent.amount}
          clientSecret={paymentIntent.client_secret}
          onSuccess={handlePaymentSuccess}
          onCancel={handlePaymentCancel}
        />
      ) : (
        <>
          {booking?.photos && booking.photos.length > 0 && (
            <PhotoReview photos={booking.photos} />
          )}

          <Card className="card-elevated">
            <CardHeader>
              <CardTitle>Job Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Booking ID:</span>
                  <span className="font-medium">#{id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Service:</span>
                  <span className="font-medium">{booking?.service?.name || 'Unknown Service'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Vendor:</span>
                  <span className="font-medium">{booking?.vendor?.name || 'Unknown Vendor'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Amount:</span>
                  <span className="font-bold text-primary">
                    ₹{booking?.total_price?.toFixed(2) || '0.00'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <span className="font-medium capitalize">{booking?.status || 'Unknown'}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-3">
            <Button 
              variant="destructive" 
              onClick={() => setShowDisputeForm(true)}
              className="flex-1"
            >
              <AlertCircle className="h-4 w-4 mr-2" />
              Raise Dispute
            </Button>
          </div>

          <Card className="card-elevated">
            <CardHeader>
              <CardTitle>Service Satisfaction</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="rating">Rate your experience (1-5 stars)</Label>
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setSatisfactionRating(star)}
                      className="focus:outline-none"
                    >
                      <Star
                        className={`h-6 w-6 ${
                          star <= satisfactionRating
                            ? 'fill-warning text-warning'
                            : 'text-muted-foreground'
                        }`}
                      />
                    </button>
                  ))}
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="comments">Comments (Optional)</Label>
                <Textarea
                  id="comments"
                  placeholder="Share your feedback about the service..."
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>

          {isSigning ? (
            <Card className="card-elevated">
              <CardContent className="flex flex-col items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin mb-4" />
                <p className="text-muted-foreground">Processing signature and payment...</p>
              </CardContent>
            </Card>
          ) : (
            <SignaturePad onSave={handleSave} />
          )}

          <Card className="bg-muted border-none">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground">
                By signing, you confirm that the service has been completed to your satisfaction.
                You will be prompted to complete payment securely after signing.
                Your signature will be encrypted and stored securely.
              </p>
              {!photosViewed && booking?.photos && booking.photos.length > 0 && (
                <p className="text-sm text-warning mt-2 flex items-center gap-1">
                  <AlertTriangle className="h-4 w-4" />
                  You must review photos before signing
                </p>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}