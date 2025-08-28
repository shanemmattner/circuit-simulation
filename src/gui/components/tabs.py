"""Tab navigation system for Circuit Analysis Dashboard."""

from dash import html
import dash_bootstrap_components as dbc


def create_tab_navigation() -> dbc.Tabs:
    """Create the main tab navigation for analysis types.

    Returns:
        Dash tabs component with DC, AC, Transient, Reports, and Jobs tabs
    """
    return dbc.Tabs(
        [
            dbc.Tab(
                label="DC Analysis",
                tab_id="dc-analysis",
                active_label_style={"color": "#007bff", "font-weight": "bold"},
            ),
            dbc.Tab(
                label="AC Analysis",
                tab_id="ac-analysis",
                active_label_style={"color": "#007bff", "font-weight": "bold"},
            ),
            dbc.Tab(
                label="Transient",
                tab_id="transient-analysis",
                active_label_style={"color": "#007bff", "font-weight": "bold"},
            ),
            dbc.Tab(
                label="Reports",
                tab_id="reports",
                active_label_style={"color": "#007bff", "font-weight": "bold"},
            ),
            dbc.Tab(
                label="Jobs",
                tab_id="jobs",
                active_label_style={"color": "#007bff", "font-weight": "bold"},
            ),
        ],
        id="analysis-tabs",
        active_tab="dc-analysis",
        className="mb-4",
    )


def create_tab_content() -> html.Div:
    """Create the main content area that changes based on selected tab.

    Returns:
        Dash div component for tab content display
    """
    return html.Div(
        [
            html.P(
                "Select an analysis tab to view results.",
                className="text-muted text-center mt-5",
            )
        ],
        id="tab-content",
        className="min-vh-50 border rounded p-4",
    )
