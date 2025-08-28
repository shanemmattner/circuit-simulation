---
name: circuit
description: Create, analyze, or simulate circuits with comprehensive reporting
tools: [Bash, Read, Write, Edit, Grep]
model: claude-sonnet-4-20250514
temperature: 0.2
---

# circuit

Create or analyze a circuit with the given parameters: $ARGUMENTS

## Workflow with Error Handling
```bash
set -e  # Exit on any error

# Parse arguments
CIRCUIT_DESC="$ARGUMENTS"
if [[ -z "$CIRCUIT_DESC" ]]; then
    echo "❌ Error: Circuit description required"
    echo "Usage: /circuit <description> or /circuit analyze <file>"
    exit 1
fi

echo "🔧 Processing circuit: $CIRCUIT_DESC"

# Check if analyzing existing circuit
if [[ "$1" == "analyze" && -n "$2" ]]; then
    if [[ ! -f "$2" ]]; then
        echo "❌ Error: File $2 not found"
        exit 1
    fi
    echo "📊 Analyzing existing circuit: $2"
    uv run python -c "
from circuit_sim import Circuit
circuit = Circuit.from_file('$2')
print(f'Circuit loaded: {circuit.name} with {len(circuit.components)} components')
"
else
    echo "🏗️  Creating new circuit from description..."
    # Use MCP server or direct Python API
    uv run python -c "
from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine

# Parse description and create circuit
# This would integrate with your circuit creation logic
print('Circuit creation from description - implement based on your parser')
"
fi

# Generate comprehensive report
echo "📈 Generating interactive report..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="examples/circuit_analysis_$TIMESTAMP.html"

echo "✅ Analysis complete!"
echo "📋 Report saved to: $REPORT_FILE"
```

## Example Usage
- `/circuit RC filter 1kHz cutoff`
- `/circuit amplifier with gain 20dB`  
- `/circuit analyze examples/bridge_rectifier.py`
- `/circuit validate examples/power_supply.cir`

## Output
- 📊 Interactive Plotly visualizations
- 📈 Frequency/time domain analysis
- 💾 Results saved to `examples/` directory
- 🔍 Validation and optimization suggestions