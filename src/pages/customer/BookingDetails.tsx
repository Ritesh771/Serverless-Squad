import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ArrowLeft, Calendar, MapPin, User, DollarSign, FileText, Image as ImageIcon, Star, Clock, CreditCard, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import { PaymentTimeline } from '@/components/PaymentTimeline';
import { bookingService, type Booking } from '@/services/bookingService';
import { Loader } from '@/components/Loader';

export default function BookingDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [rating, setRating] = useState(0);
  const [review, setReview] = useState('');
  const [showReviewForm, setShowReviewForm] = useState(false);

  // Fetch booking details from backend
  const { data: booking, isLoading, error, refetch } = useQuery({
    queryKey: ['booking', id],
    queryFn: () => bookingService.getBooking(id!),
    enabled: !!id,
    meta: {
      onError: (error: any) => {
        toast.error('Failed to load booking details');
        console.error('Error loading booking:', error);
      }
    }
  });

  const handleSubmitReview = () => {
    if (rating === 0) {
      toast.error('Please select a rating');
      return;
    }
    // TODO: Connect to backend API
    toast.success('Review submitted successfully!');
    setShowReviewForm(false);
  };

  if (isLoading) {
    return (
      <div className="w-full max-w-6xl mx-auto space-y-6 p-4 md:p-6">
        <div className="flex justify-center items-center h-64">
          <Loader />
        </div>
      </div>
    );
  }

  if (error || !booking) {
    return (
      <div className="w-full max-w-6xl mx-auto space-y-6 p-4 md:p-6">
        <div className="text-center py-12">
          <p className="text-muted-foreground">Booking not found</p>
        </div>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6 p-4 md:p-6">
      <Button variant="ghost" onClick={() => navigate(-1)}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back
      </Button>

      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">{booking.service_details?.name || booking.service_name || 'Service'}</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">Booking ID: #{booking.id}</p>
        </div>
        <Badge
          className={
            booking.status === 'signed'
              ? 'bg-success text-success-foreground'
              : booking.status === 'completed'
              ? 'bg-blue-500 text-blue-500-foreground'
              : booking.status === 'pending'
              ? 'bg-warning text-warning-foreground'
              : 'bg-secondary text-secondary-foreground'
          }
        >
          {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main details */}
        <Card className="lg:col-span-2 card-elevated">
          <CardHeader>
            <CardTitle>Booking Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Date & Time</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(booking.scheduled_date)} at {formatTime(booking.scheduled_date)}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Service Address</p>
                  <p className="text-sm text-muted-foreground">Pincode: {booking.pincode}</p>
                </div>
              </div>

              {booking.vendor_name && (
                <div className="flex items-start gap-3">
                  <User className="h-5 w-5 text-primary mt-0.5" />
                  <div>
                    <p className="font-medium">Vendor</p>
                    <p className="text-sm text-muted-foreground">{booking.vendor_name}</p>
                  </div>
                </div>
              )}

              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Description</p>
                  <p className="text-sm text-muted-foreground">{booking.customer_notes || 'No description provided'}</p>
                </div>
              </div>
            </div>

            <Separator />
          </CardContent>
        </Card>

        {/* Actions and Payment */}
        <div className="space-y-4">
          <Card className="card-elevated">
            <CardHeader>
              <CardTitle>Payment</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-4">
                <span className="text-muted-foreground">Total Amount</span>
                <span className="text-2xl font-bold text-primary">₹{Number(booking.total_price).toFixed(2)}</span>
              </div>
              <p className="text-xs text-muted-foreground mb-4">
                Payment processed securely via HomeServe Pro
              </p>
              
              {/* Payment Status Messages */}
              {booking.status === 'completed' && (
                <div className="mt-4">
                  <Button 
                    className="w-full" 
                    onClick={() => navigate(`/customer/signature/${id}`)}
                  >
                    <CreditCard className="h-4 w-4 mr-2" />
                    Sign to Complete & Pay
                  </Button>
                  <p className="text-xs text-muted-foreground mt-2 text-center">
                    Payment will be processed automatically after you sign to confirm job completion
                  </p>
                </div>
              )}
              
              {booking.status === 'signed' && (
                <div className="flex items-center text-success">
                  <CheckCircle className="h-5 w-5 mr-2" />
                  <span className="text-sm font-medium">Payment Completed</span>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="card-elevated">
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {booking.status === 'completed' && (
                <Button 
                  className="w-full" 
                  onClick={() => navigate(`/customer/signature/${id}`)}
                >
                  View/Sign Completion
                </Button>
              )}
              <Button variant="outline" className="w-full">
                Download Invoice
              </Button>
              {booking.vendor_name && (
                <Button variant="outline" className="w-full">
                  Contact Vendor
                </Button>
              )}
            </CardContent>
          </Card>

          {booking.status === 'signed' && (
            <Card className="card-elevated">
              <CardHeader>
                <CardTitle>Rate & Review</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {!showReviewForm ? (
                  <Button className="w-full" onClick={() => setShowReviewForm(true)}>
                    Leave a Review
                  </Button>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <Label>Rating</Label>
                      <div className="flex gap-1 mt-2">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <button
                            key={star}
                            type="button"
                            onClick={() => setRating(star)}
                            className="focus:outline-none"
                          >
                            <Star
                              className={`h-6 w-6 ${
                                star <= rating
                                  ? 'fill-warning text-warning'
                                  : 'text-muted-foreground'
                              }`}
                            />
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="review">Your Review</Label>
                      <Textarea
                        id="review"
                        placeholder="Share your experience..."
                        value={review}
                        onChange={(e) => setReview(e.target.value)}
                        rows={4}
                        className="mt-2"
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button className="flex-1" onClick={handleSubmitReview}>
                        Submit
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => setShowReviewForm(false)}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}