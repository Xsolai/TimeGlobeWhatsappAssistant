#!/usr/bin/env python3
"""
Quick test script to verify email configuration with Ionos SMTP.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.email_util import send_email, send_otp_email, send_password_reset_email
from app.core.config import settings

def test_email_functionality():
    """Test the email functionality with the provided email address"""
    test_email = "engrahsaninam@gmail.com"
    
    print("=" * 60)
    print("TIMEGLOBE EMAIL FUNCTIONALITY TEST")
    print("=" * 60)
    
    print(f"Testing with email: {test_email}")
    print(f"SMTP Server: {settings.SMTP_SERVER}")
    print(f"SMTP Port: {settings.SMTP_PORT}")
    print(f"From Email: {settings.EMAIL_FROM}")
    print(f"From Name: {settings.EMAIL_FROM_NAME}")
    print()
    
    # Test 1: Basic email sending
    print("🔸 Test 1: Basic Email Sending")
    print("-" * 30)
    try:
        success1 = send_email(
            recipient_email=test_email,
            subject="TimeGlobe Email Test - Basic Email",
            body="""Hello!

This is a basic email test from the TimeGlobe system.

Configuration Details:
- SMTP Server: smtp.ionos.de
- From Address: no-reply@timeglobe.ecomtask.de
- Test Time: Now

If you received this email, the basic email functionality is working correctly!

Best regards,
TimeGlobe Team""",
            sender_name="TimeGlobe System"
        )
        
        if success1:
            print("✅ Basic email test: SUCCESS")
        else:
            print("❌ Basic email test: FAILED")
    except Exception as e:
        print(f"❌ Basic email test: ERROR - {e}")
        success1 = False
    
    print()
    
    # Test 2: OTP Email
    print("🔸 Test 2: OTP Verification Email")
    print("-" * 30)
    try:
        success2 = send_otp_email(
            recipient_email=test_email,
            otp="123456",
            business_name="Test Business Account"
        )
        
        if success2:
            print("✅ OTP email test: SUCCESS")
        else:
            print("❌ OTP email test: FAILED")
    except Exception as e:
        print(f"❌ OTP email test: ERROR - {e}")
        success2 = False
    
    print()
    
    # Test 3: Password Reset Email
    print("🔸 Test 3: Password Reset Email")
    print("-" * 30)
    try:
        success3 = send_password_reset_email(
            recipient_email=test_email,
            reset_link="https://timeglobe.ecomtask.de/reset-password/123/abc-reset-token",
            business_name="Test Business Account"
        )
        
        if success3:
            print("✅ Password reset email test: SUCCESS")
        else:
            print("❌ Password reset email test: FAILED")
    except Exception as e:
        print(f"❌ Password reset email test: ERROR - {e}")
        success3 = False
    
    print()
    print("=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = 3
    passed_tests = sum([success1, success2, success3])
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print()
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Email configuration is working correctly with Ionos SMTP")
        print(f"✅ Emails are being sent from: {settings.EMAIL_FROM}")
        print(f"✅ Test emails sent to: {test_email}")
    else:
        print("⚠️ SOME TESTS FAILED!")
        print("❌ Check the error messages above for troubleshooting")
        print("❌ Verify Ionos SMTP credentials and settings")
    
    print()
    print("Check your email inbox for the test messages!")
    print("=" * 60)

if __name__ == "__main__":
    test_email_functionality() 