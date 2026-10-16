from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import uuid
from datetime import datetime


class DepartmentCreate(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime


class LocationCreate(BaseModel):
    department_id: uuid.UUID
    name: str
    building: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    description: Optional[str] = None


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    description: Optional[str] = None


class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    department_id: uuid.UUID
    name: str
    building: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
