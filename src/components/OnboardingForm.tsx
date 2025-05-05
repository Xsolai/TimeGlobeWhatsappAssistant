import React, { useState } from 'react';
import { Box, Stepper, Step, StepLabel, Container, Paper, Typography, useTheme, StepConnector, stepConnectorClasses } from '@mui/material';
import { styled } from '@mui/material/styles';
import ApiKeyStep from './steps/ApiKeyStep';
import CompanyInfoStep from './steps/CompanyInfoStep';
import ContractStep from './steps/ContractStep';
import ConfirmationStep from './steps/ConfirmationStep';
import { OnboardingFormData, OnboardingStep } from '../types';
import Logo from './Logo';
import UserMenu from './UserMenu';

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
  width: 50,
  height: 50,
  display: 'flex',
  borderRadius: '50%',
  justifyContent: 'center',
  alignItems: 'center',
  ...(ownerState.active && {
    backgroundImage: 'linear-gradient(135deg, #1967D2 0%, #1967D2 100%)',
    boxShadow: '0 4px 10px 0 rgba(25, 103, 210, 0.25)',
  }),
  ...(ownerState.completed && {
    backgroundImage: 'linear-gradient(135deg, #1967D2 0%, #1967D2 100%)',
  }),
}));

function TimeGlobeStepIcon(props: any) {
  const { active, completed, className, icon } = props;

  const icons: { [index: string]: React.ReactElement } = {
    1: <span>1</span>,
    2: <span>2</span>,
    3: <span>3</span>,
    4: <span>4</span>,
  };

  return (
    <TimeGlobeStepIconRoot ownerState={{ completed, active }} className={className}>
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

  const handleNext = () => {
    setActiveStep(getNextStep(activeStep));
  };

  const handleBack = () => {
    setActiveStep(getPreviousStep(activeStep));
  };

  const handleFormChange = (data: Partial<OnboardingFormData>) => {
    setFormData((prevData) => ({ ...prevData, ...data }));
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
          <UserMenu />
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
          <Box>
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
              WhatsApp Termin AI <span style={{ fontWeight: 'normal' }}>Onboarding</span>
            </Typography>
            
            <Box sx={{ mb: 5 }}>
              <Stepper 
                activeStep={getStepIndex(activeStep)} 
                alternativeLabel 
                connector={<TimeGlobeConnector />}
              >
                {steps.map((label) => (
                  <Step key={label}>
                    <StepLabel StepIconComponent={TimeGlobeStepIcon}>
                      <Typography sx={{ color: '#333333' }}>{label}</Typography>
                    </StepLabel>
                  </Step>
                ))}
              </Stepper>
            </Box>
            
            {renderStepContent()}
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default OnboardingForm; 