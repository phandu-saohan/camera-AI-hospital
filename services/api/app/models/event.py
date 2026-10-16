import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, Text, Float, DateTime, Enum as SAEnum, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.models.base_mixin import UUIDMixin, TimestampMixin
import enum


class EventStatus(str, enum.Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    ASSIGNED = "assigned"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class EventSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EvidenceType(str, enum.Enum):
    SNAPSHOT = "snapshot"
    CLIP = "clip"
    METADATA = "metadata"


class AIEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_events"
    
    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False, index=True
    )
    rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_rules.id"), nullable=True, index=True
    )
    
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[EventStatus] = mapped_column(
        SAEnum(EventStatus), default=EventStatus.NEW, nullable=False, index=True
    )
    severity: Mapped[EventSeverity] = mapped_column(
        SAEnum(EventSeverity), default=EventSeverity.MEDIUM, nullable=False, index=True
    )
    
    # Inference data
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rule_version: Mapped[int | None] = mapped_column(String(20), nullable=True)
    
    # Deduplication
    correlation_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Simulation flag - MUST be set for any simulated/demo event
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    detection_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    camera: Mapped["Camera"] = relationship(back_populates="ai_events")
    rule: Mapped["AIRule | None"] = relationship(back_populates="events")
    evidence: Mapped[List["EventEvidence"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    assignments: Mapped[List["EventAssignment"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    audit_logs: Mapped[List["EventAuditLog"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_ai_events_occurred_status", "occurred_at", "status"),
        Index("ix_ai_events_camera_occurred", "camera_id", "occurred_at"),
    )


class EventEvidence(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "event_evidence"
    
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=False
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(SAEnum(EvidenceType), nullable=False)
    
    # Storage key (relative path inside evidence storage, NOT absolute)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(nullable=True)
    
    access_classification: Mapped[str] = mapped_column(String(50), default="restricted", nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    event: Mapped["AIEvent"] = relationship(back_populates="evidence")


class EventAssignment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "event_assignments"
    
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assignee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    assigned_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    event: Mapped["AIEvent"] = relationship(back_populates="assignments")
    assignee: Mapped["User"] = relationship(back_populates="event_assignments", foreign_keys=[assignee_id])


class EventAuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "event_audit_logs"
    
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    event: Mapped["AIEvent"] = relationship(back_populates="audit_logs")
