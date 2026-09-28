import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.models.enums import ApplicationStatus, VerificationStatus

class AnswerUpdate(BaseModel):
    answer_text: str
    approved_status: Optional[bool] = None

class ApplicationAnswerResponse(BaseModel):
    id: str
    question_id: str
    answer_text: str
    character_count: int
    word_count: int
    source_information_used: List[str] = []
    verification_status: VerificationStatus
    approved_status: bool
    last_edited: datetime.datetime

    class Config:
        from_attributes = True

class ApplicationQuestionResponse(BaseModel):
    id: str
    application_id: str
    question_text: str
    character_limit: Optional[int] = None
    word_limit: Optional[int] = None
    is_required: bool
    field_identifier: Optional[str] = None
    answer: Optional[ApplicationAnswerResponse] = None

    class Config:
        from_attributes = True

class ApplicationStrategyResponse(BaseModel):
    eligibility_assessment: str
    recommended_project: str
    project_title: str
    project_summary: str
    problem_statement: str
    proposed_solution: str
    innovation_description: str
    target_beneficiaries: str
    activities_timeline: List[Dict[str, Any]] = []
    expected_outputs: str
    expected_outcomes: str
    long_term_impact: str
    monitoring_and_evaluation: str
    sustainability_plan: str
    risk_management: List[Dict[str, Any]] = []
    gender_inclusion: str
    sdg_alignment: List[str] = []
    budget_breakdown: Dict[str, Any] = {}
    existing_evidence_to_use: List[str] = []
    required_documents: List[str] = []
    required_from_applicant: List[str] = [] # Missing info strictly flagged
    potential_weaknesses: List[str] = []
    recommended_improvements: List[str] = []

class ApplicationReviewSummary(BaseModel):
    application_id: str
    grant_name: str
    organisation_name: str
    deadline: Optional[str] = None
    completion_percentage: int
    questions_total: int
    questions_completed: int
    questions_missing: int
    documents_total_required: int
    documents_uploaded: int
    documents_missing: int
    declarations_pending: List[str] = []
    warnings: List[str] = []
    potential_errors: List[str] = []
    word_limit_violations: List[str] = []
    character_limit_violations: List[str] = []
    eligibility_warnings: List[str] = []
    ready_for_final_approval: bool

class HumanApprovalRequest(BaseModel):
    approved: bool
    notes: Optional[str] = None
    allow_auto_submit: bool = True

class ApplicationResponse(BaseModel):
    id: str
    organisation_id: str
    grant_id: str
    status: ApplicationStatus
    completion_percentage: int
    project_title: Optional[str] = None
    project_summary: Optional[str] = None
    submission_date: Optional[datetime.datetime] = None
    application_reference: Optional[str] = None
    confirmation_number: Optional[str] = None
    human_approved: bool
    auto_submit_after_approval: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    questions: List[ApplicationQuestionResponse] = []

    class Config:
        from_attributes = True
