from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.all_models import User, AuditLog
from app.core.security import mask_sensitive_data

router = APIRouter(prefix="/audit", tags=["Audit Log"])

@router.get("")
def get_audit_trail(
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if target_type:
        query = query.filter(AuditLog.target_type == target_type)

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    # Format and sanitize output to guarantee secrets are never exposed
    sanitized_logs = []
    for log in logs:
        clean_details = {}
        for k, v in (log.details or {}).items():
            if any(s in k.lower() for s in ["password", "token", "otp", "secret"]):
                clean_details[k] = "******"
            elif isinstance(v, str):
                clean_details[k] = mask_sensitive_data(v)
            else:
                clean_details[k] = v
        
        sanitized_logs.append({
            "id": log.id,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "details": clean_details,
            "timestamp": log.timestamp
        })

    return sanitized_logs
