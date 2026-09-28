from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.models.all_models import User
from app.models.enums import UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Optional[UserRole] = UserRole.MEMBER

class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str

class FirebaseLoginRequest(BaseModel):
    firebase_token: str
    email: EmailStr
    full_name: str
    firebase_uid: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    role: str

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    if not credentials:
        # Development fallback: auto-provision default local admin user if no token provided
        dev_user = db.query(User).filter(User.email == "demo@grantagent.ai").first()
        if not dev_user:
            dev_user = User(
                email="demo@grantagent.ai",
                full_name="Grant Agent Officer",
                role=UserRole.ADMIN,
                hashed_password=get_password_hash("password123")
            )
            db.add(dev_user)
            db.commit()
            db.refresh(dev_user)
        return dev_user

    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=req.email,
        full_name=req.full_name,
        role=req.role or UserRole.MEMBER,
        hashed_password=get_password_hash(req.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value
    )

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    identifier = (req.email or req.username or "").strip().lower()
    if not identifier:
        raise HTTPException(status_code=400, detail="Email or username is required")
    user = db.query(User).filter(User.email.ilike(identifier)).first()
    if not user or not user.hashed_password or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value
    )

@router.post("/firebase-login", response_model=TokenResponse)
def firebase_login(req: FirebaseLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter((User.firebase_uid == req.firebase_uid) | (User.email == req.email)).first()
    if not user:
        user = User(
            email=req.email,
            full_name=req.full_name,
            firebase_uid=req.firebase_uid,
            role=UserRole.MEMBER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.firebase_uid = req.firebase_uid
        db.commit()

    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value
    )

@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "created_at": user.created_at
    }
