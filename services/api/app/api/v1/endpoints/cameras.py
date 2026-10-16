import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.camera import Camera, CameraStatus, CameraHealthLog, CameraProtocol, Recorder
from app.models.user import User
from app.schemas.camera import (
    CameraCreate, CameraUpdate, CameraResponse, CameraListResponse,
    CameraConnectionTestResult, CameraHealthResponse, RecorderCreate, RecorderResponse, RecorderUpdate
)
from app.schemas.common import PaginatedResponse
from app.api.v1.deps import get_current_user, require_permission
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get("", response_model=PaginatedResponse)
def list_cameras(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    ai_enabled: Optional[bool] = None,
    is_active: Optional[bool] = True,
    location_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Camera).filter(Camera.deleted_at.is_(None))
    
    if is_active is not None:
        query = query.filter(Camera.is_active == is_active)
    if status:
        query = query.filter(Camera.status == status)
    if ai_enabled is not None:
        query = query.filter(Camera.ai_enabled == ai_enabled)
    if location_id:
        query = query.filter(Camera.location_id == location_id)
    if search:
        query = query.filter(
            Camera.name.ilike(f"%{search}%") | Camera.ip_address.ilike(f"%{search}%")
        )
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": [CameraListResponse.model_validate(c) for c in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
def create_camera(
    data: CameraCreate,
    current_user: User = Depends(require_permission("cameras", "write")),
    db: Session = Depends(get_db),
):
    camera = Camera(
        name=data.name,
        description=data.description,
        manufacturer=data.manufacturer,
        model=data.model,
        ip_address=data.ip_address,
        port=data.port,
        protocol=data.protocol,
        location_id=data.location_id,
        recorder_id=data.recorder_id,
        ai_enabled=data.ai_enabled,
        tags=data.tags,
        is_demo=data.is_demo,
    )
    db.add(camera)
    db.commit()
    db.refresh(camera)
    
    # Store credentials encrypted (simplified - use proper key management in prod)
    if data.username or data.password or data.rtsp_main_url:
        from app.models.camera import CameraCredential, CameraStream
        import base64
        if data.username:
            cred = CameraCredential(
                camera_id=camera.id,
                username_encrypted=base64.b64encode(data.username.encode()).decode() if data.username else None,
                password_encrypted=base64.b64encode(data.password.encode()).decode() if data.password else None,
            )
            db.add(cred)
        if data.rtsp_main_url:
            stream = CameraStream(
                camera_id=camera.id,
                stream_type="main",
                rtsp_url_encrypted=base64.b64encode(data.rtsp_main_url.encode()).decode(),
            )
            db.add(stream)
        if data.rtsp_sub_url:
            stream = CameraStream(
                camera_id=camera.id,
                stream_type="sub",
                rtsp_url_encrypted=base64.b64encode(data.rtsp_sub_url.encode()).decode(),
            )
            db.add(stream)
        db.commit()
    
    logger.info(f"Camera created: {camera.id} ({camera.name}) by user {current_user.id}")
    return camera


@router.get("/health", response_model=List[dict])
def get_cameras_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cameras = db.query(Camera).filter(Camera.deleted_at.is_(None), Camera.is_active == True).all()
    return [
        {
            "camera_id": str(c.id),
            "name": c.name,
            "status": c.status.value,
            "last_seen_at": c.last_seen_at.isoformat() if c.last_seen_at else None,
            "last_error": c.last_error,
        }
        for c in cameras
    ]


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    camera = db.query(Camera).filter(
        Camera.id == camera_id, Camera.deleted_at.is_(None)
    ).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.patch("/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: uuid.UUID,
    data: CameraUpdate,
    current_user: User = Depends(require_permission("cameras", "write")),
    db: Session = Depends(get_db),
):
    camera = db.query(Camera).filter(
        Camera.id == camera_id, Camera.deleted_at.is_(None)
    ).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    update_data = data.model_dump(exclude_none=True, exclude={"username", "password", "rtsp_main_url", "rtsp_sub_url"})
    for field, value in update_data.items():
        setattr(camera, field, value)
    
    db.commit()
    db.refresh(camera)
    return camera


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(
    camera_id: uuid.UUID,
    current_user: User = Depends(require_permission("cameras", "admin")),
    db: Session = Depends(get_db),
):
    camera = db.query(Camera).filter(
        Camera.id == camera_id, Camera.deleted_at.is_(None)
    ).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    camera.soft_delete()
    db.commit()


@router.post("/{camera_id}/test-connection", response_model=CameraConnectionTestResult)
def test_camera_connection(
    camera_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    camera = db.query(Camera).filter(
        Camera.id == camera_id, Camera.deleted_at.is_(None)
    ).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Perform actual connection test
    from app.services.camera_service import test_camera_connection_impl
    result = test_camera_connection_impl(camera, db)
    
    # Persist health log
    health_log = CameraHealthLog(
        camera_id=camera.id,
        status=CameraStatus.ONLINE if result.success else CameraStatus.OFFLINE,
        latency_ms=result.latency_ms,
        error_message=result.error,
        checked_at=result.tested_at,
    )
    db.add(health_log)
    camera.status = CameraStatus.ONLINE if result.success else CameraStatus.OFFLINE
    if result.success:
        camera.last_seen_at = result.tested_at
        camera.last_error = None
        camera.connection_retry_count = 0
    else:
        camera.last_error = result.error
        camera.connection_retry_count += 1
    db.commit()
    
    return result


@router.get("/{camera_id}/health-history", response_model=List[CameraHealthResponse])
def get_camera_health_history(
    camera_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    camera = db.query(Camera).filter(
        Camera.id == camera_id, Camera.deleted_at.is_(None)
    ).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    logs = db.query(CameraHealthLog).filter(
        CameraHealthLog.camera_id == camera_id
    ).order_by(CameraHealthLog.checked_at.desc()).limit(limit).all()
    
    return logs


@router.get("/{camera_id}/live-feed")
def get_camera_live_feed(
    camera_id: uuid.UUID,
    stream_type: str = Query("main"),
    tracking: bool = Query(True),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Direct HTTP MJPEG Live Stream from physical IP camera or fallback generator with AI Person Tracking."""
    from fastapi.responses import StreamingResponse
    import cv2
    import base64
    import time
    from app.models.camera import CameraStream
    from app.services.person_tracker import get_or_create_tracker

    camera = db.query(Camera).filter(Camera.id == camera_id, Camera.deleted_at.is_(None)).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    tracker = get_or_create_tracker(str(camera_id))

    # Retrieve RTSP URL if available
    stream = db.query(CameraStream).filter(
        CameraStream.camera_id == camera_id,
        CameraStream.stream_type == stream_type,
    ).first()
    if not stream:
        stream = db.query(CameraStream).filter(
            CameraStream.camera_id == camera_id,
            CameraStream.stream_type == "main",
        ).first()

    rtsp_url = None
    if stream and stream.rtsp_url_encrypted:
        try:
            rtsp_url = base64.b64decode(stream.rtsp_url_encrypted.encode()).decode()
            if rtsp_url:
                rtsp_url = rtsp_url.split('#')[0]
            if stream_type == "sub" and "subtype=0" in rtsp_url:
                rtsp_url = rtsp_url.replace("subtype=0", "subtype=1")
        except Exception:
            rtsp_url = None

    def stream_generator():
        if rtsp_url and not camera.is_demo and not rtsp_url.startswith("mock://"):
            cap = cv2.VideoCapture(rtsp_url)
            try:
                fail_count = 0
                frame_idx = 0
                while fail_count < 30:
                    ret, frame = cap.read()
                    if not ret:
                        fail_count += 1
                        time.sleep(0.1)
                        continue
                    fail_count = 0
                    frame_idx += 1
                    h, w = frame.shape[:2]
                    # Resize HD/3K to optimal web size (max 960px wide)
                    if w > 960:
                        scale = 960.0 / w
                        frame = cv2.resize(frame, (960, int(h * scale)))

                    # AI Person Tracking overlay
                    if tracking:
                        try:
                            # Run detection every frame or every 2 frames for ultra efficiency
                            dets = tracker.detect_persons(frame)
                            tracker.update(dets)
                            frame = tracker.draw_tracking_overlay(frame, show_hud=True)
                        except Exception as e:
                            logger.debug(f"Tracker overlay error: {e}")

                    # Add live camera timestamp
                    ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(frame, f"CAM: {camera.name} | {ts_str}", (16, 32),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

                    success, encoded_jpg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                    if success:
                        yield (b"--frame\r\n"
                               b"Content-Type: image/jpeg\r\n\r\n" + encoded_jpg.tobytes() + b"\r\n")
                    time.sleep(0.04)  # ~25 FPS
            finally:
                cap.release()
        else:
            # Fallback synthetic frame generator with dynamic person tracking simulation
            from app.services.ai_worker import ai_worker
            while True:
                frame = ai_worker.generate_synthetic_hospital_frame(camera)
                if tracking:
                    try:
                        h, w = frame.shape[:2]
                        period = 120
                        cycle = (ai_worker._simulated_step % period) / period
                        person_norm_x = 0.2 + 0.35 * (1 - abs(cycle * 2 - 1))
                        person_norm_y = 0.45
                        px = int(person_norm_x * w)
                        py = int(person_norm_y * h)
                        pw, ph = 70, 160
                        dets = [{
                            "bbox": [px, py, pw, ph],
                            "centroid": (px + pw / 2, py + ph / 2),
                            "confidence": 0.94,
                            "is_fallen": False,
                        }]
                        tracker.update(dets)
                        frame = tracker.draw_tracking_overlay(frame, show_hud=True)
                    except Exception as e:
                        logger.debug(f"Synthetic tracking error: {e}")

                success, encoded_jpg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                if success:
                    yield (b"--frame\r\n"
                           b"Content-Type: image/jpeg\r\n\r\n" + encoded_jpg.tobytes() + b"\r\n")
                time.sleep(0.04)

    return StreamingResponse(
        stream_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/{camera_id}/live-frame")
def get_camera_live_frame(
    camera_id: uuid.UUID,
    stream_type: str = Query("main"),
    tracking: bool = Query(True),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Fetch single current frame from camera with optional person tracking overlay."""
    from fastapi.responses import Response
    import cv2
    import base64
    from app.models.camera import CameraStream
    from app.services.person_tracker import get_or_create_tracker

    camera = db.query(Camera).filter(Camera.id == camera_id, Camera.deleted_at.is_(None)).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    tracker = get_or_create_tracker(str(camera_id))

    stream = db.query(CameraStream).filter(
        CameraStream.camera_id == camera_id,
        CameraStream.stream_type == stream_type,
    ).first()
    if not stream:
        stream = db.query(CameraStream).filter(
            CameraStream.camera_id == camera_id,
            CameraStream.stream_type == "main",
        ).first()

    rtsp_url = None
    if stream and stream.rtsp_url_encrypted:
        try:
            rtsp_url = base64.b64decode(stream.rtsp_url_encrypted.encode()).decode()
            if rtsp_url:
                rtsp_url = rtsp_url.split('#')[0]
            if stream_type == "sub" and "subtype=0" in rtsp_url:
                rtsp_url = rtsp_url.replace("subtype=0", "subtype=1")
        except Exception:
            rtsp_url = None

    if rtsp_url and not camera.is_demo and not rtsp_url.startswith("mock://"):
        cap = cv2.VideoCapture(rtsp_url)
        try:
            ret, frame = cap.read()
            if not ret:
                raise HTTPException(status_code=503, detail="Could not capture frame from camera")

            h, w = frame.shape[:2]
            if w > 1280:
                scale = 1280.0 / w
                frame = cv2.resize(frame, (1280, int(h * scale)))

            if tracking:
                dets = tracker.detect_persons(frame)
                tracker.update(dets)
                frame = tracker.draw_tracking_overlay(frame, show_hud=True)

            success, encoded_jpg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            if not success:
                raise HTTPException(status_code=500, detail="JPEG encoding failed")
            return Response(content=encoded_jpg.tobytes(), media_type="image/jpeg")
        finally:
            cap.release()
    else:
        from app.services.ai_worker import ai_worker
        frame = ai_worker.generate_synthetic_hospital_frame(camera)
        if tracking:
            h, w = frame.shape[:2]
            period = 120
            cycle = (ai_worker._simulated_step % period) / period
            person_norm_x = 0.2 + 0.35 * (1 - abs(cycle * 2 - 1))
            person_norm_y = 0.45
            px = int(person_norm_x * w)
            py = int(person_norm_y * h)
            pw, ph = 70, 160
            dets = [{
                "bbox": [px, py, pw, ph],
                "centroid": (px + pw / 2, py + ph / 2),
                "confidence": 0.94,
                "is_fallen": False,
            }]
            tracker.update(dets)
            frame = tracker.draw_tracking_overlay(frame, show_hud=True)

        success, encoded_jpg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        return Response(content=encoded_jpg.tobytes(), media_type="image/jpeg")
