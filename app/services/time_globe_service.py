from ..core.config import settings
import requests, time, json
from fastapi import HTTPException, status
from ..repositories.time_globe_repository import TimeGlobeRepository
from ..db.session import get_db
from ..logger import main_logger
from datetime import datetime
import re


# Add a local format_datetime function to avoid circular imports
def format_datetime(user_date_time: str) -> str:
    """
    Converts various user date-time formats to ISO 8601 format.
    Handles formats like:
    - YYYY-MM-DD HH:MM
    - YYYY-MM-DD HH:MM AM/PM
    - Month DD, YYYY HH:MM AM/PM
    - Already ISO 8601 formatted strings (returns as-is)

    Args:
        user_date_time: A string containing date and time

    Returns:
        ISO 8601 formatted string (YYYY-MM-DDT00:00:00.000Z)

    Raises:
        ValueError: If the date-time format cannot be parsed
    """
    start_time = time.time()
    main_logger.info(f"format_datetime() called with input: {user_date_time}")

    # Check if input is already in ISO 8601 format
    iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$"
    if re.match(iso_pattern, user_date_time):
        # Validate it's a real date by parsing and reformatting
        try:
            dt = datetime.strptime(user_date_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            main_logger.info(f"Input already in ISO format: {user_date_time}")
            return user_date_time
        except ValueError:
            try:
                dt = datetime.strptime(user_date_time, "%Y-%m-%dT%H:%M:%SZ")
                main_logger.info(f"Input already in ISO format: {user_date_time}")
                return user_date_time
            except ValueError:
                main_logger.debug(
                    "Input matched ISO pattern but failed validation, trying other formats"
                )
                pass  # Not a valid ISO format, continue with other formats

    formats = [
        # YYYY-MM-DD formats
        "%Y-%m-%d %H:%M",  # 2025-03-21 14:00
        "%Y-%m-%d %I:%M %p",  # 2025-03-21 02:00 PM
        # Month name formats
        "%B %d, %Y %I:%M %p",  # March 21, 2025 10:00 AM
        "%b %d, %Y %I:%M %p",  # Mar 21, 2025 10:00 AM
        # Additional formats with various separators
        "%Y/%m/%d %H:%M",  # 2025/03/21 14:00
        "%d/%m/%Y %H:%M",  # 21/03/2025 14:00
        "%m/%d/%Y %I:%M %p",  # 03/21/2025 02:00 PM
        "%d-%b-%Y %I:%M %p",  # 21-Mar-2025 02:00 PM
    ]

    # If input contains separate date and time parameters
    if " " in user_date_time and len(user_date_time.split(" ")) == 2:
        user_date, user_time = user_date_time.split(" ", 1)
        main_logger.debug(f"Split input into date: {user_date} and time: {user_time}")
        # Try both formats from the original function
        try:
            dt = datetime.strptime(f"{user_date} {user_time}", "%Y-%m-%d %H:%M")
            result = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            execution_time = time.time() - start_time
            main_logger.info(
                f"format_datetime() completed successfully in {execution_time:.4f}s"
            )
            return result
        except ValueError:
            main_logger.debug(
                "Failed to parse with format %Y-%m-%d %H:%M, trying %Y-%m-%d %I:%M %p"
            )
            try:
                dt = datetime.strptime(f"{user_date} {user_time}", "%Y-%m-%d %I:%M %p")
                result = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                execution_time = time.time() - start_time
                main_logger.info(
                    f"format_datetime() completed successfully in {execution_time:.4f}s"
                )
                return result
            except ValueError:
                main_logger.debug(
                    "Failed to parse with both initial formats, continuing to other formats"
                )
                pass  # Continue to the general case

    # Try all formats
    for fmt in formats:
        try:
            main_logger.debug(f"Trying format: {fmt}")
            dt = datetime.strptime(user_date_time, fmt)
            result = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            execution_time = time.time() - start_time
            main_logger.info(
                f"format_datetime() completed successfully in {execution_time:.4f}s"
            )
            return result
        except ValueError:
            continue

    # If still no match, try to be more flexible by normalizing the input
    normalized_input = user_date_time.replace(",", "")  # Remove commas
    main_logger.debug(f"Using normalized input: {normalized_input}")

    # Check for common patterns
    month_pattern = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d{1,2})[\w,]* (\d{4})"
    time_pattern = r"(\d{1,2}):(\d{2})(?:\s*([AP]M))?"

    month_match = re.search(month_pattern, user_date_time, re.IGNORECASE)
    time_match = re.search(time_pattern, user_date_time)

    if month_match and time_match:
        main_logger.debug("Found month and time patterns in the input")
        month = month_match.group(1)
        day = month_match.group(2)
        year = month_match.group(3)

        hour = time_match.group(1)
        minute = time_match.group(2)
        ampm = time_match.group(3) if time_match.group(3) else ""

        main_logger.debug(
            f"Extracted components - Month: {month}, Day: {day}, Year: {year}, Hour: {hour}, Minute: {minute}, AM/PM: {ampm}"
        )

        try:
            date_str = f"{month} {day} {year} {hour}:{minute} {ampm}".strip()
            format_str = "%b %d %Y %I:%M %p" if ampm else "%b %d %Y %H:%M"
            main_logger.debug(
                f"Attempting to parse: '{date_str}' with format: '{format_str}'"
            )

            dt = datetime.strptime(date_str, format_str)
            result = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            execution_time = time.time() - start_time
            main_logger.info(
                f"format_datetime() completed successfully in {execution_time:.4f}s"
            )
            return result
        except ValueError as e:
            main_logger.debug(f"Failed to parse extracted components: {e}")
            pass

    # If we get here, no format matched
    execution_time = time.time() - start_time
    main_logger.error(
        f"Invalid date-time format: {user_date_time} (processing took {execution_time:.4f}s)"
    )
    raise ValueError(f"Invalid date-time format: {user_date_time}")


class TimeGlobeService:
    def __init__(self):
        self.base_url = settings.TIME_GLOBE_BASE_URL
        self.username = settings.TIME_GLOBE_LOGIN_USERNAME
        self.password = settings.TIME_GLOBE_LOGIN_PASSWORD
        self.time_globe_repo = TimeGlobeRepository(next(get_db()))
        self.token = None
        self.expire_time = 3600  # 1 hour
        # self.siteCd = "bonn"  # None
        # self.item_no = None
        # self.employee_id = None
        # self.item_name = None
        # self.mobile_number = None

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

    def request(
        self,
        method: str,
        endpoint: str,
        mobile_number: str = None,
        data=None,
        is_header=False,
    ):
        """Generic method to make authenticated requests."""
        main_logger.debug(f"Making {method} request to {endpoint}")
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "x-book-auth-key": settings.TIME_GLOBE_API_KEY,
            "x-book-login-nm": mobile_number,
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

    def get_products(self, siteCd: str):
        """Retrieve a list of available services for a selected salon."""
        main_logger.debug(f"Fetching products for site: {siteCd}")
        # self.siteCd = siteCd
        payload = {"customerCd": "demo", "siteCd": siteCd}
        response = self.request("POST", "/browse/getProducts", data=payload)
        main_logger.info(f"Successfully fetched products for site: {siteCd}")
        return response

    def get_employee(self, items: str, siteCd: str,week: int):
        """Retrieve a list of available employees for a studio."""
        main_logger.debug(f"Fetching employees for item: {items}")
        payload = {
            "customerCd": "demo",
            "siteCd": siteCd,
            "week": week,
            "items": items,
        }
        # self.item_no = item_no
        # self.item_name = item_name
        response = self.request("POST", "/browse/getEmployees", data=payload)
        main_logger.info(f"Successfully fetched employees for item: {items}")
        return response

    def AppointmentSuggestion(self, week: int, employee_id: int, item_no: int, siteCd: str):
        """Retrieve available appointment slots for selected services."""
        main_logger.debug(f"Fetching suggestions for employee: {employee_id}")
        # self.employee_id = employee_id
        payload = {
            "customerCd": "demo",
            "siteCd": siteCd,
            "week": week,
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
        # self.mobile_number = mobile_number
        response = self.request(
            method="POST",
            endpoint="/bot/getProfile",
            mobile_number=mobile_number,
            is_header=True,
        )

        if response and response.get("code") != -3:
            main_logger.info(f"Profile found for mobile number: {mobile_number}")
            self.time_globe_repo.create_customer(response, mobile_number)
        else:
            main_logger.warning(f"No profile found for mobile number: {mobile_number}")

        return response

    def get_orders(self, mobile_number):
        """Retrieve a list of open appointments."""
        main_logger.debug("Fetching open orders")
        response = self.request(
            "POST", "/bot/getOrders", is_header=True, mobile_number=mobile_number
        )
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
        beginTs: str,
        durationMillis: int,
        mobileNumber: str,
        employeeId: int,
        itemNo: int,
        siteCd: str,
    ):
        """Book an appointment."""
        main_logger.debug("Booking appointment")
        try:
            # main_logger.debug(f"Formatting date/time: {user_date_time}")
            # formatted_datetime = format_datetime(user_date_time)
            main_logger.debug(f"datetime: {beginTs}")

            payload = {
                "siteCd": siteCd,
                "reminderSms": True,
                "reminderEmail": True,
                "positions": [
                    {
                        "beginTs": beginTs,  # "2025-02-25T12:00:00.000Z"
                        "durationMillis": durationMillis,
                        "employeeId": employeeId,
                        "itemNo": itemNo,
                    }
                ],
            }
            
            response = self.request(
                "POST",
                "/bot/book",
                data=payload,
                is_header=True,
                mobile_number=mobileNumber,
            )
            if response.get("code") == 0:
                main_logger.info("Appointment booked successfully")
                payload.update(
                    {
                        "mobileNumber": mobileNumber,
                        "orderId": response.get("orderId")
                    }
                )
                self.time_globe_repo.save_book_appointment(payload)
            else:
                main_logger.error(f"Failed to book appointment: {response}")
            return response
        except Exception as e:
            main_logger.error(f"Error in book_appointment: {str(e)}")
            raise

    def cancel_appointment(self, orderId: int, mobileNumber: str, siteCd):
        """Cancel an existing appointment."""
        main_logger.debug(f"Canceling appointment with order ID: {orderId}")
        payload = {
            "siteCd": siteCd,
            "orderId": orderId,
        }
        response = self.request(
            "POST",
            "/bot/cancel",
            data=payload,
            is_header=True,
            mobile_number=mobileNumber,
        )
        if response.get("code") == 0:
            main_logger.info(f"Appointment canceled successfully: {orderId}")
            self.time_globe_repo.delete_booking(orderId)
        else:
            main_logger.error(f"Failed to cancel appointment: {orderId}")
        return response

    def store_profile(
        self,
        mobile_number: str,
        email: str,
        gender: str,
        full_name: str,
        first_name: str,
        last_name: str,
    ):
        """Store user profile."""
        main_logger.debug(f"Storing profile for mobile number: {mobile_number}")

        # Ensure mobile number is properly formatted (remove leading zeroes, ensure country code, etc.)
        if mobile_number.startswith("0"):
            mobile_number = mobile_number[1:]  # Remove leading zero
        if not mobile_number.startswith("+"):
            # Add + if missing (commonly expected format for international numbers)
            mobile_number = "+" + mobile_number

        # self.mobile_number = mobile_number
        # full_name = first_name + " " + last_name

        # Create the payload with proper field names
        payload = {
            "salutationCd": gender,
            "email": email,
            "fullNm": full_name,
            "firstNm": first_name,
            "lastNm": last_name,
        }

        # Add extra debugging
        main_logger.debug(f"Sending profile data to API: {payload}")

        try:
            response = self.request(
                "POST",
                "/bot/storeProfileData",
                data=payload,
                is_header=True,
                mobile_number=mobile_number,
            )

            # Check for specific response patterns
            main_logger.debug(f"API response for store_profile: {response}")

            if response and isinstance(response, dict):
                code = response.get("code")
                main_logger.info(f"Profile API response code: {code}")

                if code == 0:
                    main_logger.info(
                        f"Profile stored successfully in API: {mobile_number}"
                    )
                    # Make sure customer data has the right field names for the repository
                    customer_data = {
                        "salutationCd": gender,
                        "email": email,
                        "fullNm": full_name,
                        "firstNm": first_name,
                        "lastNm": last_name,
                    }
                    self.time_globe_repo.create_customer(customer_data, mobile_number)
                    return {"code": 0, "message": "Profile created successfully"}
                else:
                    main_logger.error(f"API returned error code: {code}")
                    return response
            else:
                main_logger.error(f"Invalid response from API: {response}")
                return {"code": -1, "message": "Invalid response from API"}
        except Exception as e:
            main_logger.error(f"Error storing profile: {str(e)}")
            return {"code": -1, "message": f"Error: {str(e)}"}
