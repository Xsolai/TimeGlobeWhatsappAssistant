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
  },

  // Update main contract 
  updateMainContract: async (contractData: {
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
      
      const response = await fetch(`${API_URL}/contract/update`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(contractData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error updating main contract:', error);
      throw error;
    }
  },

  // Update Auftragsverarbeitung contract
  updateAuftragsverarbeitung: async (contractData: {
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
      
      const response = await fetch(`${API_URL}/auftragsverarbeitung/update`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(contractData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error updating Auftragsverarbeitung contract:', error);
      throw error;
    }
  },

  // Update Lastschriftmandat 
  updateLastschriftmandat: async (lastschriftData: {
    pdf_file: string;
    file_name: string;
    description: string;
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
      
      const response = await fetch(`${API_URL}/lastschriftmandat/update`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(lastschriftData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error updating Lastschriftmandat:', error);
      throw error;
    }
  }
};

export default contractService; 