import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ArrowLeft, Calendar, MapPin, User, DollarSign, FileText, Image as ImageIcon, Star, Download } from 'lucide-react';
import { toast } from 'sonner';
import { PhotoUpload } from '@/components/PhotoUpload';
// @ts-expect-error - jsPDF types are not properly defined
import jsPDF from 'jspdf';
// @ts-expect-error - autoTable types are not properly defined
import autoTable from 'jspdf-autotable';

export default function BookingDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [rating, setRating] = useState(0);
  const [review, setReview] = useState('');
  const [showReviewForm, setShowReviewForm] = useState(false);

  const [beforePhotos, setBeforePhotos] = useState<File[]>([]);
  const [afterPhotos, setAfterPhotos] = useState<File[]>([]);
  const [aiScore, setAiScore] = useState<number | null>(null);
  const [aiScoreLabel, setAiScoreLabel] = useState<string>('');
  const [isAiAnalyzing, setIsAiAnalyzing] = useState<boolean>(false);

  const handleBeforePhotoUpload = (files: File[]) => {
    setBeforePhotos(files);
    // Trigger AI analysis when both photo sets are uploaded
    if (files.length > 0 && afterPhotos.length > 0) {
      simulateAiAnalysis();
    }
  };

  const handleAfterPhotoUpload = (files: File[]) => {
    setAfterPhotos(files);
    // Trigger AI analysis when both photo sets are uploaded
    if (files.length > 0 && beforePhotos.length > 0) {
      simulateAiAnalysis();
    }
  };

  const simulateAiAnalysis = () => {
    setIsAiAnalyzing(true);
    // Simulate AI analysis delay
    setTimeout(() => {
      // Generate a random score between 1-100
      const score = Math.floor(Math.random() * 100) + 1;
      setAiScore(score);
      
      // Determine score label
      if (score >= 80) {
        setAiScoreLabel('Excellent');
      } else if (score >= 60) {
        setAiScoreLabel('Good');
      } else {
        setAiScoreLabel('Poor');
      }
      
      setIsAiAnalyzing(false);
    }, 2000);
  };

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
    price: 'RS180',
    description: 'Leaking kitchen faucet needs repair',
    
  };

  // Function to generate and download PDF invoice
  const downloadInvoice = () => {
    const doc = new jsPDF();
    
    // Add company header
    doc.setFontSize(20);
    doc.setTextColor(40, 116, 166);
    doc.text('HomeServe Pro', 20, 20);
    
    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text('Professional Home Services', 20, 30);
    doc.text('contact@homeservepro.com', 20, 37);
    doc.text('+1 (555) 123-4567', 20, 44);
    
    // Add invoice title
    doc.setFontSize(18);
    doc.setTextColor(40, 116, 166);
    doc.text('INVOICE', 150, 20);
    
    // Add invoice details
    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text(`Invoice #: INV-${booking.id || '001'}`, 150, 30);
    doc.text(`Date: ${new Date().toLocaleDateString()}`, 150, 37);
    doc.text(`Due Date: ${new Date().toLocaleDateString()}`, 150, 44);
    
    // Add separator line
    doc.setLineWidth(0.5);
    doc.line(20, 50, 190, 50);
    
    // Add billing information
    doc.setFontSize(14);
    doc.setTextColor(40, 116, 166);
    doc.text('Bill To:', 20, 60);
    
    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text(`${localStorage.getItem('user_name') || 'Customer'}`, 20, 70);
    doc.text(`${booking.address}`, 20, 77);
    doc.text(`${booking.pincode}`, 20, 84);
    
    // Add service details
    doc.setFontSize(14);
    doc.setTextColor(40, 116, 166);
    doc.text('Service Details:', 20, 100);
    
    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text(`Booking ID: ${booking.id}`, 20, 110);
    doc.text(`Service: ${booking.service}`, 20, 117);
    doc.text(`Date: ${booking.date}`, 20, 124);
    doc.text(`Time: ${booking.time}`, 20, 131);
    doc.text(`Vendor: ${booking.vendor}`, 20, 138);
    
    // Add description
    doc.setFontSize(12);
    doc.text('Description:', 20, 150);
    doc.setFontSize(10);
    doc.text(`${booking.description}`, 20, 157);
    
    // Add payment details table
    // @ts-expect-error - autoTable types are not properly defined
    autoTable(doc, {
      startY: 170,
      head: [['Description', 'Amount']],
      body: [
        [`${booking.service} Service`, booking.price],
        ['Tax', 'Rs0.00'],
        ['Total', booking.price],
      ],
      styles: {
        fontSize: 10
      },
      headStyles: {
        fillColor: [40, 116, 166]
      }
    });
    
    // Add payment status
    // @ts-expect-error - jsPDF types are not properly defined
    const finalY = doc.lastAutoTable.finalY || 190;
    doc.setFontSize(12);
    doc.setTextColor(40, 116, 166);
    doc.text('Payment Status:', 20, finalY + 20);
    
    doc.setFontSize(12);
    doc.setTextColor(0, 150, 0);
    doc.text('PAID', 50, finalY + 20);
    
    doc.setFontSize(10);
    doc.setTextColor(0, 0, 0);
    doc.text('Transaction ID: TXN-' + Date.now(), 20, finalY + 30);
    
    // Add footer
    doc.setFontSize(10);
    doc.setTextColor(150, 150, 150);
    doc.text('Thank you for choosing HomeServe Pro!', 20, 280);
    doc.text('This is a computer generated invoice', 20, 285);
    
    // Save the PDF
    doc.save(`invoice-${booking.id || '001'}.pdf`);
    
    toast.success('PDF Invoice downloaded successfully!');
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
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-6">
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
              
              {/* Before Photos Upload */}
              <div className="mb-6">
                <PhotoUpload
                  onUpload={handleBeforePhotoUpload}
                  maxFiles={3}
                  title="Before Photos"
                  description="Upload photos showing the condition before work began"
                />
              </div>
              
              {/* After Photos Upload */}
              <div className="mb-6">
                <PhotoUpload
                  onUpload={handleAfterPhotoUpload}
                  maxFiles={3}
                  title="After Photos"
                  description="Upload photos showing the completed work"
                />
              </div>

              {/* AI Predicted Score */}
              {(isAiAnalyzing || aiScore !== null) && (
                <div className="mt-6 p-4 rounded-lg border bg-card text-card-foreground shadow-sm animate-in fade-in-50 slide-in-from-bottom-2 duration-500">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">AI Quality Assessment</h3>
                    {isAiAnalyzing && (
                      <div className="flex items-center text-sm text-muted-foreground">
                        <div className="h-2 w-2 bg-primary rounded-full animate-pulse mr-2"></div>
                        Analyzing...
                      </div>
                    )}
                  </div>
                  
                  {isAiAnalyzing ? (
                    <div className="mt-4 flex flex-col items-center justify-center py-6">
                      <div className="relative">
                        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                        <div className="absolute inset-0 flex items-center justify-center">
                          <ImageIcon className="h-6 w-6 text-primary" />
                        </div>
                      </div>
                      <p className="mt-3 text-sm text-muted-foreground">
                        AI is analyzing your before/after photos...
                      </p>
                    </div>
                  ) : aiScore !== null ? (
                    <div className="mt-4">
                      <div className="flex items-end justify-between">
                        <div>
                          <div className="text-3xl font-bold">
                            {aiScore}
                            <span className="text-lg text-muted-foreground">/100</span>
                          </div>
                          <div className={`text-lg font-semibold ${
                            aiScore >= 80 ? 'text-green-600' : 
                            aiScore >= 60 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {aiScoreLabel}
                          </div>
                        </div>
                        <div className="relative">
                          <div className="radial-progress bg-primary text-primary-foreground w-16 h-16 rounded-full flex items-center justify-center" 
                            style={{ 
                              background: `conic-gradient(${aiScore >= 80 ? '#16a34a' : aiScore >= 60 ? '#ca8a04' : '#dc2626'} ${aiScore * 3.6}deg, #e5e7eb 0deg)` 
                            }}>
                            <span className="text-xs font-bold">{aiScore}%</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="mt-4 pt-4 border-t">
                        <p className="text-sm text-muted-foreground">
                          {aiScore >= 80 
                            ? "Excellent work! The improvement is clearly visible and meets high-quality standards." 
                            : aiScore >= 60 
                            ? "Good job! The work shows noticeable improvement, with some areas for enhancement." 
                            : "The work shows improvement but could benefit from additional attention to detail."}
                        </p>
                      </div>
                    </div>
                  ) : null}
                </div>
              )}
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
              <Button className="w-full" onClick={() => navigate(`/customer/signature/${id || ''}`)}>
                View Signature
              </Button>
              <Button variant="outline" className="w-full" onClick={downloadInvoice}>
                <Download className="mr-2 h-4 w-4" />
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