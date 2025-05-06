import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, Typography, Paper, List, ListItem, ListItemText, Divider, useTheme, 
  Snackbar, Alert, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import { OnboardingFormData } from '../../types';
import DoneAll from '@mui/icons-material/DoneAll';
import ArrowBack from '@mui/icons-material/ArrowBack';
import VpnKey from '@mui/icons-material/VpnKey';
import Business from '@mui/icons-material/Business';
import Person from '@mui/icons-material/Person';
import Email from '@mui/icons-material/Email';
import Phone from '@mui/icons-material/Phone';
import CheckCircle from '@mui/icons-material/CheckCircle';
import WhatsApp from '@mui/icons-material/WhatsApp';

interface ConfirmationStepProps {
  formData: OnboardingFormData;
  onBack: () => void;
}

const ConfirmationStep: React.FC<ConfirmationStepProps> = ({ formData, onBack }) => {
  const theme = useTheme();
  const [openSuccessDialog, setOpenSuccessDialog] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'connecting' | 'success' | 'error'>('idle');
  const popupWindowRef = useRef<Window | null>(null);
  const popupCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // 360dialog onboarding URL configuration
  const PARTNER_ID = "MalHtRPA";
  const REDIRECT_URL = "https://timeglobe-server.ecomtask.de/redirect";
  const base_url = `https://hub.360dialog.com/dashboard/app/${PARTNER_ID}/permissions`;
  
  // Query parameters
  const query_params = new URLSearchParams({
    redirect_url: REDIRECT_URL,
    plan_selection: "regular"
  });
  
  // Final onboarding URL
  const onboarding_url = `${base_url}?${query_params.toString()}`;
  
  // Set up a listener for messages from the redirect page
  useEffect(() => {
    // Function to handle messages from the popup window
    const handleMessage = (event: MessageEvent) => {
      // Verify origin for security - replace with your actual domain
      if (event.origin !== "https://solasolution.ecomtask.de") return;
      
      // Check the message content
      if (event.data && event.data.type === 'whatsapp_connection') {
        if (event.data.status === 'success') {
          setConnectionStatus('success');
          setOpenSuccessDialog(true);
        } else if (event.data.status === 'error') {
          setConnectionStatus('error');
        }
      }
    };

    // Add event listener for messages
    window.addEventListener('message', handleMessage);
    
    // Clean up the event listener when component unmounts
    return () => {
      window.removeEventListener('message', handleMessage);
      // Also clear any active intervals
      if (popupCheckIntervalRef.current) {
        clearInterval(popupCheckIntervalRef.current);
      }
    };
  }, []);

  // Handle popup window for WhatsApp connection
  const handleWhatsAppConnect = () => {
    setConnectionStatus('connecting');
    
    // Open the 360dialog onboarding URL in a new tab or popup window
    const popupWindow = window.open(onboarding_url, 'WhatsAppConnection', 
      'width=1000,height=800,left=100,top=100');
    
    // Check if popup was blocked
    if (!popupWindow || popupWindow.closed || typeof popupWindow.closed === 'undefined') {
      alert('Popup wurde blockiert. Bitte erlauben Sie Popups für diese Website.');
      setConnectionStatus('idle');
      return;
    }

    // Store the popup reference
    popupWindowRef.current = popupWindow;
    
    // Set up an interval to check if the popup window was closed
    popupCheckIntervalRef.current = setInterval(() => {
      if (popupWindow.closed) {
        // If popup closed, consider it a successful connection
        clearInterval(popupCheckIntervalRef.current!);
        setConnectionStatus('success');
        setOpenSuccessDialog(true);
      }
    }, 1000);
    
    // Alternative method: Check for redirect in the current tab
    // This assumes the redirect happens in the same tab
    // and you can detect it by checking URL parameters
    const checkRedirectInterval = setInterval(() => {
      const urlParams = new URLSearchParams(window.location.search);
      const status = urlParams.get('whatsapp_status');
      
      if (status === 'success') {
        clearInterval(checkRedirectInterval);
        setConnectionStatus('success');
        setOpenSuccessDialog(true);
      } else if (status === 'error') {
        clearInterval(checkRedirectInterval);
        setConnectionStatus('error');
      }
    }, 1000);
    
    // Clear interval after 5 minutes (300000 ms) to prevent memory leaks
    setTimeout(() => {
      clearInterval(checkRedirectInterval);
      if (popupCheckIntervalRef.current) {
        clearInterval(popupCheckIntervalRef.current);
      }
    }, 300000);
  };
  
  // Handle closing the success dialog
  const handleCloseSuccessDialog = () => {
    setOpenSuccessDialog(false);
  };

  return (
    <Box sx={{ mt: 3, pb: 8 }}>
      {/* Success Dialog */}
      <Dialog 
        open={openSuccessDialog} 
        onClose={handleCloseSuccessDialog}
        PaperProps={{
          sx: {
            borderRadius: 3,
            minWidth: '400px',
            maxWidth: '600px'
          }
        }}
      >
        <DialogTitle sx={{ 
          backgroundColor: '#25D366', 
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          gap: 1 
        }}>
          <WhatsApp fontSize="large" />
          <Typography variant="h6">WhatsApp erfolgreich verknüpft!</Typography>
        </DialogTitle>
        <DialogContent sx={{ pt: 3, pb: 2 }}>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Ihr WhatsApp Business-Konto wurde erfolgreich mit TimeGlobe verknüpft.
            Sie können nun Ihre WhatsApp-Kommunikation über TimeGlobe verwalten.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button 
            variant="contained" 
            onClick={handleCloseSuccessDialog}
            sx={{ 
              backgroundColor: '#25D366',
              '&:hover': {
                backgroundColor: '#128C7E'
              }
            }}
          >
            Zum Dashboard
          </Button>
        </DialogActions>
      </Dialog>

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
        <Typography 
          variant="h6" 
          gutterBottom
          sx={{ 
            display: 'flex', 
            alignItems: 'center',
            color: '#333333',
            fontWeight: 'medium',
            mb: 2
          }}
        >
          <DoneAll sx={{ mr: 1, opacity: 0.9, color: '#1967D2' }} />
          Bestätigen & Verknüpfen
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 4, ml: 0.5 }}>
          Bitte überprüfen Sie Ihre Eingaben und verknüpfen Sie Ihren WhatsApp-Account.
        </Typography>
        
        <Paper 
          variant="outlined" 
          sx={{ 
            p: 3, 
            mb: 4,
            borderRadius: 2,
            backgroundColor: '#FFFFFF',
            borderColor: 'rgba(0, 0, 0, 0.1)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <Typography 
            variant="subtitle1" 
            gutterBottom 
            sx={{ 
              fontWeight: 'bold',
              mb: 3,
              color: '#333333',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <CheckCircle sx={{ mr: 1, fontSize: 20, color: '#1967D2' }} />
            Zusammenfassung
          </Typography>
          
          <List disablePadding>
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0, 
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <VpnKey sx={{ mr: 2, color: '#1967D2' }} />
              <ListItemText 
                primary="API-Schlüssel" 
                secondary={formData.apiKey} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: '#666666'
                }}
              />
            </ListItem>
            
            <Divider sx={{ my: 1, borderColor: 'rgba(0, 0, 0, 0.08)' }} />
            
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0,
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <Business sx={{ mr: 2, color: '#1967D2' }} />
              <ListItemText 
                primary="Unternehmen" 
                secondary={formData.companyName} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: '#666666'
                }}
              />
            </ListItem>
            
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0,
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <ListItemText 
                inset
                primary="Adresse" 
                secondary={`${formData.street}, ${formData.zipCode} ${formData.city}, ${formData.country}`} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: '#666666'
                }}
              />
            </ListItem>
            
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0,
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <Person sx={{ mr: 2, color: '#1967D2' }} />
              <ListItemText 
                primary="Ansprechpartner" 
                secondary={formData.contactPerson} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: '#666666'
                }}
              />
            </ListItem>
            
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0,
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <Email sx={{ mr: 2, color: '#1967D2' }} />
              <ListItemText 
                primary="E-Mail" 
                secondary={formData.email} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: '#666666'
                }}
              />
            </ListItem>
            
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0,
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <Phone sx={{ mr: 2, color: '#1967D2' }} />
              <ListItemText 
                primary="Telefon" 
                secondary={formData.phone} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: '#666666'
                }}
              />
            </ListItem>
            
            <Divider sx={{ my: 1, borderColor: 'rgba(0, 0, 0, 0.08)' }} />
            
            <ListItem 
              sx={{ 
                py: 1.5, 
                px: 0,
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }
              }}
            >
              <CheckCircle sx={{ mr: 2, color: formData.hasAcceptedTerms ? '#1967D2' : 'rgba(0, 0, 0, 0.3)' }} />
              <ListItemText 
                primary="Vertrag akzeptiert" 
                secondary={formData.hasAcceptedTerms ? 'Ja' : 'Nein'} 
                primaryTypographyProps={{ 
                  fontWeight: 'medium',
                  color: '#333333' 
                }}
                secondaryTypographyProps={{
                  color: formData.hasAcceptedTerms ? '#1967D2' : '#666666'
                }}
              />
            </ListItem>
          </List>
          
          {formData.signature && (
            <Box>
              <Typography 
                variant="subtitle2" 
                sx={{ 
                  mt: 3, 
                  mb: 2, 
                  color: '#333333', 
                  fontWeight: 'medium'
                }}
              >
                Unterschrift:
              </Typography>
              
              <Box 
                sx={{ 
                  mt: 1, 
                  border: '1px solid rgba(0, 0, 0, 0.1)', 
                  p: 2, 
                  maxWidth: '300px',
                  borderRadius: 2,
                  backgroundColor: 'rgba(0, 0, 0, 0.02)'
                }}
              >
                <img 
                  src={formData.signature} 
                  alt="Unterschrift" 
                  style={{ maxWidth: '100%', height: 'auto' }} 
                />
              </Box>
            </Box>
          )}
        </Paper>
        
        <Box 
          sx={{ 
            p: 3, 
            borderRadius: 2, 
            backgroundColor: 'rgba(25, 103, 210, 0.05)',
            border: '1px solid rgba(25, 103, 210, 0.2)',
            mb: 2
          }}
        >
          <Typography color="#1967D2" sx={{ fontWeight: 'medium', fontSize: '0.95rem' }}>
            Der nächste Schritt ist die Verknüpfung Ihres WhatsApp Business-Kontos. 
            Klicken Sie auf "WhatsApp verknüpfen", um den Prozess zu starten.
          </Typography>
        </Box>

        {connectionStatus === 'success' && (
          <Alert 
            severity="success" 
            sx={{ 
              mb: 3, 
              mt: 2,
              borderRadius: 2,
              backgroundColor: 'rgba(76, 175, 80, 0.1)', 
              border: '1px solid rgba(76, 175, 80, 0.2)',
              color: '#4caf50',
              '& .MuiAlert-icon': {
                color: '#4caf50'
              }
            }}
          >
            WhatsApp wurde erfolgreich mit Ihrem TimeGlobe-Konto verknüpft!
          </Alert>
        )}

        {connectionStatus === 'error' && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3, 
              mt: 2,
              borderRadius: 2,
              backgroundColor: 'rgba(211, 47, 47, 0.1)', 
              border: '1px solid rgba(211, 47, 47, 0.2)',
              color: '#f44336',
              '& .MuiAlert-icon': {
                color: '#f44336'
              }
            }}
          >
            Bei der Verknüpfung mit WhatsApp ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.
          </Alert>
        )}
      </Paper>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button 
          onClick={onBack}
          variant="outlined"
          startIcon={<ArrowBack />}
          sx={{ 
            borderRadius: 3,
            borderColor: '#1967D2',
            color: '#1967D2',
            px: 3,
            py: 1.2,
            '&:hover': {
              borderColor: '#1967D2',
              backgroundColor: 'rgba(25, 103, 210, 0.05)'
            }
          }}
        >
          Zurück
        </Button>
        <Button
          onClick={handleWhatsAppConnect}
          variant="contained"
          color="primary"
          disabled={connectionStatus === 'connecting'}
          endIcon={connectionStatus === 'connecting' ? null : <WhatsApp />}
          sx={{ 
            px: 4, 
            py: 1.5,
            borderRadius: 3,
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
            backgroundColor: connectionStatus === 'success' ? '#4CAF50' : '#25D366', // WhatsApp green
            '&:hover': {
              boxShadow: '0 6px 20px rgba(0,0,0,0.3)',
              backgroundColor: connectionStatus === 'success' ? '#388E3C' : '#128C7E', // Darker WhatsApp green
            }
          }}
        >
          {connectionStatus === 'connecting' ? 'Verbindung wird hergestellt...' : 
           connectionStatus === 'success' ? 'Erfolgreich verknüpft' : 'WhatsApp verknüpfen'}
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
const ConfirmationStepWithFooter: React.FC<ConfirmationStepProps> = (props) => {
  return (
    <>
      <ConfirmationStep {...props} />
      <Footer />
    </>
  );
};

export default ConfirmationStepWithFooter; 