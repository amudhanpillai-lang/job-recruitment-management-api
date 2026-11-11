
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Application(Base):
    __tablename__ = "applications"

    # Prevent a user from applying to the same job twice.
    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "applicant_id",
            name="unique_job_application"
        ),
    )

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Job being applied for.
    job_id = Column(
        Integer,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False
    )

    # User who submitted the application.
    applicant_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # Application status.
    status = Column(
        String(30),
        default="Applied",
        nullable=False
    )

    # Optional cover letter.
    cover_letter = Column(String, nullable=True)

    # Automatically records submission time.
    applied_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationship with the job.
    job = relationship(
        "Job",
        back_populates="applications"
    )

    # Relationship with the applicant.
    applicant = relationship(
        "User",
        back_populates="applications"
    )
