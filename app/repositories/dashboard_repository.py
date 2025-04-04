from sqlalchemy.orm import Session
from ..models.customer_model import CustomerModel
from ..models.booked_appointment import BookModel
from ..models.booking_detail import BookingDetail
from ..models.services import ServicesModel
from ..models.sender_model import SenderModel
from ..models.user_subscription import UserSubscription
from ..models.subscription_plan import SubscriptionPlan
from datetime import datetime
from ..logger import (
    main_logger,
)
from sqlalchemy import func
from datetime import datetime, timedelta, timezone


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def overview(self, user_id: int):
        try:
            main_logger.info(f"Fetch Dashboard Overview for {user_id}")
            total_bookings = self.db.query(func.count(BookModel.id)).scalar()
            active_bookings = (
                self.db.query(func.count(BookModel.id))
                .join(BookingDetail, BookingDetail.book_id == BookModel.id)
                .filter(BookingDetail.begin_ts > datetime.now())
                .scalar()
            )
            agent_status = (
                self.db.query(SenderModel.status)
                .filter(SenderModel.user_id == user_id)
                .first()
            )
            user_subscription = (
                self.db.query(SubscriptionPlan.name, UserSubscription.end_date)
                .join(UserSubscription)
                .filter(
                    UserSubscription.user_id == user_id,
                    UserSubscription.is_active == True,
                )
                .first()
            )
            if user_subscription:
                subscription_plan, renewal_date = user_subscription
            now = datetime.now()
            start_of_month = datetime(now.year, now.month, 1)
            end_of_month = (
                datetime(now.year, now.month + 1, 1)
                if now.month != 12
                else datetime(now.year + 1, 1, 1)
            )
            total_revenue = (
                self.db.query(
                    func.sum(ServicesModel.min_price).label(
                        "total_revenue"
                    )  # Sum of the service prices
                )
                .join(BookingDetail, BookingDetail.item_no == ServicesModel.item_no)
                .join(BookModel, BookModel.id == BookingDetail.book_id)
                .filter(
                    BookModel.created_at >= start_of_month,
                    BookModel.created_at < end_of_month,
                )
                .scalar()
            )
            return {
                "total_bookings": total_bookings,
                "active_bookings": active_bookings,
                "ai_agent_status": "active" if agent_status == "Online" else "inactive",
                "subscription_plan": subscription_plan,
                "renewal_date": renewal_date.strftime("%Y-%m-%d"),
                "revenue_this_month": total_revenue if total_revenue else 0,
            }
        except Exception as e:
            main_logger.error(f"Error fetching overview: {str(e)}")
            raise Exception(f"Database Error {str(e)}")

    def get_appointments(self, days: int, user_id: int):
        try:
            main_logger.info(f"Fetch appointment for {user_id}")
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            bookings_per_days = (
                self.db.query(
                    BookModel.created_at.label("date"),
                    func.count(BookModel.id).label("bookings"),
                )
                .filter(BookModel.created_at >= start_date)
                .order_by(BookModel.created_at.desc())
                .all()
            )
            main_logger.debug(
                f"Appointments for {user_id} in range {days} : {bookings_per_days}"
            )
            result = [
                {"date": row.date.strftime("%Y-%m-%d"), "bookings": row.bookings}
                for row in bookings_per_days
            ]
            return result
        except Exception as e:
            main_logger.error(f"Error fetching appointment: {str(e)}")
            raise Exception(f"Database Error {str(e)}")

    def get_top_service(self, user_id: int):
        try:
            main_logger.info(f"Fetching booked items count for user_id: {user_id}")
            thirty_days_togo = datetime.now(timezone.utc) - timedelta(days=30)
            booked_items = (
                self.db.query(
                    ServicesModel.item_name, func.count(ServicesModel.item_name)
                )
                .join(BookingDetail, BookingDetail.item_no == ServicesModel.item_no)
                .join(BookModel, BookingDetail.book_id == BookModel.id)
                .filter(BookModel.created_at >= thirty_days_togo)
                .group_by(ServicesModel.item_name)
                .order_by(func.count(ServicesModel.item_name).desc())
                .all()
            )
            item_count_list = [
                {"service": item_name, "count": count}
                for item_name, count in booked_items
            ]
            main_logger.info(
                f"Booked items count for user {user_id} : {item_count_list}"
            )
            return item_count_list

        except Exception as e:
            main_logger.error(f"Error fetching booked items count: {str(e)}")
            raise Exception(f"Database Error {str(e)}")

    def get_top_customer(self, user_id: int):
        try:
            main_logger.info(f"Fetching top customer from DB for {user_id}")
            top_customer = (
                self.db.query(
                    CustomerModel.first_name + " " + CustomerModel.last_name,
                    CustomerModel.mobile_number.label("phone"),
                    func.count(BookModel.customer_id).label("total_bookings"),
                    func.max(BookModel.created_at).label("last_visit"),
                )
                .join(BookModel, BookModel.customer_id == CustomerModel.id)
                .group_by(CustomerModel.id)
                .order_by(func.count(BookModel.customer_id).desc())
                .all()
            )
            main_logger.debug(f"top customers {top_customer}")
            top_customers_dic = [
                {
                    "name": name,
                    "phone": phone,
                    "total_bookings": t_bookings,
                    "last_visit": (
                        last_visit.strftime("%Y-%m-%d") if last_visit else None
                    ),
                }
                for name, phone, t_bookings, last_visit in top_customer
            ]
            return top_customers_dic
        except Exception as e:
            main_logger.error(f"Error fetching top customer: {str(e)}")
            raise Exception(f"Database Error {str(e)}")

    def ai_performance(self, user_id: int):
        try:
            main_logger.info(f"Fetching Perfomance from DB")
            total_bookings = (
                self.db.query(func.count(BookModel.id))
                .join(SenderModel, BookModel.sender_id == SenderModel.id)
                .filter(SenderModel.user_id == user_id)
                .scalar()
            )
            return {"bookings_completed_by_ai": total_bookings}
        except Exception as e:
            main_logger.error(f"Error fetching perfomance: {str(e)}")
            raise Exception(f"Database Error {str(e)}")
