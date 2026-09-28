from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.all_models import User, Grant, Application, Organisation
from app.models.enums import (
    GrantStageClassification, GrantApplicationStatus, ApplicationStatus
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Counts
    open_grants_count = db.query(Grant).filter(Grant.application_status == GrantApplicationStatus.OPEN).count()
    idea_stage_count = db.query(Grant).filter(Grant.stage_classification == GrantStageClassification.GREEN_IDEA).count()
    
    in_progress_apps = db.query(Application).filter(Application.status.in_([
        ApplicationStatus.PREPARING,
        ApplicationStatus.READY_TO_APPLY,
        ApplicationStatus.APPLICATION_STARTED
    ])).count()

    requiring_attention_apps = db.query(Application).filter(Application.status.in_([
        ApplicationStatus.WAITING_FOR_USER,
        ApplicationStatus.READY_FOR_REVIEW
    ])).count()

    # Funding Potential calculation
    total_funding_potential = db.query(func.sum(Grant.funding_amount_max)).scalar() or 0.0

    # Recent Grants
    recent_grants = db.query(Grant).order_by(Grant.created_at.desc()).limit(5).all()
    recent_grants_data = [{
        "id": g.id,
        "grant_name": g.grant_name,
        "funder": g.funder,
        "amount_max": g.funding_amount_max,
        "stage": g.stage_classification.value,
        "deadline": g.deadline,
        "status": g.application_status.value
    } for g in recent_grants]

    # Recent Submissions
    submitted_apps = db.query(Application).filter(Application.status.in_([
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.AWARDED
    ])).order_by(Application.submission_date.desc()).limit(5).all()

    submitted_apps_data = [{
        "id": a.id,
        "grant_name": a.grant.grant_name if a.grant else "Grant",
        "organisation_name": a.organisation.organisation_name if a.organisation else "Organisation",
        "reference": a.application_reference,
        "submission_date": a.submission_date,
        "status": a.status.value
    } for a in submitted_apps]

    # Upcoming Deadlines
    upcoming_grants = db.query(Grant).filter(Grant.deadline != None).order_by(Grant.deadline.asc()).limit(5).all()
    upcoming_deadlines = [{
        "id": g.id,
        "grant_name": g.grant_name,
        "funder": g.funder,
        "deadline": g.deadline,
        "amount_max": g.funding_amount_max
    } for g in upcoming_grants]

    return {
        "open_grants": open_grants_count,
        "idea_stage_grants": idea_stage_count,
        "applications_in_progress": in_progress_apps,
        "applications_requiring_attention": requiring_attention_apps,
        "funding_potential_usd": total_funding_potential,
        "recent_grants": recent_grants_data,
        "recent_submissions": submitted_apps_data,
        "upcoming_deadlines": upcoming_deadlines
    }
