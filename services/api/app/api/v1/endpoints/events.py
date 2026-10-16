import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.event import AIEvent, EventStatus, EventSeverity, EventAuditLog, EventAssignment
from app.models.user import User
from app.schemas.event import (
    AIEventCreate, AIEventResponse, AIEventListResponse,
    EventAcknowledge, EventAssignRequest, EventResolve, EvidenceResponse
)
from app.schemas.common import PaginatedResponse
from app.api.v1.deps import get_current_user, require_permission
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=PaginatedResponse)
def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    camera_id: Optional[uuid.UUID] = None,
    is_simulated: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(AIEvent).filter(AIEvent.is_duplicate == False)
    
    if status:
        query = query.filter(AIEvent.status == status)
    if severity:
        query = query.filter(AIEvent.severity == severity)
    if camera_id:
        query = query.filter(AIEvent.camera_id == camera_id)
    if is_simulated is not None:
        query = query.filter(AIEvent.is_simulated == is_simulated)
    
    query = query.order_by(AIEvent.occurred_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": [AIEventListResponse.model_validate(e) for e in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.get("/{event_id}", response_model=AIEventResponse)
def get_event(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(AIEvent).filter(AIEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/{event_id}/acknowledge", response_model=AIEventResponse)
def acknowledge_event(
    event_id: uuid.UUID,
    data: EventAcknowledge,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(AIEvent).filter(AIEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status not in (EventStatus.NEW,):
        raise HTTPException(status_code=400, detail=f"Cannot acknowledge event in status: {event.status}")
    
    old_status = event.status
    event.status = EventStatus.ACKNOWLEDGED
    event.acknowledged_at = datetime.now(timezone.utc)
    
    audit = EventAuditLog(
        event_id=event.id,
        user_id=current_user.id,
        action="acknowledge",
        old_status=old_status.value,
        new_status=event.status.value,
        note=data.note,
    )
    db.add(audit)
    db.commit()
    db.refresh(event)
    
    # Notify via WebSocket
    from app.services.websocket_manager import ws_manager
    import asyncio
    try:
        asyncio.get_event_loop().run_until_complete(
            ws_manager.broadcast({"type": "ai.event_updated", "event_id": str(event.id), "status": event.status.value})
        )
    except Exception:
        pass  # WebSocket broadcast is best-effort
    
    return event


@router.post("/{event_id}/assign", response_model=AIEventResponse)
def assign_event(
    event_id: uuid.UUID,
    data: EventAssignRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(AIEvent).filter(AIEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    assignee = db.query(User).filter(User.id == data.assignee_id).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assignee not found")
    
    # Deactivate old assignments
    db.query(EventAssignment).filter(
        EventAssignment.event_id == event_id, EventAssignment.is_active == True
    ).update({"is_active": False})
    
    assignment = EventAssignment(
        event_id=event.id,
        assignee_id=data.assignee_id,
        assigned_by_id=current_user.id,
        note=data.note,
    )
    db.add(assignment)
    
    old_status = event.status
    event.status = EventStatus.ASSIGNED
    
    audit = EventAuditLog(
        event_id=event.id,
        user_id=current_user.id,
        action="assign",
        old_status=old_status.value,
        new_status=event.status.value,
        note=data.note,
    )
    db.add(audit)
    db.commit()
    db.refresh(event)
    return event


@router.post("/{event_id}/resolve", response_model=AIEventResponse)
def resolve_event(
    event_id: uuid.UUID,
    data: EventResolve,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(AIEvent).filter(AIEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status == EventStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="Event already resolved")
    
    old_status = event.status
    event.status = EventStatus.FALSE_POSITIVE if data.is_false_positive else EventStatus.RESOLVED
    event.resolved_at = datetime.now(timezone.utc)
    
    audit = EventAuditLog(
        event_id=event.id,
        user_id=current_user.id,
        action="resolve",
        old_status=old_status.value,
        new_status=event.status.value,
        note=data.note,
    )
    db.add(audit)
    db.commit()
    db.refresh(event)
    return event


@router.get("/{event_id}/evidence", response_model=List[EvidenceResponse])
def get_event_evidence(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.event import EventEvidence
    event = db.query(AIEvent).filter(AIEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    evidence_list = db.query(EventEvidence).filter(EventEvidence.event_id == event_id).all()
    
    result = []
    for ev in evidence_list:
        ev_dict = EvidenceResponse.model_validate(ev).model_dump()
        # Generate a short-lived access token for this evidence (not the storage key itself)
        from app.core.security import create_access_token
        from datetime import timedelta
        access_token = create_access_token(
            {"evidence_id": str(ev.id), "user_id": str(current_user.id)},
            expires_delta=timedelta(minutes=15)
        )
        ev_dict["access_url"] = f"/api/v1/evidence/{ev.id}/download?token={access_token}"
        result.append(ev_dict)
    
    return result
