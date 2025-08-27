#!/usr/bin/env python3
"""
Comprehensive Report Testing Script

Tests all existing example circuits to generate reports and analyze their quality.
This script will:
1. Discover all example circuits
2. Generate reports for each circuit
3. Analyze the generated reports
4. Provide comprehensive feedback on report quality
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import traceback
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.reports import ReportGenerator


class ComprehensiveReportTester:
    """Test all example circuits and generate comprehensive reports"""
    
    def __init__(self):
        self.examples_dir = Path("examples")
        self.output_dir = Path("reports_test_output")
        self.output_dir.mkdir(exist_ok=True)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "circuits_tested": 0,
            "successful_reports": 0,
            "failed_reports": 0,
            "circuit_results": [],
            "errors": []
        }
    
    def discover_circuits(self) -> List[Path]:
        """Discover all circuit.py files in examples directory"""
        circuit_files = []
        
        # Find all circuit.py files
        for circuit_file in self.examples_dir.rglob("circuit.py"):
            circuit_files.append(circuit_file)
        
        print(f"📋 Found {len(circuit_files)} example circuits:")
        for cf in circuit_files:
            print(f"   • {cf.relative_to(self.examples_dir)}")
        
        return sorted(circuit_files)
    
    def load_circuit_module(self, circuit_file: Path) -> Optional[Any]:
        """Load a circuit.py file as a Python module"""
        try:
            module_name = f"circuit_{circuit_file.parent.name}_{circuit_file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, circuit_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"❌ Failed to load {circuit_file}: {e}")
            return None
    
    def extract_circuit_from_module(self, module: Any) -> Optional[Circuit]:
        """Extract Circuit object from loaded module"""
        # Try different common patterns
        circuit_candidates = []
        
        # Look for functions that create circuits
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                # Try calling functions that might return circuits
                try:
                    result = attr()
                    if isinstance(result, Circuit):
                        circuit_candidates.append((attr_name, result))
                except Exception:
                    # Function might require parameters, skip
                    pass
        
        # Look for direct Circuit objects
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, Circuit):
                circuit_candidates.append((attr_name, attr))
        
        if circuit_candidates:
            # Prefer main circuit or create_circuit functions
            for name, circuit in circuit_candidates:
                if 'main' in name.lower() or 'create' in name.lower():
                    return circuit
            # Otherwise return the first one
            return circuit_candidates[0][1]
        
        return None
    
    def test_circuit_simulation(self, circuit: Circuit) -> Tuple[bool, Dict[str, Any]]:
        """Test if circuit can be simulated successfully"""
        try:
            engine = SimulationEngine()
            
            # Test DC analysis
            dc_results = None
            try:
                dc_results = engine.simulate_dc(circuit)
            except Exception as e:
                print(f"   ⚠️  DC simulation failed: {e}")
            
            # Test transient analysis
            transient_results = None
            try:
                transient_results = engine.simulate_transient(circuit, duration="1ms")
            except Exception as e:
                print(f"   ⚠️  Transient simulation failed: {e}")
            
            # Test AC analysis
            ac_results = None
            try:
                ac_results = engine.simulate_ac(circuit, start_freq="1Hz", stop_freq="1MHz", points=50)
            except Exception as e:
                print(f"   ⚠️  AC simulation failed: {e}")
            
            simulation_data = {
                "dc_success": dc_results is not None,
                "transient_success": transient_results is not None,
                "ac_success": ac_results is not None,
                "dc_results": dc_results,
                "transient_results": transient_results,
                "ac_results": ac_results
            }
            
            # At least one simulation must succeed
            success = any([dc_results, transient_results, ac_results])
            
            return success, simulation_data
            
        except Exception as e:
            return False, {"error": str(e), "traceback": traceback.format_exc()}
    
    def generate_circuit_report(self, circuit: Circuit, simulation_data: Dict[str, Any], 
                              circuit_name: str) -> Tuple[bool, Dict[str, Any]]:
        """Generate comprehensive report for a circuit"""
        try:
            generator = ReportGenerator()
            
            # Create results object for report generation
            from circuit_sim.simulator.results import SimulationResults
            
            # Build SimulationResults from simulation data
            results = SimulationResults(circuit.name)
            
            if simulation_data.get("dc_results"):
                results.dc_results = simulation_data["dc_results"]
            
            if simulation_data.get("transient_results"):
                results.transient_results = simulation_data["transient_results"]
            
            if simulation_data.get("ac_results"):
                results.ac_results = simulation_data["ac_results"]
            
            # Generate different report types
            report_paths = {}
            
            for report_type in ["detailed", "quick", "executive"]:
                try:
                    report_path = self.output_dir / f"{circuit_name}_{report_type}_report.html"
                    
                    report_html = generator.generate_report(
                        circuit=circuit,
                        results=results,
                        report_type=report_type,
                        output_format="html"
                    )
                    
                    # Save to file
                    with open(report_path, 'w') as f:
                        f.write(report_html)
                    
                    report_paths[report_type] = str(report_path)
                    
                    # Get report file size
                    file_size = report_path.stat().st_size
                    print(f"   ✅ {report_type.title()} report: {file_size:,} bytes")
                    
                except Exception as e:
                    print(f"   ❌ {report_type.title()} report failed: {e}")
                    report_paths[report_type] = None
            
            success = any(report_paths.values())
            
            return success, {
                "report_paths": report_paths,
                "report_types_generated": len([p for p in report_paths.values() if p])
            }
            
        except Exception as e:
            return False, {"error": str(e), "traceback": traceback.format_exc()}
    
    def analyze_report_quality(self, report_path: str) -> Dict[str, Any]:
        """Analyze the quality of a generated report"""
        try:
            with open(report_path, 'r') as f:
                content = f.read()
            
            analysis = {
                "file_size": len(content),
                "contains_plotly": "plotly" in content.lower(),
                "contains_charts": "chart" in content.lower() or "plot" in content.lower(),
                "contains_metrics": "metrics" in content.lower() or "analysis" in content.lower(),
                "contains_css": "<style>" in content or "css" in content.lower(),
                "interactive": "onclick" in content.lower() or "plotly" in content.lower(),
                "professional_styling": "bootstrap" in content.lower() or "card" in content.lower()
            }
            
            # Count sections
            sections = content.lower().count("<section>") + content.lower().count("<div class")
            analysis["section_count"] = sections
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def test_single_circuit(self, circuit_file: Path) -> Dict[str, Any]:
        """Test a single circuit comprehensively"""
        circuit_name = f"{circuit_file.parent.parent.name}_{circuit_file.parent.name}"
        
        print(f"\n🔬 Testing {circuit_name} ({circuit_file.relative_to(self.examples_dir)})")
        
        result = {
            "name": circuit_name,
            "file_path": str(circuit_file.relative_to(self.examples_dir)),
            "success": False,
            "errors": []
        }
        
        # Step 1: Load circuit module
        module = self.load_circuit_module(circuit_file)
        if not module:
            result["errors"].append("Failed to load circuit module")
            return result
        
        # Step 2: Extract circuit
        circuit = self.extract_circuit_from_module(module)
        if not circuit:
            result["errors"].append("No Circuit object found in module")
            return result
        
        print(f"   📊 Circuit: {circuit.name} ({len(circuit.components)} components)")
        result["circuit_info"] = {
            "name": circuit.name,
            "component_count": len(circuit.components),
            "net_count": len(circuit.nets)
        }
        
        # Step 3: Test simulation
        sim_success, sim_data = self.test_circuit_simulation(circuit)
        result["simulation"] = sim_data
        
        if not sim_success:
            result["errors"].append("All simulations failed")
            print("   ❌ All simulations failed")
            return result
        
        print(f"   ✅ Simulations: DC={sim_data.get('dc_success', False)}, "
              f"Transient={sim_data.get('transient_success', False)}, "
              f"AC={sim_data.get('ac_success', False)}")
        
        # Step 4: Generate reports
        report_success, report_data = self.generate_circuit_report(circuit, sim_data, circuit_name)
        result["reports"] = report_data
        
        if not report_success:
            result["errors"].append("Report generation failed")
            return result
        
        # Step 5: Analyze report quality
        result["report_analysis"] = {}
        for report_type, report_path in report_data["report_paths"].items():
            if report_path:
                analysis = self.analyze_report_quality(report_path)
                result["report_analysis"][report_type] = analysis
        
        result["success"] = True
        return result
    
    def run_comprehensive_test(self):
        """Run comprehensive test on all example circuits"""
        print("🚀 Starting Comprehensive Report Testing")
        print("=" * 60)
        
        # Discover circuits
        circuit_files = self.discover_circuits()
        self.results["circuits_discovered"] = len(circuit_files)
        
        # Test each circuit
        for circuit_file in circuit_files:
            self.results["circuits_tested"] += 1
            
            try:
                circuit_result = self.test_single_circuit(circuit_file)
                self.results["circuit_results"].append(circuit_result)
                
                if circuit_result["success"]:
                    self.results["successful_reports"] += 1
                else:
                    self.results["failed_reports"] += 1
                    
            except Exception as e:
                self.results["failed_reports"] += 1
                self.results["errors"].append({
                    "circuit": str(circuit_file),
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
                print(f"❌ Unexpected error testing {circuit_file}: {e}")
        
        # Save results
        results_file = self.output_dir / "comprehensive_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        print(f"Circuits discovered: {self.results['circuits_discovered']}")
        print(f"Circuits tested: {self.results['circuits_tested']}")
        print(f"Successful reports: {self.results['successful_reports']}")
        print(f"Failed reports: {self.results['failed_reports']}")
        print(f"Success rate: {self.results['successful_reports']/max(1,self.results['circuits_tested'])*100:.1f}%")
        print(f"\n📁 Results saved to: {results_file}")
        print(f"📁 Reports saved to: {self.output_dir}")
        
        return self.results


if __name__ == "__main__":
    tester = ComprehensiveReportTester()
    results = tester.run_comprehensive_test()
    
    print(f"\n✨ Testing complete! Generated reports for {results['successful_reports']} circuits.")