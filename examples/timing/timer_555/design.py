"""Design functions for 555 timer circuits."""

import numpy as np
from typing import Optional
from .circuit import Timer555Circuit


def design_astable_555(
    frequency: float,
    duty_cycle: float = 0.5,
    capacitor: Optional[float] = None,
    use_diode: bool = False
) -> Timer555Circuit:
    """Design astable 555 oscillator.
    
    Args:
        frequency: Target frequency in Hz
        duty_cycle: Target duty cycle (0-1)
        capacitor: Fixed capacitor value (optional)
        use_diode: Use diode for 50% duty cycle
        
    Returns:
        Configured Timer555Circuit
    """
    # Choose capacitor if not specified
    if capacitor is None:
        # Select based on frequency range
        if frequency < 100:
            capacitor = 10e-6  # 10µF for low freq
        elif frequency < 10000:
            capacitor = 100e-9  # 100nF for mid freq
        else:
            capacitor = 10e-9  # 10nF for high freq
    
    if use_diode or abs(duty_cycle - 0.5) < 0.01:
        # 50% duty cycle with diode
        # f = 1.44 / ((R1 + R2) * C)
        r_total = 1.44 / (frequency * capacitor)
        r1 = r_total / 2
        r2 = r_total / 2
        has_diode = True
    else:
        # Standard astable
        # f = 1.44 / ((R1 + 2*R2) * C)
        # D = (R1 + R2) / (R1 + 2*R2)
        
        # Solve for R1 and R2
        r_sum = 1.44 / (frequency * capacitor)
        
        # From duty cycle equation
        r2 = r_sum * (1 - duty_cycle) / 2
        r1 = r_sum - 2 * r2
        
        # Ensure positive values
        if r1 <= 0:
            r1 = 100  # Minimum value
            r2 = (1.44 / (frequency * capacitor) - r1) / 2
        
        has_diode = False
    
    # Round to standard values
    r1 = _round_to_standard(r1)
    r2 = _round_to_standard(r2)
    
    return Timer555Circuit(
        mode="astable",
        r1=r1,
        r2=r2,
        c=capacitor,
        has_diode=has_diode
    )


def design_monostable_555(
    pulse_width: float,
    capacitor: Optional[float] = None
) -> Timer555Circuit:
    """Design monostable 555 one-shot.
    
    Args:
        pulse_width: Target pulse width in seconds
        capacitor: Fixed capacitor value (optional)
        
    Returns:
        Configured Timer555Circuit
    """
    # Choose capacitor if not specified
    if capacitor is None:
        if pulse_width < 1e-3:
            capacitor = 100e-9  # 100nF for short pulses
        elif pulse_width < 1:
            capacitor = 10e-6  # 10µF for medium pulses
        else:
            capacitor = 100e-6  # 100µF for long pulses
    
    # T = 1.1 * R * C
    r1 = pulse_width / (1.1 * capacitor)
    
    # Round to standard value
    r1 = _round_to_standard(r1)
    
    return Timer555Circuit(
        mode="monostable",
        r1=r1,
        c=capacitor
    )


def _round_to_standard(value: float) -> float:
    """Round to nearest standard resistor value.
    
    Args:
        value: Resistance in ohms
        
    Returns:
        Standard resistor value
    """
    # E12 series
    e12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
    
    # Find decade
    decade = 10 ** np.floor(np.log10(value))
    normalized = value / decade
    
    # Find closest standard value
    closest = min(e12, key=lambda x: abs(x - normalized))
    
    return closest * decade