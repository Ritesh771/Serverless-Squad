import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { Loader2, Lock } from 'lucide-react';
import api from '@/services/api';

interface LoginFormData {
  identifier: string;
  otp: string;
}

export default function VendorLogin() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<LoginFormData>({
    identifier: '',
    otp: '',
  });
  const [loading, setLoading] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [timer, setTimer] = useState(0);

  // Timer effect for resend OTP
  useState(() => {
    let interval: NodeJS.Timeout | null = null;
    if (timer > 0) {
      interval = setInterval(() => {
        setTimer(prev => prev - 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [timer]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const sendOtp = async () => {
    if (!formData.identifier) {
      toast.error('Please enter your phone number or email');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/api/auth/vendor/send-otp/', {
        phone: formData.identifier.includes('@') ? undefined : formData.identifier,
        email: formData.identifier.includes('@') ? formData.identifier : undefined,
      });

      if (response.data.otp_sent) {
        setOtpSent(true);
        setTimer(30); // 30 seconds timer
        toast.success('OTP sent successfully!');
      } else {
        toast.error('Failed to send OTP');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async () => {
    if (!formData.identifier || !formData.otp) {
      toast.error('Please enter both identifier and OTP');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/api/auth/vendor/verify-otp/', {
        phone: formData.identifier.includes('@') ? undefined : formData.identifier,
        email: formData.identifier.includes('@') ? formData.identifier : undefined,
        otp: formData.otp,
      });

      if (response.data.access) {
        // Store tokens in localStorage
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        
        toast.success('Login successful!');
        navigate('/vendor/dashboard');
      } else {
        toast.error('Invalid OTP');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to verify OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (otpSent) {
      verifyOtp();
    } else {
      sendOtp();
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md">
        <Card className="card-elevated shadow-xl">
          <CardHeader className="text-center">
            <div className="mx-auto bg-primary/10 p-3 rounded-full w-16 h-16 flex items-center justify-center mb-4">
              <Lock className="h-8 w-8 text-primary" />
            </div>
            <CardTitle className="text-2xl">Vendor Login</CardTitle>
            <CardDescription>
              Access your HomeServe Pro vendor dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="identifier">Phone or Email</Label>
                <Input
                  id="identifier"
                  name="identifier"
                  type="text"
                  placeholder="Enter phone number or email"
                  value={formData.identifier}
                  onChange={handleInputChange}
                  disabled={otpSent}
                />
              </div>

              {otpSent && (
                <div className="space-y-2">
                  <Label htmlFor="otp">OTP</Label>
                  <Input
                    id="otp"
                    name="otp"
                    type="text"
                    placeholder="Enter 6-digit OTP"
                    value={formData.otp}
                    onChange={handleInputChange}
                    maxLength={6}
                  />
                </div>
              )}

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {otpSent ? 'Verifying...' : 'Sending OTP...'}
                  </>
                ) : otpSent ? (
                  'Verify OTP & Login'
                ) : (
                  'Send OTP'
                )}
              </Button>

              {otpSent && (
                <div className="text-center text-sm">
                  {timer > 0 ? (
                    <p className="text-muted-foreground">
                      Resend OTP in {timer} seconds
                    </p>
                  ) : (
                    <Button
                      type="button"
                      variant="link"
                      onClick={sendOtp}
                      className="p-0 h-auto"
                    >
                      Resend OTP
                    </Button>
                  )}
                </div>
              )}

              <div className="text-center text-sm">
                <Link to="/vendor/application" className="text-primary hover:underline">
                  Don't have an account? Apply as a vendor
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}