from typing import Optional
from sqlalchemy.orm import Session
from ..models.business_model import Business
from ..schemas.auth import BusinessCreate
from ..utils.security_util import get_password_hash

class BusinessRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[Business]:
        return self.db.query(Business).filter(Business.email == email).first()

    def get_by_id(self, business_id: str) -> Optional[Business]:
        return self.db.query(Business).filter(Business.id == business_id).first()

    def create(self, business_data: BusinessCreate) -> Business:
        hashed_password = get_password_hash(business_data.password)
        db_business = Business(
            business_name=business_data.business_name,
            email=business_data.email,
            password=hashed_password,
            phone_number=business_data.phone_number,
            timeglobe_auth_key=business_data.timeglobe_auth_key
        )
        self.db.add(db_business)
        self.db.commit()
        self.db.refresh(db_business)
        return db_business

    def update_password(self, business_id: str, new_password: str) -> None:
        hashed_password = get_password_hash(new_password)
        self.db.query(Business).filter(Business.id == business_id).update(
            {"password": hashed_password}
        )
        self.db.commit()

    def create_business(self, business_name: str, email: str, password: str, 
                       phone_number: str = None, timeglobe_auth_key: str = None, 
                       customer_cd: str = None) -> Business:
        """
        Create a business with all fields explicitly defined
        """
        hashed_password = get_password_hash(password)
        db_business = Business(
            business_name=business_name,
            email=email,
            password=hashed_password,
            phone_number=phone_number,
            timeglobe_auth_key=timeglobe_auth_key,
            customer_cd=customer_cd
        )
        self.db.add(db_business)
        self.db.commit()
        self.db.refresh(db_business)
        return db_business

    def update(self, business_id: str, data: dict) -> None:
        """
        Update business record with a dictionary of fields to update
        
        Args:
            business_id: The ID of the business to update
            data: Dictionary of fields to update, e.g. {"timeglobe_auth_key": "key", "customer_cd": "cd"}
        """
        self.db.query(Business).filter(Business.id == business_id).update(data)
        self.db.commit()
        
    def update_business_info(self, business_id: str, data: dict) -> Business:
        """
        Update business information
        
        Args:
            business_id: The ID of the business to update
            data: Dictionary of fields to update
            
        Returns:
            Updated business object
        """
        business = self.db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return None
            
        # Update only provided fields
        for key, value in data.items():
            if hasattr(business, key) and value is not None:
                setattr(business, key, value)
                
        self.db.commit()
        self.db.refresh(business)
        return business
        
    def delete_business_info(self, business_id: str, fields: list) -> Business:
        """
        Delete specific business information fields by setting them to None
        
        Args:
            business_id: The ID of the business
            fields: List of field names to clear
            
        Returns:
            Updated business object
        """
        business = self.db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return None
            
        # Set specified fields to None
        for field in fields:
            if hasattr(business, field):
                setattr(business, field, None)
                
        self.db.commit()
        self.db.refresh(business)
        return business