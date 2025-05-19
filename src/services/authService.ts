// Using native fetch API instead of axios

const API_URL = 'https://timeglobe-server.ecomtask.de/api/auth';

// Token refresh configuration
const TOKEN_REFRESH_THRESHOLD = 5 * 60; // 5 minutes in seconds
let refreshPromise: Promise<void> | null = null;

// Helper function to handle fetch calls
const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  
  if (token) {
    // Check if token needs refresh before making the call
    await checkAndRefreshTokenIfNeeded();
    
    // Get potentially refreshed token
    const currentToken = localStorage.getItem('token');
    if (currentToken) {
      headers['Authorization'] = `Bearer ${currentToken}`;
    }
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  // Handle specific status codes
  if (response.status === 401) {
    // Clear token and trigger logout
    localStorage.removeItem('token');
    sessionStorage.removeItem('currentUser');
    window.dispatchEvent(new Event('auth-error'));
    throw new Error('Authentication expired. Please login again.');
  }
  
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }
  
  return response.json();
};

// Check if token is valid by decoding its expiration
const isTokenValid = (token: string): boolean => {
  try {
    const payload = token.split('.')[1];
    if (!payload) return false;
    
    const decodedPayload = JSON.parse(atob(payload));
    
    if (!decodedPayload.exp) return false;
    
    // Check if token expires within threshold
    const expiresIn = decodedPayload.exp - (Date.now() / 1000);
    return expiresIn > 0;
  } catch (e) {
    console.error('Failed to decode token:', e);
    return false;
  }
};

// Check if token needs refresh (expires within threshold)
const needsRefresh = (token: string): boolean => {
  try {
    const payload = token.split('.')[1];
    if (!payload) return true;
    
    const decodedPayload = JSON.parse(atob(payload));
    
    if (!decodedPayload.exp) return true;
    
    const expiresIn = decodedPayload.exp - (Date.now() / 1000);
    return expiresIn < TOKEN_REFRESH_THRESHOLD;
  } catch (e) {
    console.error('Failed to check token refresh:', e);
    return true;
  }
};

// Refresh token if needed
const checkAndRefreshTokenIfNeeded = async () => {
  const token = localStorage.getItem('token');
  if (!token) return;

  if (needsRefresh(token)) {
    // Use singleton promise to prevent multiple simultaneous refresh calls
    if (!refreshPromise) {
      refreshPromise = (async () => {
        try {
          const response = await fetch(`${API_URL}/refresh-token`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const data = await response.json();
            if (data.access_token) {
              localStorage.setItem('token', data.access_token);
            }
          } else {
            // If refresh fails, clear token and trigger logout
            localStorage.removeItem('token');
            sessionStorage.removeItem('currentUser');
            window.dispatchEvent(new Event('auth-error'));
          }
        } catch (error) {
          console.error('Token refresh failed:', error);
          localStorage.removeItem('token');
          sessionStorage.removeItem('currentUser');
          window.dispatchEvent(new Event('auth-error'));
        } finally {
          refreshPromise = null;
        }
      })();
    }
    await refreshPromise;
  }
};

const authService = {
  // Register a new business
  register: async (userData: {
    business_name: string;
    email: string;
    phone_number: string;
    password: string;
  }) => {
    try {
      return await fetchWithAuth(`${API_URL}/register`, {
        method: 'POST',
        body: JSON.stringify(userData),
      });
    } catch (error) {
      throw error;
    }
  },

  // Login
  login: async (credentials: { username: string; password: string }) => {
    try {
      // For form-urlencoded content type
      const formData = new URLSearchParams();
      Object.entries(credentials).forEach(([key, value]) => {
        formData.append(key, value);
      });
      
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
      }
      
      return data;
    } catch (error) {
      throw error;
    }
  },

  // Verify OTP
  verifyOtp: async (data: { email: string; otp: string }) => {
    try {
      return await fetchWithAuth(`${API_URL}/verify-otp`, {
        method: 'POST',
        body: JSON.stringify(data),
      });
    } catch (error) {
      throw error;
    }
  },

  // Resend OTP
  resendOtp: async (data: { email: string }) => {
    try {
      return await fetchWithAuth(`${API_URL}/resend-otp`, {
        method: 'POST',
        body: JSON.stringify(data),
      });
    } catch (error) {
      throw error;
    }
  },

  // Forgot password
  forgotPassword: async (data: { email: string }) => {
    try {
      return await fetchWithAuth(`${API_URL}/forget-password`, {
        method: 'POST',
        body: JSON.stringify(data),
      });
    } catch (error) {
      throw error;
    }
  },

  // Reset password
  resetPassword: async (data: { business_id: string; token: string; new_password: string }) => {
    try {
      return await fetchWithAuth(`${API_URL}/reset-password`, {
        method: 'POST',
        body: JSON.stringify(data),
      });
    } catch (error) {
      throw error;
    }
  },

  // Get business profile
  getBusinessProfile: async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      // Assuming the /business/me endpoint no longer returns the auth key
      return await fetchWithAuth(`${API_URL}/business/me`, {
        method: 'GET',
      });
    } catch (error) {
      throw error;
    }
  },

  // Get TimeGlobe API key for the business
  getTimeglobeAuthKey: async (): Promise<{ timeglobe_auth_key: string; customer_cd: string }> => {
    try {
      return await fetchWithAuth(`${API_URL}/business/timeglobe-key`, {
        method: 'GET',
      });
    } catch (error) {
      console.error('Error fetching TimeGlobe Auth Key:', error);
      throw error;
    }
  },

  // Update business profile
  updateBusinessProfile: async (data: {
    business_name?: string;
    phone_number?: string;
    timeglobe_auth_key?: string;
    whatsapp_number?: string;
  }) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      return await fetchWithAuth(`${API_URL}/business/update`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    } catch (error) {
      throw error;
    }
  },

  // Logout
  logout: () => {
    localStorage.removeItem('token');
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    return token ? isTokenValid(token) : false;
  },

  // Get TimeGlobe API key for the business
  getBusinessTimeglobeKey: async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      return await fetchWithAuth(`${API_URL}/business/timeglobe-key`, {
        method: 'GET',
      });
    } catch (error) {
      throw error;
    }
  },

  // Validate TimeGlobe API key
  validateTimeglobeKey: async (authKey: string) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      return await fetchWithAuth(`${API_URL}/validate-timeglobe-key`, {
        method: 'POST',
        body: JSON.stringify({ auth_key: authKey }),
      });
    } catch (error) {
      throw error;
    }
  },

  // Get business information
  getBusinessInfo: async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      return await fetchWithAuth(`${API_URL}/business/info`, {
        method: 'GET',
      });
    } catch (error) {
      throw error;
    }
  },

  // Update business information
  updateBusinessInfo: async (data: {
    business_name?: string;
    tax_id?: string;
    street_address?: string;
    postal_code?: string;
    city?: string;
    country?: string;
    contact_person?: string;
    phone_number?: string;
    email?: string;
  }) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      return await fetchWithAuth(`${API_URL}/update-business-info`, {
        method: 'POST',
        body: JSON.stringify(data),
      });
    } catch (error) {
      throw error;
    }
  },

  // Delete business info fields
  deleteBusinessInfoFields: async (fields: string[]) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      return await fetchWithAuth(`${API_URL}/delete-business-info`, {
        method: 'DELETE',
        body: JSON.stringify({ fields }),
      });
    } catch (error) {
      throw error;
    }
  },

  // Validate password for auth key visibility
  validatePassword: async (password: string) => {
    try {
      // Get current user email from storage
      const currentUserStr = sessionStorage.getItem('currentUser');
      const currentUser = currentUserStr ? JSON.parse(currentUserStr) : null;
      
      if (!currentUser?.email) {
        console.error('No user email found');
        return false;
      }

      // Use the same format as login
      const formData = new URLSearchParams();
      formData.append('username', currentUser.email);
      formData.append('password', password);
      
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });
      
      if (!response.ok) {
        return false;
      }
      
      const data = await response.json();
      return data.access_token ? true : false;
    } catch (error) {
      console.error('Password validation failed:', error);
      return false;
    }
  },
};

export default authService; 