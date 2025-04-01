import re
import logging
import time
from datetime import datetime
from ..core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

# Remove circular imports - use lazy loading instead
_assistant_manager = None
_time_globe_service = None


def _get_assistant_manager():
    """Lazy initialization of the AssistantManager to avoid circular imports"""
    global _assistant_manager
    if _assistant_manager is None:
        from ..agent import AssistantManager

    return _assistant_manager


def _get_time_globe_service():
    """Lazy initialization of the TimeGlobeService to avoid circular imports"""
    global _time_globe_service
    if _time_globe_service is None:
        from ..services.time_globe_service import TimeGlobeService

        _time_globe_service = TimeGlobeService()
    return _time_globe_service


def get_sites():
    """Get a list of available salons"""
    logger.info("Tool called: get_sites()")
    start_time = time.time()
    try:
        sites = _get_time_globe_service().get_sites()
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
        products = _get_time_globe_service().get_products(siteCd)
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
        employees = _get_time_globe_service().get_employee(items, siteCd,week)
        execution_time = time.time() - start_time
        logger.info(f"get_employee() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "employees": employees}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_employee(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def AppointmentSuggestion(customerCd: str, siteCd: str, week: int, positions: list):
    """Get available appointment slots for selected services and optionally specific employees at a given salon"""
    logger.info(
        f"Tool called: AppointmentSuggestion(customerCd={customerCd}, siteCd={siteCd}, week={week}, positions={positions})"
    )
    start_time = time.time()
    try:
        suggestions = _get_time_globe_service().AppointmentSuggestion(
            customerCd=customerCd,
            siteCd=siteCd,
            week=week,
            positions=positions
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
    beginTs,
    durationMillis,
    mobileNumber,
    employeeId,
    itemNo,
    siteCd
):
    """Book an appointment with the selected parameters"""
    logger.info(
        f"Tool called: book_appointment(duration={durationMillis}, user_date_time={beginTs})"
    )
    start_time = time.time()
    try:
        # Try our own date parsing in case there's any issue with the format
        # Used for debug, not actual conversion since time_globe_service has its own format_datetime
        if not isinstance(beginTs, str):
            logger.warning(f"Invalid date/time types: date={type(beginTs)}")
            return {"status": "error", "message": "Date and time must be strings"}

        logger.info(f"Processing appointment with date and time={beginTs}")

        # Call the service function which has a local format_datetime
        result = _get_time_globe_service().book_appointment(
                    beginTs,
                    durationMillis,
                    mobileNumber,
                    employeeId,
                    itemNo,
                    siteCd
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

        result = _get_time_globe_service().cancel_appointment(
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
        profile = _get_time_globe_service().get_profile(mobile_number)
        execution_time = time.time() - start_time

        if profile.get("code") == 0:
            logger.info(
                f"get_profile() - profile retrieved successfully - took {execution_time:.2f}s"
            )
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
        orders = _get_time_globe_service().get_orders(mobile_number=mobile_number)
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
        old_orders = _get_time_globe_service().get_old_orders(customer_code)
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
    full_name: str,
    first_name: str,
    last_name: str,
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
        email = ""

    if not gender:
        logger.warning("store_profile() called without gender, using default")
        gender = "M"  # Default to Male

    if not first_name:
        logger.warning("store_profile() called without first_name, using default")
        first_name = "User"

    if not last_name:
        logger.warning("store_profile() called without last_name, using default")
        last_name = ""

    logger.info(
        f"Tool called: store_profile(mobile_number={mobile_number}, email={email}, gender={gender}, first_name={first_name}, last_name={last_name})"
    )
    start_time = time.time()
    try:
        response = _get_time_globe_service().store_profile(
            mobile_number, email, gender, full_name, first_name, last_name
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
    logger.debug(f"Tool called: format_response(text length={len(text)})")
    start_time = time.time()
    try:
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
        return text  # Return original text if formatting fails


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
    logger.info(f"format_datetime() called with input: {user_date_time}")

    # Check if input is already in ISO 8601 format
    iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$"
    if re.match(iso_pattern, user_date_time):
        # Validate it's a real date by parsing and reformatting
        try:
            dt = datetime.strptime(user_date_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            logger.info(f"Input already in ISO format: {user_date_time}")
            return user_date_time
        except ValueError:
            try:
                dt = datetime.strptime(user_date_time, "%Y-%m-%dT%H:%M:%SZ")
                logger.info(f"Input already in ISO format: {user_date_time}")
                return user_date_time
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


def get_response_from_gpt(msg, user_id, _assistant_manager):
    logger.info(f"Tool called: get_response_from_gpt(user_id={user_id})")
    start_time = time.time()
    try:
        response = _assistant_manager.run_conversation(user_id, msg)
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
