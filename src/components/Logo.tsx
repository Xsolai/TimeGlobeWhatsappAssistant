import React from 'react';
import { Box, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Logo: React.FC = () => {
  const timeGlobeBlue = '#1967D2'; // Die TimeGlobe Blau-Farbe
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
          height: 52,
          mr: 2
        }}
      />
      <Typography 
        variant="h5" 
        component="span" 
        sx={{ 
          fontWeight: 'bold',
          color: timeGlobeBlue,
          fontSize: '2.3rem',
          letterSpacing: '-0.02em',
          fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif'
        }}
      >
        TimeGlobe
      </Typography>
    </Box>
  );
};

export default Logo; 