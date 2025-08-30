#!/usr/bin/env python3
"""
Circuit-Synth to Circuit-Simulation Demo with Plots and Reports

This script demonstrates the complete workflow:
1. You run circuit-synth to generate a design
2. This script automatically loads the JSON and simulates it
3. Generates professional plots and reports
"""

import json
import sys
from pathlib import Path
import webbrowser

# Add circuit-simulation to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim.circuit_synth_integration import simulate_from_circuit_synth, CircuitSynthError
from circuit_sim.reports import ReportGenerator


def simulate_and_plot(json_path: Path):
    """Load circuit-synth JSON, simulate, and generate plots/reports."""
    
    print(f"🔄 Processing circuit from: {json_path.name}")
    print("=" * 60)
    
    try:
        # Load circuit-synth JSON output
        with open(json_path, "r") as f:
            circuit_data = json.load(f)
        
        circuit_name = circuit_data.get('name', 'Unknown Circuit')
        components = circuit_data.get('components', {})
        nets = circuit_data.get('nets', {})
        
        print(f"📋 Circuit: {circuit_name}")
        print(f"   • Components: {len(components)}")
        print(f"   • Nets: {len(nets)}")
        print()
        
        if len(components) == 0:
            # Handle hierarchical circuits
            subcircuits = circuit_data.get('subcircuits', [])
            if subcircuits:
                print("🏗️  Hierarchical circuit detected:")
                total_components = 0
                for sub in subcircuits:
                    sub_components = len(sub.get('components', {}))
                    total_components += sub_components
                    print(f"   • {sub.get('name', 'Unknown')}: {sub_components} components")
                print(f"   • Total components: {total_components}")
                print("\n⚠️  Note: This demo works best with flat circuits.")
                print("   For hierarchical circuits, try a simpler design first.")
                return
        
        print("🔄 Running circuit-simulation integration...")
        print("   • Smart SPICE model mapping")
        print("   • Component resolution")
        print("   • DC analysis")
        print()
        
        # Use our integration to simulate the circuit
        results = simulate_from_circuit_synth(circuit_data)
        
        print("✅ Simulation completed!")
        print()
        
        # Show voltage results
        if hasattr(results, 'voltages') and results.voltages:
            print("📊 Node Voltages:")
            for node_name, voltage in results.voltages.items():
                try:
                    if hasattr(voltage, '__iter__') and len(voltage) > 0:
                        v_val = complex(voltage[0])
                    else:
                        v_val = complex(voltage)
                    
                    if abs(v_val.imag) < 1e-9:  # Essentially real
                        print(f"   • {node_name}: {v_val.real:.3f} V")
                    else:
                        print(f"   • {node_name}: {v_val.real:.3f} + {v_val.imag:.3f}j V")
                except:
                    print(f"   • {node_name}: {str(voltage)}")
        
        print()
        
        # Generate interactive plots and reports
        print("📈 Generating plots and reports...")
        
        # Create a simple plot of the DC voltages
        try:
            import plotly.graph_objects as go
            import plotly.io as pio
            
            if hasattr(results, 'voltages') and results.voltages:
                # Extract real voltage values
                nodes = []
                voltages_real = []
                
                for node_name, voltage in results.voltages.items():
                    try:
                        if hasattr(voltage, '__iter__') and len(voltage) > 0:
                            v_val = complex(voltage[0]).real
                        else:
                            v_val = complex(voltage).real
                        nodes.append(node_name)
                        voltages_real.append(v_val)
                    except:
                        continue
                
                if nodes and voltages_real:
                    # Create voltage bar chart
                    fig = go.Figure(data=[
                        go.Bar(
                            x=nodes,
                            y=voltages_real,
                            marker_color='lightblue',
                            text=[f"{v:.3f}V" for v in voltages_real],
                            textposition='auto',
                        )
                    ])
                    
                    fig.update_layout(
                        title=f"DC Analysis Results - {circuit_name}",
                        xaxis_title="Circuit Nodes",
                        yaxis_title="Voltage (V)",
                        template="plotly_white",
                        showlegend=False,
                        height=500,
                        font=dict(size=12)
                    )
                    
                    # Get plot as HTML div for embedding
                    plot_div = fig.to_html(include_plotlyjs='cdn', div_id="voltage_plot")
                    
                    # Also save standalone plot
                    plot_file = f"{circuit_name}_voltage_plot.html"
                    fig.write_html(plot_file)
                    print(f"   ✅ Interactive plot saved: {plot_file}")
                    
        except ImportError:
            print("   ⚠️  Plotly not available - skipping interactive plots")
        except Exception as e:
            print(f"   ⚠️  Plot generation error: {e}")
        
        # Generate professional report
        try:
            from circuit_sim.circuit import Circuit
            
            # Try to get the circuit object from the integration
            print("   📄 Generating professional report...")
            
            # Create a basic report with available data
            # Check if we have a plot to embed
            plot_html = ""
            if 'plot_div' in locals():
                plot_html = f"""
    <div class="section">
        <h3>📈 Interactive Voltage Plot</h3>
        {plot_div}
    </div>
                """
            
            report_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Circuit Analysis Report - {circuit_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
        .section {{ margin: 20px 0; }}
        .voltage-table {{ border-collapse: collapse; width: 100%; }}
        .voltage-table th, .voltage-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .voltage-table th {{ background-color: #f2f2f2; }}
        .success {{ color: #28a745; }}
        .info {{ color: #17a2b8; }}
        .plot-container {{ background: #f8f9fa; padding: 15px; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Circuit Analysis Report</h1>
        <h2 class="info">{circuit_name}</h2>
        <p><strong>Analysis Type:</strong> DC Operating Point</p>
        <p><strong>Generated:</strong> {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    {plot_html}
    
    <div class="section">
        <h3>Circuit Summary</h3>
        <ul>
            <li><strong>Components:</strong> {len(components)}</li>
            <li><strong>Nets:</strong> {len(nets)}</li>
            <li><strong>Simulation Status:</strong> <span class="success">✅ Successful</span></li>
        </ul>
    </div>
    
    <div class="section">
        <h3>Component List</h3>
        <table class="voltage-table">
            <tr><th>Reference</th><th>Type</th><th>Value</th><th>Symbol</th></tr>
            {''.join(f'<tr><td>{ref}</td><td>{comp.get("symbol", "").split(":")[-1]}</td><td>{comp.get("value", "N/A")}</td><td>{comp.get("symbol", "N/A")}</td></tr>' 
                    for ref, comp in components.items())}
        </table>
    </div>
            """
            
            if hasattr(results, 'voltages') and results.voltages:
                voltage_rows = ""
                for node_name, voltage in results.voltages.items():
                    try:
                        if hasattr(voltage, '__iter__') and len(voltage) > 0:
                            v_val = complex(voltage[0]).real
                        else:
                            v_val = complex(voltage).real
                        voltage_rows += f"<tr><td>{node_name}</td><td>{v_val:.6f} V</td></tr>"
                    except:
                        voltage_rows += f"<tr><td>{node_name}</td><td>{str(voltage)}</td></tr>"
                
                report_content += f"""
    <div class="section">
        <h3>DC Analysis Results</h3>
        <table class="voltage-table">
            <tr><th>Node</th><th>Voltage</th></tr>
            {voltage_rows}
        </table>
    </div>
                """
            
            report_content += """
    <div class="section">
        <h3>Integration Notes</h3>
        <p>This circuit was generated by <strong>circuit-synth</strong> and simulated using <strong>circuit-simulation</strong> with intelligent SPICE model mapping.</p>
        <ul>
            <li>Component symbols automatically mapped to SPICE models</li>
            <li>KiCad-Spice-Library integration (50K+ models)</li>
            <li>Professional fallback models for unknown components</li>
        </ul>
    </div>
</body>
</html>
            """
            
            report_file = f"{circuit_name}_analysis_report.html"
            with open(report_file, 'w') as f:
                f.write(report_content)
            
            print(f"   ✅ Professional report saved: {report_file}")
            
            # Open the report automatically
            print(f"\n🌐 Opening report in browser...")
            webbrowser.open(f"file://{Path(report_file).absolute()}")
            
        except Exception as e:
            print(f"   ⚠️  Report generation error: {e}")
        
        print()
        print("🎯 Integration Demo Complete!")
        print(f"   📄 Report: {circuit_name}_analysis_report.html")
        if 'plot_file' in locals():
            print(f"   📈 Plot: {plot_file}")
        print("   🔗 Files opened in browser automatically")
        
    except CircuitSynthError as e:
        print(f"❌ Circuit-synth integration error: {e.message}")
        return
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"   Type: {type(e).__name__}")
        return


def main():
    """Main demo function."""
    print("🚀 Circuit-Synth → Circuit-Simulation Demo")
    print("   With Interactive Plots and Professional Reports")
    print("=" * 60)
    print()
    print("Instructions:")
    print("1. First, run circuit-synth to generate a circuit:")
    print("   cd submodules/circuit-synth/example_project/circuit-synth")
    print("   uv run python main.py")
    print()
    print("2. Then run this script to simulate and generate reports:")
    print("   uv run python demo_circuit_synth_with_plots.py <json_file>")
    print()
    
    # Check for command line argument
    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])
        if json_path.exists():
            simulate_and_plot(json_path)
        else:
            print(f"❌ File not found: {json_path}")
    else:
        # Look for common circuit-synth output files
        possible_files = [
            "ESP32_C6_Dev_Board.json",
            "submodules/circuit-synth/example_project/circuit-synth/ESP32_C6_Dev_Board.json",
        ]
        
        found_file = None
        for file_path in possible_files:
            if Path(file_path).exists():
                found_file = Path(file_path)
                break
        
        if found_file:
            print(f"📄 Found circuit file: {found_file}")
            print("   Processing automatically...")
            print()
            simulate_and_plot(found_file)
        else:
            print("📋 No circuit files found. Please:")
            print("   1. Generate a circuit with circuit-synth")
            print("   2. Run: uv run python demo_circuit_synth_with_plots.py <circuit.json>")


if __name__ == "__main__":
    main()