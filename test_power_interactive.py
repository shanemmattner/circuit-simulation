#!/usr/bin/env python3
"""
🔋 Interactive Power Analysis Test Script

This script demonstrates comprehensive power analysis capabilities with:
- Multiple test circuits with different power characteristics  
- Interactive Plotly visualizations and reports
- Component rating validation
- Power optimization suggestions
- Professional HTML reports with embedded charts

Run this script to see all power analysis features in action!
"""

import sys
from pathlib import Path
import webbrowser
from datetime import datetime

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.validation import PowerAnalyzer
from circuit_sim.reports import ReportGenerator

def create_test_circuits():
    """Create various test circuits with different power characteristics."""
    circuits = []
    
    # Circuit 1: Simple resistor - normal power
    circuit1 = Circuit("Simple Resistor Test")
    circuit1.add_voltage_source("V1", 1, 0, "5V")
    circuit1.add_resistor("R1", 1, 0, "100")  # 100Ω = 0.25W
    circuits.append(("Simple", circuit1, {"R1": 0.5}))  # 0.5W rating - safe
    
    # Circuit 2: Voltage divider - moderate power
    circuit2 = Circuit("Voltage Divider")  
    circuit2.add_voltage_source("V1", 1, 0, "12V")
    circuit2.add_resistor("R1", 1, 2, "1k")   # 1kΩ
    circuit2.add_resistor("R2", 2, 0, "2k")   # 2kΩ
    circuit2.add_resistor("R3", 1, 3, "500")  # 500Ω parallel branch
    circuit2.add_resistor("R4", 3, 0, "1.5k") # 1.5kΩ
    circuits.append(("Voltage Divider", circuit2, {
        "R1": 0.25, "R2": 0.25, "R3": 0.5, "R4": 0.25  # Mixed ratings
    }))
    
    # Circuit 3: High power - triggers warnings
    circuit3 = Circuit("High Power Load")
    circuit3.add_voltage_source("V1", 1, 0, "15V") 
    circuit3.add_resistor("R1", 1, 0, "10")    # 10Ω = 22.5W - high power!
    circuits.append(("High Power", circuit3, {"R1": 1.0}))  # 1W rating - will fail!
    
    # Circuit 4: Complex circuit with mixed components
    circuit4 = Circuit("Mixed Component Circuit")
    circuit4.add_voltage_source("V1", 1, 0, "9V")
    circuit4.add_resistor("R1", 1, 2, "220")    # 220Ω
    circuit4.add_resistor("R2", 2, 3, "470")    # 470Ω  
    circuit4.add_resistor("R3", 3, 0, "1k")     # 1kΩ
    circuit4.add_capacitor("C1", 2, 0, "100u")  # 100μF (DC analysis = 0 power)
    circuit4.add_inductor("L1", 1, 4, "10m")    # 10mH (DC analysis = 0 power)  
    circuit4.add_resistor("R4", 4, 0, "330")    # 330Ω
    circuits.append(("Mixed Components", circuit4, {
        "R1": 0.25, "R2": 0.125, "R3": 0.25, "R4": 0.5
    }))
    
    return circuits

def analyze_circuit_power(name, circuit, component_ratings):
    """Analyze power for a single circuit with detailed reporting."""
    print(f"\n🔋 Analyzing: {name}")
    print("=" * (len(name) + 15))
    
    try:
        # Simulate circuit
        engine = SimulationEngine()  
        results = engine.simulate_dc(circuit)
        
        # Show basic simulation results
        print(f"✅ DC simulation completed")
        print(f"📊 Node voltages:")
        for node_id in sorted(results.nodes):
            voltage = results.voltage(node_id)
            if voltage is not None:
                print(f"   V({node_id}) = {voltage[0]:.3f}V")
        
        # Power analysis with custom thresholds
        analyzer = PowerAnalyzer(
            power_warning_threshold=0.5,   # 500mW warning
            power_error_threshold=5.0      # 5W error  
        )
        power_analysis = analyzer.analyze_power(circuit, results, component_ratings)
        
        # Results summary
        status = "✅ VALID" if power_analysis.is_valid else "❌ ISSUES FOUND"
        print(f"\n🔍 Power Analysis: {status}")
        print(f"📈 Total Power Dissipated: {power_analysis.total_power:.3f}W")
        
        # Component breakdown
        print(f"\n💡 Component Power Breakdown:")
        for comp_name, info in power_analysis.component_power.items():
            rating_info = ""
            if info.rating:
                utilization = (info.power / info.rating) * 100
                if utilization > 100:
                    status_icon = "❌"
                elif utilization > 80:
                    status_icon = "⚠️"
                else:
                    status_icon = "✅"
                rating_info = f" [{info.rating}W rated, {utilization:.1f}% {status_icon}]"
            
            print(f"   {comp_name}: {info.power:.3f}W @ {info.voltage:.2f}V, {info.current:.3f}A ({info.method}){rating_info}")
        
        # Source power
        print(f"\n🔌 Source Power:")
        for source_name, info in power_analysis.source_power.items():
            supplying = "supplying" if info.power < 0 else "consuming"
            print(f"   {source_name}: {abs(info.power):.3f}W ({supplying})")
            
        # Power budget
        budget = power_analysis.power_budget
        print(f"\n📊 Power Budget:")
        print(f"   Supplied: {budget['total_supplied']:.3f}W")
        print(f"   Dissipated: {budget['total_dissipated']:.3f}W") 
        print(f"   Efficiency: {budget['efficiency']*100:.1f}%")
        print(f"   Balance Error: {budget['balance']:.6f}W")
        
        # Issues and warnings
        if power_analysis.issues:
            print(f"\n❌ Issues ({len(power_analysis.issues)}):")
            for issue in power_analysis.issues:
                print(f"   • {issue.message}")
                if issue.suggestion:
                    print(f"     💡 {issue.suggestion}")
                    
        if power_analysis.warnings:
            print(f"\n⚠️  Warnings ({len(power_analysis.warnings)}):")
            for warning in power_analysis.warnings:
                print(f"   • {warning.message}")
                if warning.suggestion:
                    print(f"     💡 {warning.suggestion}")
        
        return results, power_analysis
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None, None

def create_power_visualization(circuits_data):
    """Create interactive Plotly visualizations for power analysis."""
    try:
        import plotly.graph_objects as go
        import plotly.subplots as sp
        from plotly.offline import plot
        
        print(f"\n📊 Creating Interactive Plotly Visualizations...")
        
        # Extract data for plotting
        circuit_names = []
        total_powers = []
        component_counts = []
        max_component_powers = []
        efficiencies = []
        
        detailed_data = {}  # For component-level breakdown
        
        for name, circuit, ratings, results, power_analysis in circuits_data:
            if power_analysis is None:
                continue
                
            circuit_names.append(name)
            total_powers.append(power_analysis.total_power)
            component_counts.append(len(power_analysis.component_power))
            
            # Find max component power
            max_power = max([info.power for info in power_analysis.component_power.values()], default=0)
            max_component_powers.append(max_power)
            
            efficiencies.append(power_analysis.power_budget['efficiency'] * 100)
            
            # Store detailed component data
            detailed_data[name] = {
                'components': list(power_analysis.component_power.keys()),
                'powers': [info.power for info in power_analysis.component_power.values()],
                'voltages': [info.voltage for info in power_analysis.component_power.values()],
                'currents': [info.current for info in power_analysis.component_power.values()]
            }
        
        # Create subplots
        fig = sp.make_subplots(
            rows=2, cols=2,
            subplot_titles=('Total Power Dissipation', 'Component Power Breakdown', 
                          'Power Efficiency', 'Voltage vs Current'),
            specs=[[{"secondary_y": False}, {"type": "bar"}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Plot 1: Total power comparison
        fig.add_trace(
            go.Bar(name='Total Power', x=circuit_names, y=total_powers,
                  marker_color='lightblue', text=[f'{p:.3f}W' for p in total_powers],
                  textposition='auto'),
            row=1, col=1
        )
        
        # Plot 2: Component power breakdown (stacked bar)
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3']
        for i, (name, data) in enumerate(detailed_data.items()):
            for j, (comp, power) in enumerate(zip(data['components'], data['powers'])):
                fig.add_trace(
                    go.Bar(name=f'{name}-{comp}' if len(detailed_data) > 1 else comp,
                          x=[name], y=[power],
                          marker_color=colors[j % len(colors)],
                          text=f'{power:.3f}W', textposition='auto',
                          showlegend=True),
                    row=1, col=2
                )
        
        # Plot 3: Efficiency comparison
        fig.add_trace(
            go.Scatter(x=circuit_names, y=efficiencies, mode='markers+lines',
                      marker=dict(size=12, color='green'),
                      name='Efficiency (%)', text=[f'{e:.1f}%' for e in efficiencies]),
            row=2, col=1
        )
        
        # Plot 4: V-I characteristics (scatter plot)
        for name, data in detailed_data.items():
            fig.add_trace(
                go.Scatter(x=data['currents'], y=data['voltages'], 
                          mode='markers', name=f'{name} Components',
                          marker=dict(size=10), text=data['components']),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title_text="🔋 Circuit Power Analysis Dashboard",
            title_x=0.5,
            height=800,
            showlegend=True
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Circuit", row=1, col=1)
        fig.update_yaxes(title_text="Power (W)", row=1, col=1)
        
        fig.update_xaxes(title_text="Circuit", row=1, col=2)
        fig.update_yaxes(title_text="Component Power (W)", row=1, col=2)
        
        fig.update_xaxes(title_text="Circuit", row=2, col=1)
        fig.update_yaxes(title_text="Efficiency (%)", row=2, col=1)
        
        fig.update_xaxes(title_text="Current (A)", row=2, col=2)
        fig.update_yaxes(title_text="Voltage (V)", row=2, col=2)
        
        # Save interactive HTML
        output_file = "power_analysis_report.html"
        plot(fig, filename=output_file, auto_open=False)
        
        print(f"✅ Interactive visualization saved to: {output_file}")
        return output_file
        
    except ImportError:
        print("⚠️  Plotly not available. Install with: pip install plotly")
        return None
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return None

def create_html_report(circuits_data):
    """Create a comprehensive HTML report with power analysis."""
    try:
        # Create HTML content
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🔋 Power Analysis Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .circuit {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
        .power-info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0; }}
        .power-card {{ background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }}
        .component {{ font-family: monospace; margin: 5px 0; }}
        .valid {{ color: #27ae60; }}
        .warning {{ color: #f39c12; }}
        .error {{ color: #e74c3c; }}
        .summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #3498db; color: white; }}
        .status-ok {{ background-color: #d4edda; }}
        .status-warning {{ background-color: #fff3cd; }}
        .status-error {{ background-color: #f8d7da; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔋 Circuit Power Analysis Report</h1>
        <div class="summary">
            <h3>📊 Report Summary</h3>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Circuits Analyzed:</strong> {len([d for d in circuits_data if d[4] is not None])}</p>
            <p><strong>Total Components:</strong> {sum(len(d[4].component_power) for d in circuits_data if d[4] is not None)}</p>
        </div>
"""
        
        # Add each circuit analysis
        for name, circuit, ratings, results, power_analysis in circuits_data:
            if power_analysis is None:
                continue
                
            status_class = "valid" if power_analysis.is_valid else "error"
            status_text = "✅ Valid" if power_analysis.is_valid else "❌ Issues Found"
            
            html_content += f"""
        <div class="circuit">
            <h2>{name} Circuit</h2>
            <p class="{status_class}"><strong>Status:</strong> {status_text}</p>
            
            <div class="power-info">
                <div class="power-card">
                    <h4>⚡ Total Power</h4>
                    <p style="font-size: 1.5em; color: #2c3e50;">{power_analysis.total_power:.3f}W</p>
                </div>
                <div class="power-card">
                    <h4>📊 Power Budget</h4>
                    <p>Supplied: {power_analysis.power_budget['total_supplied']:.3f}W</p>
                    <p>Efficiency: {power_analysis.power_budget['efficiency']*100:.1f}%</p>
                </div>
                <div class="power-card">
                    <h4>🔧 Components</h4>
                    <p>{len([comp for comp in circuit.components if comp.get('type') not in ['voltage_source', 'current_source']])} total</p>
                    <p>{len(power_analysis.component_power)} analyzed</p>
                    <p>Max: {max([info.power for info in power_analysis.component_power.values()], default=0):.3f}W</p>
                </div>
            </div>
            
            <h3>💡 Component Analysis</h3>
            <table>
                <tr><th>Component</th><th>Power</th><th>Voltage</th><th>Current</th><th>Method</th><th>Rating</th><th>Utilization</th></tr>
"""
            
            # Add component details
            for comp_name, info in power_analysis.component_power.items():
                utilization = ""
                row_class = ""
                if info.rating:
                    util_pct = (info.power / info.rating) * 100
                    utilization = f"{util_pct:.1f}%"
                    if util_pct > 100:
                        row_class = "status-error"
                    elif util_pct > 80:
                        row_class = "status-warning"
                    else:
                        row_class = "status-ok"
                
                html_content += f"""
                <tr class="{row_class}">
                    <td>{comp_name}</td>
                    <td>{info.power:.3f}W</td>
                    <td>{info.voltage:.2f}V</td>
                    <td>{info.current:.3f}A</td>
                    <td>{info.method}</td>
                    <td>{info.rating or 'N/A'}W</td>
                    <td>{utilization}</td>
                </tr>
"""
            
            html_content += "</table>"
            
            # Add issues and warnings
            if power_analysis.issues:
                html_content += "<h3 class='error'>❌ Issues</h3><ul>"
                for issue in power_analysis.issues:
                    html_content += f"<li>{issue.message}"
                    if issue.suggestion:
                        html_content += f"<br><em>💡 {issue.suggestion}</em>"
                    html_content += "</li>"
                html_content += "</ul>"
                
            if power_analysis.warnings:
                html_content += "<h3 class='warning'>⚠️ Warnings</h3><ul>"
                for warning in power_analysis.warnings:
                    html_content += f"<li>{warning.message}"
                    if warning.suggestion:
                        html_content += f"<br><em>💡 {warning.suggestion}</em>"
                    html_content += "</li>"
                html_content += "</ul>"
            
            html_content += "</div>"
        
        html_content += """
    </div>
</body>
</html>"""
        
        # Save report
        report_file = "power_analysis_detailed_report.html"
        with open(report_file, 'w') as f:
            f.write(html_content)
            
        print(f"✅ Detailed HTML report saved to: {report_file}")
        return report_file
        
    except Exception as e:
        print(f"❌ HTML report generation failed: {e}")
        return None

def main():
    """Main test function."""
    print("🔋 Interactive Power Analysis Test Suite")
    print("=" * 50)
    print("This script will:")
    print("  • Analyze 4 different test circuits")
    print("  • Test component rating validation")
    print("  • Generate interactive Plotly visualizations")
    print("  • Create comprehensive HTML reports")
    print("  • Open results in your web browser")
    print("\nStarting analysis...\n")
    
    # Create test circuits
    test_circuits = create_test_circuits()
    circuits_data = []
    
    # Analyze each circuit
    for name, circuit, ratings in test_circuits:
        results, power_analysis = analyze_circuit_power(name, circuit, ratings)
        circuits_data.append((name, circuit, ratings, results, power_analysis))
    
    print(f"\n🎯 Analysis Summary")
    print("=" * 20)
    valid_circuits = sum(1 for _, _, _, _, pa in circuits_data if pa and pa.is_valid)
    total_circuits = len([pa for _, _, _, _, pa in circuits_data if pa is not None])
    print(f"Circuits analyzed: {total_circuits}")
    print(f"Valid circuits: {valid_circuits}")
    print(f"Issues found: {total_circuits - valid_circuits}")
    
    # Generate visualizations
    visualization_file = create_power_visualization(circuits_data)
    report_file = create_html_report(circuits_data)
    
    # Open results in browser
    if report_file:
        print(f"\n🌐 Opening detailed report in browser...")
        try:
            webbrowser.open(f"file://{Path(report_file).absolute()}")
        except:
            print(f"Could not open browser. Manual open: {Path(report_file).absolute()}")
    
    if visualization_file:
        print(f"🌐 Opening interactive visualization in browser...")
        try:
            webbrowser.open(f"file://{Path(visualization_file).absolute()}")
        except:
            print(f"Could not open browser. Manual open: {Path(visualization_file).absolute()}")
    
    print(f"\n✨ Test completed successfully!")
    print(f"📁 Files generated:")
    if report_file:
        print(f"   • {report_file} (detailed HTML report)")
    if visualization_file:
        print(f"   • {visualization_file} (interactive Plotly dashboard)")
    
    return 0

if __name__ == "__main__":
    exit(main())