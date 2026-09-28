from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.all_models import User, Organisation, Grant, GrantMatch, AuditLog
from app.schemas.grant import GrantMatchResult
from app.agents.matcher import grant_matcher

router = APIRouter(prefix="/matching", tags=["Grant Matching"])

class AnalyseMatchRequest(BaseModel):
    organisation_id: str
    grant_id: str

@router.post("/analyse", response_model=GrantMatchResult)
def analyse_grant_match(
    req: AnalyseMatchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    org = db.query(Organisation).filter(Organisation.id == req.organisation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    grant = db.query(Grant).filter(Grant.id == req.grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")

    match_result = grant_matcher.evaluate_match(org, grant)

    # Upsert match record in DB
    existing = db.query(GrantMatch).filter(
        GrantMatch.organisation_id == org.id,
        GrantMatch.grant_id == grant.id
    ).first()

    if existing:
        existing.eligibility_status = match_result["eligibility_status"]
        existing.relevance_score = match_result["relevance_score"]
        existing.strong_match_factors = match_result["strong_match_factors"]
        existing.weak_match_factors = match_result["weak_match_factors"]
        existing.missing_requirements = match_result["missing_requirements"]
        existing.disqualifying_requirements = match_result["disqualifying_requirements"]
        existing.information_needed = match_result["information_needed"]
    else:
        existing = GrantMatch(
            organisation_id=org.id,
            grant_id=grant.id,
            eligibility_status=match_result["eligibility_status"],
            relevance_score=match_result["relevance_score"],
            strong_match_factors=match_result["strong_match_factors"],
            weak_match_factors=match_result["weak_match_factors"],
            missing_requirements=match_result["missing_requirements"],
            disqualifying_requirements=match_result["disqualifying_requirements"],
            information_needed=match_result["information_needed"]
        )
        db.add(existing)

    db.commit()
    db.refresh(existing)

    audit = AuditLog(
        user_id=user.id,
        action="grant_analysed",
        target_type="grant_match",
        target_id=existing.id,
        details={
            "organisation": org.organisation_name,
            "grant": grant.grant_name,
            "status": existing.eligibility_status.value,
            "score": existing.relevance_score
        }
    )
    db.add(audit)
    db.commit()

    return existing

@router.get("/{org_id}", response_model=List[GrantMatchResult])
def get_organisation_matches(
    org_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(GrantMatch).filter(GrantMatch.organisation_id == org_id).all()
