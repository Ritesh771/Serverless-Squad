import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { SignaturePad } from '@/components/SignaturePad';
import { PhotoReview } from '@/components/PhotoReview';
import { DisputeForm } from '@/components/DisputeForm';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, AlertTriangle, AlertCircle, CheckCircle, CreditCard } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';

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

  useEffect(() => {
    if (id) {
      fetchBookingDetails();
    }
  }, [id]);

  const fetchBookingDetails = async () => {
    try {
      const response = await api.get(`${ENDPOINTS.CUSTOMER.BOOKING(id!)}/`);
      setBooking(response.data);
    } catch (error) {
      toast.error('Failed to load booking details');
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
    
    try {
      const response = await api.post(ENDPOINTS.SIGNATURE.SIGN(id!), {
        signature_data: signatureData,
        satisfaction_rating: 5, // Default rating, could be made configurable
        comments: 'Service completed to satisfaction'
      });
      
      toast.success('Signature saved successfully! Payment will be processed automatically.', {
        duration: 5000
      });
      
      // Show success message and redirect after a delay
      setTimeout(() => {
        navigate(`/customer/my-bookings/${id}`);
      }, 2000);
    } catch (error) {
      toast.error('Failed to save signature');
    }
  };

  const handlePhotosViewed = () => {
    setPhotosViewed(true);
    toast.success('Photos reviewed. You can now proceed with signing.');
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
          Loading...
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
                    ${booking?.total_price?.toFixed(2) || '0.00'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <span className="font-medium capitalize">{booking?.status || 'Unknown'}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Payment Information */}
          <Alert className="border-primary/20">
            <CreditCard className="h-4 w-4" />
            <AlertDescription>
              <span className="font-medium">Payment Information:</span> Your payment of ${booking?.total_price?.toFixed(2) || '0.00'} 
              will be processed automatically after you sign to confirm job completion.
            </AlertDescription>
          </Alert>

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

          <SignaturePad onSave={handleSave} />

          <Card className="bg-muted border-none">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground">
                By signing, you confirm that the service has been completed to your satisfaction
                and authorize automatic payment processing. Your signature will be encrypted and stored
                securely with blockchain verification.
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