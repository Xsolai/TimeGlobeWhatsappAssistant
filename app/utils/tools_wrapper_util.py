import re
import logging
import time
from datetime import datetime
from ..services.time_globe_service import TimeGlobeService
from ..agent import AssistantManager
from ..core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

assistant_manager = AssistantManager(
    settings.OPENAI_API_KEY, settings.OPENAI_ASSISTANT_ID
)

# Initialize the TimeGlobeService
time_globe_service = TimeGlobeService()


def get_sites():
    """Get a list of available salons"""
    logger.info("Tool called: get_sites()")
    start_time = time.time()
    try:
        sites = time_globe_service.get_sites()
        execution_time = time.time() - start_time
        logger.info(f"get_sites() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "sites": sites}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_sites(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def get_products(site_code="bonn"):
    """Get a list of available services for a specific salon"""
    logger.info(f"Tool called: get_products(site_code={site_code})")
    start_time = time.time()
    try:
        products = time_globe_service.get_products(site_code)
        execution_time = time.time() - start_time
        logger.info(f"get_products() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "products": products}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_products(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def get_employee(item_no, item_name):
    """Get a list of available employees for a specific service"""
    logger.info(f"Tool called: get_employee(item_no={item_no}, item_name={item_name})")
    start_time = time.time()
    try:
        employees = time_globe_service.get_employee(item_no, item_name)
        execution_time = time.time() - start_time
        logger.info(f"get_employee() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "employees": employees}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_employee(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def get_suggestions(employee_id, item_no):
    """Get available appointment slots for a selected employee and service"""
    logger.info(f"Tool called: get_suggestions(employee_id={employee_id}, item_no={item_no})")
    start_time = time.time()
    try:
        suggestions = time_globe_service.get_suggestions(employee_id, item_no)
        execution_time = time.time() - start_time
        logger.info(f"get_suggestions() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "suggestions": suggestions}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_suggestions(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def book_appointment(duration, user_date, user_time):
    """Book an appointment with the selected parameters"""
    logger.info(f"Tool called: book_appointment(duration={duration}, user_date={user_date}, user_time={user_time})")
    start_time = time.time()
    try:
        result = time_globe_service.book_appointment(
            duration,
            user_date,
            user_time,
        )
        execution_time = time.time() - start_time
        
        if result.get("code") == 90:
            logger.info(f"book_appointment() - user already has 2 appointments - took {execution_time:.2f}s")
            return {
                "status": "success",
                "booking_result": "you already have 2 appointments in future \
            in order to make another appointment please cancel one of them.",
            }
        elif result.get("code") == 0:
            order_id = result.get("orderId")
            logger.info(f"book_appointment() - appointment booked successfully (orderID: {order_id}) - took {execution_time:.2f}s")
            return {
                "status": "success",
                "booking_result": f"appointment booked successfully orderID is {order_id}",
            }
        else:
            logger.warning(f"book_appointment() - unexpected code: {result.get('code')} - took {execution_time:.2f}s")
            return {
                "status": "error",
                "message": f"Unexpected response code: {result.get('code')}",
            }
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in book_appointment(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def cancel_appointment(order_id):
    """Cancel an existing appointment"""
    logger.info(f"Tool called: cancel_appointment(order_id={order_id})")
    start_time = time.time()
    try:
        if not order_id:
            logger.warning("cancel_appointment() called without order_id")
            return {"status": "error", "message": "order_id is required"}
            
        result = time_globe_service.cancel_appointment(order_id)
        execution_time = time.time() - start_time
        
        if result.get("code") == 0:
            logger.info(f"cancel_appointment() - appointment cancelled successfully - took {execution_time:.2f}s")
            return {
                "status": "success",
                "message": "your appointment has been cancelled.",
            }
        else:
            logger.warning(f"cancel_appointment() - invalid appointment ID - took {execution_time:.2f}s")
            return {
                "status": "success",
                "cancellation_result": "The provided id is not valid appointment id",
            }
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in cancel_appointment(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def get_profile(mobile_number: str):
    """Get the profile data for a given phone number"""
    logger.info(f"Tool called: get_profile(mobile_number={mobile_number})")
    start_time = time.time()
    try:
        profile = time_globe_service.get_profile(mobile_number)
        execution_time = time.time() - start_time
        
        if profile.get("code") == 0:
            logger.info(f"get_profile() - profile retrieved successfully - took {execution_time:.2f}s")
            return {"status": "success", "profile": profile}
        elif profile.get("code") == -3:
            logger.info(f"get_profile() - user does not exist - took {execution_time:.2f}s")
            return {
                "status": "success",
                "message": "user with this number does not exist",
            }
        else:
            logger.warning(f"get_profile() - error getting user info, code: {profile.get('code')} - took {execution_time:.2f}s")
            return {"status": "success", "message": "there is error getting user info"}

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_profile(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def get_orders():
    """Get a list of open appointments"""
    logger.info("Tool called: get_orders()")
    start_time = time.time()
    try:
        orders = time_globe_service.get_orders()
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
        old_orders = time_globe_service.get_old_orders(customer_code)
        execution_time = time.time() - start_time
        logger.info(f"get_old_orders() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "old_orders": old_orders}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_old_orders(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def store_profile(
    mobile_number: str,
    email: str,
    gender: str,
    first_name: str,
    last_name: str,
):
    """store user profile"""
    logger.info(f"Tool called: store_profile(mobile_number={mobile_number}, email={email}, gender={gender}, first_name={first_name}, last_name={last_name})")
    start_time = time.time()
    try:
        response = time_globe_service.store_profile(
            mobile_number, email, gender, first_name, last_name
        )
        execution_time = time.time() - start_time
        
        if response.get("code") == 0:
            logger.info(f"store_profile() - profile created successfully - took {execution_time:.2f}s")
            return {"status": "success", "message": "profile created successfully"}
        else:
            logger.warning(f"store_profile() - error creating profile, code: {response.get('code')} - took {execution_time:.2f}s")
            return {"status": "success", "message": "There is error creating profile"}

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
        final_response = remove_brackets(final_response)  # removing brackets before linke
        final_response = remove_small_brackets(
            final_response
        )  # removing small brackets from link
        # remove all ### from the response
        final_response=final_response.replace("### ","")
        
        execution_time = time.time() - start_time
        logger.debug(f"format_response() completed in {execution_time:.4f}s")
        return final_response
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in format_response(): {str(e)} - took {execution_time:.4f}s")
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


def format_datetime(user_date: str, user_time: str) -> str:
    """Converts user-selected date (YYYY-MM-DD) and time (HH:MM or HH:MM AM/PM) to ISO 8601 format."""
    logger.info(f"Tool called: format_datetime(user_date={user_date}, user_time={user_time})")
    start_time = time.time()
    try:
        # Try parsing in 24-hour format first
        dt = datetime.strptime(f"{user_date} {user_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            # If it fails, try parsing in 12-hour format
            dt = datetime.strptime(f"{user_date} {user_time}", "%Y-%m-%d %I:%M %p")
        except ValueError:
            logger.error(f"Invalid date-time format: {user_date} {user_time}")
            raise ValueError(f"Invalid date-time format: {user_date} {user_time}")

    # Convert to ISO 8601 format
    result = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    execution_time = time.time() - start_time
    logger.info(f"format_datetime() completed successfully in {execution_time:.4f}s")
    return result


def get_response_from_gpt(msg, user_id):
    logger.info(f"Tool called: get_response_from_gpt(user_id={user_id})")
    start_time = time.time()
    try:
        response = assistant_manager.run_conversation(user_id, msg)
        execution_time = time.time() - start_time
        logger.info(f"get_response_from_gpt() for user {user_id} completed in {execution_time:.2f}s")
        return response
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_response_from_gpt(): {str(e)} - took {execution_time:.2f}s")
        return f"Error processing request: {str(e)}"
