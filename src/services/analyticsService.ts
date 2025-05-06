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

const analyticsService = {
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

  // Future analytics methods can be added here
};

export default analyticsService; 