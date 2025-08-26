# circuit

Create or analyze a circuit with the given parameters: $ARGUMENTS

Workflow:
1. Parse the circuit description from arguments
2. Create or load the circuit netlist
3. Run appropriate simulation (DC, AC, or transient)
4. Generate interactive Plotly report
5. Save results to examples/ directory

Example usage:
- `/circuit RC filter 1kHz cutoff`
- `/circuit amplifier with gain 20dB`
- `/circuit analyze examples/bridge_rectifier.py`

Provide detailed analysis and visualization of the circuit behavior.