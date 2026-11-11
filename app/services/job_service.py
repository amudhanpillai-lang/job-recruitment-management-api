
from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


# ----------------------------------------------------------
# CREATE JOB
# ----------------------------------------------------------

def create_job(db: Session, job_data: JobCreate, recruiter_id: int):

    # Convert validated Pydantic data into a SQLAlchemy model.
    new_job = Job(
        **job_data.model_dump(),
        recruiter_id=recruiter_id
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


# ----------------------------------------------------------
# GET ALL JOBS
# ----------------------------------------------------------

def get_all_jobs(db: Session):

    return db.query(Job).order_by(Job.id.desc()).all()


# ----------------------------------------------------------
# GET JOB BY ID
# ----------------------------------------------------------

def get_job_by_id(db: Session, job_id: int):

    return db.query(Job).filter(Job.id == job_id).first()


# ----------------------------------------------------------
# UPDATE JOB
# ----------------------------------------------------------

def update_job(
    db: Session,
    job: Job,
    update_data: JobUpdate
):

    # Extract only fields supplied by the recruiter.
    updated_fields = update_data.model_dump(exclude_unset=True)

    for field, value in updated_fields.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)

    return job


# ----------------------------------------------------------
# DELETE JOB
# ----------------------------------------------------------

def delete_job(db: Session, job: Job):

    db.delete(job)
    db.commit()

    return True


# ----------------------------------------------------------
# SEARCH JOBS
# ----------------------------------------------------------

def search_jobs(
    db: Session,
    location: str = None,
    min_salary: float = None
):

    query = db.query(Job)

    # Filter by location when supplied.
    if location:
        query = query.filter(
            Job.location.ilike(f"%{location}%")
        )

    # Filter by minimum salary when supplied.
    if min_salary is not None:
        query = query.filter(Job.salary >= min_salary)

    return query.order_by(Job.id.desc()).all()
