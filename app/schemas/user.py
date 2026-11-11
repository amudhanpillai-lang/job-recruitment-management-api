
# Import Pydantic components
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Schema for user registration
class UserCreate(BaseModel):

    name: str = Field(min_length=2, max_length=100)

    email: EmailStr

    password: str = Field(min_length=8, max_length=128)


# Schema for returning user information
class UserResponse(BaseModel):

    id: int

    name: str

    email: EmailStr

    role: str

    # Allows Pydantic to read SQLAlchemy objects
    model_config = ConfigDict(from_attributes=True)


# Schema for returning JWT token
class TokenResponse(BaseModel):

    access_token: str

    token_type: str
