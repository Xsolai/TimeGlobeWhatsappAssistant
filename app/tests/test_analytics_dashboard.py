import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Allow running tests directly
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.main import app
from app.db.session import get_db
from app.models.base import Base
from app.models.business_model import Business
from app.models.customer_model import CustomerModel
from app.models.booked_appointment import BookModel
from app.models.booking_detail import BookingDetail
from app.utils.security_util import create_access_token, get_password_hash

# Setup in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

# Override dependency

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def create_sample_data():
    """Insert sample business and booking data for analytics tests."""
    db = TestingSessionLocal()
    business = Business(
        id=str(uuid.uuid4()),
        business_name="Analytics Biz",
        email="analytics@example.com",
        password=get_password_hash("pass123"),
        phone_number="+123456789",
        whatsapp_number="123456789",
    )
    db.add(business)
    db.commit()
    db.refresh(business)

    cust1 = CustomerModel(
        first_name="John",
        last_name="Doe",
        mobile_number="1111111111",
        business_id=business.id,
    )
    cust2 = CustomerModel(
        first_name="Jane",
        last_name="Smith",
        mobile_number="2222222222",
        business_id=business.id,
    )
    db.add_all([cust1, cust2])
    db.commit()

    now = datetime.now()
    earlier = now - timedelta(days=5)

    booking1 = BookModel(
        order_id=1,
        site_cd="A",
        customer_id=cust1.id,
        business_phone_number=business.whatsapp_number,
        created_at=now,
    )
    booking2 = BookModel(
        order_id=2,
        site_cd="A",
        customer_id=cust2.id,
        business_phone_number=business.whatsapp_number,
        created_at=earlier,
    )
    db.add_all([booking1, booking2])
    db.commit()

    detail1 = BookingDetail(
        begin_ts=now,
        duration_millis=3600000,
        employee_id=1,
        item_no=101,
        item_nm="Service A",
        book_id=booking1.id,
        created_at=now,
    )
    detail2 = BookingDetail(
        begin_ts=earlier,
        duration_millis=3600000,
        employee_id=2,
        item_no=102,
        item_nm="Service B",
        book_id=booking2.id,
        created_at=earlier,
    )
    db.add_all([detail1, detail2])
    db.commit()

    token = create_access_token(business.email)
    db.close()
    return token


def test_dashboard_endpoint():
    token = create_sample_data()
    response = client.get(
        "/api/analytics/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"

    dashboard = payload["data"]
    summary = dashboard["summary"]

    assert summary["today_appointments"] == 1
    assert summary["todays_services"] == 1
    assert summary["costs_today"] == pytest.approx(0.99, rel=1e-2)
    assert summary["costs_last_30_days"] == pytest.approx(1.98, rel=1e-2)
    assert summary["monthly_appointments"] == 2
    assert summary["monthly_services_booked"] == 2
    assert summary["monthly_growth_rate"] == 0

    assert len(dashboard["recent_appointments"]) == 2
    assert len(dashboard["appointment_time_series"]) == 2
