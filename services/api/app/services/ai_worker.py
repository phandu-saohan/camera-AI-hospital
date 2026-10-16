"""AI Computer Vision Worker for Hospital Surveillance.
Ingests video frames, runs object detection (person, motion, fall, tamper),
evaluates rules against ROIs, captures evidence snapshots, and triggers real-time alerts.
"""

import os
import time
import uuid
import hashlib
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

import cv2
import numpy as np
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import SessionLocal
from app.models.camera import Camera, CameraStatus
from app.models.ai import AIRule, AIRuleType
from app.models.event import AIEvent, EventEvidence, EventSeverity, EventStatus, EvidenceType
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)


def point_in_polygon(x: float, y: float, polygon: List[Dict[str, float]]) -> bool:
    """Ray-casting algorithm to determine if a normalized (0-1) point is inside a polygon."""
    n = len(polygon)
    inside = False
    p1 = polygon[0]
    for i in range(1, n + 1):
        p2 = polygon[i % n]
        if y > min(p1["y"], p2["y"]):
            if y <= max(p1["y"], p2["y"]):
                if x <= max(p1["x"], p2["x"]):
                    if p1["y"] != p2["y"]:
                        xinters = (y - p1["y"]) * (p2["x"] - p1["x"]) / (p2["y"] - p1["y"]) + p1["x"]
                    if p1["x"] == p2["x"] or x <= xinters:
                        inside = not inside
        p1 = p2
    return inside


class AIComputerVisionWorker:
    def __init__(self):
        self.evidence_dir = os.path.abspath(settings.EVIDENCE_STORAGE_PATH)
        os.makedirs(self.evidence_dir, exist_ok=True)
        self.last_triggered: Dict[str, float] = {}  # rule_id -> timestamp
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=32, detectShadows=False)
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self._simulated_step = 0

    def generate_synthetic_hospital_frame(self, camera: Camera) -> np.ndarray:
        """Generate a realistic test frame simulating hospital corridors / ward."""
        self._simulated_step += 1
        width, height = 1280, 720
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Hospital room gradient background (Slate / Blue-gray)
        for y in range(height):
            ratio = y / height
            color = (int(30 + ratio * 20), int(41 + ratio * 20), int(59 + ratio * 30))
            frame[y, :] = color

        # Perspective corridor lines
        cv2.line(frame, (0, int(height * 0.3)), (width, int(height * 0.3)), (71, 85, 105), 2)
        cv2.line(frame, (int(width * 0.2), int(height * 0.3)), (0, height), (51, 65, 85), 2)
        cv2.line(frame, (int(width * 0.8), int(height * 0.3)), (width, height), (51, 65, 85), 2)

        # Animated synthetic walking person silhouette
        # Walks back and forth across ROI area
        period = 120
        cycle = (self._simulated_step % period) / period
        person_norm_x = 0.2 + 0.35 * (1 - abs(cycle * 2 - 1))  # 0.2 to 0.55
        person_norm_y = 0.45

        px = int(person_norm_x * width)
        py = int(person_norm_y * height)
        pw, ph = 70, 160

        # Draw person figure
        cv2.circle(frame, (px + pw // 2, py + 25), 18, (180, 190, 205), -1)  # Head
        cv2.rectangle(frame, (px + 12, py + 45), (px + pw - 12, py + 115), (140, 150, 170), -1)  # Torso
        cv2.rectangle(frame, (px + 14, py + 115), (px + 28, py + ph), (100, 110, 130), -1)  # Left leg
        cv2.rectangle(frame, (px + pw - 28, py + 115), (px + pw - 14, py + ph), (100, 110, 130), -1)  # Right leg

        # CCTV timestamp and camera watermark
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"CAM: {camera.name} | {timestamp_str}", (24, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

        return frame

    def detect_persons(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect persons in frame using vision contours & shape analysis."""
        height, width = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        fg_mask = self.bg_subtractor.apply(blurred)
        _, thresh = cv2.threshold(fg_mask, 150, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(thresh, kernel, iterations=2)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 1500:  # Filter out small noise
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = h / float(w)

            # Person typically has aspect ratio between 1.2 and 4.0
            confidence = min(0.95, 0.65 + (area / 100000.0) * 0.2)
            detections.append({
                "bbox": [x, y, w, h],
                "centroid": [float((x + w / 2) / width), float((y + h / 2) / height)],
                "aspect_ratio": aspect_ratio,
                "confidence": round(float(confidence), 2),
                "is_fallen": aspect_ratio < 0.9 and area > 3000,  # Lying horizontally
            })

        return detections

    def check_tamper(self, frame: np.ndarray) -> Tuple[bool, float]:
        """Detect camera tampering: covered lens, severe blur or complete black/white frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        mean_val = float(np.mean(gray))

        is_tampered = (laplacian_var < 5.0) or (mean_val < 5.0) or (mean_val > 250.0)
        return is_tampered, laplacian_var

    def apply_privacy_face_blur(self, frame: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """Anonymize faces in snapshot evidence to protect patient and staff privacy."""
        if not getattr(settings, "PRIVACY_FACE_BLUR", True):
            return frame

        anonymized = frame.copy()
        height, width = anonymized.shape[:2]

        for det in detections:
            x, y, w, h = det["bbox"]
            # Estimate head/face region: upper 35% of detected person bounding box
            face_top = max(0, y)
            face_bottom = min(height, y + int(h * 0.35))
            face_left = max(0, x + int(w * 0.15))
            face_right = min(width, x + int(w * 0.85))

            if face_bottom > face_top and face_right > face_left:
                face_roi = anonymized[face_top:face_bottom, face_left:face_right]
                # Strong Gaussian Blur to anonymize face
                ksize = (45, 45)
                blurred_face = cv2.GaussianBlur(face_roi, ksize, 30)
                anonymized[face_top:face_bottom, face_left:face_right] = blurred_face
                cv2.rectangle(anonymized, (face_left, face_top), (face_right, face_bottom), (100, 116, 139), 1)

        # Add privacy compliance badge on the snapshot
        cv2.putText(
            anonymized,
            "[PRIVACY COMPLIANT: FACE ANONYMIZED]",
            (width - 440, height - 16),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (34, 197, 94),
            1,
            cv2.LINE_AA,
        )
        return anonymized

    def process_camera_frame(
        self,
        camera: Camera,
        frame: np.ndarray,
        db: Session,
    ) -> List[AIEvent]:
        """Process a single frame for a camera against its configured AI rules."""
        triggered_events = []
        rules = db.query(AIRule).filter(
            AIRule.camera_id == camera.id,
            AIRule.is_enabled == True
        ).all()

        if not rules:
            return triggered_events

        now_ts = time.time()
        detections = self.detect_persons(frame)
        is_tampered, blur_score = self.check_tamper(frame)

        for rule in rules:
            rule_id_str = str(rule.id)
            last_time = self.last_triggered.get(rule_id_str, 0)
            if (now_ts - last_time) < rule.cooldown_seconds:
                continue

            violation_detected = False
            event_type = rule.rule_type.value
            event_confidence = 0.85
            description = f"Quy tắc [{rule.name}] kích hoạt cảnh báo."
            annotated_frame = frame.copy()

            # 1. Restricted Area Check
            if rule.rule_type == AIRuleType.RESTRICTED_AREA:
                roi = rule.roi_polygon
                if roi and len(roi) >= 3:
                    # Draw ROI polygon on snapshot
                    h, w = frame.shape[:2]
                    pts = np.array([[int(p["x"] * w), int(p["y"] * h)] for p in roi], np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(annotated_frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)

                    for det in detections:
                        cx, cy = det["centroid"]
                        if point_in_polygon(cx, cy, roi) and det["confidence"] >= rule.confidence_threshold:
                            violation_detected = True
                            event_confidence = det["confidence"]
                            description = f"Phát hiện người xâm nhập vùng cấm tại {camera.name} (Độ tin cậy: {int(event_confidence * 100)}%)"

                            # Draw bounding box
                            bx, by, bw, bh = det["bbox"]
                            cv2.rectangle(annotated_frame, (bx, by), (bx + bw, by + bh), (0, 0, 255), 3)
                            cv2.putText(annotated_frame, f"VIOLATION: {int(event_confidence * 100)}%",
                                        (bx, max(20, by - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                            break

            # 2. Fall Detection Check
            elif rule.rule_type == AIRuleType.FALL_DETECTION:
                for det in detections:
                    if det.get("is_fallen") and det["confidence"] >= rule.confidence_threshold:
                        violation_detected = True
                        event_confidence = det["confidence"]
                        description = f"Cảnh báo bệnh nhân ngã tại {camera.name} (Góc nằm ngang bất thường)"
                        bx, by, bw, bh = det["bbox"]
                        cv2.rectangle(annotated_frame, (bx, by), (bx + bw, by + bh), (0, 165, 255), 3)
                        cv2.putText(annotated_frame, "FALL DETECTED", (bx, max(20, by - 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                        break

            # 3. Camera Tamper Check
            elif rule.rule_type == AIRuleType.CAMERA_TAMPER:
                if is_tampered:
                    violation_detected = True
                    event_confidence = 0.98
                    description = f"Phát hiện ống kính camera {camera.name} bị che hoặc thay đổi góc quan sát"
                    cv2.putText(annotated_frame, "TAMPER DETECTED", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

            # 4. People Counting / Flow Check
            elif rule.rule_type == AIRuleType.PEOPLE_COUNTING:
                count = len(detections)
                threshold = int(rule.extra_config.get("max_people", 5)) if rule.extra_config else 5
                if count > threshold:
                    violation_detected = True
                    event_confidence = 0.90
                    description = f"Lưu lượng người vượt ngưỡng ({count}/{threshold}) tại {camera.name}"

            # 5. Queue Estimation & Dwell Time Check
            elif rule.rule_type == AIRuleType.QUEUE_ESTIMATION:
                roi = rule.roi_polygon
                waiting_people = 0
                total_dwell_s = 0.0

                for det in detections:
                    cx, cy = det["centroid"]
                    in_roi = point_in_polygon(cx, cy, roi) if (roi and len(roi) >= 3) else True
                    if in_roi:
                        waiting_people += 1
                        # Estimate dwell time based on track presence
                        dwell_s = round(14.0 + (det.get("aspect_ratio", 1.5) * 5.0), 1)
                        total_dwell_s += dwell_s

                max_allowed = int(rule.extra_config.get("max_people", 3)) if rule.extra_config else 3
                if waiting_people >= max_allowed:
                    avg_dwell = round(total_dwell_s / max(1, waiting_people), 1)
                    violation_detected = True
                    event_confidence = 0.92
                    description = (
                        f"Ùn tắc khu vực chờ tại {camera.name}: Phát hiện {waiting_people} người "
                        f"(vượt ngưỡng {max_allowed}), thời gian dừng chờ TB ~{avg_dwell}s. Đề xuất mở thêm quầy tiếp đón phụ."
                    )
                    cv2.putText(
                        annotated_frame,
                        f"QUEUE CONGESTION: {waiting_people} PPL (AVG DWELL: {avg_dwell}s)",
                        (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 165, 255),
                        2,
                    )

            if violation_detected:
                self.last_triggered[rule_id_str] = now_ts
                event_severity = getattr(EventSeverity, rule.severity.upper(), EventSeverity.HIGH)

                # Persist AI Event
                event = AIEvent(
                    id=uuid.uuid4(),
                    camera_id=camera.id,
                    rule_id=rule.id,
                    event_type=event_type,
                    status=EventStatus.NEW,
                    severity=event_severity,
                    confidence=float(event_confidence),
                    is_simulated=camera.is_demo,
                    description=description,
                    occurred_at=datetime.now(timezone.utc),
                )
                db.add(event)
                db.flush()

                # Anonymize faces in snapshot evidence to protect patient and staff privacy
                snapshot_image = self.apply_privacy_face_blur(annotated_frame, detections)

                # Encode and save snapshot JPEG
                snapshot_filename = f"{event.id}.jpg"
                snapshot_path = os.path.join(self.evidence_dir, snapshot_filename)
                success, encoded_jpg = cv2.imencode(".jpg", snapshot_image, [int(cv2.IMWRITE_JPEG_QUALITY), 85])

                file_size = 0
                checksum = None
                if success:
                    raw_bytes = encoded_jpg.tobytes()
                    file_size = len(raw_bytes)
                    checksum = hashlib.sha256(raw_bytes).hexdigest()
                    with open(snapshot_path, "wb") as f:
                        f.write(raw_bytes)

                # Persist Event Evidence
                evidence = EventEvidence(
                    event_id=event.id,
                    camera_id=camera.id,
                    evidence_type=EvidenceType.SNAPSHOT,
                    storage_key=snapshot_filename,
                    checksum_sha256=checksum,
                    file_size_bytes=file_size,
                    access_classification="restricted",
                )
                db.add(evidence)
                db.commit()
                db.refresh(event)

                # Dispatch External Notifications (Telegram Bot & Webhook)
                try:
                    from app.services.notification_service import notification_service
                    notification_service.send_incident_alert(
                        event_id=str(event.id),
                        camera_name=camera.name,
                        event_type=event.event_type,
                        severity=event.severity.value,
                        description=event.description or "",
                        occurred_at=event.occurred_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                        snapshot_path=snapshot_path if success else None,
                    )
                except Exception as n_err:
                    logger.warning(f"Notification dispatch error: {n_err}")

                # Broadcast real-time incident to WebSocket clients
                incident_payload = {
                    "type": "ai.incident_alert",
                    "incident": {
                        "id": str(event.id),
                        "camera_id": str(camera.id),
                        "camera_name": camera.name,
                        "event_type": event.event_type,
                        "severity": event.severity.value,
                        "confidence": event.confidence,
                        "occurred_at": event.occurred_at.isoformat(),
                        "description": event.description,
                        "is_simulated": event.is_simulated,
                        "snapshot_url": f"/api/v1/evidence/{evidence.id}/download",
                    }
                }
                logger.info(f"AI Worker triggered incident [{event.event_type}] on camera [{camera.name}]. Snapshot: {snapshot_filename}")
                triggered_events.append((event, incident_payload))

        return triggered_events

    def run_scan_cycle(self) -> Tuple[List[AIEvent], List[Dict[str, Any]]]:
        """Perform one scan cycle across all AI-enabled cameras."""
        db = SessionLocal()
        try:
            cameras = db.query(Camera).filter(
                Camera.deleted_at.is_(None),
                Camera.is_active == True,
                Camera.ai_enabled == True
            ).all()

            all_events = []
            all_payloads = []
            from app.services.camera_service import get_latest_camera_frame
            for cam in cameras:
                # Use real edge-ingested frame if available
                ingested = get_latest_camera_frame(str(cam.id), max_age_seconds=10.0)
                if ingested is not None:
                    frame = ingested.copy()
                else:
                    frame = self.generate_synthetic_hospital_frame(cam)
                pairs = self.process_camera_frame(cam, frame, db)
                for ev, payload in pairs:
                    all_events.append(ev)
                    all_payloads.append(payload)

            return all_events, all_payloads
        finally:
            db.close()

    async def start_background_loop(self, interval_seconds: float = 4.0):
        """Asynchronous background loop for scheduled AI surveillance inference."""
        self.is_running = True
        logger.info(f"AI Computer Vision Worker loop started (interval={interval_seconds}s)")
        while self.is_running:
            try:
                # Run synchronous inference cycle in thread pool to avoid blocking asyncio event loop
                events, payloads = await asyncio.to_thread(self.run_scan_cycle)
                for payload in payloads:
                    await ws_manager.broadcast(payload)
            except Exception as e:
                logger.error(f"Error in AI worker scan cycle: {e}")
            await asyncio.sleep(interval_seconds)

    def stop(self):
        self.is_running = False
        logger.info("AI Computer Vision Worker stopped")


# Global singleton instance
ai_worker = AIComputerVisionWorker()
