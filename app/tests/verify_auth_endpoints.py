import sys
import os
from pathlib import Path
import requests
import time
import json

# Add the parent directory to sys.path to make app imports work
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

# Now we can import from dotenv and app modules
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")
TEST_EMAIL = f"verify_{int(time.time())}@example.com"
TEST_PASSWORD = "StrongPassword123!"
TEST_BUSINESS_NAME = "Verification Business"

# Storage for tokens and other data
data_store = {
    "access_token": None,
    "otp": None,
    "reset_token": None
}

def print_section(title):
    """Helper to print formatted section titles"""
    print("\n" + "="*50)
    print(f" {title} ".center(50, "="))
    print("="*50)

def print_response(response, message="Response"):
    """Helper to print formatted responses"""
    print(f"\n{message}:")
    print(f"Status code: {response.status_code}")
    try:
        print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response text: {response.text}")

def verify_register():
    """Verify the registration endpoint"""
    print_section("TESTING REGISTRATION")
    
    url = f"{API_BASE_URL}/auth/register"
    payload = {
        "business_name": TEST_BUSINESS_NAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "phone_number": "+1234567890"
    }
    
    print(f"Sending registration request to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload)
    print_response(response, "Registration response")
    
    if response.status_code == 200:
        print("\n✅ Registration endpoint working correctly")
        
        # In a real application, you would get the OTP from the email
        otp_input = input("\nEnter the OTP you received (check server logs or database): ")
        if otp_input:
            data_store["otp"] = otp_input
            return True
    else:
        print("\n❌ Registration endpoint failed")
        return False

def verify_otp():
    """Verify the OTP verification endpoint"""
    if not data_store["otp"]:
        print("\n❌ No OTP available, skipping OTP verification")
        return False
        
    print_section("TESTING OTP VERIFICATION")
    
    url = f"{API_BASE_URL}/auth/verify-otp"
    payload = {
        "email": TEST_EMAIL,
        "otp": data_store["otp"]
    }
    
    print(f"Sending OTP verification request to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload)
    print_response(response, "OTP verification response")
    
    if response.status_code == 200:
        print("\n✅ OTP verification endpoint working correctly")
        return True
    else:
        print("\n❌ OTP verification endpoint failed")
        return False

def verify_login():
    """Verify the login endpoint"""
    print_section("TESTING LOGIN")
    
    url = f"{API_BASE_URL}/auth/login"
    payload = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    print(f"Sending login request to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        url, 
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print_response(response, "Login response")
    
    if response.status_code == 200:
        data_store["access_token"] = response.json().get("access_token")
        print("\n✅ Login endpoint working correctly")
        return True
    else:
        print("\n❌ Login endpoint failed")
        return False

def verify_profile():
    """Verify the business profile endpoint"""
    if not data_store["access_token"]:
        print("\n❌ No access token available, skipping profile verification")
        return False
        
    print_section("TESTING BUSINESS PROFILE")
    
    url = f"{API_BASE_URL}/auth/business/me"
    headers = {"Authorization": f"Bearer {data_store['access_token']}"}
    
    print(f"Sending profile request to {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    
    response = requests.get(url, headers=headers)
    print_response(response, "Profile response")
    
    if response.status_code == 200:
        print("\n✅ Profile endpoint working correctly")
        return True
    else:
        print("\n❌ Profile endpoint failed")
        return False

def verify_forget_password():
    """Verify the forget password endpoint"""
    print_section("TESTING FORGET PASSWORD")
    
    url = f"{API_BASE_URL}/auth/forget-password"
    payload = {
        "email": TEST_EMAIL,
        "otp": "dummy"  # Not used for forget password
    }
    
    print(f"Sending forget password request to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload)
    print_response(response, "Forget password response")
    
    if response.status_code == 200:
        print("\n✅ Forget password endpoint working correctly")
        
        # In a real application, you would get the reset token from the email link
        reset_token = input("\nEnter the reset token (check server logs or get from email link): ")
        if reset_token:
            data_store["reset_token"] = reset_token
            return True
    else:
        print("\n❌ Forget password endpoint failed")
        return False

def verify_reset_password():
    """Verify the reset password endpoint"""
    if not data_store["reset_token"]:
        print("\n❌ No reset token available, skipping password reset verification")
        return False
        
    print_section("TESTING RESET PASSWORD")
    
    url = f"{API_BASE_URL}/auth/reset-password"
    new_password = f"NewPassword{int(time.time())}"
    payload = {
        "token": data_store["reset_token"],
        "new_password": new_password
    }
    
    print(f"Sending reset password request to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload)
    print_response(response, "Reset password response")
    
    if response.status_code == 200:
        print("\n✅ Reset password endpoint working correctly")
        
        # Verify login with new password
        login_url = f"{API_BASE_URL}/auth/login"
        login_payload = {
            "username": TEST_EMAIL,
            "password": new_password
        }
        
        print("\nVerifying login with new password...")
        login_response = requests.post(
            login_url, 
            data=login_payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code == 200:
            print("\n✅ Login with new password successful")
            return True
        else:
            print("\n❌ Login with new password failed")
            return False
    else:
        print("\n❌ Reset password endpoint failed")
        return False

def verify_resend_otp():
    """Verify the resend OTP endpoint"""
    print_section("TESTING RESEND OTP")
    
    # Create a temporary user for testing resend OTP
    temp_email = f"resend_{int(time.time())}@example.com"
    
    # First register to create an OTP
    register_url = f"{API_BASE_URL}/auth/register"
    register_payload = {
        "business_name": "Resend Test",
        "email": temp_email,
        "password": "TestPassword123!",
        "phone_number": "+9876543210"
    }
    
    print(f"Creating temporary user for resend OTP test...")
    register_response = requests.post(register_url, json=register_payload)
    
    if register_response.status_code != 200:
        print("\n❌ Failed to create temporary user for resend OTP test")
        return False
    
    # Now test resending the OTP
    url = f"{API_BASE_URL}/auth/resend-otp"
    payload = {
        "email": temp_email,
        "otp": "dummy"  # The value doesn't matter for resend
    }
    
    print(f"Sending resend OTP request to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload)
    print_response(response, "Resend OTP response")
    
    if response.status_code == 200:
        print("\n✅ Resend OTP endpoint working correctly")
        return True
    else:
        print("\n❌ Resend OTP endpoint failed")
        return False

def run_verification():
    """Run all verification tests"""
    print_section("STARTING AUTH ENDPOINTS VERIFICATION")
    print(f"API base URL: {API_BASE_URL}")
    print(f"Test email: {TEST_EMAIL}")
    
    # Run tests
    verification_steps = [
        ("Registration", verify_register),
        ("OTP Verification", verify_otp),
        ("Login", verify_login),
        ("Profile", verify_profile),
        ("Resend OTP", verify_resend_otp),
        ("Forget Password", verify_forget_password),
        ("Reset Password", verify_reset_password)
    ]
    
    results = {}
    
    for name, func in verification_steps:
        result = func()
        results[name] = "✅ Success" if result else "❌ Failed"
    
    # Print summary
    print_section("VERIFICATION SUMMARY")
    for name, result in results.items():
        print(f"{name}: {result}")

if __name__ == "__main__":
    print("Starting verification of authentication endpoints...")
    run_verification() 