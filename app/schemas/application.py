
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from typing import Literal


# Data submitted by a job seeker.
class ApplicationCreate(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None


# Data used when a recruiter changes application status.
class ApplicationStatusUpdate(BaseModel):
    status: Literal[
        "Applied",
        "Under Review",
        "Shortlisted",
        "Rejected"
    ]


# Application information returned by the API.
class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    applicant_id: int
    status: str
    cover_letter: Optional[str] = None
    applied_at: datetime

    model_config = ConfigDict(from_attributes=True)
