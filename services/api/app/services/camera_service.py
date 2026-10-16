import uuid
import socket
import time
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.camera import Camera, CameraStatus, CameraProtocol
from app.schemas.camera import CameraConnectionTestResult
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def test_camera_connection_impl(camera: Camera, db: Session) -> CameraConnectionTestResult:
    """Test a camera connection. Returns sanitized results (no credentials)."""
    tested_at = datetime.now(timezone.utc)
    
    if camera.protocol == CameraProtocol.MOCK or camera.is_demo:
        # Demo camera: simulate connection
        return CameraConnectionTestResult(
            camera_id=camera.id,
            success=True,
            latency_ms=15.0,
            error=None,
            stream_info={"codec": "h264", "resolution": "1920x1080", "fps": 25.0, "note": "SIMULATED"},
            tested_at=tested_at,
        )
    
    if not camera.ip_address:
        return CameraConnectionTestResult(
            camera_id=camera.id,
            success=False,
            latency_ms=None,
            error="No IP address configured",
            stream_info=None,
            tested_at=tested_at,
        )
    
    # Validate IP is in allowed subnets
    if not _is_allowed_ip(camera.ip_address):
        return CameraConnectionTestResult(
            camera_id=camera.id,
            success=False,
            latency_ms=None,
            error="Camera IP not in allowed subnet",
            stream_info=None,
            tested_at=tested_at,
        )
    
    # TCP reachability test
    port = camera.port or 554  # default RTSP port
    start = time.monotonic()
    try:
        with socket.create_connection((camera.ip_address, port), timeout=5.0):
            latency_ms = (time.monotonic() - start) * 1000
            return CameraConnectionTestResult(
                camera_id=camera.id,
                success=True,
                latency_ms=latency_ms,
                error=None,
                stream_info={"host": camera.ip_address, "port": port, "method": "tcp_connect"},
                tested_at=tested_at,
            )
    except socket.timeout:
        return CameraConnectionTestResult(
            camera_id=camera.id,
            success=False,
            latency_ms=None,
            error=f"Connection timed out to {camera.ip_address}:{port}",  # No credentials
            stream_info=None,
            tested_at=tested_at,
        )
    except OSError as e:
        return CameraConnectionTestResult(
            camera_id=camera.id,
            success=False,
            latency_ms=None,
            error=f"Connection failed: {type(e).__name__}",  # No credentials in error
            stream_info=None,
            tested_at=tested_at,
        )


def _is_allowed_ip(ip: str) -> bool:
    """Check if an IP is in the configured allowed subnets."""
    import ipaddress
    try:
        addr = ipaddress.ip_address(ip)
        for subnet in settings.CAMERA_ALLOWED_SUBNETS:
            if addr in ipaddress.ip_network(subnet, strict=False):
                return True
        # Also allow loopback for dev
        return addr.is_loopback
    except ValueError:
        return False


# In-memory buffer for edge-ingested camera frames: camera_id -> (numpy_frame, timestamp)
latest_camera_frames: dict = {}


def _norm_id(cam_id) -> str:
    return str(cam_id).replace("-", "").lower()


def store_camera_frame(camera_id, frame) -> None:
    """Store latest ingested frame from an edge camera pusher."""
    key = _norm_id(camera_id)
    latest_camera_frames[key] = (frame, time.time())


def get_latest_camera_frame(camera_id, max_age_seconds: float = 10.0):
    """Retrieve the latest frame if it was received within max_age_seconds."""
    key = _norm_id(camera_id)
    data = latest_camera_frames.get(key)
    if not data:
        return None
    frame, ts = data
    if time.time() - ts > max_age_seconds:
        return None
    return frame


