import uuid
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.models.base_mixin import UUIDMixin, TimestampMixin


class Department(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "departments"
    
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    locations: Mapped[List["Location"]] = relationship(back_populates="department", cascade="all, delete-orphan")


class Location(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "locations"
    
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    building: Mapped[str | None] = mapped_column(String(100), nullable=True)
    floor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    room: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    department: Mapped["Department"] = relationship(back_populates="locations")
    cameras: Mapped[List["Camera"]] = relationship(back_populates="location")
