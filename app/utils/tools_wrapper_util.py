import re
from datetime import datetime
from ..services.time_globe_service import TimeGlobeService

# Initialize the TimeGlobeService
time_globe_service = TimeGlobeService()


def get_sites():
    """Get a list of available salons"""
    try:
        sites = time_globe_service.get_sites()
        return {"status": "success", "sites": sites}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_products(site_code="chatbot"):
    """Get a list of available services for a specific salon"""
    try:
        products = time_globe_service.get_products(site_code)
        return {"status": "success", "products": products}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_employee(item_no, item_name):
    """Get a list of available employees for a specific service"""
    try:
        employees = time_globe_service.get_employee(item_no, item_name)
        return {"status": "success", "employees": employees}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_suggestions(employee_id):
    """Get available appointment slots for a selected employee and service"""
    try:
        suggestions = time_globe_service.get_suggestions(employee_id)
        return {"status": "success", "suggestions": suggestions}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def book_appointment(
    firstname, lastname, gender, mobile_number, email, duration, user_date, user_time
):
    """Book an appointment with the selected parameters"""
    try:
        result = time_globe_service.book_appointment(
            firstname,
            lastname,
            gender,
            mobile_number,
            email,
            duration,
            user_date,
            user_time,
        )
        return {"status": "success", "booking_result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def cancel_appointment(site_code, customer_code="demo", order_id=None):
    """Cancel an existing appointment"""
    try:
        if not order_id:
            return {"status": "error", "message": "order_id is required"}
        result = time_globe_service.cancel_appointment(
            site_code, customer_code, order_id
        )
        return {"status": "success", "cancellation_result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_profile(customer_code="demo"):
    """Get user profile information"""
    try:
        profile = time_globe_service.get_profile(customer_code)
        return {"status": "success", "profile": profile}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_orders(customer_code="demo"):
    """Get a list of open appointments"""
    try:
        orders = time_globe_service.get_orders(customer_code)
        return {"status": "success", "orders": orders}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_old_orders(customer_code="demo"):
    """Get a list of past appointments"""
    try:
        old_orders = time_globe_service.get_old_orders(customer_code)
        return {"status": "success", "old_orders": old_orders}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def format_response(text):
    final_response = replace_double_with_single_asterisks(text)  # removing single *
    final_response = remove_sources(final_response)  # removing sources if any
    final_response = remove_brackets(final_response)  # removing brackets before linke
    final_response = remove_small_brackets(
        final_response
    )  # removing small brackets from link

    return final_response


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
    """Converts user-selected date and time to ISO 8601 format (YYYY-MM-DDTHH:MM:SS.000Z)."""
    try:
        # Try parsing in 12-hour format first
        dt = datetime.strptime(f"{user_date} {user_time}", "%B %d, %Y %I:%M %p")
    except ValueError:
        try:
            # If it fails, try parsing in 24-hour format
            dt = datetime.strptime(f"{user_date} {user_time}", "%B %d, %Y %H:%M")
        except ValueError:
            raise ValueError(f"Invalid date-time format: {user_date} {user_time}")

    # Convert to ISO format (2025-03-03T16:15:00.000Z)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
