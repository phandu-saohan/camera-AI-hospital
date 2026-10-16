from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.common import HealthResponse
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])


@router.get("/health/live")
def liveness():
    """Kubernetes liveness probe - is the process alive?"""
    return {"status": "alive"}


@router.get("/health/ready", response_model=HealthResponse)
def readiness(db: Session = Depends(get_db)):
    """Kubernetes readiness probe - is the app ready to serve?"""
    db_status = "unknown"
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.warning(f"DB health check error: {e}")
        db_status = f"error: {type(e).__name__}"
    
    # Check AI engine
    ai_status = "disabled"
    if settings.AI_ENABLED:
        try:
            from app.services.ai_status import get_ai_status
            ai_info = get_ai_status()
            ai_status = "ok" if ai_info.get("ready") else "degraded"
        except Exception:
            ai_status = "unavailable"
    
    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        version=settings.APP_VERSION,
        database=db_status,
        demo_mode=settings.DEMO_MODE,
        services={
            "database": db_status,
            "ai_engine": ai_status,
            "video_gateway": "not_checked",
        }
    )


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    """Basic operational metrics."""
    try:
        from app.models.camera import Camera, CameraStatus
        from app.models.event import AIEvent, EventStatus
        from sqlalchemy import func
        
        camera_total = db.query(func.count(Camera.id)).filter(Camera.deleted_at.is_(None)).scalar()
        camera_online = db.query(func.count(Camera.id)).filter(
            Camera.deleted_at.is_(None), Camera.status == CameraStatus.ONLINE
        ).scalar()
        event_new = db.query(func.count(AIEvent.id)).filter(
            AIEvent.status == EventStatus.NEW
        ).scalar()
        event_total_today = db.query(func.count(AIEvent.id)).filter(
            func.date(AIEvent.occurred_at) == func.current_date()
        ).scalar()
        
        return {
            "cameras": {"total": camera_total, "online": camera_online, "offline": camera_total - camera_online},
            "events": {"new": event_new, "today": event_total_today},
            "demo_mode": settings.DEMO_MODE,
        }
    except Exception as e:
        return {"error": str(e)}
