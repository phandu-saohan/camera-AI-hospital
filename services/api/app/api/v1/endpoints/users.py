import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.user import User, Role, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import PaginatedResponse
from app.api.v1.deps import get_current_user, require_permission
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=PaginatedResponse[UserResponse])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_permission("users", "read")),
    db: Session = Depends(get_db),
):
    """List system users with pagination and search."""
    query = db.query(User).filter(User.deleted_at.is_(None))

    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        query = query.filter(
            User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
        )

    total = query.count()
    items = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [UserResponse.model_validate(u) for u in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    role_name: Optional[str] = Query("Operator"),
    current_user: User = Depends(require_permission("users", "write")),
    db: Session = Depends(get_db),
):
    """Create a new user account."""
    existing = db.query(User).filter(User.email == data.email, User.deleted_at.is_(None)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng")

    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=get_password_hash(data.password),
        phone=data.phone,
        is_active=True,
        is_superuser=data.is_superuser,
        department_id=data.department_id,
    )
    db.add(user)
    db.flush()

    # Assign role
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = db.query(Role).filter(Role.name == "Operator").first()
    if role:
        db.add(UserRole(user_id=user.id, role_id=role.id))

    db.commit()
    db.refresh(user)
    logger.info(f"User created: {user.email} by {current_user.email}")
    return user


@router.get("/roles")
def list_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List system roles."""
    roles = db.query(Role).all()
    return [{"id": str(r.id), "name": r.name, "description": r.description} for r in roles]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_permission("users", "read")),
    db: Session = Depends(get_db),
):
    """Get single user by ID."""
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    password: Optional[str] = None,
    current_user: User = Depends(require_permission("users", "write")),
    db: Session = Depends(get_db),
):
    """Update user information or toggle active status."""
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    update_dict = data.model_dump(exclude_none=True)
    for field, val in update_dict.items():
        setattr(user, field, val)

    if password:
        user.hashed_password = get_password_hash(password)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_permission("users", "admin")),
    db: Session = Depends(get_db),
):
    """Soft delete user."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Không thể xóa tài khoản của chính mình")

    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    user.soft_delete()
    db.commit()
