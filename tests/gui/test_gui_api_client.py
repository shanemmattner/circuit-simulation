"""Test API client integration - Chunk 4 TDD tests."""

import pytest
from unittest.mock import Mock, patch
from src.gui.services.api_client import CircuitAPIClient


class TestCircuitAPIClient:
    """Test circuit API client functionality."""
    
    def test_api_client_can_be_created(self):
        """Test that CircuitAPIClient can be instantiated."""
        # This will fail initially - we haven't created the api_client module yet
        client = CircuitAPIClient("http://localhost:8000")
        assert client is not None
        assert client.base_url == "http://localhost:8000"
        
    def test_get_circuits_returns_list(self):
        """Test that get_circuits returns a list of circuits."""
        client = CircuitAPIClient("http://localhost:8000")
        with patch('requests.get') as mock_get:
            # Mock successful API response
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: [
                    {"id": "rc_filter", "name": "RC Filter"},
                    {"id": "voltage_divider", "name": "Voltage Divider"}
                ]
            )
            
            circuits = client.get_circuits()
            assert isinstance(circuits, list)
            assert len(circuits) == 2
            assert circuits[0]["name"] == "RC Filter"
            
    def test_get_circuits_handles_api_error(self):
        """Test that get_circuits handles API errors gracefully."""
        client = CircuitAPIClient("http://localhost:8000")
        with patch('requests.get') as mock_get:
            # Mock API error
            mock_get.return_value = Mock(status_code=500)
            
            circuits = client.get_circuits()
            assert circuits == []  # Should return empty list on error
            
    def test_get_circuit_options_for_dropdown(self):
        """Test formatting circuit data for Dash dropdown."""
        client = CircuitAPIClient("http://localhost:8000")
        with patch.object(client, 'get_circuits') as mock_get_circuits:
            mock_get_circuits.return_value = [
                {"id": "rc_filter", "name": "RC Filter"},
                {"id": "voltage_divider", "name": "Voltage Divider"}
            ]
            
            options = client.get_circuit_options()
            assert isinstance(options, list)
            assert len(options) == 2
            assert options[0] == {"label": "RC Filter", "value": "rc_filter"}
            assert options[1] == {"label": "Voltage Divider", "value": "voltage_divider"}
            
    def test_get_circuit_details(self):
        """Test getting detailed circuit information."""
        client = CircuitAPIClient("http://localhost:8000")
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: {
                    "id": "rc_filter",
                    "name": "RC Filter", 
                    "components": [
                        {"type": "resistor", "name": "R1", "value": "1k"},
                        {"type": "capacitor", "name": "C1", "value": "1u"}
                    ]
                }
            )
            
            circuit = client.get_circuit_details("rc_filter")
            assert circuit["name"] == "RC Filter"
            assert len(circuit["components"]) == 2