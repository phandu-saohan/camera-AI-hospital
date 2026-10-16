from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
import uuid
from datetime import datetime
from app.models.ai import AIRuleType


class AIModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    version: str
    model_type: str
    backend: str
    is_active: bool
    capabilities: Optional[List[str]] = None
    created_at: datetime


class ROIPoint(BaseModel):
    x: float  # normalized 0-1
    y: float  # normalized 0-1


class AIRuleSchedule(BaseModel):
    days: List[int] = [0, 1, 2, 3, 4, 5, 6]  # 0=Monday, 6=Sunday
    start_time: str = "00:00"  # HH:MM
    end_time: str = "23:59"  # HH:MM


class AIRuleCreate(BaseModel):
    camera_id: uuid.UUID
    model_id: Optional[uuid.UUID] = None
    name: str
    rule_type: AIRuleType
    confidence_threshold: float = 0.5
    roi_polygon: Optional[List[ROIPoint]] = None
    schedule: Optional[AIRuleSchedule] = None
    cooldown_seconds: int = 60
    min_duration_seconds: float = 1.0
    severity: str = "medium"
    extra_config: Optional[dict] = None


class AIRuleUpdate(BaseModel):
    name: Optional[str] = None
    is_enabled: Optional[bool] = None
    confidence_threshold: Optional[float] = None
    roi_polygon: Optional[List[ROIPoint]] = None
    schedule: Optional[AIRuleSchedule] = None
    cooldown_seconds: Optional[int] = None
    min_duration_seconds: Optional[float] = None
    severity: Optional[str] = None
    extra_config: Optional[dict] = None


class AIRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    camera_id: uuid.UUID
    model_id: Optional[uuid.UUID] = None
    name: str
    rule_type: AIRuleType
    is_enabled: bool
    confidence_threshold: float
    roi_polygon: Optional[List[dict]] = None
    schedule: Optional[dict] = None
    cooldown_seconds: int
    min_duration_seconds: float
    severity: str
    extra_config: Optional[dict] = None
    created_at: datetime


class AIStatusResponse(BaseModel):
    ai_enabled: bool
    backend: str
    gpu_available: bool
    gpu_devices: List[dict]
    active_workers: int
    queue_depth: int
    demo_mode: bool
