import os
import uuid
import pytest
from app.services.ai_worker import ai_worker, point_in_polygon
from app.models.camera import Camera, CameraStatus, CameraProtocol
from app.models.ai import AIRule, AIRuleType


def test_point_in_polygon():
    polygon = [
        {"x": 0.1, "y": 0.1},
        {"x": 0.5, "y": 0.1},
        {"x": 0.5, "y": 0.5},
        {"x": 0.1, "y": 0.5},
    ]
    # Point inside
    assert point_in_polygon(0.3, 0.3, polygon) is True
    # Point outside
    assert point_in_polygon(0.8, 0.8, polygon) is False


def test_ai_worker_scan_and_snapshot(db):
    cam = Camera(
        id=uuid.uuid4(),
        name="Test Camera ER",
        protocol=CameraProtocol.MOCK,
        status=CameraStatus.ONLINE,
        is_active=True,
        ai_enabled=True,
    )
    db.add(cam)
    db.commit()

    frame = ai_worker.generate_synthetic_hospital_frame(cam)
    assert frame is not None
    assert frame.shape == (720, 1280, 3)

    # Process frame against rules
    pairs = ai_worker.process_camera_frame(cam, frame, db)
    assert isinstance(pairs, list)
