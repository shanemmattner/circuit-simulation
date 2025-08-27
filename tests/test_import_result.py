"""
Test ImportResult class for tracking partial import success.
"""

import pytest
from circuit_sim import Circuit
from src.io.parsers.import_result import (
    ImportResult, 
    ComponentFailure, 
    ComponentWarning, 
    FailureLevel,
    create_component_failure
)


class TestImportResult:
    """Test the ImportResult tracking functionality."""
    
    def test_empty_result_initialization(self):
        """Test creating an empty ImportResult."""
        result = ImportResult()
        
        assert result.circuit is not None
        assert result.total_components_found == 0
        assert result.is_successful is True  # No critical failures
        assert result.has_warnings is False
        
    def test_successful_component_tracking(self):
        """Test tracking successful component imports."""
        result = ImportResult()
        
        result.add_success("R1")
        result.add_success("R2")
        result.add_success("C1")
        
        assert len(result.successful_components) == 3
        assert "R1" in result.successful_components
        assert result.total_components_found == 3
        assert result.is_successful is True
        
    def test_component_failure_tracking(self):
        """Test tracking component failures."""
        result = ImportResult()
        
        failure = ComponentFailure(
            component_ref="U1",
            error_message="Unknown component type",
            level=FailureLevel.ERROR,
            suggestion="Check if component is supported"
        )
        
        result.add_failure(failure)
        result.add_success("R1")  # Some success
        
        assert len(result.failed_components) == 1
        assert result.total_components_found == 2
        assert result.is_successful is True  # Non-critical failure
        assert result.has_warnings is True
        
    def test_critical_failure_affects_success(self):
        """Test that critical failures mark import as unsuccessful."""
        result = ImportResult()
        
        critical_failure = ComponentFailure(
            component_ref="PARSER",
            error_message="Malformed netlist structure",
            level=FailureLevel.CRITICAL
        )
        
        result.add_failure(critical_failure)
        
        assert result.is_successful is False
        assert result.has_warnings is True
        
    def test_warning_tracking(self):
        """Test tracking component warnings."""
        result = ImportResult()
        
        warning = ComponentWarning(
            component_ref="R1",
            warning_message="Value field empty", 
            action_taken="Used default value 1k"
        )
        
        result.add_warning(warning)
        result.add_success("R1")
        
        assert len(result.warnings) == 1
        assert result.has_warnings is True
        assert result.is_successful is True
        
    def test_summary_generation(self):
        """Test generating user-friendly summaries."""
        result = ImportResult()
        
        # Add mixed results
        result.add_success("R1")
        result.add_success("R2")
        
        warning = ComponentWarning("R3", "Empty value", "Used default")
        result.add_warning(warning)
        
        failure = create_component_failure("U1", "Unsupported component", FailureLevel.ERROR)
        result.add_failure(failure)
        
        summary = result.summary()
        
        # Should contain key information
        assert "2 components imported successfully" in summary
        assert "1 component(s) had warnings" in summary  
        assert "1 component(s) failed" in summary
        assert "⚠️" in summary  # Warning indicator
        
    def test_successful_import_summary(self):
        """Test summary for completely successful import."""
        result = ImportResult()
        
        result.add_success("R1")
        result.add_success("C1")
        result.add_success("L1")
        
        summary = result.summary()
        
        assert "✅ Import successful" in summary
        assert "3 components imported successfully" in summary
        assert "warning" not in summary.lower()
        
    def test_failed_import_summary(self):
        """Test summary for failed import."""
        result = ImportResult()
        
        critical_failure = create_component_failure(
            "PARSER", 
            "Cannot parse netlist", 
            FailureLevel.CRITICAL
        )
        result.add_failure(critical_failure)
        
        summary = result.summary()
        
        assert "❌ Import failed" in summary
        assert "1 critical error" in summary
        
    def test_create_component_failure_helper(self):
        """Test the helper function for creating component failures."""
        failure = create_component_failure(
            "R1",
            "Empty value field",
            FailureLevel.WARNING,
            line_number=42
        )
        
        assert failure.component_ref == "R1"
        assert failure.error_message == "Empty value field"
        assert failure.level == FailureLevel.WARNING
        assert failure.line_number == 42
        assert failure.suggestion is not None  # Should have auto-generated suggestion
        assert "value" in failure.suggestion.lower()
        
    def test_component_failure_string_representation(self):
        """Test string representation of ComponentFailure."""
        failure = ComponentFailure(
            component_ref="R1",
            error_message="Empty value", 
            level=FailureLevel.WARNING,
            line_number=10,
            context='(value "")',
            suggestion="Add value in KiCad"
        )
        
        failure_str = str(failure)
        
        assert "Line 10" in failure_str
        assert "WARNING: R1" in failure_str
        assert "Empty value" in failure_str
        assert "Context:" in failure_str
        assert "Suggestion:" in failure_str
        
    def test_detailed_report_generation(self):
        """Test detailed report with all information."""
        result = ImportResult()
        
        result.add_success("R1")
        result.add_parsing_error("Line 5: Unexpected token")
        
        warning = ComponentWarning("R2", "Default value used", "Set to 1k")
        result.add_warning(warning)
        
        failure = create_component_failure("U1", "Unknown component")
        result.add_failure(failure)
        
        report = result.detailed_report()
        
        # Should contain all sections
        assert "Import Results:" in report
        assert "Parsing Errors:" in report
        assert "Failed Components:" in report 
        assert "Warnings:" in report
        assert "Successfully Imported:" in report
        assert "Line 5: Unexpected token" in report