"""
Simplified integration tests for FastAPI service.

Tests end-to-end API functionality without complex simulation dependencies.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def simple_circuit_data():
    """Simple circuit data that we know works."""
    return {
        "name": "Simple Test Circuit",
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
                "negative_node": "0",
                "value": "1k",
            },
        ],
    }


class TestAPIIntegration:
    """Test complete API workflow integration."""

    def test_complete_api_workflow(self, client, simple_circuit_data):
        """Test complete API workflow: create → simulate → status → list."""

        # 1. Create circuit
        create_response = client.post("/api/circuits", json=simple_circuit_data)
        assert create_response.status_code == 201

        circuit = create_response.json()
        circuit_id = circuit["id"]

        # 2. List circuits (should include our circuit)
        list_response = client.get("/api/circuits")
        assert list_response.status_code == 200

        circuits = list_response.json()
        assert circuits["total"] >= 1
        circuit_ids = [c["id"] for c in circuits["circuits"]]
        assert circuit_id in circuit_ids

        # 3. Get specific circuit
        get_response = client.get(f"/api/circuits/{circuit_id}")
        assert get_response.status_code == 200

        circuit_details = get_response.json()
        assert circuit_details["id"] == circuit_id
        assert circuit_details["name"] == simple_circuit_data["name"]

        # 4. Start simulation
        sim_request = {"type": "dc", "parameters": {"analysis": "operating_point"}, "priority": 5}

        sim_response = client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request)
        assert sim_response.status_code == 202

        simulation = sim_response.json()
        job_id = simulation["job_id"]
        assert simulation["circuit_id"] == circuit_id

        # 5. Get simulation status
        status_response = client.get(f"/api/simulations/{job_id}")
        assert status_response.status_code == 200

        status = status_response.json()
        assert status["job_id"] == job_id
        assert status["circuit_id"] == circuit_id
        assert status["type"] == "dc"

        # 6. List simulations (should include our job)
        sims_response = client.get("/api/simulations")
        assert sims_response.status_code == 200

        simulations = sims_response.json()
        assert simulations["total"] >= 1
        job_ids = [s["job_id"] for s in simulations["simulations"]]
        assert job_id in job_ids

        # 7. Attempt to get results (may or may not be ready)
        results_response = client.get(f"/api/simulations/{job_id}/results")
        # Should either have results (200) or simulation not complete (409)
        assert results_response.status_code in [200, 409]

    def test_websocket_basic_integration(self, client, simple_circuit_data):
        """Test basic WebSocket integration workflow."""

        # Create circuit and simulation
        create_response = client.post("/api/circuits", json=simple_circuit_data)
        circuit_id = create_response.json()["id"]

        sim_response = client.post(
            f"/api/circuits/{circuit_id}/simulate",
            json={"type": "dc", "parameters": {}, "priority": 5},
        )
        job_id = sim_response.json()["job_id"]

        # Test WebSocket connection and basic communication
        with client.websocket_connect(f"/ws/simulation/{job_id}") as websocket:
            # Should receive connection message
            initial_msg = websocket.receive_json()
            assert initial_msg["type"] == "connection"
            assert initial_msg["job_id"] == job_id

            # Send ping, receive pong
            websocket.send_json({"type": "ping"})
            pong_msg = websocket.receive_json()
            assert pong_msg["type"] == "pong"

    def test_api_error_handling_integration(self, client):
        """Test comprehensive error handling across the API."""

        # 1. Invalid circuit creation
        invalid_data = {"name": "", "components": []}
        response = client.post("/api/circuits", json=invalid_data)
        assert response.status_code == 422

        # 2. Non-existent circuit operations
        fake_id = "550e8400-e29b-41d4-a716-446655440000"

        get_response = client.get(f"/api/circuits/{fake_id}")
        assert get_response.status_code == 404

        delete_response = client.delete(f"/api/circuits/{fake_id}")
        assert delete_response.status_code == 404

        sim_response = client.post(
            f"/api/circuits/{fake_id}/simulate", json={"type": "dc", "parameters": {}}
        )
        assert sim_response.status_code == 404

        # 3. Non-existent simulation operations
        fake_job_id = "123e4567-e89b-12d3-a456-426614174000"

        status_response = client.get(f"/api/simulations/{fake_job_id}")
        assert status_response.status_code == 404

        results_response = client.get(f"/api/simulations/{fake_job_id}/results")
        assert results_response.status_code == 404

        cancel_response = client.delete(f"/api/simulations/{fake_job_id}")
        assert cancel_response.status_code == 404

    def test_api_pagination_integration(self, client, simple_circuit_data):
        """Test pagination across multiple API endpoints."""

        # Create multiple circuits
        circuit_ids = []
        for i in range(5):
            data = simple_circuit_data.copy()
            data["name"] = f"Circuit {i+1}"

            response = client.post("/api/circuits", json=data)
            circuit_ids.append(response.json()["id"])

        # Test circuit pagination
        response = client.get("/api/circuits?limit=2")
        data = response.json()

        assert len(data["circuits"]) <= 2
        assert data["total"] >= 5
        assert data["limit"] == 2

        # Start simulations for pagination testing
        job_ids = []
        for circuit_id in circuit_ids[:3]:
            sim_response = client.post(
                f"/api/circuits/{circuit_id}/simulate",
                json={"type": "dc", "parameters": {}, "priority": 5},
            )
            job_ids.append(sim_response.json()["job_id"])

        # Test simulation pagination
        response = client.get("/api/simulations?limit=2")
        sim_data = response.json()

        assert len(sim_data["simulations"]) <= 2
        assert sim_data["total"] >= 3

    def test_api_documentation_integration(self, client):
        """Test that all documentation endpoints are accessible."""

        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema

        # Check that our endpoints are documented
        paths = schema["paths"]
        expected_paths = [
            "/api/circuits",
            "/api/circuits/{circuit_id}",
            "/api/circuits/{circuit_id}/simulate",
            "/api/simulations/{job_id}",
            "/api/simulations/{job_id}/results",
            "/health",
        ]

        for path in expected_paths:
            assert path in paths

        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200

        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_multiple_clients_same_job_websocket(self, client, simple_circuit_data):
        """Test multiple WebSocket clients for same simulation job."""

        # Create circuit and start simulation
        create_response = client.post("/api/circuits", json=simple_circuit_data)
        circuit_id = create_response.json()["id"]

        sim_response = client.post(
            f"/api/circuits/{circuit_id}/simulate",
            json={"type": "dc", "parameters": {}, "priority": 5},
        )
        job_id = sim_response.json()["job_id"]

        # Connect two WebSocket clients
        with client.websocket_connect(f"/ws/simulation/{job_id}") as ws1:
            with client.websocket_connect(f"/ws/simulation/{job_id}") as ws2:
                # Both should receive connection messages
                msg1 = ws1.receive_json()
                msg2 = ws2.receive_json()

                assert msg1["type"] == "connection"
                assert msg2["type"] == "connection"
                assert msg1["job_id"] == msg2["job_id"] == job_id
