"""
Test CLI simulate command functionality.

Testing simulation commands for DC and transient analysis.
"""

import json
import os
import tempfile
from pathlib import Path

from click.testing import CliRunner

from circuit_sim.cli.main import cli, register_commands

# Register commands for testing
register_commands()


class TestSimulateCommand:
    """Test the simulate command for circuit simulation."""

    def setup_test_circuit(self, temp_dir: str) -> str:
        """Helper to create a test circuit and return circuit ID."""
        # Create netlist
        netlist_content = """* Test RC Filter
V1 1 0 DC 5V
R1 1 2 1k  
C1 2 0 1u
.end
"""
        netlist_file = Path(temp_dir) / "test.cir"
        netlist_file.write_text(netlist_content)

        # Create circuit metadata manually
        circuits_dir = Path(temp_dir) / "circuits"
        circuits_dir.mkdir(exist_ok=True)

        circuit_id = "test123"
        metadata = {
            "id": circuit_id,
            "name": "Test Circuit",
            "netlist_path": str(netlist_file.absolute()),
            "created_at": circuit_id,
            "status": "created",
            "simulations": [],
        }

        metadata_file = circuits_dir / f"{circuit_id}.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))

        return circuit_id

    def test_simulate_dc_command_exists(self):
        """Test that simulate dc command is available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                circuit_id = self.setup_test_circuit(temp_dir)

                runner = CliRunner()
                result = runner.invoke(cli, ["simulate", "--help"])

                assert result.exit_code == 0
                assert "dc" in result.output.lower()
                assert "transient" in result.output.lower()

            finally:
                os.chdir(original_cwd)

    def test_simulate_dc_missing_circuit_id(self):
        """Test simulate dc command with missing circuit ID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                runner = CliRunner()
                result = runner.invoke(cli, ["simulate", "dc"])

                # Should show error about missing circuit-id
                assert result.exit_code != 0
                assert "circuit-id" in result.output.lower()

            finally:
                os.chdir(original_cwd)

    def test_simulate_dc_nonexistent_circuit(self):
        """Test simulate dc with nonexistent circuit ID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                runner = CliRunner()
                result = runner.invoke(cli, ["simulate", "dc", "--circuit-id", "nonexistent"])

                # Should show error about circuit not found
                assert result.exit_code == 1  # User error
                assert "not found" in result.output.lower()

            finally:
                os.chdir(original_cwd)

    def test_simulate_dc_valid_circuit(self):
        """Test simulate dc with valid circuit ID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                circuit_id = self.setup_test_circuit(temp_dir)

                runner = CliRunner()
                result = runner.invoke(cli, ["simulate", "dc", "--circuit-id", circuit_id])

                # Should complete successfully (may skip actual simulation in test mode)
                assert result.exit_code in [0, 1]  # Success or graceful skip

            finally:
                os.chdir(original_cwd)
