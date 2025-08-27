"""
Tests for FastAPI web service.

Test-driven development approach - tests written first to define behavior.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


def test_app_health_check(client):
    """Test basic health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "circuit-simulation-api"}


def test_api_root_redirect(client):
    """Test root endpoint redirects to docs."""
    response = client.get("/")
    assert response.status_code == 200
    assert "docs" in response.json()["message"]


def test_openapi_docs_available(client):
    """Test OpenAPI documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
