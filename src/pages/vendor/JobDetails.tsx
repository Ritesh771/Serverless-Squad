import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { PhotoUpload } from '@/components/PhotoUpload';
import { ArrowLeft, Calendar, MapPin, User, Phone, FileSignature, Loader2, CheckCircle, Camera } from 'lucide-react';
import { toast } from 'sonner';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bookingService } from '@/services/bookingService';
import { vendorService } from '@/services/vendorService';

export default function VendorJobDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [photos, setPhotos] = useState<File[]>([]);

  // Fetch job details
  const { data: job, isLoading, error } = useQuery({
    queryKey: ['vendor-job', id],
    queryFn: () => bookingService.getBooking(id!),
    enabled: !!id,
  });

  // Mutations for job actions
  const startJobMutation = useMutation({
    mutationFn: (jobId: string) => vendorService.startJob(jobId),
    onSuccess: () => {
      toast.success('Job started successfully!');
      queryClient.invalidateQueries({ queryKey: ['vendor-job', id] });
      queryClient.invalidateQueries({ queryKey: ['vendor-bookings'] });
    },
    onError: () => {
      toast.error('Failed to start job');
    },
  });

  const completeJobMutation = useMutation({
    mutationFn: (jobId: string) => vendorService.completeJob(jobId),
    onSuccess: () => {
      toast.success('Job completed successfully!');
      queryClient.invalidateQueries({ queryKey: ['vendor-job', id] });
      queryClient.invalidateQueries({ queryKey: ['vendor-bookings'] });
    },
    onError: () => {
      toast.error('Failed to complete job');
    },
  });

  const requestSignatureMutation = useMutation({
    mutationFn: (jobId: string) => vendorService.requestSignature(jobId),
    onSuccess: () => {
      toast.success('Signature request sent to customer!');
      queryClient.invalidateQueries({ queryKey: ['vendor-job', id] });
    },
    onError: () => {
      toast.error('Failed to request signature');
    },
  });

  const uploadPhotosMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      if (!id) throw new Error('Job ID not found');
      return vendorService.uploadPhotos(id, formData);
    },
    onSuccess: () => {
      toast.success('Photos uploaded successfully!');
      queryClient.invalidateQueries({ queryKey: ['vendor-job', id] });
      setPhotos([]);
    },
    onError: () => {
      toast.error('Failed to upload photos');
    },
  });

  const handlePhotoUpload = (files: File[]) => {
    setPhotos(files);
    // Auto-upload photos when selected
    if (files.length > 0) {
      const formData = new FormData();
      files.forEach((file, index) => {
        formData.append('photos', file);
        formData.append('photo_types', index === 0 ? 'before' : 'after'); // Simple logic for demo
      });
      uploadPhotosMutation.mutate(formData);
    }
  };

  const handleRequestSignature = () => {
    if (!id) return;
    requestSignatureMutation.mutate(id);
  };

  const handleStartJob = () => {
    if (!id) return;
    startJobMutation.mutate(id);
  };

  const handleMarkComplete = () => {
    if (!id) return;
    completeJobMutation.mutate(id);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading job details...</span>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <p className="text-destructive mb-4">Failed to load job details</p>
        <Button onClick={() => navigate(-1)}>Go Back</Button>
      </div>
    );
  }

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
                    {new Date(job.scheduled_date).toLocaleDateString()} at {new Date(job.scheduled_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Service Address</p>
                  <p className="text-sm text-muted-foreground">{job.pincode}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <User className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Customer</p>
                  <p className="text-sm text-muted-foreground">{job.customer_name || `Customer #${job.customer}`}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Phone className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">Contact</p>
                  <p className="text-sm text-muted-foreground">Contact information available after job acceptance</p>
                </div>
              </div>
            </div>

            <PhotoUpload
              onUpload={handlePhotoUpload}
              title="Upload Job Photos"
              description="Upload before/after photos for quality verification"
            />

            {photos.length > 0 && (
              <div className="p-4 bg-muted rounded-lg border">
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  Photo Upload Status
                  <Badge variant="secondary">
                    {uploadPhotosMutation.isPending ? 'Uploading...' : 'Uploaded'}
                  </Badge>
                </h4>
                {uploadPhotosMutation.isPending && (
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Uploading photos...</span>
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
              {job.status === 'confirmed' && (
                <Button className="w-full" onClick={handleStartJob} disabled={startJobMutation.isPending}>
                  {startJobMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <CheckCircle className="h-4 w-4 mr-2" />
                  )}
                  Start Job
                </Button>
              )}

              {job.status === 'in_progress' && (
                <>
                  <Button className="w-full" onClick={handleMarkComplete} disabled={completeJobMutation.isPending}>
                    {completeJobMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <CheckCircle className="h-4 w-4 mr-2" />
                    )}
                    Mark Complete
                  </Button>
                  <Button variant="outline" className="w-full" onClick={handleRequestSignature} disabled={requestSignatureMutation.isPending}>
                    {requestSignatureMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <FileSignature className="h-4 w-4 mr-2" />
                    )}
                    Request Signature
                  </Button>
                </>
              )}

              {job.status === 'completed' && (
                <Button variant="outline" className="w-full" onClick={handleRequestSignature} disabled={requestSignatureMutation.isPending}>
                  {requestSignatureMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <FileSignature className="h-4 w-4 mr-2" />
                  )}
                  Request Signature
                </Button>
              )}

              <Button variant="outline" className="w-full">
                <Phone className="h-4 w-4 mr-2" />
                Contact Customer
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}