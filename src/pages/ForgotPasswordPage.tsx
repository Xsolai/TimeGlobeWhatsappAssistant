import React, { useState } from 'react';
import { 
  Box, 
  Container, 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  Link,
  Alert,
  CircularProgress
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import Logo from '../components/Logo';
import { useAuth } from '../contexts/AuthContext';

const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const { forgotPassword } = useAuth();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    
    if (!email) {
      setError('Bitte geben Sie Ihre E-Mail-Adresse ein');
      return;
    }

    try {
      setLoading(true);
      const result = await forgotPassword(email);
      
      if (result) {
        setSuccess(true);
      } else {
        setError('Link zum Zurücksetzen konnte nicht gesendet werden. Bitte überprüfen Sie Ihre E-Mail-Adresse.');
      }
    } catch (err) {
      setError('Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

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
            mb: 6, 
            mt: 5,
            transform: 'scale(1.2)'
          }}
        >
          <Logo />
        </Box>
        
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
              mb: 2,
              color: '#333333',
            }}
          >
            Passwort zurücksetzen
          </Typography>
          
          <Typography 
            variant="body1" 
            align="center" 
            sx={{ mb: 3, color: '#666' }}
          >
            Geben Sie Ihre E-Mail-Adresse ein und wir senden Ihnen Anweisungen zum Zurücksetzen Ihres Passworts.
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {success ? (
            <Alert severity="success" sx={{ mb: 2 }}>
              Der Link zum Zurücksetzen wurde an Ihre E-Mail-Adresse gesendet. Bitte prüfen Sie Ihren Posteingang für den OTP-Code.
            </Alert>
          ) : (
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="E-Mail-Adresse"
                name="email"
                autoComplete="email"
                value={email}
                onChange={handleChange}
                sx={{ mb: 3 }}
                disabled={loading}
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
                  '&:hover': {
                    bgcolor: '#1756af',
                  },
                }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Link zum Zurücksetzen senden'}
              </Button>
            </Box>
          )}
          
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Link component={RouterLink} to="/login" variant="body2" sx={{ color: '#1967D2' }}>
              Zurück zur Anmeldung
            </Link>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default ForgotPasswordPage; 