import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="/home/ec2-user/TimeGlobeWhatsappAssistant/.env")

# Get API key from environment
api_key = os.getenv("DIALOG360_API_KEY")
phone_number = os.getenv("DIALOG360_PHONE_NUMBER")

# Set up headers and endpoint
headers = {
    "Content-Type": "application/json",
    "D360-API-KEY": api_key
}

url = "https://waba-v2.360dialog.io/messages"

# Prepare the message payload
payload = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": phone_number,
    "type": "text",
    "text": {
        "body": "Hello from the 360dialog test script!"
    }
}

# Send the message
# print(f"Sending message to {phone_number}...")
try:
    response = requests.post(url, headers=headers, json=payload)
    
    # # print response details
    # print(f"Status code: {response.status_code}")
    # print(f"Response headers: {response.headers}")
    # print(f"Response body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code in [200, 201, 202]:
        # print("Message sent successfully!")
    else:
        # print(f"Failed to send message. Error: {response.text}")
except Exception as e:
    # print(f"Exception occurred: {str(e)}") 