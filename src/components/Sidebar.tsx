import React from 'react';
import { 
  Box, 
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { 
  Dashboard as DashboardIcon,
  AccountCircle as ProfileIcon,
  QuestionAnswer as OnboardingIcon,
  ExitToApp as LogoutIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

// Width of the sidebar when expanded
const drawerWidth = 240;

interface SidebarProps {
  mobileOpen: boolean;
  handleDrawerToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, handleDrawerToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Navigation items
  const navigationItems = [
    {
      text: 'Übersicht',
      icon: <DashboardIcon />,
      path: '/dashboard',
    },
    {
      text: 'Mein Profil',
      icon: <ProfileIcon />,
      path: '/profile',
    },
    {
      text: 'Einrichtung',
      icon: <OnboardingIcon />,
      path: '/onboarding',
    }
  ];
  
  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      handleDrawerToggle(); // Close drawer on mobile after navigation
    }
  };
  
  const handleLogout = () => {
    logout();
    navigate('/login');
    if (isMobile) {
      handleDrawerToggle();
    }
  };
  
  // Drawer content
  const drawerContent = (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
      }}
    >
      <List sx={{ flex: 1 }}>
        {navigationItems.map((item) => (
          <ListItemButton
            key={item.text}
            onClick={() => handleNavigation(item.path)}
            sx={{
              my: 0.5,
              px: 2,
              py: 1.5,
              borderRadius: '8px',
              mx: 1,
              bgcolor: location.pathname === item.path ? 'rgba(25, 103, 210, 0.1)' : 'transparent',
              color: location.pathname === item.path ? theme.palette.primary.main : 'inherit',
              '&:hover': {
                bgcolor: 'rgba(25, 103, 210, 0.05)',
              },
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 42,
                color: location.pathname === item.path ? theme.palette.primary.main : 'inherit',
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItemButton>
        ))}
      </List>
      
      <Divider />
      
      <List>
        <ListItemButton
          onClick={handleLogout}
          sx={{
            my: 0.5,
            px: 2,
            py: 1.5,
            borderRadius: '8px',
            mx: 1,
            color: theme.palette.error.main,
            '&:hover': {
              bgcolor: 'rgba(211, 47, 47, 0.05)',
            },
          }}
        >
          <ListItemIcon sx={{ minWidth: 42, color: 'inherit' }}>
            <LogoutIcon />
          </ListItemIcon>
          <ListItemText primary="Abmelden" />
        </ListItemButton>
      </List>
    </Box>
  );

  return (
    <Box 
      component="nav"
      sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
    >
      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { 
            boxSizing: 'border-box', 
            width: drawerWidth,
            borderRadius: 0,
            boxShadow: '0 0 35px 0 rgba(0,0,0,0.1)'
          },
        }}
      >
        {drawerContent}
      </Drawer>
      
      {/* Desktop drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': { 
            boxSizing: 'border-box', 
            width: drawerWidth,
            borderWidth: 0,
            borderRightWidth: 1,
            borderStyle: 'solid',
            borderColor: theme.palette.divider,
            boxShadow: 'none',
            position: 'relative',
            height: '100%'
          },
        }}
        open
      >
        {drawerContent}
      </Drawer>
    </Box>
  );
};

export default Sidebar; 