import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Divider,
  Alert,
  CircularProgress,
  Snackbar,
  Stack,
  Chip
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import UserMenu from '../components/UserMenu';
import Logo from '../components/Logo';
import authService from '../services/authService';

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
  const { isAuthenticated, refreshUserData, currentUser } = useAuth();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [businessDetails, setBusinessDetails] = useState<BusinessDetails | null>(null);
  
  const [formData, setFormData] = useState({
    business_name: '',
    email: '',
    phone_number: '',
    timeglobe_auth_key: '',
    whatsapp_number: '',
  });

  // Fetch business profile details
  const fetchBusinessDetails = async () => {
    try {
      setFetchLoading(true);
      const data = await authService.getBusinessProfile();
      
      setBusinessDetails(data);
      setFormData({
        business_name: data.business_name || '',
        email: data.email || '',
        phone_number: data.phone_number || '',
        timeglobe_auth_key: data.timeglobe_auth_key || '',
        whatsapp_number: data.whatsapp_number || '',
      });
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Use the authService to update the profile
      await authService.updateBusinessProfile({
        business_name: formData.business_name,
        phone_number: formData.phone_number,
        timeglobe_auth_key: formData.timeglobe_auth_key,
        whatsapp_number: formData.whatsapp_number
      });
      
      // Refresh business details
      await fetchBusinessDetails();
      await refreshUserData();
      
      setSuccess(true);
      
      // Reset success message after 3 seconds
      setTimeout(() => {
        setSuccess(false);
      }, 3000);
    } catch (err) {
      console.error('Error updating profile:', err);
      setError(err instanceof Error ? err.message : 'Failed to update profile.');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSuccessMessage = () => {
    setSuccess(false);
  };

  // Format date string to a more readable format
  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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
      <Container maxWidth="md" sx={{ flex: 1 }}>
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 6, 
            mt: 5,
          }}
        >
          <Box sx={{ transform: 'scale(1.2)' }}>
            <Logo />
          </Box>
          <UserMenu formData={
            businessDetails ? {
              companyName: businessDetails.business_name,
              email: businessDetails.email
            } : currentUser ? {
              companyName: currentUser.business_name || '',
              email: currentUser.email
            } : undefined
          } />
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
              mb: 3,
              color: '#333333',
            }}
          >
            Business Profile
          </Typography>
          
          {/* Show account status */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
            <Chip 
              label={businessDetails?.is_active ? 'Active Account' : 'Inactive Account'} 
              color={businessDetails?.is_active ? 'success' : 'error'}
              sx={{ fontWeight: 500 }}
            />
          </Box>
          
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          
          <form onSubmit={handleSubmit}>
            <Stack spacing={3}>
              <TextField
                fullWidth
                label="Business Name"
                name="business_name"
                value={formData.business_name}
                onChange={handleChange}
                variant="outlined"
                disabled={loading}
              />
              
              <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
                <TextField
                  fullWidth
                  label="Email Address"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  variant="outlined"
                  disabled
                  helperText="Email cannot be changed"
                />
                
                <TextField
                  fullWidth
                  label="Phone Number"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  variant="outlined"
                  disabled={loading}
                />
              </Stack>
              
              <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
                <TextField
                  fullWidth
                  label="TimeGlobe Auth Key"
                  name="timeglobe_auth_key"
                  value={formData.timeglobe_auth_key}
                  onChange={handleChange}
                  variant="outlined"
                  disabled={loading}
                />
                
                <TextField
                  fullWidth
                  label="WhatsApp Number"
                  name="whatsapp_number"
                  value={formData.whatsapp_number}
                  onChange={handleChange}
                  variant="outlined"
                  disabled={loading}
                  placeholder="Example: +1234567890"
                />
              </Stack>
              
              {/* Display additional read-only information */}
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Account Information
                </Typography>
                <Stack spacing={1} sx={{ pl: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Business ID:</strong> {businessDetails?.id}
                  </Typography>
                  {businessDetails?.customer_id && (
                    <Typography variant="body2" color="text.secondary">
                      <strong>Customer ID:</strong> {businessDetails.customer_id}
                    </Typography>
                  )}
                  {businessDetails?.created_at && (
                    <Typography variant="body2" color="text.secondary">
                      <strong>Account Created:</strong> {formatDate(businessDetails.created_at)}
                    </Typography>
                  )}
                </Stack>
              </Box>
            </Stack>
            
            <Divider sx={{ my: 4 }} />
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                type="submit"
                variant="contained"
                disabled={loading}
                sx={{ 
                  py: 1.5,
                  px: 4,
                  bgcolor: '#1967D2',
                  '&:hover': {
                    bgcolor: '#1756af',
                  },
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Save Changes'}
              </Button>
            </Box>
          </form>
        </Paper>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Button 
            variant="outlined" 
            onClick={() => navigate('/onboarding')}
            sx={{ color: '#1967D2', borderColor: '#1967D2', mr: 2 }}
          >
            Back to Onboarding
          </Button>
          <Button 
            variant="outlined" 
            onClick={() => navigate('/dashboard')}
            sx={{ color: '#1967D2', borderColor: '#1967D2' }}
          >
            View Dashboard
          </Button>
        </Box>
      </Container>
      
      <Snackbar
        open={success}
        autoHideDuration={5000}
        onClose={handleCloseSuccessMessage}
        message="Profile updated successfully!"
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
};

export default ProfilePage; 