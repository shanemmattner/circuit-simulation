"""Tests for logic gate circuits."""

import pytest
import numpy as np

from examples.digital.logic_gates import (
    LogicGateCircuit,
    simulate_logic_gate,
    create_truth_table,
    design_logic_function
)


class TestLogicGates:
    """Test logic gate implementations."""
    
    def test_and_gate(self):
        """Test AND gate."""
        circuit = LogicGateCircuit(
            gate_type="AND",
            num_inputs=2,
            vcc=5.0
        )
        
        assert circuit.gate_type == "AND"
        assert circuit.num_inputs == 2
        
        # Test truth table
        assert circuit.evaluate([0, 0]) == 0
        assert circuit.evaluate([0, 1]) == 0
        assert circuit.evaluate([1, 0]) == 0
        assert circuit.evaluate([1, 1]) == 1
    
    def test_or_gate(self):
        """Test OR gate."""
        circuit = LogicGateCircuit(gate_type="OR", num_inputs=2)
        
        assert circuit.evaluate([0, 0]) == 0
        assert circuit.evaluate([0, 1]) == 1
        assert circuit.evaluate([1, 0]) == 1
        assert circuit.evaluate([1, 1]) == 1
    
    def test_not_gate(self):
        """Test NOT gate."""
        circuit = LogicGateCircuit(gate_type="NOT", num_inputs=1)
        
        assert circuit.evaluate([0]) == 1
        assert circuit.evaluate([1]) == 0
    
    def test_xor_gate(self):
        """Test XOR gate."""
        circuit = LogicGateCircuit(gate_type="XOR", num_inputs=2)
        
        assert circuit.evaluate([0, 0]) == 0
        assert circuit.evaluate([0, 1]) == 1
        assert circuit.evaluate([1, 0]) == 1
        assert circuit.evaluate([1, 1]) == 0
    
    def test_nand_gate(self):
        """Test NAND gate."""
        circuit = LogicGateCircuit(gate_type="NAND", num_inputs=2)
        
        assert circuit.evaluate([0, 0]) == 1
        assert circuit.evaluate([0, 1]) == 1
        assert circuit.evaluate([1, 0]) == 1
        assert circuit.evaluate([1, 1]) == 0


class TestLogicSimulation:
    """Test logic gate simulation."""
    
    def test_gate_simulation(self):
        """Test simulating logic gate."""
        circuit = LogicGateCircuit(gate_type="AND", num_inputs=2)
        
        results = simulate_logic_gate(
            circuit,
            input_signals=[[0, 1, 1, 0], [0, 0, 1, 1]],
            duration=4e-3
        )
        
        assert "time" in results
        assert "inputs" in results
        assert "output" in results
        
        # Check output matches AND truth table
        output = results["output"]
        assert output[0] == 0  # 0 AND 0 = 0
        assert output[1] == 0  # 1 AND 0 = 0
        assert output[2] == 1  # 1 AND 1 = 1
        assert output[3] == 0  # 0 AND 1 = 0
    
    def test_propagation_delay(self):
        """Test gate propagation delay."""
        circuit = LogicGateCircuit(
            gate_type="NOT",
            num_inputs=1,
            propagation_delay=10e-9  # 10ns
        )
        
        results = simulate_logic_gate(
            circuit,
            input_signals=[[0, 1]],
            duration=100e-9,
            timestep=1e-9
        )
        
        # Output should be delayed
        assert "propagation_delay" in results
        assert results["propagation_delay"] == 10e-9


class TestTruthTable:
    """Test truth table generation."""
    
    def test_truth_table_generation(self):
        """Test generating truth table."""
        circuit = LogicGateCircuit(gate_type="XOR", num_inputs=2)
        
        truth_table = create_truth_table(circuit)
        
        assert "inputs" in truth_table
        assert "outputs" in truth_table
        assert len(truth_table["inputs"]) == 4  # 2^2 combinations
        
        # Check XOR truth table
        assert truth_table["outputs"] == [0, 1, 1, 0]


class TestLogicDesign:
    """Test logic function design."""
    
    def test_design_logic_function(self):
        """Test designing logic function."""
        # Design a function: F = A'B + AB'
        truth_table = [
            ([0, 0], 0),
            ([0, 1], 1),
            ([1, 0], 1),
            ([1, 1], 0)
        ]
        
        circuit = design_logic_function(truth_table)
        
        assert circuit is not None
        
        # Verify it implements XOR
        for inputs, expected in truth_table:
            assert circuit.evaluate(inputs) == expected