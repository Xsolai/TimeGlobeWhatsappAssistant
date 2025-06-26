import React, { useState, useEffect, useCallback } from 'react';
import { Box, TextField, Button, Typography, Alert, useTheme, Paper, InputAdornment, CircularProgress, Chip, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Tooltip, Snackbar } from '@mui/material';
import Key from '@mui/icons-material/Key';
import ArrowForward from '@mui/icons-material/ArrowForward';
import ArrowBack from '@mui/icons-material/ArrowBack';
import CheckCircle from '@mui/icons-material/CheckCircle';
import { Visibility, VisibilityOff, ContentCopy } from '@mui/icons-material';
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
  
  // API Key visibility and password protection
  const [showApiKey, setShowApiKey] = useState(false);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [password, setPassword] = useState('');
  const [passwordError, setPasswordError] = useState(false);
  const [passwordErrorMessage, setPasswordErrorMessage] = useState('');
  const [isValidatingPassword, setIsValidatingPassword] = useState(false);
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);

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

    setIsValidatingPassword(true);
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
      setIsValidatingPassword(false);
    }
  };

  // Handle copy API key
  const handleCopyApiKey = () => {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey);
      setCopyFeedback('API-Schlüssel kopiert!');
      setTimeout(() => setCopyFeedback(null), 2000);
    }
  };

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
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: { xs: 2, sm: 3 }, pb: { xs: 6, sm: 8 } }}>
      <Box
        sx={{
          p: { xs: 2, sm: 3, md: 4 },
          mb: { xs: 2, sm: 4 },
          borderRadius: 2,
          backgroundColor: '#FFFFFF',
        }}
      >
        {isInitialLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: { xs: 6, sm: 8 } }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Box sx={{ position: 'relative', mb: { xs: 1.5, sm: 2 } }}>
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  color: '#333333',
                  fontWeight: 'medium',
                  fontSize: { xs: '1.1rem', sm: '1.25rem' }
                }}
              >
                <Key sx={{ 
                  mr: 1, 
                  opacity: 0.9, 
                  color: '#1967D2',
                  fontSize: { xs: '1.2rem', sm: '1.5rem' }
                }} />
                TimeGlobe API-Schlüssel
              </Typography>
              
              <Typography 
                variant="body2" 
                sx={{ 
                  mb: { xs: 3, sm: 4 }, 
                  color: '#333333',
                  fontSize: { xs: '0.875rem', sm: '0.875rem' },
                  lineHeight: { xs: 1.4, sm: 1.5 }
                }}
              >
                Der API-Schlüssel wird benötigt, um Ihren WhatsApp Chatbot mit Ihrem TimeGlobe-Konto zu verbinden.
              </Typography>
            </Box>
            
            {error && (
              <Alert 
                severity="error" 
                sx={{ 
                  mb: { xs: 2, sm: 3 }, 
                  borderRadius: 2,
                  backgroundColor: 'rgba(211, 47, 47, 0.15)', 
                  color: '#ff6b6b',
                  fontSize: { xs: '0.875rem', sm: '0.875rem' },
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
                  mt: { xs: 1.5, sm: 2 }, 
                  mb: { xs: 2, sm: 3 }, 
                  p: { xs: 2, sm: 3 }, 
                  borderRadius: 2, 
                  backgroundColor: 'rgba(25, 103, 210, 0.05)',
                  border: '1px solid rgba(25, 103, 210, 0.2)'
                }}
              >
                <Typography 
                  variant="subtitle2" 
                  sx={{ 
                    color: '#333333', 
                    mb: 1,
                    fontSize: { xs: '0.875rem', sm: '0.875rem' }
                  }}
                >
                  Ihr TimeGlobe Kunden-Code:
                </Typography>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    color: '#1967D2', 
                    fontWeight: 'bold',
                    fontSize: { xs: '1.1rem', sm: '1.25rem' },
                    wordBreak: 'break-all'
                  }}
                >
                  {customerCd}
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: '#666666', 
                    mt: 1,
                    fontSize: { xs: '0.75rem', sm: '0.875rem' }
                  }}
                >
                  Bitte bestätigen Sie, dass dies Ihr korrekter Kunden-Code ist, indem Sie auf "Weiter" klicken.
                </Typography>
              </Box>
            )}
            
            <Box sx={{ position: 'relative' }}>
              <TextField
                fullWidth
                label="API-Schlüssel*"
                value={showApiKey ? apiKey : maskApiKey(apiKey)}
                onChange={handleApiKeyChange}
                margin="normal"
                variant="outlined"
                required
                disabled={isLoading || isValidated}
                placeholder="Ihr TimeGlobe API-Schlüssel"
                sx={{ 
                  mb: { xs: 3, sm: 5 },
                  mt: { xs: 2, sm: 4 },
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 1,
                    backgroundColor: isValidated ? '#f5f5f5' : '#FFFFFF',
                    '&:hover': {
                      backgroundColor: isValidated ? '#f5f5f5' : '#FFFFFF',
                    },
                    '&.Mui-focused': {
                      backgroundColor: isValidated ? '#f5f5f5' : '#FFFFFF',
                    },
                    height: { xs: '48px', sm: '56px' }
                  },
                  '& .MuiInputLabel-root': {
                    color: isValidated ? '#666666' : '#555',
                    fontWeight: 500,
                    fontSize: { xs: '0.875rem', sm: '1rem' }
                  },
                  '& .MuiInputBase-input': {
                    color: isValidated ? '#666666' : '#000000',
                    fontWeight: 500,
                    cursor: isValidated ? 'not-allowed' : 'text',
                    fontSize: { xs: '0.875rem', sm: '1rem' }
                  },
                }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Key sx={{ 
                        color: isValidated ? '#666666' : '#1967d2', 
                        mr: 1,
                        fontSize: { xs: '1.2rem', sm: '1.5rem' }
                      }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        {apiKey && (
                          <IconButton
                            aria-label="Toggle API key visibility"
                            onClick={handleApiKeyVisibilityToggle}
                            edge="end"
                            size="small"
                            sx={{ p: { xs: 0.3, sm: 0.5 } }}
                          >
                            {showApiKey ? <VisibilityOff sx={{ fontSize: { xs: 16, sm: 18 } }} /> : <Visibility sx={{ fontSize: { xs: 16, sm: 18 } }} />}
                          </IconButton>
                        )}
                        {showApiKey && apiKey && (
                          <Tooltip title="API-Schlüssel kopieren">
                            <IconButton
                              onClick={handleCopyApiKey}
                              size="small"
                              sx={{ 
                                color: '#1967D2', 
                                p: { xs: 0.3, sm: 0.5 }
                              }}
                            >
                              <ContentCopy sx={{ fontSize: { xs: 16, sm: 18 } }} />
                            </IconButton>
                          </Tooltip>
                        )}
                        {isValidated && (
                          <CheckCircle sx={{ 
                            color: '#4CAF50',
                            fontSize: { xs: '1.2rem', sm: '1.5rem' }
                          }} />
                        )}
                      </Box>
                    </InputAdornment>
                  ),
                  readOnly: isValidated
                }}
              />
            </Box>
            
            <Box sx={{ 
              display: 'flex', 
              justifyContent: { xs: 'center', sm: 'flex-start' },
              width: '100%'
            }}>
              <Button
                type="submit"
                variant="contained"
                disabled={isLoading || !apiKey.trim()}
                sx={{
                  px: { xs: 3, sm: 4 },
                  py: { xs: 1.2, sm: 1.5 },
                  backgroundColor: '#1967d2',
                  color: '#FFFFFF',
                  borderRadius: 50,
                  boxShadow: '0 4px 8px 0 rgba(68, 82, 198, 0.2)',
                  minWidth: { xs: '200px', sm: 'auto' },
                  fontSize: { xs: '0.875rem', sm: '1rem' },
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
                    <ArrowForward sx={{ fontSize: { xs: '1.1rem', sm: '1.2rem' } }} />
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
              if (e.key === 'Enter' && !isValidatingPassword) {
                handlePasswordSubmit();
              }
            }}
            disabled={isValidatingPassword}
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
            disabled={isValidatingPassword}
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
            disabled={isValidatingPassword}
            fullWidth={true}
            sx={{ 
              order: { xs: 1, sm: 2 },
              minWidth: { xs: '100%', sm: 'auto' }
            }}
          >
            {isValidatingPassword ? <CircularProgress size={20} sx={{ color: 'white' }} /> : 'Bestätigen'}
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
const ApiKeyStepWithFooter: React.FC<ApiKeyStepProps> = (props) => {
  return (
    <>
      <ApiKeyStep {...props} />
      <Footer />
    </>
  );
};

export default ApiKeyStepWithFooter; 