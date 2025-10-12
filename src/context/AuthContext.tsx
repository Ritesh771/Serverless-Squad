import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';

export type UserRole = 'customer' | 'vendor' | 'onboard' | 'ops' | 'admin';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  avatar?: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string, role: UserRole) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check for stored user on mount
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    // TODO: Connect to backend API /api/auth/login
    setIsLoading(true);
    
    // Mock login - replace with actual API call
    const mockUser: User = {
      id: '1',
      email,
      name: 'Demo User',
      role: email.includes('vendor') ? 'vendor' : 
            email.includes('admin') ? 'admin' :
            email.includes('ops') ? 'ops' :
            email.includes('onboard') ? 'onboard' : 'customer'
    };

    localStorage.setItem('user', JSON.stringify(mockUser));
    setUser(mockUser);
    setIsLoading(false);

    // Redirect based on role
    const redirectMap: Record<UserRole, string> = {
      customer: '/customer/dashboard',
      vendor: '/vendor/dashboard',
      onboard: '/onboard/dashboard',
      ops: '/ops/dashboard',
      admin: '/admin/dashboard'
    };
    navigate(redirectMap[mockUser.role]);
  };

  const register = async (email: string, password: string, name: string, role: UserRole) => {
    // TODO: Connect to backend API /api/auth/register
    setIsLoading(true);

    const newUser: User = {
      id: Date.now().toString(),
      email,
      name,
      role
    };

    localStorage.setItem('user', JSON.stringify(newUser));
    setUser(newUser);
    setIsLoading(false);

    const redirectMap: Record<UserRole, string> = {
      customer: '/customer/dashboard',
      vendor: '/vendor/dashboard',
      onboard: '/onboard/dashboard',
      ops: '/ops/dashboard',
      admin: '/admin/dashboard'
    };
    navigate(redirectMap[role]);
  };

  const logout = () => {
    localStorage.removeItem('user');
    setUser(null);
    navigate('/auth/login');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading }}>
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
