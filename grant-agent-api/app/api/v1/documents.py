from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.core.storage import storage_manager
from app.models.all_models import User, Organisation, Document, AuditLog
from app.models.enums import DocumentCategory, DocumentApprovalStatus
from app.schemas.document import DocumentResponse, DocumentUpdateStatus

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    organisation_id: Optional[str] = None,
    category: Optional[str] = None,
    approval_status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(Document)
    if organisation_id:
        query = query.filter(Document.organisation_id == organisation_id)
    if category:
        query = query.filter(Document.category == category)
    if approval_status:
        query = query.filter(Document.approval_status == approval_status)
    return query.order_by(Document.upload_date.desc()).all()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    organisation_id: str = Form(...),
    category: str = Form("Organisation profile"),
    description: Optional[str] = Form(None),
    approved_for_application_use: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    org = db.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")

    content = await file.read()
    storage_path, unique_key = await storage_manager.save_file(
        content=content,
        filename=file.filename or "uploaded_file.pdf",
        content_type=file.content_type
    )

    # Basic text extraction from bytes or metadata
    extracted_text = f"Document content extracted from {file.filename} ({len(content)} bytes)"
    
    # Try finding category enum
    matched_cat = DocumentCategory.ORGANISATION_PROFILE
    for c in DocumentCategory:
        if c.value.lower() == category.lower():
            matched_cat = c
            break

    doc = Document(
        organisation_id=organisation_id,
        filename=file.filename or "document.pdf",
        storage_path=storage_path,
        file_size_bytes=len(content),
        mime_type=file.content_type or "application/pdf",
        category=matched_cat,
        description=description,
        approval_status=DocumentApprovalStatus.APPROVED_FOR_APPLICATION_USE if approved_for_application_use else DocumentApprovalStatus.PENDING_REVIEW,
        extracted_metadata={"file_key": unique_key, "original_name": file.filename},
        extracted_text=extracted_text
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    audit = AuditLog(
        user_id=user.id,
        action="document_uploaded",
        target_type="document",
        target_id=doc.id,
        details={"filename": doc.filename, "category": doc.category.value, "approval_status": doc.approval_status.value}
    )
    db.add(audit)
    db.commit()

    return doc

@router.patch("/{doc_id}/approval", response_model=DocumentResponse)
def update_document_approval(
    doc_id: str,
    data: DocumentUpdateStatus,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.approval_status = data.approval_status
    db.commit()
    db.refresh(doc)

    audit = AuditLog(
        user_id=user.id,
        action="document_approval_updated",
        target_type="document",
        target_id=doc.id,
        details={"approval_status": doc.approval_status.value}
    )
    db.add(audit)
    db.commit()

    return doc

@router.delete("/{doc_id}")
def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}
