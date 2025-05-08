import React, { useState, useEffect } from 'react';
import { Box, Avatar, Menu, MenuItem, Typography, IconButton, Divider } from '@mui/material';
import { AccountCircle, ExitToApp, Business, Dashboard } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { OnboardingFormData } from '../types';

interface UserMenuProps {
  formData?: Partial<OnboardingFormData>;
}

const UserMenu: React.FC<UserMenuProps> = ({ formData }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleClose();
    navigate('/login');
  };
  
  const handleProfileClick = () => {
    handleClose();
    navigate('/profile');
  };

  // Generate initials from user's business name or email
  const getInitials = () => {
    // First check formData if in onboarding
    if (formData?.companyName) {
      return formData.companyName
        .split(' ')
        .map(word => word.charAt(0).toUpperCase())
        .join('')
        .substring(0, 2);
    }
    
    // Then check currentUser from auth context
    if (currentUser?.business_name) {
      // Get first letter of each word in business name
      return currentUser.business_name
        .split(' ')
        .map(word => word.charAt(0).toUpperCase())
        .join('')
        .substring(0, 2);
    }
    return currentUser?.email?.charAt(0).toUpperCase() || '?';
  };

  // Get display name for the menu
  const getDisplayName = () => {
    // First check formData if in onboarding
    if (formData?.companyName) {
      return formData.companyName;
    }
    
    // Then check currentUser from auth context
    return currentUser?.business_name || 'Your Business';
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <Box sx={{ mr: 2, display: { xs: 'none', sm: 'flex' } }}>
        <Typography variant="body2" color="text.secondary">
          {getDisplayName()}
        </Typography>
      </Box>
      <IconButton
        size="large"
        onClick={handleMenu}
        color="inherit"
        sx={{ p: 0 }}
      >
        <Avatar sx={{ 
          bgcolor: '#1967D2',
          color: 'white',
          width: 40,
          height: 40
        }}>
          {getInitials()}
        </Avatar>
      </IconButton>
      <Menu
        id="menu-appbar"
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{
          elevation: 3,
          sx: { minWidth: '220px', mt: 1 }
        }}
      >
        <Box sx={{ px: 2, py: 1 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 500, display: 'flex', alignItems: 'center' }}>
            <Business fontSize="small" sx={{ mr: 1 }} />
            {getDisplayName()}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {formData?.email || currentUser?.email}
          </Typography>
        </Box>
        <Divider />
        <MenuItem onClick={handleProfileClick} sx={{ gap: 1 }}>
          <AccountCircle fontSize="small" />
          <Typography variant="body2">My Profile</Typography>
        </MenuItem>
        <MenuItem onClick={() => { handleClose(); navigate('/dashboard'); }} sx={{ gap: 1 }}>
          <Dashboard fontSize="small" />
          <Typography variant="body2">Dashboard</Typography>
        </MenuItem>
        <MenuItem onClick={handleLogout} sx={{ gap: 1 }}>
          <ExitToApp fontSize="small" />
          <Typography variant="body2">Logout</Typography>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default UserMenu; 