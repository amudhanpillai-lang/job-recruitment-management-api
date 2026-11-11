
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.application import Application
from app.models.job import Job

from app.auth.dependencies import get_current_user, require_role
from app.services import resume_service


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)


# ----------------------------------------------------------
# UPLOAD OR REPLACE RESUME
# Only job seekers can upload resumes.
# ----------------------------------------------------------

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("job_seeker"))
):

    user = await resume_service.upload_resume(
        db,
        current_user,
        file
    )

    return {
        "message": "Resume uploaded successfully",
        "filename": user.resume_filename,
        "uploaded_at": user.resume_uploaded_at
    }


# ----------------------------------------------------------
# VIEW MY RESUME INFORMATION
# ----------------------------------------------------------

@router.get("/me")
def get_my_resume(
    current_user: User = Depends(require_role("job_seeker"))
):

    if not current_user.resume_file_path:
        raise HTTPException(
            status_code=404,
            detail="No resume uploaded"
        )

    return {
        "filename": current_user.resume_filename,
        "uploaded_at": current_user.resume_uploaded_at
    }


# ----------------------------------------------------------
# DOWNLOAD MY RESUME
# ----------------------------------------------------------

@router.get("/download")
def download_my_resume(
    current_user: User = Depends(require_role("job_seeker"))
):

    if not current_user.resume_file_path:
        raise HTTPException(
            status_code=404,
            detail="No resume uploaded"
        )

    file_path = Path(current_user.resume_file_path)

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Resume file not found on server"
        )

    return FileResponse(
        path=file_path,
        filename=current_user.resume_filename
    )


# ----------------------------------------------------------
# DELETE MY RESUME
# ----------------------------------------------------------

@router.delete("/me")
def delete_my_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("job_seeker"))
):

    resume_service.delete_resume(db, current_user)

    return {
        "message": "Resume deleted successfully"
    }


# ----------------------------------------------------------
# RECRUITER DOWNLOADS AN APPLICANT'S RESUME
# Recruiters can only access applicants for their own jobs.
# Admins can access any applicant's resume.
# ----------------------------------------------------------

@router.get("/applicant/{applicant_id}")
def download_applicant_resume(
    applicant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter", "admin"))
):

    applicant = db.query(User).filter(
        User.id == applicant_id
    ).first()

    if not applicant:
        raise HTTPException(
            status_code=404,
            detail="Applicant not found"
        )

    # Check whether the recruiter owns a job
    # that this applicant has applied for.
    if current_user.role != "admin":

        has_applied_to_recruiter_job = (
            db.query(Application)
            .join(Job, Application.job_id == Job.id)
            .filter(
                Application.applicant_id == applicant_id,
                Job.recruiter_id == current_user.id
            )
            .first()
        )

        if not has_applied_to_recruiter_job:
            raise HTTPException(
                status_code=403,
                detail="You cannot access this applicant's resume"
            )

    if not applicant.resume_file_path:
        raise HTTPException(
            status_code=404,
            detail="Applicant has not uploaded a resume"
        )

    file_path = Path(applicant.resume_file_path)

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Resume file not found on server"
        )

    return FileResponse(
        path=file_path,
        filename=applicant.resume_filename
    )
