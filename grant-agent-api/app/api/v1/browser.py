import os
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.all_models import (
    User, Application, BrowserSession, BrowserEvent, AuditLog, Notification
)
from app.models.enums import (
    BrowserSessionStatus, InterventionType, ApplicationStatus
)
from app.schemas.browser import (
    BrowserSessionResponse, BrowserActionCommand
)

router = APIRouter(prefix="/browser", tags=["Browser Automation"])

class StartBrowserSessionRequest(BaseModel):
    application_id: str
    target_url: Optional[str] = None
    exact_url_mode: bool = False

@router.post("/start", response_model=BrowserSessionResponse)
def start_browser_session(
    req: StartBrowserSessionRequest,
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
