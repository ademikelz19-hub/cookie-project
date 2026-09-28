from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.all_models import (
    User, Organisation, Founder, TeamMember, OrganisationMetric, AuditLog
)
from app.models.enums import VerificationStatus
from app.schemas.organisation import (
    OrganisationCreate, OrganisationUpdate, OrganisationResponse,
    FounderCreate, FounderResponse, TeamMemberCreate, TeamMemberResponse,
    OrganisationMetricCreate, OrganisationMetricResponse, SectionVerificationUpdate
)

router = APIRouter(prefix="/organisations", tags=["Organisations"])

@router.get("", response_model=List[OrganisationResponse])
def list_organisations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(Organisation).filter(Organisation.owner_id == user.id).all()

@router.post("", response_model=OrganisationResponse)
def create_organisation(
    data: OrganisationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    org = Organisation(
        owner_id=user.id,
        **data.model_dump()
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    # Log audit
    audit = AuditLog(
        user_id=user.id,
        action="organisation_created",
        target_type="organisation",
        target_id=org.id,
        details={"name": org.organisation_name}
    )
    db.add(audit)
    db.commit()

    return org

@router.get("/{org_id}", response_model=OrganisationResponse)
def get_organisation(
    org_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    org = db.query(Organisation).filter(Organisation.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return org

@router.put("/{org_id}", response_model=OrganisationResponse)
def update_organisation(
    org_id: str,
    data: OrganisationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    org = db.query(Organisation).filter(Organisation.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(org, field, val)

    db.commit()
    db.refresh(org)

    audit = AuditLog(
        user_id=user.id,
        action="organisation_updated",
        target_type="organisation",
        target_id=org.id,
        details={"updated_fields": list(update_dict.keys())}
    )
    db.add(audit)
    db.commit()

    return org

@router.post("/{org_id}/verification", response_model=OrganisationResponse)
def update_section_verification(
    org_id: str,
    data: SectionVerificationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    org = db.query(Organisation).filter(Organisation.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    attr_map = {
        "basic_details": "basic_details_status",
        "description": "description_status",
        "problem": "problem_status",
        "solution": "solution_status",
        "stage": "stage_status",
        "traction": "traction_status",
        "funding": "funding_status",
        "impact": "impact_status",
        "technology": "technology_status",
        "financial": "financial_status",
        "grant_preferences": "grant_preferences_status"
    }

    field_name = attr_map.get(data.section_name.lower())
    if not field_name:
        raise HTTPException(status_code=400, detail=f"Invalid section name '{data.section_name}'")

    setattr(org, field_name, data.status)
    db.commit()
    db.refresh(org)

    audit = AuditLog(
        user_id=user.id,
        action="section_verification_updated",
        target_type="organisation",
        target_id=org.id,
        details={"section": data.section_name, "status": data.status.value}
    )
    db.add(audit)
    db.commit()

    return org

@router.post("/{org_id}/founders", response_model=FounderResponse)
def add_founder(
    org_id: str,
    data: FounderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    org = db.query(Organisation).filter(Organisation.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    founder = Founder(
        organisation_id=org_id,
        **data.model_dump()
    )
    db.add(founder)
    db.commit()
    db.refresh(founder)
    return founder

@router.post("/{org_id}/team", response_model=TeamMemberResponse)
def add_team_member(
    org_id: str,
    data: TeamMemberCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    org = db.query(Organisation).filter(Organisation.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    member = TeamMember(
        organisation_id=org_id,
        **data.model_dump()
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

@router.post("/{org_id}/metrics", response_model=OrganisationMetricResponse)
def add_metric(
    org_id: str,
    data: OrganisationMetricCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    org = db.query(Organisation).filter(Organisation.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    metric = OrganisationMetric(
        organisation_id=org_id,
        **data.model_dump()
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric
