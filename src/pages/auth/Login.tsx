import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Home, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await login(username, password);
      toast.success('Login successful!');
    } catch (error) {
      toast.error('Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  // Quick login buttons for demo
  const quickLogin = (role: string) => {
    const demoCredentials: Record<string, { username: string; password: string }> = {
      customer: { username: 'customer1', password: 'demo123' },
      vendor: { username: 'vendor1', password: 'demo123' },
      onboard: { username: 'onboard1', password: 'demo123' },
      ops: { username: 'ops1', password: 'demo123' },
      admin: { username: 'admin1', password: 'demo123' },
    };

    const creds = demoCredentials[role];
    if (creds) {
      setUsername(creds.username);
      setPassword(creds.password);
    }
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
          <CardTitle className="text-2xl font-bold">Welcome Back</CardTitle>
          <CardDescription>Sign in to your HomeServe Pro account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username or Email</Label>
              <Input
                id="username"
                type="text"
                placeholder="username or email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="password">Password</Label>
                <Link
                  to="/auth/forgot-password"
                  className="text-xs text-primary hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-2 text-muted-foreground">Quick Demo Login</span>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mt-4">
              <Button variant="outline" size="sm" onClick={() => quickLogin('customer')} className="flex-1 min-w-[100px]">
                Customer
              </Button>
              <Button variant="outline" size="sm" onClick={() => quickLogin('vendor')} className="flex-1 min-w-[100px]">
                Vendor
              </Button>
              <Button variant="outline" size="sm" onClick={() => quickLogin('onboard')} className="flex-1 min-w-[100px]">
                Onboard
              </Button>
              <Button variant="outline" size="sm" onClick={() => quickLogin('ops')} className="flex-1 min-w-[100px]">
                Ops
              </Button>
              <Button variant="outline" size="sm" onClick={() => quickLogin('admin')} className="flex-1 min-w-[100px]">
                Admin
              </Button>
            </div>
          </div>

          <div className="mt-6 text-center text-sm">
            <span className="text-muted-foreground">Don't have an account? </span>
            <Link to="/auth/register" className="text-primary hover:underline font-medium">
              Sign up
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
