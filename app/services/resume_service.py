
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User


# Directory where uploaded resumes will be stored.
UPLOAD_DIR = Path("uploads/resumes")

# Maximum permitted file size: 5 MB.
MAX_FILE_SIZE = 5 * 1024 * 1024

# Allowed resume extensions.
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}


# ----------------------------------------------------------
# UPLOAD RESUME
# ----------------------------------------------------------

async def upload_resume(
    db: Session,
    user: User,
    file: UploadFile
):

    # Get and validate the file extension.
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOC and DOCX files are allowed"
        )

    # Read the file and check its actual size.
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Resume must not exceed 5 MB"
        )

    # Create the upload directory if it does not exist.
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename to avoid collisions.
    unique_filename = f"{uuid4().hex}{extension}"

    # Build the destination path.
    file_path = UPLOAD_DIR / unique_filename

    # Save the file on the server.
    file_path.write_bytes(contents)

    # Remove the user's previous resume after the new file is saved.
    old_file_path = user.resume_file_path

    # Update resume metadata in the database.
    user.resume_filename = Path(file.filename).name
    user.resume_file_path = str(file_path)
    user.resume_uploaded_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()

        # Remove the newly saved file if the database update fails.
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Could not save resume information"
        )

    # Delete the previous file only after a successful database commit.
    if old_file_path:
        Path(old_file_path).unlink(missing_ok=True)

    return user


# ----------------------------------------------------------
# DELETE RESUME
# ----------------------------------------------------------

def delete_resume(db: Session, user: User):

    if not user.resume_file_path:
        raise HTTPException(
            status_code=404,
            detail="No resume found"
        )

    file_path = Path(user.resume_file_path)

    # Clear resume information in PostgreSQL.
    user.resume_filename = None
    user.resume_file_path = None
    user.resume_uploaded_at = None

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not delete resume information"
        )

    # Delete the physical file after the database update succeeds.
    file_path.unlink(missing_ok=True)

    return True
