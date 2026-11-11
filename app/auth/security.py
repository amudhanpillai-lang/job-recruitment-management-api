
# Import required libraries
import os

from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from pwdlib import PasswordHash
import jwt


# Load environment variables from .env
load_dotenv()


# ==========================================================
# 1. JWT CONFIGURATION
# ==========================================================

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

# Stop application startup if secret key is missing
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing from .env")


# ==========================================================
# 2. PASSWORD HASHING
# ==========================================================

# Initialize Argon2 password hashing
password_hash = PasswordHash.recommended()


# Hash password before storing in database
def hash_password(password: str):

    return password_hash.hash(password)


# Verify password during login
def verify_password(plain_password: str, hashed_password: str):

    return password_hash.verify(
        plain_password,
        hashed_password
    )


# ==========================================================
# 3. JWT TOKEN GENERATION
# ==========================================================

def create_access_token(data: dict):

    # Copy user information
    to_encode = data.copy()

    # Set token expiration
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Add expiration and issued-at timestamps
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })

    # Generate signed JWT token
    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# ==========================================================
# 4. JWT TOKEN VERIFICATION
# ==========================================================

def decode_access_token(token: str):

    # Decode and verify JWT signature and expiration
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    return payload
