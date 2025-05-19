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
  timeglobe_auth_key: string;
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
      setBusinessDetails(data);
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

  // Format date string to a more readable format
  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
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
    return '•'.repeat(key.length);
  };

  const handlePasswordSubmit = async () => {
    if (password.trim() === '') {
      setPasswordError(true);
      setPasswordErrorMessage('Bitte geben Sie Ihr Passwort ein');
      return;
    }

    setIsValidating(true);
    try {
      const isValid = await authService.validatePassword(password);
      if (isValid) {
        setShowAuthKey(true);
        setPasswordDialogOpen(false);
        setPassword('');
        setPasswordError(false);
        setPasswordErrorMessage('');
      } else {
        setPasswordError(true);
        setPasswordErrorMessage('Falsches Passwort');
      }
    } catch (error) {
      setPasswordError(true);
      setPasswordErrorMessage('Fehler bei der Validierung. Bitte versuchen Sie es erneut.');
    } finally {
      setIsValidating(false);
    }
  };

  const handleCopy = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopyFeedback(`${type} wurde kopiert`);
    setTimeout(() => setCopyFeedback(null), 2000);
  };

  const handleVisibilityToggle = () => {
    if (!showAuthKey) {
      setPasswordDialogOpen(true);
    } else {
      setShowAuthKey(false);
    }
  };

  // Gemeinsamer Style für alle Textfelder
  const commonTextFieldStyle = {
    '& .MuiInputBase-root': {
      height: '56px'  // Standard MUI TextField Höhe
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
            px: 4,
            py: 2
          }}
        >
          <Box sx={{ transform: 'scale(0.9)', ml: -2 }}>
            <Logo />
          </Box>
          <Box sx={{ mr: -2 }}>
            <UserMenu formData={businessDetails ? {
              companyName: businessDetails.business_name,
              email: businessDetails.email
            } : undefined} />
          </Box>
        </Box>
      </Box>

      <Box sx={{ flex: 1, px: 4, maxWidth: 1200, mx: 'auto', width: '100%', py: 4 }}>
        <Paper sx={{ p: 4, borderRadius: 2, maxWidth: 800, mx: 'auto' }}>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h5" sx={{ mb: 2, textAlign: 'left' }}>
              Unternehmensinformationen
            </Typography>
            
            <Box sx={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              bgcolor: '#4CAF50', 
              color: 'white',
              px: 1,
              py: 0.5,
              fontSize: '0.8rem',
              borderRadius: 1
            }}>
              Aktives Konto
            </Box>
          </Box>

          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}>
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                E-Mail-Adresse
              </Typography>
              <TextField
                fullWidth
                value={businessDetails?.email || ''}
                disabled
                helperText="E-Mail kann nicht geändert werden"
                sx={commonTextFieldStyle}
              />
            </Box>

            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Telefonnummer
              </Typography>
              <TextField
                fullWidth
                value={businessDetails?.phone_number || ''}
                disabled
                sx={commonTextFieldStyle}
              />
            </Box>

            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                WhatsApp-Nummer
              </Typography>
              <TextField
                fullWidth
                value={businessDetails?.whatsapp_number || ''}
                disabled
                sx={commonTextFieldStyle}
              />
            </Box>
          </Box>

          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              TimeGlobe Auth-Schlüssel
            </Typography>
            <Box sx={{ 
              display: 'flex', 
              gap: 1,
              alignItems: 'center'
            }}>
              <TextField
                fullWidth
                value={showAuthKey ? businessDetails?.timeglobe_auth_key || '' : maskAuthKey(businessDetails?.timeglobe_auth_key || '')}
                disabled
                sx={{
                  ...commonTextFieldStyle,
                  '& .MuiInputBase-root': {
                    height: '56px',
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
                        sx={{ p: 0.5 }}
                      >
                        {showAuthKey ? <VisibilityOff sx={{ fontSize: 20 }} /> : <Visibility sx={{ fontSize: 20 }} />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
          </Box>

          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Kontoinformationen
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Business ID:</strong> {businessDetails?.id}
            </Typography>
            <Typography variant="body2">
              <strong>Konto erstellt:</strong> {formatDate(businessDetails?.created_at || '')}
            </Typography>
          </Box>

          <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Änderungen können nur im Onboarding vorgenommen werden
            </Typography>
            <Button 
              variant="outlined" 
              color="primary"
              onClick={() => navigate('/onboarding')}
            >
              Zum Onboarding
            </Button>
          </Box>

          <Dialog open={passwordDialogOpen} onClose={() => {
            setPasswordDialogOpen(false);
            setPassword('');
            setPasswordError(false);
            setPasswordErrorMessage('');
          }}>
            <DialogTitle>Passwort erforderlich</DialogTitle>
            <DialogContent>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Bitte geben Sie Ihr Passwort ein, um den Auth-Schlüssel anzuzeigen.
              </Typography>
              <TextField
                autoFocus
                margin="dense"
                label="Passwort"
                type="password"
                fullWidth
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setPasswordError(false);
                  setPasswordErrorMessage('');
                }}
                error={passwordError}
                helperText={passwordErrorMessage}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !isValidating) {
                    handlePasswordSubmit();
                  }
                }}
                disabled={isValidating}
              />
            </DialogContent>
            <DialogActions>
              <Button 
                onClick={() => {
                  setPasswordDialogOpen(false);
                  setPassword('');
                  setPasswordError(false);
                  setPasswordErrorMessage('');
                }}
                disabled={isValidating}
              >
                Abbrechen
              </Button>
              <Button 
                onClick={handlePasswordSubmit} 
                variant="contained"
                disabled={isValidating}
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