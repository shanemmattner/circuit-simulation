"""
Advanced Visualization Demo

This example demonstrates all the advanced visualization capabilities
including Nyquist plots, Smith charts, Nichols charts, and interactive Plotly visualizations.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Import our visualization module
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.circuit_sim.visualization import (
    NyquistPlotter, SmithChartPlotter, NicholsPlotter, InteractivePlotter,
    PlotStyle
)


def create_test_systems():
    """Create various test transfer functions for demonstration."""
    frequencies = np.logspace(-1, 4, 200)
    omega = 2 * np.pi * frequencies
    s = 1j * omega
    
    systems = {}
    
    # First-order system
    tau = 0.01  # Time constant
    systems["First Order"] = {
        "tf": 1 / (1 + s * tau),
        "freq": frequencies,
        "description": "Single-pole low-pass filter"
    }
    
    # Second-order system
    wn = 20  # Natural frequency
    zeta = 0.3  # Damping ratio
    systems["Second Order"] = {
        "tf": wn**2 / (s**2 + 2*zeta*wn*s + wn**2),
        "freq": frequencies,
        "description": "Underdamped second-order system"
    }
    
    # Integrator with lag
    K = 10
    tau1 = 0.1
    systems["Integrator"] = {
        "tf": K / (s * (1 + s * tau1)),
        "freq": frequencies,
        "description": "Type-1 system with lag compensation"
    }
    
    return systems


def demo_nyquist_plots():
    """Demonstrate Nyquist plot capabilities."""
    print("=== Nyquist Plot Demo ===")
    
    systems = create_test_systems()
    
    # Create different plot styles
    styles = {
        "default": PlotStyle(),
        "professional": PlotStyle.professional(),
        "dark": PlotStyle.dark()
    }
    
    for style_name, style in styles.items():
        print(f"\nGenerating Nyquist plots with {style_name} style...")
        
        plotter = NyquistPlotter(style=style)
        
        for sys_name, sys_data in systems.items():
            result = plotter.plot(
                transfer_function=sys_data["tf"],
                frequencies=sys_data["freq"],
                title=f"Nyquist Plot: {sys_name} ({style_name})",
                show_stability=True,
                mark_frequencies=[1, 10, 100]
            )
            
            print(f"  - {sys_name}: Stable = {result.metadata['stability_analysis']['is_stable']}")
            plt.savefig(f"nyquist_{sys_name.lower().replace(' ', '_')}_{style_name}.png", 
                       dpi=style.dpi, bbox_inches='tight')
            plt.close()


def demo_smith_charts():
    """Demonstrate Smith chart capabilities."""
    print("\n=== Smith Chart Demo ===")
    
    # Create impedance data for different scenarios
    frequencies = np.linspace(100e6, 1000e6, 50)  # RF frequencies
    
    scenarios = {}
    
    # Capacitive to inductive sweep
    scenarios["Antenna Matching"] = {
        "Z": 50 + 1j * np.linspace(-30, 30, 50),
        "freq": frequencies,
        "description": "Antenna impedance vs frequency"
    }
    
    # Transmission line
    z0_line = 75  # Ohm line impedance
    zl = 100 + 50j  # Load impedance
    gamma_l = (zl - z0_line) / (zl + z0_line)  # Load reflection coefficient
    beta_l = 2 * np.pi * frequencies / (3e8 / 0.66)  # Propagation constant
    
    # Input impedance of loaded transmission line
    z_in = z0_line * (1 + gamma_l * np.exp(-2j * beta_l * 0.1)) / (1 - gamma_l * np.exp(-2j * beta_l * 0.1))
    scenarios["Transmission Line"] = {
        "Z": z_in,
        "freq": frequencies,
        "description": "Input impedance of 10cm loaded line"
    }
    
    plotter = SmithChartPlotter(z0=50.0)
    
    for scenario_name, scenario_data in scenarios.items():
        print(f"\nGenerating Smith chart: {scenario_name}")
        
        result = plotter.plot(
            impedances=scenario_data["Z"],
            frequencies=scenario_data["freq"],
            title=f"Smith Chart: {scenario_name}",
            show_vswr_circles=True,
            vswr_values=[1.5, 2.0, 3.0, 5.0],
            mark_frequencies=[200e6, 500e6, 800e6]
        )
        
        min_vswr = np.min(result.data["vswr"])
        print(f"  - Minimum VSWR: {min_vswr:.2f}")
        
        plt.savefig(f"smith_{scenario_name.lower().replace(' ', '_')}.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()


def demo_nichols_charts():
    """Demonstrate Nichols chart capabilities."""
    print("\n=== Nichols Chart Demo ===")
    
    systems = create_test_systems()
    plotter = NicholsPlotter()
    
    for sys_name, sys_data in systems.items():
        print(f"\nGenerating Nichols chart: {sys_name}")
        
        result = plotter.plot(
            transfer_function=sys_data["tf"],
            frequencies=sys_data["freq"],
            title=f"Nichols Chart: {sys_name}",
            show_grid=True,
            show_margins=True,
            mark_frequencies=[0.1, 1, 10, 100]
        )
        
        if "stability_margins" in result.metadata:
            margins = result.metadata["stability_margins"]
            gm = margins.get('gain_margin_db')
            pm = margins.get('phase_margin_deg')
            if gm is not None:
                print(f"  - Gain Margin: {gm:.1f} dB")
            else:
                print(f"  - Gain Margin: N/A")
            if pm is not None:
                print(f"  - Phase Margin: {pm:.1f}°")
            else:
                print(f"  - Phase Margin: N/A")
        
        plt.savefig(f"nichols_{sys_name.lower().replace(' ', '_')}.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()


def demo_interactive_plots():
    """Demonstrate interactive Plotly visualizations."""
    print("\n=== Interactive Plot Demo ===")
    
    systems = create_test_systems()
    
    # Different themes to demonstrate
    themes = ["plotly_white", "plotly_dark", "simple_white"]
    
    for theme in themes:
        print(f"\nGenerating interactive plots with {theme} theme...")
        
        plotter = InteractivePlotter(theme=theme)
        
        # Single system Bode plot
        sys_name = "Second Order"
        sys_data = systems[sys_name]
        
        bode_html = plotter.create_bode_plot(
            frequencies=sys_data["freq"],
            transfer_function=sys_data["tf"],
            title=f"Interactive Bode Plot: {sys_name} ({theme})",
            show_hover=True,
            show_export_buttons=True
        )
        
        output_file = f"interactive_bode_{theme}.html"
        with open(output_file, 'w') as f:
            f.write(bode_html)
        print(f"  - Saved: {output_file}")
        
        # Nyquist plot
        nyquist_html = plotter.create_nyquist_plot(
            transfer_function=sys_data["tf"],
            frequencies=sys_data["freq"],
            title=f"Interactive Nyquist Plot: {sys_name} ({theme})"
        )
        
        output_file = f"interactive_nyquist_{theme}.html"
        with open(output_file, 'w') as f:
            f.write(nyquist_html)
        print(f"  - Saved: {output_file}")
    
    # Multi-trace comparison
    print("\nGenerating multi-trace comparison...")
    
    plotter = InteractivePlotter()
    multi_trace_html = plotter.create_multi_trace_bode(
        frequencies=systems["First Order"]["freq"],
        transfer_functions={name: data["tf"] for name, data in systems.items()},
        title="System Comparison: Multiple Transfer Functions"
    )
    
    with open("interactive_comparison.html", 'w') as f:
        f.write(multi_trace_html)
    print("  - Saved: interactive_comparison.html")
    
    # Smith chart with RF data
    print("\nGenerating interactive Smith chart...")
    
    frequencies = np.linspace(100e6, 1000e6, 30)
    impedances = 50 + 1j * np.linspace(-25, 25, 30)
    
    smith_html = plotter.create_smith_chart(
        impedances=impedances,
        frequencies=frequencies,
        title="Interactive Smith Chart: Impedance Matching"
    )
    
    with open("interactive_smith.html", 'w') as f:
        f.write(smith_html)
    print("  - Saved: interactive_smith.html")


def demo_export_functionality():
    """Demonstrate export capabilities."""
    print("\n=== Export Functionality Demo ===")
    
    # Test different export formats
    systems = create_test_systems()
    sys_data = systems["Second Order"]
    
    plotter = NyquistPlotter(style=PlotStyle.professional())
    result = plotter.plot(
        transfer_function=sys_data["tf"],
        frequencies=sys_data["freq"],
        title="Export Test: Nyquist Plot"
    )
    
    # Export to different formats
    formats = ["png", "svg", "pdf"]
    for fmt in formats:
        try:
            filename = f"export_test.{fmt}"
            if fmt == "png":
                plt.savefig(filename, dpi=300, format=fmt, bbox_inches='tight')
            elif fmt == "svg":
                plt.savefig(filename, format=fmt, bbox_inches='tight')
            elif fmt == "pdf":
                plt.savefig(filename, format=fmt, bbox_inches='tight')
            print(f"  - Exported: {filename}")
        except Exception as e:
            print(f"  - Export failed for {fmt}: {e}")
    
    plt.close()


def run_performance_benchmark():
    """Run performance benchmarks."""
    print("\n=== Performance Benchmark ===")
    
    import time
    
    # Large dataset benchmark
    frequencies = np.logspace(0, 5, 10000)  # 10k points
    omega = 2 * np.pi * frequencies
    transfer_function = 1 / (1 + 1j * omega * 0.001)
    
    # Nyquist plot benchmark
    start_time = time.time()
    plotter = NyquistPlotter()
    result = plotter.plot(transfer_function, frequencies, title="Benchmark Test")
    nyquist_time = time.time() - start_time
    plt.close()
    
    print(f"  - Nyquist plot (10k points): {nyquist_time:.2f} seconds")
    
    # Interactive plot benchmark
    start_time = time.time()
    interactive_plotter = InteractivePlotter()
    html_output = interactive_plotter.create_bode_plot(
        frequencies=frequencies[:1000],  # Limit for reasonable HTML size
        transfer_function=transfer_function[:1000]
    )
    interactive_time = time.time() - start_time
    
    print(f"  - Interactive Bode plot (1k points): {interactive_time:.2f} seconds")
    print(f"  - HTML size: {len(html_output)/1024:.1f} KB")


def main():
    """Main demo function."""
    print("Advanced Visualization Demo")
    print("===========================")
    print("This demo showcases all advanced visualization capabilities:")
    print("- Nyquist plots with stability analysis")
    print("- Smith charts for RF design")
    print("- Nichols charts for control systems")
    print("- Interactive Plotly visualizations")
    print("- Multiple export formats")
    print("- Performance benchmarking")
    print()
    
    # Create output directory
    Path("visualization_output").mkdir(exist_ok=True)
    import os
    os.chdir("visualization_output")
    
    try:
        # Run all demonstrations
        demo_nyquist_plots()
        demo_smith_charts()
        demo_nichols_charts()
        demo_interactive_plots()
        demo_export_functionality()
        run_performance_benchmark()
        
        print("\n" + "="*50)
        print("Demo completed successfully!")
        print("Check the 'visualization_output' directory for generated files.")
        print("Open the .html files in a web browser to see interactive plots.")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        os.chdir("..")


if __name__ == "__main__":
    main()