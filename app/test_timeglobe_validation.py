"""
Test script for TimeGlobe API Key validation endpoint
"""
import requests
import json

# Base URL of your API
BASE_URL = "http://localhost:8000"  # Change if your API runs on a different port

def test_public_timeglobe_validation():
    """Test the public TimeGlobe validation endpoint"""
    url = f"{BASE_URL}/api/auth/public/validate-timeglobe-key"
    
    # Example valid API key (replace with real one for actual testing)
    payload = {
        "auth_key": "96f11820d19b7d5fe3de0d6a3aefcb2848109d507a3ddf0f95fcda285cff2b33",
        "email": "test@example.com"
    }
    
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test an invalid key
    payload = {
        "auth_key": "invalid_key",
        "email": "test@example.com"
    }
    
    response = requests.post(url, json=payload)
    print(f"Status Code (invalid key): {response.status_code}")
    print(f"Response (invalid key): {json.dumps(response.json(), indent=2)}")
    
    # Test checking if a business already has TimeGlobe integration
    payload = {
        "email": "test@example.com"  # No auth_key provided
    }
    
    response = requests.post(url, json=payload)
    print(f"Status Code (check existing): {response.status_code}")
    print(f"Response (check existing): {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_public_timeglobe_validation() 