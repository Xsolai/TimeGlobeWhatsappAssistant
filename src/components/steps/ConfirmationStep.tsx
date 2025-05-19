import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, Typography, Paper, List, ListItem, ListItemText, Divider, useTheme, 
  Snackbar, Alert, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import { OnboardingFormData } from '../../types';
import DoneAll from '@mui/icons-material/DoneAll';
import ArrowBack from '@mui/icons-material/ArrowBack';
import VpnKey from '@mui/icons-material/VpnKey';
import Business from '@mui/icons-material/Business';
import Person from '@mui/icons-material/Person';
import Email from '@mui/icons-material/Email';
import Phone from '@mui/icons-material/Phone';
import CheckCircle from '@mui/icons-material/CheckCircle';
import WhatsApp from '@mui/icons-material/WhatsApp';
import CheckCircleOutline from '@mui/icons-material/CheckCircleOutline';
import whatsappService from '../../services/whatsappService';

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
  
  // Update main contract
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
  }
};

interface ConfirmationStepProps {
  formData: OnboardingFormData;
  onBack: () => void;
}

const ConfirmationStep: React.FC<ConfirmationStepProps> = ({ formData, onBack }) => {
  const theme = useTheme();
  const [openSuccessDialog, setOpenSuccessDialog] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'connecting' | 'success' | 'error' | 'disconnected'>('idle');
  const [whatsappConnected, setWhatsappConnected] = useState(false);
  const [whatsappNumber, setWhatsappNumber] = useState('');
  const popupWindowRef = useRef<Window | null>(null);
  const popupCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // 360dialog onboarding URL configuration
  const PARTNER_ID = "MalHtRPA";
  const REDIRECT_URL = "https://timeglobe-server.ecomtask.de/redirect";
  const base_url = `https://hub.360dialog.com/dashboard/app/${PARTNER_ID}/permissions`;
  
  // Query parameters
  const query_params = new URLSearchParams({
    redirect_url: REDIRECT_URL,
    plan_selection: "regular"
  });
  
  // Final onboarding URL
  const onboarding_url = `${base_url}?${query_params.toString()}`;
  
  // Fetch WhatsApp status on component mount
  useEffect(() => {
    const fetchWhatsAppStatus = async () => {
      try {
        const statusResponse = await whatsappService.getStatus();
        console.log('WhatsApp status response:', statusResponse);
        
        if (statusResponse.status === 'connected') {
          setWhatsappConnected(true);
          setConnectionStatus('success');
          // Sicherere Überprüfung der WhatsApp-Nummer
          const whatsappNum = statusResponse.whatsapp_number;
          if (typeof whatsappNum === 'string' && whatsappNum.trim()) {
            setWhatsappNumber(whatsappNum);
          }
        } else {
          setWhatsappConnected(false);
          setConnectionStatus('disconnected');
        }
      } catch (error) {
        console.error('Error fetching WhatsApp status:', error);
        setWhatsappConnected(false);
        setConnectionStatus('error');
      }
    };
    
    fetchWhatsAppStatus();
  }, []);

  // Set up a listener for messages from the redirect page
  useEffect(() => {
    // Function to handle messages from the popup window
    const handleMessage = (event: MessageEvent) => {
      // Verify origin for security - replace with your actual domain
      if (event.origin !== "https://solasolution.ecomtask.de") return;
      
      // Check the message content
      if (event.data && event.data.type === 'whatsapp_connection') {
        if (event.data.status === 'success') {
          setConnectionStatus('success');
          setOpenSuccessDialog(true);
        } else if (event.data.status === 'error') {
          setConnectionStatus('error');
        }
      }
    };

    // Add event listener for messages
    window.addEventListener('message', handleMessage);
    
    // Expose test function to global window object for manual testing
    (window as any).testContractAPI = async () => {
      try {
        console.log('Testing contract API manually...');
        
        // Create sample contract text
        const sampleContractText = `Vertrag über die Bereitstellung des Add-ons "AI-Assistant" für den TimeGlobe-Kalender

zwischen

EcomTask UG
Rauenthaler Str. 12
65197 Wiesbaden
Deutschland
(im Folgenden "EcomTask")

und

TestXSOL
Teststraße 123
12345 Teststadt
Deutschland
(im Folgenden "Kunde")

(EcomTask und Kunde einzeln jeweils auch "Partei" und gemeinsam "Parteien")

1. Vertragsgegenstand
Gegenstand des Vertrags ist die entgeltliche und zeitlich auf die Dauer des Vertrags begrenzte Gewährung der Nutzung des Add-ons "AI-Assistent" für den TimeGlobe-Kalender (nachfolgend "Software") im Unternehmen des Kunden über das Internet.

2. Leistungen von EcomTask
EcomTask gewährt dem Kunden (bzw. dessen Kunden) die Nutzung der jeweils aktuellen Version der Software mittels Zugriff durch WhatsApp.

3. Nutzungsumfang und -rechte
Der Kunde erhält an der jeweils aktuellen Version der Software einfache, d. h. nicht unterlizenzierbare und nicht übertragbare, zeitlich auf die Dauer des Vertrags beschränkte Rechte zur Nutzung.

4. Vergütung
Die monatliche Vergütung beträgt EUR ____.

5. Vertragslaufzeit
Der Vertrag wird auf unbestimmte Zeit geschlossen und kann mit einer Frist von X Monaten gekündigt werden.`;

        const testData = {
          contract_text: sampleContractText,
          signature_image: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA" // Sample base64 data
        };
        
        console.log('Full contract text being sent in test:', sampleContractText);
        
        const response = await fetch(`${API_URL}/api/contract/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(testData)
        });
        
        console.log('Test API Response:', response.status, response.statusText);
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Error response:', errorText);
        } else {
          const result = await response.json();
          console.log('Success response:', result);
        }
      } catch (error) {
        console.error('Test API error:', error);
      }
    };
    
    console.log('Test function available. Call window.testContractAPI() in console to test API directly');
    
    // Clean up the event listener when component unmounts
    return () => {
      window.removeEventListener('message', handleMessage);
      // Also clear any active intervals
      if (popupCheckIntervalRef.current) {
        clearInterval(popupCheckIntervalRef.current);
      }
      // Remove test function
      delete (window as any).testContractAPI;
    };
  }, []);

  // Helper function to get the complete contract text
  const getFullContractText = () => {
    return `Vertrag über die Bereitstellung des Add-ons "AI-Assistant" für den TimeGlobe-Kalender

zwischen

EcomTask UG
vertreten durch Nick Wirth,
Rauenthaler Straße 12,
65197, Wiesbaden,
(im Folgenden "EcomTask")

und

${formData.companyName || '[Unternehmensname]'}
vertreten durch ${formData.contactPerson || '[Ansprechpartner]'},
${formData.street || '[Straße]'},
${formData.zipCode || '[PLZ]'}, ${formData.city || '[Stadt]'},
${formData.country || '[Land]'}
(im Folgenden "Kunde")

(EcomTask und Kunde einzeln jeweils auch "Partei" und gemeinsam "Parteien")

1. Vertragsgegenstand
Gegenstand des Vertrags ist die entgeltliche und zeitlich auf die Dauer des Vertrags begrenzte Gewährung der Nutzung des Add-ons "AI-Assistent" für den TimeGlobe-Kalender (nachfolgend "Software") im Unternehmen des Kunden über das Internet.

2. Leistungen von EcomTask
EcomTask gewährt dem Kunden (bzw. dessen Kunden) die Nutzung der jeweils aktuellen Version der Software mittels Zugriff durch WhatsApp.

3. Nutzungsumfang und -rechte
Der Kunde erhält an der jeweils aktuellen Version der Software einfache, d. h. nicht unterlizenzierbare und nicht übertragbare, zeitlich auf die Dauer des Vertrags beschränkte Rechte zur Nutzung.

4. Vergütung
Die monatliche Vergütung beträgt EUR ____.

5. Vertragslaufzeit
Der Vertrag wird auf unbestimmte Zeit geschlossen und kann mit einer Frist von X Monaten gekündigt werden.`;
  };

  // Handle popup window for WhatsApp connection
  const handleWhatsAppConnect = async () => {
    console.log('WhatsApp connect button clicked');
    console.log('Form data:', {
      ...formData,
      signature: formData.signature ? `[Signature data length: ${formData.signature.length}]` : null
    });
    
    setConnectionStatus('connecting');
    
    try {
      // First submit the contract with signature
      if (formData.signature) {
        // Get full contract text
        const fullContractText = getFullContractText();
        
        console.log('Sending contract to backend API:', {
          contract_text_length: fullContractText.length,
          signature_length: formData.signature.length
        });
        
        // Check token before making the API call
        const token = localStorage.getItem('token');
        console.log('Auth token available:', !!token);
        
        // Submit the contract to the backend
        try {
          await inlineContractService.createContract({
            contract_text: fullContractText,
            signature_image: formData.signature
          });
          
          console.log('Contract successfully sent to backend');
        } catch (contractError) {
          console.error('Error sending contract:', contractError);
          // Continue with WhatsApp connection even if contract submission fails
        }
      } else {
        console.log('No signature found, skipping contract submission');
      }
      
      // Open the 360dialog onboarding URL in a new tab or popup window
      const popupWindow = window.open(onboarding_url, 'WhatsAppConnection', 
        'width=1000,height=800,left=100,top=100');
      
      // Check if popup was blocked
      if (!popupWindow || popupWindow.closed || typeof popupWindow.closed === 'undefined') {
        alert('Popup wurde blockiert. Bitte erlauben Sie Popups für diese Website.');
        setConnectionStatus('idle');
        return;
      }

      // Store the popup reference
      popupWindowRef.current = popupWindow;
      
      // Set up an interval to check if the popup window was closed
      popupCheckIntervalRef.current = setInterval(() => {
        if (popupWindow.closed) {
          // If popup closed, consider it a successful connection
          clearInterval(popupCheckIntervalRef.current!);
          setConnectionStatus('success');
        }
      }, 1000);
      
      // Alternative method: Check for redirect in the current tab
      // This assumes the redirect happens in the same tab
      // and you can detect it by checking URL parameters
      const checkRedirectInterval = setInterval(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const status = urlParams.get('whatsapp_status');
        
        if (status === 'success') {
          clearInterval(checkRedirectInterval);
          setConnectionStatus('success');
        } else if (status === 'error') {
          clearInterval(checkRedirectInterval);
          setConnectionStatus('error');
        }
      }, 1000);
      
      // Clear interval after 5 minutes (300000 ms) to prevent memory leaks
      setTimeout(() => {
        clearInterval(checkRedirectInterval);
        if (popupCheckIntervalRef.current) {
          clearInterval(popupCheckIntervalRef.current);
        }
      }, 300000);
    } catch (error) {
      console.error('Error connecting WhatsApp:', error);
      setConnectionStatus('error');
    }
  };
  
  // Handle closing the success dialog
  const handleCloseSuccessDialog = () => {
    setOpenSuccessDialog(false);
  };

  return (
    <Box sx={{ mt: 3, pb: 8 }}>
      <Box
        sx={{
          p: 4,
          mb: 4,
          borderRadius: 2,
          backgroundColor: '#FFFFFF',
        }}
      >
        <Typography 
          variant="h6" 
          gutterBottom
          sx={{ 
            display: 'flex', 
            alignItems: 'center',
            color: '#333333',
            fontWeight: 'medium',
            mb: 2
          }}
        >
          <DoneAll sx={{ mr: 1, opacity: 0.9, color: '#1967D2' }} />
          Bestätigen & Verknüpfen
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 4, ml: 0.5 }}>
          Bitte überprüfen Sie Ihre Eingaben und verknüpfen Sie Ihren WhatsApp-Account.
        </Typography>
        
        <Paper 
          variant="outlined" 
          sx={{ 
            p: 3, 
            mb: 4,
            borderRadius: 2,
            backgroundColor: '#FFFFFF',
            borderColor: 'rgba(0, 0, 0, 0.1)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <Typography 
            variant="subtitle1" 
            gutterBottom 
            sx={{ 
              fontWeight: 'bold',
              mb: 3,
              color: '#333333',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <CheckCircle sx={{ mr: 1, fontSize: 20, color: '#1967D2' }} />
            Zusammenfassung
          </Typography>
          
          <List disablePadding>
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0, 
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <VpnKey sx={{ mr: 2, color: '#1967D2' }} />
              <ListItemText 
                primary="API-Schlüssel" 
                secondary={formData.apiKey} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: '#666666'
                }}
              />
            </ListItem>
            
            <Divider sx={{ my: 1, borderColor: 'rgba(0, 0, 0, 0.08)' }} />
            
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0,
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <Business sx={{ mr: 2, color: '#1967D2' }} />
              <ListItemText 
                primary="Unternehmen" 
                secondary={formData.companyName} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: '#666666'
                }}
              />
            </ListItem>
            
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0,
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <ListItemText 
                inset
                primary="Adresse" 
                secondary={`${formData.street}, ${formData.zipCode} ${formData.city}, ${formData.country}`} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: '#666666'
                }}
              />
            </ListItem>
            
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0,
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <Person sx={{ mr: 2, color: '#1967D2' }} />
              <ListItemText 
                primary="Ansprechpartner" 
                secondary={formData.contactPerson} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: '#666666'
                }}
              />
            </ListItem>
            
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0,
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <Email sx={{ mr: 2, color: '#1967D2' }} />
              <ListItemText 
                primary="E-Mail" 
                secondary={formData.email} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: '#666666'
                }}
              />
            </ListItem>
            
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0,
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <Phone sx={{ mr: 2, color: '#1967D2' }} />
              <ListItemText 
                primary="Telefon" 
                secondary={formData.phone} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: '#666666'
                }}
              />
            </ListItem>
            
            <Divider sx={{ my: 1, borderColor: 'rgba(0, 0, 0, 0.08)' }} />
            
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0,
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <CheckCircle sx={{ mr: 2, color: formData.hasAcceptedTerms ? '#1967D2' : 'rgba(0, 0, 0, 0.3)' }} />
              <ListItemText 
                primary="Vertrag akzeptiert" 
                secondary={formData.hasAcceptedTerms ? 'Ja' : 'Nein'} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: formData.hasAcceptedTerms ? '#1967D2' : '#666666'
                }}
              />
            </ListItem>
          </List>
          
          {formData.signature && (
            <Box>
              <Typography 
                variant="subtitle2" 
                sx={{ 
                  mt: 3, 
                  mb: 2, 
                  color: '#333333', 
                  fontWeight: 'medium'
                }}
              >
                Unterschrift:
              </Typography>
              
              <Box 
                sx={{ 
                  mt: 1, 
                  border: '1px solid rgba(0, 0, 0, 0.1)', 
                  p: 2, 
                  maxWidth: '300px',
                  borderRadius: 2,
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }}
              >
                <img 
                  src={formData.signature} 
                  alt="Unterschrift" 
                  style={{ maxWidth: '100%', height: 'auto' }} 
                />
              </Box>
            </Box>
          )}
        </Paper>
        
        <Box 
          sx={{ 
            p: 3, 
            borderRadius: 2, 
            backgroundColor: whatsappConnected ? 'rgba(76, 175, 80, 0.05)' : 'rgba(25, 103, 210, 0.05)',
            border: whatsappConnected ? '1px solid rgba(76, 175, 80, 0.2)' : '1px solid rgba(25, 103, 210, 0.2)',
            mb: 2,
            display: 'flex',
            alignItems: 'center',
            gap: 2
          }}
        >
          {whatsappConnected ? (
            <>
              <CheckCircleOutline sx={{ color: '#4CAF50', fontSize: 30 }} />
              <Box>
                <Typography color="#4CAF50" sx={{ fontWeight: 'medium', fontSize: '0.95rem' }}>
                  WhatsApp ist bereits mit Ihrem Konto verknüpft.
                </Typography>
                {whatsappNumber && (
                  <Typography color="text.secondary" sx={{ fontSize: '0.85rem', mt: 0.5 }}>
                    Verknüpfte Nummer: {whatsappNumber}
                  </Typography>
                )}
              </Box>
            </>
          ) : (
            <Typography color="#1967D2" sx={{ fontWeight: 'medium', fontSize: '0.95rem' }}>
              Der nächste Schritt ist die Verknüpfung Ihres WhatsApp Business-Kontos. 
              Klicken Sie auf "WhatsApp verknüpfen", um den Prozess zu starten.
            </Typography>
          )}
        </Box>

        {connectionStatus === 'error' && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3, 
              mt: 2,
              borderRadius: 2,
              backgroundColor: 'rgba(211, 47, 47, 0.1)', 
              border: '1px solid rgba(211, 47, 47, 0.2)',
              color: '#f44336',
              '& .MuiAlert-icon': {
                color: '#f44336'
              }
            }}
          >
            Bei der Verknüpfung mit WhatsApp ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.
          </Alert>
        )}
      </Box>
      
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        mt: 4
      }}>
        <Button 
          startIcon={<ArrowBack />}
          onClick={onBack}
          variant="outlined"
          color="primary"
        >
          Zurück
        </Button>
        
        {whatsappConnected ? (
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center',
            bgcolor: 'rgba(76, 175, 80, 0.1)',
            color: '#4CAF50',
            px: 2,
            py: 1,
            borderRadius: 1
          }}>
            <CheckCircle sx={{ mr: 1 }} />
            <Typography variant="body2">
              Erfolgreich verknüpft
            </Typography>
          </Box>
        ) : (
        <Button
          variant="contained"
          color="primary"
            onClick={handleWhatsAppConnect}
            disabled={connectionStatus === 'connecting'}
            endIcon={connectionStatus === 'connecting' ? undefined : <WhatsApp />}
        >
            {connectionStatus === 'connecting' ? 'Verbinde...' : 'Mit WhatsApp verbinden'}
        </Button>
        )}
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
const ConfirmationStepWithFooter: React.FC<ConfirmationStepProps> = (props) => {
  return (
    <>
      <ConfirmationStep {...props} />
      <Footer />
    </>
  );
};

export default ConfirmationStepWithFooter; 