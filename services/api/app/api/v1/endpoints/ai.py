import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.ai import AIRule, AIModel
from app.models.user import User
from app.schemas.ai import AIRuleCreate, AIRuleUpdate, AIRuleResponse, AIModelResponse, AIStatusResponse
from app.api.v1.deps import get_current_user, require_permission
from app.services.ai_status import get_ai_status
from app.services.ai_worker import ai_worker

router = APIRouter(prefix="/ai", tags=["AI Engine"])


@router.get("/status", response_model=AIStatusResponse)
def get_status(current_user: User = Depends(get_current_user)):
    """Return runtime AI status, GPU detection and worker state."""
    status_data = get_ai_status()
    from app.core.config import settings
    return AIStatusResponse(
        ai_enabled=status_data["ready"],
        backend=status_data["backend"],
        gpu_available=status_data["gpu_available"],
        gpu_devices=status_data["gpu_devices"],
        active_workers=1 if ai_worker.is_running else 0,
        queue_depth=status_data.get("queue_depth", 0),
        demo_mode=settings.DEMO_MODE,
    )


@router.post("/trigger-scan")
def trigger_scan(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """Manually trigger one computer vision inference scan across active cameras."""
    events, payloads = ai_worker.run_scan_cycle()
    return {
        "status": "success",
        "scanned_at": str(uuid.uuid4()),
        "events_triggered": len(events),
        "details": [{"id": str(e.id), "type": e.event_type, "severity": e.severity.value} for e in events],
    }


@router.get("/rules", response_model=List[AIRuleResponse])
def list_rules(
    camera_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(AIRule)
    if camera_id:
        query = query.filter(AIRule.camera_id == camera_id)
    return query.all()


@router.post("/rules", response_model=AIRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    data: AIRuleCreate,
    current_user: User = Depends(require_permission("ai_rules", "write")),
    db: Session = Depends(get_db),
):
    rule = AIRule(
        camera_id=data.camera_id,
        model_id=data.model_id,
        name=data.name,
        rule_type=data.rule_type,
        confidence_threshold=data.confidence_threshold,
        roi_polygon=[p.model_dump() for p in data.roi_polygon] if data.roi_polygon else None,
        schedule=data.schedule.model_dump() if data.schedule else None,
        cooldown_seconds=data.cooldown_seconds,
        min_duration_seconds=data.min_duration_seconds,
        severity=data.severity,
        extra_config=data.extra_config,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.patch("/rules/{rule_id}", response_model=AIRuleResponse)
def update_rule(
    rule_id: uuid.UUID,
    data: AIRuleUpdate,
    current_user: User = Depends(require_permission("ai_rules", "write")),
    db: Session = Depends(get_db),
):
    rule = db.query(AIRule).filter(AIRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="AI Rule not found")
    
    update_data = data.model_dump(exclude_none=True)
    if "roi_polygon" in update_data and update_data["roi_polygon"]:
        update_data["roi_polygon"] = [p.model_dump() for p in data.roi_polygon]
    if "schedule" in update_data and update_data["schedule"]:
        update_data["schedule"] = data.schedule.model_dump()
        
    for field, val in update_data.items():
        setattr(rule, field, val)
        
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: uuid.UUID,
    current_user: User = Depends(require_permission("ai_rules", "admin")),
    db: Session = Depends(get_db),
):
    """Delete an AI Rule."""
    rule = db.query(AIRule).filter(AIRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="AI Rule not found")
    db.delete(rule)
    db.commit()
