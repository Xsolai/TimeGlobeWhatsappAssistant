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
  Alert,
  CircularProgress
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { Link as RouterLink, useNavigate, useParams } from 'react-router-dom';
import Logo from '../components/Logo';
import { useAuth } from '../contexts/AuthContext';

const ResetPasswordPage: React.FC = () => {
  const [formData, setFormData] = useState({
    businessId: '',
    token: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  const { resetPassword } = useAuth();
  const navigate = useNavigate();
  const { businessId, token } = useParams();
  
  // Get business ID and token from URL params
  React.useEffect(() => {
    if (businessId && token) {
      setFormData(prev => ({ 
        ...prev, 
        businessId,
        token 
      }));
    }
  }, [businessId, token]);

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
    
    if (!formData.businessId || !formData.token || !formData.newPassword) {
      setError('Please fill in all required fields');
      return;
    }
    
    if (formData.newPassword !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      setLoading(true);
      const result = await resetPassword(formData.businessId, formData.token, formData.newPassword);
      
      if (result) {
        setSuccess(true);
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else {
        setError('Failed to reset password. The token may be invalid or expired.');
      }
    } catch (err) {
      setError('An error occurred during password reset');
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
            Reset Your Password
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {success ? (
            <Alert severity="success" sx={{ mb: 2 }}>
              Password has been successfully reset! You will be redirected to the login page.
            </Alert>
          ) : (
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
              <TextField
                margin="normal"
                required
                fullWidth
                name="newPassword"
                label="New Password"
                type={showPassword ? 'text' : 'password'}
                id="newPassword"
                value={formData.newPassword}
                onChange={handleChange}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle password visibility"
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
                label="Confirm New Password"
                type={showConfirmPassword ? 'text' : 'password'}
                id="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle confirm password visibility"
                        onClick={handleClickShowConfirmPassword}
                        edge="end"
                        disabled={loading}
                      >
                        {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  )
                }}
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
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Reset Password'}
              </Button>
            </Box>
          )}
          
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Link component={RouterLink} to="/login" variant="body2" sx={{ color: '#1967D2' }}>
              Back to Login
            </Link>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default ResetPasswordPage; 