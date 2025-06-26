import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Snackbar,
  IconButton,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import UserMenu from '../components/UserMenu';
import Logo from '../components/Logo';
import TopBar from '../components/TopBar';
import authService from '../services/authService';
import { Visibility, VisibilityOff, ContentCopy } from '@mui/icons-material';
import analyticsService from '../services/analyticsService';
import { DashboardData, DateRangeData } from '../types';

// Define a more complete business interface
interface BusinessDetails {
  id: string;
  business_name: string;
  email: string;
  phone_number: string;
  is_active: boolean;
  created_at: string;
  whatsapp_number: string;
  customer_id: string;
  timeglobe_auth_key?: string; // Make optional
}

const ProfilePage: React.FC = () => {
  const { isAuthenticated, currentUser } = useAuth();
  const navigate = useNavigate();
  
  const [fetchLoading, setFetchLoading] = useState(true);
  const [businessDetails, setBusinessDetails] = useState<BusinessDetails | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showAuthKey, setShowAuthKey] = useState(false);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [password, setPassword] = useState('');
  const [passwordError, setPasswordError] = useState(false);
  const [passwordErrorMessage, setPasswordErrorMessage] = useState('');
  const [copySuccess, setCopySuccess] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);
  
  // Fetch business profile details
  const fetchBusinessDetails = async () => {
    try {
      setFetchLoading(true);
      const data = await authService.getBusinessProfile();
      // Exclude timeglobe_auth_key from initial fetch as it's fetched separately
      const { timeglobe_auth_key, ...rest } = data; // Destructure to exclude auth key
      setBusinessDetails(rest as BusinessDetails); // Cast back to BusinessDetails
    } catch (err) {
      console.error('Error fetching business details:', err);
      setError('Failed to load business profile');
    } finally {
      setFetchLoading(false);
    }
  };

  // Load user data when component mounts
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    fetchBusinessDetails();
  }, [isAuthenticated, navigate]);

  // Format date string to a more readable format with timezone correction (+2 hours)
  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    // Add 2 hours to correct timezone
    date.setHours(date.getHours() + 2);
    return date.toLocaleDateString('de-DE', {
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Funktion zum Maskieren des Auth-Schlüssels
  const maskAuthKey = (key: string) => {
    if (!key) return '';
    return '*'.repeat(key.length);
  };

  // Handle visibility toggle click
  const handleVisibilityToggle = () => {
    if (showAuthKey) {
      // If already showing, hide it
      setShowAuthKey(false);
    } else {
      // If hidden, open the password dialog
      setPasswordDialogOpen(true);
    }
  };

  // Handle password dialog close
  const handlePasswordDialogClose = () => {
    setPasswordDialogOpen(false);
    setPassword(''); // Clear password on close
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
        // Password is correct, now fetch the auth key
        try {
          const authKeyData = await authService.getTimeglobeAuthKey();
          setBusinessDetails(prevDetails => ({
            ...prevDetails!,
            timeglobe_auth_key: authKeyData.timeglobe_auth_key
          }));
          setShowAuthKey(true);
          handlePasswordDialogClose();
        } catch (authKeyError) {
          console.error('Error fetching Auth Key after password validation:', authKeyError);
          setPasswordError(true); // Indicate error in dialog
          setPasswordErrorMessage('Fehler beim Abrufen des Auth-Schlüssels.');
          // Optionally, close the dialog on a non-recoverable error
          // handlePasswordDialogClose(); 
        }
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

  const handleCopyAuthKey = () => {
    if (businessDetails?.timeglobe_auth_key) {
      navigator.clipboard.writeText(businessDetails.timeglobe_auth_key);
      setCopyFeedback('Auth-Schlüssel kopiert!');
      setTimeout(() => setCopyFeedback(null), 2000);
    }
  };

  // Gemeinsamer Style für alle Textfelder
  const commonTextFieldStyle = {
    '& .MuiInputBase-root': {
      height: { xs: '48px', sm: '56px' }  // Responsive Höhe für mobile Geräte
    },
    '& .MuiInputLabel-root': {
      fontSize: { xs: '0.875rem', sm: '1rem' }
    },
    '& .MuiInputBase-input': {
      fontSize: { xs: '0.875rem', sm: '1rem' }
    }
  };

  if (fetchLoading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: '#FFFFFF',
      pb: 6
    }}>
      <TopBar />

      <Box 
        sx={{ 
          backgroundColor: '#FFFFFF',
          borderBottom: '1px solid #E0E0E0',
          width: '100%'
        }}
      >
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            width: '100%',
            px: { xs: 2, sm: 4 },
            py: 2
          }}
        >
          <Box sx={{ 
            transform: { xs: 'scale(0.8)', sm: 'scale(0.9)' }, 
            ml: { xs: -1, sm: -2 }
          }}>
            <Logo />
          </Box>
          <Box sx={{ mr: { xs: -1, sm: -2 } }}>
            <UserMenu formData={businessDetails ? {
              companyName: businessDetails.business_name,
              email: businessDetails.email
            } : undefined} />
          </Box>
        </Box>
      </Box>

      <Box sx={{ 
        flex: 1, 
        px: { xs: 2, sm: 4 }, 
        maxWidth: 1200, 
        mx: 'auto', 
        width: '100%', 
        py: { xs: 2, sm: 4 } 
      }}>
        <Paper sx={{ 
          p: { xs: 2, sm: 3, md: 4 }, 
          borderRadius: 2, 
          maxWidth: 800, 
          mx: 'auto' 
        }}>
          <Box sx={{ mb: { xs: 3, sm: 4 } }}>
            <Typography 
              variant="h5" 
              sx={{ 
                mb: 2, 
                textAlign: 'left',
                fontSize: { xs: '1.25rem', sm: '1.5rem' }
              }}
            >
              Unternehmensinformationen
            </Typography>
            
            <Box sx={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              bgcolor: '#4CAF50', 
              color: 'white',
              px: { xs: 0.8, sm: 1 },
              py: 0.5,
              fontSize: { xs: '0.75rem', sm: '0.8rem' },
              borderRadius: 1
            }}>
              Aktives Konto
            </Box>
          </Box>

          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { 
              xs: '1fr', 
              sm: '1fr 1fr',
              md: '1fr 1fr'
            }, 
            gap: { xs: 2, sm: 2, md: 3 }
          }}>
            <Box>
              <Typography 
                variant="subtitle2" 
                sx={{ 
                  mb: 1,
                  fontSize: { xs: '0.875rem', sm: '0.875rem' }
                }}
              >
                E-Mail-Adresse
              </Typography>
              <TextField
                fullWidth
                value={businessDetails?.email || ''}
                disabled
                helperText="E-Mail kann nicht geändert werden"
                sx={{
                  ...commonTextFieldStyle,
                  '& .MuiInputBase-root': {
                    height: { xs: '48px', sm: '56px' }
                  },
                  '& .MuiFormHelperText-root': {
                    fontSize: { xs: '0.75rem', sm: '0.75rem' }
                  }
                }}
              />
            </Box>

            <Box>
              <Typography 
                variant="subtitle2" 
                sx={{ 
                  mb: 1,
                  fontSize: { xs: '0.875rem', sm: '0.875rem' }
                }}
              >
                Telefonnummer
              </Typography>
              <TextField
                fullWidth
                value={businessDetails?.phone_number || ''}
                disabled
                sx={{
                  ...commonTextFieldStyle,
                  '& .MuiInputBase-root': {
                    height: { xs: '48px', sm: '56px' }
                  }
                }}
              />
            </Box>

            <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1', md: '1' } }}>
              <Typography 
                variant="subtitle2" 
                sx={{ 
                  mb: 1,
                  fontSize: { xs: '0.875rem', sm: '0.875rem' }
                }}
              >
                WhatsApp-Nummer
              </Typography>
              <TextField
                fullWidth
                value={businessDetails?.whatsapp_number || ''}
                disabled
                sx={{
                  ...commonTextFieldStyle,
                  '& .MuiInputBase-root': {
                    height: { xs: '48px', sm: '56px' }
                  }
                }}
              />
            </Box>
          </Box>

          <Box sx={{ mt: { xs: 2, sm: 3 } }}>
            <Typography 
              variant="subtitle2" 
              sx={{ 
                mb: 1,
                fontSize: { xs: '0.875rem', sm: '0.875rem' }
              }}
            >
              TimeGlobe Auth-Schlüssel
            </Typography>
            <Box sx={{ 
              display: 'flex', 
              gap: { xs: 0.5, sm: 1 },
              alignItems: 'center',
              flexDirection: { xs: 'column', sm: 'row' }
            }}>
              <TextField
                fullWidth
                value={showAuthKey ? businessDetails?.timeglobe_auth_key || '' : maskAuthKey(businessDetails?.timeglobe_auth_key || '')}
                disabled
                sx={{
                  ...commonTextFieldStyle,
                  '& .MuiInputBase-root': {
                    height: { xs: '48px', sm: '56px' },
                    '& .MuiInputAdornment-root': {
                      height: '100%'
                    }
                  }
                }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="Toggle auth key visibility"
                        onClick={handleVisibilityToggle}
                        edge="end"
                        size="small"
                        sx={{ p: { xs: 0.3, sm: 0.5 } }}
                      >
                        {showAuthKey ? <VisibilityOff sx={{ fontSize: { xs: 18, sm: 20 } }} /> : <Visibility sx={{ fontSize: { xs: 18, sm: 20 } }} />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              {showAuthKey && (
                <Tooltip title="Auth-Schlüssel kopieren">
                  <IconButton
                    onClick={handleCopyAuthKey}
                    size="small"
                    sx={{ 
                      color: '#1967D2', 
                      p: { xs: 0.8, sm: 0.5 },
                      alignSelf: { xs: 'center', sm: 'auto' },
                      mt: { xs: 1, sm: 0 }
                    }}
                  >
                    <ContentCopy sx={{ fontSize: { xs: 18, sm: 20 } }} />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Box>

          <Box sx={{ mt: { xs: 3, sm: 4 } }}>
            <Typography 
              variant="h6" 
              sx={{ 
                mb: 2,
                fontSize: { xs: '1.1rem', sm: '1.25rem' }
              }}
            >
              Kontoinformationen
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                mb: 1,
                fontSize: { xs: '0.875rem', sm: '0.875rem' },
                wordBreak: 'break-all'
              }}
            >
              <strong>Business ID:</strong> {businessDetails?.id}
            </Typography>
            <Typography 
              variant="body2"
              sx={{ 
                fontSize: { xs: '0.875rem', sm: '0.875rem' }
              }}
            >
              <strong>Konto erstellt:</strong> {formatDate(businessDetails?.created_at || '')}
            </Typography>
          </Box>

          <Box sx={{ 
            mt: { xs: 3, sm: 4 }, 
            display: 'flex', 
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between', 
            alignItems: { xs: 'stretch', sm: 'center' },
            gap: { xs: 2, sm: 0 }
          }}>
            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{ 
                fontSize: { xs: '0.875rem', sm: '0.875rem' },
                textAlign: { xs: 'center', sm: 'left' }
              }}
            >
              Änderungen können nur im Onboarding vorgenommen werden
            </Typography>
            <Button 
              variant="outlined" 
              color="primary"
              onClick={() => navigate('/onboarding')}
              sx={{ 
                minWidth: { xs: '100%', sm: 'auto' },
                py: { xs: 1.5, sm: 1 },
                fontSize: { xs: '0.875rem', sm: '1rem' }
              }}
            >
              Zum Onboarding
            </Button>
          </Box>

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
                Bitte geben Sie Ihr Passwort ein, um den Auth-Schlüssel anzuzeigen.
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
                {isValidating ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Bestätigen'
                )}
              </Button>
            </DialogActions>
          </Dialog>
        </Paper>
      </Box>
      
      {error && (
        <Snackbar
          open={!!error}
          autoHideDuration={5000}
          onClose={() => setError(null)}
          message={error}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        />
      )}

      <Snackbar
        open={!!copyFeedback}
        message={copyFeedback}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        sx={{
          '& .MuiSnackbarContent-root': {
            bgcolor: '#4CAF50',
            color: 'white'
          }
        }}
      />
    </Box>
  );
};

export default ProfilePage; 