import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.all_models import (
    User, Grant, GrantSource, GrantRequirement, GrantQuestion, AuditLog
)
from app.models.enums import (
    GrantStageClassification, GrantApplicationStatus, GrantVerificationStatus
)
from app.schemas.grant import (
    GrantResponse, GrantCreate, PasteGrantUrlRequest, GrantFilterParams
)
from app.agents.scout import grant_scout
from app.agents.verifier import grant_verifier

router = APIRouter(prefix="/grants", tags=["Grants"])

@router.get("", response_model=List[GrantResponse])
def list_grants(
    sector: Optional[str] = None,
    country: Optional[str] = None,
    no_mvp_only: bool = Query(False),
    idea_stage_only: bool = Query(False),
    stage_classification: Optional[str] = None,
    min_amount: Optional[float] = None,
    search_query: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(Grant)

    if idea_stage_only:
        query = query.filter(Grant.stage_classification == GrantStageClassification.GREEN_IDEA)
    elif no_mvp_only:
        query = query.filter(Grant.stage_classification.in_([
            GrantStageClassification.GREEN_IDEA,
            GrantStageClassification.YELLOW_VALIDATION
        ]))

    if stage_classification:
        query = query.filter(Grant.stage_classification == stage_classification)
    if sector and sector != "All":
        query = query.filter(Grant.sector.ilike(f"%{sector}%"))
    if min_amount:
        query = query.filter(Grant.funding_amount_max >= min_amount)
    if search_query:
        query = query.filter(
            (Grant.grant_name.ilike(f"%{search_query}%")) |
            (Grant.funder.ilike(f"%{search_query}%")) |
            (Grant.sector.ilike(f"%{search_query}%"))
        )

    return query.order_by(Grant.created_at.desc()).all()

@router.get("/{grant_id}", response_model=GrantResponse)
def get_grant(
    grant_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    grant = db.query(Grant).filter(Grant.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return grant

@router.post("/paste-url", response_model=GrantResponse)
async def paste_grant_url(
    req: PasteGrantUrlRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # 1. Fetch & extract using Grant Scout Agent
    extracted = await grant_scout.scrape_and_extract(req.url, exact_url_mode=req.exact_url_mode)
    
    # 2. Verify with Grant Verification Agent
    verified_data = await grant_verifier.verify_grant(extracted)

    grant = Grant(
        grant_name=extracted["grant_name"],
        funder=extracted["funder"],
        official_url=extracted["official_url"],
        application_url=extracted["application_url"],
        source_url=extracted["source_url"],
        funding_amount_min=extracted["funding_amount_min"],
        funding_amount_max=extracted["funding_amount_max"],
        currency=extracted["currency"],
        deadline=verified_data.get("deadline", extracted["deadline"]),
        country=extracted["country"],
        eligible_countries=extracted["eligible_countries"],
        eligible_regions=extracted["eligible_regions"],
        sector=extracted["sector"],
        grant_type=extracted["grant_type"],
        project_stage=extracted["project_stage"],
        stage_classification=extracted["stage_classification"],
        incorporation_required=extracted["incorporation_required"],
        mvp_required=extracted["mvp_required"],
        traction_required=extracted["traction_required"],
        revenue_required=extracted["revenue_required"],
        application_language=extracted["application_language"],
        application_status=verified_data.get("application_status", extracted["application_status"]),
        application_process=extracted["application_process"],
        required_documents=extracted["required_documents"],
        required_questions=extracted["required_questions"],
        selection_criteria=extracted["selection_criteria"],
        verification_status=verified_data.get("verification_status", GrantVerificationStatus.OFFICIAL_VERIFIED),
        verification_confidence=verified_data.get("verification_confidence", 0.90),
        verified_extracted_text=extracted["verified_extracted_text"]
    )
    db.add(grant)
    db.commit()
    db.refresh(grant)

    # Add source
    source = GrantSource(
        grant_id=grant.id,
        source_type="user_submitted",
        source_url=req.url,
        is_official=True
    )
    db.add(source)

    # Add default requirements
    reqs = [
        GrantRequirement(grant_id=grant.id, requirement_type="stage", description=f"Stage Requirement: {grant.stage_classification.value}"),
        GrantRequirement(grant_id=grant.id, requirement_type="geography", description=f"Eligible Geographies: {', '.join(grant.eligible_countries)}")
    ]
    for r in reqs:
        db.add(r)

    # Add questions
    for q_text in extracted["required_questions"]:
        db.add(GrantQuestion(grant_id=grant.id, question_text=q_text, character_limit=2000, word_limit=300))

    db.commit()
    db.refresh(grant)

    audit = AuditLog(
        user_id=user.id,
        action="grant_discovered",
        target_type="grant",
        target_id=grant.id,
        details={"grant_name": grant.grant_name, "url": req.url, "stage": grant.stage_classification.value}
    )
    db.add(audit)
    db.commit()

    return grant

@router.post("/{grant_id}/verify", response_model=GrantResponse)
async def verify_grant(
    grant_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    grant = db.query(Grant).filter(Grant.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")

    verified_info = await grant_verifier.verify_grant({
        "official_url": grant.official_url,
        "source_url": grant.source_url,
        "verified_extracted_text": grant.verified_extracted_text or "",
        "deadline": grant.deadline,
        "application_status": grant.application_status
    })

    grant.verification_status = verified_info["verification_status"]
    grant.verification_confidence = verified_info["verification_confidence"]
    grant.application_status = verified_info["application_status"]
    grant.website_last_checked = verified_info["website_last_checked"]

    db.commit()
    db.refresh(grant)

    audit = AuditLog(
        user_id=user.id,
        action="grant_verified",
        target_type="grant",
        target_id=grant.id,
        details={"status": grant.verification_status.value, "confidence": grant.verification_confidence}
    )
    db.add(audit)
    db.commit()

    return grant
