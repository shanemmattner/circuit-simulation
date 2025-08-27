# Feature: AC Frequency Analysis Implementation

## 🎯 Objective
Implement comprehensive AC (frequency domain) analysis capabilities including Bode plots, transfer functions, impedance analysis, and S-parameters.

## 📋 Requirements

### Core Features
- [ ] Frequency sweep analysis (logarithmic/linear)
- [ ] Complex impedance calculation
- [ ] Transfer function extraction
- [ ] Noise analysis
- [ ] Stability analysis (poles/zeros)
- [ ] Group delay calculation

### Visualization
- [ ] Bode magnitude plots
- [ ] Bode phase plots
- [ ] Nyquist plots
- [ ] Nichols charts
- [ ] Smith charts (for RF)
- [ ] Polar plots

### Analysis Types
- [ ] Single frequency analysis
- [ ] Frequency sweep (decade/octave)
- [ ] Multi-port S-parameters
- [ ] Input/output impedance
- [ ] Loop gain analysis
- [ ] CMRR/PSRR analysis

## 🛠️ Technical Implementation

### File Structure
```
src/simulator/
├── ac_analysis/
│   ├── __init__.py
│   ├── frequency_sweep.py    # Core sweep engine
│   ├── transfer_function.py  # H(s) extraction
│   ├── impedance.py         # Z(f) calculations
│   ├── s_parameters.py      # S11, S21, etc.
│   ├── stability.py         # Pole-zero analysis
│   └── noise.py             # Noise figure calc
├── visualization/
│   ├── bode_plot.py         # Magnitude/phase
│   ├── nyquist_plot.py      # Stability plots
│   ├── smith_chart.py       # RF impedance
│   └── polar_plot.py        # Complex plane
└── utils/
    ├── complex_math.py       # Complex arithmetic
    └── frequency_utils.py    # Freq generation
```

### Core Implementation
```python
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FrequencyPoint:
    frequency: float
    magnitude: complex
    phase: float
    impedance: complex
    
class ACAnalysis:
    """Frequency domain analysis engine."""
    
    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.frequencies = []
        self.results = {}
        
    def frequency_sweep(
        self,
        start_freq: float = 1,
        stop_freq: float = 1e9,
        points_per_decade: int = 20,
        sweep_type: str = "logarithmic"
    ) -> 'ACResults':
        """
        Perform AC frequency sweep analysis.
        
        Args:
            start_freq: Starting frequency in Hz
            stop_freq: Ending frequency in Hz
            points_per_decade: Resolution for log sweep
            sweep_type: 'logarithmic' or 'linear'
        
        Returns:
            ACResults object with frequency response data
        """
        # Generate frequency points
        if sweep_type == "logarithmic":
            num_decades = np.log10(stop_freq/start_freq)
            num_points = int(num_decades * points_per_decade)
            frequencies = np.logspace(
                np.log10(start_freq),
                np.log10(stop_freq),
                num_points
            )
        else:
            frequencies = np.linspace(start_freq, stop_freq, 1000)
        
        # Build complex admittance matrix
        results = []
        for freq in frequencies:
            omega = 2 * np.pi * freq
            
            # Update reactive components
            self._update_complex_impedances(omega)
            
            # Solve circuit at this frequency
            Y_matrix = self._build_admittance_matrix(omega)
            V_nodes = self._solve_ac_circuit(Y_matrix)
            
            # Store results
            results.append(FrequencyPoint(
                frequency=freq,
                magnitude=np.abs(V_nodes),
                phase=np.angle(V_nodes, deg=True),
                impedance=self._calculate_impedances(V_nodes, omega)
            ))
        
        return ACResults(frequencies, results)
    
    def transfer_function(
        self,
        input_node: str,
        output_node: str,
        reference: str = "gnd"
    ) -> TransferFunction:
        """
        Calculate transfer function H(s) = Vout/Vin.
        
        Args:
            input_node: Input signal node
            output_node: Output measurement node
            reference: Reference node (ground)
        
        Returns:
            TransferFunction object with poles, zeros, gain
        """
        # Symbolic analysis for s-domain
        s = symbols('s')
        
        # Build symbolic admittance matrix
        Y_symbolic = self._build_symbolic_matrix(s)
        
        # Calculate transfer function
        H_s = self._solve_transfer_function(
            Y_symbolic, input_node, output_node
        )
        
        # Extract poles and zeros
        poles = self._find_poles(H_s)
        zeros = self._find_zeros(H_s)
        dc_gain = float(H_s.subs(s, 0))
        
        return TransferFunction(H_s, poles, zeros, dc_gain)
    
    def calculate_impedance(
        self,
        node1: str,
        node2: str = "gnd",
        frequency: float = 1000
    ) -> complex:
        """
        Calculate impedance between two nodes.
        
        Args:
            node1: First node
            node2: Second node (default ground)
            frequency: Test frequency in Hz
        
        Returns:
            Complex impedance Z = R + jX
        """
        omega = 2 * np.pi * frequency
        
        # Inject test current
        I_test = 1.0  # 1A test current
        
        # Calculate voltage response
        V_response = self._inject_current_calculate_voltage(
            node1, node2, I_test, omega
        )
        
        # Z = V/I
        impedance = V_response / I_test
        
        return impedance
    
    def stability_analysis(self) -> StabilityResult:
        """
        Analyze circuit stability using various methods.
        
        Returns:
            StabilityResult with margins and criteria
        """
        # Calculate loop gain
        loop_gain = self._calculate_loop_gain()
        
        # Phase margin at gain crossover
        phase_margin = self._calculate_phase_margin(loop_gain)
        
        # Gain margin at phase crossover  
        gain_margin = self._calculate_gain_margin(loop_gain)
        
        # Nyquist criterion
        encirclements = self._count_nyquist_encirclements(loop_gain)
        
        return StabilityResult(
            phase_margin=phase_margin,
            gain_margin=gain_margin,
            is_stable=(encirclements == 0),
            poles=loop_gain.poles,
            zeros=loop_gain.zeros
        )
```

### Bode Plot Generation
```python
def plot_bode(results: ACResults, title: str = "Bode Plot"):
    """Generate Bode magnitude and phase plots."""
    fig, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(10, 8))
    
    frequencies = results.frequencies
    magnitudes_db = 20 * np.log10(results.magnitudes)
    phases = results.phases
    
    # Magnitude plot
    ax_mag.semilogx(frequencies, magnitudes_db)
    ax_mag.set_ylabel('Magnitude (dB)')
    ax_mag.grid(True, which='both', alpha=0.3)
    ax_mag.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    
    # Phase plot
    ax_phase.semilogx(frequencies, phases)
    ax_phase.set_xlabel('Frequency (Hz)')
    ax_phase.set_ylabel('Phase (degrees)')
    ax_phase.grid(True, which='both', alpha=0.3)
    ax_phase.axhline(y=-180, color='r', linestyle='--', alpha=0.3)
    
    plt.suptitle(title)
    return fig
```

## 📊 Success Criteria
- [ ] Accurate frequency response (±0.1dB, ±1°)
- [ ] Handles 1Hz to 100GHz range
- [ ] Stability analysis matches theory
- [ ] Plots are publication quality
- [ ] Performance: <1s for 1000 points
- [ ] Matches SPICE AC analysis results

## 🔗 Dependencies
- Depends on: Core simulation engine, NumPy/SciPy
- Blocks: Report generator (needs AC plots)
- Related: #2 (Examples need AC analysis)

## 📚 Resources
- [Network Analysis and Synthesis](https://www.wiley.com/network-analysis)
- [Microwave Engineering - Pozar](https://www.wiley.com/microwave-engineering)
- [Control Systems Engineering](https://www.wiley.com/control-systems)

## ✅ Acceptance Criteria
1. Bode plots match theoretical predictions
2. Transfer functions are symbolically correct
3. Stability margins are accurate
4. S-parameters validated against standards
5. All plot types are implemented

## 🏷️ Labels
`enhancement` `simulation` `analysis` `priority-high`

## 📝 Branch
`feature/ac-analysis`

## ⏱️ Estimated Effort
**Time**: 3-4 days
**Complexity**: High
**Priority**: High