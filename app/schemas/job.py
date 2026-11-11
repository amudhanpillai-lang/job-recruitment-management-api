
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# Data required when a recruiter creates a job.
class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    company: str = Field(min_length=2, max_length=150)
    description: str
    location: str
    salary: float = Field(gt=0)


# Data accepted when updating a job.
# Every field is optional.
class JobUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=150)
    company: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[float] = Field(default=None, gt=0)


# Data returned to API clients.
class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    description: str
    location: str
    salary: float
    recruiter_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
