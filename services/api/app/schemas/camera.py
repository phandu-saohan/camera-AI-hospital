from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import Optional, List, Any
import uuid
from datetime import datetime
from app.models.camera import CameraStatus, CameraProtocol


class RecorderCreate(BaseModel):
    name: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    ip_address: str
    port: int = 80


class RecorderUpdate(BaseModel):
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    is_active: Optional[bool] = None


class RecorderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    ip_address: str
    port: int
    is_active: bool
    created_at: datetime
    # credentials and rtsp_urls are NEVER returned


class CameraCreate(BaseModel):
    name: str
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    protocol: CameraProtocol = CameraProtocol.RTSP
    location_id: Optional[uuid.UUID] = None
    recorder_id: Optional[uuid.UUID] = None
    ai_enabled: bool = False
    tags: Optional[List[str]] = None
    is_demo: bool = False
    # Stream credentials are accepted but stored encrypted, never echoed back
    username: Optional[str] = None  # write-only, stored encrypted
    password: Optional[str] = None  # write-only, stored encrypted
    rtsp_main_url: Optional[str] = None  # write-only, stored encrypted
    rtsp_sub_url: Optional[str] = None   # write-only, stored encrypted
    
    @field_validator("rtsp_main_url", "rtsp_sub_url", mode="before")
    @classmethod
    def validate_rtsp_url(cls, v):
        if v and not (v.startswith("rtsp://") or v.startswith("rtsps://")):
            if not v.startswith("mock://"):  # allow mock:// for demo mode
                raise ValueError("RTSP URL must start with rtsp:// or rtsps://")
        return v


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    location_id: Optional[uuid.UUID] = None
    recorder_id: Optional[uuid.UUID] = None
    ai_enabled: Optional[bool] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    username: Optional[str] = None
    password: Optional[str] = None
    rtsp_main_url: Optional[str] = None
    rtsp_sub_url: Optional[str] = None


class CameraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    protocol: CameraProtocol
    location_id: Optional[uuid.UUID] = None
    recorder_id: Optional[uuid.UUID] = None
    status: CameraStatus
    is_active: bool
    is_demo: bool
    ai_enabled: bool
    tags: Optional[List[str]] = None
    stream_codec: Optional[str] = None
    stream_resolution: Optional[str] = None
    stream_fps: Optional[float] = None
    last_seen_at: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime
    # rtsp_url, username, password are NEVER included


class CameraListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    ip_address: Optional[str] = None
    status: CameraStatus
    is_active: bool
    is_demo: bool
    ai_enabled: bool
    location_id: Optional[uuid.UUID] = None
    last_seen_at: Optional[datetime] = None
    created_at: datetime


class CameraConnectionTestResult(BaseModel):
    camera_id: uuid.UUID
    success: bool
    latency_ms: Optional[float] = None
    error: Optional[str] = None  # Sanitized error, no credentials
    stream_info: Optional[dict] = None
    tested_at: datetime


class CameraHealthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    camera_id: uuid.UUID
    status: CameraStatus
    latency_ms: Optional[float] = None
    error_message: Optional[str] = None
    checked_at: datetime
