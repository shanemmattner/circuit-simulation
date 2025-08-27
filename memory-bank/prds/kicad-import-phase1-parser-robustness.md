# PRD: KiCad Import Phase 1 - Parser Robustness

## Document Information
- **Version**: 1.0
- **Date**: 2025-01-27
- **Status**: Draft
- **Scope**: Phase 1 of KiCad Import Enhancement

## Problem Statement

The current KiCad parser works for simple cases but fails unpredictably on real-world netlists. Users don't know why imports fail or how to fix them.

## Goal

Make the parser resilient and informative - it should handle various KiCad formats gracefully and tell users exactly what went wrong when it can't.

## Proposed Solution

### 1. Flexible Value Extraction

Instead of hard-coded regex patterns, use a fallback strategy:

```python
class ValueExtractor:
    """Try multiple strategies to find component values."""
    
    def extract_value(self, component_section: str, ref: str) -> Optional[str]:
        """
        Try multiple approaches:
        1. Look for (value "...") anywhere in component block
        2. Check for value as a parameter
        3. Look for common patterns in part names
        4. Return None if not found (let user provide)
        """
```

### 2. Better Error Context

When parsing fails, show users:
- What was being parsed
- Where in the file it failed  
- What the parser expected
- Suggestions for fixing

```python
# Example error output:
"""
Failed to parse component at line 45:
  (comp (ref "U1") (value "")
  
Issue: Empty value field
Suggestion: Component U1 has no value. You can:
  1. Add it manually after import: circuit.set_value("U1", "LM358")
  2. Fix in KiCad and re-export
  3. Continue with default value
"""
```

### 3. Partial Import Success

Don't fail the entire import for one bad component:

```python
class ImportResult:
    """Track what worked and what didn't."""
    
    def __init__(self):
        self.circuit = Circuit()
        self.successful_components = []
        self.failed_components = []
        self.warnings = []
        
    def summary(self):
        """Show import results."""
        return f"""
        Import Results:
        ✓ {len(self.successful_components)} components imported
        ✗ {len(self.failed_components)} components failed
        ⚠ {len(self.warnings)} warnings
        
        See result.failed_components for details.
        """
```

### 4. Format Detection

Auto-detect KiCad version and format variations:

```python
def detect_format(content: str) -> KiCadFormat:
    """Detect which KiCad version/format this is."""
    # Look for version markers
    # Check structure patterns
    # Return format info for appropriate parser
```

## Success Criteria

1. **Parse 80% of components** even in problematic files
2. **Clear error messages** that users can act on
3. **No silent failures** - always report what couldn't be parsed
4. **Backward compatible** - existing working imports still work

## Implementation Approach

1. **Collect test files** - Get various KiCad netlists that currently fail
2. **Build test suite** - Each file becomes a test case
3. **Iterative improvement** - Fix parser based on real failures
4. **User feedback loop** - Show errors, get feedback, improve messages

## Timeline

**1 week** - This is a focused improvement to existing code

## Next Phases (Separate PRDs)

- **Phase 2**: Component Model Mapping (flexible, not hard-coded)
- **Phase 3**: Power Supply Intelligence (configurable detection)
- **Phase 4**: Advanced Features (hierarchical, export, etc.)

---

**This PRD focuses only on making the parser robust and user-friendly. No new features, just reliability.**