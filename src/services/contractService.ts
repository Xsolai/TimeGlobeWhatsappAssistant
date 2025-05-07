// Contract service for handling contract operations

const API_URL = 'https://timeglobe-server.ecomtask.de/api';

const contractService = {
  // Create a contract with signature
  createContract: async (contractData: {
    contract_text: string;
    signature_image: string;
  }) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
      
      const response = await fetch(`${API_URL}/contract/create`, {
        method: 'POST',
        headers,
        body: JSON.stringify(contractData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating contract:', error);
      throw error;
    }
  }
};

export default contractService; 