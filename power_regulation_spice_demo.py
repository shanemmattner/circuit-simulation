#!/usr/bin/env python3
"""
Enhanced Power Regulation Demo - Real SPICE Simulation

Demonstrates complete circuit-synth → SPICE → circuit-simulation workflow
Tests actual SPICE simulation with AMS1117-3.3 power regulation analysis.
"""

import sys
import os
import subprocess

# Add circuit-synth to Python path
sys.path.insert(0, 'submodules/circuit-synth/src')
sys.path.insert(0, 'src')

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
except ImportError:
    print("📦 Installing plotly...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'plotly'])
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.offline as pyo

from circuit_synth import *
from circuit_sim.circuit_synth_integration import simulate_from_spice, CircuitSynthError

@circuit(name="ESP32_Power_Regulation")
def esp32_power_regulation():
    """ESP32 power regulation circuit with AMS1117-3.3 regulator"""
    
    # Create nets
    vbus = Net('VBUS')        # 5V USB input
    vcc_3v3 = Net('VCC_3V3')  # 3.3V regulated output
    gnd = Net('GND')          # Ground
    
    # AMS1117-3.3 voltage regulator
    regulator = Component(
        symbol="Regulator_Linear:AMS1117-3.3", 
        ref="U1",
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2"
    )
    
    # Input capacitor (10µF ceramic for input filtering)
    cap_in = Component(
        symbol="Device:C", 
        ref="C1", 
        value="10uF", 
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    
    # Output capacitor (22µF tantalum for output stability and low ESR)
    cap_out = Component(
        symbol="Device:C", 
        ref="C2", 
        value="22uF",
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    
    # ESP32-C6 equivalent load (variable: active 200mA, sleep 10µA)
    # Using 16.5Ω for 200mA @ 3.3V for active load simulation
    esp32_load = Component(
        symbol="Device:R", 
        ref="R1", 
        value="16.5", 
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    
    # LED status indicator (2mA @ 3.3V with current limiting resistor)
    led_resistor = Component(
        symbol="Device:R",
        ref="R2", 
        value="1650",  # ~2mA LED current
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    
    # Power regulation connections
    regulator["VI"] += vbus      # 5V input from USB
    regulator["VO"] += vcc_3v3   # 3.3V regulated output
    regulator["GND"] += gnd      # Ground reference
    
    # Input filtering capacitor
    cap_in[1] += vbus
    cap_in[2] += gnd
    
    # Output decoupling capacitor
    cap_out[1] += vcc_3v3
    cap_out[2] += gnd
    
    # ESP32 load simulation
    esp32_load[1] += vcc_3v3
    esp32_load[2] += gnd
    
    # LED indicator load
    led_resistor[1] += vcc_3v3
    led_resistor[2] += gnd


def analyze_spice_results(results, analysis_type="dc"):
    """
    Analyze SPICE simulation results for power regulation performance.
    
    Args:
        results: SimulationResults from circuit-simulation
        analysis_type: Type of analysis performed
        
    Returns:
        dict: Analyzed performance metrics
    """
    print(f"📊 Analyzing {analysis_type.upper()} simulation results...")
    
    analysis = {
        'regulation_performance': {},
        'efficiency': {},
        'recommendations': []
    }
    
    try:
        if analysis_type == "dc":
            # DC analysis for line regulation
            voltages = results.get_node_voltages()
            currents = results.get_branch_currents()
            
            # Extract key metrics
            vbus_voltage = voltages.get('VBUS', 0)
            vcc_3v3_voltage = voltages.get('VCC_3V3', 0)
            input_current = abs(currents.get('VIN', 0))
            
            # Calculate regulation performance
            regulation_error = abs(vcc_3v3_voltage - 3.3) / 3.3 * 100
            efficiency = (vcc_3v3_voltage * input_current) / (vbus_voltage * input_current) * 100 if vbus_voltage > 0 else 0
            power_dissipation = (vbus_voltage - vcc_3v3_voltage) * input_current
            
            analysis['regulation_performance'] = {
                'input_voltage': vbus_voltage,
                'output_voltage': vcc_3v3_voltage,
                'regulation_error_percent': regulation_error,
                'meets_3v3_spec': regulation_error < 5.0  # ±5% tolerance
            }
            
            analysis['efficiency'] = {
                'efficiency_percent': efficiency,
                'input_current_mA': input_current * 1000,
                'power_dissipation_mW': power_dissipation * 1000,
                'thermal_acceptable': power_dissipation < 1.0  # <1W for SOT-223
            }
            
            # Engineering recommendations
            if efficiency < 70:
                analysis['recommendations'].append("⚠️ Low efficiency - consider switching regulator")
            if regulation_error > 5:
                analysis['recommendations'].append("⚠️ Poor regulation - check output capacitor ESR")
            if power_dissipation > 0.8:
                analysis['recommendations'].append("⚠️ High power dissipation - add thermal relief")
            if not analysis['recommendations']:
                analysis['recommendations'].append("✅ Power regulation meets design specifications")
                
    except Exception as e:
        print(f"⚠️  Analysis error: {e}")
        analysis['error'] = str(e)
        
    return analysis


def create_professional_power_report(spice_netlist, analysis_results, circuit_name):
    """Generate professional power regulation analysis report"""
    
    # Create subplots for comprehensive analysis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Power Regulation Performance',
            'Efficiency Analysis',
            'SPICE Circuit Netlist', 
            'Engineering Recommendations'
        ),
        specs=[[{"type": "xy"}, {"type": "xy"}],
               [{"type": "table"}, {"type": "table"}]]
    )
    
    # Power regulation performance gauge
    if 'regulation_performance' in analysis_results:
        perf = analysis_results['regulation_performance']
        error = perf.get('regulation_error_percent', 0)
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=perf.get('output_voltage', 0),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Output Voltage (V)"},
                delta={'reference': 3.3},
                gauge={
                    'axis': {'range': [3.0, 3.6]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [3.0, 3.135], 'color': "lightgray"},
                        {'range': [3.135, 3.465], 'color': "lightgreen"},
                        {'range': [3.465, 3.6], 'color': "lightgray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 3.3
                    }
                }
            ),
            row=1, col=1
        )
    
    # Efficiency analysis
    if 'efficiency' in analysis_results:
        eff = analysis_results['efficiency']
        efficiency = eff.get('efficiency_percent', 0)
        power_loss = eff.get('power_dissipation_mW', 0)
        
        fig.add_trace(
            go.Bar(
                x=['Efficiency (%)', 'Power Loss (mW)', 'Input Current (mA)'],
                y=[efficiency, power_loss, eff.get('input_current_mA', 0)],
                marker_color=['green' if efficiency > 70 else 'orange',
                             'red' if power_loss > 800 else 'blue',
                             'blue'],
                name='Performance Metrics'
            ),
            row=1, col=2
        )
    
    # SPICE netlist table
    netlist_lines = spice_netlist.split('\n')[:15]  # First 15 lines
    fig.add_trace(
        go.Table(
            header=dict(
                values=[f'SPICE Netlist: {circuit_name}'],
                fill_color='lightblue',
                align='left',
                font=dict(size=12, color='black')
            ),
            cells=dict(
                values=[netlist_lines],
                fill_color='white',
                align='left',
                font=dict(size=9, family='monospace')
            )
        ),
        row=2, col=1
    )
    
    # Engineering recommendations table
    recommendations = analysis_results.get('recommendations', ['No analysis available'])
    fig.add_trace(
        go.Table(
            header=dict(
                values=['Engineering Analysis & Recommendations'],
                fill_color='orange',
                align='left',
                font=dict(size=12, color='black')
            ),
            cells=dict(
                values=[recommendations],
                fill_color='white',
                align='left',
                font=dict(size=11)
            )
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'⚡ Professional Power Regulation Analysis: {circuit_name}',
            'font': {'size': 18},
            'x': 0.5
        },
        height=800,
        showlegend=False
    )
    
    return fig


def main():
    print("⚡ Enhanced Power Regulation Demo - Real SPICE Simulation")
    print("=" * 70)
    
    # Step 1: Create ESP32 power regulation circuit
    print("🔧 Creating ESP32 power regulation circuit...")
    circuit = esp32_power_regulation()
    print(f"✅ Circuit created: {circuit.name}")
    print(f"   Components: {len(circuit.get_components())}")
    print(f"   Nets: {len(circuit.get_nets())}")
    
    # List components for verification
    print("\n📋 Circuit components:")
    for comp in circuit.get_components():
        print(f"   • {comp.ref}: {comp.symbol} = {comp.value}")
    
    # Step 2: Export to SPICE netlist
    print(f"\n📋 Exporting to SPICE netlist...")
    try:
        spice_netlist = circuit.to_spice(include_analysis=True)
        print("✅ SPICE netlist generated successfully!")
        
        # Save netlist for inspection
        netlist_file = "esp32_power_regulation.cir"
        with open(netlist_file, "w") as f:
            f.write(spice_netlist)
        print(f"💾 Saved netlist as: {netlist_file}")
        
    except Exception as e:
        print(f"❌ SPICE export failed: {e}")
        return
    
    # Step 3: Run actual SPICE simulation
    print(f"\n🔄 Running SPICE simulation through circuit-simulation...")
    try:
        # Run DC analysis for line regulation
        dc_results = simulate_from_spice(spice_netlist, "dc")
        print("✅ DC analysis completed!")
        
        # Analyze results
        analysis = analyze_spice_results(dc_results, "dc")
        
    except CircuitSynthError as e:
        print(f"❌ SPICE simulation failed: {e.message}")
        if hasattr(e, 'details'):
            print(f"   Details: {e.details}")
        
        # Create fallback analysis for demonstration
        print("📊 Creating theoretical analysis...")
        analysis = {
            'regulation_performance': {
                'input_voltage': 5.0,
                'output_voltage': 3.3,
                'regulation_error_percent': 0.0,
                'meets_3v3_spec': True
            },
            'efficiency': {
                'efficiency_percent': 66.0,
                'input_current_mA': 202.0,
                'power_dissipation_mW': 340.0,
                'thermal_acceptable': True
            },
            'recommendations': [
                "⚠️ SPICE simulation not available - using theoretical analysis",
                "✅ Regulation meets 3.3V specification",
                "⚠️ Efficiency could be improved with switching regulator"
            ]
        }
    
    # Step 4: Generate professional report
    print(f"\n📈 Generating professional power analysis report...")
    fig = create_professional_power_report(spice_netlist, analysis, circuit.name)
    
    # Save and display the report
    report_file = "esp32_power_regulation_analysis.html"
    pyo.plot(fig, filename=report_file, auto_open=True)
    print(f"✅ Professional report saved: {report_file}")
    
    # Step 5: Print engineering summary
    print(f"\n🎯 ESP32 Power Regulation Analysis Summary:")
    print("=" * 50)
    
    if 'regulation_performance' in analysis:
        reg = analysis['regulation_performance']
        print(f"📋 Regulation Performance:")
        print(f"   Input Voltage:  {reg.get('input_voltage', 'N/A'):.2f}V (USB 5V)")
        print(f"   Output Voltage: {reg.get('output_voltage', 'N/A'):.2f}V (Target: 3.3V)")
        print(f"   Regulation Error: {reg.get('regulation_error_percent', 'N/A'):.1f}%")
        print(f"   Meets Spec: {'✅ Yes' if reg.get('meets_3v3_spec') else '❌ No'}")
    
    if 'efficiency' in analysis:
        eff = analysis['efficiency']
        print(f"\n📋 Power Efficiency:")
        print(f"   Efficiency: {eff.get('efficiency_percent', 'N/A'):.1f}%")
        print(f"   Input Current: {eff.get('input_current_mA', 'N/A'):.0f}mA")
        print(f"   Power Loss: {eff.get('power_dissipation_mW', 'N/A'):.0f}mW")
        print(f"   Thermal OK: {'✅ Yes' if eff.get('thermal_acceptable') else '❌ No'}")
    
    print(f"\n💡 Engineering Recommendations:")
    for rec in analysis.get('recommendations', []):
        print(f"   {rec}")
    
    print(f"\n✅ ESP32 power regulation analysis complete!")
    print(f"📁 Files generated:")
    print(f"   • {netlist_file} - SPICE netlist")
    print(f"   • {report_file} - Interactive analysis report")
    
    # Calculate and display ESP32 system metrics
    print(f"\n📊 ESP32 System Analysis:")
    reg_perf = analysis.get('regulation_performance', {})
    output_voltage = reg_perf.get('output_voltage', 3.3)
    
    print(f"   ESP32-C6 Active Power: {output_voltage * 0.2:.1f}W (200mA)")
    print(f"   LED Indicator Power: {output_voltage * 0.002:.1f}W (2mA)")
    print(f"   Total System Power: {output_voltage * 0.202:.1f}W")
    print(f"   Battery Life (2000mAh): ~{2000/202:.1f} hours active")


if __name__ == "__main__":
    main()