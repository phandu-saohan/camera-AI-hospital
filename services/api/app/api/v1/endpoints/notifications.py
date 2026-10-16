from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.core.config import settings
from app.services.notification_service import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationTestRequest(BaseModel):
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    webhook_url: Optional[str] = None
    message: Optional[str] = None


@router.get("/config")
def get_notification_config(current_user: User = Depends(get_current_user)):
    """Return status of notification integrations (without exposing full bot token)."""
    has_telegram = bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)
    has_webhook = bool(settings.WEBHOOK_URL)
    return {
        "telegram_enabled": has_telegram,
        "telegram_chat_id": settings.TELEGRAM_CHAT_ID if has_telegram else None,
        "webhook_enabled": has_webhook,
        "webhook_url": settings.WEBHOOK_URL if has_webhook else None,
        "min_severity": settings.NOTIFICATION_MIN_SEVERITY,
        "privacy_face_blur": settings.PRIVACY_FACE_BLUR,
    }


@router.post("/test")
def test_notification(
    data: NotificationTestRequest,
    current_user: User = Depends(get_current_user),
):
    """Test Telegram Bot or Webhook delivery."""
    custom_service = notification_service
    if data.telegram_bot_token:
        custom_service.bot_token = data.telegram_bot_token
    if data.telegram_chat_id:
        custom_service.chat_id = data.telegram_chat_id
    if data.webhook_url:
        custom_service.webhook_url = data.webhook_url

    results = custom_service.send_incident_alert(
        event_id="test-notification-event",
        camera_name="[TEST] Camera Sảnh Cấp cứu",
        event_type="queue_estimation",
        severity="high",
        description=data.message or "Thử nghiệm gửi cảnh báo tự động từ hệ thống AI Hospital Camera.",
        occurred_at="Vừa xong",
    )
    return {
        "status": "success",
        "results": results,
    }
