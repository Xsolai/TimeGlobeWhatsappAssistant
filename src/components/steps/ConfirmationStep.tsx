import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, Typography, Paper, List, ListItem, ListItemText, Divider, useTheme, 
  Snackbar, Alert, Dialog, DialogTitle, DialogContent, DialogActions, TextField, CircularProgress, Stack, IconButton, InputAdornment, Tooltip } from '@mui/material';
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
import { Visibility, VisibilityOff, ContentCopy } from '@mui/icons-material';
import whatsappService from '../../services/whatsappService';
import authService from '../../services/authService';

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

export const ConfirmationStep: React.FC<ConfirmationStepProps> = ({ formData, onBack }): JSX.Element => {
  const theme = useTheme();
  const [openSuccessDialog, setOpenSuccessDialog] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'connecting' | 'success' | 'error' | 'disconnected'>('idle');
  const [whatsappConnected, setWhatsappConnected] = useState<boolean>(false);
  const [whatsappNumber, setWhatsappNumber] = useState<string>('');
  const [signupData, setSignupData] = useState<any>(null);
  const [authCode, setAuthCode] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error' | 'info', message: string } | null>(null);
  const [isCheckingStatus, setIsCheckingStatus] = useState<boolean>(false);
  const [isCompletingOnboarding, setIsCompletingOnboarding] = useState<boolean>(false);
  
  // API Key visibility and password protection
  const [showApiKey, setShowApiKey] = useState(false);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [password, setPassword] = useState('');
  const [passwordError, setPasswordError] = useState(false);
  const [passwordErrorMessage, setPasswordErrorMessage] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);
  
  // Check status on component mount
  useEffect(() => {
    if (formData.email) {
      handleCheckStatus();
    }
  }, [formData.email]);

  // Check status every 30 seconds if not connected
  useEffect(() => {
    let statusCheckInterval: NodeJS.Timeout | null = null;
    
    if (!whatsappConnected && formData.email) {
      statusCheckInterval = setInterval(handleCheckStatus, 30000);
    }

    return () => {
      if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
      }
    };
  }, [whatsappConnected, formData.email]);

  // API Key masking function
  const maskApiKey = (key: string) => {
    if (!key) return '';
    return '*'.repeat(key.length);
  };

  // Handle API Key visibility toggle
  const handleApiKeyVisibilityToggle = () => {
    if (showApiKey) {
      setShowApiKey(false);
    } else {
      setPasswordDialogOpen(true);
    }
  };

  // Handle password dialog close
  const handlePasswordDialogClose = () => {
    setPasswordDialogOpen(false);
    setPassword('');
    setPasswordError(false);
    setPasswordErrorMessage('');
  };

  // Handle password input change
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    setPasswordError(false);
    setPasswordErrorMessage('');
  };

  // Handle password submission
  const handlePasswordSubmit = async () => {
    if (!password) {
      setPasswordError(true);
      setPasswordErrorMessage('Bitte geben Sie Ihr Passwort ein.');
      return;
    }

    setIsValidating(true);
    try {
      const isValid = await authService.validatePassword(password);
      if (isValid) {
        setShowApiKey(true);
        handlePasswordDialogClose();
      } else {
        setPasswordError(true);
        setPasswordErrorMessage('Ungültiges Passwort.');
      }
    } catch (err) {
      console.error('Password validation error:', err);
      setPasswordError(true);
      setPasswordErrorMessage('Fehler bei der Passwortprüfung. Bitte versuchen Sie es erneut.');
    } finally {
      setIsValidating(false);
    }
  };

  // Handle copy API key
  const handleCopyApiKey = () => {
    if (formData.apiKey) {
      navigator.clipboard.writeText(formData.apiKey);
      setCopyFeedback('API-Schlüssel kopiert!');
      setTimeout(() => setCopyFeedback(null), 2000);
    }
  };

  // Event listener for WhatsApp signup messages
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (!event.origin.endsWith('facebook.com')) return;
      try {
        let data;
        if (typeof event.data === 'string') {
          data = JSON.parse(event.data);
        } else {
          data = event.data;
        }

        if (data.type === 'WA_EMBEDDED_SIGNUP') {
          console.log('WhatsApp Signup Event:', data);
          
          // Clean and normalize the data
          const cleanData = {
            type: 'WA_EMBEDDED_SIGNUP',
            event: String(data.event || 'FINISH'),
            version: '3',
            business_id: String(data.business_id || data.data?.business_id || ''),
            phone_number_id: String(data.phone_number_id || data.data?.phone_number_id || ''),
            waba_id: String(data.waba_id || data.data?.waba_id || '')
          };

          console.log('Cleaned signup data:', cleanData);
          setSignupData(cleanData);
          
          if (data.event === 'FINISH' || data.event === 'FINISH_ONLY_WABA' || data.event === 'FINISH_WHATSAPP_BUSINESS_APP_ONBOARDING') {
            setStatusMessage({
              type: 'success',
              message: 'Facebook-Autorisierung war erfolgreich. Sie können nun das Onboarding abschließen.'
            });
          } else if (data.event === 'CANCEL') {
            setStatusMessage({
              type: 'error',
              message: 'Der Onboarding-Prozess wurde abgebrochen.'
            });
          }
        }
      } catch (e) {
        console.error('Error parsing message:', e);
        console.log('Raw message event:', event.data);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // Debug effect to log state changes
  useEffect(() => {
    console.log('State updated:', {
      hasAuthCode: !!authCode,
      hasSignupData: !!signupData,
      signupEvent: signupData?.event,
      isConnected: whatsappConnected,
      connectionStatus
    });
  }, [authCode, signupData, whatsappConnected, connectionStatus]);

  // Facebook login callback
  const fbLoginCallback = (response: any) => {
    console.log('=== FACEBOOK LOGIN CALLBACK DEBUG ===');
    console.log('Full Facebook Response Object:', response);
    
    if (response.authResponse) {
      console.log('--- AUTH RESPONSE DETAILS ---');
      console.log('Full authResponse:', response.authResponse);
      
      // Extract code from the correct location in the response
      let code = null;
      
      // Try to get code from different possible locations
      if (response.authResponse.code) {
        code = response.authResponse.code;
      } else if (response.authResponse.data && response.authResponse.data.code) {
        code = response.authResponse.data.code;
        } else {
        // Try to parse code from raw response if needed
        try {
          const rawData = JSON.stringify(response);
          const codeMatch = rawData.match(/code=([^&]+)/);
          if (codeMatch) {
            code = codeMatch[1];
          }
        } catch (e) {
          console.error('Error parsing raw response:', e);
        }
      }

      if (code) {
        console.log('Authorization Code Found:', code.substring(0, 20) + '...');
        setAuthCode(code);
        setStatusMessage({
          type: 'info',
          message: 'Facebook-Autorisierung war erfolgreich. Sie können nun das Onboarding abschließen.'
        });
      } else {
        console.error('No authorization code found in response');
        setStatusMessage({
          type: 'error',
          message: 'Es konnte kein Autorisierungscode gefunden werden. Bitte versuchen Sie die Verbindung erneut.'
        });
      }
    } else {
      console.log('Login failed:', response);
      setStatusMessage({
        type: 'error',
        message: 'Die Anmeldung bei Facebook war nicht erfolgreich. Bitte versuchen Sie es erneut.'
      });
    }
  };

  // Launch WhatsApp signup
  const handleWhatsAppConnect = () => {
    console.log('🚀 Starting Facebook Login with Embedded Signup...');
    setConnectionStatus('connecting');
    // Reset previous states
    setAuthCode(null);
    setSignupData(null);
    setStatusMessage(null);
    
    (window as any).FB.login(fbLoginCallback, {
      config_id: '966700112247031',
      response_type: 'code',
      override_default_response_type: true,
      extras: {
        setup: {},
        featureType: '',
        sessionInfoVersion: '3'
      }
    });
  };

  // Complete onboarding
  const handleCompleteOnboarding = async (signupDataParam: any, authCodeParam: string) => {
    if (!signupDataParam || !authCodeParam) {
      setStatusMessage({
        type: 'info',
        message: 'Um das Onboarding abzuschließen, verbinden Sie sich bitte zuerst mit Facebook.'
      });
      return;
    }

    try {
      setIsCompletingOnboarding(true);
      setConnectionStatus('connecting');
      console.log('Raw signup data:', signupDataParam);

      // Safely extract data, ensuring all values are strings
      const businessId = String(signupDataParam.business_id || signupDataParam.data?.business_id || '');
      const phoneNumberId = String(signupDataParam.phone_number_id || signupDataParam.data?.phone_number_id || '');
      const wabaId = String(signupDataParam.waba_id || signupDataParam.data?.waba_id || '');

      // Clean and validate the data
      const cleanSignupData = {
        business_id: businessId,
        phone_number_id: phoneNumberId,
        waba_id: wabaId,
        event: String(signupDataParam.event || 'FINISH'),
        type: 'WA_EMBEDDED_SIGNUP',
        version: '3'
      };

      // Create the payload with minimal required data
      const payload = {
        auth_code: String(authCodeParam),
        business_email: formData.email,
        signup_data: cleanSignupData
      };

      console.log('Cleaned payload:', payload);

      const response = await fetch(`${API_URL}/api/whatsapp/complete-onboarding-public`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Server response:', errorText);
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('Server response:', result);

      if (result.success) {
        setStatusMessage({
          type: 'success',
          message: 'WhatsApp Business API wurde erfolgreich mit Ihrem Konto verbunden.'
        });
        setConnectionStatus('success');
        setWhatsappConnected(true);
        
        if (result.facebook_permissions_url) {
          showFacebookPermissionsButton(result.facebook_permissions_url);
        }
        
        handleCheckStatus();
      } else {
        throw new Error(result.detail || result.message || 'Unbekannter Fehler');
      }
    } catch (error) {
      console.error('Error completing onboarding:', error);
              setStatusMessage({
          type: 'error',
          message: `Es ist ein Fehler beim Onboarding-Prozess aufgetreten: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`
        });
      setConnectionStatus('error');
    } finally {
      setIsCompletingOnboarding(false);
    }
  };

  // Check onboarding status
  const handleCheckStatus = async () => {
    if (!formData.email || isCheckingStatus) return;

    try {
      setIsCheckingStatus(true);
      
      const response = await fetch(`${API_URL}/api/whatsapp/status-public?business_email=${encodeURIComponent(formData.email)}`);
      
      if (response.ok) {
        const status = await response.json();
        
                if (status.is_connected) {
          const webhookStatus = status.whatsapp_profile?.webhook_configured ? 'Konfiguriert' : 'Manuelle Einrichtung erforderlich';
          setWhatsappConnected(true);
          setWhatsappNumber(status.whatsapp_number || '');
          setConnectionStatus('success');
          setStatusMessage({
            type: 'success',
            message: `WhatsApp erfolgreich verbunden. Telefonnummer: ${status.whatsapp_number || 'Nicht verfügbar'}. Webhook-Status: ${webhookStatus}.`
          });
          
          // Disable the connect button if already connected
          const fbButton = document.querySelector('[data-fb-connect]') as HTMLButtonElement;
          if (fbButton) {
            fbButton.disabled = true;
          }
        } else {
          setWhatsappConnected(false);
          setConnectionStatus('disconnected');
          setStatusMessage({
            type: 'info',
            message: 'WhatsApp ist derzeit nicht mit Ihrem Konto verbunden. Bitte stellen Sie eine Verbindung über Facebook her.'
          });
        }
      }
    } catch (error) {
      console.error('Error checking status:', error);
      setStatusMessage({
        type: 'error',
        message: 'Es ist ein Fehler beim Überprüfen des WhatsApp-Verbindungsstatus aufgetreten.'
      });
    } finally {
      setIsCheckingStatus(false);
    }
  };
  
  // Helper function to show Facebook permissions button
  const showFacebookPermissionsButton = (permissionsUrl: string) => {
    const buttonContainer = document.querySelector('.button-container');
    if (!buttonContainer) return;
    
    const existingBtn = document.getElementById('facebookPermissionsBtn');
    if (existingBtn) existingBtn.remove();
    
    const permissionsBtn = document.createElement('button');
    permissionsBtn.id = 'facebookPermissionsBtn';
    permissionsBtn.className = 'MuiButton-root MuiButton-contained MuiButton-containedPrimary';
    permissionsBtn.textContent = 'Messaging-Berechtigungen erteilen';
    permissionsBtn.style.marginLeft = '10px';
    permissionsBtn.style.backgroundColor = '#25D366';
    permissionsBtn.style.color = 'white';
    permissionsBtn.onclick = () => window.open(permissionsUrl, '_blank');
    
    buttonContainer.appendChild(permissionsBtn);
  };

  const showCompleteButton = authCode && 
    signupData && 
    (signupData.event === 'FINISH' || signupData.event === 'FINISH_ONLY_WABA' || signupData.event === 'FINISH_WHATSAPP_BUSINESS_APP_ONBOARDING') && 
    !whatsappConnected;

  return (
    <Box sx={{ width: '100%', maxWidth: 800, mx: 'auto', p: { xs: 2, sm: 3 } }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 4, fontSize: { xs: '1.25rem', sm: '1.5rem' } }}>
        Bestätigung und WhatsApp-Verbindung
        </Typography>
        
      <Paper sx={{ p: { xs: 2, sm: 3 }, mb: 4 }}>
        <List>
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0, 
                borderRadius: 1,
                flexDirection: 'column',
                alignItems: 'flex-start',
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, width: '100%' }}>
                <VpnKey sx={{ mr: 2, color: '#1967D2' }} />
                <Typography 
                  variant="body1" 
                  sx={{ fontWeight: 'medium', color: '#333333' }}
                >
                  API-Schlüssel
                </Typography>
              </Box>
              <Box sx={{ 
                display: 'flex', 
                gap: { xs: 0.5, sm: 1 },
                alignItems: 'center',
                width: '100%',
                flexDirection: { xs: 'column', sm: 'row' }
              }}>
                <TextField
                  fullWidth
                  value={showApiKey ? formData.apiKey : maskApiKey(formData.apiKey)}
                  disabled
                  size="small"
                  sx={{
                    '& .MuiInputBase-root': {
                      height: { xs: '40px', sm: '44px' },
                      fontSize: { xs: '0.75rem', sm: '0.875rem' },
                      fontFamily: 'monospace',
                      '& .MuiInputAdornment-root': {
                        height: '100%'
                      }
                    }
                  }}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="Toggle API key visibility"
                          onClick={handleApiKeyVisibilityToggle}
                          edge="end"
                          size="small"
                          sx={{ p: { xs: 0.3, sm: 0.5 } }}
                        >
                          {showApiKey ? <VisibilityOff sx={{ fontSize: { xs: 16, sm: 18 } }} /> : <Visibility sx={{ fontSize: { xs: 16, sm: 18 } }} />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                {showApiKey && (
                  <Tooltip title="API-Schlüssel kopieren">
                    <IconButton
                      onClick={handleCopyApiKey}
                      size="small"
                      sx={{ 
                        color: '#1967D2', 
                        p: { xs: 0.8, sm: 0.5 },
                        alignSelf: { xs: 'center', sm: 'auto' },
                        mt: { xs: 1, sm: 0 }
                      }}
                    >
                      <ContentCopy sx={{ fontSize: { xs: 16, sm: 18 } }} />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>
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
        </Paper>
        
      <Paper sx={{ p: { xs: 2, sm: 3 }, mt: 2 }}>
        <Typography variant="h5" gutterBottom sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem' } }}>
          WhatsApp Business API Verbindung
            </Typography>
        
        <Box sx={{ mt: 3 }}>
          <Stack 
            spacing={{ xs: 2, sm: 3 }} 
            direction={{ xs: 'column', sm: 'row' }} 
            alignItems="center" 
            justifyContent="center"
          >
            <Button
              onClick={onBack}
              variant="text"
            sx={{ 
                color: '#3b82f6',
                width: { xs: '100%', sm: 'auto' },
                order: { xs: 3, sm: 1 },
                '&:hover': {
                  backgroundColor: 'transparent',
                  textDecoration: 'underline'
                }
              }}
              startIcon={<span>←</span>}
        >
          Zurück
        </Button>
        
            <Button
              variant="contained"
              onClick={handleWhatsAppConnect}
              startIcon={whatsappConnected ? <CheckCircle /> : <WhatsApp />}
              disabled={whatsappConnected || isCheckingStatus}
              data-fb-connect
              sx={{
                backgroundColor: whatsappConnected ? '#22c55e' : '#3b82f6',
                '&:hover': {
                  backgroundColor: whatsappConnected ? '#16a34a' : '#2563eb',
                },
                color: 'white',
                minWidth: { xs: 'auto', sm: '220px' },
                width: { xs: '100%', sm: 'auto' },
                borderRadius: '8px',
                textTransform: 'none',
                fontSize: { xs: '0.875rem', sm: '0.95rem' },
                py: { xs: 1.2, sm: 1.5 },
                order: { xs: 1, sm: 2 }
              }}
            >
              {isCheckingStatus ? (
                <>
                  <CircularProgress
                    size={24}
                    sx={{
                      color: 'white',
                      position: 'absolute',
                      left: '50%',
                      marginLeft: '-12px'
                    }}
                  />
                  <span style={{ visibility: 'hidden' }}>Mit Facebook verbinden</span>
                </>
              ) : whatsappConnected ? (
                'Verbunden'
              ) : (
                'Mit Facebook verbinden'
              )}
            </Button>

            <Button
              variant="contained"
              onClick={() => {
                if (!authCode || !signupData) {
                  setStatusMessage({
                    type: 'info',
                    message: 'Um das Onboarding abzuschließen, verbinden Sie sich bitte zuerst mit Facebook.'
                  });
                  return;
                }
                handleCompleteOnboarding(signupData, authCode);
              }}
              disabled={isCompletingOnboarding || whatsappConnected || !authCode || !signupData}
              sx={{
                backgroundColor: '#22c55e',
                '&:hover': {
                  backgroundColor: '#16a34a',
                },
                color: 'white',
                fontWeight: 500,
                minWidth: { xs: 'auto', sm: '220px' },
                width: { xs: '100%', sm: 'auto' },
                borderRadius: '8px',
                textTransform: 'none',
                fontSize: { xs: '0.875rem', sm: '0.95rem' },
                py: { xs: 1.2, sm: 1.5 },
                position: 'relative',
                order: { xs: 2, sm: 3 }
              }}
            >
              {isCompletingOnboarding ? (
                <>
                  <CircularProgress
                    size={24}
                    sx={{
                      color: 'white',
                      position: 'absolute',
                      left: '50%',
                      marginLeft: '-12px'
                    }}
                  />
                  <span style={{ visibility: 'hidden' }}>Onboarding abschließen</span>
                </>
              ) : whatsappConnected ? (
                'Onboarding abgeschlossen'
              ) : (
                'Onboarding abschließen'
              )}
            </Button>
          </Stack>

          {statusMessage && (
          <Box sx={{ 
              mt: 3, 
              p: { xs: 2, sm: 2 }, 
              borderRadius: 2,
              backgroundColor: statusMessage.type === 'success' ? '#e8f5e9' : 
                             statusMessage.type === 'error' ? '#ffebee' : '#e3f2fd',
            display: 'flex', 
            alignItems: 'flex-start',
              gap: 1
            }}>
              <Box sx={{ 
                width: 24, 
                height: 24, 
                borderRadius: '50%', 
                backgroundColor: statusMessage.type === 'success' ? '#2e7d32' : 
                               statusMessage.type === 'error' ? '#c62828' : '#1565c0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                mt: 0.25
              }}>
                {statusMessage.type === 'info' && (
                  <Typography sx={{ color: 'white', fontSize: '14px', fontWeight: 'bold' }}>i</Typography>
                )}
                {statusMessage.type === 'success' && (
                  <CheckCircleOutline sx={{ color: 'white', fontSize: '16px' }} />
                )}
                {statusMessage.type === 'error' && (
                  <Typography sx={{ color: 'white', fontSize: '14px', fontWeight: 'bold' }}>!</Typography>
                )}
              </Box>
              <Box sx={{ flexGrow: 1 }}>
                <Typography 
                  variant="body2"
                  sx={{ 
                    color: statusMessage.type === 'success' ? '#2e7d32' : 
                           statusMessage.type === 'error' ? '#c62828' : '#1565c0',
                    fontWeight: 'medium',
                    fontSize: { xs: '0.875rem', sm: '1rem' }
                  }}
                >
                  {statusMessage.message}
                </Typography>
              </Box>
            </Box>
        )}
      </Box>
      </Paper>

      <Dialog
        open={openSuccessDialog}
        onClose={() => setOpenSuccessDialog(false)}
      >
        <DialogTitle>Verbindung erfolgreich</DialogTitle>
        <DialogContent>
          <Typography>
            Ihr WhatsApp Business Account wurde erfolgreich verbunden.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenSuccessDialog(false)} color="primary">
            Schließen
          </Button>
        </DialogActions>
      </Dialog>

      {/* Password Dialog for API Key */}
      <Dialog 
        open={passwordDialogOpen} 
        onClose={handlePasswordDialogClose}
        fullWidth
        maxWidth="sm"
        sx={{
          '& .MuiDialog-paper': {
            mx: { xs: 1, sm: 3 },
            width: { xs: 'calc(100% - 16px)', sm: 'auto' }
          }
        }}
      >
        <DialogTitle sx={{ 
          fontSize: { xs: '1.1rem', sm: '1.25rem' },
          pb: { xs: 1, sm: 2 }
        }}>
          Passwort erforderlich
        </DialogTitle>
        <DialogContent sx={{ pt: { xs: 1, sm: 2 } }}>
          <Typography 
            variant="body2" 
            sx={{ 
              mb: { xs: 1.5, sm: 2 },
              fontSize: { xs: '0.875rem', sm: '0.875rem' }
            }}
          >
            Bitte geben Sie Ihr Passwort ein, um den API-Schlüssel anzuzeigen.
          </Typography>
          <TextField
            autoFocus
            margin="dense"
            label="Passwort"
            type="password"
            fullWidth
            value={password}
            onChange={handlePasswordChange}
            error={passwordError}
            helperText={passwordErrorMessage}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !isValidating) {
                handlePasswordSubmit();
              }
            }}
            disabled={isValidating}
            sx={{
              '& .MuiInputBase-root': {
                height: { xs: '48px', sm: '56px' }
              },
              '& .MuiFormHelperText-root': {
                fontSize: { xs: '0.75rem', sm: '0.75rem' }
              }
            }}
          />
        </DialogContent>
        <DialogActions sx={{ 
          px: { xs: 2, sm: 3 },
          pb: { xs: 2, sm: 3 },
          gap: { xs: 1, sm: 0 },
          flexDirection: { xs: 'column', sm: 'row' }
        }}>
          <Button 
            onClick={handlePasswordDialogClose}
            disabled={isValidating}
            fullWidth={true}
            sx={{ 
              order: { xs: 2, sm: 1 },
              minWidth: { xs: '100%', sm: 'auto' }
            }}
          >
            Abbrechen
          </Button>
          <Button 
            onClick={handlePasswordSubmit} 
            variant="contained"
            disabled={isValidating}
            fullWidth={true}
            sx={{ 
              order: { xs: 1, sm: 2 },
              minWidth: { xs: '100%', sm: 'auto' }
            }}
          >
            {isValidating ? <CircularProgress size={20} sx={{ color: 'white' }} /> : 'Bestätigen'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Copy Feedback Snackbar */}
      {copyFeedback && (
        <Snackbar
          open={!!copyFeedback}
          autoHideDuration={2000}
          onClose={() => setCopyFeedback(null)}
          message={copyFeedback}
          sx={{
            '& .MuiSnackbarContent-root': {
              backgroundColor: '#4CAF50',
              color: 'white'
            }
          }}
        />
      )}
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