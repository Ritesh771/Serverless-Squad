import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { signatureService, Signature } from '../services/signatureService';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { useToast } from './ui/use-toast';

const SignatureReviewPage: React.FC = () => {
  const { signatureId } = useParams<{ signatureId: string }>();
  const navigate = useNavigate();
  const [signatureData, setSignatureData] = useState<Signature | null>(null);
  const [loading, setLoading] = useState(true);
  const [signing, setSigning] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const fetchSignatureData = async () => {
      if (!signatureId) return;
      
      try {
        const data = await signatureService.getSignature(signatureId);
        setSignatureData(data);
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load signature data.",
          variant: "destructive",
        });
        console.error('Failed to fetch signature data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSignatureData();
  }, [signatureId, toast]);

  const handleSign = async () => {
    if (!signatureId) return;
    
    setSigning(true);
    try {
      // In a real implementation, you would call the signature service
      // For now, we'll simulate the signing process
      toast({
        title: "Document Signed",
        description: "Your signature has been recorded successfully.",
      });
      
      // Redirect to success page
      navigate('/dashboard');
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to sign document. Please try again.",
        variant: "destructive",
      });
      console.error('Failed to sign:', error);
    } finally {
      setSigning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (!signatureData) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800">Signature Not Found</h2>
          <p className="text-gray-600 mt-2">The requested signature could not be found.</p>
          <Button onClick={() => navigate('/dashboard')} className="mt-4">
            Return to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Service Satisfaction Confirmation</CardTitle>
          <p className="text-gray-600">Please review the service details and confirm your satisfaction by signing below.</p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-xl font-semibold mb-4">Booking Details</h2>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">Signature ID</p>
                  <p className="font-medium">{signatureData.id}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Booking ID</p>
                  <p className="font-medium">{signatureData.booking}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <p className="font-medium capitalize">{signatureData.status}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Requested At</p>
                  <p className="font-medium">{new Date(signatureData.requested_at).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Expires At</p>
                  <p className="font-medium">{new Date(signatureData.expires_at).toLocaleString()}</p>
                </div>
              </div>

              <h2 className="text-xl font-semibold mt-8 mb-4">Service Photos</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="border rounded-lg p-4 text-center">
                  <div className="bg-gray-200 border-2 border-dashed rounded-xl w-32 h-32 mx-auto" />
                  <p className="mt-2 text-sm">Before</p>
                </div>
                <div className="border rounded-lg p-4 text-center">
                  <div className="bg-gray-200 border-2 border-dashed rounded-xl w-32 h-32 mx-auto" />
                  <p className="mt-2 text-sm">After</p>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4">Customer Declaration</h2>
              <div className="border rounded-lg p-6 bg-gray-50">
                <p className="mb-4">
                  I confirm that the service was completed to my satisfaction and I am happy with the work performed. 
                  I understand that by signing this document, I am confirming my satisfaction with the service and 
                  authorizing payment to be released to the service provider.
                </p>
                
                <div className="mt-8">
                  <p className="font-medium mb-2">Customer Name</p>
                  <div className="border-b border-gray-300 h-8"></div>
                </div>
                
                <div className="mt-6">
                  <p className="font-medium mb-2">Signature</p>
                  <div className="border-b border-gray-300 h-16"></div>
                </div>
                
                <div className="mt-6">
                  <p className="font-medium mb-2">Date</p>
                  <div className="border-b border-gray-300 h-8"></div>
                </div>
              </div>
              
              <div className="mt-8 flex flex-col sm:flex-row gap-3">
                <Button variant="outline" onClick={() => navigate('/dashboard')} className="flex-1">
                  Cancel
                </Button>
                <Button onClick={handleSign} disabled={signing} className="flex-1">
                  {signing ? 'Processing...' : 'Confirm and Sign'}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SignatureReviewPage;