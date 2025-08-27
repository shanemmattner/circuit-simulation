"""
Tests for simulation job API endpoints.

Tests simulation job creation, status monitoring, and result retrieval.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_circuit_data():
    """Sample circuit for simulation tests."""
    return {
        "name": "RC Filter",
        "components": [
            {
                "type": "voltage_source",
                "name": "V1",
                "positive_node": "1",
                "negative_node": "0",
                "value": "5V",
            },
            {
                "type": "resistor",
                "name": "R1",
                "positive_node": "1",
                "negative_node": "2",
                "value": "1k",
            },
            {
                "type": "capacitor",
                "name": "C1",
                "positive_node": "2",
                "negative_node": "0",
                "value": "1u",
            },
        ],
    }


class TestSimulationJobs:
    """Test simulation job management."""

    def test_start_dc_simulation(self, client, sample_circuit_data):
        """Test starting a DC simulation job."""
        # Create circuit first
        create_response = client.post("/api/circuits", json=sample_circuit_data)
        circuit_id = create_response.json()["id"]

        # Start simulation
        sim_request = {"type": "dc", "parameters": {"analysis": "operating_point"}, "priority": 5}

        response = client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request)

        assert response.status_code == 202  # Accepted (async)
        data = response.json()
        assert "job_id" in data
        assert data["circuit_id"] == circuit_id
        assert data["type"] == "dc"
        assert data["status"] == "pending"

    def test_start_transient_simulation(self, client, sample_circuit_data):
        """Test starting a transient simulation job."""
        # Create circuit first
        create_response = client.post("/api/circuits", json=sample_circuit_data)
        circuit_id = create_response.json()["id"]

        # Start transient simulation
        sim_request = {
            "type": "transient",
            "parameters": {"stop_time": 0.01, "step_time": 0.0001},
            "priority": 7,
        }

        response = client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request)

        assert response.status_code == 202
        data = response.json()
        assert data["type"] == "transient"
        assert data["priority"] == 7

    def test_start_simulation_invalid_circuit(self, client):
        """Test starting simulation on non-existent circuit fails."""
        sim_request = {"type": "dc", "parameters": {"analysis": "operating_point"}}

        response = client.post("/api/circuits/invalid-id/simulate", json=sim_request)
        assert response.status_code == 404

    def test_get_simulation_status(self, client, sample_circuit_data):
        """Test getting simulation job status."""
        # Create circuit and start simulation
        create_response = client.post("/api/circuits", json=sample_circuit_data)
        circuit_id = create_response.json()["id"]

        sim_request = {"type": "dc", "parameters": {}}
        sim_response = client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request)
        job_id = sim_response.json()["job_id"]

        # Get status
        response = client.get(f"/api/simulations/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert "status" in data
        assert "progress" in data
        assert "created_at" in data

    def test_get_simulation_status_not_found(self, client):
        """Test getting status for non-existent job fails."""
        response = client.get("/api/simulations/invalid-job-id")
        assert response.status_code == 404

    def test_cancel_simulation(self, client, sample_circuit_data):
        """Test cancelling a simulation job."""
        # Create circuit and start simulation
        create_response = client.post("/api/circuits", json=sample_circuit_data)
        circuit_id = create_response.json()["id"]

        sim_request = {"type": "transient", "parameters": {"stop_time": 10.0}}  # Long simulation
        sim_response = client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request)
        job_id = sim_response.json()["job_id"]

        # Cancel simulation
        response = client.delete(f"/api/simulations/{job_id}")

        assert response.status_code == 204

        # Check status shows cancelled
        status_response = client.get(f"/api/simulations/{job_id}")
        assert status_response.json()["status"] == "cancelled"

    def test_cancel_simulation_not_found(self, client):
        """Test cancelling non-existent job fails."""
        response = client.delete("/api/simulations/invalid-job-id")
        assert response.status_code == 404

    def test_list_simulations(self, client, sample_circuit_data):
        """Test listing all simulation jobs."""
        # Create circuit and start multiple simulations
        create_response = client.post("/api/circuits", json=sample_circuit_data)
        circuit_id = create_response.json()["id"]

        sim_request1 = {"type": "dc", "parameters": {}}
        sim_request2 = {"type": "transient", "parameters": {"stop_time": 0.001}}

        client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request1)
        client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request2)

        # List simulations
        response = client.get("/api/simulations")

        assert response.status_code == 200
        data = response.json()
        assert "simulations" in data
        assert "total" in data
        assert len(data["simulations"]) >= 2
