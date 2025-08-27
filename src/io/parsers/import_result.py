"""
Import result tracking for partial success scenarios.
Allows users to see what worked and what didn't during netlist import.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

from circuit_sim import Circuit


class FailureLevel(Enum):
    """Severity level of import failures."""
    WARNING = "warning"     # Component imported with default/assumed values
    ERROR = "error"        # Component could not be imported
    CRITICAL = "critical"  # Parser error that stopped processing


@dataclass
class ComponentFailure:
    """Details about a failed component import."""
    component_ref: str
    error_message: str
    level: FailureLevel
    line_number: Optional[int] = None
    context: Optional[str] = None       # Problematic text
    suggestion: Optional[str] = None    # How user can fix it
    
    def __str__(self):
        """User-friendly error description."""
        result = f"{self.level.value.upper()}: {self.component_ref} - {self.error_message}"
        
        if self.line_number:
            result = f"Line {self.line_number}: " + result
            
        if self.context:
            result += f"\n  Context: {self.context}"
            
        if self.suggestion:
            result += f"\n  Suggestion: {self.suggestion}"
            
        return result


@dataclass 
class ComponentWarning:
    """Details about a component warning during import."""
    component_ref: str
    warning_message: str
    action_taken: str  # What the parser did to handle it
    
    def __str__(self):
        return f"WARNING: {self.component_ref} - {self.warning_message} ({self.action_taken})"


class ImportResult:
    """
    Tracks the results of a netlist import operation.
    Provides visibility into what succeeded, failed, or had warnings.
    """
    
    def __init__(self, circuit: Optional[Circuit] = None):
        self.circuit = circuit or Circuit("Imported Circuit")
        self.successful_components: List[str] = []
        self.failed_components: List[ComponentFailure] = []
        self.warnings: List[ComponentWarning] = []
        self.parsing_errors: List[str] = []
        
    def add_success(self, component_ref: str):
        """Record a successfully imported component."""
        self.successful_components.append(component_ref)
        
    def add_failure(self, failure: ComponentFailure):
        """Record a failed component import."""
        self.failed_components.append(failure)
        
    def add_warning(self, warning: ComponentWarning):
        """Record a component warning."""
        self.warnings.append(warning)
        
    def add_parsing_error(self, error: str):
        """Record a general parsing error."""
        self.parsing_errors.append(error)
    
    @property
    def is_successful(self) -> bool:
        """True if import had no critical failures."""
        return len([f for f in self.failed_components if f.level == FailureLevel.CRITICAL]) == 0
    
    @property
    def has_warnings(self) -> bool:
        """True if import had warnings or non-critical errors."""
        return len(self.warnings) > 0 or len(self.failed_components) > 0
        
    @property
    def total_components_found(self) -> int:
        """Total number of components encountered."""
        return len(self.successful_components) + len(self.failed_components)
        
    def summary(self) -> str:
        """Generate a user-friendly summary of the import."""
        if self.total_components_found == 0:
            return "❌ No components found in netlist"
        
        success_count = len(self.successful_components)
        warning_count = len(self.warnings)
        error_count = len([f for f in self.failed_components if f.level == FailureLevel.ERROR])
        critical_count = len([f for f in self.failed_components if f.level == FailureLevel.CRITICAL])
        
        lines = []
        
        # Overall status
        if critical_count > 0:
            lines.append(f"❌ Import failed with {critical_count} critical error(s)")
        elif error_count > 0 or warning_count > 0:
            lines.append(f"⚠️  Import completed with issues")
        else:
            lines.append("✅ Import successful")
        
        # Component counts
        lines.append("")
        lines.append("Import Results:")
        lines.append(f"  ✓ {success_count} components imported successfully")
        
        if warning_count > 0:
            lines.append(f"  ⚠ {warning_count} component(s) had warnings")
            
        if error_count > 0:
            lines.append(f"  ✗ {error_count} component(s) failed to import")
            
        if critical_count > 0:
            lines.append(f"  🚨 {critical_count} critical parsing error(s)")
            
        # Show details if there are issues
        if self.has_warnings:
            lines.append("")
            lines.append("Issues found:")
            
            # Show up to 3 most critical issues
            all_issues = (
                [(f, f.level.value) for f in self.failed_components] + 
                [(w, "warning") for w in self.warnings]
            )
            all_issues.sort(key=lambda x: {"critical": 0, "error": 1, "warning": 2}[x[1]])
            
            for issue, level in all_issues[:3]:
                lines.append(f"  • {issue}")
                
            if len(all_issues) > 3:
                lines.append(f"  ... and {len(all_issues) - 3} more issues")
                
            lines.append("")
            lines.append("💡 Use result.failed_components and result.warnings for full details")
        
        return "\n".join(lines)
    
    def detailed_report(self) -> str:
        """Generate a detailed report of all issues."""
        lines = [self.summary(), ""]
        
        if self.parsing_errors:
            lines.append("Parsing Errors:")
            for error in self.parsing_errors:
                lines.append(f"  • {error}")
            lines.append("")
        
        if self.failed_components:
            lines.append("Failed Components:")
            for failure in self.failed_components:
                lines.append(f"  • {failure}")
            lines.append("")
            
        if self.warnings:
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"  • {warning}")
            lines.append("")
        
        if self.successful_components:
            lines.append("Successfully Imported:")
            for component in self.successful_components:
                lines.append(f"  ✓ {component}")
        
        return "\n".join(lines)


def create_component_failure(
    component_ref: str,
    error_message: str, 
    level: FailureLevel = FailureLevel.ERROR,
    suggestion: Optional[str] = None,
    line_number: Optional[int] = None,
    context: Optional[str] = None
) -> ComponentFailure:
    """Helper function to create ComponentFailure with sensible defaults."""
    return ComponentFailure(
        component_ref=component_ref,
        error_message=error_message,
        level=level,
        line_number=line_number,
        context=context,
        suggestion=suggestion or _get_default_suggestion(error_message, component_ref)
    )


def _get_default_suggestion(error_message: str, component_ref: str) -> str:
    """Generate helpful suggestions based on error patterns."""
    error_lower = error_message.lower()
    
    if "value" in error_lower and "empty" in error_lower:
        return f"Add a value for {component_ref} in KiCad, or set it manually after import"
    elif "value" in error_lower:
        return f"Check the value format for {component_ref} in the netlist"
    elif "unknown" in error_lower or "unsupported" in error_lower:
        return f"Component type for {component_ref} may not be supported yet"
    elif "format" in error_lower or "syntax" in error_lower:
        return "Check netlist format - it may be corrupted or from unsupported KiCad version"
    else:
        return "Check component definition in original KiCad schematic"