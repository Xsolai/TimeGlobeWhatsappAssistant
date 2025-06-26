import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  Link,
  InputAdornment,
  IconButton,
  Alert,
  CircularProgress,
  Snackbar
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import Logo from '../components/Logo';
import { useAuth } from '../contexts/AuthContext';
import authService from '../services/authService';

interface LocationState {
  from?: {
    pathname: string;
  };
  registrationSuccess?: boolean;
}

const LoginPage: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const locationState = location.state as LocationState;
  const from = locationState?.from?.pathname || '/onboarding';
  
  // Check if redirected from successful registration
  useEffect(() => {
    if (locationState?.registrationSuccess) {
      setShowSuccessMessage(true);
    }
  }, [locationState]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    
    if (!formData.email || !formData.password) {
      setError('Bitte füllen Sie alle Felder aus');
      return;
    }

    try {
      setLoading(true);
      const success = await login(formData.email, formData.password);
      
      if (success) {
        // Nach erfolgreichem Login das Benutzerprofil abrufen
        try {
          const userProfile = await authService.getBusinessProfile();
          // Wenn WhatsApp-Nummer vorhanden ist, zum Dashboard weiterleiten
          if (userProfile.whatsapp_number) {
            navigate('/dashboard', { replace: true });
          } else {
            // Wenn keine WhatsApp-Nummer vorhanden ist, zum Onboarding weiterleiten
            navigate('/onboarding', { replace: true });
          }
        } catch (err) {
          console.error('Error fetching user profile:', err);
          navigate('/onboarding', { replace: true });
        }
      } else {
        setError('Ungültige E-Mail oder Passwort');
      }
    } catch (err) {
      setError('Ein Fehler ist während des Anmeldevorgangs aufgetreten');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClickShowPassword = () => {
    setShowPassword(show => !show);
  };

  const handleCloseSnackbar = () => {
    setShowSuccessMessage(false);
  };

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: '#FFFFFF',
      pb: 6
    }}>
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
        </Box>
      </Box>

      <Container maxWidth="sm" sx={{ flex: 1, mt: 8 }}>
        <Paper 
          elevation={2} 
          sx={{ 
            p: 4, 
            mb: 4,
            borderRadius: 3,
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
            backgroundColor: '#FFFFFF',
            border: '1px solid #F0F0F0',
          }}
        >
          <Typography 
            variant="h4" 
            align="center" 
            gutterBottom
            sx={{ 
              fontWeight: 'bold',
              mb: 3,
              color: '#333333',
            }}
          >
            Willkommen <span style={{ fontWeight: 'normal' }}>zurück</span>
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="E-Mail-Adresse"
              name="email"
              autoComplete="email"
              value={formData.email}
              onChange={handleChange}
              sx={{ 
                mb: 2,
                '& .MuiOutlinedInput-root': {
                  backgroundColor: '#F8FAFC',
                  '& fieldset': {
                    borderColor: '#E2E8F0',
                  },
                  '&:hover fieldset': {
                    borderColor: '#CBD5E1',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#1967D2',
                  }
                },
                '& .MuiInputLabel-root': {
                  color: '#64748B',
                  '&.Mui-focused': {
                    color: '#1967D2',
                  }
                },
                '& input': {
                  padding: '16px 14px',
                  '&::placeholder': {
                    color: '#94A3B8',
                    opacity: 1,
                  }
                }
              }}
              variant="outlined"
              disabled={loading}
              InputLabelProps={{
                shrink: true,
              }}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Passwort"
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="Passwort anzeigen"
                      onClick={handleClickShowPassword}
                      edge="end"
                      disabled={loading}
                      sx={{
                        color: '#64748B',
                        '&:hover': {
                          color: '#1967D2',
                        }
                      }}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
              sx={{ 
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  backgroundColor: '#F8FAFC',
                  '& fieldset': {
                    borderColor: '#E2E8F0',
                  },
                  '&:hover fieldset': {
                    borderColor: '#CBD5E1',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#1967D2',
                  }
                },
                '& .MuiInputLabel-root': {
                  color: '#64748B',
                  '&.Mui-focused': {
                    color: '#1967D2',
                  }
                },
                '& input': {
                  padding: '16px 14px',
                  '&::placeholder': {
                    color: '#94A3B8',
                    opacity: 1,
                  }
                }
              }}
              variant="outlined"
              disabled={loading}
              InputLabelProps={{
                shrink: true,
              }}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ 
                mt: 2, 
                mb: 3,
                py: 1.5,
                bgcolor: '#1967D2',
                fontSize: '1rem',
                textTransform: 'none',
                boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                '&:hover': {
                  bgcolor: '#1756af',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                },
              }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Anmelden'}
            </Button>
            
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              '& a': {
                color: '#1967D2',
                textDecoration: 'none',
                fontSize: '0.875rem',
                '&:hover': {
                  textDecoration: 'underline',
                }
              }
            }}>
              <Link component={RouterLink} to="/forgot-password">
                Passwort vergessen?
              </Link>
              <Link component={RouterLink} to="/signup">
                Noch kein Konto? Jetzt registrieren
              </Link>
            </Box>
          </Box>
        </Paper>
        
        <Snackbar
          open={showSuccessMessage}
          autoHideDuration={6000}
          onClose={handleCloseSnackbar}
          message="Registrierung erfolgreich! Bitte melden Sie sich mit Ihren Zugangsdaten an."
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        />
      </Container>

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
    </Box>
  );
};

export default LoginPage; 