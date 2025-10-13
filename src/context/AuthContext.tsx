import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, type User } from '@/services/authService';

export type UserRole = 'customer' | 'vendor' | 'onboard_manager' | 'ops_manager' | 'super_admin';

export type { User };

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  registerWithOTP: (identifier: string, userData: RegisterData, method?: 'sms' | 'email') => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  sendOTP: (identifier: string, method?: 'sms' | 'email', createUser?: boolean, username?: string) => Promise<void>;
  verifyOTP: (identifier: string, otp: string, method?: 'sms' | 'email') => Promise<void>;
  sendVendorOTP: (identifier: string, method?: 'sms' | 'email') => Promise<void>;
  verifyVendorOTP: (identifier: string, otp: string, method?: 'sms' | 'email') => Promise<void>;
}

interface RegisterData {
  username: string;
  email?: string;
  role: UserRole;
  first_name?: string;
  last_name?: string;
  phone?: string;
  pincode?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check for stored user and token on mount
    const currentUser = authService.getCurrentUser();
    const isAuthenticated = authService.isAuthenticated();

    if (currentUser && isAuthenticated) {
      setUser(currentUser);
    } else {
      // Clear invalid data
      authService.logout();
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    setIsLoading(true);

    try {
      const response = await authService.login({ username, password });
      setUser(response.user);
      navigate(authService.getRoleBasedPath(response.user.role));
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // OTP-based registration for new users
  const registerWithOTP = async (identifier: string, userData: RegisterData, method: 'sms' | 'email' = 'email') => {
    setIsLoading(true);

    try {
      // First, send OTP with user creation enabled
      await authService.sendOTP({
        email: method === 'email' ? identifier : undefined,
        phone: method === 'sms' ? identifier : undefined,
        method,
        create_user: true,
        username: userData.username
      });
      
      // The user will need to verify OTP in the next step
      // This method just sends the OTP
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const sendOTP = async (identifier: string, method: 'sms' | 'email' = 'email', createUser = false, username?: string) => {
    try {
      await authService.sendOTP({
        email: method === 'email' ? identifier : undefined,
        phone: method === 'sms' ? identifier : undefined,
        method,
        create_user: createUser,
        username
      });
    } catch (error) {
      console.error('Send OTP error:', error);
      throw error;
    }
  };

  const verifyOTP = async (identifier: string, otp: string, method: 'sms' | 'email' = 'email') => {
    try {
      const response = await authService.verifyOTP({
        email: method === 'email' ? identifier : undefined,
        phone: method === 'sms' ? identifier : undefined,
        otp
      });
      
      setUser(response.user);
      navigate(authService.getRoleBasedPath(response.user.role));
    } catch (error) {
      console.error('OTP verification error:', error);
      throw error;
    }
  };

  // Vendor-specific OTP methods
  const sendVendorOTP = async (identifier: string, method: 'sms' | 'email' = 'email') => {
    try {
      await authService.sendVendorOTP(identifier, method);
    } catch (error) {
      console.error('Send vendor OTP error:', error);
      throw error;
    }
  };

  const verifyVendorOTP = async (identifier: string, otp: string, method: 'sms' | 'email' = 'email') => {
    try {
      const response = await authService.verifyVendorOTP(identifier, otp, method);
      setUser(response.user);
      navigate(authService.getRoleBasedPath(response.user.role));
    } catch (error) {
      console.error('Verify vendor OTP error:', error);
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    navigate('/auth/login');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        registerWithOTP,
        logout,
        isLoading,
        sendOTP,
        verifyOTP,
        sendVendorOTP,
        verifyVendorOTP,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
