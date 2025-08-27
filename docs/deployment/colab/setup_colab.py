#!/usr/bin/env python3
"""
Google Colab setup script for Circuit Simulation Learning Environment.

Run this cell at the beginning of any Colab notebook to set up the environment.
"""

import os
import sys
import subprocess
from IPython.display import HTML, display
import time

def setup_colab_environment():
    """Set up the complete Colab environment for interactive learning."""
    
    print("🚀 Setting up Circuit Simulation Learning Environment...")
    print("=" * 60)
    
    # Check if already set up
    if os.path.exists('/content/circuit-simulation-setup-complete'):
        print("✅ Environment already set up!")
        return True
    
    try:
        # Clone repository if not exists
        if not os.path.exists('/content/circuit-simulation'):
            print("📥 Cloning circuit simulation repository...")
            subprocess.run([
                'git', 'clone', 
                'https://github.com/circuit-synth/circuit-simulation.git',
                '/content/circuit-simulation'
            ], check=True, capture_output=True)
            print("✅ Repository cloned")
        
        # Change to repo directory
        os.chdir('/content/circuit-simulation')
        
        # Install dependencies
        print("📦 Installing dependencies...")
        subprocess.run([
            'pip', 'install', '-q',
            'PySpice>=1.5',
            'numpy>=1.24.0', 
            'matplotlib>=3.6.0',
            'plotly>=6.3.0',
            'pandas>=2.3.2',
            'ipywidgets>=8.1.1',
            'voila>=0.5.0',
            'jupyter-dash>=0.4.2',
            'pyyaml>=6.0.2',
            'jinja2>=3.1.6',
            'rich>=13.0.0'
        ], check=True)
        print("✅ Dependencies installed")
        
        # Install circuit-sim package in development mode
        print("🔧 Installing circuit-sim package...")
        subprocess.run(['pip', 'install', '-e', '.'], check=True, capture_output=True)
        print("✅ Circuit-sim package installed")
        
        # Enable widgets
        print("🎛️ Enabling interactive widgets...")
        from google.colab import output
        output.enable_custom_widget_manager()
        print("✅ Widgets enabled")
        
        # Create symlink to learning modules
        if not os.path.exists('/content/learning_modules'):
            os.symlink('/content/circuit-simulation/docs/learning_modules', '/content/learning_modules')
            print("✅ Learning modules linked")
        
        # Mark setup complete
        with open('/content/circuit-simulation-setup-complete', 'w') as f:
            f.write(f"Setup completed at {time.time()}")
        
        print("\n" + "=" * 60)
        print("🎉 Setup Complete!")
        print("📚 Navigate to /content/learning_modules/ to start learning")
        print("🔬 All interactive features are now available")
        
        # Display navigation helper
        display(HTML("""
        <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; border: 2px solid green; margin: 10px 0;">
            <h3>🎓 Interactive Circuit Learning Environment Ready!</h3>
            <p><strong>Quick Start:</strong></p>
            <ol>
                <li>Navigate to <code>/content/learning_modules/</code></li>
                <li>Start with <code>track1_dc_analysis/module_1.1_dc_basics/</code></li>
                <li>Open <code>explain_dc_concept.ipynb</code> to begin!</li>
            </ol>
            <p><strong>Features available:</strong> ✅ Interactive widgets ✅ Live simulations ✅ Plotly charts</p>
        </div>
        """))
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed: {e}")
        print("Please check your internet connection and try again.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def quick_test():
    """Quick test to verify the environment is working."""
    try:
        from circuit_sim import Circuit
        import ipywidgets as widgets
        import plotly.graph_objects as go
        
        # Test circuit creation
        circuit = Circuit("Test")
        circuit.add_voltage_source("V1", 1, 0, "5V")
        circuit.add_resistor("R1", 1, 0, "1k")
        
        # Test widget creation
        slider = widgets.IntSlider(value=50, description='Test:')
        
        # Test plotly
        fig = go.Figure()
        fig.add_bar(x=['A', 'B'], y=[1, 2])
        
        print("✅ All systems operational!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

# Main setup function
def setup():
    """Main setup function - call this in your Colab notebook."""
    success = setup_colab_environment()
    if success:
        test_success = quick_test()
        if test_success:
            print("\n🚀 Ready for interactive circuit learning!")
        else:
            print("\n⚠️ Setup complete but some features may not work")
    else:
        print("\n❌ Setup failed - please try again")
    
    return success

# Convenience function for notebooks
def colab_setup():
    """Convenience function for easy import in notebooks."""
    return setup()

if __name__ == "__main__":
    setup()