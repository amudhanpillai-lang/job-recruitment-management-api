
# Import FastAPI components
from fastapi import APIRouter, Depends, HTTPException, status

# Import OAuth2 login form
from fastapi.security import OAuth2PasswordRequestForm

# Import SQLAlchemy
from sqlalchemy.orm import Session

# Import database dependency
from app.database import get_db

# Import User model
from app.models.user import User

# Import Pydantic schemas
from app.schemas.user import UserCreate, UserResponse, TokenResponse

# Import security functions
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token
)

# Import authentication dependencies
from app.auth.dependencies import (
    get_current_user,
    require_role
)


# Create authentication router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================================================
# 1. USER REGISTRATION
# ==========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # Check whether email already exists
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash the user's password
    hashed_password = hash_password(user.password)

    # Create new user
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role="job_seeker"
    )

    try:
        # Add user to database
        db.add(new_user)

        # Save changes
        db.commit()

        # Retrieve generated user ID
        db.refresh(new_user)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not register user"
        )

    return new_user


# ==========================================================
# 2. USER LOGIN
# ==========================================================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # OAuth2 form uses username as the email address
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    # Check user and password
    if user is None or not verify_password(
        form_data.password,
        user.hashed_password
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Generate JWT token
    access_token = create_access_token(
        data={
            "sub": str(user.id)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ==========================================================
# 3. GET CURRENT USER
# ==========================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):

    return current_user


# ==========================================================
# 4. ADMIN-ONLY ENDPOINT
# ==========================================================

@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(require_role("admin"))
):

    return {
        "message": "Welcome to the Admin Dashboard",
        "user": current_user.name,
        "role": current_user.role
    }


# ==========================================================
# 5. RECRUITER-ONLY ENDPOINT
# ==========================================================

@router.get("/recruiter")
def recruiter_dashboard(
    current_user: User = Depends(require_role("recruiter"))
):

    return {
        "message": "Welcome to the Recruiter Dashboard",
        "user": current_user.name,
        "role": current_user.role
    }


# ==========================================================
# 6. JOB SEEKER-ONLY ENDPOINT
# ==========================================================

@router.get("/job-seeker")
def job_seeker_dashboard(
    current_user: User = Depends(require_role("job_seeker"))
):

    return {
        "message": "Welcome to the Job Seeker Dashboard",
        "user": current_user.name,
        "role": current_user.role
    }
