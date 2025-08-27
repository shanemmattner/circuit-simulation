"""Design functions for power supplies."""

from .circuit import PowerSupplyCircuit


def design_regulated_supply(
    v_out: float,
    i_out: float,
    ripple_max: float,
    v_ac_available: float
) -> PowerSupplyCircuit:
    """Design a regulated power supply.
    
    Args:
        v_out: Output voltage
        i_out: Output current
        ripple_max: Maximum ripple
        v_ac_available: Available AC voltage
        
    Returns:
        Configured PowerSupplyCircuit
    """
    # Determine regulator type based on efficiency needs
    voltage_drop = v_ac_available * 1.414 - 1.4 - v_out
    
    if voltage_drop > 5:
        # Large drop, use switching for efficiency
        regulator_type = "switching"
    else:
        # Small drop, linear is simpler
        regulator_type = "linear"
    
    # Calculate filter capacitor for ripple
    # C = I / (2 * f * Vripple)
    c_filter = i_out / (120 * ripple_max * 10)  # Extra margin
    
    # Round to standard value
    c_values = [100e-6, 220e-6, 470e-6, 1000e-6, 2200e-6, 4700e-6]
    c_filter = min(c for c in c_values if c >= c_filter)
    
    return PowerSupplyCircuit(
        v_ac_input=v_ac_available,
        v_dc_output=v_out,
        i_max=i_out,
        regulator_type=regulator_type,
        filter_capacitor=c_filter
    )