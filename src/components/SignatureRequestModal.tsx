import React, { useState } from 'react';
import { useSignatureService } from '../services/signatureService';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useToast } from './ui/use-toast';

interface SignatureRequestModalProps {
  bookingId: string;
  isOpen: boolean;
  onClose: () => void;
  onSignatureRequested: () => void;
}

const SignatureRequestModal: React.FC<SignatureRequestModalProps> = ({ 
  bookingId, 
  isOpen, 
  onClose, 
  onSignatureRequested 
}) => {
  const [rating, setRating] = useState(5);
  const [comments, setComments] = useState('');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async () => {
    setLoading(true);
    try {
      // In a real implementation, you would call the signature service
      // For now, we'll simulate the request
      toast({
        title: "Signature Requested",
        description: "Signature request has been sent to the customer.",
      });
      
      onSignatureRequested();
      onClose();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to request signature. Please try again.",
        variant: "destructive",
      });
      console.error('Failed to request signature:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Request Customer Signature</h2>
        <p className="text-gray-600 mb-6">Send a signature request to the customer for service confirmation.</p>
        
        <div className="mb-4">
          <Label htmlFor="rating" className="block text-sm font-medium text-gray-700 mb-2">
            Service Rating
          </Label>
          <Select value={rating.toString()} onValueChange={(value) => setRating(parseInt(value))}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select rating" />
            </SelectTrigger>
            <SelectContent>
              {[1, 2, 3, 4, 5].map(num => (
                <SelectItem key={num} value={num.toString()}>
                  {num} Star{num > 1 ? 's' : ''}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div className="mb-6">
          <Label htmlFor="comments" className="block text-sm font-medium text-gray-700 mb-2">
            Comments
          </Label>
          <Textarea 
            id="comments"
            value={comments} 
            onChange={(e) => setComments(e.target.value)} 
            placeholder="Additional comments..."
            rows={3}
          />
        </div>
        
        <div className="flex justify-end space-x-3">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? 'Sending...' : 'Send Signature Request'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SignatureRequestModal;