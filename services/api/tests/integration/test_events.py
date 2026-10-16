import pytest
from datetime import datetime, timezone
import uuid
from app.models.event import AIEvent, EventStatus, EventSeverity


def test_create_event_and_list(client, auth_headers, db):
    # Create a camera first
    cam_resp = client.post("/api/v1/cameras", json={
        "name": "Event Test Camera",
        "protocol": "mock",
        "is_demo": True,
    }, headers=auth_headers)
    assert cam_resp.status_code == 201
    camera_id = cam_resp.json()["id"]

    # Directly insert event or test listing
    event = AIEvent(
        camera_id=uuid.UUID(camera_id),
        event_type="restricted_area",
        status=EventStatus.NEW,
        severity=EventSeverity.HIGH,
        confidence=0.88,
        description="Test restricted area entry",
        occurred_at=datetime.now(timezone.utc),
        is_simulated=True,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # List events
    resp = client.get("/api/v1/events", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any(e["id"] == str(event.id) for e in data["items"])

    # Get single event
    get_resp = client.get(f"/api/v1/events/{event.id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["event_type"] == "restricted_area"
    assert get_resp.json()["status"] == "new"


def test_event_acknowledge_and_resolve(client, auth_headers, admin_user, db):
    cam_resp = client.post("/api/v1/cameras", json={
        "name": "Ack Test Camera",
        "protocol": "mock",
        "is_demo": True,
    }, headers=auth_headers)
    camera_id = cam_resp.json()["id"]

    event = AIEvent(
        camera_id=uuid.UUID(camera_id),
        event_type="fall_detection",
        status=EventStatus.NEW,
        severity=EventSeverity.CRITICAL,
        confidence=0.75,
        description="Patient fall suspected",
        occurred_at=datetime.now(timezone.utc),
        is_simulated=True,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # 1. Acknowledge
    ack_resp = client.post(f"/api/v1/events/{event.id}/acknowledge", json={
        "note": "Điều dưỡng đang kiểm tra",
    }, headers=auth_headers)
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "acknowledged"

    # 2. Assign
    assign_resp = client.post(f"/api/v1/events/{event.id}/assign", json={
        "assignee_id": str(admin_user.id),
        "note": "Phân công cho bác sĩ trực",
    }, headers=auth_headers)
    assert assign_resp.status_code == 200
    assert assign_resp.json()["status"] == "assigned"

    # 3. Resolve as normal or false positive
    res_resp = client.post(f"/api/v1/events/{event.id}/resolve", json={
        "resolution": "Bệnh nhân trượt chân nhưng đã được hỗ trợ an toàn",
        "is_false_positive": False,
        "note": "Đã ghi hồ sơ",
    }, headers=auth_headers)
    assert res_resp.status_code == 200
    assert res_resp.json()["status"] == "resolved"
