from pydantic import BaseModel
from typing import TypeVar, Generic, List, Optional, Any

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    demo_mode: bool
    services: dict[str, str]


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
