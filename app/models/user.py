

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # User information
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # job_seeker, recruiter or admin
    role = Column(String(30), default="job_seeker", nullable=False)

    # Resume file information
    resume_filename = Column(String(255), nullable=True)
    resume_file_path = Column(String(500), nullable=True)
    resume_uploaded_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # Jobs created by this recruiter
    jobs = relationship(
        "Job",
        back_populates="recruiter"
    )

    # Applications submitted by this user
    applications = relationship(
        "Application",
        back_populates="applicant"
    )
