// Analytics Service for fetching dashboard data

import { DashboardData, DateRangeData } from '../types';

const API_URL = 'https://timeglobe-server.ecomtask.de/api';



// Response structure
interface ApiResponse<T> {
  status: string;
  message: string | null;
  data: T;
}

// Helper function to format date for API
const formatDateForApi = (date: Date): string => {
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// Helper function to handle API authentication
const fetchWithAuth = async (url: string): Promise<any> => {
  const token = localStorage.getItem('token');
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// Utility to format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
};

const analyticsService = {
  getMonthlyAnalytics: async (selectedMonth: Date): Promise<DashboardData> => {
    try {
      const year = selectedMonth.getFullYear();
      const month = selectedMonth.getMonth() + 1;
      const formattedMonth = month.toString().padStart(2, '0');
      const response = await fetchWithAuth(`${API_URL}/analytics/dashboard?month=${year}-${formattedMonth}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching monthly analytics:', error);
      throw error;
    }
  },

  getAppointmentsForDate: async (date: Date): Promise<DashboardData> => {
    try {
      const formattedDate = formatDateForApi(date);
      const response = await fetchWithAuth(`${API_URL}/analytics/appointments?date=${formattedDate}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching appointments:', error);
      throw error;
    }
  },

  getServicesForDate: async (date: Date): Promise<DashboardData> => {
    try {
      const formattedDate = formatDateForApi(date);
      const response = await fetchWithAuth(`${API_URL}/analytics/services?date=${formattedDate}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching services:', error);
      throw error;
    }
  },

  getAvailableDateRanges: async (): Promise<DateRangeData> => {
    try {
      const response = await fetchWithAuth(`${API_URL}/analytics/available-dates`);
      return response.data;
    } catch (error) {
      console.error('Error fetching available dates:', error);
      throw error;
    }
  }
};

export default analyticsService;