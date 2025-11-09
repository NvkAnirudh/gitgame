"""
Security utilities for authentication and authorization
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing context with explicit configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password (max 72 bytes for bcrypt)

    Returns:
        Hashed password string
    """
    # Ensure password is a string and encode to handle any special characters
    if isinstance(password, bytes):
        password = password.decode('utf-8')

    # Truncate to 72 bytes if needed (bcrypt limitation)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Dictionary containing user data (typically {'sub': user_id})
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token

    Args:
        data: Dictionary containing user data (typically {'sub': user_id})
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """
    Verify a token and return the subject (user_id)

    Args:
        token: JWT token string
        token_type: Expected token type ('access' or 'refresh')

    Returns:
        User ID (sub) from token or None if invalid
    """
    payload = decode_token(token)

    if payload is None:
        return None

    # Check token type
    if payload.get("type") != token_type:
        return None

    # Get user ID
    user_id: str = payload.get("sub")
    if user_id is None:
        return None

    return user_id


def create_password_reset_token(email: str) -> str:
    """
    Create a password reset token

    Args:
        email: User's email address

    Returns:
        Encoded token
    """
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {"sub": email, "exp": expire, "type": "password_reset"}
    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_token


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token

    Args:
        token: Password reset token

    Returns:
        Email from token or None if invalid
    """
    payload = decode_token(token)

    if payload is None:
        return None

    # Check token type
    if payload.get("type") != "password_reset":
        return None

    email: str = payload.get("sub")
    return email
