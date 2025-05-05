// Using native fetch API instead of axios

const API_URL = 'https://solasolution.ecomtask.de/app3/api/auth';

// Helper function to handle fetch calls
const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  // Handle specific status codes
  if (response.status === 401) {
    // Token expired or unauthorized - but don't clear token here
    throw new Error('Authentication expired. Please login again.');
  }
  
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }
  
  return response.json();
};

// Check if token is valid by decoding its expiration
const isTokenValid = (): boolean => {
  const token = localStorage.getItem('token');
  if (!token) return false;
  
  try {
    // For JWT tokens, they are structured as header.payload.signature
    // We need to decode the payload part
    const payload = token.split('.')[1];
    if (!payload) return false;
    
    // Decode base64 payload
    const decodedPayload = JSON.parse(atob(payload));
    
    // Check if token has expiration and if it's still valid
    if (decodedPayload.exp) {
      // exp is in seconds, Date.now() is in milliseconds
      return decodedPayload.exp * 1000 > Date.now();
    }
    
    // If token doesn't have expiration, assume it's valid
    return true;
  } catch (e) {
    console.error('Failed to decode token:', e);
    return false;
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
  resetPassword: async (data: { token: string; new_password: string }) => {
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
      
      return await fetchWithAuth(`${API_URL}/business/me`, {
        method: 'GET',
      });
    } catch (error) {
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
    return isTokenValid();
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
};

export default authService; 