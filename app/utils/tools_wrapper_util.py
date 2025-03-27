import re
import logging
import time
from datetime import datetime
from ..core.config import settings
from functools import lru_cache
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Remove circular imports - use lazy loading instead
_assistant_manager = None
_time_globe_service = None

# Cache for service instances
_service_cache: Dict[str, Any] = {}
_cache_ttl = 300  # 5 minutes


def _get_assistant_manager():
    """Lazy initialization of the AssistantManager to avoid circular imports"""
    global _assistant_manager
    if _assistant_manager is None:
        from ..agent import AssistantManager

    return _assistant_manager


def _get_time_globe_service():
    """Lazy initialization of the TimeGlobeService with caching."""
    global _time_globe_service
    if _time_globe_service is None:
        from ..services.time_globe_service import TimeGlobeService
        _time_globe_service = TimeGlobeService()
    return _time_globe_service


@lru_cache(maxsize=100)
def get_sites():
    """Get a list of available salons with caching."""
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


@lru_cache(maxsize=100)
def get_products(siteCd: str):
    """Get a list of available services for a specific salon with caching."""
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


@lru_cache(maxsize=100)
def get_employee(items: str, siteCd: str, week: int):
    """Get a list of available employees for a specific service with caching."""
    logger.info(f"Tool called: get_employee(items={items}, siteCd={siteCd}, week={week})")
    start_time = time.time()
    try:
        employees = _get_time_globe_service().get_employee(items, siteCd, week)
        execution_time = time.time() - start_time
        logger.info(f"get_employee() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "employees": employees}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_employee(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


@lru_cache(maxsize=100)
def AppointmentSuggestion(week: int, employeeid: int, itemno: int, siteCd: str):
    """Get available appointment slots with caching."""
    logger.info(f"Tool called: AppointmentSuggestion(week={week}, employeeid={employeeid}, itemno={itemno}, siteCd={siteCd})")
    start_time = time.time()
    try:
        suggestions = _get_time_globe_service().AppointmentSuggestion(week, employeeid, itemno, siteCd)
        execution_time = time.time() - start_time
        logger.info(f"AppointmentSuggestion() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "suggestions": suggestions}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in AppointmentSuggestion(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def book_appointment(
    beginTs: str,
    durationMillis: int,
    mobileNumber: str,
    employeeId: int,
    itemNo: int,
    siteCd: str
):
    """Book an appointment with optimized error handling."""
    logger.info(f"Tool called: book_appointment(duration={durationMillis}, user_date_time={beginTs})")
    start_time = time.time()
    try:
        if not isinstance(beginTs, str):
            logger.warning(f"Invalid date/time types: date={type(beginTs)}")
            return {"status": "error", "message": "Date and time must be strings"}

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
            logger.info(f"book_appointment() - user already has 2 appointments - took {execution_time:.2f}s")
            return {
                "status": "success",
                "booking_result": "you already have 2 appointments in future in order to make another appointment please cancel one of them.",
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


def cancel_appointment(orderId: int, mobileNumber: str, siteCd: str):
    """Cancel an existing appointment with optimized error handling."""
    logger.info(f"Tool called: cancel_appointment(orderId={orderId}, sitecode={siteCd})")
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


@lru_cache(maxsize=100)
def get_profile(mobile_number: str):
    """Get the profile data for a given phone number with caching."""
    logger.info(f"Tool called: get_profile(mobile_number={mobile_number})")
    start_time = time.time()
    try:
        profile = _get_time_globe_service().get_profile(mobile_number)
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


@lru_cache(maxsize=100)
def get_orders(mobile_number: str):
    """Get a list of open appointments with caching."""
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


@lru_cache(maxsize=100)
def get_old_orders(customer_code: str = "demo"):
    """Get a list of past appointments with caching."""
    logger.info("Tool called: get_old_orders()")
    start_time = time.time()
    try:
        orders = _get_time_globe_service().get_old_orders(customer_code)
        execution_time = time.time() - start_time
        logger.info(f"get_old_orders() completed successfully in {execution_time:.2f}s")
        return {"status": "success", "orders": orders}
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in get_old_orders(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def store_profile(
    mobile_number: str,
    email: str,
    gender: str,
    full_name: str,
    first_name: str,
    last_name: str,
):
    """Store user profile with optimized error handling."""
    logger.info(f"Tool called: store_profile(mobile_number={mobile_number})")
    start_time = time.time()
    try:
        # Clear any cached profile data for this number
        get_profile.cache_clear()
        
        result = _get_time_globe_service().store_profile(
            mobile_number,
            email,
            gender,
            full_name,
            first_name,
            last_name,
        )
        execution_time = time.time() - start_time
        logger.info(f"store_profile() completed successfully in {execution_time:.2f}s")
        return result
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error in store_profile(): {str(e)} - took {execution_time:.2f}s")
        return {"status": "error", "message": str(e)}


def format_response(text: str) -> str:
    """Format the response text with optimized string operations."""
    if not text:
        return ""
    
    # Use a single pass for all replacements
    text = text.replace("【", "").replace("】", "")
    text = re.sub(r'\d+:\d+†[^\s]+', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', text)
    
    return text.strip()


def get_response_from_gpt(msg: str, user_id: str, _assistant_manager: Any) -> str:
    """Get response from GPT with optimized performance."""
    try:
        response = _assistant_manager.run_conversation(user_id, msg)
        return format_response(response)
    except Exception as e:
        logger.error(f"Error in get_response_from_gpt: {str(e)}")
        return "I apologize, but I encountered an error processing your request. Please try again."
