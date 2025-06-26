import React, { useRef, useState, useEffect } from 'react';
import { Box, Button, Typography, Checkbox, FormControlLabel, Paper, Alert, useTheme, Stepper, Step, StepLabel, StepButton } from '@mui/material';
import SignatureCanvas from 'react-signature-canvas';
import { OnboardingFormData } from '../../types';
import { PDFDocument, rgb } from 'pdf-lib';
import Description from '@mui/icons-material/Description';
import ArrowBack from '@mui/icons-material/ArrowBack';
import ArrowForward from '@mui/icons-material/ArrowForward';
import Edit from '@mui/icons-material/Edit';
import Delete from '@mui/icons-material/Delete';
import Check from '@mui/icons-material/Check';
import DescriptionOutlined from '@mui/icons-material/DescriptionOutlined';
import Article from '@mui/icons-material/Article';
import Payment from '@mui/icons-material/Payment';
import Download from '@mui/icons-material/Download';
import Upload from '@mui/icons-material/Upload';
import FileUpload from '@mui/icons-material/FileUpload';
import CloudUpload from '@mui/icons-material/CloudUpload';
import InfoOutlined from '@mui/icons-material/InfoOutlined';
import Euro from '@mui/icons-material/Euro';
// Import contract text from separate files
import { getMainContractText, getMainContractPreviewText } from '../../contracts/MainContract';
import { getDataProcessingContractText, getDataProcessingContractPreviewText } from '../../contracts/DataProcessingContract';
import { getMainContractSections, getDataProcessingContractSections } from '../../contracts/contractSections';
import ContractViewer from './ContractViewer';
import pdfService from '../../services/pdfService';

// Inline contract service if import fails
const API_URL = 'https://timeglobe-server.ecomtask.de';

const inlineContractService = {
  createContract: async (contractData: {
    contract_text: string;
    signature_image: string;
  }) => {
    try {
      const token = localStorage.getItem('token');
      console.log('Token available:', !!token);
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      // Only add Authorization header if token is available
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        console.warn('No authentication token found, proceeding without auth header');
      }
      
      const requestBody = {
        contract_text: contractData.contract_text,
        signature_image: contractData.signature_image
      };
      
      console.log(`Making API call to ${API_URL}/api/contract/create`);
      console.log('Request headers:', { 
        ...headers, 
        Authorization: headers.Authorization ? 'Bearer [REDACTED]' : undefined 
      });
      console.log('Request body preview:', { 
        contract_text: requestBody.contract_text,
        signature_image: `[Base64 string of length ${requestBody.signature_image.length}]` 
      });
      
      const response = await fetch(`${API_URL}/api/contract/create`, {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody),
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Could not read error response');
        console.error(`API error: ${response.status} ${response.statusText}`);
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('API response:', result);
      return result;
    } catch (error) {
      console.error('Error creating contract:', error);
      throw error;
    }
  },

  // Function to create an Auftragsverarbeitung contract
  createDataProcessingContract: async (contractData: {
    contract_text: string;
    signature_image: string;
  }) => {
    try {
      const token = localStorage.getItem('token');
      console.log('Token available for data processing contract:', !!token);
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      // Only add Authorization header if token is available
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        console.warn('No authentication token found, proceeding without auth header');
      }
      
      const requestBody = {
        contract_text: contractData.contract_text,
        signature_image: contractData.signature_image
      };
      
      console.log(`Making API call to ${API_URL}/api/auftragsverarbeitung/create`);
      console.log('Request headers:', { 
        ...headers, 
        Authorization: headers.Authorization ? 'Bearer [REDACTED]' : undefined 
      });
      console.log('Request body preview:', { 
        contract_text: requestBody.contract_text,
        signature_image: `[Base64 string of length ${requestBody.signature_image.length}]` 
      });
      
      const response = await fetch(`${API_URL}/api/auftragsverarbeitung/create`, {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody),
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Could not read error response');
        console.error(`API error: ${response.status} ${response.statusText}`);
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('API response for data processing contract:', result);
      return result;
    } catch (error) {
      console.error('Error creating data processing contract:', error);
      throw error;
    }
  },

  // Function to update the main contract
  updateMainContract: async (contractData: {
    contract_text: string;
    signature_image: string;
  }) => {
    try {
      const token = localStorage.getItem('token');
      console.log('Token available for main contract update:', !!token);
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      // Only add Authorization header if token is available
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        console.warn('No authentication token found, proceeding without auth header');
      }
      
      const requestBody = {
        contract_text: contractData.contract_text,
        signature_image: contractData.signature_image
      };
      
      console.log(`Making API call to ${API_URL}/api/contract/update`);
      console.log('Request headers:', { 
        ...headers, 
        Authorization: headers.Authorization ? 'Bearer [REDACTED]' : undefined 
      });
      console.log('Request body preview:', { 
        contract_text: requestBody.contract_text,
        signature_image: `[Base64 string of length ${requestBody.signature_image.length}]` 
      });
      
      const response = await fetch(`${API_URL}/api/contract/update`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(requestBody),
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Could not read error response');
        console.error(`API error: ${response.status} ${response.statusText}`);
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('API response for main contract update:', result);
      return result;
    } catch (error) {
      console.error('Error updating main contract:', error);
      throw error;
    }
  },

  // Function to update Auftragsverarbeitung contract
  updateAuftragsverarbeitung: async (contractData: {
    contract_text: string;
    signature_image: string;
  }) => {
    try {
      const token = localStorage.getItem('token');
      console.log('Token available for Auftragsverarbeitung update:', !!token);
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      // Only add Authorization header if token is available
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        console.warn('No authentication token found, proceeding without auth header');
      }
      
      const requestBody = {
        contract_text: contractData.contract_text,
        signature_image: contractData.signature_image
      };
      
      console.log(`Making API call to ${API_URL}/api/auftragsverarbeitung/update`);
      console.log('Request headers:', { 
        ...headers, 
        Authorization: headers.Authorization ? 'Bearer [REDACTED]' : undefined 
      });
      console.log('Request body preview:', { 
        contract_text: requestBody.contract_text,
        signature_image: `[Base64 string of length ${requestBody.signature_image.length}]` 
      });
      
      const response = await fetch(`${API_URL}/api/auftragsverarbeitung/update`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(requestBody),
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Could not read error response');
        console.error(`API error: ${response.status} ${response.statusText}`);
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('API response for Auftragsverarbeitung update:', result);
      return result;
    } catch (error) {
      console.error('Error updating Auftragsverarbeitung contract:', error);
      throw error;
    }
  },

  // Function to get existing contract
  getContract: async () => {
    try {
      const token = localStorage.getItem('token');
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      // Only add Authorization header if token is available
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        console.warn('No authentication token found, proceeding without auth header');
      }
      
      console.log(`Making API call to ${API_URL}/api/contract`);
      console.log('Request headers:', { 
        ...headers, 
        Authorization: headers.Authorization ? 'Bearer [REDACTED]' : undefined 
      });
      
      const response = await fetch(`${API_URL}/api/contract`, {
        method: 'GET',
        headers
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (!response.ok) {
        if (response.status === 404) {
          // No contract found - this is a valid case, not an error
          console.log('No existing contract found');
          return null;
        }
        
        const errorText = await response.text().catch(() => 'Could not read error response');
        console.error(`API error: ${response.status} ${response.statusText}`);
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Contract API response:', result);
      return result;
    } catch (error) {
      console.error('Error fetching contract:', error);
      return null;
    }
  },

  // Function to get existing Auftragsverarbeitung contract
  getDataProcessingContract: async () => {
    try {
      const token = localStorage.getItem('token');
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      // Only add Authorization header if token is available
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        console.warn('No authentication token found, proceeding without auth header');
      }
      
      console.log(`Making API call to ${API_URL}/api/auftragsverarbeitung`);
      console.log('Request headers:', { 
        ...headers, 
        Authorization: headers.Authorization ? 'Bearer [REDACTED]' : undefined 
      });
      
      const response = await fetch(`${API_URL}/api/auftragsverarbeitung`, {
        method: 'GET',
        headers
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (!response.ok) {
        if (response.status === 404) {
          // No contract found - this is a valid case, not an error
          console.log('No existing data processing contract found');
          return null;
        }
        
        const errorText = await response.text().catch(() => 'Could not read error response');
        console.error(`API error: ${response.status} ${response.statusText}`);
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Data Processing Contract API response:', result);
      return result;
    } catch (error) {
      console.error('Error fetching data processing contract:', error);
      return null;
    }
  },

  // Get existing Lastschriftmandat
  getLastschriftmandat: async () => {
    try {
      const token = localStorage.getItem('token');
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        console.warn('No authentication token found, proceeding without auth header');
      }
      
      console.log(`Making API call to ${API_URL}/api/lastschriftmandat/`);
      console.log('Request headers:', { 
        ...headers, 
        Authorization: headers.Authorization ? 'Bearer [REDACTED]' : undefined 
      });
      
      const response = await fetch(`${API_URL}/api/lastschriftmandat/`, {
        method: 'GET',
        headers
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (!response.ok) {
        if (response.status === 404) {
          console.log('No existing Lastschriftmandat found');
          return null;
        }
        
        const errorText = await response.text().catch(() => 'Could not read error response');
        console.error(`API error: ${response.status} ${response.statusText}`);
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Lastschriftmandat API response:', result);
      return result;
    } catch (error) {
      console.error('Error fetching Lastschriftmandat:', error);
      return null;
    }
  },
  
  // Upload Lastschriftmandat
  uploadLastschriftmandat: async (data: {
    pdf_file: string;
    file_name: string;
    description?: string;
  }) => {
    try {
      const token = localStorage.getItem('token');
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        console.warn('No authentication token found, proceeding without auth header');
      }
      
      console.log(`Making API call to ${API_URL}/api/lastschriftmandat/upload`);
      console.log('Request headers:', { 
        ...headers, 
        Authorization: headers.Authorization ? 'Bearer [REDACTED]' : undefined 
      });
      console.log('Request body preview:', {
        pdf_file: `[PDF file string of length ${data.pdf_file.length}]`,
        file_name: data.file_name,
        description: data.description
      });
      
      const response = await fetch(`${API_URL}/api/lastschriftmandat/upload`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data)
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Could not read error response');
        console.error(`API error: ${response.status} ${response.statusText}`);
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Lastschriftmandat upload API response:', result);
      return result;
    } catch (error) {
      console.error('Error uploading Lastschriftmandat:', error);
      throw error;
    }
  },
  
  // Download Lastschriftmandat
  downloadLastschriftmandat: async () => {
    try {
      const token = localStorage.getItem('token');
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        console.warn('No authentication token found, proceeding without auth header');
      }
      
      console.log(`Making API call to ${API_URL}/api/lastschriftmandat/download`);
      console.log('Request headers:', { 
        ...headers, 
        Authorization: headers.Authorization ? 'Bearer [REDACTED]' : undefined 
      });
      
      const response = await fetch(`${API_URL}/api/lastschriftmandat/download`, {
        method: 'GET',
        headers
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Could not read error response');
        console.error(`API error: ${response.status} ${response.statusText}`);
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Lastschriftmandat download API response:', result);
      return result;
    } catch (error) {
      console.error('Error downloading Lastschriftmandat:', error);
      throw error;
    }
  },
  
  // Update Lastschriftmandat
  updateLastschriftmandat: async (data: {
    pdf_file: string;
    file_name: string;
    description?: string;
  }) => {
    try {
      const token = localStorage.getItem('token');
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        console.warn('No authentication token found, proceeding without auth header');
      }
      
      console.log(`Making API call to ${API_URL}/api/lastschriftmandat/update`);
      console.log('Request headers:', { 
        ...headers, 
        Authorization: headers.Authorization ? 'Bearer [REDACTED]' : undefined 
      });
      console.log('Request body preview:', {
        pdf_file: `[PDF file string of length ${data.pdf_file.length}]`,
        file_name: data.file_name,
        description: data.description
      });
      
      const response = await fetch(`${API_URL}/api/lastschriftmandat/update`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(data)
      });
      
      console.log('Response status:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Could not read error response');
        console.error(`API error: ${response.status} ${response.statusText}`);
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Lastschriftmandat update API response:', result);
      return result;
    } catch (error) {
      console.error('Error updating Lastschriftmandat:', error);
      throw error;
    }
  }
};

interface ContractStepProps {
  formData: OnboardingFormData;
  onFormChange: (data: Partial<OnboardingFormData>) => void;
  onNext: () => void;
  onBack: () => void;
}

const ContractStep: React.FC<ContractStepProps> = ({ formData, onFormChange, onNext, onBack }) => {
  const [error, setError] = useState<string | null>(null);
  const [hasScrolledToBottom, setHasScrolledToBottom] = useState<boolean>(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState<string>('');
  const [mandateReference, setMandateReference] = useState<string>('10001');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const signatureRef = useRef<SignatureCanvas>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const contractTextRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const theme = useTheme();
  
  // Verwende formData.currentSignatureStep für die Navigation zwischen den Unterschriftsschritten
  const currentStep = formData.currentSignatureStep || 0;
  // State to track if Lastschriftmandat already exists
  const [mandateExists, setMandateExists] = useState<boolean>(false);

  // Definiere die Titel und Beschreibungen für die verschiedenen Vertragsschritte
  const contractSteps = [
    { 
      title: "Hauptvertrag", 
      description: "Bitte lesen Sie den Hauptvertrag sorgfältig durch und unterzeichnen Sie ihn.", 
      icon: <Description />,
      signatureField: "signature"
    },
    { 
      title: "Auftragsverarbeitung", 
      description: "Bitte bestätigen Sie die Vereinbarung zur Auftragsverarbeitung gemäß DSGVO.", 
      icon: <Article />,
      signatureField: "dataProcessingSignature"
    },
    { 
      title: "Lastschriftmandat", 
      description: "Bitte bestätigen Sie das SEPA-Lastschriftmandat für die monatlichen Zahlungen.", 
      icon: <Payment />,
      signatureField: "directDebitSignature"
    }
  ];

  // Check for existing contract on component mount
  useEffect(() => {
    const fetchExistingContracts = async () => {
      try {
        // Fetch main contract
        const contractData = await inlineContractService.getContract();
        
        // If we found an existing contract with a signature, use it
        if (contractData && contractData.signature_image) {
          console.log('Found existing contract with signature, loading it');
          
          // Only update the signature field, not the contract text
          onFormChange({ signature: contractData.signature_image });
          
          // Set accepted terms to true since they already signed
          onFormChange({ hasAcceptedTerms: true });
          setHasScrolledToBottom(true);
        } else {
          console.log('No existing main contract found or no signature present');
        }
        
        // Fetch data processing contract (Auftragsverarbeitung)
        const dataProcessingContract = await inlineContractService.getDataProcessingContract();
        
        // If we found an existing data processing contract with a signature, use it
        if (dataProcessingContract && dataProcessingContract.signature_image) {
          console.log('Found existing data processing contract with signature, loading it');
          
          // Update the data processing signature field
          onFormChange({ dataProcessingSignature: dataProcessingContract.signature_image });
        } else {
          console.log('No existing data processing contract found or no signature present');
        }
        
        // Fetch SEPA-Lastschriftmandat
        const lastschriftmandat = await inlineContractService.getLastschriftmandat();
        
        // If we found an existing SEPA-Lastschriftmandat, update the UI
        if (lastschriftmandat && lastschriftmandat.file_name) {
          console.log('Found existing Lastschriftmandat, loading it');
          
          // Mark that mandate exists for future upload operations
          setMandateExists(true);
          
          // Create a dummy File object for the UI
          setUploadedFileName(lastschriftmandat.file_name);
          
          // Store the direct debit signature (which could be the PDF file or ID reference)
          onFormChange({ directDebitSignature: 'existing-file' });
        } else {
          console.log('No existing Lastschriftmandat found');
          // Make sure mandate doesn't exist
          setMandateExists(false);
        }
      } catch (error) {
        console.error('Error loading existing contracts:', error);
        // Don't show error to user, just log it
      }
    };
    
    fetchExistingContracts();
  }, []);

  // Lade die gespeicherte Mandatsreferenz beim Initialisieren
  useEffect(() => {
    const savedReference = localStorage.getItem('mandateReference');
    if (savedReference) {
      setMandateReference(savedReference);
    }
  }, []);

  // Aktualisiere Canvas-Größe bei Änderungen der Fenstergröße
  useEffect(() => {
    const resizeCanvas = () => {
      if (signatureRef.current && containerRef.current) {
        const canvas = signatureRef.current as any;
        const ratio = Math.max(window.devicePixelRatio || 1, 1);
        canvas.clear();
        canvas._canvas.width = containerRef.current.offsetWidth * ratio;
        canvas._canvas.height = 200 * ratio;
        canvas._canvas.getContext("2d").scale(ratio, ratio);
        
        // If there's an existing signature in formData, render it in the canvas
        const signatureField = contractSteps[currentStep].signatureField;
        const signatureValue = 
          signatureField === 'signature' ? formData.signature :
          signatureField === 'dataProcessingSignature' ? formData.dataProcessingSignature :
          signatureField === 'directDebitSignature' ? formData.directDebitSignature :
          null;
          
        if (signatureValue) {
          // Small delay to ensure canvas is ready
          setTimeout(() => {
            if (signatureRef.current && signatureValue) {
              const img = new Image();
              img.onload = () => {
                // Additional null check to make TypeScript happy
                if (signatureRef.current && signatureValue) {
                  signatureRef.current.fromDataURL(signatureValue);
                }
              };
              img.src = signatureValue;
            }
          }, 200);
        }
      }
    };

    window.addEventListener("resize", resizeCanvas);
    // Initial setzen
    setTimeout(resizeCanvas, 100);

    return () => window.removeEventListener("resize", resizeCanvas);
  }, [currentStep, formData]);

  // When changing steps, render the signature if available
  useEffect(() => {
    if (signatureRef.current) {
      const signatureField = contractSteps[currentStep].signatureField;
      let signatureValue: string | null = null;
      
      if (signatureField === 'signature') {
        signatureValue = formData.signature;
      } else if (signatureField === 'dataProcessingSignature') {
        signatureValue = formData.dataProcessingSignature;
      } else if (signatureField === 'directDebitSignature') {
        signatureValue = formData.directDebitSignature;
      }
      
      if (signatureValue) {
        // Display existing signature from formData
        const img = new Image();
        img.onload = () => {
          if (signatureRef.current && signatureValue) {
            signatureRef.current.fromDataURL(signatureValue);
          }
        };
        img.src = signatureValue;
      } else {
        // Clear the canvas if no signature exists
        signatureRef.current.clear();
      }
    }
  }, [currentStep, formData]);

  // Überwache den Scroll-Status des Vertragstextes
  const handleScroll = () => {
    const element = contractTextRef.current;
    if (element) {
      // Überprüfe, ob der Text bis zum Ende gescrollt wurde
      const isAtBottom = Math.abs(
        (element.scrollHeight - element.scrollTop) - element.clientHeight
      ) < 2;

      if (isAtBottom && !hasScrolledToBottom) {
        setHasScrolledToBottom(true);
      }
    }
  };

  const handleAcceptTermsChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (hasScrolledToBottom || formData.hasAcceptedTerms) {
      onFormChange({ hasAcceptedTerms: event.target.checked });
    }
  };

  const clearSignature = () => {
    if (signatureRef.current) {
      signatureRef.current.clear();
      
      // Setze die entsprechende Signatur basierend auf dem aktuellen Schritt zurück
      const signatureField = contractSteps[currentStep].signatureField;
      onFormChange({ [signatureField]: null });
    }
  };

  // Helper function to get the complete contract text
  const getFullContractText = () => {
    // Get the complete contract text based on the current step
    if (currentStep === 0) {
      return getMainContractText(
        formData.companyName, 
        formData.street, 
        formData.zipCode || '[PLZ]', 
        formData.city || '[Ort]',
        formData.contactPerson
      );
    } else if (currentStep === 1) {
      return getDataProcessingContractText(
        formData.companyName,
        formData.street,
        formData.zipCode,
        formData.city,
        formData.country,
        formData.contactPerson
      );
    } else if (currentStep === 2) {
      return `SEPA-Lastschriftmandat für ${formData.companyName || '[Unternehmensname]'}
Mandatsreferenz: ${mandateReference}

Ich ermächtige EcomTask UG, Zahlungen von meinem Konto mittels Lastschrift einzuziehen. Zugleich weise ich mein Kreditinstitut an, die von EcomTask UG auf mein Konto gezogenen Lastschriften einzulösen.

Hinweis: Ich kann innerhalb von acht Wochen, beginnend mit dem Belastungsdatum, die Erstattung des belasteten Betrages verlangen. Es gelten dabei die mit meinem Kreditinstitut vereinbarten Bedingungen.`;
    }
    
    // Fallback text if no specific text is available
    return `Vertrag zwischen EcomTask UG und ${formData.companyName || '[Unternehmensname]'}`;
  };

  // Update save signature function
  const saveSignature = async () => {
    if (signatureRef.current) {
      if (signatureRef.current.isEmpty()) {
        setError('Bitte unterzeichnen Sie das Dokument');
        return;
      }
      
      const signatureData = signatureRef.current.toDataURL('image/png');
      
      // Speichere die Signatur im entsprechenden Feld basierend auf dem aktuellen Schritt
      const signatureField = contractSteps[currentStep].signatureField;
      onFormChange({ [signatureField]: signatureData });
      
      console.log(`Signature saved for step ${currentStep}, field: ${signatureField}`);
      
      // Get full contract text
      const fullContractText = getFullContractText();
      
      // If this is the main contract signature, immediately send it to the API
      if (currentStep === 0 && signatureField === "signature") {
        try {
          console.log("Sending main contract to API immediately after signature save");
          
          // Check if there's an existing contract to determine whether to use create or update endpoint
          const existingContract = await inlineContractService.getContract();
          
          if (existingContract && existingContract.id) {
            console.log("Existing contract found, using update endpoint");
            await inlineContractService.updateMainContract({
              contract_text: fullContractText,
              signature_image: signatureData
            });
            console.log("Contract successfully updated via API from save signature function");
          } else {
            console.log("No existing contract found, using create endpoint");
            await inlineContractService.createContract({
              contract_text: fullContractText,
              signature_image: signatureData
            });
            console.log("Contract successfully created via API from save signature function");
          }
        } catch (error) {
          console.error("Error sending contract from save signature function:", error);
          // Don't show error to user here, just log it
        }
      }
      // If this is the data processing contract signature, immediately send it to the API
      else if (currentStep === 1 && signatureField === "dataProcessingSignature") {
        try {
          console.log("Sending data processing contract to API immediately after signature save");
          
          // Check if there's an existing data processing contract
          const existingContract = await inlineContractService.getDataProcessingContract();
          
          if (existingContract && existingContract.id) {
            console.log("Existing data processing contract found, using update endpoint");
            await inlineContractService.updateAuftragsverarbeitung({
              contract_text: fullContractText,
              signature_image: signatureData
            });
            console.log("Data processing contract successfully updated via API");
          } else {
            console.log("No existing data processing contract found, using create endpoint");
            await inlineContractService.createDataProcessingContract({
              contract_text: fullContractText,
              signature_image: signatureData
            });
            console.log("Data processing contract successfully created via API");
          }
        } catch (error) {
          console.error("Error sending data processing contract from save signature function:", error);
          // Don't show error to user here, just log it
        }
      }
      
      setError(null);
    }
  };

  const handleStepChange = (step: number) => {
    // Wechsle zu einem anderen Signaturschritt
    onFormChange({ currentSignatureStep: step });
    setHasScrolledToBottom(false);
    setError(null);
    
    // Lösche die Signatur, wenn der Canvas gewechselt wird
    if (signatureRef.current) {
      signatureRef.current.clear();
    }
  };

  const handleNextStep = async () => {
    // Validiere den aktuellen Schritt
    if (currentStep === 0 && !formData.signature) {
      setError('Bitte unterzeichnen Sie den Hauptvertrag');
      return;
    } else if (currentStep === 1 && !formData.dataProcessingSignature) {
      setError('Bitte unterzeichnen Sie die Auftragsverarbeitung');
      return;
    } else if (currentStep === 2 && !formData.directDebitSignature && !uploadedFileName) {
      setError('Bitte laden Sie ein unterschriebenes SEPA-Lastschriftmandat hoch');
      return;
    }
    
    console.log('handleNextStep called, currentStep:', currentStep);
    console.log('Signature status:', {
      mainSignature: !!formData.signature,
      dataProcessingSignature: !!formData.dataProcessingSignature,
      directDebitSignature: !!formData.directDebitSignature
    });
    
    if (currentStep < 2) {
      // Gehe zum nächsten Unterschrittsschritt
      onFormChange({ currentSignatureStep: currentStep + 1 });
      setHasScrolledToBottom(false);
      setError(null);
    } else {
      // If we're on the last step, just proceed to the next main step without API calls
      console.log('Moving to next main step without API calls');
      onNext();
    }
  };

  const handlePrevStep = () => {
    if (currentStep > 0) {
      // Gehe zum vorherigen Unterschrittsschritt
      onFormChange({ currentSignatureStep: currentStep - 1 });
      setHasScrolledToBottom(false);
      setError(null);
    } else {
      // Gehe zum vorherigen Hauptschritt
      onBack();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('Submit button clicked in ContractStep, currentStep:', currentStep);
    
    // Überprüfe, ob alle erforderlichen Unterschriften vorhanden sind
    if (currentStep === 0 && !formData.hasAcceptedTerms) {
      setError('Bitte akzeptieren Sie die Vertragsbedingungen');
      return;
    }
    
    if (currentStep === 0 && !formData.signature) {
      setError('Bitte unterzeichnen Sie den Hauptvertrag');
      return;
    } else if (currentStep === 1 && !formData.dataProcessingSignature) {
      setError('Bitte unterzeichnen Sie die Auftragsverarbeitung');
      return;
    } else if (currentStep === 2 && !formData.directDebitSignature && !uploadedFileName) {
      setError('Bitte laden Sie ein unterschriebenes SEPA-Lastschriftmandat hoch');
      return;
    }
    
    console.log('All validations passed, proceeding to next step');
    
    // Navigiere je nach aktuellem Schritt weiter
    handleNextStep();
  };

  const triggerFileInput = () => {
    // Simply trigger the file input click
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      
      // Prüfe, ob es eine PDF-Datei ist
      if (file.type !== 'application/pdf') {
        setError('Bitte laden Sie eine PDF-Datei hoch');
        return;
      }
      
      // Prüfe die Dateigröße (max. 5 MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Die Datei ist zu groß. Maximale Größe: 5 MB');
        return;
      }
      
      setUploadedFile(file);
      setUploadedFileName(file.name);
      
      // Speichere die Datei als Base64-String
      const reader = new FileReader();
      reader.onload = async (e) => {
        const result = e.target?.result as string;
        
        // Check if this is an update based on if a mandate already exists
        const isUpdate = mandateExists;
        
        try {
          setError(null); // Clear previous errors
          
          // Prepare request data
          const requestData = {
            pdf_file: result,
            file_name: file.name,
            description: `SEPA-Lastschriftmandat für ${formData.companyName || 'Kunde'}`
          };
          
          let response;
          
          if (isUpdate) {
            // Use update endpoint for existing files
            console.log('Updating existing Lastschriftmandat');
            response = await inlineContractService.updateLastschriftmandat(requestData);
          } else {
            // Use upload endpoint for new files
            console.log('Uploading new Lastschriftmandat');
            response = await inlineContractService.uploadLastschriftmandat(requestData);
          }
          
          console.log('Successfully processed Lastschriftmandat:', response);
          
          // Set a marker in formData to indicate a file has been uploaded
          onFormChange({ directDebitSignature: 'file-uploaded' });
          
          // After a successful upload/update, set mandateExists to true for future operations
          setMandateExists(true);
          
          // Update UI to show success
          setError(null);
        } catch (error) {
          console.error(`Error ${isUpdate ? 'updating' : 'uploading'} Lastschriftmandat:`, error);
          setError(`Fehler beim ${isUpdate ? 'Aktualisieren' : 'Hochladen'} des Lastschriftmandats. Bitte versuchen Sie es erneut.`);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDownloadSepaMandat = async () => {
    // Setze den Download-Button auf "Wird geladen..."
    setIsLoading(true);
    
    try {
      // Use the /api/download/pdf endpoint directly as requested
      const response = await fetch(`${API_URL}/api/download/pdf`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        },
      });
      
      if (!response.ok) {
        throw new Error(`PDF konnte nicht geladen werden: ${response.status} ${response.statusText}`);
      }
      
      // Parse die JSON-Antwort vom Server
      const data = await response.json();
      
      if (!data.filename || !data.file_content) {
        throw new Error('Die Serverantwort enthält nicht die erwarteten Daten');
      }
      
      // Extrahiere die Referenznummer aus dem Dateinamen (z.B. "SEPA-Lastschriftmandat_10035.pdf")
      const filenameMatch = data.filename.match(/(\d+)\.pdf$/);
      if (filenameMatch && filenameMatch[1]) {
        const fileReferenceNumber = filenameMatch[1];
        // Speichere die vom Server gelieferte Referenznummer im localStorage
        localStorage.setItem('mandateReference', fileReferenceNumber);
        // Aktualisiere den State mit der vom Server gelieferten Referenz
        setMandateReference(fileReferenceNumber);
      }
      
      // Decode den Base64-codierten Inhalt zu einem Blob
      const binaryString = atob(data.file_content);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Erstelle einen Blob aus den Binärdaten mit dem korrekten Content-Type
      const contentType = data.content_type || 'application/pdf';
      const blob = new Blob([bytes], { type: contentType });
      
      // Erstelle eine URL für den Blob und trigger den Download
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Verwende den vom Server gelieferten Dateinamen
      link.setAttribute('download', data.filename);
      
      // Verzögerung für bessere Browser-Kompatibilität
      setTimeout(() => {
        document.body.appendChild(link);
        link.click();
        
        // Bereinige nach einer kurzen Verzögerung
        setTimeout(() => {
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        }, 200);
      }, 100);
      
      console.log(`${data.filename} Download initiiert`);
      setError(null); // Lösche etwaige Fehlermeldungen bei Erfolg
    } catch (error) {
      console.error('Fehler beim Herunterladen des PDFs:', error);
      setError('Der Download ist fehlgeschlagen. Bitte versuchen Sie es erneut oder kontaktieren Sie den Support.');
    } finally {
      // Button-Status zurücksetzen
      setIsLoading(false);
    }
  };

  // Bestimme, ob der aktuelle Schritt eine gültige Signatur hat
  const hasCurrentSignature = () => {
    switch (currentStep) {
      case 0: return !!formData.signature;
      case 1: return !!formData.dataProcessingSignature;
      case 2: return !!formData.directDebitSignature || !!uploadedFileName;
      default: return false;
    }
  };

  // Update Weiter button click handler to remove API call
  const handleWeiterClick = async () => {
    console.log("Weiter button clicked directly");
    
    // Just continue with normal form submission without API call
    const fakeEvent = { preventDefault: () => {} } as React.FormEvent;
    handleSubmit(fakeEvent);
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: { xs: 2, sm: 3 }, pb: { xs: 6, sm: 8 } }}>
      {/* Dokumentenauswahl für die drei Vertragsschritte */}
      <Box sx={{ 
        mb: 4, 
        display: { xs: 'none', sm: 'flex' },
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        position: 'relative',
        width: '100%',
        maxWidth: '800px',
        mx: 'auto',
        px: 4
      }}>
        {contractSteps.map((step, index) => (
          <Box 
            key={index} 
            onClick={() => handleStepChange(index)}
            sx={{ 
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              cursor: 'pointer',
              p: 1.5,
              borderRadius: 2,
              backgroundColor: currentStep === index ? 'rgba(25, 103, 210, 0.1)' : '#FFFFFF',
              border: currentStep === index ? '1px solid rgba(25, 103, 210, 0.3)' : '1px solid transparent',
              '&:hover': {
                backgroundColor: 'rgba(25, 103, 210, 0.05)'
              },
              transition: 'all 0.2s ease-in-out',
              width: '180px',
              textAlign: 'center',
              position: 'relative',
              zIndex: 1
            }}
          >
            <Box sx={{ 
              width: 40, 
              height: 40, 
              borderRadius: '50%', 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: currentStep === index ? '#1967D2' : 'rgba(0, 0, 0, 0.1)',
              color: currentStep === index ? '#FFFFFF' : '#666666',
              mb: 1,
              mx: 'auto'
            }}>
              {React.cloneElement(step.icon, { fontSize: 'small' })}
            </Box>
            <Typography 
              variant="body2"
              align="center"
              sx={{ 
                color: currentStep === index ? '#1967D2' : '#333333',
                fontWeight: currentStep === index ? 'medium' : 'normal',
                fontSize: '0.85rem',
                lineHeight: 1.2
              }}
            >
              {step.title}
            </Typography>
            {/* Statusindikator */}
            <Box 
              sx={{ 
                width: 8, 
                height: 8, 
                borderRadius: '50%', 
                mt: 1,
                backgroundColor: (
                  (index === 0 && !!formData.signature) || 
                  (index === 1 && !!formData.dataProcessingSignature) || 
                  (index === 2 && (!!formData.directDebitSignature || !!uploadedFileName))
                ) ? '#4CAF50' : 'transparent'
              }}
            />
          </Box>
        ))}
      </Box>

      {/* Mobile Schritt-Anzeige */}
      <Box sx={{ 
        display: { xs: 'block', sm: 'none' },
        mb: 2,
        textAlign: 'center'
      }}>
        <Typography variant="body2" sx={{ color: '#666666', mb: 0.5 }}>
          Schritt {currentStep + 1} von 3
        </Typography>
        <Typography variant="h6" sx={{ color: '#1967D2', fontWeight: 'medium' }}>
          {contractSteps[currentStep].title}
        </Typography>
      </Box>

      <Box
        sx={{
          p: { xs: 2, sm: 3, md: 4 },
          mb: { xs: 2, sm: 4 },
          borderRadius: 2,
          backgroundColor: '#FFFFFF',
        }}
      >
        <Typography 
          variant="h6" 
          gutterBottom
          sx={{ 
            display: { xs: 'none', sm: 'flex' },
            alignItems: 'center',
            color: '#333333',
            fontWeight: 'medium'
          }}
        >
          {contractSteps[currentStep].icon}
          <Box component="span" sx={{ ml: 1 }}>{contractSteps[currentStep].title}</Box>
        </Typography>
        
        <Typography variant="body2" sx={{ mb: 3, ml: 0.5, color: '#333333' }}>
          {contractSteps[currentStep].description}
        </Typography>
        
        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3, 
              borderRadius: 2,
              backgroundColor: 'rgba(211, 47, 47, 0.15)', 
              color: '#ff6b6b',
              '& .MuiAlert-icon': {
                color: '#ff6b6b'
              }
            }}
          >
            {error}
          </Alert>
        )}
        
        {/* Vertragstext basierend auf dem aktuellen Schritt */}
        {currentStep === 0 && (
          <ContractViewer
            contractType="main"
            title="Hauptvertrag"
            description="Vertrag über die Nutzung des WhatsApp Termin Assistenten"
            sections={getMainContractSections({
              companyName: formData.companyName,
              street: formData.street,
              zipCode: formData.zipCode || '[PLZ]',
              city: formData.city || '[Ort]',
              country: formData.country,
              contactPerson: formData.contactPerson,
              email: formData.email,
              phone: formData.phone
            })}
            onScrollComplete={() => setHasScrolledToBottom(true)}
            showDownload={true}
            onDownload={async () => {
              try {
                // Download der statischen SaaS.pdf
                const link = document.createElement('a');
                link.href = '/contracts/SaaS.pdf';
                link.download = `Hauptvertrag_${formData.companyName || 'TimeGlobe'}.pdf`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              } catch (error) {
                console.error('Error downloading contract PDF:', error);
                setError('Fehler beim PDF-Download');
              }
            }}
          />
        )}
        
        {currentStep === 1 && (
          <ContractViewer
            contractType="dataProcessing"
            title="Auftragsverarbeitungsvertrag"
            description="Vereinbarung zur Verarbeitung personenbezogener Daten gemäß Art. 28 DSGVO"
            sections={getDataProcessingContractSections({
              companyName: formData.companyName,
              street: formData.street,
              zipCode: formData.zipCode || '[PLZ]',
              city: formData.city || '[Ort]',
              country: formData.country,
              contactPerson: formData.contactPerson,
              email: formData.email,
              phone: formData.phone
            })}
            onScrollComplete={() => setHasScrolledToBottom(true)}
            showDownload={true}
            onDownload={async () => {
              try {
                // Download der statischen AVV.pdf
                const link = document.createElement('a');
                link.href = '/contracts/AVV.pdf';
                link.download = `Auftragsverarbeitungsvertrag_${formData.companyName || 'TimeGlobe'}.pdf`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              } catch (error) {
                console.error('Error downloading contract PDF:', error);
                setError('Fehler beim PDF-Download');
              }
            }}
          />
        )}
        
        {currentStep === 2 && (
          <Box sx={{ 
            p: 3, 
            backgroundColor: 'rgba(25, 103, 210, 0.03)', 
            borderRadius: 2,
            border: '1px solid rgba(25, 103, 210, 0.2)'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Euro sx={{ fontSize: 28, color: 'rgba(0, 0, 0, 0.87)', mr: 2 }} />
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  SEPA-Lastschriftmandat
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Ermächtigung zum Lastschrifteinzug für {formData.companyName || '[Unternehmensname]'}
                </Typography>
              </Box>
            </Box>
            
            <Typography variant="body1" sx={{ mb: 3, color: '#333' }}>
              Für die monatliche Abrechnung benötigen wir ein unterschriebenes SEPA-Lastschriftmandat.
            </Typography>
            
            <Box sx={{ 
              backgroundColor: 'white', 
              p: 2, 
              borderRadius: 1,
              border: '1px solid rgba(0, 0, 0, 0.1)'
            }}>
              <Typography variant="body2" sx={{ mb: 2 }}>
                <strong>So funktioniert's:</strong>
              </Typography>
              <Box sx={{ pl: 2 }}>
                <Typography variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'flex-start' }}>
                  <span style={{ marginRight: 8 }}>1.</span>
                  Laden Sie das vorausgefüllte SEPA-Lastschriftmandat herunter
                </Typography>
                <Typography variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'flex-start' }}>
                  <span style={{ marginRight: 8 }}>2.</span>
                  Füllen Sie Ihre Bankverbindung aus und unterschreiben Sie das Dokument
                </Typography>
                <Typography variant="body2" sx={{ display: 'flex', alignItems: 'flex-start' }}>
                  <span style={{ marginRight: 8 }}>3.</span>
                  Laden Sie das unterschriebene Dokument hier wieder hoch
                </Typography>
              </Box>
            </Box>
            
            {mandateReference && (
              <Box sx={{ mt: 2, p: 1.5, backgroundColor: 'rgba(25, 103, 210, 0.1)', borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  Ihre Mandatsreferenz: <strong>{mandateReference}</strong>
                </Typography>
              </Box>
            )}
          </Box>
        )}

        {currentStep === 0 && (
          <FormControlLabel
            control={
              <Checkbox 
                checked={formData.hasAcceptedTerms} 
                onChange={handleAcceptTermsChange} 
                color="primary"
                disabled={!hasScrolledToBottom}
                icon={<Box sx={{ 
                  width: 20, 
                  height: 20, 
                  border: '2px solid rgba(0, 0, 0, 0.3)', 
                  borderRadius: 1,
                  ...(hasScrolledToBottom ? {} : { opacity: 0.5 })
                }} />}
                checkedIcon={<Box sx={{ 
                  width: 20, 
                  height: 20, 
                  borderRadius: 1,
                  backgroundColor: '#1967D2',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <Check sx={{ color: '#fff', fontSize: 16 }} />
                </Box>}
              />
            }
            label={
              <Typography variant="body2" sx={{ color: '#666666' }}>
                {hasScrolledToBottom 
                  ? 'Ich akzeptiere die Vertragsbedingungen' 
                  : 'Bitte scrollen Sie den Vertrag vollständig durch, um die Bedingungen zu akzeptieren'}
              </Typography>
            }
            sx={{ mb: 3 }}
          />
        )}
        
        {/* Only show signature area for Hauptvertrag (0) and Auftragsverarbeitung (1) */}
        {(currentStep === 0 || currentStep === 1) && (
          <>
            <Typography variant="subtitle1" gutterBottom sx={{ 
              display: 'flex', 
              alignItems: 'center',
              mt: 4,
              color: '#333333',
            }}>
              <Edit sx={{ mr: 1, fontSize: 20, opacity: 0.9, color: '#1967D2' }} />
              Ihre Unterschrift:
            </Typography>
            
            <Box 
              ref={containerRef}
              sx={{ 
                border: '1px solid rgba(0, 0, 0, 0.2)', 
                borderRadius: 2, 
                mb: 2,
                backgroundColor: '#FFFFFF',
                position: 'relative',
                overflow: 'hidden',
                height: '200px',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  width: '100%',
                  height: '5px',
                  backgroundColor: '#1967D2',
                  opacity: 0.5
                }
              }}
            >
              <SignatureCanvas 
                ref={signatureRef}
                canvasProps={{ 
                  className: 'signature-canvas',
                  style: { 
                    width: '100%', 
                    height: '100%', 
                    cursor: 'crosshair'
                  }
                }}
                backgroundColor="rgba(0, 0, 0, 0)"
                penColor="#000000"
                velocityFilterWeight={0}
                dotSize={0.5}
                minWidth={0.5}
                maxWidth={1.5}
                throttle={0}
              />
            </Box>
            
            <Box sx={{ 
              display: 'flex', 
              mb: 1,
              flexDirection: { xs: 'column', sm: 'row' },
              gap: { xs: 1, sm: 0 }
            }}>
              <Button 
                onClick={clearSignature} 
                variant="outlined"
                startIcon={<Delete sx={{ fontSize: { xs: '1.1rem', sm: '1.2rem' } }} />}
                sx={{ 
                  mr: { xs: 0, sm: 2 },
                  borderRadius: 2,
                  borderColor: 'rgba(0, 0, 0, 0.2)',
                  color: '#666666',
                  py: { xs: 1.2, sm: 1 },
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  width: { xs: '100%', sm: 'auto' },
                  '&:hover': {
                    borderColor: '#f44336',
                    backgroundColor: 'rgba(244, 67, 54, 0.08)'
                  }
                }}
              >
                Löschen
              </Button>
              <Button 
                onClick={saveSignature} 
                variant="contained"
                startIcon={<Check sx={{ fontSize: { xs: '1.1rem', sm: '1.2rem' } }} />}
                sx={{ 
                  borderRadius: 2,
                  backgroundColor: '#1967D2', 
                  color: 'white',
                  py: { xs: 1.2, sm: 1 },
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  width: { xs: '100%', sm: 'auto' },
                  '&:hover': {
                    backgroundColor: '#1756B0',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
                  }
                }}
              >
                Speichern und senden
              </Button>
            </Box>
          </>
        )}
        
        {/* Show Lastschriftmandat upload and download buttons only for tab 2 */}
        {currentStep === 2 && (
          <Box sx={{ mt: 3 }}>
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              accept="application/pdf"
              onChange={handleFileUpload}
            />
            
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              gap: 2,
              alignItems: 'flex-start'
            }}>
              <Box sx={{ 
                width: '100%', 
                display: 'flex', 
                gap: { xs: 1, sm: 2 }, 
                alignItems: 'center',
                flexDirection: { xs: 'column', sm: 'row' }
              }}>
                <Button
                  variant="contained"
                  startIcon={<Download sx={{ fontSize: { xs: '1.1rem', sm: '1.2rem' } }} />}
                  onClick={handleDownloadSepaMandat}
                  disabled={isLoading}
                  sx={{ 
                    borderRadius: 2,
                    backgroundColor: '#1967D2',
                    color: 'white',
                    px: { xs: 2, sm: 3 },
                    py: { xs: 1, sm: 1.2 },
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    width: { xs: '100%', sm: 'auto' },
                    '&:hover': {
                      backgroundColor: '#1756B0',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                    }
                  }}
                >
                  {isLoading ? 'Wird geladen...' : 'SEPA-Lastschriftmandat herunterladen'}
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<Upload sx={{ fontSize: { xs: '1.1rem', sm: '1.2rem' } }} />}
                  onClick={triggerFileInput}
                  sx={{ 
                    borderRadius: 2,
                    borderColor: '#1967D2',
                    color: '#1967D2',
                    px: { xs: 2, sm: 3 },
                    py: { xs: 1, sm: 1.2 },
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    width: { xs: '100%', sm: 'auto' },
                    '&:hover': {
                      borderColor: '#1967D2',
                      backgroundColor: 'rgba(25, 103, 210, 0.05)'
                    }
                  }}
                >
                  {mandateExists ? 'Mandat aktualisieren' : 'Unterschriebenes Mandat hochladen'}
                </Button>
              </Box>
              
              {uploadedFileName && (
                <Box sx={{ 
                  backgroundColor: 'rgba(25, 103, 210, 0.1)',
                  borderRadius: 2,
                  p: { xs: 2, sm: 1.5 },
                  width: '100%',
                  my: 1
                }}>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    mb: { xs: 1, sm: 0 }
                  }}>
                    <Description sx={{ color: '#1967D2', mr: 1 }} />
                    <Typography variant="body2" sx={{ 
                      color: '#333333', 
                      flexGrow: 1,
                      fontSize: { xs: '0.8rem', sm: '0.875rem' }
                    }}>
                      {uploadedFileName}
                    </Typography>
                  </Box>
                  <Box sx={{ 
                    display: 'flex',
                    flexDirection: { xs: 'column', sm: 'row' },
                    gap: { xs: 1, sm: 1 },
                    mt: { xs: 1, sm: 0 },
                    ml: { xs: 0, sm: 'auto' },
                    width: { xs: '100%', sm: 'auto' }
                  }}>
                    <Button
                      size="small"
                      sx={{ 
                        color: '#1967D2', 
                        minWidth: { xs: 'auto', sm: 0 },
                        fontSize: { xs: '0.75rem', sm: '0.875rem' },
                        py: { xs: 0.8, sm: 0.5 },
                        width: { xs: '100%', sm: 'auto' }
                      }}
                      onClick={async () => {
                      try {
                        // Use the /api/lastschriftmandat/download endpoint as requested
                        const token = localStorage.getItem('token');
                        
                        const headers: Record<string, string> = {
                          'Accept': '*/*'  // Accept any content type
                        };
                        
                        if (token) {
                          headers['Authorization'] = `Bearer ${token}`;
                        }
                        
                        console.log(`Making API call to ${API_URL}/api/lastschriftmandat/download`);
                        
                        const response = await fetch(`${API_URL}/api/lastschriftmandat/download`, {
                          method: 'GET',
                          headers
                        });
                        
                        if (!response.ok) {
                          throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        
                        // Check content type to determine how to handle the response
                        const contentType = response.headers.get('content-type');
                        console.log('Response content type:', contentType);
                        
                        // Handle different response formats
                        if (contentType && contentType.includes('application/json')) {
                          // Handle JSON response (if API returns JSON with PDF in base64)
                          const result = await response.json();
                          
                          if (result.pdf_file) {
                            // Handle base64 PDF from API response
                            const base64Data = result.pdf_file;
                            // Remove the data URL prefix if present
                            const base64Content = base64Data.includes('base64,') 
                              ? base64Data.split('base64,')[1] 
                              : base64Data;
                            
                            // Convert base64 to binary
                            const binaryString = atob(base64Content);
                            const len = binaryString.length;
                            const bytes = new Uint8Array(len);
                            for (let i = 0; i < len; i++) {
                              bytes[i] = binaryString.charCodeAt(i);
                            }
                            
                            // Create a blob with the PDF data
                            const blob = new Blob([bytes], { type: 'application/pdf' });
                            const url = URL.createObjectURL(blob);
                            
                            // Open PDF in new tab
                            window.open(url, '_blank');
                            
                            // Cleanup URL after a delay
                            setTimeout(() => {
                              URL.revokeObjectURL(url);
                            }, 1000);
                          } else {
                            throw new Error('Response does not contain PDF data');
                          }
                        } else {
                          // Handle direct binary response (PDF file)
                          const blob = await response.blob();
                          const url = URL.createObjectURL(blob);
                          
                          // Open PDF in new tab
                          window.open(url, '_blank');
                          
                          // Cleanup URL after a delay
                          setTimeout(() => {
                            URL.revokeObjectURL(url);
                          }, 1000);
                        }
                        
                        console.log('Viewed Lastschriftmandat from API');
                        setError(null);
                      } catch (error) {
                        console.error('Error viewing file:', error);
                        setError('Fehler beim Anzeigen der Datei.');
                      }
                    }}
                  >
                    Anzeigen
                  </Button>
                    <Button
                      size="small"
                      sx={{ 
                        color: '#1967D2', 
                        minWidth: { xs: 'auto', sm: 0 },
                        fontSize: { xs: '0.75rem', sm: '0.875rem' },
                        py: { xs: 0.8, sm: 0.5 },
                        width: { xs: '100%', sm: 'auto' }
                      }}
                      onClick={triggerFileInput}
                    >
                      Aktualisieren
                    </Button>
                  </Box>
                </Box>
              )}
              
              <Typography variant="body2" sx={{ color: '#666666', display: 'flex', alignItems: 'center' }}>
                <InfoOutlined sx={{ fontSize: '1rem', mr: 0.5, color: '#999999' }} />
                Bitte unterschreiben Sie das Dokument und laden Sie es wieder hoch
              </Typography>
            </Box>
          </Box>
        )}
      </Box>
      
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        mt: { xs: 2, sm: 3 },
        flexDirection: { xs: 'column', sm: 'row' },
        gap: { xs: 1, sm: 0 }
      }}>
        <Button 
          onClick={handlePrevStep}
          variant="outlined"
          startIcon={<ArrowBack sx={{ fontSize: { xs: '1.1rem', sm: '1.2rem' } }} />}
          sx={{ 
            borderRadius: 3,
            borderColor: '#1967D2',
            px: { xs: 2, sm: 3 },
            py: { xs: 1, sm: 1.2 },
            fontSize: { xs: '0.875rem', sm: '1rem' },
            color: '#1967D2',
            width: { xs: '100%', sm: 'auto' },
            order: { xs: 2, sm: 1 },
            '&:hover': {
              borderColor: '#1967D2',
              backgroundColor: 'rgba(25, 103, 210, 0.05)'
            }
          }}
        >
          {currentStep === 0 ? 'Zurück' : 'Vorherige'}
        </Button>
        <Button
          onClick={handleWeiterClick}
          variant="contained"
          color="primary"
          disabled={
            (currentStep === 0 && (!formData.hasAcceptedTerms || !formData.signature)) || 
            (currentStep === 1 && !formData.dataProcessingSignature) ||
            (currentStep === 2 && !formData.directDebitSignature && !uploadedFileName)
          }
          endIcon={<ArrowForward sx={{ fontSize: { xs: '1.1rem', sm: '1.2rem' } }} />}
          sx={{ 
            px: { xs: 3, sm: 4 }, 
            py: { xs: 1.2, sm: 1.5 },
            fontSize: { xs: '0.875rem', sm: '1rem' },
            borderRadius: 3,
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
            backgroundColor: '#1967D2',
            width: { xs: '100%', sm: 'auto' },
            order: { xs: 1, sm: 2 },
            '&:hover': {
              boxShadow: '0 6px 20px rgba(0,0,0,0.3)',
              backgroundColor: '#1756B0',
            },
            '&.Mui-disabled': {
              backgroundColor: 'rgba(0, 0, 0, 0.12)',
              color: 'rgba(0, 0, 0, 0.3)'
            }
          }}
        >
          {currentStep < 2 ? 'Weiter' : 'Abschließen'}
        </Button>
      </Box>
    </Box>
  );
};

// Footer als eigenständige Komponente außerhalb des Hauptinhalts
const Footer = () => (
  <Box 
    sx={{ 
      position: 'fixed',
      bottom: 0,
      left: 0,
      height: '20px',
      width: '100%',
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center',
      py: 0.5,
      backgroundColor: 'rgba(255, 255, 255, 0)',
      backdropFilter: 'blur(5px)',
      opacity: 1,
      zIndex: 10,
      borderTop: '1px solidrgba(224, 224, 224, 0)'
    }}
  >
    <Typography 
      variant="body2" 
      sx={{ 
        color: '#666666',
        mr: 1,
        fontSize: '0.75rem'
      }}
    >
      powered by
    </Typography>
    <img 
      src="/images/EcomTask_logo.svg" 
      alt="EcomTask Logo" 
      style={{ height: '30px' }} 
    />
  </Box>
);

// Die gesamte App-Komponente mit Hauptinhalt und Footer
const ContractStepWithFooter: React.FC<ContractStepProps> = (props) => {
  return (
    <>
      <ContractStep {...props} />
      <Footer />
    </>
  );
};

export default ContractStepWithFooter; 