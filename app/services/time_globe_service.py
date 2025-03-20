from ..core.config import settings
import requests, time, json
from fastapi import HTTPException, status
from ..repositories.time_globe_repository import TimeGlobeRepository
from ..db.session import get_db
from ..logger import main_logger
from datetime import datetime


# Add a local format_datetime function to avoid circular imports
def format_datetime(user_date: str, user_time: str) -> str:
    """Converts user-selected date (YYYY-MM-DD) and time (HH:MM or HH:MM AM/PM) to ISO 8601 format."""
    try:
        # Try parsing in 24-hour format first
        dt = datetime.strptime(f"{user_date} {user_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            # If it fails, try parsing in 12-hour format
            dt = datetime.strptime(f"{user_date} {user_time}", "%Y-%m-%d %I:%M %p")
        except ValueError:
            raise ValueError(f"Invalid date-time format: {user_date} {user_time}")

    # Convert to ISO 8601 format
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


class TimeGlobeService:
    def __init__(self):
        self.base_url = settings.TIME_GLOBE_BASE_URL
        self.username = settings.TIME_GLOBE_LOGIN_USERNAME
        self.password = settings.TIME_GLOBE_LOGIN_PASSWORD
        self.time_globe_repo = TimeGlobeRepository(next(get_db()))
        self.token = None
        self.expire_time = 3600  # 1 hour
        self.site_code = "bonn"  # None
        self.item_no = None
        self.employee_id = None
        self.item_name = None
        self.mobile_number = None

    def login(self) -> None:
        """Authenticate and retrieve a new JWT token."""
        main_logger.debug("Attempting to log in to Time Globe API")
        payload = {
            "customerCd": "demo",
            "loginNm": self.username,
            "password": self.password,
        }
        response = requests.post(url=self.base_url + "/auth/login", json=payload)
        if response.status_code == 200:
            self.token = response.json().get("jwt")
            self.expire_time = time.time() + 3600  # 1 hour
            main_logger.info("Successfully logged in to Time Globe API")
        else:
            main_logger.error("Failed to log in to Time Globe API")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to login"
            )

    def get_token(self) -> str:
        """Return a valid token, refreshing if expired."""
        main_logger.debug("Checking token validity")
        if not self.token or time.time() > self.expire_time:
            main_logger.info("Token expired or missing, refreshing token")
            self.login()
        return self.token

    def request(self, method: str, endpoint: str, data=None, is_header=False):
        """Generic method to make authenticated requests."""
        main_logger.debug(f"Making {method} request to {endpoint}")
        headers = {
            "Content-Type": "application/json",
            "x-book-auth-key": settings.TIME_GLOBE_API_KEY,
            "x-book-login-nm": self.mobile_number,
        }
        url = f"{self.base_url}{endpoint}"
        main_logger.debug(f"Request payload: {data}")

        if data:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers if is_header else None,
            )
        else:
            response = requests.request(
                method=method, url=url, headers=headers if is_header else None
            )

        main_logger.debug(f"Response status code: {response.status_code}")
        main_logger.debug(f"Response body: {response.text}")

        if response.status_code in [401, 500]:  # token expired or invalid
            main_logger.warning("Token expired or invalid, attempting to refresh token")
            self.login()
            response = requests.request(
                method=method, url=url, json=data, headers=headers
            )

        return response.json()

    def get_sites(self):
        """Get the available salons."""
        main_logger.debug("Fetching available salons")
        payload = {"customerCd": "demo"}
        response = self.request("POST", "/browse/getSites", data=payload)
        sites = []
        for item in response.get("sites"):
            sites.append(
                {"salon name": item.get("siteNm"), "siteCd": item.get("siteCd")}
            )
        main_logger.info(f"Successfully fetched {len(sites)} salons")
        return sites

    def get_products(self, site_code: str = "bonn"):
        """Retrieve a list of available services for a studio."""
        main_logger.debug(f"Fetching products for site: {site_code}")
        self.site_code = site_code
        payload = {"customerCd": "demo", "siteCd": site_code}
        response = self.request("POST", "/browse/getProducts", data=payload)
        main_logger.info(f"Successfully fetched products for site: {site_code}")
        return response

    def get_employee(self, item_no: str, item_name):
        """Retrieve a list of available employees for a studio."""
        main_logger.debug(f"Fetching employees for item: {item_no}")
        payload = {
            "customerCd": "demo",
            "siteCd": self.site_code,
            "week": 0,
            "items": [item_no],
        }
        self.item_no = item_no
        self.item_name = item_name
        response = self.request("POST", "/browse/getEmployees", data=payload)
        main_logger.info(f"Successfully fetched employees for item: {item_no}")
        return response

    def get_suggestions(self, employee_id: int, item_no: int):
        """Retrieve available appointment slots for selected services."""
        main_logger.debug(f"Fetching suggestions for employee: {employee_id}")
        self.employee_id = employee_id
        payload = {
            "customerCd": "demo",
            "siteCd": self.site_code,
            "week": 0,
            "positions": [{"itemNo": item_no, "employeeId": employee_id}],
        }
        response = self.request("POST", "/browse/getSuggestions", data=payload)
        main_logger.info(
            f"Successfully fetched suggestions for employee: {employee_id}"
        )
        return response

    def get_profile(self, mobile_number: str):
        """Retrieve the profile data for a given phone number."""
        main_logger.debug(f"Fetching profile for mobile number: {mobile_number}")
        self.mobile_number = mobile_number
        response = self.request(
            method="POST", endpoint="/bot/getProfile", is_header=True
        )

        if response and response.get("code") != -3:
            main_logger.info(f"Profile found for mobile number: {mobile_number}")
            self.time_globe_repo.create_customer(response, mobile_number)
        else:
            main_logger.warning(f"No profile found for mobile number: {mobile_number}")

        return response

    def get_orders(self):
        """Retrieve a list of open appointments."""
        main_logger.debug("Fetching open orders")
        response = self.request("POST", "/bot/getOrders", is_header=True)
        main_logger.info("Successfully fetched open orders")
        return response

    def get_old_orders(self, customer_code: str = "demo"):
        """Retrieve a list of past appointments."""
        main_logger.debug("Fetching old orders")
        payload = {"customerCd": customer_code}
        response = self.request("POST", "/book/getOldOrders", data=payload)
        main_logger.info("Successfully fetched old orders")
        return response

    def book_appointment(
        self,
        duration: int,
        user_date: str,
        user_time: str,
    ):
        """Book an appointment."""
        main_logger.debug("Booking appointment")
        try:
            main_logger.debug(f"Formatting date/time: {user_date} {user_time}")
            formatted_datetime = format_datetime(user_date, user_time)
            main_logger.debug(f"Formatted datetime: {formatted_datetime}")
            
            payload = {
                "siteCd": self.site_code,
                "reminderSms": True,
                "reminderEmail": True,
                "positions": [
                    {
                        "ordinalPosition": 1,
                        "beginTs": formatted_datetime,  # "2025-02-25T12:00:00.000Z"
                        "durationMillis": duration,
                        "employeeId": self.employee_id,
                        "itemNo": self.item_no,
                        "itemNm": self.item_name,
                    }
                ],
            }
            response = self.request("POST", "/bot/book", data=payload, is_header=True)
            if response.get("code") == 0:
                main_logger.info("Appointment booked successfully")
                payload.update(
                    {
                        "mobile_number": self.mobile_number,
                        "order_id": response.get("orderId"),
                    }
                )
                self.time_globe_repo.save_book_appointement(payload)
            else:
                main_logger.error(f"Failed to book appointment: {response}")
            return response
        except Exception as e:
            main_logger.error(f"Error in book_appointment: {str(e)}")
            raise

    def cancel_appointment(self, order_id: int):
        """Cancel an existing appointment."""
        main_logger.debug(f"Canceling appointment with order ID: {order_id}")
        payload = {
            "siteCd": self.site_code,
            "orderId": order_id,
        }
        response = self.request("POST", "/bot/cancel", data=payload, is_header=True)
        if response.get("code") == 0:
            main_logger.info(f"Appointment canceled successfully: {order_id}")
            self.time_globe_repo.delete_booking(order_id)
        else:
            main_logger.error(f"Failed to cancel appointment: {order_id}")
        return response

    def store_profile(
        self,
        mobile_number: str,
        email: str,
        gender: str,
        first_name: str,
        last_name: str,
    ):
        """Store user profile."""
        main_logger.debug(f"Storing profile for mobile number: {mobile_number}")
        self.mobile_number = mobile_number
        full_name = first_name + " " + last_name
        payload = {
            "salutationCd": gender,
            "email": email,
            "fullNm": full_name,
            "firstNm": first_name,
            "lastNm": last_name,
        }
        response = self.request(
            "POST", "/bot/storeProfileData", data=payload, is_header=True
        )
        if response:
            main_logger.info(f"Profile stored successfully: {mobile_number}")
            self.time_globe_repo.create_customer(payload, mobile_number)
        else:
            main_logger.error(f"Failed to store profile: {mobile_number}")
        return response
