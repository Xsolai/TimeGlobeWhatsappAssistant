import pytest
import sys
import os
from pathlib import Path
import time
import uuid

# Add the parent directory to sys.path to make app imports work
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Now imports from app will work
from app.db.session import get_db
from app.models.base import Base
from app.main import app

# Create a test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the tables in the test database
Base.metadata.create_all(bind=engine)

# Override the dependency to use our test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create a test client
client = TestClient(app)

# Mock variables to simulate OTP and reset tokens
test_email = f"test_{int(time.time())}@example.com"
test_business_name = "Test Business"
test_password = "StrongPassword123!"
test_otp = "123456"

# Store the access token for use across tests
auth_token = None

def test_register():
    """Test business registration endpoint"""
    # Mock the email sending and OTP storage
    from app.services.auth_service import otp_storage
    
    response = client.post(
        "/api/auth/register",
        json={
            "business_name": test_business_name,
            "email": test_email,
            "password": test_password,
            "phone_number": "+1234567890"
        }
    )
    
    assert response.status_code == 200
    assert "OTP sent" in response.json()["message"]
    
    # Verify OTP was stored
    assert test_email in otp_storage
    # Save the OTP for later use
    global test_otp
    test_otp = otp_storage[test_email]["otp"]

def test_verify_otp():
    """Test OTP verification endpoint"""
    from app.services.auth_service import otp_storage
    
    # Ensure the OTP is in storage from the registration test
    assert test_email in otp_storage
    
    response = client.post(
        "/api/auth/verify-otp",
        json={
            "email": test_email,
            "otp": test_otp
        }
    )
    
    assert response.status_code == 200
    assert "Registration Successful" in response.json()["message"]
    
    # OTP should be removed after successful verification
    assert test_email not in otp_storage

def test_login():
    """Test login endpoint"""
    global auth_token
    
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_email,
            "password": test_password
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Save token for subsequent tests
    auth_token = data["access_token"]

def test_get_business_profile():
    """Test getting business profile endpoint"""
    global auth_token
    
    # Ensure we have a token from the login test
    assert auth_token is not None, "No auth token available. Login test must run first."
    
    response = client.get(
        "/api/auth/business/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_email
    assert data["business_name"] == test_business_name

def test_resend_otp():
    """Test resending OTP endpoint"""
    # Register a new temporary email for testing resend
    temp_email = f"resend_{int(time.time())}@example.com"
    
    # First register to create an OTP
    client.post(
        "/api/auth/register",
        json={
            "business_name": "Resend Test",
            "email": temp_email,
            "password": "TestPassword123!",
            "phone_number": "+9876543210"
        }
    )
    
    # Now test resending the OTP
    response = client.post(
        "/api/auth/resend-otp",
        json={
            "email": temp_email,
            "otp": "dummy"  # The value doesn't matter for resend
        }
    )
    
    assert response.status_code == 200
    assert "OTP has been resent" in response.json()["message"]

def test_forget_password():
    """Test forget password endpoint"""
    from app.services.auth_service import reset_tokens
    
    # Clear any existing reset tokens
    reset_tokens.clear()
    
    response = client.post(
        "/api/auth/forget-password",
        json={
            "email": test_email,
            "otp": "dummy"  # Not used for forget password
        }
    )
    
    assert response.status_code == 200
    assert "Reset password link has been sent" in response.json()["message"]
    assert len(reset_tokens) > 0

def test_reset_password():
    """Test reset password endpoint"""
    from app.services.auth_service import reset_tokens
    
    # Ensure we have reset tokens from previous test
    assert len(reset_tokens) > 0
    
    # Get the first token
    token = list(reset_tokens.keys())[0]
    
    # Test resetting the password
    new_password = "NewStrongPassword456!"
    response = client.post(
        "/api/auth/reset-password",
        json={
            "token": token,
            "new_password": new_password
        }
    )
    
    assert response.status_code == 200
    assert "Password has been reset successfully" in response.json()["message"]
    
    # Token should be removed after successful reset
    assert token not in reset_tokens
    
    # Verify login with new password works
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_email,
            "password": new_password
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert login_response.status_code == 200

def test_invalid_login():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_email,
            "password": "WrongPassword123!"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_protected_route_without_token():
    """Test accessing protected route without token"""
    response = client.get("/api/auth/business/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

if __name__ == "__main__":
    print("Running auth tests...")
    pytest.main(["-xvs", __file__]) 