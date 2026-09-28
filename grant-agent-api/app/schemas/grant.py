import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, HttpUrl
from app.models.enums import (
    GrantStageClassification, GrantApplicationStatus,
    GrantVerificationStatus, EligibilityMatchStatus
)

class GrantQuestionSchema(BaseModel):
    id: Optional[str] = None
    question_text: str
    character_limit: Optional[int] = None
    word_limit: Optional[int] = None
    is_required: bool = True
    guidance: Optional[str] = None

class GrantRequirementSchema(BaseModel):
    id: Optional[str] = None
    requirement_type: str = "eligibility"
    description: str
    is_mandatory: bool = True
    unconfirmed: bool = False

class GrantBase(BaseModel):
    grant_name: str
    funder: str
    official_url: str
    application_url: Optional[str] = None
    source_url: Optional[str] = None

    funding_amount_min: float = 0.0
    funding_amount_max: float = 0.0
    currency: str = "USD"

    deadline: Optional[str] = None
    opening_date: Optional[str] = None
    country: str = "Global"
    eligible_countries: List[str] = []
    eligible_regions: List[str] = []
    sector: str = "Technology"
    grant_type: str = "grant"
    organisation_types: List[str] = []

    project_stage: str = "idea"
    stage_classification: GrantStageClassification = GrantStageClassification.GREEN_IDEA

    incorporation_required: bool = False
    mvp_required: bool = False
    traction_required: bool = False
    revenue_required: bool = False
    previous_funding_required: bool = False
    age_requirement: str = "UNCONFIRMED"
    team_requirement: str = "UNCONFIRMED"

    application_language: str = "English"
    application_status: GrantApplicationStatus = GrantApplicationStatus.OPEN
    application_process: Optional[str] = None
    required_documents: List[str] = []
    required_questions: List[str] = []
    selection_criteria: Optional[str] = None
    response_timeline: str = "UNCONFIRMED"
    reapplication_allowed: bool = True
    matching_funds_required: bool = False
    equity_required: bool = False

    verification_status: GrantVerificationStatus = GrantVerificationStatus.OFFICIAL_VERIFIED
    verification_confidence: float = 1.0
    verified_extracted_text: Optional[str] = None

class GrantCreate(GrantBase):
    pass

class GrantResponse(GrantBase):
    id: str
    website_last_checked: datetime.datetime
    created_at: datetime.datetime
    requirements: List[GrantRequirementSchema] = []
    questions: List[GrantQuestionSchema] = []

    class Config:
        from_attributes = True

class PasteGrantUrlRequest(BaseModel):
    url: str
    organisation_id: Optional[str] = None
    exact_url_mode: bool = False

class GrantFilterParams(BaseModel):
    sector: Optional[str] = None
    country: Optional[str] = None
    no_mvp_only: bool = False
    idea_stage_only: bool = False
    stage_classification: Optional[GrantStageClassification] = None
    min_amount: Optional[float] = None
    search_query: Optional[str] = None

class GrantMatchResult(BaseModel):
    grant_id: str
    organisation_id: str
    eligibility_status: EligibilityMatchStatus
    relevance_score: float  # 0-100 internal score, NOT a probability
    strong_match_factors: List[str] = []
    weak_match_factors: List[str] = []
    missing_requirements: List[str] = []
    disqualifying_requirements: List[str] = []
    information_needed: List[str] = []

    class Config:
        from_attributes = True
