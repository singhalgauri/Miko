# Owner: Person 4
# Purpose: Smoke test for health check endpoint
# TODO(person4): Add health checks for database and vector store connectivity

from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_endpoint():
    """Verify GET /health returns status ok and app name Miko."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "Miko"
