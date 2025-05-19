import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import authService from '../services/authService';

interface User {
  id: string;
  email: string;
  business_name?: string;
  phone_number?: string;
  timeglobe_auth_key?: string;
  is_active?: boolean;
  created_at?: string;
  whatsapp_number?: string;
  customer_id?: string;
}

interface AuthContextType {
  currentUser: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (
    businessName: string, 
    email: string, 
    phoneNumber: string, 
    password: string
  ) => Promise<boolean>;
  verifyOtp: (email: string, otp: string) => Promise<boolean>;
  resendOtp: (email: string) => Promise<boolean>;
  forgotPassword: (email: string) => Promise<boolean>;
  resetPassword: (businessId: string, token: string, newPassword: string) => Promise<boolean>;
  refreshUserData: () => Promise<boolean>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

// Helper to store user in sessionStorage to persist across page refreshes
const storeUserInSession = (user: User | null) => {
  if (user) {
    sessionStorage.setItem('currentUser', JSON.stringify(user));
  } else {
    sessionStorage.removeItem('currentUser');
  }
};

// Helper to retrieve user from sessionStorage
const getUserFromSession = (): User | null => {
  const userData = sessionStorage.getItem('currentUser');
  return userData ? JSON.parse(userData) : null;
};

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(() => getUserFromSession());
  const [loading, setLoading] = useState<boolean>(true);

  // Update sessionStorage when currentUser changes
  useEffect(() => {
    storeUserInSession(currentUser);
  }, [currentUser]);

  // Listen for auth errors
  useEffect(() => {
    const handleAuthError = () => {
      setCurrentUser(null);
      // Optional: Redirect to login page
      window.location.href = '/login';
    };

    window.addEventListener('auth-error', handleAuthError);
    return () => window.removeEventListener('auth-error', handleAuthError);
  }, []);

  // Helper function to fetch and set user data
  const fetchUserData = async (): Promise<boolean> => {
    try {
      if (authService.isAuthenticated()) {
        try {
          const userData = await authService.getBusinessProfile();
          const user = {
            id: userData.id || '',
            email: userData.email || '',
            business_name: userData.business_name,
            phone_number: userData.phone_number,
            timeglobe_auth_key: userData.timeglobe_auth_key
          };
          setCurrentUser(user);
          return true;
        } catch (error) {
          console.error('Error fetching user profile:', error);
          
          if (error instanceof Error && 
              (error.message.includes('Authentication expired') || 
               error.message.includes('No authentication token found'))) {
            logout();
          }
          return false;
        }
      }
      return false;
    } catch (error) {
      console.error('Error checking authentication:', error);
      return false;
    }
  };

  useEffect(() => {
    // Check if user is already logged in
    const checkAuth = async () => {
      await fetchUserData();
      setLoading(false);
    };

    checkAuth();
  }, []);

  const refreshUserData = async (): Promise<boolean> => {
    setLoading(true);
    const result = await fetchUserData();
    setLoading(false);
    return result;
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      const response = await authService.login({ 
        username: email, 
        password 
      });
      
      // Assuming login immediately returns user data
      const user = {
        id: response.id || '',
        email: email,
        business_name: response.business_name,
        phone_number: response.phone_number,
        timeglobe_auth_key: response.timeglobe_auth_key
      };
      
      setCurrentUser(user);
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (
    businessName: string, 
    email: string, 
    phoneNumber: string, 
    password: string
  ): Promise<boolean> => {
    try {
      setLoading(true);
      await authService.register({
        business_name: businessName,
        email,
        phone_number: phoneNumber,
        password
      });
      
      // After successful registration, user needs to verify OTP
      // We don't log them in automatically
      return true;
    } catch (error) {
      console.error('Signup error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async (email: string, otp: string): Promise<boolean> => {
    try {
      setLoading(true);
      await authService.verifyOtp({ email, otp });
      return true;
    } catch (error) {
      console.error('OTP verification error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const resendOtp = async (email: string): Promise<boolean> => {
    try {
      setLoading(true);
      await authService.resendOtp({ email });
      return true;
    } catch (error) {
      console.error('Resend OTP error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const forgotPassword = async (email: string): Promise<boolean> => {
    try {
      setLoading(true);
      await authService.forgotPassword({ email });
      return true;
    } catch (error) {
      console.error('Forgot password error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (businessId: string, token: string, newPassword: string): Promise<boolean> => {
    try {
      setLoading(true);
      await authService.resetPassword({ 
        business_id: businessId,
        token, 
        new_password: newPassword 
      });
      return true;
    } catch (error) {
      console.error('Reset password error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setCurrentUser(null);
    sessionStorage.removeItem('currentUser');
    // Optional: Redirect to login page
    window.location.href = '/login';
  };

  const value = {
    currentUser,
    isAuthenticated: !!currentUser,
    login,
    signup,
    verifyOtp,
    resendOtp,
    forgotPassword,
    resetPassword,
    refreshUserData,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext; 