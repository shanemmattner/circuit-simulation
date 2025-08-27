#!/usr/bin/env python3
"""
Comprehensive validation script for Circuit Simulation Library
Tests all components and provides clear status report
"""

import sys
import subprocess
from pathlib import Path

# ANSI color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def test_imports():
    """Test that all required packages can be imported"""
    print_header("Testing Python Imports")
    
    imports = [
        ("numpy", "NumPy"),
        ("matplotlib", "Matplotlib"),
        ("PySpice", "PySpice"),
        ("circuit_sim", "Circuit Sim Library"),
        ("mcp", "MCP Protocol"),
        ("pydantic", "Pydantic"),
    ]
    
    all_good = True
    for module, name in imports:
        try:
            __import__(module)
            version = None
            if hasattr(__import__(module), '__version__'):
                version = __import__(module).__version__
            if version:
                print_success(f"{name} ({version})")
            else:
                print_success(f"{name}")
        except ImportError as e:
            print_error(f"{name}: {e}")
            all_good = False
    
    return all_good

def test_ngspice():
    """Test ngspice installation and functionality"""
    print_header("Testing NgSpice Installation")
    
    try:
        # Check if ngspice is installed
        result = subprocess.run(['which', 'ngspice'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"NgSpice found at: {result.stdout.strip()}")
        else:
            print_error("NgSpice not found in PATH")
            return False
        
        # Get version
        result = subprocess.run(['ngspice', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[1] if result.stdout else "Unknown"
            print_success(f"NgSpice version: {version_line.strip()}")
        
        # Test PySpice integration
        from PySpice.Spice.NgSpice.Shared import NgSpiceShared
        ngspice = NgSpiceShared.new_instance()
        print_success("PySpice can load NgSpice library")
        
        return True
        
    except Exception as e:
        print_error(f"NgSpice test failed: {e}")
        return False

def test_circuit_simulation():
    """Test basic circuit simulation"""
    print_header("Testing Circuit Simulation")
    
    try:
        from circuit_sim import Circuit
        from circuit_sim.simulator import SimulationEngine
        
        # Create a simple voltage divider
        circuit = Circuit("Test Circuit")
        circuit.add_voltage_source("V1", 1, 0, "10V")
        circuit.add_resistor("R1", 1, 2, "1k")
        circuit.add_resistor("R2", 2, 0, "1k")
        
        print_success(f"Created circuit: {circuit}")
        
        # Run DC simulation
        engine = SimulationEngine()
        results = engine.simulate_dc(circuit)
        
        # Check results
        v_out = results.get_voltage(2)
        expected = 5.0
        
        if abs(v_out - expected) < 0.1:
            print_success(f"DC simulation correct: {v_out:.3f}V ≈ {expected}V")
            return True
        else:
            print_error(f"DC simulation incorrect: {v_out:.3f}V ≠ {expected}V")
            return False
            
    except Exception as e:
        print_error(f"Circuit simulation failed: {e}")
        return False

def test_mcp_server():
    """Test MCP server functionality"""
    print_header("Testing MCP Server")
    
    try:
        from src.circuit_mcp.tools.circuit_tools import CircuitTools
        from src.circuit_mcp.tools.simulation_tools import SimulationTools
        import asyncio
        
        # Create tools
        ct = CircuitTools()
        st = SimulationTools()
        
        # Test circuit creation
        result = ct.create_circuit({"name": "MCP Test"})
        circuit_id = result.get("circuit_id")
        if circuit_id:
            print_success(f"Created circuit via MCP: {circuit_id}")
        else:
            print_error("Failed to create circuit via MCP")
            return False
        
        # Add components
        ct.add_component({
            "circuit_id": circuit_id,
            "component_type": "voltage_source",
            "name": "V1",
            "positive": 1,
            "negative": 0,
            "value": "5V"
        })
        
        ct.add_component({
            "circuit_id": circuit_id,
            "component_type": "resistor",
            "name": "R1",
            "positive": 1,
            "negative": 0,
            "value": "1k"
        })
        
        print_success("Added components via MCP")
        
        # Run simulation
        sim_result = asyncio.run(st.run_dc_simulation({"circuit_id": circuit_id}))
        if sim_result.get("status") == "success":
            print_success("MCP simulation completed")
            return True
        else:
            print_error(f"MCP simulation failed: {sim_result}")
            return False
            
    except Exception as e:
        print_error(f"MCP server test failed: {e}")
        return False

def test_examples():
    """Test that example scripts run without errors"""
    print_header("Testing Example Scripts")
    
    examples = [
        "test_circuit_functions.py",
        "examples/test_docker_ngspice.py",
    ]
    
    all_good = True
    for example in examples:
        try:
            result = subprocess.run(['python', example], 
                                  capture_output=True, text=True,
                                  timeout=10)
            if result.returncode == 0:
                print_success(f"{example}")
            else:
                print_warning(f"{example} (non-zero exit)")
                all_good = False
        except subprocess.TimeoutExpired:
            print_warning(f"{example} (timeout)")
        except Exception as e:
            print_error(f"{example}: {e}")
            all_good = False
    
    return all_good

def check_environment():
    """Check environment setup"""
    print_header("Environment Check")
    
    # Python version
    import sys
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 10):
        print_success(f"Python {py_version}")
    else:
        print_warning(f"Python {py_version} (3.10+ recommended)")
    
    # Check for virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success("Running in virtual environment")
    else:
        print_warning("Not in virtual environment")
    
    # Check for uv
    result = subprocess.run(['which', 'uv'], capture_output=True, text=True)
    if result.returncode == 0:
        print_success("uv package manager available")
    else:
        print_warning("uv not found (optional)")
    
    return True

def main():
    """Run all validation tests"""
    print(f"\n{BOLD}{BLUE}🔬 Circuit Simulation Library - Setup Validation{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = []
    
    # Run all tests
    results.append(("Environment", check_environment()))
    results.append(("Imports", test_imports()))
    results.append(("NgSpice", test_ngspice()))
    results.append(("Circuit Simulation", test_circuit_simulation()))
    results.append(("MCP Server", test_mcp_server()))
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    all_passed = True
    for name, passed in results:
        if passed:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")
            all_passed = False
    
    print()
    if all_passed:
        print(f"{GREEN}{BOLD}🎉 All validations passed! Your setup is working correctly.{RESET}")
        print(f"\n{BOLD}Next steps:{RESET}")
        print("1. Run example circuits: uv run python examples/simulation_demo.py")
        print("2. Start MCP server: uv run python run_mcp_server.py")
        print("3. Create your own circuits in Python or via MCP")
        return 0
    else:
        print(f"{RED}{BOLD}⚠️  Some validations failed. Please check the errors above.{RESET}")
        print(f"\n{BOLD}Troubleshooting:{RESET}")
        print("1. Ensure all dependencies are installed: uv pip install -r requirements.txt")
        print("2. Check ngspice installation: brew install ngspice")
        print("3. Review docs/MACOS_SETUP.md for detailed instructions")
        return 1

if __name__ == "__main__":
    sys.exit(main())