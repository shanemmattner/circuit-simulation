"""Design functions for transistor amplifiers."""

from .circuit import TransistorAmplifierCircuit


def design_common_emitter(
    gain: float, vcc: float = 12, ic_target: float = 5e-3, beta: float = 100
) -> TransistorAmplifierCircuit:
    """Design a common emitter amplifier.

    Args:
        gain: Target voltage gain (negative for CE)
        vcc: Supply voltage
        ic_target: Target collector current
        beta: Transistor beta

    Returns:
        Configured TransistorAmplifierCircuit
    """
    # Set Vc to Vcc/2 for maximum swing
    vc = vcc / 2

    # Calculate Rc from Ic
    rc = vc / ic_target

    # Calculate Re for desired gain (with degeneration)
    re = abs(rc / gain)

    # Set Ve to about 1V for stability
    ve = 1.0
    re = ve / ic_target

    # Recalculate Rc for correct gain
    rc = abs(gain * re)

    # Voltage divider bias
    # Set base current to Ic/beta/10 for stiff bias
    ib = ic_target / beta
    i_divider = 10 * ib

    # Calculate bias resistors
    vb = ve + 0.7  # Ve + Vbe
    r2 = vb / i_divider
    r1 = (vcc - vb) / i_divider

    # Round to standard values
    rc = _round_to_standard(rc)
    re = _round_to_standard(re)
    r1 = _round_to_standard(r1)
    r2 = _round_to_standard(r2)

    return TransistorAmplifierCircuit(
        config="common_emitter", vcc=vcc, rc=rc, re=re, r1=r1, r2=r2, beta=beta
    )


def _round_to_standard(value: float) -> float:
    """Round to standard resistor value.

    Args:
        value: Resistance in ohms

    Returns:
        Standard value
    """
    e12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

    decade = 10 ** np.floor(np.log10(value))
    normalized = value / decade

    closest = min(e12, key=lambda x: abs(x - normalized))

    return closest * decade


import numpy as np
