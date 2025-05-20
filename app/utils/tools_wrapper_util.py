import re
import logging
import time
from datetime import datetime, timedelta
from .timezone_util import BERLIN_TZ
from ..core.config import settings
from typing import List, Dict

# Set up logging
logger = logging.getLogger(__name__)

# Remove circular imports - use lazy loading instead
_assistant_manager = None
_chat_agent = None
_timeglobe_service = None


def _get_assistant_manager():
    """Lazy initialization of the AssistantManager to avoid circular imports"""
    global _assistant_manager
    if _assistant_manager is None:
        from ..agent import AssistantManager

    return _assistant_manager


def _get_chat_agent():
    """Lazy initialization of the ChatAgent to avoid circular imports"""
    global _chat_agent
    if _chat_agent is None:
        from ..chat_agent import ChatAgent
        from ..core.config import settings
        from ..db.session import SessionLocal
        
        # Create a new session for the chat agent
        db = SessionLocal()
        _chat_agent = ChatAgent(db=db)  # No need to pass the API key, it will use from settings
    return _chat_agent


def _get_timeglobe_service():
    """Lazy initialization of the TimeGlobeService to avoid circular imports"""
    global _timeglobe_service
    if _timeglobe_service is None:
        from ..services.timeglobe_service import TimeGlobeService

        _timeglobe_service = TimeGlobeService()
    return _timeglobe_service


def get_sites():
    """Get a list of available salons"""
    logger.info("Tool called: get_sites()")
    start_time = time.time()
    try:
        sites = _get_timeglobe_service().get_sites()
        execution_time = time.time() - start_time
        logger.info(f"get_sites() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "sites": sites}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_sites(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def get_products(siteCd: str):
    """Get a list of available services for a specific salon"""
    logger.info(f"Tool called: get_products(siteCd={siteCd})")
    start_time = time.time()
    try:
        products = _get_timeglobe_service().get_products(siteCd)
        execution_time = time.time() - start_time
        logger.info(f"get_products() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "products": products}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_products(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def get_employee(items, siteCd,week):
    """Get a list of available employees for a specific service.
     Parameters:
    items (int): The item number of the selected service for which employees are to be retrieved.
    siteCd (str): The siteCd of the salon"""
    logger.info(f"Tool called: get_employee(items={items}, siteCd={siteCd},week={week})")
    start_time = time.time()
    try:
        employees = _get_timeglobe_service().get_employee(items, siteCd,week)
        execution_time = time.time() - start_time
        logger.info(f"get_employee() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "employees": employees}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_employee(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def AppointmentSuggestion(week, employeeid, itemno, siteCd: str):
    """Get available appointment slots for a selected employee,service and salon"""
    logger.info(
        f"Tool called: AppointmentSuggestion(week={week}, employeeid={employeeid}, itemno={itemno}, siteCd={siteCd})"
    )
    start_time = time.time()
    try:
        suggestions = _get_timeglobe_service().AppointmentSuggestion(
            week=week,
            employee_id=employeeid, 
            item_no=itemno, 
            siteCd=siteCd
        )
        execution_time = time.time() - start_time
        logger.info(
            f"AppointmentSuggestion() completed successfully in {execution_time:.2f}s"
        )
        return {"status": "success", "suggestions": suggestions}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            f"Error in AppointmentSuggestion(): {str(e)} - took {execution_time:.2f}s"
        )
        return {"status": "error", "message": str(e)}


def book_appointment(
    mobileNumber: str,
    siteCd: str,
    positions: list,
    reminderSms: bool = True,
    reminderEmail: bool = True,
    business_phone_number: str = None
):
    """Book appointments with the selected parameters. Supports multiple positions."""
    logger.info(
        f"Tool called: book_appointment(positions={positions}, siteCd={siteCd}, business_phone_number={business_phone_number})"
    )
    start_time = time.time()
    try:
        # Format mobile number if needed
        if not mobileNumber.startswith("+"):
            mobileNumber = f"+{mobileNumber}"
            
        # Validate each position has required fields
        required_fields = ["beginTs", "durationMillis", "employeeId", "itemNo", "ordinalPosition"]
        for pos in positions:
            missing = [k for k in required_fields if k not in pos]
            if missing:
                logger.warning(f"Missing required fields in position: {missing}")
                return {"status": "error", "message": f"Missing required fields in position: {missing}"}
            
            # Ensure itemNm is present, use itemNo as fallback
            if "itemNm" not in pos or not pos["itemNm"]:
                pos["itemNm"] = f"Service {pos.get('itemNo')}"
                logger.info(f"Added default itemNm for itemNo: {pos.get('itemNo')}")
                
            logger.info(f"Processing appointment with date and time={pos.get('beginTs')}")

        # Call the service function with multiple positions
        result = _get_timeglobe_service().book_appointment(
            mobileNumber=mobileNumber,
            siteCd=siteCd,
            positions=positions,
            reminderSms=reminderSms,
            reminderEmail=reminderEmail,
            business_phone_number=business_phone_number
        )
        
        execution_time = time.time() - start_time
        if result.get("code") == 90:
            logger.info(
                f"book_appointment() - user already has 2 appointments - took {execution_time:.2f}s"
            )
            return {
                "status": "success",
                "booking_result": "you already have 2 appointments in future \
            in order to make another appointment please cancel one of them.",
            }
        elif result.get("code") == 0:
            order_id = result.get("orderId")
            logger.info(
                f"book_appointment() - appointment booked successfully (orderID: {order_id}) - took {execution_time:.2f}s"
            )
            return {
                "status": "success",
                "booking_result": f"appointment booked successfully orderID is {order_id}",
            }
        else:
            logger.warning(
                f"book_appointment() - unexpected code: {result.get('code')} - took {execution_time:.2f}s"
            )
            return {
                "status": "error",
                "message": f"Unexpected response code: {result.get('code')}",
            }
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            f"Error in book_appointment(): {str(e)} - took {execution_time:.2f}s"
        )
        return {"status": "error", "message": str(e)}


def cancel_appointment(orderId, mobileNumber, siteCd):
    """Cancel an existing appointment"""
    logger.info(f"Tool called: cancel_appointment(orderId={orderId},sitecode={siteCd})")
    
    start_time = time.time()
    try:    
        if not orderId:
            logger.warning("cancel_appointment() called without orderId")
            return {"status": "error", "message": "orderId is required"}

        result = _get_timeglobe_service().cancel_appointment(
            orderId=orderId, mobileNumber=mobileNumber, siteCd=siteCd
        )
        execution_time = time.time() - start_time

        if result.get("code") == 0:
            logger.info(
                f"cancel_appointment() - appointment cancelled successfully - took {execution_time:.2f}s"
            )
            return {
                "status": "success",
                "message": "your appointment has been cancelled.",
            }
        else:
            logger.warning(
                f"cancel_appointment() - invalid appointment ID - took {execution_time:.2f}s"
            )
            return {
                "status": "success",
                "cancellation_result": "The provided id is not valid appointment id",
            }
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            f"Error in cancel_appointment(): {str(e)} - took {execution_time:.2f}s"
        )
        return {"status": "error", "message": str(e)}


def get_profile(mobile_number: str):
    """Get the profile data for a given phone number"""
    logger.info(f"Tool called: get_profile(mobile_number={mobile_number})")
    start_time = time.time()
    try:
        # Get the business phone number from MessageCache
        from .message_cache import MessageCache
        message_cache = MessageCache.get_instance()
        business_phone = message_cache.get_business_phone(mobile_number)
        
        if business_phone:
            logger.info(f"Found business phone {business_phone} for customer {mobile_number}")
        
        # Get TimeGlobe service instance
        service = _get_timeglobe_service()
        
        # Get profile from TimeGlobe API
        profile = service.get_profile(mobile_number, business_phone)
        execution_time = time.time() - start_time

        if profile.get("code") == 0:
            logger.info(
                f"get_profile() - profile retrieved successfully - took {execution_time:.2f}s"
            )
            
            # Ensure profile is saved to local database
            try:
                # The profile should already be saved by the service.get_profile call,
                # but we'll make an explicit call to ensure it's saved
                logger.info(f"Ensuring profile is saved to local database")
                service.timeglobe_repo.create_customer(profile, mobile_number, business_phone)
                logger.info(f"Successfully saved/updated profile in local database")
                if business_phone:
                    logger.info(f"Customer linked to business phone: {business_phone}")
            except Exception as db_error:
                logger.error(f"Error ensuring profile is in local database: {str(db_error)}")
                # Continue even if DB save fails
                
            return {"status": "success", "profile": profile}
        elif profile.get("code") == -3:
            logger.info(
                f"get_profile() - user does not exist - took {execution_time:.2f}s"
            )
            return {
                "status": "success",
                "message": "user with this number does not exist",
            }
        else:
            logger.warning(
                f"get_profile() - error getting user info, code: {profile.get('code')} - took {execution_time:.2f}s"
            )
            return {"status": "success", "message": "there is error getting user info"}

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_profile(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def get_orders(mobile_number: str):
    """Get a list of open appointments"""
    logger.info("Tool called: get_orders()")
    start_time = time.time()
    try:
        orders = _get_timeglobe_service().get_orders(mobile_number=mobile_number)
        execution_time = time.time() - start_time
        logger.info(f"get_orders() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "orders": orders}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_orders(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def get_old_orders(customer_code="demo"):
    """Get a list of past appointments"""
    logger.info(f"Tool called: get_old_orders(customer_code={customer_code})")
    start_time = time.time()
    try:
        old_orders = _get_timeglobe_service().get_old_orders(customer_code)
        execution_time = time.time() - start_time
        logger.info(f"get_old_orders() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "old_orders": old_orders}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            f"Error in get_old_orders(): {str(e)} - took {execution_time:.2f}s"
        )
        return {"status": "error", "message": str(e)}


def store_profile(
    mobile_number: str,
    email: str,
    gender: str,
    title: str,
    full_name: str,
    first_name: str,
    last_name: str,
    dplAccepted: bool = False
):
    """Store user profile"""
    # Handle missing parameters
    if not mobile_number:
        logger.error("store_profile() called without mobile_number")
        return {"status": "error", "message": "Mobile number is required"}

    # Normalize mobile number format - remove spaces and any special chars except +
    if mobile_number:
        mobile_number = "".join(c for c in mobile_number if c.isdigit() or c == "+")

        # Ensure proper international formatting
        if mobile_number.startswith("00"):  # Common format for international numbers
            mobile_number = "+" + mobile_number[2:]
        elif not mobile_number.startswith("+"):
            # Add + if doesn't have country code indicator
            mobile_number = "+" + mobile_number

    # Provide default values for optional parameters
    if not email:
        logger.warning("store_profile() called without email, using default")
        email = None

    if not gender:
        logger.warning("store_profile() called without gender, using default")
        gender = None  # Default to Male

    if not first_name:
        logger.warning("store_profile() called without first_name, using default")
        first_name = None

    if not last_name:
        logger.warning("store_profile() called without last_name, using default")
        last_name = None

    if not full_name:
        logger.warning("store_profile() called without full_name, using default")
        full_name = None
    
    if not dplAccepted:
        logger.warning("store_profile() called without dplAccepted, using default")
        dplAccepted = None

    if not title:
        logger.warning("store_profile() called without title, using default")
        title = None

    logger.info(
        f"Tool called: store_profile(mobile_number={mobile_number}, email={email}, gender={gender}, title={title}, first_name={first_name}, last_name={last_name}, dplAccepted={dplAccepted})"
    )
    start_time = time.time()
    try:
        response = _get_timeglobe_service().store_profile(
            mobile_number, email, gender, title, full_name, first_name, last_name, dplAccepted
        )
        execution_time = time.time() - start_time

        if response.get("code") == 0:
            logger.info(
                f"store_profile() - profile created successfully - took {execution_time:.2f}s"
            )
            return {"status": "success", "message": "profile created successfully"}
        else:
            error_code = response.get("code", "unknown")
            error_msg = response.get("message", "Unknown error")
            logger.warning(
                f"store_profile() - error creating profile, code: {error_code}, message: {error_msg} - took {execution_time:.2f}s"
            )
            return {
                "status": "error",
                "message": f"Error creating profile: {error_msg}",
            }

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in store_profile(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def format_response(text):
    logger.debug(f"Tool called: format_response(text length={len(text) if text else 0})")
    start_time = time.time()
    try:
        # Handle None or empty text
        if not text:
            logger.warning("Empty text passed to format_response")
            return "I'm sorry, I couldn't generate a proper response. Please try again."
            
        final_response = replace_double_with_single_asterisks(text)  # removing single *
        final_response = remove_sources(final_response)  # removing sources if any
        final_response = remove_brackets(
            final_response
        )  # removing brackets before linke
        final_response = remove_small_brackets(
            final_response
        )  # removing small brackets from link
        # remove all ### from the response
        final_response = final_response.replace("### ", "")

        execution_time = time.time() - start_time
        logger.debug(f"format_response() completed in {execution_time:.4f}s")
        return final_response
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            f"Error in format_response(): {str(e)} - took {execution_time:.4f}s"
        )
        return text or "I'm sorry, I couldn't generate a proper response. Please try again."  # Return original text or default message if formatting fails


def replace_double_with_single_asterisks(text):
    return re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)


def remove_sources(text):
    # Use regex to match the pattern 【number:number†filename.extension】
    clean_text = re.sub(r"【\d+:\d+†[^\s]+】", "", text)
    return clean_text


def remove_brackets(text):
    # Use regex to find and remove square brackets and their content
    return re.sub(r"\[.*?\]", "", text)


def remove_small_brackets(text):
    # Use regex to find and remove only the parentheses, but keep the content inside
    return re.sub(r"[()]", "", text)


def format_datetime(user_date_time: str) -> str:
    """
    Converts various user date-time formats to ISO 8601 format using the Berlin timezone.
    Handles formats like:
    - YYYY-MM-DD HH:MM
    - YYYY-MM-DD HH:MM AM/PM
    - Month DD, YYYY HH:MM AM/PM
    - Already ISO 8601 formatted strings (returns as-is)

    Args:
        user_date_time: A string containing date and time

    Returns:
        ISO 8601 formatted string (YYYY-MM-DDT00:00:00.000Z) in Berlin timezone

    Raises:
        ValueError: If the date-time format cannot be parsed
    """
    start_time = time.time()
    logger.info(f"format_datetime() called with input: {user_date_time}")

    # Check if input is already in ISO 8601 format
    iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$"
    if re.match(iso_pattern, user_date_time):
        # Validate it's a real date by parsing and reformatting
        try:
            dt = datetime.strptime(user_date_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=BERLIN_TZ)
            dt = dt.astimezone(BERLIN_TZ)
            result = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            logger.info(f"Input already in ISO format: {user_date_time}")
            return result
        except ValueError:
            try:
                dt = datetime.strptime(user_date_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=BERLIN_TZ)
                dt = dt.astimezone(BERLIN_TZ)
                result = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                logger.info(f"Input already in ISO format: {user_date_time}")
                return result
            except ValueError:
                logger.debug(
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
        logger.debug(f"Split input into date: {user_date} and time: {user_time}")
        # Try both formats from the original function
        try:
            dt = datetime.strptime(f"{user_date} {user_time}", "%Y-%m-%d %H:%M")
            dt = dt.replace(tzinfo=BERLIN_TZ)
            result = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            execution_time = time.time() - start_time
            logger.info(
                f"format_datetime() completed successfully in {execution_time:.4f}s"
            )
            return result
        except ValueError:
            logger.debug(
                "Failed to parse with format %Y-%m-%d %H:%M, trying %Y-%m-%d %I:%M %p"
            )
            try:
                dt = datetime.strptime(f"{user_date} {user_time}", "%Y-%m-%d %I:%M %p")
                dt = dt.replace(tzinfo=BERLIN_TZ)
                result = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                execution_time = time.time() - start_time
                logger.info(
                    f"format_datetime() completed successfully in {execution_time:.4f}s"
                )
                return result
            except ValueError:
                logger.debug(
                    "Failed to parse with both initial formats, continuing to other formats"
                )
                pass  # Continue to the general case

    # Try all formats
    for fmt in formats:
        try:
            logger.debug(f"Trying format: {fmt}")
            dt = datetime.strptime(user_date_time, fmt)
            dt = dt.replace(tzinfo=BERLIN_TZ)
            result = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            execution_time = time.time() - start_time
            logger.info(
                f"format_datetime() completed successfully in {execution_time:.4f}s"
            )
            return result
        except ValueError:
            continue

    # If still no match, try to be more flexible by normalizing the input
    normalized_input = user_date_time.replace(",", "")  # Remove commas
    logger.debug(f"Using normalized input: {normalized_input}")

    # Check for common patterns
    month_pattern = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d{1,2})[\w,]* (\d{4})"
    time_pattern = r"(\d{1,2}):(\d{2})(?:\s*([AP]M))?"

    month_match = re.search(month_pattern, user_date_time, re.IGNORECASE)
    time_match = re.search(time_pattern, user_date_time)

    if month_match and time_match:
        logger.debug("Found month and time patterns in the input")
        month = month_match.group(1)
        day = month_match.group(2)
        year = month_match.group(3)

        hour = time_match.group(1)
        minute = time_match.group(2)
        ampm = time_match.group(3) if time_match.group(3) else ""

        logger.debug(
            f"Extracted components - Month: {month}, Day: {day}, Year: {year}, Hour: {hour}, Minute: {minute}, AM/PM: {ampm}"
        )

        try:
            date_str = f"{month} {day} {year} {hour}:{minute} {ampm}".strip()
            format_str = "%b %d %Y %I:%M %p" if ampm else "%b %d %Y %H:%M"
            logger.debug(
                f"Attempting to parse: '{date_str}' with format: '{format_str}'"
            )

            dt = datetime.strptime(date_str, format_str)
            dt = dt.replace(tzinfo=BERLIN_TZ)
            result = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            execution_time = time.time() - start_time
            logger.info(
                f"format_datetime() completed successfully in {execution_time:.4f}s"
            )
            return result
        except ValueError as e:
            logger.debug(f"Failed to parse extracted components: {e}")
            pass

    # If we get here, no format matched
    execution_time = time.time() - start_time
    logger.error(
        f"Invalid date-time format: {user_date_time} (processing took {execution_time:.4f}s)"
    )
    raise ValueError(f"Invalid date-time format: {user_date_time}")


def get_response_from_gpt(msg, user_id, _assistant_manager=None):
    logger.info(f"Tool called: get_response_from_gpt(user_id={user_id})")
    start_time = time.time()
    try:
        # Get business phone number from cache
        from .message_cache import MessageCache
        message_cache = MessageCache.get_instance()
        business_phone = message_cache.get_business_phone(user_id)
        
        if business_phone:
            logger.info(f"Retrieved business phone {business_phone} for user {user_id}")
            # Add business phone number to the message context
            msg = f"{msg}\n\nBUSINESS_PHONE:{business_phone}"
            logger.debug(f"Updated message with business phone: {msg}")
        
        # Use the new ChatAgent instead of AssistantManager
        chat_agent = _get_chat_agent()
        response = chat_agent.run_conversation(user_id, msg)
        execution_time = time.time() - start_time
        logger.info(
            f"get_response_from_gpt() for user {user_id} completed in {execution_time:.2f}s"
        )
        return response
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            f"Error in get_response_from_gpt(): {str(e)} - took {execution_time:.2f}s"
        )
        return f"Error processing request: {str(e)}"


# Function aliases to match the German function names
def getSites():
    return get_sites()

def getProducts(siteCd: str):
    return get_products(siteCd)

def getEmployees(siteCd: str, week: int, items: List[str]):
    # Convert to match the original get_employee format
    if len(items) > 0:
        # Currently our implementation takes a single item, so use the first one
        return get_employee(items, siteCd, week)
    return {"status": "error", "message": "No items specified"}

def getProfile(mobile_number:str=None):
    """Wrapper for get_profile that accepts mobile_number"""
    # Directly call the timeglobe_service method to avoid recursive calls
    try:
        # Make sure we have a valid mobile number
        if not mobile_number:
            mobile_number = ""
        logger.info(f"getProfile wrapper called with mobile_number={mobile_number}")
        
        # Get the business phone number from MessageCache
        from .message_cache import MessageCache
        message_cache = MessageCache.get_instance()
        business_phone = message_cache.get_business_phone(mobile_number)
        
        if business_phone:
            logger.info(f"Found business phone {business_phone} for customer {mobile_number}")
        
        # Get the TimeGlobe service instance
        service = _get_timeglobe_service()
        
        # Call the service to get the profile with business phone
        response = service.get_profile(mobile_number, business_phone)
        
        # Ensure profile data is stored in local database if valid
        if response and response.get("code") != -3:
            logger.info(f"Valid profile found for {mobile_number}, ensuring it's saved to local DB")
            try:
                # Get the repository from the service to avoid creating a new one
                repo = service.timeglobe_repo
                repo.create_customer(response, mobile_number, business_phone)
                logger.info(f"Successfully saved/updated profile in local database")
                if business_phone:
                    logger.info(f"Customer linked to business phone: {business_phone}")
            except Exception as db_error:
                logger.error(f"Error saving profile to local database: {str(db_error)}")
                # Continue even if saving to DB fails - we still want to return the profile
        
        return response
    except Exception as e:
        logger.error(f"Error in getProfile wrapper: {str(e)}")
        return {"status": "error", "message": f"Error retrieving profile: {str(e)}"}

def getOrders(mobile_number:str=None):
    """Wrapper for get_orders that accepts mobile_number"""
    # Directly call the timeglobe_service method to avoid recursive calls
    try:
        # Make sure we have a valid mobile number
        if not mobile_number:
            mobile_number = ""
        logger.info(f"getOrders wrapper called with mobile_number={mobile_number}")
        return _get_timeglobe_service().get_orders(mobile_number)
    except Exception as e:
        logger.error(f"Error in getOrders wrapper: {str(e)}")
        return {"status": "error", "message": f"Error retrieving orders: {str(e)}"}

def AppointmentSuggestion_wrapper(siteCd: str, week: int, positions: List[Dict]):
    """Wrapper for AppointmentSuggestion to match the new schema"""
    # Check if positions are provided
    if not positions or len(positions) == 0:
        return {"status": "error", "message": "No positions specified"}
    
    # Process all positions
    try:
        service = _get_timeglobe_service()
        # Call the service method directly with all positions
        suggestions = service.AppointmentSuggestion(
            week=week,
            siteCd=siteCd,
            positions=positions
        )
        return {"status": "success", "suggestions": suggestions}
    except Exception as e:
        logger.error(f"Error in AppointmentSuggestion_wrapper: {str(e)}")
        return {"status": "error", "message": str(e)}

def bookAppointment(siteCd: str, reminderSms: bool, reminderEmail: bool, positions: List[Dict], customerId: str = None, business_phone_number: str = None):
    """Wrapper for book_appointment that handles multiple positions"""
    if not positions or len(positions) == 0:
        return {"status": "error", "message": "No positions specified"}
    
    # Pass all positions to the booking function
    return book_appointment(
        mobileNumber=customerId,
        siteCd=siteCd,
        positions=positions,
        reminderSms=reminderSms,
        reminderEmail=reminderEmail,
        business_phone_number=business_phone_number
    )

def cancelAppointment(siteCd: str, orderId: int, mobileNumber: str = ""):
    # The mobileNumber will be provided by the handler
    return cancel_appointment(orderId=str(orderId), mobileNumber=mobileNumber, siteCd=siteCd)

def store_profile_wrapper(fullNm=None, email=None, gender=None, title=None, first_name=None, last_name=None, dplAccepted=None, mobile_number=None):
    """Wrapper for store_profile that accepts German schema parameters"""
    # Map the German parameters to the existing function
    return store_profile(
        mobile_number=mobile_number or "",
        email=email or "",
        gender=gender or "M",
        title=title or "",
        full_name=fullNm or "",
        first_name=first_name or "",
        last_name=last_name or "",
        dplAccepted=dplAccepted or False
    )
