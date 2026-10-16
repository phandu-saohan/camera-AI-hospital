import pytest
from app.models.camera import Camera, CameraProtocol


def test_create_demo_camera(client, auth_headers, db):
    response = client.post("/api/v1/cameras", json={
        "name": "Test Camera Demo",
        "protocol": "mock",
        "is_demo": True,
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Camera Demo"
    assert data["is_demo"] is True
    # Ensure no sensitive data leaked
    assert "rtsp_url" not in data
    assert "password" not in data
    assert "username" not in data
    assert "credential" not in str(data).lower()


def test_list_cameras(client, auth_headers):
    response = client.get("/api/v1/cameras", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


def test_get_camera_not_found(client, auth_headers):
    import uuid
    response = client.get(f"/api/v1/cameras/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404


def test_camera_connection_test_demo(client, auth_headers, db):
    # Create demo camera
    create_resp = client.post("/api/v1/cameras", json={
        "name": "Test Conn Camera",
        "protocol": "mock",
        "is_demo": True,
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    camera_id = create_resp.json()["id"]
    
    # Test connection
    test_resp = client.post(f"/api/v1/cameras/{camera_id}/test-connection", headers=auth_headers)
    assert test_resp.status_code == 200
    result = test_resp.json()
    assert result["success"] is True
    # Ensure no credentials exposed
    assert "password" not in str(result)
    assert "rtsp://" not in str(result) or "***" in str(result)


def test_invalid_rtsp_url_rejected(client, auth_headers):
    response = client.post("/api/v1/cameras", json={
        "name": "Bad Camera",
        "rtsp_main_url": "http://not-rtsp.com/stream",  # invalid - should be rejected
    }, headers=auth_headers)
    assert response.status_code == 422


def test_delete_camera_soft_delete(client, auth_headers, db):
    create_resp = client.post("/api/v1/cameras", json={
        "name": "Camera to Delete",
        "protocol": "mock",
        "is_demo": True,
    }, headers=auth_headers)
    camera_id = create_resp.json()["id"]
    
    del_resp = client.delete(f"/api/v1/cameras/{camera_id}", headers=auth_headers)
    assert del_resp.status_code == 204
    
    # Should not be retrievable
    get_resp = client.get(f"/api/v1/cameras/{camera_id}", headers=auth_headers)
    assert get_resp.status_code == 404
    
    # But should still exist in DB (soft delete)
    import uuid as _uuid
    cam = db.query(Camera).filter(Camera.id == _uuid.UUID(camera_id)).first()
    assert cam is not None
    assert cam.deleted_at is not None
