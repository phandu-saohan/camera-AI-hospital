import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.location import Department, Location
from app.models.user import User
from app.schemas.location import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    LocationCreate, LocationUpdate, LocationResponse
)
from app.api.v1.deps import get_current_user, require_permission
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/departments", tags=["Departments & Locations"])


@router.get("", response_model=List[DepartmentResponse])
def list_departments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all hospital departments."""
    return db.query(Department).order_by(Department.name.asc()).all()


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    data: DepartmentCreate,
    current_user: User = Depends(require_permission("users", "write")),
    db: Session = Depends(get_db),
):
    """Create a new hospital department."""
    existing = db.query(Department).filter(Department.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tên khoa phòng này đã tồn tại")

    dept = Department(
        name=data.name,
        code=data.code,
        description=data.description,
        is_active=True,
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.patch("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: uuid.UUID,
    data: DepartmentUpdate,
    current_user: User = Depends(require_permission("users", "write")),
    db: Session = Depends(get_db),
):
    """Update department info."""
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Khoa phòng không tồn tại")

    update_dict = data.model_dump(exclude_none=True)
    for field, val in update_dict.items():
        setattr(dept, field, val)

    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    department_id: uuid.UUID,
    current_user: User = Depends(require_permission("users", "admin")),
    db: Session = Depends(get_db),
):
    """Delete department and its locations."""
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Khoa phòng không tồn tại")

    db.delete(dept)
    db.commit()


@router.get("/{department_id}/locations", response_model=List[LocationResponse])
def list_department_locations(
    department_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List locations in a department."""
    return db.query(Location).filter(Location.department_id == department_id).all()


@router.post("/locations", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    data: LocationCreate,
    current_user: User = Depends(require_permission("users", "write")),
    db: Session = Depends(get_db),
):
    """Create a new location inside a department."""
    loc = Location(
        department_id=data.department_id,
        name=data.name,
        building=data.building,
        floor=data.floor,
        room=data.room,
        description=data.description,
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: uuid.UUID,
    current_user: User = Depends(require_permission("users", "admin")),
    db: Session = Depends(get_db),
):
    """Delete a location."""
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Khu vực không tồn tại")
    db.delete(loc)
    db.commit()
