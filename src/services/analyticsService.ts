// Analytics Service for fetching dashboard data

const API_URL = 'https://timeglobe-server.ecomtask.de/api';

// Analytics Dashboard Data Interface
export interface DashboardData {
  summary: {
    today_appointments: number;
    yesterday_appointments: number;
    thirty_day_appointments: number;
    thirty_day_growth_rate: number;
    customer_stats: {
      total_customers: number;
      new_customers_30d: number;
      returning_customers: number;
      retention_rate: number;
    }
  };
  appointment_trend: Array<{
    date: string;
    count: number;
  }>;
  top_services: Array<{
    item_no: number;
    service_name: string;
    booking_count: number;
  }>;
  recent_activities: Array<{
    id: string;
    service_name: string;
    customer_name: string;
    booking_time: string;
    appointment_time: string;
    status: 'confirmed' | 'pending' | 'cancelled';
  }>;
  busy_times: {
    busiest_hours: Array<{
      hour: number;
      count: number;
    }>;
    busiest_days: Array<{
      day: string;
      count: number;
    }>;
  };
  revenue: {
    period_days: number;
    services_booked: number;
    estimated_revenue: number;
    avg_service_value: number;
  };
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
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
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
      return response.data as DashboardData;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  },

  // Get appointments for a specific date
  getAppointmentsForDate: async (date: Date): Promise<DashboardData> => {
    try {
      const formattedDate = formatDateForApi(date);
      const response = await fetchWithAuth(`${API_URL}/analytics/appointments/date/${formattedDate}`);
      return response.data as DashboardData;
    } catch (error) {
      console.error('Error fetching appointments for date:', error);
      throw error;
    }
  },

  // Get services booked for a specific date
  getServicesForDate: async (date: Date): Promise<DashboardData> => {
    try {
      const formattedDate = formatDateForApi(date);
      const response = await fetchWithAuth(`${API_URL}/analytics/services/date/${formattedDate}`);
      return response.data as DashboardData;
    } catch (error) {
      console.error('Error fetching services for date:', error);
      throw error;
    }
  },

  // Get analytics for a specific month
  getMonthlyAnalytics: async (date: Date): Promise<DashboardData> => {
    try {
      const year = date.getFullYear();
      const month = date.getMonth() + 1; // JavaScript months are 0-based
      const response = await fetchWithAuth(`${API_URL}/analytics/monthly/${year}/${month}`);
      return response.data as DashboardData;
    } catch (error) {
      console.error('Error fetching monthly analytics:', error);
      throw error;
    }
  }
};

export default analyticsService; 