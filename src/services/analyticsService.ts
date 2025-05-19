// Analytics Service for fetching dashboard data

const API_URL = 'https://timeglobe-server.ecomtask.de/api';

// Analytics Dashboard Data Interface
export interface DashboardData {
  summary: {
    today_appointments?: number;
    todays_services?: number;
    costs_today?: number;
    costs_last_30_days?: number;
    monthly_appointments: number;
    monthly_services_booked: number;
    monthly_growth_rate: number;
  };
  recent_appointments?: Array<{
    booking_id: number;
    service_name: string;
    appointment_date: string;
    appointment_time: string;
    customer_name: string;
    customer_phone: string;
  }>;
  appointment_time_series: Array<{
    date: string;
    count: number;
  }>;
  // Note: top_services and busy_times are no longer in this payload structure
  // Note: revenue is replaced by costs in summary
}

// Neue Interface für Datumsbereiche
export interface DateRangeData {
  start_date: string;
  end_date: string;
  available_dates: string[];
}

// Response structure
interface ApiResponse<T> {
  status: string;
  message: string | null;
  data: T;
}

// Helper function to handle fetch calls with authentication
const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, { ...options, headers });
  
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

// Format date to YYYY-MM-DD
const formatDateForApi = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

const analyticsService = {
  // Get available date ranges
  getAvailableDateRanges: async (): Promise<DateRangeData> => {
    try {
      // Assuming available dates is still needed and provided by a different endpoint or the dashboard endpoint directly
      // If the dashboard endpoint provides it, we might need to adjust getDashboard
      // For now, keeping the separate call based on previous context
      const response = await fetchWithAuth(`${API_URL}/analytics/available-dates`);
      return response.data as DateRangeData;
    } catch (error) {
      console.error('Error fetching available dates:', error);
      throw error;
    }
  },

  // Get dashboard analytics
  getDashboard: async (): Promise<DashboardData> => {
    try {
      const response = await fetchWithAuth(`${API_URL}/analytics/dashboard`);
      // Assuming the new payload structure is directly under 'data'
      return response.data as DashboardData;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  },

  // Get appointments for a specific date (adjusting to new summary field)
  getAppointmentsForDate: async (date: Date): Promise<{ summary: { today_appointments: number } }> => {
    try {
      const formattedDate = formatDateForApi(date);
      // Assuming a specific endpoint for daily appointments might still exist or is needed for the date picker
      // If not, this function might need to be refactored or removed.
      const response = await fetchWithAuth(`${API_URL}/analytics/appointments/date/${formattedDate}`);
      // Assuming the response for this specific endpoint has a similar structure or at least the summary field
      return response.data;
    } catch (error) {
      console.error('Error fetching appointments for date:', error);
      throw error;
    }
  },

  // Get services booked for a specific date (adjusting to new summary field)
  getServicesForDate: async (date: Date): Promise<{ summary: { todays_services: number } }> => {
    try {
      const formattedDate = formatDateForApi(date);
      // Assuming a specific endpoint for daily services might still exist or is needed for the date picker
      // If not, this function might need to be refactored or removed.
      const response = await fetchWithAuth(`${API_URL}/analytics/services/date/${formattedDate}`);
      // Assuming the response for this specific endpoint has a similar structure or at least the summary field
      return response.data;
    } catch (error) {
      console.error('Error fetching services for date:', error);
      throw error;
    }
  },

  // Get analytics for a specific month (adjusting to new summary fields)
  getMonthlyAnalytics: async (date: Date): Promise<DashboardData> => {
    try {
      const year = date.getFullYear(); // Get full year
      const month = date.getMonth() + 1; // JavaScript months are 0-based, add 1
      const formattedMonth = month < 10 ? `0${month}` : `${month}`; // Format month with leading zero if needed
      const response = await fetchWithAuth(`${API_URL}/analytics/dashboard?month=${year}-${formattedMonth}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching monthly analytics:', error);
      throw error;
    }
  }
};

export default analyticsService; 