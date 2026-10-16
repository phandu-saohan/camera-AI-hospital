import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, Text, Float, Integer, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.models.base_mixin import UUIDMixin, TimestampMixin
import enum


class AIRuleType(str, enum.Enum):
    PERSON_DETECTION = "person_detection"
    RESTRICTED_AREA = "restricted_area"
    FALL_DETECTION = "fall_detection"
    PEOPLE_COUNTING = "people_counting"
    QUEUE_ESTIMATION = "queue_estimation"
    CAMERA_TAMPER = "camera_tamper"
    ZONE_MONITORING = "zone_monitoring"
    PROCEDURE_AREA = "procedure_area"


class AIModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_models"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    model_type: Mapped[str] = mapped_column(String(100), nullable=False)
    backend: Mapped[str] = mapped_column(String(50), nullable=False)  # cpu | cuda | tensorrt
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    capabilities: Mapped[list | None] = mapped_column(JSON, nullable=True)  # ["person_detection", "pose"]
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    
    rules: Mapped[List["AIRule"]] = relationship(back_populates="model")


class AIRule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_rules"
    
    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_models.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    rule_type: Mapped[AIRuleType] = mapped_column(SAEnum(AIRuleType), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Thresholds
    confidence_threshold: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    
    # ROI - polygon points as JSON [{x: float, y: float}, ...] in normalized coords 0-1
    roi_polygon: Mapped[list | None] = mapped_column(JSON, nullable=True)
    
    # Schedule: JSON cron-style {"days": [1,2,3,4,5], "start": "08:00", "end": "18:00"}
    schedule: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Cooldown in seconds before re-triggering same rule on same camera
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    
    # Min detection duration before triggering (seconds)
    min_duration_seconds: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    
    # Severity: low | medium | high | critical
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    
    # Extra rule-specific config
    extra_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    camera: Mapped["Camera"] = relationship(back_populates="ai_rules")
    model: Mapped["AIModel | None"] = relationship(back_populates="rules")
    events: Mapped[List["AIEvent"]] = relationship(back_populates="rule")
