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
                    "site_code": {
                        "type": "string",
                        "description": "Site code for the salon. Default is 'chatbot'",
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
                    "firstname": {
                        "type": "string",
                        "description": "Customer's first name",
                    },
                    "lastname": {
                        "type": "string",
                        "description": "Customer's last name",
                    },
                    "gender": {"type": "string", "description": "Customer's gender"},
                    "mobile_number": {
                        "type": "string",
                        "description": "Customer's mobile number (format: +4915167973449)",
                    },
                    "email": {
                        "type": "string",
                        "description": "Customer's email address",
                    },
                },
                "required": [
                    "firstname",
                    "lastname",
                    "gender",
                    "mobile_number",
                    "email",
                ],
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
                    "site_code": {
                        "type": "string",
                        "description": "Site code for the salon",
                    },
                    "customer_code": {
                        "type": "string",
                        "description": "Customer code. Default is 'demo'",
                    },
                    "order_id": {
                        "type": "integer",
                        "description": "ID of the order to cancel",
                    },
                },
                "required": ["site_code", "order_id"],
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
]


prompt = ""
