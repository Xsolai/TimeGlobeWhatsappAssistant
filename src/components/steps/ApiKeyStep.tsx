import React, { useState, useEffect, useCallback } from 'react';
import { Box, TextField, Button, Typography, Alert, useTheme, Paper, InputAdornment, CircularProgress, Chip } from '@mui/material';
import Key from '@mui/icons-material/Key';
import ArrowForward from '@mui/icons-material/ArrowForward';
import ArrowBack from '@mui/icons-material/ArrowBack';
import CheckCircle from '@mui/icons-material/CheckCircle';
import authService from '../../services/authService';

interface ApiKeyStepProps {
  apiKey: string;
  onFormChange: (data: { apiKey: string, customerCd?: string }) => void;
  onNext: () => void;
  onBack?: () => void;
}

const ApiKeyStep: React.FC<ApiKeyStepProps> = ({ apiKey, onFormChange, onNext, onBack }) => {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isInitialLoading, setIsInitialLoading] = useState<boolean>(true);
  const [customerCd, setCustomerCd] = useState<string | null>(null);
  const [isValidated, setIsValidated] = useState<boolean>(false);
  const theme = useTheme();

  // Create a stable reference to onFormChange
  const stableOnFormChange = useCallback((data: { apiKey: string, customerCd?: string }) => {
    onFormChange(data);
  }, [onFormChange]);

  // Fetch TimeGlobe key on component mount and check validation status
  useEffect(() => {
    let isMounted = true;
    const fetchExistingKey = async () => {
      try {
        setIsInitialLoading(true);
        const response = await authService.getBusinessTimeglobeKey();
        console.log('Existing key response:', response);

        // Only update state if component is still mounted
        if (!isMounted) return;

        if (response && response.timeglobe_auth_key) {
          // If key exists, set it
          stableOnFormChange({ apiKey: response.timeglobe_auth_key });
          
          // If the key exists and is validated, set validation status
          if (response.customer_id || response.customer_cd) {
            setCustomerCd(response.customer_id || response.customer_cd);
            setIsValidated(true);
          } else if (apiKey) {
            // Wenn wir einen API-Key haben aber keine Validierung, validieren wir erneut
            validateApiKey();
          }
        }
      } catch (err) {
        console.error('Error fetching existing TimeGlobe key:', err);
      } finally {
        if (isMounted) {
          setIsInitialLoading(false);
        }
      }
    };

    fetchExistingKey();
    
    return () => {
      isMounted = false;
    };
  }, []);

  const handleApiKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Prevent changes if already validated
    if (isValidated) {
      return;
    }
    onFormChange({ apiKey: e.target.value });
    setError(null);
    setIsValidated(false);
    setCustomerCd(null);
  };

  const validateApiKey = async () => {
    if (!apiKey.trim()) {
      setError('Bitte geben Sie einen gültigen API-Schlüssel ein');
      return false;
    }

    try {
      setIsLoading(true);
      
      try {
        // Use the authService to validate the TimeGlobe key
        const data = await authService.validateTimeglobeKey(apiKey);
        console.log("API-Antwort:", data);
        
        // Check for "valid: true" or "success: true" in the response
        if (data && (data.valid === true || data.success === true)) {
          // If the API key is valid
          const customerId = data.customer_cd || data.customer_id || 'Validiert';
          setCustomerCd(customerId);
          onFormChange({ apiKey, customerCd: customerId });
          setIsValidated(true);
          
          return true;
        } else {
          // Handle case when the API returns a 200 status but validation failed
          setError('Der TimeGlobe API-Schlüssel ist ungültig. Bitte überprüfen Sie den Schlüssel und versuchen Sie es erneut.');
          return false;
        }
      } catch (apiError: any) {
        console.error('API-Fehler:', apiError);
        
        // Check if there's a specific error message from the API
        if (apiError.message) {
          setError('Der TimeGlobe API-Schlüssel konnte nicht validiert werden: ' + apiError.message);
        } else {
          setError('Die Verbindung zum TimeGlobe-Server konnte nicht hergestellt werden. Bitte versuchen Sie es später erneut.');
        }
        return false;
      }
    } catch (err) {
      console.error('Allgemeiner Fehler:', err);
      setError('Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isValidated) {
      const isValid = await validateApiKey();
      if (isValid) {
        onNext();
      }
    } else {
      // If already validated, then go to next step
      onNext();
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3, pb: 8 }}>
      <Box
        sx={{
          p: 4,
          mb: 4,
          borderRadius: 2,
          backgroundColor: '#FFFFFF',
        }}
      >
        {isInitialLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 8 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Box sx={{ position: 'relative', mb: 2 }}>
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  color: '#333333',
                  fontWeight: 'medium'
                }}
              >
                <Key sx={{ mr: 1, opacity: 0.9, color: '#1967D2' }} />
                TimeGlobe API-Schlüssel
              </Typography>
              
              <Typography variant="body2" sx={{ mb: 4, color: '#333333' }}>
                Der API-Schlüssel wird benötigt, um Ihren WhatsApp Chatbot mit Ihrem TimeGlobe-Konto zu verbinden.
              </Typography>
            </Box>
            
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
            
            {isValidated && customerCd && (
              <Box 
                sx={{ 
                  mt: 2, 
                  mb: 3, 
                  p: 3, 
                  borderRadius: 2, 
                  backgroundColor: 'rgba(25, 103, 210, 0.05)',
                  border: '1px solid rgba(25, 103, 210, 0.2)'
                }}
              >
                <Typography variant="subtitle2" sx={{ color: '#333333', mb: 1 }}>
                  Ihr TimeGlobe Kunden-Code:
                </Typography>
                <Typography variant="h6" sx={{ color: '#1967D2', fontWeight: 'bold' }}>
                  {customerCd}
                </Typography>
                <Typography variant="body2" sx={{ color: '#666666', mt: 1 }}>
                  Bitte bestätigen Sie, dass dies Ihr korrekter Kunden-Code ist, indem Sie auf "Weiter" klicken.
                </Typography>
              </Box>
            )}
            
            <TextField
              fullWidth
              label="API-Schlüssel*"
              value={apiKey}
              onChange={handleApiKeyChange}
              margin="normal"
              variant="outlined"
              required
              disabled={isLoading || isValidated}
              placeholder="Ihr TimeGlobe API-Schlüssel"
              sx={{ 
                mb: 5,
                mt: 4,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 1,
                  backgroundColor: isValidated ? '#f5f5f5' : '#FFFFFF',
                  '&:hover': {
                    backgroundColor: isValidated ? '#f5f5f5' : '#FFFFFF',
                  },
                  '&.Mui-focused': {
                    backgroundColor: isValidated ? '#f5f5f5' : '#FFFFFF',
                  },
                  height: '56px'
                },
                '& .MuiInputLabel-root': {
                  color: isValidated ? '#666666' : '#555',
                  fontWeight: 500
                },
                '& .MuiInputBase-input': {
                  color: isValidated ? '#666666' : '#000000',
                  fontWeight: 500,
                  cursor: isValidated ? 'not-allowed' : 'text'
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Key sx={{ color: isValidated ? '#666666' : '#1967d2', mr: 1 }} />
                  </InputAdornment>
                ),
                endAdornment: isValidated ? (
                  <InputAdornment position="end">
                    <CheckCircle sx={{ color: '#4CAF50' }} />
                  </InputAdornment>
                ) : null,
                readOnly: isValidated
              }}
            />
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
              <Button
                type="submit"
                variant="contained"
                disabled={isLoading || !apiKey.trim()}
                sx={{
                  px: 4,
                  py: 1.5,
                  backgroundColor: '#1967d2',
                  color: '#FFFFFF',
                  borderRadius: 50,
                  boxShadow: '0 4px 8px 0 rgba(68, 82, 198, 0.2)',
                  '&:hover': {
                    backgroundColor: '#3A45A6',
                  },
                  '&:disabled': {
                    backgroundColor: '#E0E0E0',
                    color: '#9E9E9E',
                  },
                  textTransform: 'none',
                  fontWeight: 'medium',
                }}
                endIcon={
                  isLoading ? (
                    <CircularProgress size={20} color="inherit" />
                  ) : (
                    <ArrowForward />
                  )
                }
              >
                {isLoading ? 'Validiere...' : isValidated ? 'Weiter' : 'Validieren'}
              </Button>
            </Box>
          </>
        )}
      </Box>
      <Box sx={{ display: 'none' }}>
        <Footer />
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
const ApiKeyStepWithFooter: React.FC<ApiKeyStepProps> = (props) => {
  return (
    <>
      <ApiKeyStep {...props} />
      <Footer />
    </>
  );
};

export default ApiKeyStepWithFooter; 