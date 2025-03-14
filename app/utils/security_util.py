from passlib.context import CryptContext
from typing import Union, Any
from datetime import timedelta, datetime, timezone
from ..core.config import settings
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

pwd_hasing = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str, expire_time: timedelta = None):
    if expire_time:
        expire = datetime.now(timezone.utc) + expire_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_TIME
        )
    print(f"sub==>> {subject}")
    to_encode = {"exp": expire, "sub": subject}
    encoded_token = jwt.encode(to_encode, algorithm="HS256", key=settings.SECRETE_KEY)
    return encoded_token


def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRETE_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.ExpiredSignatureError:

        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print(f"exception==>> {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


def verify_password(plain_password: str, hash_password: str) -> bool:
    return pwd_hasing.verify(plain_password, hash_password)


def get_password_hash(plain_password: str) -> str:
    return pwd_hasing.hash(plain_password)
