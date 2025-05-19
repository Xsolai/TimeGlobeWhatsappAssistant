import React from 'react';
import { Box, IconButton, Tooltip } from '@mui/material';
import { ContentCopy } from '@mui/icons-material';

const TopBar: React.FC = () => {
  const handleCopy = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <Box 
      sx={{ 
        backgroundColor: '#002B56',
        color: 'white',
        py: 0.5
      }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          width: '100%',
          px: 4,
          fontSize: '0.75rem'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center',
            position: 'relative',
            '&:hover': {
              '& .copy-button': {
                transform: 'translateX(0)',
                opacity: 1
              }
            }
          }}>
            <Box 
              component="a"
              href="tel:+4922838759280"
              sx={{ 
                color: 'inherit', 
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                pr: 3,
                '&:hover': {
                  color: 'rgba(255, 255, 255, 0.9)'
                }
              }}
            >
              0228 / 387 592 80
            </Box>
            <Tooltip title="Nummer kopieren" placement="bottom">
              <IconButton
                className="copy-button"
                onClick={(e) => {
                  e.preventDefault();
                  handleCopy('0228 / 387 592 80', 'Telefonnummer');
                }}
                sx={{ 
                  position: 'absolute',
                  right: 0,
                  transform: 'translateX(-5px)',
                  opacity: 0,
                  transition: 'all 0.2s ease-in-out',
                  p: 0.3,
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.2)'
                  }
                }}
                size="small"
              >
                <ContentCopy sx={{ fontSize: 14 }} />
              </IconButton>
            </Tooltip>
          </Box>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center',
            position: 'relative',
            '&:hover': {
              '& .copy-button': {
                transform: 'translateX(0)',
                opacity: 1
              }
            }
          }}>
            <Box 
              component="a"
              href="mailto:support@ecomtask.de"
              sx={{ 
                color: 'inherit', 
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                pr: 3,
                '&:hover': {
                  color: 'rgba(255, 255, 255, 0.9)'
                }
              }}
            >
              support@ecomtask.de
            </Box>
            <Tooltip title="E-Mail kopieren" placement="bottom">
              <IconButton
                className="copy-button"
                onClick={(e) => {
                  e.preventDefault();
                  handleCopy('support@ecomtask.de', 'E-Mail');
                }}
                sx={{ 
                  position: 'absolute',
                  right: 0,
                  transform: 'translateX(-5px)',
                  opacity: 0,
                  transition: 'all 0.2s ease-in-out',
                  p: 0.3,
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.2)'
                  }
                }}
                size="small"
              >
                <ContentCopy sx={{ fontSize: 14 }} />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <a 
            href="https://www.instagram.com/ecomtask.de"
            target="_blank" 
            rel="noopener noreferrer"
            style={{ color: 'inherit', textDecoration: 'none' }}
          >
            <Box 
              component="img" 
              src="/images/instagram.svg" 
              alt="Instagram"
              sx={{ 
                height: '16px',
                opacity: 0.8,
                transition: 'opacity 0.2s',
                '&:hover': {
                  opacity: 1
                }
              }}
            />
          </a>
          <a 
            href="https://www.linkedin.com/company/ecomtask-ai-mitarbeiter"
            target="_blank" 
            rel="noopener noreferrer"
            style={{ color: 'inherit', textDecoration: 'none' }}
          >
            <Box 
              component="img" 
              src="/images/linkedin.svg" 
              alt="LinkedIn"
              onError={(e: any) => {
                e.target.onerror = null;
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
              sx={{ 
                height: '16px',
                opacity: 0.8,
                transition: 'opacity 0.2s',
                '&:hover': {
                  opacity: 1
                }
              }}
            />
            <Box
              sx={{ 
                display: 'none',
                fontSize: '0.75rem',
                color: 'white',
                opacity: 0.8,
                transition: 'opacity 0.2s',
                '&:hover': {
                  opacity: 1
                }
              }}
            >
              LinkedIn
            </Box>
          </a>
        </Box>
      </Box>
    </Box>
  );
};

export default TopBar; 