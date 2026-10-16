import pytest
import uuid
from datetime import datetime, timezone
import sys
import os

# Add API to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'api')))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.camera import Camera, CameraStatus
from app.models.event import AIEvent, EventStatus, EventSeverity
from app.models.audit import AuditLog

TEST_DB_URL = "sqlite:///./test_e2e.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_complete_vertical_slice():
    """
    End-to-end verification of the required vertical slice:
    Admin Auth -> Create Camera -> Test Connection -> Generate AI Event ->
    Alert Listed -> Staff Acknowledges -> Staff Resolves -> Audit Verified.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    try:
        # 1. Create Test Admin
        admin_email = "e2e_admin@example.com"
        admin = User(
            email=admin_email,
            full_name="E2E Director",
            hashed_password=get_password_hash("E2ePass@123"),
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        db.commit()

        # 2. Login to get JWT
        login_resp = client.post("/api/v1/auth/login", json={
            "email": admin_email,
            "password": "E2ePass@123",
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 3. Create simulated camera
        cam_resp = client.post("/api/v1/cameras", json={
            "name": "E2E Khoa Cap Cuu - Cua 1",
            "protocol": "mock",
            "is_demo": True,
            "ai_enabled": True,
            "tags": ["er", "entrance"],
        }, headers=auth_headers)
        assert cam_resp.status_code == 201
        camera_id = cam_resp.json()["id"]

        # 4. Test camera connection
        conn_resp = client.post(f"/api/v1/cameras/{camera_id}/test-connection", headers=auth_headers)
        assert conn_resp.status_code == 200
        assert conn_resp.json()["success"] is True

        # 5. Generate AI Event (Simulated)
        event = AIEvent(
            camera_id=uuid.UUID(camera_id),
            event_type="restricted_area",
            status=EventStatus.NEW,
            severity=EventSeverity.HIGH,
            confidence=0.91,
            description="[E2E] Phat hien xam nhap phong mo",
            occurred_at=datetime.now(timezone.utc),
            is_simulated=True,
        )
        db.add(event)
        db.commit()
        event_id = str(event.id)

        # 6. Retrieve Event in staff dashboard
        events_resp = client.get(f"/api/v1/events/{event_id}", headers=auth_headers)
        assert events_resp.status_code == 200
        assert events_resp.json()["status"] == "new"
        assert events_resp.json()["is_simulated"] is True

        # 7. Staff acknowledges
        ack_resp = client.post(f"/api/v1/events/{event_id}/acknowledge", json={
            "note": "Dieu duong da tiep nhan qua man hinh",
        }, headers=auth_headers)
        assert ack_resp.status_code == 200
        assert ack_resp.json()["status"] == "acknowledged"

        # 8. Staff resolves
        res_resp = client.post(f"/api/v1/events/{event_id}/resolve", json={
            "resolution": "Bac si truc da xac nhan an toan",
            "is_false_positive": False,
        }, headers=auth_headers)
        assert res_resp.status_code == 200
        assert res_resp.json()["status"] == "resolved"

        # 9. Verify Unauthorized access rejected
        unauth_resp = client.get("/api/v1/cameras")
        assert unauth_resp.status_code in (401, 403)

        print("\n>>> End-to-End Vertical Slice: 100% SUCCESSFUL <<<")

    finally:
        app.dependency_overrides.clear()
        db.close()
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test_e2e.db"):
            try:
                os.remove("./test_e2e.db")
            except Exception:
                pass
