"""
Tests for WebSocket real-time simulation updates.

Tests WebSocket connection, message handling, and real-time progress updates.
"""

import pytest
import json
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_circuit_data():
    """Sample circuit for WebSocket tests."""
    return {
        "name": "WebSocket Test Circuit",
        "components": [
            {
                "type": "voltage_source",
                "name": "V1",
                "positive_node": "1",
                "negative_node": "0",
                "value": "5V"
            },
            {
                "type": "resistor",
                "name": "R1",
                "positive_node": "1",
                "negative_node": "0",
                "value": "1k"
            }
        ]
    }


class TestWebSocketConnections:
    """Test WebSocket functionality."""

    def test_websocket_connection_basic(self, client):
        """Test basic WebSocket connection."""
        with client.websocket_connect("/ws/simulation/test-job-123") as websocket:
            # Connection should be established
            assert websocket is not None

    def test_websocket_invalid_job_id(self, client):
        """Test WebSocket connection with invalid job ID format."""
        with pytest.raises(Exception):
            # Should raise connection error for invalid job ID
            with client.websocket_connect("/ws/simulation/") as websocket:
                pass

    def test_websocket_simulation_progress_messages(self, client, sample_circuit_data):
        """Test receiving simulation progress via WebSocket."""
        # Create circuit first
        create_response = client.post("/api/circuits", json=sample_circuit_data)
        circuit_id = create_response.json()["id"]
        
        # Start simulation
        sim_request = {
            "type": "dc",
            "parameters": {"analysis": "operating_point"},
            "priority": 5
        }
        
        sim_response = client.post(f"/api/circuits/{circuit_id}/simulate", json=sim_request)
        job_id = sim_response.json()["job_id"]
        
        # Connect to WebSocket for this job
        with client.websocket_connect(f"/ws/simulation/{job_id}") as websocket:
            # Should receive initial connection message
            initial_msg = websocket.receive_json()
            assert initial_msg["type"] == "connection"
            assert initial_msg["job_id"] == job_id
            assert initial_msg["message"] == "Connected to simulation updates"

    def test_websocket_multiple_clients(self, client, sample_circuit_data):
        """Test multiple WebSocket clients for same simulation."""
        # Create circuit and simulation
        create_response = client.post("/api/circuits", json=sample_circuit_data)
        circuit_id = create_response.json()["id"]
        
        sim_response = client.post(f"/api/circuits/{circuit_id}/simulate", json={
            "type": "transient",
            "parameters": {"stop_time": 0.001},
            "priority": 5
        })
        job_id = sim_response.json()["job_id"]
        
        # Connect multiple WebSocket clients
        with client.websocket_connect(f"/ws/simulation/{job_id}") as ws1:
            with client.websocket_connect(f"/ws/simulation/{job_id}") as ws2:
                # Both should receive connection messages
                msg1 = ws1.receive_json()
                msg2 = ws2.receive_json()
                
                assert msg1["type"] == "connection"
                assert msg2["type"] == "connection"
                assert msg1["job_id"] == msg2["job_id"] == job_id

    def test_websocket_message_format(self, client, sample_circuit_data):
        """Test WebSocket message format compliance."""
        # Create circuit and start simulation
        create_response = client.post("/api/circuits", json=sample_circuit_data)
        circuit_id = create_response.json()["id"]
        
        sim_response = client.post(f"/api/circuits/{circuit_id}/simulate", json={
            "type": "dc",
            "parameters": {},
            "priority": 5
        })
        job_id = sim_response.json()["job_id"]
        
        with client.websocket_connect(f"/ws/simulation/{job_id}") as websocket:
            message = websocket.receive_json()
            
            # Verify message structure
            required_fields = ["type", "job_id", "message"]
            for field in required_fields:
                assert field in message
            
            assert isinstance(message["type"], str)
            assert isinstance(message["job_id"], str)
            assert isinstance(message["message"], str)

    def test_websocket_client_commands(self, client, sample_circuit_data):
        """Test client sending commands via WebSocket."""
        # Create circuit and start simulation  
        create_response = client.post("/api/circuits", json=sample_circuit_data)
        circuit_id = create_response.json()["id"]
        
        sim_response = client.post(f"/api/circuits/{circuit_id}/simulate", json={
            "type": "transient",
            "parameters": {"stop_time": 10.0},  # Long simulation
            "priority": 5
        })
        job_id = sim_response.json()["job_id"]
        
        with client.websocket_connect(f"/ws/simulation/{job_id}") as websocket:
            # Receive connection message
            websocket.receive_json()
            
            # Send cancel command
            cancel_command = {
                "type": "command",
                "action": "cancel"
            }
            websocket.send_json(cancel_command)
            
            # Should receive acknowledgment or error (simulation might already be completed)
            response = websocket.receive_json()
            assert response["type"] in ["command_ack", "error"]
            if response["type"] == "command_ack":
                assert "cancel" in response["message"].lower()
            else:
                assert "cancel" in response["message"].lower() or "completed" in response["message"].lower()

    def test_websocket_connection_cleanup(self, client):
        """Test WebSocket connection cleanup on disconnect."""
        job_id = "test-cleanup-123"
        
        with client.websocket_connect(f"/ws/simulation/{job_id}") as websocket:
            # Connection established
            initial_msg = websocket.receive_json()
            assert initial_msg["type"] == "connection"
        
        # Connection should be cleaned up automatically when context exits
        # This test verifies no exceptions are raised during cleanup