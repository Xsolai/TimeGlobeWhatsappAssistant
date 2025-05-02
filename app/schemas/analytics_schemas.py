from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Base response model
class BaseResponse(BaseModel):
    status: str
    message: Optional[str] = None
    
# Daily appointment data
class DailyAppointment(BaseModel):
    date: str
    count: int
    
# Service popularity data
class ServicePopularity(BaseModel):
    item_no: int
    service_name: str
    booking_count: int
    
# Time distribution
class TimeDistribution(BaseModel):
    hour: int
    count: int
    
# Day distribution
class DayDistribution(BaseModel):
    day: str
    count: int
    
# Busy times data
class BusyTimes(BaseModel):
    busiest_hours: List[TimeDistribution]
    busiest_days: List[DayDistribution]
    
# Customer statistics
class CustomerStats(BaseModel):
    total_customers: int
    new_customers_30d: int
    returning_customers: int
    retention_rate: float
    
# Revenue estimates
class RevenueEstimates(BaseModel):
    period_days: int
    services_booked: int
    estimated_revenue: float
    avg_service_value: float
    
# Summary metrics
class DashboardSummary(BaseModel):
    today_appointments: int
    yesterday_appointments: int
    thirty_day_appointments: int
    thirty_day_growth_rate: float
    customer_stats: CustomerStats
    
# Complete dashboard response
class DashboardData(BaseModel):
    summary: DashboardSummary
    appointment_trend: List[DailyAppointment]
    top_services: List[ServicePopularity]
    busy_times: BusyTimes
    revenue: RevenueEstimates
    
# Dashboard response
class DashboardResponse(BaseResponse):
    data: Optional[DashboardData] = None
    
# Appointment analysis data
class AppointmentCounts(BaseModel):
    today: int
    yesterday: int
    last_30_days: int
    growth_rate: float
    
class AppointmentAnalyticsData(BaseModel):
    daily_appointments: List[DailyAppointment]
    busiest_times: BusyTimes
    appointment_counts: AppointmentCounts
    
# Appointment analytics response
class AppointmentAnalyticsResponse(BaseResponse):
    data: Optional[AppointmentAnalyticsData] = None
    
# Customer analytics response
class CustomerAnalyticsResponse(BaseResponse):
    data: Optional[CustomerStats] = None
    
# Service analytics data
class ServiceAnalyticsData(BaseModel):
    popular_services: List[ServicePopularity]
    revenue_estimates: RevenueEstimates
    
# Service analytics response
class ServiceAnalyticsResponse(BaseResponse):
    data: Optional[ServiceAnalyticsData] = None

# Customer list item
class CustomerListItem(BaseModel):
    id: int
    name: str
    mobile_number: str
    email: Optional[str] = None
    booking_count: int
    latest_booking: Optional[str] = None
    created_at: str
    
# Customer list data
class CustomerListData(BaseModel):
    total: int
    customers: List[CustomerListItem]
    
# Customer list response
class CustomerListResponse(BaseResponse):
    data: Optional[CustomerListData] = None 