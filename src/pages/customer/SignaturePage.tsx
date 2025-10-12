import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { SignaturePad } from '@/components/SignaturePad';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

export default function SignaturePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [signature, setSignature] = useState<string | null>(null);

  const handleSave = async (signatureData: string) => {
    setSignature(signatureData);
    
    // TODO: Connect to /api/signature/verify
    toast.success('Signature saved successfully!');
    
    setTimeout(() => {
      navigate(`/customer/my-bookings/${id}`);
    }, 1500);
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
              <span className="font-medium">Plumbing Repair</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Vendor:</span>
              <span className="font-medium">John Smith</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Total Amount:</span>
              <span className="font-bold text-primary">$80</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <SignaturePad onSave={handleSave} />

      <Card className="bg-muted border-none">
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            By signing, you confirm that the service has been completed to your satisfaction
            and authorize payment processing. Your signature will be encrypted and stored
            securely with blockchain verification.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
