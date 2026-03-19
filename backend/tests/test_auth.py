"""
Tests for authentication endpoints.
"""
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_login_returns_token():
    """Test that login returns an access token with hardcoded credentials."""
    response = client.post(
        "/api/auth/login",
        data={"username": "user", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_login_success_hardcoded():
    """Test successful login with hardcoded credentials."""
    response = client.post(
        "/api/auth/login",
        data={"username": "user", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    # Verify token is valid and contains correct subject
    token = data["access_token"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user"


def test_login_failure_wrong_password():
    """Test login fails with incorrect password."""
    response = client.post(
        "/api/auth/login",
        data={"username": "user", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_failure_wrong_username():
    """Test login fails with non-existent username."""
    response = client.post(
        "/api/auth/login",
        data={"username": "nonexistent", "password": "password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_get_current_user_with_valid_token():
    """Test accessing protected endpoint with valid token."""
    # Create the hardcoded user in the database first using UserService
    from src.services.user_service import UserService

    db = TestingSessionLocal()
    try:
        existing = UserService.get_by_username(db, "user")
        if not existing:
            UserService.create_user(db, username="user", password="password")
        db.commit()
    finally:
        db.close()

    # First login to get token
    login_response = client.post(
        "/api/auth/login",
        data={"username": "user", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user"
    assert data["is_active"] is True


def test_get_current_user_without_token():
    """Test accessing protected endpoint without token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_get_current_user_with_invalid_token():
    """Test accessing protected endpoint with malformed token."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_register_new_user():
    """Test successful user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data

    # Verify we can login with new user
    login_response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert login_response.status_code == 200


def test_register_duplicate_username():
    """Test registration fails with existing username."""
    # Register first user
    client.post(
        "/api/auth/register",
        json={"username": "duplicateuser", "password": "password1"}
    )

    # Try to register same username again
    response = client.post(
        "/api/auth/register",
        json={"username": "duplicateuser", "password": "password2"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_token_expiration():
    """Test that tokens have correct expiration."""
    login_response = client.post(
        "/api/auth/login",
        data={"username": "user", "password": "password"}
    )
    token = login_response.json()["access_token"]

    # Decode token to check expiration (without verification)
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={"verify_exp": False}
    )
    assert "exp" in payload

    # Verify token would be valid for expected duration
    from datetime import datetime
    exp_timestamp = payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    now = datetime.utcnow()
    time_diff = exp_datetime - now

    # Should be approximately ACCESS_TOKEN_EXPIRE_MINUTES in the future
    expected_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    # Allow 60 second tolerance for test execution time
    assert abs(time_diff.total_seconds() - expected_seconds) < 60


def test_protected_routes_require_auth():
    """Test that all protected routes require authentication."""
    protected_routes = [
        "/api/auth/me",
    ]

    for route in protected_routes:
        response = client.get(route)
        if response.status_code != 404:  # Ignore routes that don't exist yet
            assert response.status_code == 401, f"Route {route} should require auth"