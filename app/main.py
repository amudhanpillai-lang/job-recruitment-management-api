
from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO)

# Import models so Alembic can detect all database tables.
from app.models import Job, User, Application
#import services so that they are initialized and ready to use.
from app.routes.resumes import router as resume_router


# Import API routers.
from app.routes.jobs import router as job_router
from app.routes.auth import router as auth_router
from app.routes.applications import router as application_router


# ----------------------------------------------------------
# CREATE FASTAPI APPLICATION
# ----------------------------------------------------------

app = FastAPI(
    title="Job Recruitment Management API",
    description="Backend API for managing jobs, users and applications",
    version="1.0.0"
)


# ----------------------------------------------------------
# REGISTER ROUTERS
# ----------------------------------------------------------

app.include_router(job_router)
app.include_router(auth_router)
app.include_router(application_router)
app.include_router(resume_router)


# ----------------------------------------------------------
# HOME ENDPOINT
# ----------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to the Job Recruitment Management API!",
        "status": "running"
    }


# ----------------------------------------------------------
# HEALTH CHECK
# ----------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Job Recruitment Management API"
    }
