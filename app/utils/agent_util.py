from ..services.time_globe_service import TimeGlobeService

service = TimeGlobeService()

available_functions = {
    "get_sites": service.get_sites,
}
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_sites",
            "description": "Get a list of available salons",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_products",
            "description": "Get a list of available services for a specific salon",
            "parameters": {
                "type": "object",
                "properties": {
                    "siteCd": {
                        "type": "string",
                        "description": "Site code for the salon. Default is 'bonn'",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_employee",
            "description": "Get a list of available employees for a specific service",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_no": {
                        "type": "string",
                        "description": "The service item number",
                    },
                    "item_name": {
                        "type": "string",
                        "description": "The name of the service",
                    },
                },
                "required": ["item_no", "item_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_suggestions",
            "description": "Get available appointment slots for a selected employee and service",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "integer",
                        "description": "ID of the selected employee",
                    }
                },
                "required": ["employee_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment with the selected parameters",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration": {
                        "type": "integer",
                        "description": "Duration of the appointment in milliseconds (e.g., 45 minutes = 2700000ms)",
                    },
                    "user_date": {
                        "type": "string",
                        "description": "Appointment date in format (e.g., 'March 4, 2025')",
                    },
                    "user_time": {
                        "type": "string",
                        "description": "Appointment time in format (e.g., '08:00 AM')",
                    },
                },
                "required": ["user_date", "user_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "ID of the  appointment to cancel",
                    },
                },
                "required": ["siteCd", "order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_profile",
            "description": "Get user profile information",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_code": {
                        "type": "string",
                        "description": "Customer code. Default is 'demo'",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_profile_data",
            "description": "Get user profile information for given phone number",
            "parameters": {
                "type": "object",
                "properties": {
                    "mobile_number": {
                        "type": "string",
                        "description": "User's mobile number",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_orders",
            "description": "Get a list of open appointments",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_code": {
                        "type": "string",
                        "description": "Customer code. Default is 'demo'",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_old_orders",
            "description": "Get a list of past appointments",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_code": {
                        "type": "string",
                        "description": "Customer code. Default is 'demo'",
                    }
                },
            },
        },
    },
    {
        "name": "store_profile",
        "description": "Stores user profile data",
        "parameters": {
            "type": "object",
            "properties": {
                "mobile_number": {
                    "type": "string",
                    "description": "User's mobile phone number",
                },
                "email": {"type": "string", "description": "User's email address"},
                "gender": {
                    "type": "string",
                    "enum": ["M", "F"],
                    "description": "User's gender ('M' for Male, 'F' for Female)",
                },
                "first_name": {"type": "string", "description": "User's first name"},
                "last_name": {"type": "string", "description": "User's last name"},
            },
            "required": ["mobile_number", "email", "gender", "first_name", "last_name"],
        },
    },
]
