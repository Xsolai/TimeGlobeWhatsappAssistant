import React, { useState } from 'react';
import { Box, AppBar, Toolbar, IconButton, useTheme, Typography, Link } from '@mui/material';
import { Menu as MenuIcon, Email as EmailIcon } from '@mui/icons-material';
import Sidebar from './Sidebar';
import Logo from './Logo';

// Width of the sidebar
const drawerWidth = 240;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Top App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
          bgcolor: 'white',
          color: 'text.primary',
        }}
      >
        <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { md: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
          
            {/* Show logo only on mobile */}
            <Box sx={{ display: { xs: 'block', md: 'none' } }}>
              <Logo />
            </Box>
          </Box>

          {/* Support Email */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <EmailIcon sx={{ fontSize: 20, color: theme.palette.primary.main }} />
            <Link 
              href="mailto:support@ecomtask.de"
              underline="none"
              sx={{ 
                display: 'flex',
                alignItems: 'center',
                color: theme.palette.primary.main,
                '&:hover': {
                  color: theme.palette.primary.dark
                }
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                support@ecomtask.de
              </Typography>
            </Link>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Sidebar mobileOpen={mobileOpen} handleDrawerToggle={handleDrawerToggle} />

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          backgroundColor: '#F9FAFC',
          marginTop: '64px', // Height of the app bar
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout; 