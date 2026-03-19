"""
Tests for hello world endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_hello_world():
    """Test the basic hello world endpoint."""
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_hello_name():
    """Test personalized hello endpoint."""
    response = client.get("/api/hello/John")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, John!"}


def test_echo_message():
    """Test echo endpoint with default repeat."""
    response = client.get("/api/hello/echo/test")
    assert response.status_code == 200
    data = response.json()
    assert data["original"] == "test"
    assert data["echoed"] == "test"
    assert data["repeat_count"] == 1


def test_echo_message_with_repeat():
    """Test echo endpoint with custom repeat count."""
    response = client.get("/api/hello/echo/test?repeat=3")
    assert response.status_code == 200
    data = response.json()
    assert data["original"] == "test"
    assert data["echoed"] == "test test test"
    assert data["repeat_count"] == 3


def test_echo_post():
    """Test echo endpoint via POST."""
    response = client.post("/api/hello/echo", json={"message": "test post"})
    assert response.status_code == 200
    data = response.json()
    assert data["method"] == "POST"
    assert data["message"] == "test post"


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_api_root():
    """Test the API root endpoint."""
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert "endpoints" in data
    assert "health" in data["endpoints"]
    assert "hello" in data["endpoints"]