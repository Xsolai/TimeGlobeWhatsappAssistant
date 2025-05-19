from ..repositories.analytics_repository import AnalyticsRepository
from sqlalchemy.orm import Session
from ..logger import main_logger

class AnalyticsService:
    """Service class for business analytics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics_repo = AnalyticsRepository(db)
    
    def get_business_dashboard(self, business_phone: str):
        """
        Get a complete dashboard data for a business
        
        Args:
            business_phone: Business phone number to filter by
            
        Returns:
            Dictionary with all dashboard components
        """
        try:
            # Get summary data (quick stats)
            summary = self.analytics_repo.get_dashboard_summary(business_phone)
            
            # Get revenue estimates (needed for monthly services booked)
            revenue = self.analytics_repo.get_revenue_estimates(business_phone)
            
            # Get recent appointments
            recent_appointments = self.analytics_repo.get_recent_appointments(business_phone, limit=10)

            # Get appointment time series data for the last 30 days
            appointment_time_series_data = self.analytics_repo.get_appointments_by_timeframe(business_phone, days=30)

            # Construct the dashboard response with only the required fields
            dashboard_data = {
                "summary": {
                    "today_appointments": summary["today_appointments"],
                    "todays_services": summary["todays_services_count"],
                    "costs_today": summary["costs_today_calculated"],
                    "costs_last_30_days": summary["costs_last_30_days_calculated"],
                    "monthly_appointments": summary["thirty_day_appointments"],
                    "monthly_services_booked": revenue["services_booked"],
                    "monthly_growth_rate": summary["thirty_day_growth_rate"]
                },
                "recent_appointments": recent_appointments,
                "appointment_time_series": appointment_time_series_data
            }
            
            return {
                "status": "success",
                "data": dashboard_data
            }
            
        except Exception as e:
            main_logger.error(f"Error getting business dashboard: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate dashboard: {str(e)}"
            }
    
    def get_appointment_analytics(self, business_phone: str, timeframe: int = 30):
        """
        Get detailed appointment analytics
        
        Args:
            business_phone: Business phone number
            timeframe: Number of days to analyze
            
        Returns:
            Dictionary with appointment analytics
        """
        try:
            # Get daily appointment data
            daily_data = self.analytics_repo.get_appointments_by_timeframe(business_phone, timeframe)
            
            # Get busiest times
            busy_times = self.analytics_repo.get_busiest_times(business_phone)
            
            # Get summary data that includes appointment counts
            summary = self.analytics_repo.get_dashboard_summary(business_phone)
            
            return {
                "status": "success",
                "data": {
                    "daily_appointments": daily_data,
                    "busiest_times": busy_times,
                    "appointment_counts": {
                        "today": summary["today_appointments"],
                        "yesterday": summary["yesterday_appointments"],
                        "last_30_days": summary["thirty_day_appointments"],
                        "growth_rate": summary["thirty_day_growth_rate"]
                    }
                }
            }
            
        except Exception as e:
            main_logger.error(f"Error getting appointment analytics: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate appointment analytics: {str(e)}"
            }
    
    def get_customer_analytics(self, business_phone: str):
        """
        Get detailed customer analytics
        
        Args:
            business_phone: Business phone number
            
        Returns:
            Dictionary with customer analytics
        """
        try:
            # Get customer statistics
            customer_stats = self.analytics_repo.get_customer_statistics(business_phone)
            
            return {
                "status": "success",
                "data": customer_stats
            }
            
        except Exception as e:
            main_logger.error(f"Error getting customer analytics: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate customer analytics: {str(e)}"
            }
    
    def get_service_analytics(self, business_phone: str, limit: int = 10):
        """
        Get detailed service analytics
        
        Args:
            business_phone: Business phone number
            limit: Number of top services to return
            
        Returns:
            Dictionary with service analytics
        """
        try:
            # Get service popularity data
            service_popularity = self.analytics_repo.get_service_popularity(business_phone, limit)
            
            # Get revenue estimates
            revenue = self.analytics_repo.get_revenue_estimates(business_phone)
            
            return {
                "status": "success",
                "data": {
                    "popular_services": service_popularity,
                    "revenue_estimates": revenue
                }
            }
            
        except Exception as e:
            main_logger.error(f"Error getting service analytics: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate service analytics: {str(e)}"
            }
    
    def get_business_customers(self, business_phone: str, page: int = 1, page_size: int = 10):
        """
        Get a paginated list of customers for a business
        
        Args:
            business_phone: Business phone number
            page: Page number (starting from 1)
            page_size: Number of customers per page
            
        Returns:
            Dictionary with paginated customer data
        """
        try:
            # Get customer data from repository
            customer_data = self.analytics_repo.get_business_customers(
                business_phone, 
                page, 
                page_size
            )
            
            return {
                "status": "success",
                "data": customer_data
            }
            
        except Exception as e:
            main_logger.error(f"Error getting business customers: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to retrieve customer list: {str(e)}"
            } 