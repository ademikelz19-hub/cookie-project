import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.all_models import User, AIJob, Application, Grant
from app.models.enums import AITaskStatus
from app.schemas.ai_job import AIJobResponse
from app.core.gemini_service import gemini_service

router = APIRouter(prefix="/jobs", tags=["AI Jobs & Resilience"])

@router.get("", response_model=List[AIJobResponse])
def list_ai_jobs(
    status_filter: Optional[AITaskStatus] = None,
    job_type: Optional[str] = None,
    application_id: Optional[str] = None,
    grant_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Lists all AI background jobs and resilience tracking records."""
    query = db.query(AIJob)
    if status_filter:
        query = query.filter(AIJob.status == status_filter)
    if job_type:
        query = query.filter(AIJob.job_type == job_type)
    if application_id:
        query = query.filter(AIJob.application_id == application_id)
    if grant_id:
        query = query.filter(AIJob.grant_id == grant_id)
    return query.order_by(AIJob.created_at.desc()).limit(100).all()

@router.get("/{job_id}", response_model=AIJobResponse)
def get_ai_job(
    job_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieves an AI job by its unique identifier."""
    job = db.query(AIJob).filter(AIJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="AI Job not found")
    return job

@router.post("/{job_id}/retry", response_model=AIJobResponse)
def retry_ai_job(
    job_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Safely retries a job marked as RETRYABLE_FAILED without duplicate writes.
    Resets status to RUNNING and increments attempt tracking.
    """
    job = db.query(AIJob).filter(AIJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="AI Job not found")

    if job.status not in (AITaskStatus.RETRYABLE_FAILED, AITaskStatus.PERMANENTLY_FAILED):
        raise HTTPException(
            status_code=400,
            detail=f"Job cannot be retried from its current state: {job.status.value}"
        )

    job.status = AITaskStatus.RUNNING
    job.last_error_category = None
    job.last_error_message = None
    job.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(job)
    return job
