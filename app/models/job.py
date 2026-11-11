
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Job information
    title = Column(String(150), nullable=False)
    company = Column(String(150), nullable=False)
    description = Column(String, nullable=False)
    location = Column(String(100), nullable=False)
    salary = Column(Float, nullable=False)

    # Recruiter who created this job.
    # Nullable temporarily to preserve existing Module 2 job records.
    recruiter_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # Relationship with the recruiter.
    recruiter = relationship(
        "User",
        back_populates="jobs"
    )

    # All applications submitted for this job.
    applications = relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan"
    )
