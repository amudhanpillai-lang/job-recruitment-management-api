
# Import FastAPI components
from fastapi import Depends, HTTPException, status

# Import OAuth2 bearer token support
from fastapi.security import OAuth2PasswordBearer

# Import SQLAlchemy session
from sqlalchemy.orm import Session

# Import database dependency
from app.database import get_db

# Import User database model
from app.models.user import User

# Import JWT decoder
from app.auth.security import decode_access_token

# Import JWT exception
from jwt.exceptions import InvalidTokenError


# ==========================================================
# 1. OAUTH2 CONFIGURATION
# ==========================================================

# Swagger will use the login endpoint to obtain a token.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ==========================================================
# 2. GET CURRENT LOGGED-IN USER
# ==========================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    # Error response for invalid authentication
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:

        # Decode JWT token
        payload = decode_access_token(token)

        # Extract user ID from token subject
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        # Convert user ID to integer
        user_id = int(user_id)

    except (InvalidTokenError, TypeError, ValueError):
        raise credentials_exception

    # Find user in PostgreSQL
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise credentials_exception

    return user


# ==========================================================
# 3. ROLE-BASED AUTHORIZATION
# ==========================================================

def require_role(*allowed_roles):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):

        # Check whether user's role is permitted
        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return current_user

    return role_checker
