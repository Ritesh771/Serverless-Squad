import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';

export default function VendorApplicationSuccess() {
  const navigate = useNavigate();

  return (
    <div className="max-w-2xl mx-auto space-y-6 p-4 md:p-6">
      <div className="text-center">
        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
        <h1 className="text-2xl md:text-3xl font-bold">Application Submitted!</h1>
        <p className="text-muted-foreground mt-2">
          Thank you for your interest in joining HomeServe Pro.
        </p>
      </div>

      <Card className="card-elevated">
        <CardHeader>
          <CardTitle>Next Steps</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="bg-primary/10 p-2 rounded-full">
                <span className="text-primary font-bold">1</span>
              </div>
              <div>
                <h3 className="font-medium">Document Verification</h3>
                <p className="text-sm text-muted-foreground">
                  Our team will verify your documents within 24-48 hours.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="bg-primary/10 p-2 rounded-full">
                <span className="text-primary font-bold">2</span>
              </div>
              <div>
                <h3 className="font-medium">Approval Process</h3>
                <p className="text-sm text-muted-foreground">
                  Once verified, our onboarding team will review your application.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="bg-primary/10 p-2 rounded-full">
                <span className="text-primary font-bold">3</span>
              </div>
              <div>
                <h3 className="font-medium">Account Activation</h3>
                <p className="text-sm text-muted-foreground">
                  Upon approval, you'll receive login credentials and onboarding materials.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
            <h4 className="font-medium text-blue-800">Need Help?</h4>
            <p className="text-sm text-blue-700 mt-1">
              If you have any questions, contact our vendor support team at{' '}
              <a href="mailto:vendors@homeservepro.com" className="underline">
                vendors@homeservepro.com
              </a>{' '}
              or call +1 234 567 8900.
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="text-center">
        <Button onClick={() => navigate('/')}>
          Back to Home
        </Button>
      </div>
    </div>
  );
}