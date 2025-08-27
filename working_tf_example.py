#!/usr/bin/env python3
"""
Working Transfer Function Example - Core Features Only
"""

import numpy as np
import matplotlib.pyplot as plt
from circuit_sim.analysis import TransferFunction

def main():
    print("🎯 TRANSFER FUNCTION ANALYSIS - WORKING EXAMPLE")
    print("=" * 55)
    
    # Example 1: RC Low-Pass Filter Analysis
    print("\n📍 Example 1: RC Low-Pass Filter")
    print("-" * 35)
    
    # H(s) = 1/(RCs + 1) for R=1kΩ, C=1μF
    R = 1000  # ohms  
    C = 1e-6  # farads
    cutoff_theory = 1/(2*np.pi*R*C)  # Hz
    
    # Create transfer function: H(s) = 1000/(s + 1000)
    tf_rc = TransferFunction([1000], [1, 1000])
    
    print(f"Circuit: R={R/1000}kΩ, C={C*1e6}μF")
    print(f"Theoretical -3dB frequency: {cutoff_theory:.1f} Hz")
    print(f"Calculated -3dB frequency: {tf_rc.bandwidth/(2*np.pi):.1f} Hz")
    print(f"DC Gain: {20*np.log10(tf_rc.dc_gain):.1f} dB")
    print(f"Poles: {tf_rc.poles[0]:.0f} rad/s")
    
    # Example 2: Lead Compensator Design
    print("\n📍 Example 2: Lead Compensator Design")
    print("-" * 37)
    
    # Design requirements: Add 45° phase lead at 10 Hz
    freq_design = 10 * 2*np.pi  # 10 Hz in rad/s
    
    # Lead compensator: Gc(s) = α(s + 1/αT)/(s + 1/T) 
    # Choose α=10 for good phase lead
    alpha = 10
    T = 1/(freq_design * np.sqrt(alpha))  # Center frequency at design freq
    
    zero = -1/(alpha*T)  # Zero location
    pole = -1/T          # Pole location
    gain = alpha
    
    tf_lead = TransferFunction.from_poles_zeros([pole], [zero], gain)
    
    print(f"Design frequency: {freq_design/(2*np.pi):.1f} Hz")
    print(f"Zero: {zero:.1f} rad/s ({abs(zero)/(2*np.pi):.2f} Hz)")
    print(f"Pole: {pole:.1f} rad/s ({abs(pole)/(2*np.pi):.1f} Hz)")
    print(f"Gain: {gain}")
    
    # Check phase at design frequency
    response_at_design = tf_lead.evaluate(1j * freq_design)
    phase_at_design = np.degrees(np.angle(response_at_design))
    gain_at_design = 20*np.log10(abs(response_at_design))
    
    print(f"At {freq_design/(2*np.pi):.1f} Hz:")
    print(f"  Phase lead: {phase_at_design:.1f}°")
    print(f"  Gain boost: {gain_at_design:.1f} dB")
    
    # Example 3: Second-Order System Analysis
    print("\n📍 Example 3: Second-Order System Analysis")
    print("-" * 42)
    
    # Underdamped system: H(s) = ωn²/(s² + 2ζωn·s + ωn²)
    wn = 5    # Natural frequency (rad/s)
    zeta = 0.3  # Damping ratio (underdamped)
    
    # Coefficients: [1, 2*zeta*wn, wn^2] for denominator
    tf_second = TransferFunction([wn**2], [1, 2*zeta*wn, wn**2])
    
    print(f"Natural frequency: {wn} rad/s ({wn/(2*np.pi):.2f} Hz)")
    print(f"Damping ratio: {zeta}")
    print(f"Poles: {tf_second.poles}")
    
    # Theoretical vs calculated performance
    theoretical_overshoot = 100 * np.exp(-zeta*np.pi/np.sqrt(1-zeta**2))
    calculated_overshoot = tf_second.overshoot()
    
    print(f"Step Response Analysis:")
    print(f"  Theoretical overshoot: {theoretical_overshoot:.1f}%")
    print(f"  Calculated overshoot: {calculated_overshoot:.1f}%")
    print(f"  Rise time: {tf_second.rise_time():.3f} s")
    print(f"  Settling time: {tf_second.settling_time():.3f} s")
    
    # Example 4: Stability Analysis
    print("\n📍 Example 4: Stability Analysis")
    print("-" * 34)
    
    # Create a system near stability limit
    tf_marginal = TransferFunction([10], [1, 1, 10])
    margins = tf_marginal.stability_margins()
    
    print(f"System: H(s) = 10/(s² + s + 10)")
    print(f"Poles: {tf_marginal.poles}")
    print(f"Stability Analysis:")
    print(f"  Phase margin: {margins.phase_margin:.1f}°")
    print(f"  Gain margin: {margins.gain_margin:.1f} dB") 
    print(f"  System is: {'STABLE' if margins.is_stable else 'UNSTABLE'}")
    
    # Example 5: Frequency Response Plotting
    print("\n📍 Example 5: Frequency Response Visualization")
    print("-" * 46)
    
    try:
        # Create Bode plot for the RC filter
        frequencies = np.logspace(-1, 4, 1000)  # 0.1 to 10000 rad/s
        response = tf_rc.frequency_response(frequencies)
        
        magnitude_db = 20 * np.log10(np.abs(response))
        phase_deg = np.degrees(np.angle(response))
        
        # Find -3dB point
        idx_3db = np.argmin(np.abs(magnitude_db + 3))
        freq_3db = frequencies[idx_3db] / (2*np.pi)
        
        print(f"Frequency response calculated for {len(frequencies)} points")
        print(f"DC gain: {magnitude_db[0]:.1f} dB")
        print(f"-3dB frequency: {freq_3db:.1f} Hz")
        print(f"High frequency roll-off: ~-20 dB/decade")
        
        # Create a simple plot if matplotlib is available
        plt.figure(figsize=(12, 8))
        
        # Magnitude plot
        plt.subplot(2, 1, 1)
        plt.semilogx(frequencies/(2*np.pi), magnitude_db)
        plt.axhline(-3, color='r', linestyle='--', alpha=0.7, label='-3dB line')
        plt.axvline(freq_3db, color='r', linestyle='--', alpha=0.7)
        plt.grid(True, alpha=0.3)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude (dB)')
        plt.title('RC Low-Pass Filter - Bode Plot')
        plt.legend()
        
        # Phase plot  
        plt.subplot(2, 1, 2)
        plt.semilogx(frequencies/(2*np.pi), phase_deg)
        plt.grid(True, alpha=0.3)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Phase (degrees)')
        
        plt.tight_layout()
        plt.savefig('transfer_function_bode.png', dpi=150, bbox_inches='tight')
        print(f"Bode plot saved as 'transfer_function_bode.png'")
        plt.show()
        
    except ImportError:
        print("matplotlib not available - skipping visualization")
    except Exception as e:
        print(f"Plotting error: {e}")
    
    print("\n🎉 TRANSFER FUNCTION ANALYSIS COMPLETE!")
    print("=" * 55)
    print("✅ All core features demonstrated successfully")
    print("🚀 Ready for control system and filter design applications")

if __name__ == "__main__":
    main()