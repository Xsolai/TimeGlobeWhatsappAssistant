// WhatsApp service for checking WhatsApp status and connection

import apiService from './apiService';

interface WhatsAppStatusResponse {
  status: 'connected' | 'disconnected';
  whatsapp_number?: string;
}

const whatsappService = {
  // Get WhatsApp connection status
  getStatus: async (): Promise<WhatsAppStatusResponse> => {
    try {
      return await apiService.get<WhatsAppStatusResponse>('/whatsapp-status/status');
    } catch (error) {
      console.error('Error fetching WhatsApp status:', error);
      // Return disconnected status as fallback
      return { status: 'disconnected' };
    }
  }
};

export default whatsappService; 