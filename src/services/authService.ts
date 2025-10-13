import api from './api';
import { ENDPOINTS } from './endpoints';

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_verified: boolean;
  phone?: string;
  pincode?: string;
  first_name?: string;
  last_name?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  role: 'customer' | 'vendor';
  phone?: string;
  pincode?: string;
  first_name?: string;
  last_name?: string;
}

export interface OTPRequest {
  email?: string;
  phone?: string;
  method: 'email' | 'sms';
  create_user?: boolean;
  username?: string;
}

export interface OTPVerifyRequest {
  email?: string;
  phone?: string;
  otp: string;
}

class AuthService {
  // Store tokens in localStorage
  private static TOKEN_KEY = 'access_token';
  private static REFRESH_KEY = 'refresh_token';
  private static USER_KEY = 'user';

  // Traditional password-based registration
  async register(request: RegisterRequest): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>(ENDPOINTS.AUTH.REGISTER, request);
      
      if (response.data.access) {
        this.setTokens(response.data.access, response.data.refresh);
        this.setUser(response.data.user);
      }
      
      return response.data;
    } catch (error: any) {
      console.error('Registration error:', error);
      throw new Error(
        error.response?.data?.error ||
        error.response?.data?.username?.[0] ||
        error.response?.data?.email?.[0] ||
        error.response?.data?.password?.[0] ||
        'Registration failed. Please try again.'
      );
    }
  }

  // Traditional login (for existing users with passwords)
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>(ENDPOINTS.AUTH.LOGIN, credentials);
      
      if (response.data.access) {
        this.setTokens(response.data.access, response.data.refresh);
        this.setUser(response.data.user);
      }
      
      return response.data;
    } catch (error: any) {
      console.error('Login error:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.response?.data?.non_field_errors?.[0] || 
        'Login failed. Please check your credentials.'
      );
    }
  }

  // OTP-based registration flow
  async sendOTP(request: OTPRequest): Promise<{ message: string; method: string; otp_sent: boolean }> {
    try {
      const response = await api.post(ENDPOINTS.AUTH.SEND_OTP, request);
      return response.data;
    } catch (error: any) {
      console.error('Send OTP error:', error);
      throw new Error(
        error.response?.data?.error || 
        'Failed to send OTP. Please try again.'
      );
    }
  }

  // Verify OTP and get tokens
  async verifyOTP(request: OTPVerifyRequest): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>(ENDPOINTS.AUTH.VERIFY_OTP, request);
      
      if (response.data.access) {
        this.setTokens(response.data.access, response.data.refresh);
        this.setUser(response.data.user);
      }
      
      return response.data;
    } catch (error: any) {
      console.error('Verify OTP error:', error);
      throw new Error(
        error.response?.data?.error || 
        'OTP verification failed. Please check your OTP.'
      );
    }
  }

  // Vendor-specific OTP methods
  async sendVendorOTP(identifier: string, method: 'email' | 'sms' = 'email'): Promise<{ message: string; method: string }> {
    try {
      const payload = method === 'email' 
        ? { email: identifier, method } 
        : { phone: identifier, method };
        
      const response = await api.post(ENDPOINTS.AUTH.VENDOR_SEND_OTP, payload);
      return response.data;
    } catch (error: any) {
      console.error('Send vendor OTP error:', error);
      throw new Error(
        error.response?.data?.error || 
        'Failed to send vendor OTP. Please try again.'
      );
    }
  }

  async verifyVendorOTP(identifier: string, otp: string, method: 'email' | 'sms' = 'email'): Promise<LoginResponse> {
    try {
      const payload = method === 'email' 
        ? { email: identifier, otp } 
        : { phone: identifier, otp };
        
      const response = await api.post<LoginResponse>(ENDPOINTS.AUTH.VENDOR_VERIFY_OTP, payload);
      
      if (response.data.access) {
        this.setTokens(response.data.access, response.data.refresh);
        this.setUser(response.data.user);
      }
      
      return response.data;
    } catch (error: any) {
      console.error('Verify vendor OTP error:', error);
      throw new Error(
        error.response?.data?.error || 
        'Vendor OTP verification failed. Please check your OTP.'
      );
    }
  }

  // Token management
  private setTokens(access: string, refresh: string): void {
    localStorage.setItem(AuthService.TOKEN_KEY, access);
    localStorage.setItem(AuthService.REFRESH_KEY, refresh);
  }

  private setUser(user: User): void {
    localStorage.setItem(AuthService.USER_KEY, JSON.stringify(user));
  }

  getAccessToken(): string | null {
    return localStorage.getItem(AuthService.TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(AuthService.REFRESH_KEY);
  }

  getCurrentUser(): User | null {
    try {
      const user = localStorage.getItem(AuthService.USER_KEY);
      return user ? JSON.parse(user) : null;
    } catch {
      return null;
    }
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken() && !!this.getCurrentUser();
  }

  // Refresh access token
  async refreshToken(): Promise<string> {
    try {
      const refresh = this.getRefreshToken();
      if (!refresh) {
        throw new Error('No refresh token available');
      }

      const response = await api.post(ENDPOINTS.AUTH.REFRESH, { refresh });
      const newAccessToken = response.data.access;
      
      localStorage.setItem(AuthService.TOKEN_KEY, newAccessToken);
      return newAccessToken;
    } catch (error: any) {
      console.error('Token refresh error:', error);
      this.logout();
      throw new Error('Session expired. Please login again.');
    }
  }

  // Logout
  logout(): void {
    localStorage.removeItem(AuthService.TOKEN_KEY);
    localStorage.removeItem(AuthService.REFRESH_KEY);
    localStorage.removeItem(AuthService.USER_KEY);
  }

  // Helper method to get role-based redirect path
  getRoleBasedPath(role: string): string {
    const roleRoutes: Record<string, string> = {
      customer: '/customer/dashboard',
      vendor: '/vendor/dashboard',
      onboard_manager: '/onboard-manager/dashboard',
      ops_manager: '/ops-manager/dashboard',
      super_admin: '/super-admin/dashboard',
    };
    return roleRoutes[role] || '/customer/dashboard';
  }
}

export const authService = new AuthService();
export default authService;