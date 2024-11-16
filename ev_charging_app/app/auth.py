from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from .config import settings

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt", "argon2"], deprecated="auto")

# Authentication settings
ALGORITHM = settings.JWT_ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new JWT access token with an expiration time.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    """
    Create a new JWT refresh token with a longer expiration time.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    """
    Decode a JWT token to extract the payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if a plain password matches its hashed version.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a hashed version of a plain password.
    """
    return pwd_context.hash(password)


def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token has expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if not exp:
            return True
        return datetime.utcnow() > datetime.utcfromtimestamp(exp)
    except JWTError:
        return True


def renew_access_token(refresh_token: str):
    """
    Renew an access token using a valid refresh token.
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")
        if is_token_expired(refresh_token):
            raise ValueError("Refresh token expired")
        new_access_token = create_access_token({"sub": payload.get("sub")})
        return new_access_token
    except JWTError as e:
        raise ValueError(f"Token renewal failed: {str(e)}")


def validate_token(token: str, expected_type: str = "access") -> dict:
    """
    Validate a JWT token and ensure it matches the expected type.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            raise ValueError(f"Invalid token type. Expected: {expected_type}")
        return payload
    except JWTError as e:
        raise ValueError(f"Token validation failed: {str(e)}")
