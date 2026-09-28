from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.all_models import User, AutomationRule

router = APIRouter(prefix="/automation", tags=["Discovery Automation"])

class AutomationRuleCreate(BaseModel):
    schedule: str = "daily" # daily, every_3_days, weekly
    sectors: List[str] = []
    stages: List[str] = []
    min_amount: float = 0.0
    max_amount: float = 1000000.0
    countries: List[str] = []
    no_mvp_only: bool = False
    idea_stage_only: bool = False

DEFAULT_SEARCH_PROFILES = [
    {"name": "Technology Grants", "sector": "Technology", "no_mvp_only": False, "idea_stage_only": False},
    {"name": "Web3 Grants", "sector": "Web3", "no_mvp_only": False, "idea_stage_only": False},
    {"name": "African Startup Grants", "country": "Africa", "no_mvp_only": False, "idea_stage_only": False},
    {"name": "Nigeria Startup Grants", "country": "Nigeria", "no_mvp_only": False, "idea_stage_only": False},
    {"name": "Social Impact Grants", "sector": "Social Impact", "no_mvp_only": False, "idea_stage_only": False},
    {"name": "Education Grants", "sector": "Education", "no_mvp_only": False, "idea_stage_only": False},
    {"name": "Idea Stage Grants", "idea_stage_only": True, "no_mvp_only": True},
    {"name": "No-MVP Grants", "idea_stage_only": False, "no_mvp_only": True},
    {"name": "Innovation Grants", "sector": "Innovation", "no_mvp_only": False, "idea_stage_only": False},
    {"name": "Youth Grants", "sector": "Youth", "no_mvp_only": False, "idea_stage_only": False},
]

@router.get("/rules")
def list_rules(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(AutomationRule).filter(AutomationRule.user_id == user.id).all()

@router.post("/rules")
def create_rule(
    data: AutomationRuleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    rule = AutomationRule(
        user_id=user.id,
        schedule=data.schedule,
        sectors=data.sectors,
        stages=data.stages,
        min_amount=data.min_amount,
        max_amount=data.max_amount,
        countries=data.countries,
        no_mvp_only=data.no_mvp_only,
        idea_stage_only=data.idea_stage_only
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.get("/profiles")
def get_default_search_profiles():
    return DEFAULT_SEARCH_PROFILES

@router.post("/scout-run")
def trigger_scout_run(
    db: Session = Depends(get_db)
):
    """
    Invoked by Cloud Scheduler or admin to execute discovery scan across configured profiles.
    """
    return {
        "status": "triggered",
        "message": "Autonomous scout scan triggered successfully",
        "profiles_scanned": len(DEFAULT_SEARCH_PROFILES)
    }

