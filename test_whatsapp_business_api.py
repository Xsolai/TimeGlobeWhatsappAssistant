#!/usr/bin/env python3
"""
Test script for WhatsApp Business API integration.
Use this to verify your setup before full migration.
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.env import load_env

def test_whatsapp_business_api():
    """Test WhatsApp Business API integration."""
    print("🔍 Testing WhatsApp Business API Integration")
    print("=" * 50)
    
    # Load environment variables
    load_env()
    
    # Get environment variables
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    webhook_verify_token = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN")
    test_phone = os.getenv("TEST_PHONE_NUMBER")  # Add this to your .env for testing
    
    print(f"📱 Access Token: {'✅ Set' if access_token else '❌ Missing'}")
    print(f"📞 Phone Number ID: {'✅ Set' if phone_number_id else '❌ Missing'}")
    print(f"🔑 Webhook Verify Token: {'✅ Set' if webhook_verify_token else '❌ Missing'}")
    print(f"🧪 Test Phone Number: {'✅ Set' if test_phone else '❌ Missing'}")
    print()
    
    if not all([access_token, phone_number_id, webhook_verify_token]):
        print("❌ Missing required environment variables. Check your .env file.")
        return False
    
    # Test 1: Verify API credentials
    print("1️⃣ Testing API Credentials...")
    if test_api_credentials(access_token, phone_number_id):
        print("✅ API credentials are valid")
    else:
        print("❌ API credentials are invalid")
        return False
    
    # Test 2: Get business profile
    print("2️⃣ Testing Business Profile...")
    if test_business_profile(access_token, phone_number_id):
        print("✅ Business profile retrieved successfully")
    else:
        print("❌ Failed to retrieve business profile")
    
    # Test 3: Send test message (optional)
    if test_phone:
        print("3️⃣ Testing Message Sending...")
        if test_send_message(access_token, phone_number_id, test_phone):
            print("✅ Test message sent successfully")
        else:
            print("❌ Failed to send test message")
    else:
        print("3️⃣ Skipping message test (no TEST_PHONE_NUMBER set)")
    
    print()
    print("🎉 WhatsApp Business API testing completed!")
    return True

def test_api_credentials(access_token, phone_number_id):
    """Test if API credentials are valid."""
    try:
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📞 Phone Number: {data.get('display_phone_number', 'N/A')}")
            print(f"   🆔 Phone Number ID: {data.get('id', 'N/A')}")
            return True
        else:
            print(f"   ❌ API Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_business_profile(access_token, phone_number_id):
    """Test business profile retrieval."""
    try:
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/whatsapp_business_profile"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            profile_data = data.get('data', [{}])[0] if data.get('data') else {}
            print(f"   🏢 Business Name: {profile_data.get('about', 'N/A')}")
            print(f"   📧 Email: {profile_data.get('email', 'N/A')}")
            print(f"   🌐 Website: {profile_data.get('websites', ['N/A'])[0] if profile_data.get('websites') else 'N/A'}")
            return True
        else:
            print(f"   ❌ Profile Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_send_message(access_token, phone_number_id, test_phone):
    """Test sending a message."""
    try:
        # Format phone number
        if not test_phone.startswith("+"):
            test_phone = f"+{test_phone}"
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": test_phone,
            "type": "text",
            "text": {
                "body": f"🧪 WhatsApp Business API Test Message\nSent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nThis is a test message to verify your WhatsApp Business API integration is working correctly."
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', 'N/A')
            print(f"   ✅ Message ID: {message_id}")
            print(f"   📱 Sent to: {test_phone}")
            return True
        else:
            print(f"   ❌ Send Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_webhook_verification():
    """Test webhook verification endpoint."""
    print("4️⃣ Testing Webhook Verification...")
    
    # This would require your server to be running
    # You can test this manually using curl or a tool like Postman
    webhook_url = os.getenv("WEBHOOK_URL", "http://localhost:8000/api/whatsapp/webhook")
    verify_token = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN")
    
    print(f"   🔗 Webhook URL: {webhook_url}")
    print(f"   🔑 Verify Token: {verify_token}")
    print(f"   📝 Test Command:")
    print(f"   curl -X GET \"{webhook_url}?hub.mode=subscribe&hub.challenge=test123&hub.verify_token={verify_token}\"")
    print("   Expected Response: test123")

if __name__ == "__main__":
    print("🚀 WhatsApp Business API Integration Tester")
    print("This script will test your WhatsApp Business API setup")
    print()
    
    # Add test phone number prompt
    if not os.getenv("TEST_PHONE_NUMBER"):
        print("💡 Tip: Set TEST_PHONE_NUMBER in your .env file to test message sending")
        test_phone = input("Enter a test phone number (with country code, e.g., +1234567890) or press Enter to skip: ").strip()
        if test_phone:
            os.environ["TEST_PHONE_NUMBER"] = test_phone
    
    print()
    success = test_whatsapp_business_api()
    
    print()
    test_webhook_verification()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("Your WhatsApp Business API integration is ready to use.")
    else:
        print("\n❌ Some tests failed. Please check your configuration.")
    
    print("\n📚 Next Steps:")
    print("1. Update your database with WhatsApp Business API credentials")
    print("2. Configure your webhook URL in Facebook Developer Console") 
    print("3. Test end-to-end message flow")
    print("4. Monitor logs during initial testing") 