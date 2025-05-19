# TimeGlobe WhatsApp Assistant API Documentation

## Base URL
```
https://timeglobe-server.ecomtask.de/api
```

## Current Endpoints

### Dashboard Overview
```
GET /analytics/dashboard
```
Returns general dashboard data including today's appointments, monthly statistics, and recent activities.

**Response Format:**
```typescript
{
  summary: {
    today_appointments: number;
    yesterday_appointments: number;
    thirty_day_appointments: number;
    thirty_day_growth_rate: number;
    customer_stats: {
      total_customers: number;
      new_customers_30d: number;
      returning_customers: number;
      retention_rate: number;
    }
  },
  appointment_trend: Array<{
    date: string;
    count: number;
  }>,
  top_services: Array<{
    item_no: number;
    service_name: string;
    booking_count: number;
  }>,
  recent_activities: Array<{
    id: string;
    service_name: string;
    customer_name: string;
    booking_time: string;
    appointment_time: string;
    status: 'confirmed' | 'pending' | 'cancelled';
  }>,
  revenue: {
    period_days: number;
    services_booked: number;
    estimated_revenue: number;
    avg_service_value: number;
  }
}
```

### Daily Appointments
```
GET /analytics/appointments/date/{YYYY-MM-DD}
```
Returns appointment data for a specific date.

### Daily Services
```
GET /analytics/services/date/{YYYY-MM-DD}
```
Returns service booking data for a specific date.

### Monthly Analytics
```
GET /analytics/monthly/{YYYY}/{MM}
```
Returns analytics data for a specific month.

## Required New Endpoints

### Available Date Ranges
```
GET /analytics/available-dates
```
Should return available dates for which data exists.

**Expected Response Format:**
```typescript
{
  start_date: string;    // YYYY-MM-DD
  end_date: string;      // YYYY-MM-DD
  available_dates: string[];  // Array of YYYY-MM-DD strings
}
```

### Detailed Service Analytics
```
GET /analytics/services/stats
```
Should return detailed statistics about services.

**Expected Response Format:**
```typescript
{
  services: Array<{
    id: string;
    name: string;
    total_bookings: number;
    revenue: number;
    average_rating: number;
    booking_trend: Array<{
      date: string;
      count: number;
    }>
  }>
}
```

### Customer Analytics
```
GET /analytics/customers/stats
```
Should return detailed customer statistics.

**Expected Response Format:**
```typescript
{
  total_customers: number;
  new_customers: {
    daily: number;
    weekly: number;
    monthly: number;
  },
  returning_customers: {
    count: number;
    percentage: number;
  },
  customer_satisfaction: {
    average_rating: number;
    total_reviews: number;
  }
}
```

### Revenue Analytics
```
GET /analytics/revenue/stats
```
Should return detailed revenue statistics.

**Expected Response Format:**
```typescript
{
  current_period: {
    total_revenue: number;
    service_revenue: number;
    average_transaction: number;
  },
  comparison: {
    previous_period: {
      total_revenue: number;
      service_revenue: number;
      average_transaction: number;
    },
    growth_rate: {
      total_revenue: number;
      service_revenue: number;
      average_transaction: number;
    }
  },
  revenue_trend: Array<{
    date: string;
    revenue: number;
    services_count: number;
  }>
}
```

## Authentication

All endpoints require authentication using a Bearer token:

```
Authorization: Bearer <token>
```

## Error Handling

All endpoints should return appropriate HTTP status codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error response format:
```typescript
{
  status: "error",
  message: string,
  code: number
}
```

## Rate Limiting

Consider implementing rate limiting to protect the API:
- 100 requests per minute per IP
- 1000 requests per hour per user

## Data Constraints

- Historical data should be available for at least the last 12 months
- Future dates should return 404 Not Found
- All dates should be in ISO 8601 format (YYYY-MM-DD)
- All monetary values should be in cents/pennies to avoid floating-point issues 