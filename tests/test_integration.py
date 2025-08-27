"""
Integration tests for the complete FastAPI circuit simulation service.

Tests end-to-end workflows including circuit creation, simulation execution,
WebSocket updates, and result retrieval.
"""

import time

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def complex_circuit_data():
    """Circuit data for integration testing - simplified for reliability."""
    return {
        "name": "Integration Test Circuit",
        "description": "RC circuit for end-to-end testing",
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


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    def test_complete_dc_simulation_workflow(self, client, complex_circuit_data):
        """Test complete DC simulation workflow from creation to results."""

        # 1. Create circuit
        create_response = client.post("/api/circuits", json=complex_circuit_data)
        assert create_response.status_code == 201

        circuit = create_response.json()
        circuit_id = circuit["id"]
        assert circuit["name"] == complex_circuit_data["name"]
        assert circuit["component_count"] == 3

        # 2. Start DC simulation
        sim_request = {"type": "dc", "parameters": {"analysis": "operating_point"}, "priority": 8}

        sim_response = client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request)
        assert sim_response.status_code == 202

        simulation = sim_response.json()
        job_id = simulation["job_id"]
        assert simulation["type"] == "dc"
        assert simulation["circuit_id"] == circuit_id

        # 3. Monitor simulation status
        max_attempts = 10
        attempts = 0
        final_status = None

        while attempts < max_attempts:
            status_response = client.get(f"/api/simulations/{job_id}")
            assert status_response.status_code == 200

            status = status_response.json()
            final_status = status["status"]

            if final_status in ["completed", "failed"]:
                break

            time.sleep(0.1)  # Brief wait
            attempts += 1

        # 4. Verify simulation completed
        assert final_status == "completed", f"Simulation failed with status: {final_status}"

        # 5. Get simulation results
        results_response = client.get(f"/api/simulations/{job_id}/results")
        assert results_response.status_code == 200

        results = results_response.json()
        assert "voltages" in results
        assert "currents" in results
        assert "metadata" in results
        assert len(results["voltages"]) > 0  # Should have voltage data

        # 6. Verify circuit still exists
        circuit_response = client.get(f"/api/circuits/{circuit_id}")
        assert circuit_response.status_code == 200

        # 7. List all simulations - should include our job
        sims_response = client.get("/api/simulations")
        assert sims_response.status_code == 200

        sims_data = sims_response.json()
        assert sims_data["total"] >= 1
        job_ids = [sim["job_id"] for sim in sims_data["simulations"]]
        assert job_id in job_ids

    def test_complete_transient_simulation_workflow(self, client, complex_circuit_data):
        """Test complete transient simulation workflow."""

        # Create circuit
        create_response = client.post("/api/circuits", json=complex_circuit_data)
        circuit_id = create_response.json()["id"]

        # Start transient simulation
        sim_request = {
            "type": "transient",
            "parameters": {
                "stop_time": 0.001,  # 1ms simulation
                "step_time": 0.0001,  # 0.1ms steps
            },
            "priority": 9,
        }

        sim_response = client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request)
        assert sim_response.status_code == 202

        job_id = sim_response.json()["job_id"]

        # Wait for completion (transient takes longer)
        max_wait = 5.0  # 5 seconds max wait
        start_time = time.time()
        final_status = None

        while (time.time() - start_time) < max_wait:
            status_response = client.get(f"/api/simulations/{job_id}")
            status = status_response.json()
            final_status = status["status"]

            if final_status in ["completed", "failed"]:
                break

            time.sleep(0.2)

        assert final_status == "completed", "Transient simulation should complete"

        # Get results and verify time-domain data
        results_response = client.get(f"/api/simulations/{job_id}/results")
        results = results_response.json()

        assert "time" in results
        assert results["time"] is not None
        assert len(results["time"]) > 1  # Should have time series data

    def test_websocket_integration_workflow(self, client, complex_circuit_data):
        """Test WebSocket integration with simulation workflow."""

        # Create circuit
        create_response = client.post("/api/circuits", json=complex_circuit_data)
        circuit_id = create_response.json()["id"]

        # Start simulation
        sim_request = {"type": "dc", "parameters": {}, "priority": 7}

        sim_response = client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request)
        job_id = sim_response.json()["job_id"]

        # Test WebSocket connection
        messages_received = []

        with client.websocket_connect(f"/ws/simulation/{job_id}") as websocket:
            # Should receive initial connection message
            initial_msg = websocket.receive_json()
            messages_received.append(initial_msg)

            assert initial_msg["type"] == "connection"
            assert initial_msg["job_id"] == job_id

            # Send ping command
            ping_msg = {"type": "ping"}
            websocket.send_json(ping_msg)

            # Should receive pong response
            pong_msg = websocket.receive_json()
            messages_received.append(pong_msg)

            assert pong_msg["type"] == "pong"

            # Send status request
            status_msg = {"type": "command", "action": "status"}
            websocket.send_json(status_msg)

            # Should receive status update
            status_update = websocket.receive_json()
            messages_received.append(status_update)

            assert status_update["type"] == "status_update"
            assert "data" in status_update

        # Verify we received expected messages
        assert len(messages_received) >= 3
        message_types = [msg["type"] for msg in messages_received]
        assert "connection" in message_types
        assert "pong" in message_types
        assert "status_update" in message_types

    def test_concurrent_simulations_workflow(self, client, complex_circuit_data):
        """Test multiple concurrent simulations."""

        # Create circuit
        create_response = client.post("/api/circuits", json=complex_circuit_data)
        circuit_id = create_response.json()["id"]

        # Start multiple simulations concurrently
        job_ids = []

        for i in range(3):
            sim_request = {
                "type": "dc" if i % 2 == 0 else "transient",
                "parameters": {"stop_time": 0.001, "step_time": 0.0001} if i % 2 == 1 else {},
                "priority": 5 + i,
            }

            sim_response = client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request)
            assert sim_response.status_code == 202

            job_ids.append(sim_response.json()["job_id"])

        # Wait for all simulations to complete
        completed_jobs = []
        max_wait = 10.0  # 10 seconds total
        start_time = time.time()

        while len(completed_jobs) < len(job_ids) and (time.time() - start_time) < max_wait:
            for job_id in job_ids:
                if job_id not in completed_jobs:
                    status_response = client.get(f"/api/simulations/{job_id}")
                    status = status_response.json()

                    if status["status"] in ["completed", "failed"]:
                        completed_jobs.append(job_id)

            time.sleep(0.3)

        # Verify all jobs completed
        assert len(completed_jobs) == len(job_ids), "All concurrent simulations should complete"

        # Verify results are available for completed jobs
        for job_id in completed_jobs:
            status_response = client.get(f"/api/simulations/{job_id}")
            status = status_response.json()

            if status["status"] == "completed":
                results_response = client.get(f"/api/simulations/{job_id}/results")
                assert results_response.status_code == 200

    def test_error_handling_workflow(self, client):
        """Test error handling in various scenarios."""

        # 1. Test invalid circuit creation
        invalid_circuit = {"name": "", "components": []}  # Invalid empty name

        response = client.post("/api/circuits", json=invalid_circuit)
        assert response.status_code == 422

        # 2. Test simulation on non-existent circuit
        sim_request = {"type": "dc", "parameters": {}}
        response = client.post("/api/circuits/invalid-id/simulate", json=sim_request)
        assert response.status_code == 404

        # 3. Test getting non-existent simulation
        response = client.get("/api/simulations/invalid-job-id")
        assert response.status_code == 404

        # 4. Test getting results for non-existent job
        response = client.get("/api/simulations/invalid-job-id/results")
        assert response.status_code == 404

        # 5. Test WebSocket with invalid job ID
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/simulation/"):
                pass

    def test_api_documentation_endpoints(self, client):
        """Test that API documentation endpoints work."""

        # Test OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200

        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert "paths" in openapi_spec

        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200

        root_data = response.json()
        assert "message" in root_data
        assert "endpoints" in root_data
        assert "docs" in root_data["endpoints"]


class TestPerformanceAndLimits:
    """Test performance characteristics and limits."""

    def test_large_circuit_handling(self, client):
        """Test handling of larger circuits."""

        # Create a circuit with many components
        components = [
            {
                "type": "voltage_source",
                "name": "V1",
                "positive_node": "1",
                "negative_node": "0",
                "value": "12V",
            }
        ]

        # Add many resistors in series
        for i in range(2, 52):  # 50 resistors
            components.append(
                {
                    "type": "resistor",
                    "name": f"R{i-1}",
                    "positive_node": str(i - 1),
                    "negative_node": str(i),
                    "value": f"{i}k",
                }
            )

        # Final load resistor
        components.append(
            {
                "type": "resistor",
                "name": "RL",
                "positive_node": "51",
                "negative_node": "0",
                "value": "1k",
            }
        )

        large_circuit = {
            "name": "Large Circuit Test",
            "description": "Circuit with many components",
            "components": components,
        }

        # Should handle large circuit creation
        create_response = client.post("/api/circuits", json=large_circuit)
        assert create_response.status_code == 201

        circuit = create_response.json()
        assert circuit["component_count"] == len(components)

        # Should handle simulation of large circuit
        circuit_id = circuit["id"]
        sim_request = {"type": "dc", "parameters": {}, "priority": 10}

        sim_response = client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request)
        assert sim_response.status_code == 202

    def test_pagination_functionality(self, client, complex_circuit_data):
        """Test pagination in list endpoints."""

        # Create multiple circuits
        circuit_ids = []
        for i in range(5):
            circuit_data = complex_circuit_data.copy()
            circuit_data["name"] = f"Test Circuit {i+1}"

            response = client.post("/api/circuits", json=circuit_data)
            circuit_ids.append(response.json()["id"])

        # Test circuit pagination
        response = client.get("/api/circuits?limit=2&skip=0")
        assert response.status_code == 200

        data = response.json()
        assert len(data["circuits"]) <= 2
        assert data["total"] >= 5
        assert data["skip"] == 0
        assert data["limit"] == 2

        # Test simulation pagination (create some simulations first)
        for i, circuit_id in enumerate(circuit_ids[:3]):
            sim_request = {"type": "dc", "parameters": {}, "priority": 5}
            client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request)

        response = client.get("/api/simulations?limit=2&skip=0")
        assert response.status_code == 200

        sim_data = response.json()
        assert len(sim_data["simulations"]) <= 2
        assert sim_data["total"] >= 3
