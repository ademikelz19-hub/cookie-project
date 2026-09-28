import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.models.enums import DocumentCategory, DocumentApprovalStatus

class DocumentBase(BaseModel):
    category: DocumentCategory = DocumentCategory.ORGANISATION_PROFILE
    description: Optional[str] = None
    expiration_date: Optional[datetime.datetime] = None
    approval_status: DocumentApprovalStatus = DocumentApprovalStatus.PENDING_REVIEW

class DocumentCreate(DocumentBase):
    organisation_id: str

class DocumentUpdateStatus(BaseModel):
    approval_status: DocumentApprovalStatus

class DocumentResponse(DocumentBase):
    id: str
    organisation_id: str
    filename: str
    storage_path: str
    file_size_bytes: int
    mime_type: str
    upload_date: datetime.datetime
    extracted_metadata: Dict[str, Any] = {}
    extracted_text: Optional[str] = None

    class Config:
        from_attributes = True
