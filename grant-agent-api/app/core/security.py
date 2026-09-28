import re
import datetime
from typing import Optional, Any, Dict
import bcrypt
from jose import jwt, JWTError
from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def create_access_token(subject: str, role: str = "member", expires_delta: Optional[datetime.timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode: Dict[str, Any] = {"exp": expire, "sub": str(subject), "role": role}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

# Prompt Injection Defense: Sanitize untrusted input from external websites
SUSPICIOUS_PATTERNS = [
    r"(?i)ignore\s+(previous|all)\s+instructions",
    r"(?i)system\s+prompt",
    r"(?i)upload\s+your\s+credentials",
    r"(?i)send\s+(secrets|api\s*key|passwords)",
    r"(?i)run\s+this\s+command",
    r"(?i)curl\s+https?://",
    r"(?i)eval\s*\(",
    r"(?i)<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
]

def sanitize_untrusted_web_content(text: str) -> str:
    """
    Sanitizes external web content to prevent prompt injection and remote instruction execution.
    Website text is only treated as factual data, never instructions.
    """
    if not text:
        return ""
    sanitized = text
    for pattern in SUSPICIOUS_PATTERNS:
        sanitized = re.sub(pattern, "[UNTRUSTED_CONTENT_FILTERED]", sanitized)
    return sanitized.strip()

def mask_sensitive_data(text: str) -> str:
    """Masks tokens, OTPs, or passwords in logs and payloads."""
    if not text:
        return ""
    text = re.sub(r"(?i)(password|secret|token|api_key|otp|bearer\s+)[:=]\s*['\"]?([^'\"\s]+)", r"\1=******", text)
    return text
