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
  Button,
  IconButton,
  Tooltip,
  Snackbar,
  Popover
} from '@mui/material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker, DateCalendar } from '@mui/x-date-pickers';
import { de } from 'date-fns/locale';
import { 
  TodayOutlined, 
  CalendarTodayOutlined, 
  TrendingUpOutlined, 
  PeopleOutlined,
  AccessTimeOutlined,
  AttachMoneyOutlined,
  NewReleasesOutlined,
  RepeatOutlined,
  ContentCopy,
  WhatsApp
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import UserMenu from '../components/UserMenu';
import Logo from '../components/Logo';
import TopBar from '../components/TopBar';
import analyticsService, { DashboardData, DateRangeData } from '../services/analyticsService';
import authService from '../services/authService';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer
} from 'recharts';
import useCountUp from '../hooks/useCountUp';

// Utility function to format date string
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('de-DE', { 
    month: 'short', 
    day: 'numeric' 
  });
};

// Utility to format currency
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

const DashboardPage: React.FC = () => {
  const { isAuthenticated, currentUser } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [selectedMonth, setSelectedMonth] = useState<Date>(new Date());
  const [calendarAnchorEl, setCalendarAnchorEl] = useState<HTMLElement | null>(null);
  const [activeCalendarType, setActiveCalendarType] = useState<'today' | 'services' | 'month' | null>(null);
  const [accountCreationDate, setAccountCreationDate] = useState<Date | null>(null);
  const [availableDates, setAvailableDates] = useState<string[]>([]);

  // Hilfsfunktion für die Formatierung des Monatstitels
  const getMonthTitle = (date: Date) => {
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    const selectedMonth = date.getMonth();
    const selectedYear = date.getFullYear();

    if (currentMonth === selectedMonth && currentYear === selectedYear) {
      return 'Aktueller Monat';
    } else if (
      currentMonth === selectedMonth + 1 && 
      currentYear === selectedYear
    ) {
      return 'Letzter Monat';
    } else {
      return new Intl.DateTimeFormat('de-DE', { month: 'long', year: 'numeric' }).format(date);
    }
  };

  // Hilfsfunktion für die Formatierung des Tagstitels
  const getDayTitle = (type: string, date: Date) => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    const isToday = date.toDateString() === today.toDateString();
    const isYesterday = date.toDateString() === yesterday.toDateString();
    
    if (isToday) {
      return type === 'appointments' ? 'Termine Heute' : 'Gebuchte Leistungen Heute';
    } else if (isYesterday) {
      return type === 'appointments' ? 'Termine Gestern' : 'Gebuchte Leistungen Gestern';
    } else {
      const formattedDate = new Intl.DateTimeFormat('de-DE', { 
        day: '2-digit',
        month: '2-digit',
        year: '2-digit'
      }).format(date);
      return `${type === 'appointments' ? 'Termine' : 'Gebuchte Leistungen'} ${formattedDate}`;
    }
  };

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const fetchData = async () => {
      try {
        setLoading(true);
        // Hole das Geschäftsprofil für das Erstellungsdatum
        const businessProfile = await authService.getBusinessProfile();
        if (businessProfile.created_at) {
          setAccountCreationDate(new Date(businessProfile.created_at));
        }

        // Hole die verfügbaren Datumsbereiche
        try {
          const dateRanges = await analyticsService.getAvailableDateRanges();
          setAvailableDates(dateRanges.available_dates);
        } catch (error) {
          console.error('Fehler beim Laden der verfügbaren Datumsbereiche:', error);
          // Wenn die Datumsbereiche nicht geladen werden können, fahren wir trotzdem fort
        }

        // Hole die monatlichen Dashboard-Daten basierend auf dem ausgewählten Monat
        const monthlyData = await analyticsService.getMonthlyAnalytics(selectedMonth);
        setDashboardData(monthlyData);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Fehler beim Laden der monatlichen Daten');
      } finally {
        setLoading(false);
      }
    };

    // Initial data fetch on component mount
    fetchData();
  }, [isAuthenticated, navigate, selectedMonth]); // Abhängigkeit von selectedMonth hinzufügen

  // Periodically refresh dashboard data without reloading the page
  useEffect(() => {
    if (!isAuthenticated) return;

    const intervalId = setInterval(() => {
      analyticsService
        .getMonthlyAnalytics(selectedMonth)
        .then((data) => setDashboardData(data))
        .catch((err) =>
          console.error('Error refreshing dashboard data:', err)
        );
    }, 30000); // 30 seconds

    return () => clearInterval(intervalId);
  }, [isAuthenticated, selectedMonth]);

  // Hilfsfunktion zur Überprüfung, ob ein Datum verfügbar ist
  const isDateAvailable = (date: Date) => {
    if (!availableDates.length) return true; // Wenn keine Daten verfügbar sind, erlauben wir alle Daten
    const dateString = date.toISOString().split('T')[0];
    return availableDates.includes(dateString);
  };

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

  const handleCopy = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopyFeedback(`${type} wurde kopiert`);
    setTimeout(() => setCopyFeedback(null), 2000);
  };

  // Handle calendar icon click
  const handleCalendarClick = (event: React.MouseEvent<HTMLElement>, type: 'today' | 'services' | 'month') => {
    setCalendarAnchorEl(event.currentTarget);
    setActiveCalendarType(type);
  };

  // Handle calendar close
  const handleCalendarClose = () => {
    setCalendarAnchorEl(null);
    setActiveCalendarType(null);
  };

  // Handle date selection
  const handleDateChange = async (newDate: Date | null) => {
    if (newDate) {
      try {
        setLoading(true);
        setError(null);

        // Überprüfe, ob das ausgewählte Datum in der Zukunft liegt
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (newDate > today) {
          throw new Error('Bitte wählen Sie ein Datum in der Vergangenheit oder heute aus');
        }

        console.log('Ausgewähltes Datum:', newDate.toISOString());
        console.log('Kalendertyp:', activeCalendarType);

        switch (activeCalendarType) {
          case 'today':
            setSelectedDate(newDate);
            const appointmentsData = await analyticsService.getAppointmentsForDate(newDate);
            console.log('Empfangene Termindaten:', appointmentsData);
            if (appointmentsData && appointmentsData.summary) {
              setDashboardData(prevData => ({
                ...prevData!,
                summary: {
                  ...prevData!.summary,
                  today_appointments: appointmentsData.summary.today_appointments
                }
              }));
            } else {
              throw new Error('Ungültige Daten vom Server empfangen');
            }
            break;

          case 'services':
            setSelectedDate(newDate);
            const servicesData = await analyticsService.getServicesForDate(newDate);
            console.log('Empfangene Servicedaten:', servicesData);
            if (servicesData && servicesData.summary) {
              setDashboardData(prevData => ({
                ...prevData!,
                summary: {
                  ...prevData!.summary,
                  todays_services: servicesData.summary.todays_services
                }
              }));
            } else {
              throw new Error('Ungültige Daten vom Server empfangen');
            }
            break;

          case 'month':
            setSelectedMonth(newDate);
            const monthlyData = await analyticsService.getMonthlyAnalytics(newDate);
            console.log('Empfangene Monatsdaten:', monthlyData);
            // Since getMonthlyAnalytics now returns DashboardData, set it directly
            setDashboardData(monthlyData);
            break;
        }
      } catch (error) {
        console.error('Fehler beim Laden der Daten:', error);
        if (error instanceof Error && error.message.includes('404')) {
          setError('Keine Daten für das ausgewählte Datum verfügbar');
        } else {
          setError(error instanceof Error ? error.message : 'Fehler beim Laden der Daten für das ausgewählte Datum');
        }
      } finally {
        setLoading(false);
        handleCalendarClose();
      }
    }
  };

  // Example for "Termine Heute"
  const todayAppointmentsEnd = dashboardData?.summary?.today_appointments || 0;
  const todayAppointments = useCountUp({ end: todayAppointmentsEnd, duration: 3500, startOnMount: !!dashboardData });

  // Example for "Gebuchte Leistungen Heute"
  const servicesBookedTodayEnd = dashboardData?.summary?.todays_services || 0;
  const servicesBookedToday = useCountUp({ end: servicesBookedTodayEnd, duration: 3500, startOnMount: !!dashboardData });

  // Cost for the month
  const monthlyCost = dashboardData?.summary?.costs_last_30_days || 0;

  // Cost for today
  const dailyCost = dashboardData?.summary?.costs_today || 0;

  // Example for "Termine" in month overview
  const thirtyDayAppointmentsEnd = dashboardData?.summary?.monthly_appointments || 0;
  const thirtyDayAppointments = useCountUp({ end: thirtyDayAppointmentsEnd, duration: 3500, startOnMount: !!dashboardData });

  // Example for "Gebuchte Services" in month overview
  const monthlyServicesBookedEnd = dashboardData?.summary?.monthly_services_booked || 0;
  const monthlyServicesBooked = useCountUp({ end: monthlyServicesBookedEnd, duration: 3500, startOnMount: !!dashboardData });

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
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={de}>
      <Box sx={{ 
        height: '100vh', 
        display: 'flex', 
        flexDirection: 'column',
        backgroundColor: '#FFFFFF',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* WhatsApp Wasserzeichen */}
        <Box
          sx={{
            position: 'fixed',
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)',
            width: '140%',
            height: '140%',
            opacity: 0.020,
            zIndex: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <WhatsApp sx={{ width: '100%', height: '100%' }} />
        </Box>

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
              px: 4,
              py: 2
            }}
          >
            <Box sx={{ transform: 'scale(0.9)', ml: -2 }}>
              <Logo />
            </Box>
            <Box sx={{ mr: -2 }}>
              <UserMenu formData={currentUser ? { 
                companyName: currentUser.business_name || '',
                email: currentUser.email || ''
              } : undefined} />
            </Box>
          </Box>
        </Box>

        <Box sx={{ 
          display: 'flex',
          gap: 4,
          px: 4,
          maxWidth: 1600,
          width: '100%',
          py: 4,
          flex: 1
        }}>
          {/* Hauptbereich */}
          <Box sx={{ 
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            height: 'calc(100vh - 140px)',
            overflow: 'hidden'
          }}>
            <Typography 
              variant="h4" 
              sx={{ 
                fontWeight: 1100, 
                mb: 4,
                color: '#000000',
                textAlign: 'left',
                display: 'flex',
                alignItems: 'center',
                gap: 1
              }}
            >
              WhatsApp Termin Assistent
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {dashboardData && (
              <>
                {/* Summary Metrics */}
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 500, color: '#2C3E50', textAlign: 'left' }}>
                  Terminübersicht
                </Typography>
                <Stack spacing={3} sx={{ mb: 4 }}>
                  <Box 
                    sx={{ 
                      display: 'grid',
                      gridTemplateColumns: { xs: '1fr', sm: '1fr 2fr' },
                      gap: 3,
                      width: '100%'
                    }}
                  >
                    <Stack spacing={3}>
                      <Box>
                        <Paper 
                          sx={{ 
                            height: 'auto',
                            p: 2,
                            borderRadius: 2,
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                            transition: 'transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease',
                            '&:hover': {
                              transform: 'scale(1.02)',
                              boxShadow: '0 5px 10px rgba(0,0,0,0.12)',
                              opacity: 1
                            }
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                            <Typography variant="subtitle2" color="text.secondary">
                              {getDayTitle('appointments', selectedDate)}
                            </Typography>
                          </Box>
                          <Typography variant="h4" sx={{ fontWeight: 500, color: '#1976D2' }}>
                            {todayAppointments}
                          </Typography>
                        </Paper>
                      </Box>

                      <Box>
                        <Paper 
                          sx={{ 
                            height: 'auto',
                            p: 2,
                            borderRadius: 2,
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                            transition: 'transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease',
                            '&:hover': {
                              transform: 'scale(1.02)',
                              boxShadow: '0 5px 10px rgba(0,0,0,0.12)',
                              opacity: 1
                            }
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                            <Typography variant="subtitle2" color="text.secondary">
                              {getDayTitle('services', selectedDate)}
                            </Typography>
                          </Box>
                          <Typography variant="h4" sx={{ fontWeight: 500, color: '#1976D2' }}>
                            {servicesBookedToday}
                          </Typography>
                        </Paper>
                      </Box>

                      <Box>
                        <Paper 
                          sx={{ 
                            p: 2,
                            borderRadius: 2,
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                            transition: 'transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease',
                            '&:hover': {
                              transform: 'scale(1.02)',
                              boxShadow: '0 5px 10px rgba(0,0,0,0.12)',
                              opacity: 1
                            }
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="subtitle2" color="text.secondary">
                              Kosten
                            </Typography>
                            <AttachMoneyOutlined sx={{ color: '#1976D2', fontSize: 20 }} />
                          </Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                Monat
                              </Typography>
                              <Typography variant="h5" sx={{ color: '#1976D2', fontWeight: 500 }}>
                                {monthlyCost.toFixed(2).replace('.', ',')} €
                              </Typography>
                            </Box>
                            <Box sx={{ textAlign: 'right' }}>
                              <Typography variant="body2" color="text.secondary">
                                Heute
                              </Typography>
                              <Typography variant="h6" sx={{ color: '#4CAF50' }}>
                                {dailyCost.toFixed(2).replace('.', ',')} €
                              </Typography>
                            </Box>
                          </Box>
                        </Paper>
                      </Box>
                    </Stack>

                    <Box>
                      <Paper 
                        sx={{ 
                          height: '100%',
                          p: 2,
                          borderRadius: 2,
                          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                          transition: 'transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease',
                          '&:hover': {
                            transform: 'scale(1.02)',
                            boxShadow: '0 5px 10px rgba(0,0,0,0.12)',
                            opacity: 1
                          }
                        }}
                      >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="subtitle2" color="text.secondary">
                            {getMonthTitle(selectedMonth)}
                          </Typography>
                          <IconButton 
                            onClick={(e) => handleCalendarClick(e, 'month')}
                            sx={{ color: '#1976D2' }}
                          >
                            <CalendarTodayOutlined />
                          </IconButton>
                        </Box>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Termine
                            </Typography>
                            <Typography variant="h4" sx={{ fontWeight: 500, color: '#1976D2' }}>
                              {thirtyDayAppointments}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Gebuchte Services
                            </Typography>
                            <Typography variant="h4" sx={{ fontWeight: 500, color: '#1976D2' }}>
                              {monthlyServicesBooked}
                            </Typography>
                          </Box>
                          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            Wachstum: {dashboardData?.summary?.monthly_growth_rate}%
                          </Typography>
                          
                          {/* Liniendiagramm */}
                          <Box sx={{ height: 200, mt: 2 }}>
                            <ResponsiveContainer width="100%" height="100%">
                              <LineChart
                                data={dashboardData?.appointment_time_series || []}
                                margin={{
                                  top: 5,
                                  right: 5,
                                  left: -20,
                                  bottom: 5,
                                }}
                              >
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis 
                                  dataKey="date"
                                  tickFormatter={(date) => {
                                    return new Date(date).toLocaleDateString('de-DE', { 
                                      day: '2-digit',
                                      month: '2-digit'
                                    });
                                  }}
                                  stroke="#666"
                                  fontSize={12}
                                />
                                <YAxis 
                                  stroke="#666"
                                  fontSize={12}
                                  tickFormatter={(value) => Math.round(value).toString()}
                                />
                                <RechartsTooltip
                                  formatter={(value: number, name: string) => [
                                    value,
                                    name === 'count' ? 'Termine' : 'Services'
                                  ]}
                                  labelFormatter={(label: string) => {
                                    return new Date(label).toLocaleDateString('de-DE', {
                                      day: '2-digit',
                                      month: '2-digit',
                                      year: 'numeric'
                                    });
                                  }}
                                />
                                <Line
                                  type="monotone"
                                  dataKey="count"
                                  stroke="#1976D2"
                                  strokeWidth={2}
                                  dot={{ r: 3 }}
                                  activeDot={{ r: 5 }}
                                />
                                <Line
                                  type="monotone"
                                  dataKey="services"
                                  stroke="#FF9800"
                                  strokeWidth={2}
                                  dot={{ r: 3 }}
                                  activeDot={{ r: 5 }}
                                />
                              </LineChart>
                            </ResponsiveContainer>
                          </Box>
                        </Box>
                      </Paper>
                    </Box>
                  </Box>
                </Stack>
              </>
            )}
          </Box>

          {/* Seitenleiste für Aktivitäten */}
          <Box sx={{ 
            width: '300px',
            flexShrink: 0,
            backgroundColor: '#FFFFFF',
            borderRadius: 2,
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            display: 'flex',
            flexDirection: 'column',
            alignSelf: 'stretch'
          }}>
            <Typography variant="h6" sx={{ p: 3, pb: 2, fontWeight: 500, color: '#2C3E50', flexShrink: 0 }}>
              Letzte Aktivitäten
            </Typography>

            <Box sx={{ 
              flex: 1,
              overflowY: 'auto',
              p: 3,
              pt: 0,
              display: 'flex',
              flexDirection: 'column'
            }}>
              {dashboardData?.recent_appointments && dashboardData.recent_appointments.length > 0 ? (
                <Stack spacing={2}>
                  {dashboardData.recent_appointments.map((activity) => (
                    <Box 
                      key={activity.booking_id}
                      sx={{ 
                        p: 2,
                        borderRadius: 1,
                        backgroundColor: 'rgba(25, 118, 210, 0.04)',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          backgroundColor: 'rgba(25, 118, 210, 0.08)',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                        }
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 500, flex: 1 }}>
                          {activity.service_name}
                        </Typography>
                      </Box>
                      
                      <Typography variant="body2" sx={{ 
                        color: 'text.secondary',
                        mb: 1.5,
                        display: 'flex',
                        alignItems: 'center'
                      }}>
                        <Box component="span" sx={{ 
                          display: 'inline-block',
                          width: '24px',
                          height: '24px',
                          borderRadius: '50%',
                          backgroundColor: 'rgba(25, 118, 210, 0.1)',
                          color: '#1967D2',
                          textAlign: 'center',
                          lineHeight: '24px',
                          mr: 1,
                          fontSize: '12px'
                        }}>
                          {activity.customer_name.charAt(0).toUpperCase()}
                        </Box>
                        {activity.customer_name}
                      </Typography>

                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        <Typography variant="caption" sx={{ 
                          color: 'text.secondary',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5
                        }}>
                          <Box component="span" sx={{ color: '#666666' }}>Termin:</Box>
                          {new Date(`${activity.appointment_date}T${activity.appointment_time}`).toLocaleString('de-DE', {
                            day: '2-digit',
                            month: '2-digit',
                            year: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit'
                          })} Uhr
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Stack>
              ) : (
                <Box sx={{ 
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: 'center',
                  backgroundColor: 'rgba(25, 118, 210, 0.04)',
                  borderRadius: 2,
                  p: 3
                }}>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Keine aktuellen Aktivitäten
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mt: 1 }}>
                    Neue Buchungen erscheinen hier automatisch
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>
        </Box>

        {/* Calendar Popover */}
        <Popover
          open={Boolean(calendarAnchorEl)}
          anchorEl={calendarAnchorEl}
          onClose={handleCalendarClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'center',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'center',
          }}
        >
          <Box sx={{ p: 2 }}>
            <DateCalendar 
              value={activeCalendarType === 'month' ? selectedMonth : selectedDate}
              onChange={handleDateChange}
              views={activeCalendarType === 'month' ? ['month', 'year'] : ['day']}
              minDate={accountCreationDate || undefined}
              maxDate={new Date()}
              disableFuture={true}
              shouldDisableDate={(date) => !isDateAvailable(date)}
              sx={{
                '& .MuiPickersDay-root.Mui-disabled': {
                  opacity: 0.4,
                  textDecoration: 'line-through',
                  color: 'text.disabled'
                },
                '& .MuiPickersMonth-root': {
                  position: 'relative',
                  '&.Mui-disabled': {
                    opacity: 0.7,
                    color: '#999',
                    backgroundColor: 'rgba(0, 0, 0, 0.04)',
                    textDecoration: 'line-through',
                    '&::after': {
                      content: '"Nicht verfügbar"',
                      position: 'absolute',
                      bottom: '-18px',
                      left: '50%',
                      transform: 'translateX(-50%)',
                      fontSize: '0.6rem',
                      color: '#666',
                      whiteSpace: 'nowrap',
                      pointerEvents: 'none'
                    }
                  }
                },
                '& .MuiPickersMonth-monthButton': {
                  border: '1px solid transparent',
                  transition: 'all 0.2s ease',
                  '&:not(.Mui-disabled)': {
                    backgroundColor: 'rgba(25, 118, 210, 0.08)',
                    '&:hover': {
                      backgroundColor: 'rgba(25, 118, 210, 0.15)',
                    },
                    '&.Mui-selected': {
                      backgroundColor: '#1976D2',
                      color: 'white',
                      '&:hover': {
                        backgroundColor: '#1565C0',
                      }
                    }
                  },
                  '&.Mui-disabled': {
                    borderColor: '#ddd',
                    background: 'repeating-linear-gradient(45deg, rgba(0, 0, 0, 0.04), rgba(0, 0, 0, 0.04) 10px, rgba(0, 0, 0, 0.08) 10px, rgba(0, 0, 0, 0.08) 20px)'
                  }
                }
              }}
            />
          </Box>
        </Popover>

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

        {/* Footer */}
        <Box 
          sx={{ 
            position: 'fixed',
            bottom: 0,
            left: 0,
            height: '20px',
            width: '100%',
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center',
            py: 0.5,
            backgroundColor: 'rgba(255, 255, 255, 0)',
            backdropFilter: 'blur(5px)',
            opacity: 1,
            zIndex: 10,
            borderTop: '1px solidrgba(224, 224, 224, 0)'
          }}
        >
          <Typography 
            variant="body2" 
            sx={{ 
              color: '#666666',
              mr: 1,
              fontSize: '0.75rem'
            }}
          >
            powered by
          </Typography>
          <img 
            src="/images/EcomTask_logo.svg" 
            alt="EcomTask Logo" 
            style={{ height: '30px' }} 
          />
        </Box>
      </Box>
    </LocalizationProvider>
  );
};

export default DashboardPage; 