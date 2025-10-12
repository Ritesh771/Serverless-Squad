import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ArrowLeft, Calendar, MapPin, User, DollarSign, FileText, Image as ImageIcon, Star } from 'lucide-react';
import { toast } from 'sonner';

export default function BookingDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [rating, setRating] = useState(0);
  const [review, setReview] = useState('');
  const [showReviewForm, setShowReviewForm] = useState(false);

  // Mock data
  const booking = {
    id,
    service: 'Plumbing Repair',
    vendor: 'John Smith',
    vendorPhone: '+1 234 567 8900',
    date: '2025-01-15',
    time: '10:00 AM',
    address: '123 Main St, Apartment 4B',
    pincode: '12345',
    status: 'Completed',
    price: '$80',
    description: 'Leaking kitchen faucet needs repair',
    photos: [
      'https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=400',
      'https://images.unsplash.com/photo-1607472586893-edb57bdc0e39?w=400',
    ],
  };

  const handleSubmitReview = () => {
    if (rating === 0) {
      toast.error('Please select a rating');
      return;
    }
    // TODO: Connect to backend API
    toast.success('Review submitted successfully!');
    setShowReviewForm(false);
  };

  return (
    <div className="w-full x-auto space-y-6 p-4 md:p-6">
      <Button variant="ghost" onClick={() => navigate(-1)}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back
      </Button>

      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">{booking.service}</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">Booking ID: #{booking.id}</p>
        </div>
        <Badge
          className={
            booking.status === 'Completed'
              ? 'bg-success text-success-foreground'
              : booking.status === 'Pending'
              ? 'bg-warning text-warning-foreground'
              : 'bg-primary text-primary-foreground'
          }
        >
          {booking.status}
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
                    {booking.date} at {booking.time}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Service Address</p>
                  <p className="text-sm text-muted-foreground">{booking.address}</p>
                  <p className="text-sm text-muted-foreground">Pincode: {booking.pincode}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <User className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Vendor</p>
                  <p className="text-sm text-muted-foreground">{booking.vendor}</p>
                  <p className="text-sm text-muted-foreground">{booking.vendorPhone}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Description</p>
                  <p className="text-sm text-muted-foreground">{booking.description}</p>
                </div>
              </div>
            </div>

            <Separator />

            {/* Photos */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <ImageIcon className="h-5 w-5 text-primary" />
                <p className="font-medium">Job Photos</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {booking.photos.map((photo, index) => (
                  <img
                    key={index}
                    src={photo}
                    alt={`Job photo ${index + 1}`}
                    className="w-full h-40 object-cover rounded-lg"
                  />
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="space-y-4">
          <Card className="card-elevated">
            <CardHeader>
              <CardTitle>Payment</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-4">
                <span className="text-muted-foreground">Total Amount</span>
                <span className="text-2xl font-bold text-primary">{booking.price}</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Payment processed securely via HomeServe Pro
              </p>
            </CardContent>
          </Card>

          <Card className="card-elevated">
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full" onClick={() => navigate(`/customer/signature/${id}`)}>
                View Signature
              </Button>
              <Button variant="outline" className="w-full">
                Download Invoice
              </Button>
              <Button variant="outline" className="w-full">
                Contact Vendor
              </Button>
            </CardContent>
          </Card>

          {booking.status === 'Completed' && (
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
