// WhatsApp service for checking WhatsApp status and connection

const API_URL = 'https://timeglobe-server.ecomtask.de/api';

interface WhatsAppStatusResponse {
  status: string;
  whatsapp_number?: string;
}

const whatsappService = {
  // Get WhatsApp connection status
  getStatus: async (): Promise<WhatsAppStatusResponse> => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const headers: Record<string, string> = {
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      };
      
      const response = await fetch(`${API_URL}/whatsapp-status/status`, {
        method: 'GET',
        headers
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching WhatsApp status:', error);
      // Return disconnected status as fallback
      return { status: 'disconnected' };
    }
  }
};

export default whatsappService; 