
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.application import Application
from app.models.job import Job


# ----------------------------------------------------------
# SUBMIT APPLICATION
# ----------------------------------------------------------

def submit_application(
    db: Session,
    job_id: int,
    applicant_id: int,
    cover_letter: str = None
):

    application = Application(
        job_id=job_id,
        applicant_id=applicant_id,
        cover_letter=cover_letter,
        status="Applied"
    )

    try:
        db.add(application)
        db.commit()
        db.refresh(application)

    except IntegrityError:
        # The unique database constraint prevents duplicate applications.
        db.rollback()
        return None

    return application


# ----------------------------------------------------------
# GET APPLICATIONS SUBMITTED BY A USER
# ----------------------------------------------------------

def get_my_applications(db: Session, applicant_id: int):

    return (
        db.query(Application)
        .filter(Application.applicant_id == applicant_id)
        .order_by(Application.applied_at.desc())
        .all()
    )


# ----------------------------------------------------------
# GET APPLICATIONS FOR A RECRUITER'S JOBS
# ----------------------------------------------------------

def get_recruiter_applications(
    db: Session,
    recruiter_id: int
):

    return (
        db.query(Application)
        .join(Job, Application.job_id == Job.id)
        .filter(Job.recruiter_id == recruiter_id)
        .order_by(Application.applied_at.desc())
        .all()
    )


# ----------------------------------------------------------
# GET APPLICATION BY ID
# ----------------------------------------------------------

def get_application_by_id(db: Session, application_id: int):

    return (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )


# ----------------------------------------------------------
# UPDATE APPLICATION STATUS
# ----------------------------------------------------------

def update_application_status(
    db: Session,
    application: Application,
    new_status: str
):

    application.status = new_status

    db.commit()
    db.refresh(application)

    return application
