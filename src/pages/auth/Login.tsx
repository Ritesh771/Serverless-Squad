import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Home, Loader2, LogIn } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

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
    } catch {
      toast.error('Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

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
    <div className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-100 overflow-hidden">
      {/* Floating gradient blobs */}
      <div className="absolute w-72 h-72 bg-primary/30 rounded-full blur-3xl top-10 left-10 animate-pulse" />
      <div className="absolute w-96 h-96 bg-blue-400/20 rounded-full blur-3xl bottom-10 right-10 animate-pulse" />

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        <Card className="w-full max-w-xl backdrop-blur-xl bg-white/80 border border-blue-100 shadow-xl rounded-2xl">
          <CardHeader className="text-center space-y-2">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 120, damping: 8 }}
              className="flex justify-center mb-4"
            >
              <div className="h-14 w-14 bg-primary rounded-2xl flex items-center justify-center shadow-md shadow-primary/30">
                <Home className="h-7 w-7 text-primary-foreground" />
              </div>
            </motion.div>

            <CardTitle className="text-3xl font-bold text-gray-800">Welcome Back</CardTitle>
            <CardDescription className="text-gray-500">
              Sign in to your <span className="text-primary font-semibold">HomeServe Pro</span> account
            </CardDescription>
          </CardHeader>

          <CardContent>
            <motion.form
              onSubmit={handleSubmit}
              className="space-y-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="space-y-2">
                <Label htmlFor="username">Username or Email</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="username or email"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className="focus:ring-2 focus:ring-primary focus:outline-none transition-all"
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
                  className="focus:ring-2 focus:ring-primary focus:outline-none transition-all"
                />
              </div>

              <Button
                type="submit"
                className="w-full font-medium transition-all hover:scale-[1.02] active:scale-[0.98]"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  <>
                    <LogIn className="mr-2 h-4 w-4" />
                    Sign In
                  </>
                )}
              </Button>
            </motion.form>
            <div className="mt-6 text-center text-sm">
              <span className="text-muted-foreground">Don’t have an account? </span>
              <Link
                to="/auth/register"
                className="text-primary hover:underline font-medium"
              >
                Sign up
              </Link>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
