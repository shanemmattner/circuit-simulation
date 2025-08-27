"""Circuit Analysis Dashboard - Main Dash Application."""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

try:
    from src.gui.components.header import create_header
    from src.gui.components.tabs import create_tab_navigation, create_tab_content
    from src.gui.services.api_client import CircuitAPIClient
    from src.gui.utils.logging_config import setup_gui_logging, log_callback_execution
except ImportError:
    # For direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.gui.components.header import create_header
    from src.gui.components.tabs import create_tab_navigation, create_tab_content
    from src.gui.services.api_client import CircuitAPIClient
    from src.gui.utils.logging_config import setup_gui_logging, log_callback_execution

# Set up logging
gui_logger = setup_gui_logging()

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Circuit Analysis Dashboard"
)

# Basic layout structure for testing
# Create API client
api_client = CircuitAPIClient()

app.layout = dbc.Container(
    [
        # Navigation header
        create_header(),
        
        # Analysis tabs
        create_tab_navigation(),
        
        # Tab content area
        create_tab_content(),
        
        # Hidden div to trigger loading circuits on page load
        html.Div(id="page-load-trigger", style={"display": "none"})
    ],
    fluid=True
)


# Callback to load circuits into dropdown on page load
@app.callback(
    Output("circuit-selector", "options"),
    Input("page-load-trigger", "children")
)
def load_circuits(trigger):
    """Load available circuits from API into dropdown."""
    gui_logger.info("Loading circuits from API...")
    
    try:
        options = api_client.get_circuit_options()
        gui_logger.info(f"Retrieved {len(options)} circuit options from API")
        log_callback_execution(gui_logger, "load_circuits", {"trigger": trigger}, success=True)
        
        if not options:
            gui_logger.warning("No circuits found - API may be unavailable")
            return [{"label": "No circuits available - start API server", "value": ""}]
        
        gui_logger.info(f"Successfully loaded circuits: {[opt['label'] for opt in options]}")
        return options
    except Exception as e:
        gui_logger.error(f"Exception in load_circuits: {str(e)}")
        log_callback_execution(gui_logger, "load_circuits", {"trigger": trigger}, success=False, error=str(e))
        return [{"label": f"Error loading circuits: {str(e)[:50]}...", "value": ""}]


# Callback to update tab content when circuit is selected
@app.callback(
    Output("tab-content", "children"),
    [Input("circuit-selector", "value"), Input("analysis-tabs", "active_tab")]
)
def update_tab_content(selected_circuit, active_tab):
    """Update content based on selected circuit and active tab."""
    gui_logger.info(f"Updating tab content - Circuit: {selected_circuit}, Tab: {active_tab}")
    
    try:
        if not selected_circuit:
            gui_logger.debug("No circuit selected, showing placeholder")
            return html.P(
                "Select a circuit to view analysis results.",
                className="text-muted text-center mt-5"
            )
        
        log_callback_execution(
            gui_logger, 
            "update_tab_content", 
            {"circuit": selected_circuit, "tab": active_tab}, 
            success=True
        )
        
        # Get circuit details for display
        circuit_details = api_client.get_circuit_details(selected_circuit)
        circuit_name = circuit_details.get('name', 'Unknown') if circuit_details else 'Unknown'
        
        if active_tab == "dc-analysis":
            return create_dc_analysis_content(selected_circuit, circuit_name, circuit_details)
        elif active_tab == "ac-analysis":
            return create_ac_analysis_content(selected_circuit, circuit_name)
        elif active_tab == "transient-analysis":
            return create_transient_analysis_content(selected_circuit, circuit_name)
        elif active_tab == "reports":
            return create_reports_content(selected_circuit, circuit_name)
        elif active_tab == "jobs":
            return create_jobs_content(selected_circuit, circuit_name)
        else:
            return html.Div([
                html.H4(f"Circuit: {circuit_name}", className="text-primary"),
                html.H5(f"Analysis: {active_tab.replace('-', ' ').title()}", className="text-secondary"),
                html.P("Unknown analysis type.", className="text-danger mt-3")
            ])
    except Exception as e:
        gui_logger.error(f"Error in update_tab_content: {str(e)}")
        log_callback_execution(
            gui_logger, 
            "update_tab_content", 
            {"circuit": selected_circuit, "tab": active_tab}, 
            success=False, 
            error=str(e)
        )
        return html.P(
            f"Error updating content: {str(e)}",
            className="text-danger text-center mt-5"
        )


def create_dc_analysis_content(circuit_id: str, circuit_name: str, circuit_details: dict) -> html.Div:
    """Create DC analysis tab content."""
    if not circuit_details:
        return html.Div([
            html.H4(f"Circuit: {circuit_name}", className="text-primary"),
            html.H5("DC Analysis", className="text-secondary"),
            html.P("Circuit details not available.", className="text-warning")
        ])
    
    component_count = circuit_details.get('component_count', 0)
    node_count = circuit_details.get('node_count', 0)
    
    return html.Div([
        # Circuit info header
        dbc.Row([
            dbc.Col([
                html.H4(f"🔍 DC Analysis: {circuit_name}", className="text-primary mb-3")
            ])
        ]),
        
        # Circuit overview
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Circuit Overview"),
                    dbc.CardBody([
                        html.P(f"📊 Components: {component_count}"),
                        html.P(f"🔗 Nodes: {node_count}"),
                        html.P(f"🆔 ID: {circuit_id[:8]}..."),
                        dbc.Button(
                            "🚀 Run DC Analysis", 
                            color="primary",
                            id="run-dc-button",
                            className="mt-2"
                        )
                    ])
                ])
            ], width=4),
            
            # Results placeholder
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Operating Point Results"),
                    dbc.CardBody([
                        html.P("Click 'Run DC Analysis' to see results.", className="text-muted"),
                        html.P("• Node voltages table"),
                        html.P("• Component currents"),  
                        html.P("• Power dissipation"),
                        html.Div(id="dc-results-table")
                    ])
                ])
            ], width=8)
        ])
    ])


def create_ac_analysis_content(circuit_id: str, circuit_name: str) -> html.Div:
    """Create AC analysis tab content."""
    return html.Div([
        html.H4(f"📈 AC Analysis: {circuit_name}", className="text-primary mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Frequency Response Settings"),
                    dbc.CardBody([
                        html.P("📍 Start: 1 Hz"),
                        html.P("📍 Stop: 1 MHz"),
                        html.P("📏 Points: 50/decade"),
                        dbc.Button("🚀 Run AC Analysis", color="success", className="mt-2")
                    ])
                ])
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Bode Plot"),
                    dbc.CardBody([
                        html.P("📊 Magnitude & phase vs frequency", className="text-muted"),
                        html.P("🎯 Interactive cursors for measurements"),
                        html.P("📋 Automatic gain/phase margins")
                    ])
                ])
            ], width=8)
        ])
    ])


def create_transient_analysis_content(circuit_id: str, circuit_name: str) -> html.Div:
    """Create transient analysis tab content."""
    return html.Div([
        html.H4(f"⚡ Transient Analysis: {circuit_name}", className="text-primary mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Time Domain Settings"),
                    dbc.CardBody([
                        html.P("⏱️ Duration: 10ms"),
                        html.P("⚡ Step: 10μs"),
                        html.P("🔄 Analysis: Transient"),
                        dbc.Button("🚀 Run Transient", color="warning", className="mt-2")
                    ])
                ])
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Waveform Viewer"),
                    dbc.CardBody([
                        html.P("📈 Voltage & current vs time", className="text-muted"),
                        html.P("📏 Rise time, settling time measurements"),
                        html.P("🎥 Animated signal flow")
                    ])
                ])
            ], width=8)
        ])
    ])


def create_reports_content(circuit_id: str, circuit_name: str) -> html.Div:
    """Create reports tab content."""
    return html.Div([
        html.H4(f"📊 Reports: {circuit_name}", className="text-primary mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Report Templates"),
                    dbc.CardBody([
                        dbc.Button("📋 Quick Report", color="info", className="mb-2 w-100"),
                        dbc.Button("📈 Detailed Report", color="primary", className="mb-2 w-100"),
                        dbc.Button("💼 Executive Report", color="secondary", className="mb-2 w-100")
                    ])
                ])
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Report Features"),
                    dbc.CardBody([
                        html.P("📊 Interactive Plotly charts", className="text-muted"),
                        html.P("📏 Performance metrics & analysis"),
                        html.P("🎨 Professional HTML/PDF export"),
                        html.P("📧 Shareable report URLs")
                    ])
                ])
            ], width=8)
        ])
    ])


def create_jobs_content(circuit_id: str, circuit_name: str) -> html.Div:
    """Create jobs management tab content."""
    return html.Div([
        html.H4(f"⚙️ Jobs: {circuit_name}", className="text-primary mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Active Jobs"),
                    dbc.CardBody([
                        html.P("🔄 No active simulations", className="text-muted"),
                        dbc.Badge("✅ System Ready", color="success", className="mb-2"),
                        html.Br(),
                        dbc.Badge("📡 WebSocket Connected", color="info")
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Job History"),
                    dbc.CardBody([
                        html.P("📋 Recent simulations:", className="text-muted"),
                        html.P("⏱️ Real-time progress monitoring"),
                        html.P("📊 Performance metrics"),
                        html.P("🚫 Job cancellation controls")
                    ])
                ])
            ], width=6)
        ])
    ])


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)