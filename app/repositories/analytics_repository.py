from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, distinct, extract
from datetime import datetime, timedelta
from ..models.booked_appointment import BookModel
from ..models.booking_detail import BookingDetail
from ..models.customer_model import CustomerModel
from ..logger import main_logger
from ..models.business_model import Business

class AnalyticsRepository:
    """Repository class for business analytics data queries"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_appointments_by_timeframe(self, business_phone: str, days: int = 30):
        """
        Get appointment count grouped by day for the specified timeframe
        
        Args:
            business_phone: The business phone number
            days: Number of days to look back (default 30)
            
        Returns:
            List of daily appointment counts
        """
        try:
            # Calculate the date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Query appointments grouped by day (using BookModel creation date)
            query = (
                self.db.query(
                    func.date(BookModel.created_at).label('date'),
                    func.count().label('count')
                )
                .join(BookingDetail, BookModel.id == BookingDetail.book_id)
                .filter(
                    BookModel.business_phone_number == business_phone,
                    BookModel.created_at >= start_date,
                    BookModel.created_at <= end_date
                )
                .group_by(func.date(BookModel.created_at))
                .order_by(func.date(BookModel.created_at))
            )
            
            results = query.all()
            
            # Format results as list of dictionaries
            return [
                {"date": str(row.date), "count": row.count}
                for row in results
            ]
            
        except Exception as e:
            main_logger.error(f"Error getting appointments by timeframe: {str(e)}")
            return []
    
    def get_service_popularity(self, business_phone: str, limit: int = 10):
        """
        Get the most popular services based on booking count
        
        Args:
            business_phone: The business phone number
            limit: Number of services to return (default 10)
            
        Returns:
            List of service popularity data
        """
        try:
            query = (
                self.db.query(
                    BookingDetail.item_no,
                    BookingDetail.item_nm,
                    func.count().label('booking_count')
                )
                .join(BookModel, BookModel.id == BookingDetail.book_id)
                .filter(BookModel.business_phone_number == business_phone)
                .group_by(BookingDetail.item_no, BookingDetail.item_nm)
                .order_by(desc('booking_count'))
                .limit(limit)
            )
            
            results = query.all()
            
            return [
                {
                    "item_no": row.item_no,
                    "service_name": row.item_nm or f"Service {row.item_no}",
                    "booking_count": row.booking_count
                }
                for row in results
            ]
            
        except Exception as e:
            main_logger.error(f"Error getting service popularity: {str(e)}")
            return []
    
    def get_customer_statistics(self, business_phone: str):
        """
        Get customer statistics for the business
        
        Args:
            business_phone: The business phone number
            
        Returns:
            Dictionary with customer statistics
        """
        try:
            # First, get the business_id from the business_phone
            business = self.db.query(Business).filter(Business.whatsapp_number == business_phone).first()
            
            if not business:
                main_logger.warning(f"No business found with WhatsApp number: {business_phone}")
                return {
                    "total_customers": 0,
                    "new_customers_30d": 0,
                    "returning_customers": 0,
                    "retention_rate": 0
                }
            
            business_id = business.id
            main_logger.info(f"Found business ID: {business_id} for phone: {business_phone}")
            
            # Total customers directly linked to the business
            total_customers = (
                self.db.query(func.count(distinct(CustomerModel.id)))
                .filter(CustomerModel.business_id == business_id)
                .scalar() or 0
            )
            
            # New customers in the last 30 days directly linked to the business
            thirty_days_ago = datetime.now() - timedelta(days=30)
            new_customers = (
                self.db.query(func.count(distinct(CustomerModel.id)))
                .filter(
                    CustomerModel.business_id == business_id,
                    CustomerModel.created_at >= thirty_days_ago
                )
                .scalar() or 0
            )
            
            # Returning customers (with more than one booking)
            # Still need to join with BookModel to count bookings
            returning_customers = (
                self.db.query(func.count(distinct(CustomerModel.id)))
                .join(BookModel, BookModel.customer_id == CustomerModel.id)
                .filter(
                    CustomerModel.business_id == business_id
                )
                .group_by(CustomerModel.id)
                .having(func.count(BookModel.id) > 1)
                .count() or 0
            )
            
            return {
                "total_customers": total_customers,
                "new_customers_30d": new_customers,
                "returning_customers": returning_customers,
                "retention_rate": round(returning_customers / total_customers * 100, 2) if total_customers > 0 else 0
            }
            
        except Exception as e:
            main_logger.error(f"Error getting customer statistics: {str(e)}")
            return {
                "total_customers": 0,
                "new_customers_30d": 0,
                "returning_customers": 0,
                "retention_rate": 0
            }
    
    def get_busiest_times(self, business_phone: str):
        """
        Get busiest hours of the day and days of the week
        
        Args:
            business_phone: The business phone number
            
        Returns:
            Dictionary with busiest times data
        """
        try:
            # Busiest hours of the day
            hours_query = (
                self.db.query(
                    extract('hour', BookingDetail.begin_ts).label('hour'),
                    func.count().label('count')
                )
                .join(BookModel, BookModel.id == BookingDetail.book_id)
                .filter(BookModel.business_phone_number == business_phone)
                .group_by('hour')
                .order_by(desc('count'))
            )
            
            hours_results = hours_query.all()
            
            # Busiest days of the week
            days_query = (
                self.db.query(
                    extract('dow', BookingDetail.begin_ts).label('day'),
                    func.count().label('count')
                )
                .join(BookModel, BookModel.id == BookingDetail.book_id)
                .filter(BookModel.business_phone_number == business_phone)
                .group_by('day')
                .order_by(desc('count'))
            )
            
            days_results = days_query.all()
            
            # Map day numbers to names
            day_names = {
                0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 
                4: "Thursday", 5: "Friday", 6: "Saturday"
            }
            
            return {
                "busiest_hours": [
                    {"hour": row.hour, "count": row.count} 
                    for row in hours_results
                ],
                "busiest_days": [
                    {"day": day_names.get(int(row.day)), "count": row.count} 
                    for row in days_results
                ]
            }
            
        except Exception as e:
            main_logger.error(f"Error getting busiest times: {str(e)}")
            return {"busiest_hours": [], "busiest_days": []}
    
    def get_revenue_estimates(self, business_phone: str, days: int = 30):
        """
        Get estimated revenue based on service bookings
        Note: This is a placeholder as we don't have price data
        
        Args:
            business_phone: The business phone number
            days: Number of days to look back
            
        Returns:
            Revenue estimate data
        """
        try:
            # For demonstration purposes - assuming average service value
            # In a real implementation, you would join with a prices table
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            services_count = (
                self.db.query(func.count(BookingDetail.id))
                .join(BookModel, BookModel.id == BookingDetail.book_id)
                .filter(
                    BookModel.business_phone_number == business_phone,
                    BookingDetail.begin_ts >= start_date,
                    BookingDetail.begin_ts <= end_date
                )
                .scalar() or 0
            )
            
            # Placeholder for estimated value (would be replaced with actual price data)
            avg_service_value = 50  # Example value
            
            return {
                "period_days": days,
                "services_booked": services_count,
                "estimated_revenue": services_count * avg_service_value,
                "avg_service_value": avg_service_value
            }
            
        except Exception as e:
            main_logger.error(f"Error getting revenue estimates: {str(e)}")
            return {
                "period_days": days,
                "services_booked": 0,
                "estimated_revenue": 0,
                "avg_service_value": 0
            }
    
    def get_dashboard_summary(self, business_phone: str):
        """
        Get a summary of key metrics for a business dashboard
        
        Args:
            business_phone: The business phone number
            
        Returns:
            Dictionary with summary metrics
        """
        try:
            # Get today's date and previous periods
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            thirty_days_ago = today - timedelta(days=30)
            previous_thirty_days = thirty_days_ago - timedelta(days=30)
            
            # Appointments booked today (using BookModel creation date)
            today_appointments = (
                self.db.query(func.count(BookingDetail.id))
                .join(BookModel, BookModel.id == BookingDetail.book_id)
                .filter(
                    BookModel.business_phone_number == business_phone,
                    func.date(BookModel.created_at) == today.date()
                )
                .scalar() or 0
            )
            
            # Appointments booked yesterday
            yesterday_appointments = (
                self.db.query(func.count(BookingDetail.id))
                .join(BookModel, BookModel.id == BookingDetail.book_id)
                .filter(
                    BookModel.business_phone_number == business_phone,
                    func.date(BookModel.created_at) == yesterday.date()
                )
                .scalar() or 0
            )
            
            # Appointments booked in the last 30 days
            thirty_day_appointments = (
                self.db.query(func.count(BookingDetail.id))
                .join(BookModel, BookModel.id == BookingDetail.book_id)
                .filter(
                    BookModel.business_phone_number == business_phone,
                    BookModel.created_at >= thirty_days_ago,
                    BookModel.created_at <= today
                )
                .scalar() or 0
            )
            
            # Appointments booked in the previous 30 days (for comparison)
            previous_thirty_day_appointments = (
                self.db.query(func.count(BookingDetail.id))
                .join(BookModel, BookModel.id == BookingDetail.book_id)
                .filter(
                    BookModel.business_phone_number == business_phone,
                    BookModel.created_at >= previous_thirty_days,
                    BookModel.created_at <= thirty_days_ago
                )
                .scalar() or 0
            )
            
            # Customer statistics
            customer_stats = self.get_customer_statistics(business_phone)
            
            # Calculate growth rate
            growth_rate = 0
            if previous_thirty_day_appointments > 0:
                growth_rate = ((thirty_day_appointments - previous_thirty_day_appointments) 
                              / previous_thirty_day_appointments) * 100
            
            return {
                "today_appointments": today_appointments,
                "yesterday_appointments": yesterday_appointments,
                "thirty_day_appointments": thirty_day_appointments,
                "thirty_day_growth_rate": round(growth_rate, 2),
                "customer_stats": customer_stats
            }
            
        except Exception as e:
            main_logger.error(f"Error getting dashboard summary: {str(e)}")
            return {
                "today_appointments": 0,
                "yesterday_appointments": 0,
                "thirty_day_appointments": 0,
                "thirty_day_growth_rate": 0,
                "customer_stats": {
                    "total_customers": 0,
                    "new_customers_30d": 0,
                    "returning_customers": 0,
                    "retention_rate": 0
                }
            }
    
    def get_business_customers(self, business_phone: str, page: int = 1, page_size: int = 10):
        """
        Get all customers for a business with pagination
        
        Args:
            business_phone: The business phone number
            page: Page number (1-based)
            page_size: Number of customers per page
            
        Returns:
            Dictionary with paginated customer list and count
        """
        try:
            # First, get the business_id from the business_phone
            business = self.db.query(Business).filter(Business.whatsapp_number == business_phone).first()
            
            if not business:
                main_logger.warning(f"No business found with WhatsApp number: {business_phone}")
                return {
                    "total": 0,
                    "customers": []
                }
            
            business_id = business.id
            
            # Calculate offset
            offset = (page - 1) * page_size
            
            # Get total count
            total_count = (
                self.db.query(func.count(CustomerModel.id))
                .filter(CustomerModel.business_id == business_id)
                .scalar() or 0
            )
            
            # Get customers for the current page
            customers_query = (
                self.db.query(CustomerModel)
                .filter(CustomerModel.business_id == business_id)
                .order_by(CustomerModel.created_at.desc())
                .offset(offset)
                .limit(page_size)
            )
            
            customers = customers_query.all()
            
            # Format customer data
            customer_list = []
            for customer in customers:
                # Count bookings for this customer
                booking_count = (
                    self.db.query(func.count(BookModel.id))
                    .filter(BookModel.customer_id == customer.id)
                    .scalar() or 0
                )
                
                # Get most recent booking date
                latest_booking = (
                    self.db.query(BookingDetail.begin_ts)
                    .join(BookModel, BookModel.id == BookingDetail.book_id)
                    .filter(BookModel.customer_id == customer.id)
                    .order_by(BookingDetail.begin_ts.desc())
                    .first()
                )
                
                customer_data = {
                    "id": customer.id,
                    "name": f"{customer.first_name} {customer.last_name}".strip(),
                    "mobile_number": customer.mobile_number,
                    "email": customer.email,
                    "booking_count": booking_count,
                    "latest_booking": str(latest_booking.begin_ts) if latest_booking else None,
                    "created_at": str(customer.created_at)
                }
                
                customer_list.append(customer_data)
            
            return {
                "total": total_count,
                "customers": customer_list
            }
            
        except Exception as e:
            main_logger.error(f"Error getting business customers: {str(e)}")
            return {
                "total": 0,
                "customers": []
            } 