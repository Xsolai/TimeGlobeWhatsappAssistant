import authService from './authService';

const API_URL = 'https://timeglobe-server.ecomtask.de/api';

interface ApiOptions extends RequestInit {
  skipAuth?: boolean;
}

class ApiService {
  private static instance: ApiService;
  
  private constructor() {}
  
  public static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }
  
  private async getHeaders(options: ApiOptions): Promise<Headers> {
    const headers = new Headers(options.headers);
    headers.set('Content-Type', 'application/json');
    
    if (!options.skipAuth) {
      const token = localStorage.getItem('token');
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
    }
    
    return headers;
  }
  
  public async request<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
    try {
      const headers = await this.getHeaders(options);
      
      const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
      });
      
      if (response.status === 401) {
        // Trigger auth error event
        window.dispatchEvent(new Event('auth-error'));
        throw new Error('Authentication expired');
      }
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }
  
  public async get<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }
  
  public async post<T>(endpoint: string, data: any, options: ApiOptions = {}): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  public async put<T>(endpoint: string, data: any, options: ApiOptions = {}): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }
  
  public async delete<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

export const apiService = ApiService.getInstance();
export default apiService; 