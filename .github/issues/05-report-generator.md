# Feature: Advanced Report Generator with Plotly

## 🎯 Objective
Create a professional report generation system that produces interactive HTML reports and print-ready PDFs with embedded Plotly visualizations, comprehensive analysis summaries, and customizable templates.

## 📋 Requirements

### Report Types
- [ ] **Quick Summary** - Single page overview
- [ ] **Detailed Analysis** - Complete technical report
- [ ] **Executive Summary** - High-level business report
- [ ] **Comparison Report** - Multi-circuit comparison
- [ ] **Parameter Sweep** - Design space exploration
- [ ] **Validation Report** - Test vs. simulation

### Report Sections
- [ ] Title page with metadata
- [ ] Executive summary
- [ ] Circuit schematic
- [ ] Component list (BOM style)
- [ ] DC operating points
- [ ] Transient analysis results
- [ ] AC frequency response
- [ ] Interactive Plotly charts
- [ ] Performance metrics
- [ ] Conclusions and recommendations

### Export Formats
- [ ] Interactive HTML with Plotly
- [ ] PDF (print-ready)
- [ ] Word/DOCX
- [ ] Markdown
- [ ] LaTeX
- [ ] Jupyter Notebook

## 🛠️ Technical Implementation

### Dependencies
```toml
[dependencies]
plotly = "^5.18.0"
kaleido = "^0.2.1"      # Static image export
jinja2 = "^3.1.0"       # Template engine
weasyprint = "^60.0"    # HTML to PDF
python-docx = "^1.1.0"  # Word documents
nbformat = "^5.9.0"     # Jupyter notebooks
pandas = "^2.1.0"       # Data tables
```

### File Structure
```
src/reports/
├── __init__.py
├── generator.py         # Main report generator
├── templates/
│   ├── base.html       # Base HTML template
│   ├── quick.html      # Quick summary
│   ├── detailed.html   # Full technical
│   ├── executive.html  # Business focused
│   ├── styles.css      # Report styling
│   └── components/
│       ├── header.html
│       ├── charts.html
│       ├── tables.html
│       └── footer.html
├── builders/
│   ├── html_builder.py
│   ├── pdf_builder.py
│   ├── docx_builder.py
│   └── notebook_builder.py
├── charts/
│   ├── plotly_charts.py
│   ├── circuit_diagram.py
│   └── data_tables.py
└── utils/
    ├── formatting.py
    └── metrics.py
```

### Report Generator Class
```python
from typing import Dict, List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

class ReportGenerator:
    """Generate professional circuit analysis reports."""
    
    def __init__(self, template_dir: str = "templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.figures = []
        self.metadata = {}
        
    def generate_report(
        self,
        circuit: Circuit,
        results: SimulationResults,
        report_type: str = "detailed",
        output_format: str = "html"
    ) -> str:
        """
        Generate a comprehensive report.
        
        Args:
            circuit: Circuit object
            results: Simulation results
            report_type: 'quick', 'detailed', 'executive'
            output_format: 'html', 'pdf', 'docx', 'notebook'
        
        Returns:
            Path to generated report file
        """
        # Collect report data
        report_data = {
            'metadata': self._generate_metadata(circuit),
            'circuit': self._analyze_circuit(circuit),
            'results': self._process_results(results),
            'charts': self._create_charts(results),
            'metrics': self._calculate_metrics(results),
            'summary': self._generate_summary(results)
        }
        
        # Generate report based on type
        if output_format == "html":
            return self._generate_html(report_data, report_type)
        elif output_format == "pdf":
            return self._generate_pdf(report_data, report_type)
        elif output_format == "docx":
            return self._generate_docx(report_data, report_type)
        elif output_format == "notebook":
            return self._generate_notebook(report_data)
        
    def _create_charts(self, results: SimulationResults) -> Dict:
        """Create interactive Plotly visualizations."""
        charts = {}
        
        # DC Operating Point Chart
        if results.type == "dc":
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[f"Node {n}" for n in results.nodes],
                y=results.voltages,
                text=[f"{v:.3f}V" for v in results.voltages],
                textposition='auto',
                marker_color='rgb(55, 83, 109)'
            ))
            fig.update_layout(
                title="DC Operating Points",
                xaxis_title="Node",
                yaxis_title="Voltage (V)",
                showlegend=False
            )
            charts['dc_voltages'] = fig
        
        # Transient Analysis Chart
        if results.type == "transient":
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Voltages", "Currents"),
                shared_xaxes=True
            )
            
            # Voltage traces
            for node in results.nodes:
                fig.add_trace(
                    go.Scatter(
                        x=results.time,
                        y=results.get_voltage(node),
                        name=f"V({node})",
                        mode='lines'
                    ),
                    row=1, col=1
                )
            
            # Current traces
            for component in results.components:
                fig.add_trace(
                    go.Scatter(
                        x=results.time,
                        y=results.get_current(component),
                        name=f"I({component})",
                        mode='lines'
                    ),
                    row=2, col=1
                )
            
            fig.update_xaxes(title_text="Time (s)", row=2, col=1)
            fig.update_yaxes(title_text="Voltage (V)", row=1, col=1)
            fig.update_yaxes(title_text="Current (A)", row=2, col=1)
            fig.update_layout(height=600, showlegend=True)
            charts['transient'] = fig
        
        # AC Frequency Response (Bode Plot)
        if results.type == "ac":
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Magnitude", "Phase"),
                shared_xaxes=True
            )
            
            # Magnitude plot
            fig.add_trace(
                go.Scatter(
                    x=results.frequencies,
                    y=20*np.log10(results.magnitudes),
                    name="Magnitude",
                    mode='lines',
                    line=dict(color='blue', width=2)
                ),
                row=1, col=1
            )
            
            # Phase plot
            fig.add_trace(
                go.Scatter(
                    x=results.frequencies,
                    y=results.phases,
                    name="Phase",
                    mode='lines',
                    line=dict(color='red', width=2)
                ),
                row=2, col=1
            )
            
            fig.update_xaxes(type="log", title_text="Frequency (Hz)", row=2)
            fig.update_yaxes(title_text="Magnitude (dB)", row=1)
            fig.update_yaxes(title_text="Phase (°)", row=2)
            charts['bode'] = fig
        
        return charts
    
    def _generate_html(self, data: Dict, report_type: str) -> str:
        """Generate interactive HTML report."""
        template = self.env.get_template(f"{report_type}.html")
        
        # Convert Plotly figures to HTML
        data['charts_html'] = {}
        for name, fig in data['charts'].items():
            data['charts_html'][name] = fig.to_html(
                include_plotlyjs='cdn',
                div_id=f"chart-{name}"
            )
        
        # Render template
        html_content = template.render(
            **data,
            generated_at=datetime.now().isoformat(),
            version="1.0.0"
        )
        
        # Save to file
        output_path = f"reports/{data['metadata']['circuit_name']}_{report_type}.html"
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        return output_path
    
    def _calculate_metrics(self, results: SimulationResults) -> Dict:
        """Calculate key performance metrics."""
        metrics = {}
        
        if results.type == "dc":
            metrics['power_dissipation'] = self._calculate_power(results)
            metrics['efficiency'] = self._calculate_efficiency(results)
            
        elif results.type == "transient":
            metrics['rise_time'] = self._calculate_rise_time(results)
            metrics['settling_time'] = self._calculate_settling_time(results)
            metrics['overshoot'] = self._calculate_overshoot(results)
            
        elif results.type == "ac":
            metrics['bandwidth'] = self._calculate_bandwidth(results)
            metrics['gain'] = self._calculate_gain(results)
            metrics['phase_margin'] = self._calculate_phase_margin(results)
        
        return metrics
```

### HTML Template Example
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ metadata.circuit_name }} - Circuit Analysis Report</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="report-container">
        <!-- Header -->
        <header class="report-header">
            <h1>{{ metadata.circuit_name }}</h1>
            <p class="subtitle">{{ metadata.description }}</p>
            <div class="metadata">
                <span>Generated: {{ generated_at }}</span>
                <span>Version: {{ version }}</span>
            </div>
        </header>
        
        <!-- Executive Summary -->
        <section class="executive-summary">
            <h2>Executive Summary</h2>
            <div class="summary-grid">
                <div class="metric">
                    <h3>Components</h3>
                    <p class="value">{{ circuit.component_count }}</p>
                </div>
                <div class="metric">
                    <h3>Nodes</h3>
                    <p class="value">{{ circuit.node_count }}</p>
                </div>
                <div class="metric">
                    <h3>Simulation Time</h3>
                    <p class="value">{{ results.execution_time }}s</p>
                </div>
            </div>
            <p>{{ summary.text }}</p>
        </section>
        
        <!-- Circuit Analysis -->
        <section class="circuit-analysis">
            <h2>Circuit Analysis</h2>
            
            <!-- Component Table -->
            <table class="component-table">
                <thead>
                    <tr>
                        <th>Component</th>
                        <th>Type</th>
                        <th>Value</th>
                        <th>Nodes</th>
                    </tr>
                </thead>
                <tbody>
                    {% for comp in circuit.components %}
                    <tr>
                        <td>{{ comp.name }}</td>
                        <td>{{ comp.type }}</td>
                        <td>{{ comp.value }}</td>
                        <td>{{ comp.nodes }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </section>
        
        <!-- Simulation Results -->
        <section class="simulation-results">
            <h2>Simulation Results</h2>
            
            <!-- Interactive Charts -->
            {% for chart_name, chart_html in charts_html.items() %}
            <div class="chart-container">
                {{ chart_html | safe }}
            </div>
            {% endfor %}
            
            <!-- Metrics -->
            <div class="metrics-grid">
                {% for metric_name, metric_value in metrics.items() %}
                <div class="metric-card">
                    <h4>{{ metric_name | title | replace('_', ' ') }}</h4>
                    <p>{{ metric_value | round(3) }}</p>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <!-- Conclusions -->
        <section class="conclusions">
            <h2>Conclusions</h2>
            {{ summary.conclusions }}
        </section>
    </div>
</body>
</html>
```

## 📊 Success Criteria
- [ ] Reports generate in <5 seconds
- [ ] All chart types are interactive
- [ ] PDF export maintains quality
- [ ] Templates are customizable
- [ ] Metrics are accurately calculated
- [ ] Reports are professional quality

## 🔗 Dependencies
- Depends on: Simulation results, circuit data
- Blocks: None
- Related: #3 (API needs reports), #4 (AC plots)

## 📚 Resources
- [Plotly Documentation](https://plotly.com/python/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- [WeasyPrint Guide](https://weasyprint.org/)

## ✅ Acceptance Criteria
1. All report types generate successfully
2. Charts are interactive and responsive
3. PDF exports are print-ready
4. Templates follow best practices
5. Performance meets requirements

## 🏷️ Labels
`enhancement` `visualization` `reports` `priority-medium`

## 📝 Branch
`feature/report-engine`

## ⏱️ Estimated Effort
**Time**: 3-4 days
**Complexity**: Medium
**Priority**: Medium