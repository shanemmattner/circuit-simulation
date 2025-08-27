"""Navigation header component for Circuit Analysis Dashboard."""

from dash import dcc, html
import dash_bootstrap_components as dbc
from typing import List, Dict, Optional


def create_header(circuit_options: Optional[List[Dict[str, str]]] = None) -> dbc.Row:
    """Create the navigation header with circuit selector.
    
    Args:
        circuit_options: List of circuit options for dropdown
        
    Returns:
        Dash component for the header
    """
    if circuit_options is None:
        circuit_options = [
            {"label": "Select a circuit...", "value": ""}
        ]
    
    return dbc.Row(
        [
            # Left side - Title
            dbc.Col(
                [
                    html.H2(
                        "Circuit Analysis Dashboard",
                        className="mb-0 text-primary fw-bold",
                        style={"color": "#2c3e50"}
                    )
                ],
                width=6,
                className="d-flex align-items-center"
            ),
            
            # Right side - Circuit selector and controls
            dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label(
                                        "Circuit:",
                                        className="form-label fw-semibold me-2"
                                    )
                                ],
                                width="auto",
                                className="d-flex align-items-center"
                            ),
                            dbc.Col(
                                [
                                    dcc.Dropdown(
                                        id="circuit-selector",
                                        options=circuit_options,
                                        value="",
                                        placeholder="Select circuit...",
                                        className="mb-0"
                                    )
                                ],
                                width=8
                            )
                        ],
                        className="g-2"
                    )
                ],
                width=6,
                className="d-flex align-items-center justify-content-end"
            )
        ],
        id="header",
        className="bg-light border-bottom py-3 mb-4"
    )