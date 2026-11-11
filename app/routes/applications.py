
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.job import Job

from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatusUpdate
)

from app.auth.dependencies import get_current_user, require_role
from app.services import application_service


router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)


# Allowed application statuses.
ApplicationStatus = Literal[
    "Applied",
    "Under Review",
    "Shortlisted",
    "Rejected"
]


# ----------------------------------------------------------
# APPLY FOR A JOB
# Only authenticated job seekers can apply.
# ----------------------------------------------------------

@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
def apply_for_job(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("job_seeker"))
):

    # Confirm that the requested job exists.
    job = db.query(Job).filter(
        Job.id == application_data.job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Prevent recruiters from applying to their own job.
    if job.recruiter_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot apply to your own job"
        )

    # Submit the application.
    new_application = application_service.submit_application(
        db=db,
        job_id=application_data.job_id,
        applicant_id=current_user.id,
        cover_letter=application_data.cover_letter
    )

    # None means the unique constraint detected a duplicate.
    if new_application is None:
        raise HTTPException(
            status_code=409,
            detail="You have already applied for this job"
        )

    return new_application


# ----------------------------------------------------------
# VIEW MY APPLICATIONS
# Job seekers can view their own applications.
# ----------------------------------------------------------

@router.get(
    "/my-applications",
    response_model=list[ApplicationResponse]
)
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("job_seeker"))
):

    return application_service.get_my_applications(
        db,
        current_user.id
    )


# ----------------------------------------------------------
# VIEW APPLICATIONS RECEIVED BY RECRUITER
# Recruiters see applications only for their own jobs.
# ----------------------------------------------------------

@router.get(
    "/recruiter",
    response_model=list[ApplicationResponse]
)
def get_recruiter_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter", "admin"))
):

    # Admin can view all applications.
    if current_user.role == "admin":
        from app.models.application import Application

        return (
            db.query(Application)
            .order_by(Application.applied_at.desc())
            .all()
        )

    return application_service.get_recruiter_applications(
        db,
        current_user.id
    )


# ----------------------------------------------------------
# UPDATE APPLICATION STATUS
# Only the recruiter who owns the job or an admin can update.
# ----------------------------------------------------------

@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse
)
def update_application_status(
    application_id: int,
    status_data: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter", "admin"))
):

    # Validate the requested status.
    allowed_statuses = [
        "Applied",
        "Under Review",
        "Shortlisted",
        "Rejected"
    ]

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid application status"
        )

    application = application_service.get_application_by_id(
        db,
        application_id
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    # Verify that the recruiter owns the job.
    if (
        current_user.role != "admin"
        and application.job.recruiter_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot update this application"
        )

    return application_service.update_application_status(
        db,
        application,
        status_data.status
    )
