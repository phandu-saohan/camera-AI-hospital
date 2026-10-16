from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
import uuid
from datetime import datetime
from app.models.event import EventStatus, EventSeverity, EvidenceType


class AIEventCreate(BaseModel):
    camera_id: uuid.UUID
    rule_id: Optional[uuid.UUID] = None
    event_type: str
    severity: EventSeverity = EventSeverity.MEDIUM
    confidence: Optional[float] = None
    model_version: Optional[str] = None
    description: Optional[str] = None
    detection_metadata: Optional[dict] = None
    occurred_at: datetime
    is_simulated: bool = False
    correlation_id: Optional[str] = None


class AIEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    camera_id: uuid.UUID
    rule_id: Optional[uuid.UUID] = None
    event_type: str
    status: EventStatus
    severity: EventSeverity
    confidence: Optional[float] = None
    model_version: Optional[str] = None
    is_simulated: bool
    is_duplicate: bool
    description: Optional[str] = None
    correlation_id: Optional[str] = None
    occurred_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime


class AIEventListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    camera_id: uuid.UUID
    event_type: str
    status: EventStatus
    severity: EventSeverity
    is_simulated: bool
    is_duplicate: bool
    occurred_at: datetime
    created_at: datetime


class EventAcknowledge(BaseModel):
    note: Optional[str] = None


class EventAssignRequest(BaseModel):
    assignee_id: uuid.UUID
    note: Optional[str] = None


class EventResolve(BaseModel):
    resolution: str
    is_false_positive: bool = False
    note: Optional[str] = None


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    event_id: uuid.UUID
    evidence_type: EvidenceType
    # storage_key is NEVER returned to client
    access_classification: str
    expires_at: Optional[datetime] = None
    file_size_bytes: Optional[int] = None
    created_at: datetime
    # Temporary access URL generated server-side
    access_url: Optional[str] = None
