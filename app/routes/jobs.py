

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from redis.exceptions import RedisError

from app.database import get_db
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, JobResponse

from app.auth.dependencies import require_role
from app.services import job_service
from app.core.redis import redis_client


# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


# ----------------------------------------------------------
# REDIS CACHE CONFIGURATION
# ----------------------------------------------------------

JOBS_CACHE_KEY = "jobs:all:v1"
CACHE_TTL = 300  # 5 minutes


def invalidate_jobs_cache():
    """
    Delete cached job listings after a job is modified.
    """
    try:
        redis_client.delete(JOBS_CACHE_KEY)
        logger.info("Job cache invalidated successfully")

    except RedisError:
        logger.exception("Redis cache invalidation failed")


# ----------------------------------------------------------
# CREATE JOB
# Only recruiters and admins can create jobs.
# ----------------------------------------------------------

@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter", "admin"))
):

    new_job = job_service.create_job(
        db,
        job_data,
        current_user.id
    )

    invalidate_jobs_cache()

    logger.info("New job created: ID %s", new_job.id)

    return new_job


# ----------------------------------------------------------
# GET ALL JOBS
# Public endpoint with Redis caching.
# ----------------------------------------------------------

@router.get("/", response_model=list[JobResponse])
def get_all_jobs(db: Session = Depends(get_db)):

    # STEP 1: Check Redis cache
    try:
        cached_jobs = redis_client.get(JOBS_CACHE_KEY)

        if cached_jobs is not None:

            try:
                jobs_data = json.loads(cached_jobs)

                logger.info("REDIS CACHE HIT: Returning cached jobs")

                return jobs_data

            except json.JSONDecodeError:
                logger.warning("Invalid JSON in Redis cache; removing key")
                redis_client.delete(JOBS_CACHE_KEY)

        logger.info("REDIS CACHE MISS: Fetching jobs from PostgreSQL")

    except RedisError:
        logger.exception("Redis read failed; falling back to PostgreSQL")

    # STEP 2: Fetch jobs from PostgreSQL
    jobs = job_service.get_all_jobs(db)

    # STEP 3: Convert SQLAlchemy objects into JSON-compatible dictionaries
    jobs_data = [
        JobResponse.model_validate(job).model_dump(mode="json")
        for job in jobs
    ]

    # STEP 4: Store results in Redis
    try:
        result = redis_client.setex(
            JOBS_CACHE_KEY,
            CACHE_TTL,
            json.dumps(jobs_data)
        )

        if result:
            logger.info(
                "REDIS CACHE STORED: %s jobs, TTL %s seconds",
                len(jobs_data),
                CACHE_TTL
            )
        else:
            logger.warning("Redis did not confirm cache storage")

    except RedisError:
        logger.exception("Redis write failed; returning database results")

    return jobs_data


# ----------------------------------------------------------
# SEARCH JOBS
# ----------------------------------------------------------

@router.get("/search", response_model=list[JobResponse])
def search_jobs(
    location: str = None,
    min_salary: float = None,
    db: Session = Depends(get_db)
):

    return job_service.search_jobs(
        db,
        location,
        min_salary
    )


# ----------------------------------------------------------
# GET JOB BY ID
# ----------------------------------------------------------

@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = job_service.get_job_by_id(db, job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


# ----------------------------------------------------------
# UPDATE JOB
# Only the recruiter who owns the job or an admin can update it.
# ----------------------------------------------------------

@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter", "admin"))
):

    job = job_service.get_job_by_id(db, job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    if current_user.role != "admin" and job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot update this job"
        )

    updated_job = job_service.update_job(
        db,
        job,
        job_data
    )

    invalidate_jobs_cache()

    logger.info("Job updated: ID %s", job_id)

    return updated_job


# ----------------------------------------------------------
# DELETE JOB
# Only the recruiter who owns the job or an admin can delete it.
# ----------------------------------------------------------

@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter", "admin"))
):

    job = job_service.get_job_by_id(db, job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    if current_user.role != "admin" and job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete this job"
        )

    job_service.delete_job(db, job)

    invalidate_jobs_cache()

    logger.info("Job deleted: ID %s", job_id)

    return {
        "message": "Job deleted successfully",
        "job_id": job_id
    }

