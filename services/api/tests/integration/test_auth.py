import pytest


def test_login_success(client, admin_user):
    response = client.post("/api/v1/auth/login", json={
        "email": "test_admin@example.com",
        "password": "TestAdmin@123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, admin_user):
    response = client.post("/api/v1/auth/login", json={
        "email": "test_admin@example.com",
        "password": "WrongPassword",
    })
    assert response.status_code == 401


def test_login_wrong_email(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "nobody@nowhere.com",
        "password": "AnyPassword",
    })
    assert response.status_code == 401


def test_get_me(client, auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_admin@example.com"
    assert "hashed_password" not in data
    assert "password" not in data


def test_unauthorized_access(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)


def test_health_live(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"
