import os
import json
import logging
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

SEVERITY_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


class NotificationService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.webhook_url = settings.WEBHOOK_URL
        self.min_severity = settings.NOTIFICATION_MIN_SEVERITY.lower()

    def should_notify(self, severity: str) -> bool:
        sev_rank = SEVERITY_ORDER.get(severity.lower(), 1)
        min_rank = SEVERITY_ORDER.get(self.min_severity, 3)
        return sev_rank >= min_rank

    def send_incident_alert(
        self,
        event_id: str,
        camera_name: str,
        event_type: str,
        severity: str,
        description: str,
        occurred_at: str,
        snapshot_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatch incident notification to Telegram and generic Webhooks."""
        results = {"telegram": "skipped", "webhook": "skipped"}

        if not self.should_notify(severity):
            logger.debug(f"Notification skipped: severity {severity} < min {self.min_severity}")
            return results

        # 1. Telegram Dispatch
        if self.bot_token and self.chat_id:
            try:
                results["telegram"] = self._send_telegram(
                    camera_name=camera_name,
                    event_type=event_type,
                    severity=severity,
                    description=description,
                    occurred_at=occurred_at,
                    snapshot_path=snapshot_path,
                )
            except Exception as e:
                logger.error(f"Telegram notification error: {e}")
                results["telegram"] = f"error: {str(e)}"
        else:
            logger.info(f"[TELEGRAM DEMO LOG] Incident {severity.upper()} at {camera_name}: {description}")
            results["telegram"] = "demo_logged"

        # 2. Generic Webhook (Zalo OA / Webhook Endpoint)
        if self.webhook_url:
            try:
                results["webhook"] = self._send_webhook(
                    event_id=event_id,
                    camera_name=camera_name,
                    event_type=event_type,
                    severity=severity,
                    description=description,
                    occurred_at=occurred_at,
                )
            except Exception as e:
                logger.error(f"Webhook notification error: {e}")
                results["webhook"] = f"error: {str(e)}"
        else:
            results["webhook"] = "demo_logged"

        return results

    def _send_telegram(
        self,
        camera_name: str,
        event_type: str,
        severity: str,
        description: str,
        occurred_at: str,
        snapshot_path: Optional[str] = None,
    ) -> str:
        caption = (
            f"🚨 *[AI HOSPITAL CAMERA - CẢNH BÁO SỰ CỐ]*\n\n"
            f"• *Mức độ:* `{severity.upper()}`\n"
            f"• *Camera:* `{camera_name}`\n"
            f"• *Loại sự kiện:* `{event_type.replace('_', ' ').upper()}`\n"
            f"• *Chi tiết:* {description}\n"
            f"• *Thời gian:* `{occurred_at}`\n\n"
            f"⚠️ _Vui lòng truy cập Dashboard trung tâm để xác minh và xử lý ngay!_"
        )

        if snapshot_path and os.path.isfile(snapshot_path):
            # Send photo with multipart
            url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
            boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
            body = []

            # chat_id field
            body.extend([
                f"--{boundary}",
                'Content-Disposition: form-data; name="chat_id"',
                "",
                str(self.chat_id),
            ])

            # caption field
            body.extend([
                f"--{boundary}",
                'Content-Disposition: form-data; name="caption"',
                "",
                caption,
            ])
            body.extend([
                f"--{boundary}",
                'Content-Disposition: form-data; name="parse_mode"',
                "",
                "Markdown",
            ])

            # photo file
            with open(snapshot_path, "rb") as f:
                photo_bytes = f.read()

            body.extend([
                f"--{boundary}",
                f'Content-Disposition: form-data; name="photo"; filename="{os.path.basename(snapshot_path)}"',
                "Content-Type: image/jpeg",
                "",
            ])

            header_bytes = "\r\n".join(body).encode("utf-8") + b"\r\n"
            footer_bytes = f"\r\n--{boundary}--\r\n".encode("utf-8")
            payload = header_bytes + photo_bytes + footer_bytes

            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return f"sent_photo (status {resp.status})"
        else:
            # Fallback to plain text message
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = json.dumps({
                "chat_id": self.chat_id,
                "text": caption,
                "parse_mode": "Markdown",
            }).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                return f"sent_message (status {resp.status})"

    def _send_webhook(
        self,
        event_id: str,
        camera_name: str,
        event_type: str,
        severity: str,
        description: str,
        occurred_at: str,
    ) -> str:
        payload = {
            "source": "AI_Hospital_Camera",
            "event_id": event_id,
            "camera_name": camera_name,
            "event_type": event_type,
            "severity": severity,
            "description": description,
            "timestamp": occurred_at,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.webhook_url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=8) as resp:
            return f"delivered (status {resp.status})"


notification_service = NotificationService()
