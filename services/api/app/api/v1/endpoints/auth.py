from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.user import User
from app.schemas.user import UserLogin, Token, UserResponse
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.models.audit import AuditLog
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/login", response_model=Token)
def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == data.email,
        User.deleted_at.is_(None)
    ).first()
    
    if not user or not verify_password(data.password, user.hashed_password):
        # Audit failed login
        _log_audit(db, None, "login_failed", "auth", data.email, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account disabled")
    
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    
    _log_audit(db, user.id, "login_success", "auth", str(user.id), request)
    
    return Token(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
    )


@router.post("/refresh", response_model=Token)
def refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == uuid.UUID(user_id), User.deleted_at.is_(None)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    
    return Token(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
    )


@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    # With JWT we rely on token expiry; log the logout action
    # In production, implement a token blacklist with Redis
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
):
    from app.api.v1.deps import get_current_user
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == uuid.UUID(user_id), User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def _log_audit(db: Session, user_id, action: str, resource_type: str, resource_id: str, request: Request):
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            occurred_at=datetime.now(timezone.utc),
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"Audit log failed: {e}")
