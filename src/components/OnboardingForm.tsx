import React, { useState, useEffect } from 'react';
import { Box, Stepper, Step, StepLabel, Container, Paper, Typography, useTheme, StepConnector, stepConnectorClasses, IconButton, Tooltip, Snackbar } from '@mui/material';
import { styled } from '@mui/material/styles';
import ApiKeyStep from './steps/ApiKeyStep';
import CompanyInfoStep from './steps/CompanyInfoStep';
import ContractStep from './steps/ContractStep';
import ConfirmationStep from './steps/ConfirmationStep';
import { OnboardingFormData, OnboardingStep } from '../types';
import Logo from './Logo';
import UserMenu from './UserMenu';
import { ContentCopy } from '@mui/icons-material';
import TopBar from './TopBar';

// Anpassung des Steppers für TimeGlobe-Design
const TimeGlobeConnector = styled(StepConnector)(({ theme }) => ({
  [`&.${stepConnectorClasses.alternativeLabel}`]: {
    top: 22,
  },
  [`&.${stepConnectorClasses.active}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      backgroundImage: `linear-gradient(95deg, #1967D2 0%, #1967D2 100%)`,
    },
  },
  [`&.${stepConnectorClasses.completed}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      backgroundImage: `linear-gradient(95deg, #1967D2 0%, #1967D2 100%)`,
    },
  },
  [`& .${stepConnectorClasses.line}`]: {
    height: 3,
    border: 0,
    backgroundColor: '#E0E0E0',
    borderRadius: 1,
  },
}));

const TimeGlobeStepIconRoot = styled('div')<{
  ownerState: { completed?: boolean; active?: boolean };
}>(({ theme, ownerState }) => ({
  backgroundColor: '#ccc',
  zIndex: 1,
  color: '#fff',
  width: '50px',
  height: '50px',
  display: 'flex',
  borderRadius: '50%',
  justifyContent: 'center',
  alignItems: 'center',
  cursor: 'pointer',
  transition: 'all 0.2s ease-in-out',
  fontSize: '1rem',
  [theme.breakpoints.down('sm')]: {
    width: '40px',
    height: '40px',
    fontSize: '0.875rem',
  },
  '&:hover': {
    transform: 'scale(1.1)',
    boxShadow: '0 4px 10px 0 rgba(25, 103, 210, 0.3)',
  },
  ...(ownerState.active && {
    backgroundImage: 'linear-gradient(135deg, #1967D2 0%, #1967D2 100%)',
    boxShadow: '0 4px 10px 0 rgba(25, 103, 210, 0.25)',
  }),
  ...(ownerState.completed && {
    backgroundImage: 'linear-gradient(135deg, #1967D2 0%, #1967D2 100%)',
  }),
}));

function TimeGlobeStepIcon(props: any) {
  const { active, completed, className, icon, onClick } = props;

  const icons: { [index: string]: React.ReactElement } = {
    1: <span>1</span>,
    2: <span>2</span>,
    3: <span>3</span>,
    4: <span>4</span>,
  };

  return (
    <TimeGlobeStepIconRoot 
      ownerState={{ completed, active }} 
      className={className}
      onClick={onClick}
    >
      {icons[String(icon)]}
    </TimeGlobeStepIconRoot>
  );
}

const OnboardingForm: React.FC = () => {
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState<OnboardingStep>(OnboardingStep.API_KEY);
  const [formData, setFormData] = useState<OnboardingFormData>({
    apiKey: '',
    companyName: '',
    street: '',
    city: '',
    zipCode: '',
    country: '',
    contactPerson: '',
    email: '',
    phone: '',
    vatId: '',
    hasAcceptedTerms: false,
    signature: null,
    dataProcessingSignature: null,
    directDebitSignature: null,
    currentSignatureStep: 0
  });
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);

  // Hilfsfunktion um den nächsten Schritt zu ermitteln
  const getNextStep = (currentStep: OnboardingStep): OnboardingStep => {
    switch(currentStep) {
      case OnboardingStep.API_KEY:
        return OnboardingStep.COMPANY_INFO;
      case OnboardingStep.COMPANY_INFO:
        return OnboardingStep.CONTRACT;
      case OnboardingStep.CONTRACT:
        return OnboardingStep.CONFIRMATION;
      default:
        return OnboardingStep.CONFIRMATION;
    }
  };

  // Hilfsfunktion um den vorherigen Schritt zu ermitteln
  const getPreviousStep = (currentStep: OnboardingStep): OnboardingStep => {
    switch(currentStep) {
      case OnboardingStep.CONFIRMATION:
        return OnboardingStep.CONTRACT;
      case OnboardingStep.CONTRACT:
        return OnboardingStep.COMPANY_INFO;
      case OnboardingStep.COMPANY_INFO:
        return OnboardingStep.API_KEY;
      default:
        return OnboardingStep.API_KEY;
    }
  };

  // Hilfsfunktion, um den aktiven Schritt in einen numerischen Index umzuwandeln
  const getStepIndex = (step: OnboardingStep): number => {
    switch(step) {
      case OnboardingStep.API_KEY:
        return 0;
      case OnboardingStep.COMPANY_INFO:
        return 1;
      case OnboardingStep.CONTRACT:
        return 2;
      case OnboardingStep.CONFIRMATION:
        return 3;
      default:
        return 0;
    }
  };

  // Hilfsfunktion, um vom numerischen Index zum OnboardingStep zu konvertieren
  const getStepFromIndex = (index: number): OnboardingStep => {
    switch(index) {
      case 0:
        return OnboardingStep.API_KEY;
      case 1:
        return OnboardingStep.COMPANY_INFO;
      case 2:
        return OnboardingStep.CONTRACT;
      case 3:
        return OnboardingStep.CONFIRMATION;
      default:
        return OnboardingStep.API_KEY;
    }
  };

  // Handler für Klicks auf die Schritte
  const handleStepClick = (stepIndex: number) => {
    const currentStepIndex = getStepIndex(activeStep);
    
    // Erlaube nur Navigation zu früheren Schritten oder zum nächsten Schritt
    // (verhindert Überspringen von Schritten nach vorne)
    if (stepIndex <= currentStepIndex || stepIndex === currentStepIndex + 1) {
      setActiveStep(getStepFromIndex(stepIndex));
    }
  };

  const handleNext = () => {
    setActiveStep(getNextStep(activeStep));
  };

  const handleBack = () => {
    setActiveStep(getPreviousStep(activeStep));
  };

  const handleFormChange = (data: Partial<OnboardingFormData>) => {
    setFormData((prevData) => ({ ...prevData, ...data }));
  };

  const handleCopy = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopyFeedback(`${type} wurde kopiert`);
    setTimeout(() => setCopyFeedback(null), 2000);
  };

  const steps = ['API-Schlüssel', 'Unternehmensinformationen', 'Vertrag', 'Bestätigung'];

  const renderStepContent = () => {
    switch (activeStep) {
      case OnboardingStep.API_KEY:
        return (
          <ApiKeyStep 
            apiKey={formData.apiKey} 
            onFormChange={handleFormChange} 
            onNext={handleNext} 
          />
        );
      case OnboardingStep.COMPANY_INFO:
        return (
          <CompanyInfoStep 
            formData={formData} 
            onFormChange={handleFormChange} 
            onNext={handleNext} 
            onBack={handleBack} 
          />
        );
      case OnboardingStep.CONTRACT:
        return (
          <ContractStep 
            formData={formData} 
            onFormChange={handleFormChange} 
            onNext={handleNext} 
            onBack={handleBack} 
          />
        );
      case OnboardingStep.CONFIRMATION:
        return (
          <ConfirmationStep 
            formData={formData} 
            onBack={handleBack} 
          />
        );
      default:
        return null;
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
            <UserMenu formData={formData} />
          </Box>
        </Box>
      </Box>

      <Container 
        maxWidth="lg" 
        sx={{ 
          flex: 1, 
          py: { xs: 2, sm: 4 },
          px: { xs: 2, sm: 3 }
        }}
      >
        <Typography 
          variant="h4" 
          sx={{ 
            mb: { xs: 4, sm: 6 }, 
            textAlign: 'center',
            color: '#333333',
            fontWeight: 500,
            fontSize: { xs: '1.5rem', sm: '2rem' },
            px: { xs: 1, sm: 0 }
          }}
        >
          WhatsApp Termin Assistent Onboarding
        </Typography>
        
        <Stepper 
          activeStep={getStepIndex(activeStep)} 
          alternativeLabel 
          connector={<TimeGlobeConnector />}
          sx={{ 
            mb: { xs: 4, sm: 6 },
            display: { xs: 'none', sm: 'flex' },
            '& .MuiStepLabel-label': {
              fontSize: { xs: '0.75rem', sm: '0.875rem' },
              marginTop: { xs: '8px', sm: '8px' }
            }
          }}
        >
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel 
                StepIconComponent={(iconProps) => 
                  <TimeGlobeStepIcon 
                    {...iconProps} 
                    onClick={() => handleStepClick(index)} 
                  />
                }
              >
                <Typography 
                  sx={{ 
                    color: '#333333',
                    cursor: 'pointer',
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    textAlign: 'center',
                    lineHeight: { xs: 1.2, sm: 1.4 },
                    '&:hover': {
                      color: '#1967D2',
                      fontWeight: 'medium'
                    }
                  }}
                  onClick={() => handleStepClick(index)}
                >
                  {label}
                </Typography>
              </StepLabel>
            </Step>
          ))}
        </Stepper>
        
        <Paper 
          elevation={2} 
          sx={{ 
            p: { xs: 2, sm: 3, md: 4 }, 
            mb: { xs: 2, sm: 4 },
            borderRadius: 3,
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
            backgroundColor: '#FFFFFF',
            border: '1px solid #F0F0F0',
          }}
        >
          {renderStepContent()}
        </Paper>
      </Container>

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

export default OnboardingForm; 