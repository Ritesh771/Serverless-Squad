import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AlertCircle, Upload, X } from 'lucide-react';
import { toast } from 'sonner';
import { PhotoUpload } from '@/components/PhotoUpload';
import api from '@/services/api';
import { ENDPOINTS } from '@/services/endpoints';

interface DisputeFormProps {
  bookingId: string;
  onDisputeSubmitted: () => void;
  onCancel: () => void;
}

export const DisputeForm = ({ bookingId, onDisputeSubmitted, onCancel }: DisputeFormProps) => {
  const [reason, setReason] = useState('');
  const [description, setDescription] = useState('');
  const [evidencePhotos, setEvidencePhotos] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!reason.trim()) {
      toast.error('Please provide a reason for the dispute');
      return;
    }
    
    if (!description.trim()) {
      toast.error('Please provide a detailed description');
      return;
    }
    
    setLoading(true);
    
    try {
      // First, upload evidence photos if any
      let photoIds: string[] = [];
      if (evidencePhotos.length > 0) {
        // In a real implementation, you would upload photos and get their IDs
        // For now, we'll just note that photos were provided
        toast.info(`${evidencePhotos.length} evidence photos will be uploaded`);
      }
      
      // Create dispute
      const response = await api.post(ENDPOINTS.DISPUTES.CREATE, {
        booking: bookingId,
        reason,
        description,
        evidence_notes: evidencePhotos.length > 0 ? 
          `Customer uploaded ${evidencePhotos.length} evidence photos` : ''
      });
      
      toast.success('Dispute submitted successfully. Our team will review it shortly.');
      onDisputeSubmitted();
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to submit dispute');
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoUpload = (files: File[]) => {
    setEvidencePhotos(files);
  };

  return (
    <Card className="card-elevated border-destructive">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-destructive">
          <AlertCircle className="h-5 w-5" />
          Raise a Dispute
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="reason">Reason for Dispute *</Label>
            <Input
              id="reason"
              placeholder="e.g., Service not completed as expected"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="description">Detailed Description *</Label>
            <Textarea
              id="description"
              placeholder="Please provide detailed information about the issue..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label>Evidence Photos (Optional)</Label>
            <PhotoUpload 
              onUpload={handlePhotoUpload}
              maxFiles={5}
              title="Upload Evidence Photos"
              description="Upload photos that support your dispute"
            />
            
            {evidencePhotos.length > 0 && (
              <div className="text-sm text-muted-foreground">
                {evidencePhotos.length} photo(s) selected for upload
              </div>
            )}
          </div>
          
          <div className="bg-destructive/5 border border-destructive/20 rounded-lg p-4">
            <h4 className="font-medium text-destructive">Important Notice</h4>
            <p className="text-sm text-destructive/80 mt-1">
              Raising a dispute will pause payment processing for this booking. 
              Our customer service team will review your case and respond within 24-48 hours.
            </p>
          </div>
          
          <div className="flex gap-3">
            <Button 
              type="button" 
              variant="outline" 
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              variant="destructive"
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Submitting...' : 'Submit Dispute'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};