#!/usr/bin/env python3
"""
Debug Chart Generation

This script debugs why charts aren't appearing in reports.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.reports.charts.plotly_charts import PlotlyChartGenerator


def debug_chart_generation():
    """Debug the chart generation process step by step"""
    print("🔍 Debugging Chart Generation")
    print("=" * 50)
    
    # Create a simple circuit
    circuit = Circuit("Debug Circuit")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_resistor("R2", node1=2, node2="gnd", resistance="1k")
    
    print(f"✅ Created circuit: {circuit.name}")
    
    # Run simulation
    engine = SimulationEngine()
    try:
        dc_results = engine.simulate_dc(circuit)
        print("✅ DC simulation successful")
        print(f"   Nodes: {dc_results.nodes}")
        
        # Check what voltage data we have
        for node in dc_results.nodes:
            voltage = dc_results.voltage(node)
            print(f"   Node {node}: {voltage}")
        
    except Exception as e:
        print(f"❌ DC simulation failed: {e}")
        return
    
    # Test chart generation directly
    print("\n🎨 Testing Chart Generation")
    print("-" * 30)
    
    chart_generator = PlotlyChartGenerator()
    
    try:
        charts = chart_generator.create_charts(dc_results, circuit)
        print(f"✅ Charts created: {len(charts)} charts")
        
        for chart_name, chart_fig in charts.items():
            print(f"   📊 {chart_name}: {type(chart_fig)}")
            
            # Test HTML conversion
            if hasattr(chart_fig, "to_html"):
                try:
                    html = chart_fig.to_html(include_plotlyjs="cdn")
                    print(f"      ✅ HTML conversion successful: {len(html)} chars")
                    
                    # Save individual chart for inspection
                    with open(f"debug_chart_{chart_name}.html", 'w') as f:
                        f.write(html)
                    print(f"      💾 Saved: debug_chart_{chart_name}.html")
                    
                except Exception as e:
                    print(f"      ❌ HTML conversion failed: {e}")
            else:
                print(f"      ❌ Object doesn't have to_html method")
                
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test full report generation with debugging
    print("\n📄 Testing Full Report Generation")
    print("-" * 35)
    
    from circuit_sim.reports import ReportGenerator
    from circuit_sim.simulator.results import SimulationResults
    
    # Create results object
    results = SimulationResults(circuit.name)
    results.dc_results = dc_results
    
    generator = ReportGenerator()
    
    try:
        # Test the internal data preparation
        print("🔍 Testing report data preparation...")
        report_data = generator._prepare_report_data(circuit, results, "detailed")
        
        print(f"   ✅ Report data keys: {list(report_data.keys())}")
        
        if "charts" in report_data:
            charts = report_data["charts"]
            print(f"   📊 Charts in report data: {len(charts)} charts")
            for chart_name in charts.keys():
                print(f"      • {chart_name}")
        else:
            print("   ❌ No 'charts' key in report data")
            
        # Test HTML builder
        print("\n🏗️  Testing HTML builder...")
        from circuit_sim.reports.builders.html_builder import HTMLBuilder
        
        # Get template environment
        builder = HTMLBuilder(generator.env)
        context = builder._prepare_template_context(report_data)
        
        print(f"   ✅ Template context keys: {list(context.keys())}")
        
        if "charts_html" in context:
            charts_html = context["charts_html"]
            print(f"   📊 Charts HTML: {len(charts_html)} charts converted")
            for chart_name, chart_html in charts_html.items():
                print(f"      • {chart_name}: {len(chart_html)} chars")
                
                # Save for inspection
                with open(f"debug_chart_html_{chart_name}.html", 'w') as f:
                    f.write(chart_html)
        else:
            print("   ❌ No 'charts_html' key in context")
        
    except Exception as e:
        print(f"❌ Report generation debug failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_chart_generation()