from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
import uuid
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str
    is_superuser: bool = False
    department_id: Optional[uuid.UUID] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    department_id: Optional[uuid.UUID] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    department_id: Optional[uuid.UUID] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None
    # NOTE: hashed_password is NEVER included


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user ID
    type: str  # access | refresh
    exp: int
