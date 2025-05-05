import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Divider,
  useTheme,
  Stack,
  Button
} from '@mui/material';
import { 
  TodayOutlined, 
  CalendarTodayOutlined, 
  TrendingUpOutlined, 
  PeopleOutlined,
  AccessTimeOutlined,
  AttachMoneyOutlined,
  NewReleasesOutlined,
  RepeatOutlined
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import UserMenu from '../components/UserMenu';
import Logo from '../components/Logo';
import analyticsService, { DashboardData } from '../services/analyticsService';

// Utility function to format date string
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric' 
  });
};

// Utility to format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

const DashboardPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const data = await analyticsService.getDashboard();
        setDashboardData(data);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [isAuthenticated, navigate]);

  // Function to render a simple stat card
  const StatCard = ({ 
    title, 
    value, 
    icon, 
    color = theme.palette.primary.main, 
    secondaryValue = null, 
    secondaryLabel = null 
  }: { 
    title: string, 
    value: string | number, 
    icon: React.ReactNode, 
    color?: string,
    secondaryValue?: string | number | null,
    secondaryLabel?: string | null
  }) => {
    return (
      <Card 
        sx={{ 
          height: '100%',
          boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
          '&:hover': {
            boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
            transform: 'translateY(-4px)'
          }
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="subtitle2" color="text.secondary">
              {title}
            </Typography>
            <Box sx={{ color: color }}>
              {icon}
            </Box>
          </Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', color: color }}>
            {value}
          </Typography>
          
          {secondaryValue !== null && secondaryLabel !== null && (
            <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
              <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                {secondaryLabel}:
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                {secondaryValue}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: '#F9FAFC',
      pb: 6
    }}>
      <Container maxWidth="lg" sx={{ flex: 1 }}>
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 4, 
            mt: 3,
          }}
        >
          <Box sx={{ transform: 'scale(1.2)' }}>
            <Logo />
          </Box>
          <UserMenu />
        </Box>

        <Typography 
          variant="h4" 
          sx={{ 
            fontWeight: 'bold', 
            mb: 4,
            color: theme.palette.primary.main 
          }}
        >
          Business Dashboard
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {dashboardData && (
          <>
            {/* Summary Metrics */}
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'medium' }}>
              Appointment Overview
            </Typography>
            <Stack spacing={3} sx={{ mb: 4 }}>
              <Stack 
                direction={{ xs: 'column', sm: 'row' }} 
                spacing={3} 
                sx={{ width: '100%' }}
              >
                <Box sx={{ flex: 1 }}>
                  <StatCard 
                    title="Today's Appointments" 
                    value={dashboardData.summary.today_appointments} 
                    icon={<TodayOutlined />} 
                    color={theme.palette.primary.main}
                  />
                </Box>
                <Box sx={{ flex: 1 }}>
                  <StatCard 
                    title="Yesterday's Appointments" 
                    value={dashboardData.summary.yesterday_appointments} 
                    icon={<CalendarTodayOutlined />} 
                    color="#4CAF50"
                  />
                </Box>
                <Box sx={{ flex: 1 }}>
                  <StatCard 
                    title="30-Day Appointments" 
                    value={dashboardData.summary.thirty_day_appointments} 
                    icon={<CalendarTodayOutlined />} 
                    color="#9C27B0"
                    secondaryValue={`${dashboardData.summary.thirty_day_growth_rate}%`}
                    secondaryLabel="Growth"
                  />
                </Box>
                <Box sx={{ flex: 1 }}>
                  <StatCard 
                    title="Total Customers" 
                    value={dashboardData.summary.customer_stats.total_customers} 
                    icon={<PeopleOutlined />} 
                    color="#E91E63"
                    secondaryValue={`${dashboardData.summary.customer_stats.retention_rate}%`}
                    secondaryLabel="Retention"
                  />
                </Box>
              </Stack>
            </Stack>

            {/* Revenue Metrics */}
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'medium' }}>
              Revenue Metrics (Last {dashboardData.revenue.period_days} Days)
            </Typography>
            <Stack spacing={3} sx={{ mb: 4 }}>
              <Stack 
                direction={{ xs: 'column', sm: 'row' }} 
                spacing={3} 
                sx={{ width: '100%' }}
              >
                <Box sx={{ flex: 1 }}>
                  <StatCard 
                    title="Estimated Revenue" 
                    value={formatCurrency(dashboardData.revenue.estimated_revenue)} 
                    icon={<AttachMoneyOutlined />} 
                    color="#2196F3"
                  />
                </Box>
                <Box sx={{ flex: 1 }}>
                  <StatCard 
                    title="Services Booked" 
                    value={dashboardData.revenue.services_booked} 
                    icon={<CalendarTodayOutlined />} 
                    color="#673AB7"
                  />
                </Box>
                <Box sx={{ flex: 1 }}>
                  <StatCard 
                    title="Avg. Service Value" 
                    value={formatCurrency(dashboardData.revenue.avg_service_value)} 
                    icon={<AttachMoneyOutlined />} 
                    color="#FF9800"
                  />
                </Box>
                <Box sx={{ flex: 1 }}>
                  <StatCard 
                    title="New Customers (30d)" 
                    value={dashboardData.summary.customer_stats.new_customers_30d} 
                    icon={<NewReleasesOutlined />} 
                    color="#00BCD4"
                    secondaryValue={dashboardData.summary.customer_stats.returning_customers}
                    secondaryLabel="Returning"
                  />
                </Box>
              </Stack>
            </Stack>

            {/* Top Services and Busy Times */}
            <Stack 
              direction={{ xs: 'column', md: 'row' }} 
              spacing={3} 
              sx={{ mb: 4 }}
            >
              {/* Top Services */}
              <Box sx={{ flex: 1 }}>
                <Paper sx={{ 
                  p: 3, 
                  height: '100%', 
                  boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)'
                }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Top Services
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  <Stack spacing={2}>
                    {dashboardData.top_services.map((service) => (
                      <Box 
                        key={service.item_no}
                        sx={{ 
                          display: 'flex', 
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          p: 1,
                          borderRadius: 1,
                          bgcolor: 'rgba(25, 103, 210, 0.05)',
                        }}
                      >
                        <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                          {service.service_name}
                        </Typography>
                        <Box 
                          sx={{ 
                            display: 'flex', 
                            alignItems: 'center',
                            bgcolor: theme.palette.primary.main,
                            color: 'white',
                            borderRadius: '50%',
                            width: 30,
                            height: 30,
                            justifyContent: 'center'
                          }}
                        >
                          {service.booking_count}
                        </Box>
                      </Box>
                    ))}
                    {dashboardData.top_services.length === 0 && (
                      <Typography variant="body2" sx={{ textAlign: 'center', py: 2 }}>
                        No services data available yet
                      </Typography>
                    )}
                  </Stack>
                </Paper>
              </Box>

              {/* Busy Times */}
              <Box sx={{ flex: 1 }}>
                <Paper sx={{ 
                  p: 3, 
                  height: '100%', 
                  boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)'
                }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Busy Times
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, color: 'text.secondary' }}>
                      Busiest Days
                    </Typography>
                    <Stack spacing={1}>
                      {dashboardData.busy_times.busiest_days.map((day) => (
                        <Box 
                          key={day.day}
                          sx={{ 
                            display: 'flex', 
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            p: 1,
                            borderRadius: 1,
                            bgcolor: 'rgba(233, 30, 99, 0.05)',
                          }}
                        >
                          <Typography variant="body2">{day.day}</Typography>
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            {day.count} appointments
                          </Typography>
                        </Box>
                      ))}
                      {dashboardData.busy_times.busiest_days.length === 0 && (
                        <Typography variant="body2" sx={{ textAlign: 'center', py: 1 }}>
                          No data available yet
                        </Typography>
                      )}
                    </Stack>
                  </Box>
                  
                  <Box>
                    <Typography variant="subtitle2" sx={{ mb: 1, color: 'text.secondary' }}>
                      Busiest Hours
                    </Typography>
                    <Stack spacing={1}>
                      {dashboardData.busy_times.busiest_hours.map((hour) => (
                        <Box 
                          key={hour.hour}
                          sx={{ 
                            display: 'flex', 
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            p: 1,
                            borderRadius: 1,
                            bgcolor: 'rgba(76, 175, 80, 0.05)',
                          }}
                        >
                          <Typography variant="body2">
                            {hour.hour}:00 - {hour.hour + 1}:00
                          </Typography>
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            {hour.count} appointments
                          </Typography>
                        </Box>
                      ))}
                      {dashboardData.busy_times.busiest_hours.length === 0 && (
                        <Typography variant="body2" sx={{ textAlign: 'center', py: 1 }}>
                          No data available yet
                        </Typography>
                      )}
                    </Stack>
                  </Box>
                </Paper>
              </Box>
            </Stack>

            {/* Appointment Trends */}
            <Paper sx={{ 
              p: 3, 
              mb: 4, 
              boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)'
            }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Appointment Trends
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Box sx={{ height: 300, width: '100%', display: 'flex' }}>
                {dashboardData.appointment_trend.length > 0 ? (
                  <Box sx={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    width: '100%', 
                    overflow: 'auto',
                    gap: 2
                  }}>
                    <Stack 
                      direction="row" 
                      alignItems="flex-end" 
                      spacing={2}
                      sx={{ 
                        height: '100%', 
                        p: 2,
                        overflowX: 'auto'
                      }}
                    >
                      {dashboardData.appointment_trend.map((day) => (
                        <Stack 
                          key={day.date}
                          direction="column"
                          alignItems="center"
                          sx={{ flex: '1 0 auto', minWidth: '60px' }}
                        >
                          <Box 
                            sx={{ 
                              height: `${day.count > 0 ? day.count * 30 + 30 : 30}px`,
                              width: '80%',
                              backgroundColor: theme.palette.primary.main,
                              borderRadius: '4px 4px 0 0',
                              minHeight: '30px',
                              display: 'flex',
                              justifyContent: 'center',
                              alignItems: 'flex-start',
                              color: 'white',
                              fontWeight: 'bold'
                            }}
                          >
                            {day.count}
                          </Box>
                          <Typography 
                            variant="caption" 
                            sx={{ 
                              mt: 1, 
                              fontWeight: 'medium',
                              whiteSpace: 'nowrap'
                            }}
                          >
                            {formatDate(day.date)}
                          </Typography>
                        </Stack>
                      ))}
                    </Stack>
                  </Box>
                ) : (
                  <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'center', 
                    alignItems: 'center', 
                    width: '100%',
                    height: '100%'
                  }}>
                    <Typography variant="body2" color="text.secondary">
                      No appointment trend data available yet
                    </Typography>
                  </Box>
                )}
              </Box>
            </Paper>
          </>
        )}

        {/* Navigation buttons */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Button 
            variant="outlined" 
            onClick={() => navigate('/profile')}
            sx={{ 
              color: theme.palette.primary.main, 
              borderColor: theme.palette.primary.main,
              mr: 2
            }}
          >
            View Profile
          </Button>
          <Button 
            variant="outlined" 
            onClick={() => navigate('/onboarding')}
            sx={{ 
              color: theme.palette.primary.main, 
              borderColor: theme.palette.primary.main 
            }}
          >
            Back to Onboarding
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default DashboardPage; 