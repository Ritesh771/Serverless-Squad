import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { SignaturePad } from '@/components/SignaturePad';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, Star } from 'lucide-react';
import { toast } from 'sonner';
import { StripePaymentForm } from '@/components/StripePaymentForm';

export default function SignaturePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [satisfactionRating, setSatisfactionRating] = useState(5);
  const [comments, setComments] = useState('');
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [signatureData, setSignatureData] = useState<string | null>(null);

  const handleSave = (signatureData: string) => {
    // Save the signature data and show the payment form
    setSignatureData(signatureData);
    setShowPaymentForm(true);
  };

  const handlePaymentSuccess = () => {
    toast.success('Payment completed successfully!');
    // Redirect to booking details or success page
    navigate(`/customer/my-bookings/${id}`);
  };

  const handlePaymentCancel = () => {
    setShowPaymentForm(false);
  };

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

      {showPaymentForm ? (
        <StripePaymentForm
          paymentId={`payment_${Date.now()}`}
          amount={18000} // Rs 180 in paise
          clientSecret="mock_client_secret_12345"
          onSuccess={handlePaymentSuccess}
          onCancel={handlePaymentCancel}
        />
      ) : (
        <>
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
                  <span className="font-medium">Service Name</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Vendor:</span>
                  <span className="font-medium">Vendor Name</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Amount:</span>
                  <span className="font-bold text-primary">
                    ₹180.00
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <span className="font-medium capitalize">Completed</span>
                </div>
              </div>
            </CardContent>
          </Card>

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

          <SignaturePad onSave={handleSave} />

          <Card className="bg-muted border-none">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground">
                By signing, you will be redirected to complete payment securely.
              </p>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}