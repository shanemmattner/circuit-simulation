"""
Tests for API Pydantic models.

Tests data validation, serialization, and model behavior.
"""

import pytest
from pydantic import ValidationError

from src.api.models.circuit import CircuitCreate, ComponentInput
from src.api.models.simulation import SimulationRequest, SimulationStatus, SimulationType


class TestCircuitModels:
    """Test circuit-related Pydantic models."""

    def test_component_input_valid(self):
        """Test valid component input creation."""
        component = ComponentInput(
            type="resistor", name="R1", positive_node="1", negative_node="0", value="1k"
        )
        assert component.type == "resistor"
        assert component.name == "R1"
        assert component.value == "1k"

    def test_component_input_invalid_type(self):
        """Test invalid component type raises validation error."""
        with pytest.raises(ValidationError):
            ComponentInput(
                type="invalid_type", name="R1", positive_node="1", negative_node="0", value="1k"
            )

    def test_circuit_create_valid(self):
        """Test valid circuit creation request."""
        components = [
            ComponentInput(
                type="voltage_source", name="V1", positive_node="1", negative_node="0", value="5V"
            ),
            ComponentInput(
                type="resistor", name="R1", positive_node="1", negative_node="0", value="1k"
            ),
        ]

        circuit = CircuitCreate(
            name="Simple RC Circuit",
            description="Basic RC circuit for testing",
            components=components,
        )

        assert circuit.name == "Simple RC Circuit"
        assert len(circuit.components) == 2
        assert circuit.components[0].type == "voltage_source"

    def test_circuit_create_empty_name_invalid(self):
        """Test circuit creation with empty name fails."""
        with pytest.raises(ValidationError):
            CircuitCreate(name="", components=[])


class TestSimulationModels:
    """Test simulation-related Pydantic models."""

    def test_simulation_request_valid(self):
        """Test valid simulation request creation."""
        request = SimulationRequest(
            type=SimulationType.DC, parameters={"analysis": "operating_point"}, priority=5
        )

        assert request.type == SimulationType.DC
        assert request.priority == 5
        assert "analysis" in request.parameters

    def test_simulation_status_valid(self):
        """Test valid simulation status creation."""
        from datetime import datetime

        status = SimulationStatus(
            job_id="test-123",
            circuit_id="circuit-456",
            type=SimulationType.DC,
            priority=5,
            status="running",
            progress=45.5,
            eta_seconds=30,
            message="Running DC analysis...",
            created_at=datetime.now(),
        )

        assert status.job_id == "test-123"
        assert status.progress == 45.5
        assert status.eta_seconds == 30

    def test_simulation_type_enum_values(self):
        """Test simulation type enum has expected values."""
        assert SimulationType.DC == "dc"
        assert SimulationType.TRANSIENT == "transient"
        assert SimulationType.AC == "ac"
