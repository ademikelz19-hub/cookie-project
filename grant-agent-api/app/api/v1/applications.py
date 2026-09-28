import datetime
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.all_models import (
    User, Organisation, Grant, Application, ApplicationQuestion,
    ApplicationAnswer, Document, ApplicationDocument, ApplicationSubmission,
    AuditLog, Notification
)
from app.models.enums import (
    ApplicationStatus, DocumentApprovalStatus, VerificationStatus
)
from app.schemas.application import (
    ApplicationResponse, ApplicationReviewSummary, AnswerUpdate,
    HumanApprovalRequest, ApplicationStrategyResponse
)
from app.agents.strategist import application_strategist
from app.agents.writer import application_writer
from app.agents.validator import application_validator

router = APIRouter(prefix="/applications", tags=["Applications"])

class PrepareApplicationRequest(BaseModel):
    organisation_id: Optional[str] = None
    org_id: Optional[str] = None
    grant_id: str

    @property
    def target_org_id(self) -> str:
        return self.organisation_id or self.org_id or ""

class UpdateApplicationStatusRequest(BaseModel):
    status: ApplicationStatus
    notes: Optional[str] = None
    awarded_amount: Optional[float] = None

@router.get("", response_model=List[ApplicationResponse])
def list_applications(
    status_filter: Optional[ApplicationStatus] = None,
    organisation_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(Application)
    if status_filter:
        query = query.filter(Application.status == status_filter)
    if organisation_id:
        query = query.filter(Application.organisation_id == organisation_id)
    return query.order_by(Application.created_at.desc()).all()

@router.post("", response_model=ApplicationResponse)
@router.post("/prepare", response_model=ApplicationResponse)
def prepare_application(
    req: PrepareApplicationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    target_id = req.target_org_id
    if not target_id:
        raise HTTPException(status_code=400, detail="organisation_id or org_id is required")

    org = db.query(Organisation).filter(Organisation.id == target_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    grant = db.query(Grant).filter(Grant.id == req.grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")

    # Fetch approved documents
    approved_docs = db.query(Document).filter(
        Document.organisation_id == org.id,
        Document.approval_status == DocumentApprovalStatus.APPROVED_FOR_APPLICATION_USE
    ).all()

    # 1. Run Strategist Agent
    strat = application_strategist.generate_strategy(org, grant, approved_docs)

    # 2. Create Application record
    app_record = Application(
        organisation_id=org.id,
        grant_id=grant.id,
        status=ApplicationStatus.PREPARING,
        completion_percentage=60,
        project_title=strat["project_title"],
        project_summary=strat["project_summary"],
        problem_statement=strat["problem_statement"],
        proposed_solution=strat["proposed_solution"],
        innovation_description=strat["innovation_description"],
        target_beneficiaries=strat["target_beneficiaries"],
        activities_timeline=strat["activities_timeline"],
        expected_outputs=strat["expected_outputs"],
        expected_outcomes=strat["expected_outcomes"],
        long_term_impact=strat["long_term_impact"],
        monitoring_and_evaluation=strat["monitoring_and_evaluation"],
        sustainability_plan=strat["sustainability_plan"],
        risk_management=strat["risk_management"],
        gender_inclusion=strat["gender_inclusion"],
        sdg_alignment=strat["sdg_alignment"],
        budget_breakdown=strat["budget_breakdown"],
        required_from_applicant=strat["required_from_applicant"],
        potential_weaknesses=strat["potential_weaknesses"],
        recommended_improvements=strat["recommended_improvements"]
    )
    db.add(app_record)
    db.commit()
    db.refresh(app_record)

    # 3. Associate approved documents
    for doc in approved_docs:
        db.add(ApplicationDocument(application_id=app_record.id, document_id=doc.id))

    # 4. Generate Application Questions & Answers with Writer Agent
    grant_questions = grant.questions or []
    if not grant_questions and grant.required_questions:
        # Create questions if not already linked
        for q_text in grant.required_questions:
            gq = ApplicationQuestion(
                application_id=app_record.id,
                question_text=q_text,
                character_limit=2000,
                word_limit=300,
                is_required=True
            )
            db.add(gq)
            db.commit()
            db.refresh(gq)

            draft = application_writer.draft_answer(q_text, org, strat, max_words=300, max_chars=2000)
            ans = ApplicationAnswer(
                question_id=gq.id,
                answer_text=draft["answer"],
                character_count=draft["character_count"],
                word_count=draft["word_count"],
                source_information_used=draft["source_information_used"],
                verification_status=draft["verification_status"],
                approved_status=False
            )
            db.add(ans)
    else:
        for gq in grant_questions:
            app_q = ApplicationQuestion(
                application_id=app_record.id,
                question_text=gq.question_text,
                character_limit=gq.character_limit,
                word_limit=gq.word_limit,
                is_required=gq.is_required
            )
            db.add(app_q)
            db.commit()
            db.refresh(app_q)

            draft = application_writer.draft_answer(
                gq.question_text, org, strat,
                max_words=gq.word_limit or 300,
                max_chars=gq.character_limit or 2000
            )
            ans = ApplicationAnswer(
                question_id=app_q.id,
                answer_text=draft["answer"],
                character_count=draft["character_count"],
                word_count=draft["word_count"],
                source_information_used=draft["source_information_used"],
                verification_status=draft["verification_status"],
                approved_status=False
            )
            db.add(ans)

    app_record.status = ApplicationStatus.READY_TO_APPLY
    db.commit()
    db.refresh(app_record)

    audit = AuditLog(
        user_id=user.id,
        action="application_prepared",
        target_type="application",
        target_id=app_record.id,
        details={"project_title": app_record.project_title, "grant_name": grant.grant_name}
    )
    db.add(audit)
    db.commit()

    return app_record

@router.get("/{app_id}", response_model=ApplicationResponse)
def get_application(
    app_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.put("/{app_id}/answers/{question_id}")
def update_answer(
    app_id: str,
    question_id: str,
    data: AnswerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    ans = db.query(ApplicationAnswer).filter(ApplicationAnswer.question_id == question_id).first()
    if not ans:
        ans = ApplicationAnswer(
            question_id=question_id,
            answer_text=data.answer_text,
            character_count=len(data.answer_text),
            word_count=len(data.answer_text.split()),
            verification_status=VerificationStatus.VERIFIED,
            approved_status=data.approved_status if data.approved_status is not None else False
        )
        db.add(ans)
    else:
        ans.answer_text = data.answer_text
        ans.character_count = len(data.answer_text)
        ans.word_count = len(data.answer_text.split())
        if data.approved_status is not None:
            ans.approved_status = data.approved_status
        ans.last_edited = datetime.datetime.utcnow()

    db.commit()
    db.refresh(ans)

    audit = AuditLog(
        user_id=user.id,
        action="answer_edited",
        target_type="application_answer",
        target_id=ans.id,
        details={"word_count": ans.word_count, "approved": ans.approved_status}
    )
    db.add(audit)
    db.commit()

    return ans

@router.get("/{app_id}/review", response_model=ApplicationReviewSummary)
def review_application(
    app_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    org = app.organisation
    grant = app.grant

    # Extract answers
    answers_data = []
    for q in app.questions:
        ans_text = q.answer.answer_text if q.answer else ""
        answers_data.append({
            "question_text": q.question_text,
            "answer_text": ans_text,
            "word_limit": q.word_limit,
            "character_limit": q.character_limit
        })

    # Fetch attached approved docs
    attached_docs = [ad.document for ad in app.documents]

    # Run Consistency Checker
    val_result = application_validator.validate_application(app, org, grant, answers_data, attached_docs)

    total_q = len(app.questions)
    completed_q = len([q for q in app.questions if q.answer and q.answer.answer_text and "[REQUIRED FROM APPLICANT]" not in q.answer.answer_text])
    missing_q = total_q - completed_q

    total_req_docs = len(grant.required_documents or [])
    approved_doc_cats = {d.category.value for d in attached_docs if d.approval_status == DocumentApprovalStatus.APPROVED_FOR_APPLICATION_USE}
    uploaded_docs = len([rd for rd in (grant.required_documents or []) if rd in approved_doc_cats])
    missing_docs = total_req_docs - uploaded_docs

    calc_percent = int((completed_q / max(1, total_q) * 60) + (uploaded_docs / max(1, total_req_docs) * 40))
    app.completion_percentage = min(100, max(0, calc_percent))
    if app.completion_percentage >= 95 and not app.human_approved:
        app.status = ApplicationStatus.READY_FOR_REVIEW
    db.commit()

    return ApplicationReviewSummary(
        application_id=app.id,
        grant_name=grant.grant_name,
        organisation_name=org.organisation_name,
        deadline=grant.deadline,
        completion_percentage=app.completion_percentage,
        questions_total=total_q,
        questions_completed=completed_q,
        questions_missing=missing_q,
        documents_total_required=total_req_docs,
        documents_uploaded=uploaded_docs,
        documents_missing=missing_docs,
        declarations_pending=val_result["declarations_pending"],
        warnings=val_result["warnings"],
        potential_errors=val_result["potential_errors"],
        word_limit_violations=val_result["word_limit_violations"],
        character_limit_violations=val_result["character_limit_violations"],
        eligibility_warnings=val_result["eligibility_warnings"],
        ready_for_final_approval=val_result["ready_for_final_approval"] and missing_q == 0 and missing_docs == 0
    )

@router.post("/{app_id}/approve", response_model=ApplicationResponse)
def approve_application(
    app_id: str,
    req: HumanApprovalRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.human_approved = req.approved
    app.human_approved_at = datetime.datetime.utcnow() if req.approved else None
    app.auto_submit_after_approval = req.allow_auto_submit
    app.status = ApplicationStatus.READY_TO_APPLY if req.approved else ApplicationStatus.PREPARING

    db.commit()
    db.refresh(app)

    audit = AuditLog(
        user_id=user.id,
        action="application_reviewed",
        target_type="application",
        target_id=app.id,
        details={"approved": req.approved, "auto_submit": req.allow_auto_submit}
    )
    db.add(audit)
    db.commit()

    return app

@router.post("/{app_id}/submit", response_model=ApplicationResponse)
def submit_application(
    app_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if not app.human_approved:
        raise HTTPException(
            status_code=400,
            detail="Mandatory Human Approval Gate: Application must be explicitly reviewed and approved by user before final submission."
        )

    ref_code = f"GA-{uuid.uuid4().hex[:8].upper()}"
    app.status = ApplicationStatus.SUBMITTED
    app.submission_date = datetime.datetime.utcnow()
    app.application_reference = ref_code
    app.confirmation_number = f"CONF-{uuid.uuid4().hex[:6].upper()}"
    app.confirmation_email = user.email
    app.completion_percentage = 100

    submission = ApplicationSubmission(
        application_id=app.id,
        reference_code=ref_code,
        human_approver=user.full_name,
        raw_confirmation_text=f"Official confirmation for {app.grant.grant_name}. Application Reference: {ref_code}."
    )
    db.add(submission)

    # Notification
    notif = Notification(
        user_id=user.id,
        title="Application Submitted Successfully",
        message=f"Your application for '{app.grant.grant_name}' on behalf of '{app.organisation.organisation_name}' has been submitted. Reference: {ref_code}.",
        notification_type="submitted",
        reference_link=f"/applications/{app.id}"
    )
    db.add(notif)

    audit = AuditLog(
        user_id=user.id,
        action="application_submitted",
        target_type="application",
        target_id=app.id,
        details={"reference": ref_code, "approver": user.full_name}
    )
    db.add(audit)
    db.commit()
    db.refresh(app)

    return app

@router.patch("/{app_id}/status", response_model=ApplicationResponse)
def update_application_status(
    app_id: str,
    req: UpdateApplicationStatusRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = req.status
    if req.awarded_amount is not None:
        app.awarded_amount = req.awarded_amount
        app.decision_date = datetime.datetime.utcnow()

    db.commit()
    db.refresh(app)

    audit = AuditLog(
        user_id=user.id,
        action="application_status_updated",
        target_type="application",
        target_id=app.id,
        details={"new_status": req.status.value, "awarded": req.awarded_amount}
    )
    db.add(audit)
    db.commit()

    return app
