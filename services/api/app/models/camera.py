import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, Text, Integer, Float, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Index
from app.db.base import Base
from app.models.base_mixin import UUIDMixin, TimestampMixin, SoftDeleteMixin
import enum


class CameraStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    DISABLED = "disabled"
    UNKNOWN = "unknown"


class CameraProtocol(str, enum.Enum):
    RTSP = "rtsp"
    ONVIF = "onvif"
    HTTP = "http"
    MOCK = "mock"


class Recorder(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Network Video Recorder or video management system."""
    __tablename__ = "recorders"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=80, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    extra_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    cameras: Mapped[List["Camera"]] = relationship(back_populates="recorder")


class Camera(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "cameras"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Physical details
    manufacturer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    firmware_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mac_address: Mapped[str | None] = mapped_column(String(17), nullable=True)
    
    # Network
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protocol: Mapped[CameraProtocol] = mapped_column(
        SAEnum(CameraProtocol), default=CameraProtocol.RTSP, nullable=False
    )
    
    # Location
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True
    )
    recorder_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recorders.id"), nullable=True
    )
    
    # Status
    status: Mapped[CameraStatus] = mapped_column(
        SAEnum(CameraStatus), default=CameraStatus.UNKNOWN, nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Clearly marks demo cameras
    
    # AI
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_rules_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # Stream info (discovered, not user input for sensitive fields)
    stream_codec: Mapped[str | None] = mapped_column(String(50), nullable=True)
    stream_resolution: Mapped[str | None] = mapped_column(String(20), nullable=True)
    stream_fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Tags/groups
    tags: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    
    # Health
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    connection_retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    location: Mapped["Location | None"] = relationship(back_populates="cameras")
    recorder: Mapped["Recorder | None"] = relationship(back_populates="cameras")
    streams: Mapped[List["CameraStream"]] = relationship(back_populates="camera", cascade="all, delete-orphan")
    credentials: Mapped[List["CameraCredential"]] = relationship(back_populates="camera", cascade="all, delete-orphan")
    health_logs: Mapped[List["CameraHealthLog"]] = relationship(back_populates="camera", cascade="all, delete-orphan")
    ai_events: Mapped[List["AIEvent"]] = relationship(back_populates="camera")
    ai_rules: Mapped[List["AIRule"]] = relationship(back_populates="camera")


class CameraStream(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "camera_streams"
    
    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False
    )
    stream_type: Mapped[str] = mapped_column(String(50), default="main", nullable=False)  # main | sub
    # NOTE: rtsp_url is stored server-side only, NEVER returned to client
    rtsp_url_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)  # encrypted
    channel: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resolution: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    codec: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    camera: Mapped["Camera"] = relationship(back_populates="streams")


class CameraCredential(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "camera_credentials"
    
    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False
    )
    # NEVER store or return these in plaintext
    username_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    password_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    credential_type: Mapped[str] = mapped_column(String(50), default="rtsp", nullable=False)
    
    camera: Mapped["Camera"] = relationship(back_populates="credentials")


class CameraHealthLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "camera_health_logs"
    
    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[CameraStatus] = mapped_column(SAEnum(CameraStatus), nullable=False)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    camera: Mapped["Camera"] = relationship(back_populates="health_logs")
    
    __table_args__ = (
        Index("ix_camera_health_logs_camera_checked", "camera_id", "checked_at"),
    )
