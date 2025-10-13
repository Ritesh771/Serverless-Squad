import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth, UserRole } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Home, Loader2, Mail, Phone } from 'lucide-react';
import { toast } from 'sonner';

export default function Register() {
  const [step, setStep] = useState<'details' | 'otp'>('details');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [method, setMethod] = useState<'email' | 'sms'>('email');
  const [otp, setOtp] = useState('');
  const [role, setRole] = useState<UserRole>('customer');
  const [loading, setLoading] = useState(false);
  const { registerWithOTP, sendOTP, verifyOTP } = useAuth();
  const navigate = useNavigate();

  const handleDetailsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username.trim()) {
      toast.error('Username is required');
      return;
    }

    const identifier = method === 'email' ? email : phone;
    if (!identifier.trim()) {
      toast.error(`${method === 'email' ? 'Email' : 'Phone'} is required`);
      return;
    }

    if (method === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      toast.error('Please enter a valid email address');
      return;
    }

    if (method === 'sms' && !/^\+?[1-9]\d{1,14}$/.test(phone)) {
      toast.error('Please enter a valid phone number');
      return;
    }

    setLoading(true);
    try {
      await sendOTP(identifier, method, true, username);
      toast.success(`OTP sent to your ${method === 'email' ? 'email' : 'phone number'}`);
      setStep('otp');
    } catch (error: any) {
      toast.error(error.message || 'Failed to send OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOTPSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!otp.trim()) {
      toast.error('Please enter the OTP');
      return;
    }

    setLoading(true);
    try {
      const identifier = method === 'email' ? email : phone;
      await verifyOTP(identifier, otp, method);
      toast.success('Account created successfully!');
      // Navigation is handled by the verifyOTP method
    } catch (error: any) {
      toast.error(error.message || 'Invalid OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setLoading(true);
    try {
      const identifier = method === 'email' ? email : phone;
      await sendOTP(identifier, method, true, username);
      toast.success('OTP resent successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to resend OTP');
    } finally {
      setLoading(false);
    }
  };

  const goBack = () => {
    setStep('details');
    setOtp('');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 via-background to-background p-4">
      <Card className="w-full max-w-md card-elevated">
        <CardHeader className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <div className="h-12 w-12 bg-primary rounded-xl flex items-center justify-center">
              <Home className="h-6 w-6 text-primary-foreground" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">
            {step === 'details' ? 'Create Account' : 'Verify OTP'}
          </CardTitle>
          <CardDescription>
            {step === 'details' 
              ? 'Join HomeServe Pro today'
              : `Enter the OTP sent to your ${method === 'email' ? 'email' : 'phone number'}`
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          {step === 'details' ? (
            <form onSubmit={handleDetailsSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  placeholder="johndoe"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="role">Account Type</Label>
                <Select value={role} onValueChange={(value) => setRole(value as UserRole)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="customer">Customer</SelectItem>
                    <SelectItem value="vendor">Vendor</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Verification Method</Label>
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    type="button"
                    variant={method === 'email' ? 'default' : 'outline'}
                    onClick={() => setMethod('email')}
                    className="flex items-center gap-2"
                  >
                    <Mail className="h-4 w-4" />
                    Email
                  </Button>
                  <Button
                    type="button"
                    variant={method === 'sms' ? 'default' : 'outline'}
                    onClick={() => setMethod('sms')}
                    className="flex items-center gap-2"
                  >
                    <Phone className="h-4 w-4" />
                    SMS
                  </Button>
                </div>
              </div>

              {method === 'email' ? (
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="+1234567890"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    required
                  />
                </div>
              )}

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Sending OTP...
                  </>
                ) : (
                  'Send OTP'
                )}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleOTPSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="otp">Enter OTP</Label>
                <Input
                  id="otp"
                  placeholder="123456"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  maxLength={6}
                  pattern="[0-9]{6}"
                  required
                />
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  'Verify & Create Account'
                )}
              </Button>

              <div className="flex justify-between items-center text-sm">
                <Button type="button" variant="ghost" onClick={goBack}>
                  ← Back
                </Button>
                <Button type="button" variant="ghost" onClick={handleResendOTP} disabled={loading}>
                  Resend OTP
                </Button>
              </div>
            </form>
          )}

          <div className="mt-6 text-center text-sm">
            <span className="text-muted-foreground">Already have an account? </span>
            <Link to="/auth/login" className="text-primary hover:underline font-medium">
              Sign in
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
