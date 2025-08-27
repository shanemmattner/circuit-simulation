"""
Tests for circuit CRUD API endpoints.

Tests circuit creation, retrieval, listing, and deletion via REST API.
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
    """Sample circuit data for testing."""
    return {
        "name": "RC Filter",
        "description": "Simple RC low-pass filter",
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
                "negative_node": "2",
                "value": "1k"
            },
            {
                "type": "capacitor",
                "name": "C1",
                "positive_node": "2",
                "negative_node": "0",
                "value": "1u"
            }
        ]
    }


class TestCircuitCRUD:
    """Test circuit CRUD operations."""

    def test_create_circuit_valid(self, client, sample_circuit_data):
        """Test creating a new circuit with valid data."""
        response = client.post("/api/circuits", json=sample_circuit_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_circuit_data["name"]
        assert data["component_count"] == 3
        assert data["node_count"] == 4  # nodes: 0(int), "0"(str), "1"(str), "2"(str)
        assert "id" in data
        assert "created_at" in data

    def test_create_circuit_invalid_data(self, client):
        """Test creating circuit with invalid data fails."""
        invalid_data = {
            "name": "",  # Empty name should fail
            "components": []
        }
        
        response = client.post("/api/circuits", json=invalid_data)
        assert response.status_code == 422

    def test_create_circuit_duplicate_component_names(self, client):
        """Test creating circuit with duplicate component names fails."""
        invalid_data = {
            "name": "Invalid Circuit",
            "components": [
                {
                    "type": "resistor",
                    "name": "R1",
                    "positive_node": "1",
                    "negative_node": "0",
                    "value": "1k"
                },
                {
                    "type": "resistor", 
                    "name": "R1",  # Duplicate name
                    "positive_node": "2",
                    "negative_node": "0",
                    "value": "2k"
                }
            ]
        }
        
        response = client.post("/api/circuits", json=invalid_data)
        assert response.status_code == 422

    def test_get_circuit_by_id(self, client, sample_circuit_data):
        """Test retrieving a circuit by ID."""
        # Create circuit first
        create_response = client.post("/api/circuits", json=sample_circuit_data)
        circuit_id = create_response.json()["id"]
        
        # Get circuit by ID
        response = client.get(f"/api/circuits/{circuit_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == circuit_id
        assert data["name"] == sample_circuit_data["name"]

    def test_get_circuit_not_found(self, client):
        """Test retrieving non-existent circuit returns 404."""
        response = client.get("/api/circuits/non-existent-id")
        assert response.status_code == 404

    def test_list_circuits(self, client, sample_circuit_data):
        """Test listing all circuits."""
        # Create a couple of circuits
        client.post("/api/circuits", json=sample_circuit_data)
        
        sample_circuit_data["name"] = "Another Circuit"
        client.post("/api/circuits", json=sample_circuit_data)
        
        # List circuits
        response = client.get("/api/circuits")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["circuits"]) >= 2
        assert data["total"] >= 2

    def test_delete_circuit(self, client, sample_circuit_data):
        """Test deleting a circuit."""
        # Create circuit first
        create_response = client.post("/api/circuits", json=sample_circuit_data)
        circuit_id = create_response.json()["id"]
        
        # Delete circuit
        response = client.delete(f"/api/circuits/{circuit_id}")
        
        assert response.status_code == 204
        
        # Verify circuit is gone
        get_response = client.get(f"/api/circuits/{circuit_id}")
        assert get_response.status_code == 404

    def test_delete_circuit_not_found(self, client):
        """Test deleting non-existent circuit returns 404."""
        response = client.delete("/api/circuits/non-existent-id")
        assert response.status_code == 404