import React from 'react';
import { Box, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Logo: React.FC = () => {
  const timeGlobeBlue = '#0052FF'; // Angepasstes TimeGlobe Blau
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  const handleLogoClick = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      // If not authenticated, navigate to login page
      navigate('/login');
    }
  };
  
  return (
    <Box 
      sx={{ 
        display: 'flex', 
        alignItems: 'center',
        cursor: 'pointer',
        transition: 'transform 0.2s ease',
        '&:hover': {
          transform: 'scale(1.02)'
        }
      }}
      onClick={handleLogoClick}
    >
      <Box 
        component="img"
        src="/images/timeglobe.svg"
        alt="TimeGlobe Logo"
        sx={{ 
          height: 45,
          mr: 0.5
        }}
      />
      <Typography 
        variant="h5" 
        component="span" 
        sx={{ 
          fontWeight: 600,
          color: timeGlobeBlue,
          fontSize: '1.5rem',
          letterSpacing: '-0.01em',
          fontFamily: '"SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif',
          lineHeight: 1,
          transform: 'translateY(0px)',
          textRendering: 'optimizeLegibility',
          WebkitFontSmoothing: 'antialiased',
          MozOsxFontSmoothing: 'grayscale'
        }}
      >
        TimeGlobe
      </Typography>
    </Box>
  );
};

export default Logo; 