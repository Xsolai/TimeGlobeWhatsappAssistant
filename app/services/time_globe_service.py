from ..core.config import settings
import requests, time, json
from fastapi import HTTPException, status
from ..utils import tools_wrapper_util
from ..repositories.time_globe_repository import TimeGlobeRepository
from ..db.session import get_db


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

        payload = {
            "customerCd": "demo",
            "loginNm": self.username,
            "password": self.password,
        }
        response = requests.post(url=self.base_url + "/auth/login", json=payload)
        if response.status_code == 200:
            self.token = response.json().get("jwt")
            self.expire_time = time.time() + 3600  # 1 hour
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to login"
            )

    def get_token(self) -> str:
        """Return a valid token, refreshing if expired"""
        if not self.token or time.time() > self.expire_time:
            self.login()
        return self.token

    def request(self, method: str, endpoint: str, data=None):
        """Generic method to make authenticated requests."""

        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json",
            "x-book-auth-key": settings.TIME_GLOBE_API_KEY,
            "x-book-login-nm": self.mobile_number,
        }
        url = f"{self.base_url}{endpoint}"
        print(data)
        if data:
            response = requests.request(
                method=method, url=url, json=data, headers=headers
            )
        else:
            response = requests.request(method=method, url=url, headers=headers)

        print("resquest==>>", response.request.body)
        if response.status_code in [401, 500]:  # token expire or invalid, refresh token
            self.login()
            response = requests.request(
                method=method, url=url, json=data, headers=headers
            )
        print(f"response===>> {response.text}")
        return response.json()

    def get_sites(self):
        """get the available salon

        Returns:
            an array with available salons
        """
        payload = {"customerCd": "demo"}
        response = self.request("POST", "/browse/getSites", data=payload)
        sites = []
        for item in response.get("sites"):
            sites.append(
                {"salon name": item.get("siteNm"), "siteCd": item.get("siteCd")}
            )
        return sites

    def get_products(self, site_code: str = "bonn"):
        """Retrieves a list of available services for a studio"""
        self.site_code = site_code
        payload = {"customerCd": "demo", "siteCd": site_code}
        response = self.request("POST", "/browse/getProducts", data=payload)
        print("response==>>", response)
        return response

    def get_employee(self, item_no: str, item_name: str):
        """Retrieves a list of available employees for a studio."""
        payload = {
            "customerCd": "demo",
            "siteCd": self.site_code,
            "week": 0,
            "items": [item_no],
        }
        self.item_no = item_no
        self.item_name = item_name
        response = self.request("POST", "/browse/getEmployees", data=payload)
        return response

    def get_suggestions(self, employee_id: int):
        """Retrieves available appointment slots for selected services."""
        self.employee_id = employee_id
        payload = {
            "customerCd": "demo",
            "siteCd": self.site_code,
            "week": 0,
            "positions": [{"itemNo": self.item_no, "employeeId": employee_id}],
        }
        response = self.request("POST", "/browse/getSuggestions", data=payload)
        return response

    def get_profile(self, customer_code: str = "demo"):
        """Retrieves user profile"""
        payload = {"customerCd": customer_code}
        response = self.request("POST", "/account/getProfile", data=payload)
        return response

    def get_profile_data(self, mobile_number: str):
        """Retrieves the profile data for a given phone number"""
        self.mobile_number = mobile_number
        response = self.request(method="POST", endpoint="/bot/getProfile")
        return response

    def get_orders(self, customer_code: str = "demo"):
        """Retrieves a list of open appointments."""
        payload = {"customerCd": customer_code}
        response = self.request("POST", "/book/getOrders", data=payload)
        return response

    def get_old_orders(self, customer_code: str = "demo"):
        """Retrieves a list of past appointments."""
        payload = {"customerCd": customer_code}
        response = self.request("POST", "/book/getOldOrders", data=payload)
        return response

    def book_appointment(
        self,
        duration: int,
        user_date: str,
        user_time: str,
    ):
        """Books an appointment

        Args:
            duration (integer):when user select the duration convert this to milisecond and then pass it.
            user_date (str): required
            user_time (str):required
        """
        formatted_datetime = tools_wrapper_util.format_datetime(user_date, user_time)
        payload = {
            "customerCd": "demo",
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
        self.time_globe_repo.save_book_appointement(payload)
        response = self.request("POST", "/book/book", data=payload)
        return response

    def cancel_appointment(self, order_id: int):
        """Cancels an existing appointment."""
        payload = {
            "customerCd": "demo",
            "siteCd": self.site_code,
            "orderId": order_id,
        }
        response = self.request("POST", "/book/cancel", data=payload)
        return response

    def store_profile(
        self,
        mobile_number: str,
        email: str,
        gender: str,
        first_name: str,
        last_name: str,
    ):
        """Store user profile"""
        self.mobile_number = mobile_number
        full_name = first_name + " " + last_name
        payload = {
            "salutationCd": gender,
            "email": email,
            "fullNm": full_name,
            "firstNm": first_name,
            "lastNm": last_name,
        }
        response = self.request("POST", "/bot/storeProfileData", data=payload)
        # self.time_globe_repo.create_customer(
        #     payload.update(["mobile_number", self.mobile_number])
        # )

        return response
