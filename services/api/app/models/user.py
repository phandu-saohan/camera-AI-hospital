import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.models.base_mixin import UUIDMixin, TimestampMixin, SoftDeleteMixin


class Permission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "permissions"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)  # cameras, events, users, etc.
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # read, write, delete, admin
    
    role_permissions: Mapped[List["RolePermission"]] = relationship(back_populates="permission")


class Role(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "roles"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    user_roles: Mapped[List["UserRole"]] = relationship(back_populates="role")
    role_permissions: Mapped[List["RolePermission"]] = relationship(back_populates="role")


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True
    )
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    user_roles: Mapped[List["UserRole"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    event_assignments: Mapped[List["EventAssignment"]] = relationship(back_populates="assignee", foreign_keys="EventAssignment.assignee_id")


class UserRole(Base, TimestampMixin):
    __tablename__ = "user_roles"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    
    user: Mapped["User"] = relationship(back_populates="user_roles")
    role: Mapped["Role"] = relationship(back_populates="user_roles")


class RolePermission(Base, TimestampMixin):
    __tablename__ = "role_permissions"
    
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )
    
    role: Mapped["Role"] = relationship(back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship(back_populates="role_permissions")
