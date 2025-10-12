import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { PhotoUpload } from '@/components/PhotoUpload';
import { ArrowLeft, Calendar, MapPin, User, Phone, FileSignature } from 'lucide-react';
import { toast } from 'sonner';

export default function VendorJobDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [photos, setPhotos] = useState<File[]>([]);

  const job = {
    id,
    service: 'Plumbing Repair',
    customer: 'John Doe',
    customerPhone: '+1 234 567 8900',
    date: '2025-01-15',
    time: '10:00 AM',
    address: '123 Main St, Apartment 4B',
    pincode: '12345',
    status: 'in-progress',
    description: 'Leaking kitchen faucet needs repair',
  };

  const [aiValidation, setAiValidation] = useState({
    status: 'pending',
    score: 0,
    message: '',
  });

  const handlePhotoUpload = (files: File[]) => {
    setPhotos(files);
    toast.success('Photos uploaded successfully!');
    
    // Mock AI validation
    setTimeout(() => {
      const mockScore = Math.floor(Math.random() * 30) + 70;
      setAiValidation({
        status: mockScore >= 80 ? 'approved' : 'review',
        score: mockScore,
        message: mockScore >= 80 
          ? 'Photos meet quality standards' 
          : 'Photos require manual review',
      });
      toast.info(`AI Validation Score: ${mockScore}%`);
    }, 2000);
  };

  const handleRequestSignature = () => {
    // TODO: Trigger signature request to customer
    toast.success('Signature request sent to customer!');
  };

  const handleMarkComplete = () => {
    // TODO: Connect to backend API
    toast.success('Job marked as complete!');
    navigate('/vendor/job-list');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-6">
      <Button variant="ghost" onClick={() => navigate(-1)}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back
      </Button>

      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">{job.service}</h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">Job ID: #{job.id}</p>
        </div>
        <Badge>{job.status.replace('-', ' ')}</Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 card-elevated">
          <CardHeader>
            <CardTitle>Job Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Date & Time</p>
                  <p className="text-sm text-muted-foreground">
                    {job.date} at {job.time}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Service Address</p>
                  <p className="text-sm text-muted-foreground">{job.address}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <User className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Customer</p>
                  <p className="text-sm text-muted-foreground">{job.customer}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Phone className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Contact</p>
                  <p className="text-sm text-muted-foreground">{job.customerPhone}</p>
                </div>
              </div>
            </div>

            <PhotoUpload
              onUpload={handlePhotoUpload}
              title="Upload Job Photos"
              description="Upload before/after photos for AI validation"
            />

            {photos.length > 0 && (
              <div className="p-4 bg-muted rounded-lg border">
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  AI Validation Status
                  <Badge
                    variant={
                      aiValidation.status === 'approved'
                        ? 'default'
                        : aiValidation.status === 'review'
                        ? 'secondary'
                        : 'outline'
                    }
                    className={
                      aiValidation.status === 'approved'
                        ? 'bg-success text-success-foreground'
                        : aiValidation.status === 'review'
                        ? 'bg-warning text-warning-foreground'
                        : ''
                    }
                  >
                    {aiValidation.status === 'pending' ? 'Analyzing...' : aiValidation.status}
                  </Badge>
                </h4>
                {aiValidation.score > 0 && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Quality Score</span>
                      <span className="font-medium">{aiValidation.score}%</span>
                    </div>
                    <div className="w-full bg-background rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          aiValidation.score >= 80 ? 'bg-success' : 'bg-warning'
                        }`}
                        style={{ width: `${aiValidation.score}%` }}
                      />
                    </div>
                    <p className="text-sm text-muted-foreground mt-2">
                      {aiValidation.message}
                    </p>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card className="card-elevated">
            <CardHeader>
              <CardTitle>Payment Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-4">
                <FileSignature className="h-12 w-12 text-primary mx-auto mb-3" />
                <p className="font-medium mb-1">Payment Process</p>
                <p className="text-sm text-muted-foreground">
                  Payment will be automatically released after customer signature confirmation
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="card-elevated">
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full" onClick={handleRequestSignature}>
                Request Signature
              </Button>
              <Button variant="outline" className="w-full" onClick={handleMarkComplete}>
                Mark Complete
              </Button>
              <Button variant="outline" className="w-full">
                Contact Customer
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}