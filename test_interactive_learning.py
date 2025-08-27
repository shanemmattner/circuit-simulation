#!/usr/bin/env python3
"""
Test script for interactive learning environment.
Verifies all dependencies and basic functionality.
"""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Test all required imports for interactive learning."""
    print("🧪 Testing Interactive Learning Environment")
    print("=" * 50)
    
    required_modules = [
        ("circuit_sim", "Circuit simulation library"),
        ("ipywidgets", "Interactive widgets"), 
        ("plotly", "Interactive plotting"),
        ("plotly.graph_objects", "Plotly graph objects"),
        ("jupyter", "Jupyter notebook environment"),
        ("IPython.display", "IPython display utilities"),
        ("numpy", "Numerical computing"),
        ("pandas", "Data analysis (for reports)"),
    ]
    
    results = []
    for module_name, description in required_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name:<20} - {description}")
            results.append(True)
        except ImportError as e:
            print(f"❌ {module_name:<20} - FAILED: {e}")
            results.append(False)
    
    return all(results)

def test_circuit_simulation():
    """Test basic circuit simulation functionality."""
    print("\n🔧 Testing Circuit Simulation")
    print("-" * 30)
    
    try:
        from circuit_sim import Circuit
        
        # Create simple test circuit
        circuit = Circuit("Test Circuit")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_resistor("R1", 1, 0, "1000")
        
        print(f"✅ Circuit created: {circuit.name}")
        print(f"✅ Components: {len(circuit.components)}")
        print(f"✅ Nodes: {len(circuit.nodes)}")
        
        # Test built-in simulation method
        results = circuit.simulate(analysis="dc")
        
        voltage = results.voltage(1)[0] if results.voltage(1) else None
        current = results.current("V1")[0] if results.current("V1") else None
        
        print(f"✅ DC simulation successful")
        print(f"   Voltage at node 1: {voltage:.2f}V")
        print(f"   Current through V1: {abs(current)*1000:.1f}mA")
        
        return True
        
    except Exception as e:
        print(f"❌ Circuit simulation failed: {e}")
        return False

def test_interactive_components():
    """Test interactive widget creation."""
    print("\n🎛️ Testing Interactive Components")
    print("-" * 35)
    
    try:
        import ipywidgets as widgets
        from IPython.display import HTML
        import plotly.graph_objects as go
        
        # Test widget creation
        slider = widgets.FloatSlider(
            value=1000,
            min=100,
            max=10000,
            description='Resistance:'
        )
        print("✅ Widget slider created")
        
        # Test HTML display
        html = HTML("<p>Test HTML content</p>")
        print("✅ HTML display object created")
        
        # Test plotly figure
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['A', 'B'], y=[1, 2]))
        print("✅ Plotly figure created")
        
        return True
        
    except Exception as e:
        print(f"❌ Interactive components failed: {e}")
        return False

def test_notebook_structure():
    """Test that notebook files exist and are valid."""
    print("\n📓 Testing Notebook Structure")  
    print("-" * 30)
    
    base_path = Path("docs/learning_modules/track1_dc_analysis/module_1.1_dc_basics")
    
    expected_notebooks = [
        "explain_dc_concept.ipynb",
        "try_voltage_prediction.ipynb", 
        "build_first_circuit.ipynb",
        "challenge_ohms_law.ipynb",
        "reflect_understanding.ipynb"
    ]
    
    all_exist = True
    for notebook in expected_notebooks:
        notebook_path = base_path / notebook
        if notebook_path.exists():
            print(f"✅ {notebook}")
        else:
            print(f"❌ {notebook} - NOT FOUND")
            all_exist = False
    
    print(f"\n📁 Module structure: {'✅ Complete' if all_exist else '❌ Incomplete'}")
    return all_exist

def main():
    """Run all tests."""
    print("🚀 Interactive Circuit Learning Environment Test")
    print("=" * 60)
    
    tests = [
        ("Module imports", test_imports),
        ("Circuit simulation", test_circuit_simulation), 
        ("Interactive widgets", test_interactive_components),
        ("Notebook structure", test_notebook_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for (test_name, _), result in zip(tests, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
    
    overall_success = all(results)
    print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🚀 Ready to launch interactive learning!")
        print("🎓 Students can now use the scaffolded learning modules!")
    else:
        print("\n🔧 Please fix failing tests before using learning modules.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)