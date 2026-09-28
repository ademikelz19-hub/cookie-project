from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from app.models.enums import VerificationStatus

class FounderBase(BaseModel):
    name: str
    role: str = "Co-Founder"
    biography: Optional[str] = None
    age: Optional[int] = None
    education: Optional[str] = None
    relevant_experience: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED

class FounderCreate(FounderBase):
    pass

class FounderResponse(FounderBase):
    id: str
    organisation_id: str

    class Config:
        from_attributes = True

class TeamMemberBase(BaseModel):
    name: str
    role: str = "Core Member"
    biography: Optional[str] = None
    skills: List[str] = []
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberResponse(TeamMemberBase):
    id: str
    organisation_id: str

    class Config:
        from_attributes = True

class OrganisationMetricBase(BaseModel):
    metric_name: str
    metric_value: str
    category: str = "traction"
    evidence_reference: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED

class OrganisationMetricCreate(OrganisationMetricBase):
    pass

class OrganisationMetricResponse(OrganisationMetricBase):
    id: str
    organisation_id: str

    class Config:
        from_attributes = True

class OrganisationBase(BaseModel):
    organisation_name: str
    project_name: Optional[str] = None
    organisation_type: str = "startup"
    registration_status: str = "unregistered"
    registration_number: Optional[str] = None
    registration_country: Optional[str] = None
    date_founded: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    operating_countries: List[str] = []
    basic_details_status: VerificationStatus = VerificationStatus.UNVERIFIED

    # Descriptions
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    objectives: Optional[str] = None
    description_status: VerificationStatus = VerificationStatus.UNVERIFIED

    # Problem
    problems_addressed: Optional[str] = None
    target_audience: Optional[str] = None
    geography: Optional[str] = None
    underserved_groups: Optional[str] = None
    problem_status: VerificationStatus = VerificationStatus.UNVERIFIED

    # Solution
    products: Optional[str] = None
    services: Optional[str] = None
    programmes: Optional[str] = None
    technology_solution: Optional[str] = None
    solution_status: VerificationStatus = VerificationStatus.UNVERIFIED

    # Stage
    stage: str = "idea"
    stage_status: VerificationStatus = VerificationStatus.UNVERIFIED

    # Traction
    users_count: int = 0
    beneficiaries_count: int = 0
    customers_count: int = 0
    revenue_amount: float = 0.0
    pilots_description: Optional[str] = None
    partnerships_description: Optional[str] = None
    testimonials: Optional[str] = None
    impact_metrics: Dict[str, Any] = {}
    traction_status: VerificationStatus = VerificationStatus.UNVERIFIED

    # Funding
    previous_grants: Optional[str] = None
    investment: Optional[str] = None
    founder_funding: Optional[str] = None
    current_fundraising: Optional[str] = None
    funding_status: VerificationStatus = VerificationStatus.UNVERIFIED

    # Impact
    gender_representation: Optional[str] = None
    employment_created: int = 0
    programme_outcomes: Optional[str] = None
    sdgs: List[str] = []
    measurable_social_impact: Optional[str] = None
    impact_status: VerificationStatus = VerificationStatus.UNVERIFIED

    # Technology
    tech_stack: List[str] = []
    platform: Optional[str] = None
    intellectual_property: Optional[str] = None
    technical_capabilities: Optional[str] = None
    technology_status: VerificationStatus = VerificationStatus.UNVERIFIED

    # Financial Information
    annual_budget: float = 0.0
    annual_revenue: float = 0.0
    project_budgets: Optional[str] = None
    financial_history: Optional[str] = None
    financial_status: VerificationStatus = VerificationStatus.UNVERIFIED

    # Grant Preferences
    pref_min_amount: float = 0.0
    pref_max_amount: float = 1000000.0
    pref_countries: List[str] = []
    pref_sectors: List[str] = []
    pref_stages: List[str] = []
    pref_funding_types: List[str] = []
    grant_preferences_status: VerificationStatus = VerificationStatus.UNVERIFIED

class OrganisationCreate(OrganisationBase):
    pass

class OrganisationUpdate(BaseModel):
    organisation_name: Optional[str] = None
    project_name: Optional[str] = None
    organisation_type: Optional[str] = None
    registration_status: Optional[str] = None
    registration_number: Optional[str] = None
    registration_country: Optional[str] = None
    date_founded: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    operating_countries: Optional[List[str]] = None
    basic_details_status: Optional[VerificationStatus] = None

    short_description: Optional[str] = None
    long_description: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    objectives: Optional[str] = None
    description_status: Optional[VerificationStatus] = None

    problems_addressed: Optional[str] = None
    target_audience: Optional[str] = None
    geography: Optional[str] = None
    underserved_groups: Optional[str] = None
    problem_status: Optional[VerificationStatus] = None

    products: Optional[str] = None
    services: Optional[str] = None
    programmes: Optional[str] = None
    technology_solution: Optional[str] = None
    solution_status: Optional[VerificationStatus] = None

    stage: Optional[str] = None
    stage_status: Optional[VerificationStatus] = None

    users_count: Optional[int] = None
    beneficiaries_count: Optional[int] = None
    customers_count: Optional[int] = None
    revenue_amount: Optional[float] = None
    pilots_description: Optional[str] = None
    partnerships_description: Optional[str] = None
    testimonials: Optional[str] = None
    impact_metrics: Optional[Dict[str, Any]] = None
    traction_status: Optional[VerificationStatus] = None

    previous_grants: Optional[str] = None
    investment: Optional[str] = None
    founder_funding: Optional[str] = None
    current_fundraising: Optional[str] = None
    funding_status: Optional[VerificationStatus] = None

    gender_representation: Optional[str] = None
    employment_created: Optional[int] = None
    programme_outcomes: Optional[str] = None
    sdgs: Optional[List[str]] = None
    measurable_social_impact: Optional[str] = None
    impact_status: Optional[VerificationStatus] = None

    tech_stack: Optional[List[str]] = None
    platform: Optional[str] = None
    intellectual_property: Optional[str] = None
    technical_capabilities: Optional[str] = None
    technology_status: Optional[VerificationStatus] = None

    annual_budget: Optional[float] = None
    annual_revenue: Optional[float] = None
    project_budgets: Optional[str] = None
    financial_history: Optional[str] = None
    financial_status: Optional[VerificationStatus] = None

    pref_min_amount: Optional[float] = None
    pref_max_amount: Optional[float] = None
    pref_countries: Optional[List[str]] = None
    pref_sectors: Optional[List[str]] = None
    pref_stages: Optional[List[str]] = None
    pref_funding_types: Optional[List[str]] = None
    grant_preferences_status: Optional[VerificationStatus] = None

class SectionVerificationUpdate(BaseModel):
    section_name: str # e.g. "basic_details", "description", "problem", "solution", "stage", "traction", "funding", "impact", "technology", "financial", "grant_preferences"
    status: VerificationStatus

class OrganisationResponse(OrganisationBase):
    id: str
    owner_id: str
    founders: List[FounderResponse] = []
    team_members: List[TeamMemberResponse] = []
    metrics: List[OrganisationMetricResponse] = []

    class Config:
        from_attributes = True
