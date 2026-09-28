import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.models.enums import BrowserSessionStatus, InterventionType

class BrowserEventResponse(BaseModel):
    id: str
    event_type: str
    description: str
    screenshot_path: Optional[str] = None
    metadata_json: Dict[str, Any] = {}
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class BrowserSessionResponse(BaseModel):
    id: str
    application_id: str
    status: BrowserSessionStatus
    current_url: Optional[str] = None
    current_task: str
    current_step: str
    latest_screenshot_path: Optional[str] = None
    intervention_required: bool
    intervention_type: InterventionType
    intervention_message: Optional[str] = None
    completed_fields_count: int
    total_fields_detected: int
    error_message: Optional[str] = None
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    events: List[BrowserEventResponse] = []

    class Config:
        from_attributes = True

class BrowserActionCommand(BaseModel):
    action: str # "pause", "resume", "take_control", "cancel", "submit_intervention"
    intervention_data: Optional[Dict[str, Any]] = None # e.g. {"otp_code": "123456"} or {"user_confirmed": True}
