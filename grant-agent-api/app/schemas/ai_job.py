import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.enums import AITaskStatus

class AIJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_type: str
    grant_id: Optional[str] = None
    organisation_id: Optional[str] = None
    application_id: Optional[str] = None
    status: AITaskStatus
    attempt_count: int
    max_retries: int
    model_attempted: Optional[str] = None
    last_error_category: Optional[str] = None
    last_error_message: Optional[str] = None
    result_payload: Optional[Dict[str, Any]] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
