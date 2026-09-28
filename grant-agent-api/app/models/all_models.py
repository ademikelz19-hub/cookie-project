import datetime
import uuid
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, Enum as SQLEnum, JSON, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import (
    VerificationStatus, GrantStageClassification, GrantApplicationStatus,
    GrantVerificationStatus, EligibilityMatchStatus, ApplicationStatus,
    DocumentCategory, DocumentApprovalStatus, BrowserSessionStatus,
    InterventionType, UserRole, AITaskStatus
)

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Null if Firebase Google login
    firebase_uid = Column(String(128), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    organisations = relationship("Organisation", back_populates="owner", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic Details
    organisation_name = Column(String(255), nullable=False, index=True)
    project_name = Column(String(255), nullable=True)
    organisation_type = Column(String(100), default="startup") # startup, nonprofit, social enterprise, personal project, research, Web3
    registration_status = Column(String(100), default="unregistered") # incorporated, registered charity, pending, unregistered
    registration_number = Column(String(100), nullable=True)
    registration_country = Column(String(100), nullable=True)
    date_founded = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    operating_countries = Column(JSON, default=list) # e.g. ["Nigeria", "Kenya", "Global"]
    basic_details_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    # Organisation Description
    short_description = Column(Text, nullable=True)
    long_description = Column(Text, nullable=True)
    mission = Column(Text, nullable=True)
    vision = Column(Text, nullable=True)
    objectives = Column(Text, nullable=True)
    description_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    # Problem
    problems_addressed = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    geography = Column(Text, nullable=True)
    underserved_groups = Column(Text, nullable=True)
    problem_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    # Solution
    products = Column(Text, nullable=True)
    services = Column(Text, nullable=True)
    programmes = Column(Text, nullable=True)
    technology_solution = Column(Text, nullable=True)
    solution_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    # Stage
    stage = Column(String(100), default="idea") # idea, prototype, MVP, early users, launched, revenue, growth
    stage_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    # Traction
    users_count = Column(Integer, default=0)
    beneficiaries_count = Column(Integer, default=0)
    customers_count = Column(Integer, default=0)
    revenue_amount = Column(Float, default=0.0)
    pilots_description = Column(Text, nullable=True)
    partnerships_description = Column(Text, nullable=True)
    testimonials = Column(Text, nullable=True)
    impact_metrics = Column(JSON, default=dict)
    traction_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    # Funding
    previous_grants = Column(Text, nullable=True)
    investment = Column(Text, nullable=True)
    founder_funding = Column(Text, nullable=True)
    current_fundraising = Column(Text, nullable=True)
    funding_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    # Impact
    gender_representation = Column(Text, nullable=True)
    employment_created = Column(Integer, default=0)
    programme_outcomes = Column(Text, nullable=True)
    sdgs = Column(JSON, default=list) # e.g. ["SDG 1: No Poverty", "SDG 9: Innovation"]
    measurable_social_impact = Column(Text, nullable=True)
    impact_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    # Technology
    tech_stack = Column(JSON, default=list) # e.g. ["Python", "Solidity", "React"]
    platform = Column(String(255), nullable=True)
    intellectual_property = Column(Text, nullable=True)
    technical_capabilities = Column(Text, nullable=True)
    technology_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    # Financial Information
    annual_budget = Column(Float, default=0.0)
    annual_revenue = Column(Float, default=0.0)
    project_budgets = Column(Text, nullable=True)
    financial_history = Column(Text, nullable=True)
    financial_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    # Grant Preferences
    pref_min_amount = Column(Float, default=0.0)
    pref_max_amount = Column(Float, default=1000000.0)
    pref_countries = Column(JSON, default=list)
    pref_sectors = Column(JSON, default=list)
    pref_stages = Column(JSON, default=list)
    pref_funding_types = Column(JSON, default=list) # grant only, accelerator, competition, fellowship, investment, prize
    grant_preferences_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="organisations")
    founders = relationship("Founder", back_populates="organisation", cascade="all, delete-orphan")
    team_members = relationship("TeamMember", back_populates="organisation", cascade="all, delete-orphan")
    metrics = relationship("OrganisationMetric", back_populates="organisation", cascade="all, delete-orphan")
    projects = relationship("OrganisationProject", back_populates="organisation", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="organisation", cascade="all, delete-orphan")
    matches = relationship("GrantMatch", back_populates="organisation", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="organisation", cascade="all, delete-orphan")


class Founder(Base):
    __tablename__ = "founders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(100), default="Co-Founder")
    biography = Column(Text, nullable=True)
    age = Column(Integer, nullable=True)
    education = Column(Text, nullable=True)
    relevant_experience = Column(Text, nullable=True)
    verification_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    organisation = relationship("Organisation", back_populates="founders")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(100), default="Core Member")
    biography = Column(Text, nullable=True)
    skills = Column(JSON, default=list)
    verification_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    organisation = relationship("Organisation", back_populates="team_members")


class OrganisationMetric(Base):
    __tablename__ = "organisation_metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    metric_name = Column(String(150), nullable=False)
    metric_value = Column(String(150), nullable=False)
    category = Column(String(100), default="traction") # traction, impact, financial
    evidence_reference = Column(String(255), nullable=True)
    verification_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    organisation = relationship("Organisation", back_populates="metrics")


class OrganisationProject(Base):
    __tablename__ = "organisation_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    objectives = Column(Text, nullable=True)
    budget = Column(Float, default=0.0)
    stage = Column(String(100), default="idea")
    verification_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.UNVERIFIED)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    organisation = relationship("Organisation", back_populates="projects")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    mime_type = Column(String(100), default="application/pdf")
    category = Column(SQLEnum(DocumentCategory), default=DocumentCategory.ORGANISATION_PROFILE)
    description = Column(Text, nullable=True)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    expiration_date = Column(DateTime, nullable=True)
    approval_status = Column(SQLEnum(DocumentApprovalStatus), default=DocumentApprovalStatus.PENDING_REVIEW, nullable=False)
    extracted_metadata = Column(JSON, default=dict)
    extracted_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    organisation = relationship("Organisation", back_populates="documents")
    application_documents = relationship("ApplicationDocument", back_populates="document")


class Grant(Base):
    __tablename__ = "grants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    grant_name = Column(String(255), nullable=False, index=True)
    funder = Column(String(255), nullable=False, index=True)
    official_url = Column(String(500), nullable=False)
    application_url = Column(String(500), nullable=True)
    source_url = Column(String(500), nullable=True)

    funding_amount_min = Column(Float, default=0.0)
    funding_amount_max = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")

    deadline = Column(String(100), nullable=True) # ISO string or descriptive
    opening_date = Column(String(100), nullable=True)
    country = Column(String(100), default="Global")
    eligible_countries = Column(JSON, default=list) # e.g. ["Nigeria", "Global"]
    eligible_regions = Column(JSON, default=list) # e.g. ["Africa", "Sub-Saharan"]
    sector = Column(String(100), default="Technology")
    grant_type = Column(String(100), default="grant") # grant, accelerator, competition, fellowship, investment, prize
    organisation_types = Column(JSON, default=list) # startup, nonprofit, etc.

    # Stage requirement & classification
    project_stage = Column(String(100), default="idea")
    stage_classification = Column(SQLEnum(GrantStageClassification), default=GrantStageClassification.GREEN_IDEA, nullable=False)
    
    incorporation_required = Column(Boolean, default=False)
    mvp_required = Column(Boolean, default=False)
    traction_required = Column(Boolean, default=False)
    revenue_required = Column(Boolean, default=False)
    previous_funding_required = Column(Boolean, default=False)
    age_requirement = Column(String(100), default="UNCONFIRMED")
    team_requirement = Column(String(100), default="UNCONFIRMED")

    application_language = Column(String(50), default="English")
    application_status = Column(SQLEnum(GrantApplicationStatus), default=GrantApplicationStatus.OPEN)
    application_process = Column(Text, nullable=True)
    required_documents = Column(JSON, default=list)
    required_questions = Column(JSON, default=list)
    selection_criteria = Column(Text, nullable=True)
    response_timeline = Column(String(100), default="UNCONFIRMED")
    reapplication_allowed = Column(Boolean, default=True)
    matching_funds_required = Column(Boolean, default=False)
    equity_required = Column(Boolean, default=False)

    website_last_checked = Column(DateTime, default=datetime.datetime.utcnow)
    verification_status = Column(SQLEnum(GrantVerificationStatus), default=GrantVerificationStatus.OFFICIAL_VERIFIED)
    verification_confidence = Column(Float, default=1.0)
    verified_extracted_text = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    sources = relationship("GrantSource", back_populates="grant", cascade="all, delete-orphan")
    requirements = relationship("GrantRequirement", back_populates="grant", cascade="all, delete-orphan")
    questions = relationship("GrantQuestion", back_populates="grant", cascade="all, delete-orphan")
    matches = relationship("GrantMatch", back_populates="grant", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="grant", cascade="all, delete-orphan")


class GrantSource(Base):
    __tablename__ = "grant_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    grant_id = Column(String(36), ForeignKey("grants.id"), nullable=False, index=True)
    source_type = Column(String(50), default="official_website") # official_website, rss, search_api, user_submitted
    source_url = Column(String(500), nullable=False)
    discovered_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_official = Column(Boolean, default=True)

    grant = relationship("Grant", back_populates="sources")


class GrantRequirement(Base):
    __tablename__ = "grant_requirements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    grant_id = Column(String(36), ForeignKey("grants.id"), nullable=False, index=True)
    requirement_type = Column(String(100), default="eligibility") # eligibility, document, financial, geography, stage
    description = Column(Text, nullable=False)
    is_mandatory = Column(Boolean, default=True)
    unconfirmed = Column(Boolean, default=False)

    grant = relationship("Grant", back_populates="requirements")


class GrantQuestion(Base):
    __tablename__ = "grant_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    grant_id = Column(String(36), ForeignKey("grants.id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    character_limit = Column(Integer, nullable=True)
    word_limit = Column(Integer, nullable=True)
    is_required = Column(Boolean, default=True)
    guidance = Column(Text, nullable=True)

    grant = relationship("Grant", back_populates="questions")


class GrantMatch(Base):
    __tablename__ = "grant_matches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    grant_id = Column(String(36), ForeignKey("grants.id"), nullable=False, index=True)
    
    eligibility_status = Column(SQLEnum(EligibilityMatchStatus), default=EligibilityMatchStatus.LIKELY_ELIGIBLE)
    relevance_score = Column(Float, default=75.0) # 0-100 internal sorting score only, NOT probability
    
    strong_match_factors = Column(JSON, default=list)
    weak_match_factors = Column(JSON, default=list)
    missing_requirements = Column(JSON, default=list)
    disqualifying_requirements = Column(JSON, default=list)
    information_needed = Column(JSON, default=list)
    
    evaluated_at = Column(DateTime, default=datetime.datetime.utcnow)

    organisation = relationship("Organisation", back_populates="matches")
    grant = relationship("Grant", back_populates="matches")

    __table_args__ = (
        Index("idx_org_grant_match", "organisation_id", "grant_id", unique=True),
    )


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    grant_id = Column(String(36), ForeignKey("grants.id"), nullable=False, index=True)

    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PREPARING, nullable=False)
    completion_percentage = Column(Integer, default=0)

    # Strategy & Positioning
    project_title = Column(String(255), nullable=True)
    project_summary = Column(Text, nullable=True)
    problem_statement = Column(Text, nullable=True)
    proposed_solution = Column(Text, nullable=True)
    innovation_description = Column(Text, nullable=True)
    target_beneficiaries = Column(Text, nullable=True)
    activities_timeline = Column(JSON, default=list)
    expected_outputs = Column(Text, nullable=True)
    expected_outcomes = Column(Text, nullable=True)
    long_term_impact = Column(Text, nullable=True)
    monitoring_and_evaluation = Column(Text, nullable=True)
    sustainability_plan = Column(Text, nullable=True)
    risk_management = Column(JSON, default=list)
    gender_inclusion = Column(Text, nullable=True)
    sdg_alignment = Column(JSON, default=list)
    budget_breakdown = Column(JSON, default=dict)
    
    # Missing information requiring applicant review
    required_from_applicant = Column(JSON, default=list)
    potential_weaknesses = Column(JSON, default=list)
    recommended_improvements = Column(JSON, default=list)

    # Submission & Tracking details
    submission_date = Column(DateTime, nullable=True)
    application_reference = Column(String(100), nullable=True)
    confirmation_number = Column(String(100), nullable=True)
    confirmation_email = Column(String(255), nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    decision_date = Column(DateTime, nullable=True)
    awarded_amount = Column(Float, nullable=True)
    auto_submit_after_approval = Column(Boolean, default=False)
    human_approved = Column(Boolean, default=False)
    human_approved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    organisation = relationship("Organisation", back_populates="applications")
    grant = relationship("Grant", back_populates="applications")
    questions = relationship("ApplicationQuestion", back_populates="application", cascade="all, delete-orphan")
    documents = relationship("ApplicationDocument", back_populates="application", cascade="all, delete-orphan")
    browser_sessions = relationship("BrowserSession", back_populates="application", cascade="all, delete-orphan")
    submissions = relationship("ApplicationSubmission", back_populates="application", cascade="all, delete-orphan")


class ApplicationQuestion(Base):
    __tablename__ = "application_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False, index=True)
    
    question_text = Column(Text, nullable=False)
    character_limit = Column(Integer, nullable=True)
    word_limit = Column(Integer, nullable=True)
    is_required = Column(Boolean, default=True)
    field_identifier = Column(String(255), nullable=True) # HTML id/name/selector

    # Answers
    answer = relationship("ApplicationAnswer", uselist=False, back_populates="question", cascade="all, delete-orphan")
    application = relationship("Application", back_populates="questions")


class ApplicationAnswer(Base):
    __tablename__ = "application_answers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey("application_questions.id"), nullable=False, unique=True, index=True)
    
    answer_text = Column(Text, nullable=False)
    character_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    source_information_used = Column(JSON, default=list) # verified fields used
    verification_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.VERIFIED)
    approved_status = Column(Boolean, default=False)
    last_edited = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    question = relationship("ApplicationQuestion", back_populates="answer")


class ApplicationDocument(Base):
    __tablename__ = "application_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    
    is_uploaded = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, nullable=True)

    application = relationship("Application", back_populates="documents")
    document = relationship("Document", back_populates="application_documents")


class BrowserSession(Base):
    __tablename__ = "browser_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False, index=True)
    
    status = Column(SQLEnum(BrowserSessionStatus), default=BrowserSessionStatus.IDLE)
    current_url = Column(String(500), nullable=True)
    current_task = Column(String(255), default="Initializing")
    current_step = Column(String(255), default="Ready")
    latest_screenshot_path = Column(String(500), nullable=True)
    
    # Human Gate details
    intervention_required = Column(Boolean, default=False)
    intervention_type = Column(SQLEnum(InterventionType), default=InterventionType.NONE)
    intervention_message = Column(Text, nullable=True)

    completed_fields_count = Column(Integer, default=0)
    total_fields_detected = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    application = relationship("Application", back_populates="browser_sessions")
    events = relationship("BrowserEvent", back_populates="session", cascade="all, delete-orphan")


class BrowserEvent(Base):
    __tablename__ = "browser_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("browser_sessions.id"), nullable=False, index=True)
    
    event_type = Column(String(100), nullable=False) # visit, field_fill, upload, pause, error, human_gate
    description = Column(Text, nullable=False)
    screenshot_path = Column(String(500), nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("BrowserSession", back_populates="events")


class ApplicationSubmission(Base):
    __tablename__ = "application_submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False, index=True)
    
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    reference_code = Column(String(150), nullable=True)
    confirmation_screenshot = Column(String(500), nullable=True)
    raw_confirmation_text = Column(Text, nullable=True)
    human_approver = Column(String(255), nullable=False)

    application = relationship("Application", back_populates="submissions")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(100), default="grant_match") # grant_match, deadline, human_gate, submitted
    reference_link = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    schedule = Column(String(50), default="daily") # daily, every_3_days, weekly
    sectors = Column(JSON, default=list)
    stages = Column(JSON, default=list)
    min_amount = Column(Float, default=0.0)
    max_amount = Column(Float, default=1000000.0)
    countries = Column(JSON, default=list)
    no_mvp_only = Column(Boolean, default=False)
    idea_stage_only = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False) # grant_discovered, grant_analysed, answer_generated, etc.
    target_type = Column(String(50), nullable=True) # grant, organisation, application, browser
    target_id = Column(String(36), nullable=True)
    details = Column(JSON, default=dict) # strictly sanitized, never passwords/tokens
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")


class AIJob(Base):
    __tablename__ = "ai_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_type = Column(String(100), nullable=False, index=True) # scout_scrape, verify_grant, match_eligibility, generate_strategy, draft_answers, consistency_check
    grant_id = Column(String(36), ForeignKey("grants.id", ondelete="SET NULL"), nullable=True, index=True)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="SET NULL"), nullable=True, index=True)
    application_id = Column(String(36), ForeignKey("applications.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(SQLEnum(AITaskStatus), default=AITaskStatus.QUEUED, nullable=False, index=True)
    attempt_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    model_attempted = Column(String(100), nullable=True)
    last_error_category = Column(String(100), nullable=True) # TRANSIENT_503, TRANSIENT_429, PERMANENT_400, TIMEOUT, etc.
    last_error_message = Column(Text, nullable=True) # sanitized summary only
    result_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
