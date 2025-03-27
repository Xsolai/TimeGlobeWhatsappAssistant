from sqlalchemy.orm import Session
from typing import Optional
from ..models.customer_model import CustomerModel
from ..models.user import UserModel
from ..schemas.auth import UserCreate, User
from ..utils.security_util import get_password_hash
from ..logger import main_logger


class UserRepository:
    def __init__(self, db: Session):  # Use synchronous Session
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        main_logger.debug(f"Fetching user by ID: {user_id}")
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            main_logger.warning(f"User not found with ID: {user_id}")
        else:
            main_logger.info(f"User fetched successfully: {user.email}")
        return user

    def get_by_email(self, email: str) -> Optional[UserModel]:
        main_logger.debug(f"Fetching user by email: {email}")
        user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            main_logger.warning(f"User not found with email: {email}")
        else:
            main_logger.info(f"User fetched successfully: {email}")
        return user

    def create(self, user: UserCreate) -> dict:
        main_logger.debug(f"Creating user with email: {user.email}")
        hashed_password = get_password_hash(user.password)
        _user = UserModel(name=user.name, password=hashed_password, email=user.email)
        self.db.add(_user)
        self.db.commit()
        self.db.refresh(_user)
        main_logger.info(f"User created successfully: {user.email}")
        return {"message": "User Registered Successfully"}

    def update(self, user_id: int, password: str) -> Optional[User]:
        main_logger.debug(f"Updating user with ID: {user_id}")
        user = self.get_by_id(user_id)
        if not user:
            main_logger.warning(f"User not found with ID: {user_id}")
            return None

        user.password = get_password_hash(password)
        self.db.commit()
        self.db.refresh(user)
        main_logger.info(f"User updated successfully: {user.email}")
        return user

    def delete(self, user_id: int) -> bool:
        main_logger.debug(f"Deleting user with ID: {user_id}")
        user = self.get_by_id(user_id)
        if not user:
            main_logger.warning(f"User not found with ID: {user_id}")
            return False

        self.db.delete(user)
        self.db.commit()
        main_logger.info(f"User deleted successfully: {user.email}")
        return True
