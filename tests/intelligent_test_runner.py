#!/usr/bin/env python3
"""
Intelligent Test Runner for Claude Code

This system runs tests, analyzes results, and provides intelligent feedback
that enables Claude Code to make informed decisions about simulation health.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class IntelligentTestAssessor:
    """Provides intelligent assessment of simulation test results"""
    
    def __init__(self):
        self.knowledge_base = {
            "ac_analysis_patterns": {
                "real_only_values": {
                    "severity": "critical",
                    "description": "AC analysis returning real numbers instead of complex",
                    "symptoms": ["zero phase", "missing imaginary parts", "flat phase plots"],
                    "root_cause": "PySpice AC voltage source configuration",
                    "fix_location": "src/circuit_sim/simulator/builder.py",
                    "fix_action": "Use 'DC {value} AC 1' syntax instead of voltage_source.ac = 1.0"
                },
                "zero_phase_everywhere": {
                    "severity": "critical", 
                    "description": "Phase plots showing 0° when circuits should show phase shift",
                    "symptoms": ["RC filters with 0° phase", "RL circuits with 0° phase"],
                    "root_cause": "Complex number handling in simulation results extraction",
                    "physics_violation": "Capacitors and inductors must cause phase shift"
                }
            },
            "circuit_physics": {
                "rc_lowpass": {
                    "expected_magnitude": "0dB to -∞dB rolloff at 20dB/decade",
                    "expected_phase": "0° to -90° transition",
                    "cutoff_criterion": "-3dB point at fc = 1/(2πRC)"
                },
                "voltage_divider": {
                    "expected_magnitude": "flat response at Vout/Vin ratio",
                    "expected_phase": "0° across all frequencies (resistive)",
                    "key_check": "magnitude should equal R2/(R1+R2)"
                }
            }
        }
    
    def analyze_test_failure_pattern(self, test_results: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in test failures to identify root causes"""
        
        analysis = {
            "failure_patterns": [],
            "root_cause_analysis": {},
            "recommended_fixes": [],
            "confidence_in_diagnosis": 0.0
        }
        
        # Check for AC analysis issues
        real_only_issues = 0
        zero_phase_issues = 0
        
        for result in test_results:
            issues = result.get("issues", [])
            
            for issue in issues:
                if "real-only" in issue.lower():
                    real_only_issues += 1
                if "phase variation" in issue.lower() or "0.00°" in issue:
                    zero_phase_issues += 1
        
        # Pattern recognition
        if real_only_issues >= 2:
            analysis["failure_patterns"].append("systematic_real_only_ac_values")
            analysis["root_cause_analysis"]["primary"] = self.knowledge_base["ac_analysis_patterns"]["real_only_values"]
            analysis["confidence_in_diagnosis"] = 0.9
            
        if zero_phase_issues >= 2:
            analysis["failure_patterns"].append("systematic_zero_phase")
            analysis["root_cause_analysis"]["secondary"] = self.knowledge_base["ac_analysis_patterns"]["zero_phase_everywhere"]
            analysis["confidence_in_diagnosis"] = max(analysis["confidence_in_diagnosis"], 0.8)
        
        # Generate specific recommendations
        if "systematic_real_only_ac_values" in analysis["failure_patterns"]:
            analysis["recommended_fixes"].append({
                "priority": "critical",
                "file": "src/circuit_sim/simulator/builder.py",
                "method": "_add_voltage_source",
                "change": "Replace voltage_source.ac = 1.0 with f'DC {dc_value} AC 1'",
                "test_command": "python tests/test_robust_simulation_behavior.py::TestACAnalysisBehavior::test_ac_returns_complex_values"
            })
        
        return analysis
    
    def generate_claude_diagnosis(self, test_results_path: str) -> str:
        """Generate intelligent diagnosis for Claude Code"""
        
        with open(test_results_path, 'r') as f:
            data = json.load(f)
        
        test_results = data["test_results"]
        
        # Run pattern analysis
        pattern_analysis = self.analyze_test_failure_pattern(test_results)
        
        # Generate Claude-optimized diagnosis
        diagnosis = f"""
# 🤖 Claude Code Simulation Diagnosis

**Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Analysis Confidence**: {pattern_analysis['confidence_in_diagnosis']:.1%}

## 🎯 Primary Issue Detected

"""
        
        if pattern_analysis["root_cause_analysis"]:
            primary = pattern_analysis["root_cause_analysis"].get("primary", {})
            if primary:
                diagnosis += f"""
**Issue**: {primary.get("description", "Unknown")}
**Severity**: {primary.get("severity", "unknown").upper()}

**Symptoms Observed**:
"""
                for symptom in primary.get("symptoms", []):
                    diagnosis += f"- {symptom}\n"
                
                diagnosis += f"""
**Root Cause**: {primary.get("root_cause", "Unknown")}
**Fix Location**: {primary.get("fix_location", "Unknown")}
**Fix Action**: {primary.get("fix_action", "Unknown")}
"""
        
        # Specific recommendations
        if pattern_analysis["recommended_fixes"]:
            diagnosis += f"""
## 🔧 Specific Fixes Required

"""
            for i, fix in enumerate(pattern_analysis["recommended_fixes"], 1):
                diagnosis += f"""
### {i}. {fix["priority"].title()} Priority
- **File**: `{fix["file"]}`
- **Method**: `{fix["method"]}`  
- **Change**: {fix["change"]}
- **Test**: `{fix["test_command"]}`
"""
        
        # Success criteria
        diagnosis += f"""
## ✅ Success Criteria

After implementing fixes:
1. **AC analysis** should return complex voltages (magnitude + phase)
2. **RC filters** should show 0° to -90° phase shift
3. **Bode plots** should show proper rolloff curves
4. **All tests** should pass with >90% confidence

## 🧪 Verification Commands

```bash
# Run specific AC tests
uv run pytest tests/test_robust_simulation_behavior.py::TestACAnalysisBehavior -v

# Run comprehensive visual tests  
docker-compose -f deployment/docker-compose.yml run --rm circuit-sim python3 tests/claude_visual_tester.py

# Regenerate reports to verify fix
docker-compose -f deployment/docker-compose.yml run --rm circuit-sim python3 regenerate_all_reports.py
```

**Expected Result**: All Bode plots should show realistic frequency response curves with proper phase shift.
"""
        
        return diagnosis


if __name__ == "__main__":
    print("🤖 Intelligent Test Runner for Claude Code")
    print("=" * 50)
    
    # Check if we have test results
    json_path = Path("tests/test_results.json")
    
    if json_path.exists():
        print("📊 Found existing test results, generating diagnosis...")
        assessor = IntelligentTestAssessor()
        diagnosis = assessor.generate_claude_diagnosis(str(json_path))
        
        # Save diagnosis
        diagnosis_path = Path("tests") / "claude_diagnosis.md"
        with open(diagnosis_path, 'w') as f:
            f.write(diagnosis)
        
        print(f"🎯 Claude Code Diagnosis: {diagnosis_path}")
        print("\n" + "="*50)
        print(diagnosis[:500] + "..." if len(diagnosis) > 500 else diagnosis)
        
    else:
        print("📋 No test results found. Running comprehensive tests first...")
        
        # Import and run the visual tester
        from claude_visual_tester import main as run_visual_tests
        run_visual_tests()
        
        # Now generate diagnosis
        if json_path.exists():
            assessor = IntelligentTestAssessor()
            diagnosis = assessor.generate_claude_diagnosis(str(json_path))
            
            diagnosis_path = Path("tests") / "claude_diagnosis.md"
            with open(diagnosis_path, 'w') as f:
                f.write(diagnosis)
            
            print(f"\n🎯 Generated diagnosis: {diagnosis_path}")