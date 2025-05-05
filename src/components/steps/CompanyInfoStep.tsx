import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Box, TextField, Button, Typography, Stack, useTheme, Paper, InputAdornment, CircularProgress, Alert } from '@mui/material';
import { OnboardingFormData } from '../../types';
import Business from '@mui/icons-material/Business';
import LocationOn from '@mui/icons-material/LocationOn';
import Person from '@mui/icons-material/Person';
import Email from '@mui/icons-material/Email';
import Phone from '@mui/icons-material/Phone';
import ArrowBack from '@mui/icons-material/ArrowBack';
import ArrowForward from '@mui/icons-material/ArrowForward';
import authService from '../../services/authService';

interface CompanyInfoStepProps {
  formData: OnboardingFormData;
  onFormChange: (data: Partial<OnboardingFormData>) => void;
  onNext: () => void;
  onBack: () => void;
}

const CompanyInfoStep: React.FC<CompanyInfoStepProps> = ({ formData, onFormChange, onNext, onBack }) => {
  const theme = useTheme();
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [dataFetched, setDataFetched] = useState<boolean>(false);
  
  // Use ref to store the latest onFormChange function
  const onFormChangeRef = useRef(onFormChange);
  
  // Update the ref when onFormChange changes
  useEffect(() => {
    onFormChangeRef.current = onFormChange;
  }, [onFormChange]);
  
  // Fetch business info on component mount only
  useEffect(() => {
    // Skip if data was already fetched
    if (dataFetched) return;
    
    const fetchBusinessInfo = async () => {
      try {
        setIsLoading(true);
        const businessInfo = await authService.getBusinessInfo();
        console.log('Fetched business info:', businessInfo);
        
        // Map backend field names to form field names
        const mappedData: Partial<OnboardingFormData> = {
          companyName: businessInfo.business_name || '',
          vatId: businessInfo.tax_id || '',
          street: businessInfo.street_address || '',
          zipCode: businessInfo.postal_code || '',
          city: businessInfo.city || '',
          country: businessInfo.country || '',
          contactPerson: businessInfo.contact_person || '',
          email: businessInfo.email || '',
          phone: businessInfo.phone_number || ''
        };
        
        // Use the ref to get the latest onFormChange function
        onFormChangeRef.current(mappedData);
        setDataFetched(true);
        setError(null);
      } catch (err) {
        console.error('Error fetching business info:', err);
        // Don't show error message if it's just that no data exists yet
        if (err instanceof Error && !err.message.includes('No authentication token found')) {
          setError('Fehler beim Laden der Unternehmensinformationen. Bitte versuchen Sie es später erneut.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchBusinessInfo();
  }, []); // Empty dependency array means it runs only once on mount

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    onFormChange({ [name]: value });
    // Clear any success/error messages when user starts editing
    setSuccess(null);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setIsSaving(true);
      setError(null);
      
      // Map form field names to backend field names
      const businessInfoData = {
        business_name: formData.companyName,
        tax_id: formData.vatId,
        street_address: formData.street,
        postal_code: formData.zipCode,
        city: formData.city,
        country: formData.country,
        contact_person: formData.contactPerson,
        email: formData.email,
        phone_number: formData.phone
      };
      
      await authService.updateBusinessInfo(businessInfoData);
      setSuccess('Unternehmensdaten erfolgreich gespeichert.');
      
      // Proceed to next step
      setTimeout(() => {
        onNext();
      }, 1000);
    } catch (err) {
      console.error('Error updating business info:', err);
      setError('Fehler beim Speichern der Unternehmensinformationen. Bitte versuchen Sie es später erneut.');
    } finally {
      setIsSaving(false);
    }
  };

  // Gemeinsame Stil-Eigenschaften für alle Textfelder
  const textFieldStyles = {
    '& .MuiOutlinedInput-root': {
      borderRadius: 2,
      backgroundColor: '#FFFFFF',
      '&:hover': {
        backgroundColor: '#FFFFFF',
      },
      '&.Mui-focused': {
        backgroundColor: '#FFFFFF',
      }
    },
    '& .MuiInputBase-input': {
      color: '#000000',
      '&:-webkit-autofill': {
        WebkitBoxShadow: '0 0 0 1000px white inset',
        WebkitTextFillColor: '#000000',
        transition: 'background-color 5000s ease-in-out 0s'
      },
      '&:autofill': {
        background: 'none !important',
        backgroundColor: '#FFFFFF !important'
      },
      '&::selection': {
        background: 'rgba(25, 103, 210, 0.2)'
      }
    },
    '& .MuiFormLabel-root': {
      color: '#666666',
    },
    '& .MuiInputLabel-root.Mui-focused': {
      color: '#1967D2',
    },
    '& .MuiOutlinedInput-notchedOutline': {
      borderColor: 'rgba(0, 0, 0, 0.2)',
    },
    '& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline': {
      borderColor: '#1967D2',
    },
    '& .MuiFormLabel-root.Mui-disabled': {
      color: 'rgba(0, 0, 0, 0.38)',
    },
    '& .MuiInputBase-input.Mui-disabled': {
      color: 'rgba(0, 0, 0, 0.6)',
    },
    '& .MuiInputBase-input::placeholder': {
      color: '#000000',
      opacity: 0.5,
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3, pb: 8 }}>
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 4,
          borderRadius: 3,
          backgroundColor: '#FFFFFF',
          border: '1px solid #E0E0E0',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)'
        }}
      >
        {success && (
          <Alert 
            severity="success" 
            sx={{ 
              mb: 3, 
              borderRadius: 2,
              backgroundColor: 'rgba(76, 175, 80, 0.1)', 
              color: '#4caf50',
              '& .MuiAlert-icon': {
                color: '#4caf50'
              }
            }}
          >
            {success}
          </Alert>
        )}
        
        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3, 
              borderRadius: 2,
              backgroundColor: 'rgba(211, 47, 47, 0.1)', 
              color: '#ff6b6b',
              '& .MuiAlert-icon': {
                color: '#ff6b6b'
              }
            }}
          >
            {error}
          </Alert>
        )}
      
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
          <Business sx={{ mr: 1, opacity: 0.9, color: '#1967D2' }} />
          Unternehmensinformationen
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, ml: 0.5 }}>
          Bitte geben Sie die Informationen zu Ihrem Unternehmen ein.
        </Typography>
        
        <Stack spacing={3}>
          <TextField
            fullWidth
            name="companyName"
            label="Unternehmensname"
            value={formData.companyName}
            onChange={handleInputChange}
            required
            sx={textFieldStyles}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Business sx={{ color: '#1967D2' }} />
                </InputAdornment>
              ),
              sx: {
                backgroundColor: 'transparent !important',
                '& input': {
                  backgroundColor: 'transparent !important',
                }
              }
            }}
          />
          
          <TextField
            fullWidth
            name="vatId"
            label="Umsatzsteuer-ID"
            value={formData.vatId || ''}
            onChange={handleInputChange}
            required
            sx={textFieldStyles}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Business sx={{ color: '#1967D2' }} />
                </InputAdornment>
              ),
              sx: {
                backgroundColor: 'transparent !important',
                '& input': {
                  backgroundColor: 'transparent !important',
                }
              }
            }}
          />
          
          <TextField
            fullWidth
            name="street"
            label="Straße und Hausnummer"
            value={formData.street}
            onChange={handleInputChange}
            required
            sx={textFieldStyles}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <LocationOn sx={{ color: '#1967D2' }} />
                </InputAdornment>
              ),
              sx: {
                backgroundColor: 'transparent !important',
                '& input': {
                  backgroundColor: 'transparent !important',
                }
              }
            }}
          />
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              name="zipCode"
              label="Postleitzahl"
              value={formData.zipCode}
              onChange={handleInputChange}
              required
              sx={textFieldStyles}
              InputProps={{
                sx: {
                  backgroundColor: 'transparent !important',
                  '& input': {
                    backgroundColor: 'transparent !important',
                  }
                }
              }}
            />
            
            <TextField
              fullWidth
              name="city"
              label="Stadt"
              value={formData.city}
              onChange={handleInputChange}
              required
              sx={textFieldStyles}
              InputProps={{
                sx: {
                  backgroundColor: 'transparent !important',
                  '& input': {
                    backgroundColor: 'transparent !important',
                  }
                }
              }}
            />
          </Box>
          
          <TextField
            fullWidth
            name="country"
            label="Land"
            value={formData.country}
            onChange={handleInputChange}
            required
            sx={textFieldStyles}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <LocationOn sx={{ color: '#1967D2' }} />
                </InputAdornment>
              ),
              sx: {
                backgroundColor: 'transparent !important',
                '& input': {
                  backgroundColor: 'transparent !important',
                }
              }
            }}
          />
          
          <TextField
            fullWidth
            name="contactPerson"
            label="Ansprechpartner"
            value={formData.contactPerson}
            onChange={handleInputChange}
            required
            sx={textFieldStyles}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Person sx={{ color: '#1967D2' }} />
                </InputAdornment>
              ),
              sx: {
                backgroundColor: 'transparent !important',
                '& input': {
                  backgroundColor: 'transparent !important',
                }
              }
            }}
          />
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              name="email"
              label="E-Mail"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              sx={textFieldStyles}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email sx={{ color: '#1967D2' }} />
                  </InputAdornment>
                ),
                sx: {
                  backgroundColor: 'transparent !important',
                  '& input': {
                    backgroundColor: 'transparent !important',
                  }
                }
              }}
            />
            
            <TextField
              fullWidth
              name="phone"
              label="Telefon"
              value={formData.phone}
              onChange={handleInputChange}
              required
              sx={textFieldStyles}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Phone sx={{ color: '#1967D2' }} />
                  </InputAdornment>
                ),
                sx: {
                  backgroundColor: 'transparent !important',
                  '& input': {
                    backgroundColor: 'transparent !important',
                  }
                }
              }}
            />
          </Box>
        </Stack>
      </Paper>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button
          variant="outlined"
          color="primary"
          size="large"
          onClick={onBack}
          startIcon={<ArrowBack />}
          disabled={isLoading || isSaving}
          sx={{
            px: 4,
            py: 1.5,
            borderRadius: 3,
            borderColor: '#1967D2',
            color: '#1967D2',
            '&:hover': {
              borderColor: '#1967D2',
              backgroundColor: 'rgba(25, 103, 210, 0.05)',
            }
          }}
        >
          Zurück
        </Button>
        <Button
          type="submit"
          variant="contained"
          color="primary"
          size="large"
          disabled={isLoading || isSaving}
          endIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : <ArrowForward />}
          sx={{ 
            px: 4, 
            py: 1.5,
            borderRadius: 3,
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
            backgroundColor: '#1967D2',
            '&:hover': {
              boxShadow: '0 6px 20px rgba(0,0,0,0.3)',
              backgroundColor: '#1756B0',
            }
          }}
        >
          {isSaving ? 'Speichern...' : 'Weiter'}
        </Button>
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
      width: '100%',
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center',
      py: 1,
      backgroundColor: '#FFFFFF',
      opacity: 1,
      zIndex: 10
    }}
  >
    <Typography 
      variant="body2" 
      sx={{ 
        color: '#000000',
        mr: 1,
        fontSize: '0.85rem'
      }}
    >
      powered by
    </Typography>
    <img 
      src="/images/EcomTask_logo.svg" 
      alt="EcomTask Logo" 
      style={{ height: '36px' }} 
    />
  </Box>
);

// Die gesamte App-Komponente mit Hauptinhalt und Footer
const CompanyInfoStepWithFooter: React.FC<CompanyInfoStepProps> = (props) => {
  return (
    <>
      <CompanyInfoStep {...props} />
      <Footer />
    </>
  );
};

export default CompanyInfoStepWithFooter; 