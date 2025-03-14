from sqlalchemy.orm import Session
from typing import Optional
from ..models.user import UserModel
from ..schemas.auth import UserCreate, User
from ..utils.security_util import get_password_hash


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def create(self, user: UserCreate) -> dict:
        hashed_password = get_password_hash(user.password)
        _user = UserModel(name=user.name, password=hashed_password, email=user.email)
        self.db.add(_user)
        self.db.commit()
        self.db.refresh(_user)
        return {"message": "User Registered Successfully"}

    def update(self, user_id: int, password) -> Optional[User]:
        user = self.get_by_id(user_id)
        if not user:
            return None

        # for key, value in kwargs.items():
        #     if key == "password":
        #         setattr(user, "password", get_password_hash(value))
        #     else:
        #         setattr(user, key, value)
        user.password = get_password_hash(password)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
