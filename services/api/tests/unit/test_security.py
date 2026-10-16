import pytest
from app.core.security import get_password_hash, verify_password, create_access_token, decode_token


def test_password_hashing():
    password = "TestPassword@123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_access_token_creation():
    token = create_access_token({"sub": "test-user-id"})
    assert token
    payload = decode_token(token)
    assert payload["sub"] == "test-user-id"
    assert payload["type"] == "access"


def test_invalid_token_returns_none():
    result = decode_token("not.a.valid.token")
    assert result is None


def test_expired_token_behavior():
    from datetime import timedelta
    token = create_access_token({"sub": "test"}, expires_delta=timedelta(seconds=-1))
    result = decode_token(token)
    assert result is None
