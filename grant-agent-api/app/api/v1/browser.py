import os
import asyncio
import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.core.config import settings
from app.api.v1.auth import get_current_user
from app.models.all_models import (
    User, Application, BrowserSession, BrowserEvent, AuditLog, Notification
)
from app.models.enums import (
    BrowserSessionStatus, InterventionType, ApplicationStatus, DocumentApprovalStatus
)
from app.schemas.browser import (
    BrowserSessionResponse, BrowserActionCommand
)

router = APIRouter(prefix="/browser", tags=["Browser Automation"])

class StartBrowserSessionRequest(BaseModel):
    application_id: str
    target_url: Optional[str] = None
    exact_url_mode: bool = False
    user_provided_answers: Optional[Dict[str, Any]] = None

def run_browser_automation_task(
    session_id: str,
    app_id: str,
    target_url: str,
    user_answers: Optional[Dict[str, Any]] = None
):
    """
    Executes actual Playwright automation in background:
    Navigates to URL, captures screenshots, fills answers, uploads docs, and detects human gates.
    """
    db = SessionLocal()
    try:
        session = db.query(BrowserSession).filter(BrowserSession.id == session_id).first()
        app = db.query(Application).filter(Application.id == app_id).first()
        if not session or not app:
            return

        session.status = BrowserSessionStatus.NAVIGATING
        session.current_task = f"Navigating to {target_url}"
        db.commit()

        # Build org data
        org = app.organisation
        org_data = {
            "organisation_name": org.organisation_name if org else "Applicant Organisation",
            "email": org.email if org else "contact@applicant.org",
            "phone": org.phone if org else "+234 800 000 0000",
            "website": org.website if org else target_url,
            "address": org.address if org else "Lagos, Nigeria",
            "operating_countries": org.operating_countries if org else ["Nigeria"],
            "problems_addressed": (org.problems_addressed if org else None) or app.problem_statement or "",
            "products": (org.products if org else None) or app.proposed_solution or "",
            "technology_solution": (org.technology_solution if org else None) or app.proposed_solution or "",
            "beneficiaries_count": (org.beneficiaries_count if org else None) or 1000,
            "founders": [{"name": f.name, "role": f.role} for f in (org.founders or [])] if org else []
        }

        # Build approved answers
        approved_answers = {}
        for ans in app.answers:
            if ans.question and ans.question.question_text:
                approved_answers[ans.question.question_text] = ans.answer_text
        if app.problem_statement:
            approved_answers["problem"] = app.problem_statement
            approved_answers["challenge"] = app.problem_statement
        if app.proposed_solution:
            approved_answers["solution"] = app.proposed_solution
            approved_answers["innovation"] = app.proposed_solution
        if app.project_title:
            approved_answers["title"] = app.project_title
            approved_answers["project_name"] = app.project_title

        # Build approved documents
        approved_docs = []
        for ad in app.documents:
            if ad.document and ad.document.approval_status == DocumentApprovalStatus.APPROVED_FOR_APPLICATION_USE:
                approved_docs.append({
                    "filename": ad.document.filename,
                    "storage_path": ad.document.storage_path
                })

        # Initialize Playwright worker with screenshots directory
        from worker.browser_agent import PlaywrightBrowserWorker
        screenshots_dir = getattr(settings, "SCREENSHOTS_DIR", "./browser_screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        worker = PlaywrightBrowserWorker(session_id=session.id, screenshots_dir=screenshots_dir)

        # Run async execution
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                worker.execute_application_flow(
                    application_url=target_url,
                    org_data=org_data,
                    approved_answers=approved_answers,
                    approved_documents=approved_docs,
                    submit_after_approval=False,
                    user_provided_answers=user_answers
                )
            )
        finally:
            loop.close()

        # Update session with actual result
        session.status = result.get("status", BrowserSessionStatus.COMPLETED)
        session.current_url = result.get("current_url", target_url)
        session.latest_screenshot_path = result.get("latest_screenshot_path")
        session.intervention_required = result.get("intervention_required", False)
        session.intervention_type = result.get("intervention_type", InterventionType.NONE)
        session.intervention_message = result.get("intervention_message")
        session.completed_fields_count = result.get("fields_completed", 0)
        session.current_task = (
            f"Gate: {session.intervention_message}" if session.intervention_required
            else f"Completed ({session.completed_fields_count} fields filled)"
        )
        if session.status in [BrowserSessionStatus.COMPLETED, BrowserSessionStatus.FAILED]:
            session.completed_at = datetime.datetime.utcnow()

        for ev in result.get("events", []):
            db.add(BrowserEvent(
                session_id=session.id,
                event_type=ev.get("type", "browser_event"),
                description=ev.get("msg") or ev.get("url") or str(ev),
                metadata_json=ev
            ))

        db.commit()
    except Exception as e:
        try:
            session = db.query(BrowserSession).filter(BrowserSession.id == session_id).first()
            if session:
                session.status = BrowserSessionStatus.FAILED
                session.error_message = str(e)
                session.current_task = f"Failed: {str(e)[:150]}"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()

@router.post("/start", response_model=BrowserSessionResponse)
def start_browser_session(
    req: StartBrowserSessionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == req.application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    target_url = req.target_url or app.grant.application_url or app.grant.official_url

    session = BrowserSession(
        application_id=app.id,
        status=BrowserSessionStatus.INITIALIZING,
        current_url=target_url,
        current_task="Launching isolated Chromium worker",
        current_step="Navigating to official portal",
        total_fields_detected=len(app.questions) + 2,
        completed_fields_count=0
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Initial event
    event = BrowserEvent(
        session_id=session.id,
        event_type="visit",
        description=f"Chromium instance initiated. Target URL: {target_url}",
        metadata_json={"url": target_url, "exact_mode": req.exact_url_mode}
    )
    db.add(event)

    app.status = ApplicationStatus.APPLICATION_STARTED
    db.commit()
    db.refresh(session)

    audit = AuditLog(
        user_id=user.id,
        action="browser_started",
        target_type="browser_session",
        target_id=session.id,
        details={"url": target_url, "application_id": app.id}
    )
    db.add(audit)
    db.commit()

    # Launch actual Playwright worker in background task
    background_tasks.add_task(
        run_browser_automation_task,
        session_id=session.id,
        app_id=app.id,
        target_url=target_url,
        user_answers=req.user_provided_answers
    )

    return session

@router.get("/session/{session_id}", response_model=BrowserSessionResponse)
@router.get("/{session_id}", response_model=BrowserSessionResponse)
def get_browser_session(
    session_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    session = db.query(BrowserSession).filter(BrowserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Browser session not found")
    return session

@router.post("/{session_id}/command", response_model=BrowserSessionResponse)
def control_browser_session(
    session_id: str,
    cmd: BrowserActionCommand,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    session = db.query(BrowserSession).filter(BrowserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Browser session not found")

    action = cmd.action.lower()
    
    if action == "pause":
        session.status = BrowserSessionStatus.PAUSED
        session.current_task = "Paused by user"
        event_desc = "Session paused by user request."
    elif action == "resume":
        session.status = BrowserSessionStatus.FILLING_ANSWERS
        session.current_task = "Resumed form completion"
        session.intervention_required = False
        session.intervention_type = InterventionType.NONE
        event_desc = "Session resumed by user."
    elif action == "take_control":
        session.status = BrowserSessionStatus.WAITING_FOR_USER
        session.intervention_required = True
        session.intervention_type = InterventionType.MANUAL_TAKEOVER
        session.current_task = "Manual user takeover active"
        event_desc = "User engaged interactive takeover."
    elif action == "cancel":
        session.status = BrowserSessionStatus.CANCELLED
        session.current_task = "Session aborted"
        event_desc = "Browser session terminated by user."
    elif action == "submit_intervention":
        session.status = BrowserSessionStatus.FILLING_ANSWERS
        session.intervention_required = False
        session.intervention_type = InterventionType.NONE
        session.current_task = "Verification submitted. Resuming automation."
        event_desc = "Human intervention data received and applied."
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action '{cmd.action}'")

    ev = BrowserEvent(
        session_id=session.id,
        event_type="command",
        description=event_desc,
        metadata_json=cmd.intervention_data or {}
    )
    db.add(ev)
    db.commit()
    db.refresh(session)

    audit = AuditLog(
        user_id=user.id,
        action="browser_command_sent",
        target_type="browser_session",
        target_id=session.id,
        details={"command": action}
    )
    db.add(audit)
    db.commit()

    return session

@router.get("/{session_id}/screenshot")
def get_session_screenshot(
    session_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    session = db.query(BrowserSession).filter(BrowserSession.id == session_id).first()
    if not session or not session.latest_screenshot_path or not os.path.exists(session.latest_screenshot_path):
        # Return fallback placeholder 1x1 png or 404
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return FileResponse(session.latest_screenshot_path, media_type="image/png")
