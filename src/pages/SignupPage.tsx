import React, { useState } from 'react';
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
  Divider,
  Checkbox,
  FormControlLabel,
  Alert,
  CircularProgress,
  Stack,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import Logo from '../components/Logo';
import { useAuth } from '../contexts/AuthContext';

enum SignupStep {
  REGISTRATION = 0,
  OTP_VERIFICATION = 1
}

const SignupPage: React.FC = () => {
  // Form states
  const [formData, setFormData] = useState({
    businessName: '',
    email: '',
    phoneNumber: '',
    password: '',
    confirmPassword: '',
    acceptTerms: false
  });
  
  // Password visibility states
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  // UI states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState<SignupStep>(SignupStep.REGISTRATION);
  const [otp, setOtp] = useState('');
  
  const { signup, verifyOtp, resendOtp } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'acceptTerms' ? checked : value
    }));
  };

  const handleOtpChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOtp(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    
    // Validate inputs
    if (!formData.businessName || !formData.email || !formData.phoneNumber || !formData.password) {
      setError('Bitte füllen Sie alle erforderlichen Felder aus');
      return;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Die Passwörter stimmen nicht überein');
      return;
    }
    
    if (!formData.acceptTerms) {
      setError('Bitte akzeptieren Sie die Nutzungsbedingungen');
      return;
    }

    try {
      setLoading(true);
      const success = await signup(
        formData.businessName,
        formData.email,
        formData.phoneNumber,
        formData.password
      );
      
      if (success) {
        setActiveStep(SignupStep.OTP_VERIFICATION);
      } else {
        setError('Konto konnte nicht erstellt werden');
      }
    } catch (err) {
      setError('Ein Fehler ist während der Registrierung aufgetreten');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOtpSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    
    if (!otp) {
      setError('Please enter the OTP sent to your email');
      return;
    }

    try {
      setLoading(true);
      const success = await verifyOtp(formData.email, otp);
      
      if (success) {
        navigate('/login', { state: { registrationSuccess: true } });
      } else {
        setError('Invalid OTP. Please try again');
      }
    } catch (err) {
      setError('An error occurred during OTP verification');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    try {
      setLoading(true);
      await resendOtp(formData.email);
      setError(null);
    } catch (err) {
      setError('Failed to resend OTP');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClickShowPassword = () => {
    setShowPassword(show => !show);
  };

  const handleClickShowConfirmPassword = () => {
    setShowConfirmPassword(show => !show);
  };

  const renderSignupForm = () => (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <TextField
        margin="normal"
        required
        fullWidth
        id="businessName"
        label="Firmenname"
        name="businessName"
        autoComplete="organization"
        value={formData.businessName}
        onChange={handleChange}
        sx={{ mb: 2 }}
        disabled={loading}
      />
      
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 2 }}>
        <TextField
          required
          fullWidth
          id="email"
          label="E-Mail-Adresse"
          name="email"
          autoComplete="email"
          value={formData.email}
          onChange={handleChange}
          disabled={loading}
        />
        <TextField
          required
          fullWidth
          id="phoneNumber"
          label="Telefonnummer"
          name="phoneNumber"
          autoComplete="tel"
          value={formData.phoneNumber}
          onChange={handleChange}
          disabled={loading}
        />
      </Stack>
      
      <TextField
        margin="normal"
        required
        fullWidth
        name="password"
        label="Passwort"
        type={showPassword ? 'text' : 'password'}
        id="password"
        autoComplete="new-password"
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
              >
                {showPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          )
        }}
        sx={{ mb: 2 }}
        disabled={loading}
      />

      <TextField
        margin="normal"
        required
        fullWidth
        name="confirmPassword"
        label="Passwort bestätigen"
        type={showConfirmPassword ? 'text' : 'password'}
        id="confirmPassword"
        autoComplete="new-password"
        value={formData.confirmPassword}
        onChange={handleChange}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                aria-label="Passwort bestätigen anzeigen"
                onClick={handleClickShowConfirmPassword}
                edge="end"
                disabled={loading}
              >
                {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          )
        }}
        sx={{ mb: 2 }}
        disabled={loading}
      />

      <FormControlLabel
        control={
          <Checkbox 
            checked={formData.acceptTerms} 
            onChange={handleChange} 
            name="acceptTerms" 
            color="primary"
            disabled={loading}
          />
        }
        label={
          <Box component="span" sx={{ fontSize: '0.875rem' }}>
            Ich stimme den <Link component={RouterLink} to="/terms" sx={{ color: '#1967D2' }}>Nutzungsbedingungen</Link> und der <Link component={RouterLink} to="/privacy" sx={{ color: '#1967D2' }}>Datenschutzerklärung</Link> zu
          </Box>
        }
        sx={{ mt: 1 }}
      />
      
      <Button
        type="submit"
        fullWidth
        variant="contained"
        disabled={loading}
        sx={{ 
          mt: 3, 
          mb: 3,
          py: 1.5,
          bgcolor: '#1967D2',
          '&:hover': {
            bgcolor: '#1756af',
          },
        }}
      >
        {loading ? <CircularProgress size={24} color="inherit" /> : 'Registrieren'}
      </Button>
      
      <Divider sx={{ my: 2 }} />
      
      <Box sx={{ textAlign: 'center' }}>
        <Link component={RouterLink} to="/login" variant="body2" sx={{ color: '#1967D2' }}>
          Bereits ein Konto? Jetzt anmelden
        </Link>
      </Box>
    </Box>
  );

  const renderOtpVerification = () => (
    <Box component="form" onSubmit={handleOtpSubmit} sx={{ mt: 2 }}>
      <Typography variant="body1" sx={{ mb: 2, textAlign: 'center' }}>
        Wir haben einen Bestätigungscode an <strong>{formData.email}</strong> gesendet. 
        Bitte geben Sie den Code unten ein, um Ihr Konto zu verifizieren.
      </Typography>
      
      <TextField
        margin="normal"
        required
        fullWidth
        id="otp"
        label="Bestätigungscode"
        name="otp"
        value={otp}
        onChange={handleOtpChange}
        sx={{ mb: 3 }}
        disabled={loading}
        inputProps={{ maxLength: 6 }}
      />
      
      <Button
        type="submit"
        fullWidth
        variant="contained"
        disabled={loading}
        sx={{ 
          mb: 2,
          py: 1.5,
          bgcolor: '#1967D2',
          '&:hover': {
            bgcolor: '#1756af',
          },
        }}
      >
        {loading ? <CircularProgress size={24} color="inherit" /> : 'Bestätigen'}
      </Button>
      
      <Box sx={{ textAlign: 'center', mb: 2 }}>
        <Link 
          component="button"
          variant="body2"
          onClick={handleResendOtp}
          disabled={loading}
          sx={{ 
            color: '#1967D2',
            textDecoration: 'none',
            border: 'none',
            background: 'none',
            cursor: 'pointer',
            '&:disabled': {
              color: 'text.disabled',
              cursor: 'default',
            }
          }}
        >
          Keinen Code erhalten? Erneut senden
        </Link>
      </Box>
      
      <Divider sx={{ my: 2 }} />
      
      <Box sx={{ textAlign: 'center' }}>
        <Link 
          component="button" 
          variant="body2" 
          onClick={() => setActiveStep(SignupStep.REGISTRATION)}
          sx={{ color: '#1967D2', textDecoration: 'none', border: 'none', background: 'none', cursor: 'pointer' }}
        >
          Zurück zur Registrierung
        </Link>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: '#FFFFFF',
      pb: 6
    }}>
      <Container maxWidth="sm" sx={{ flex: 1 }}>
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'center',
            mb: 4, 
            mt: 5,
            transform: 'scale(1.2)'
          }}
        >
          <Logo />
        </Box>
        
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          <Step>
            <StepLabel>Registrierung</StepLabel>
          </Step>
          <Step>
            <StepLabel>Verifizierung</StepLabel>
          </Step>
        </Stepper>
        
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
            {activeStep === SignupStep.REGISTRATION 
              ? <><span>Registrierung</span> <span style={{ fontWeight: 'normal' }}>für ein neues Konto</span></>
              : <><span>Bestätigen</span> <span style={{ fontWeight: 'normal' }}>Sie Ihr Konto</span></>
            }
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {activeStep === SignupStep.REGISTRATION 
            ? renderSignupForm() 
            : renderOtpVerification()
          }
        </Paper>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Link component={RouterLink} to="/onboarding" variant="body2" sx={{ color: '#666' }}>
            Onboarding fortsetzen
          </Link>
        </Box>
      </Container>
    </Box>
  );
};

export default SignupPage; 