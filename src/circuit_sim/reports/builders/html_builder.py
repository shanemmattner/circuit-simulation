"""
HTML report builder using Jinja2 templates.

This module provides the HTMLBuilder class that generates professional
HTML reports with embedded Plotly charts and proper styling.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from jinja2 import Environment


class HTMLBuilder:
    """Build HTML reports from template data."""

    def __init__(self, jinja_env: Environment):
        """
        Initialize the HTML builder.

        Args:
            jinja_env: Configured Jinja2 environment with templates loaded
        """
        self.env = jinja_env

    def build(self, data: Dict[str, Any], report_type: str, output_path: str) -> str:
        """
        Build an HTML report from template data.

        Args:
            data: Report data dictionary containing metadata, charts, etc.
            report_type: Type of report template to use ('detailed', 'quick', etc.)
            output_path: Full path where HTML file should be saved

        Returns:
            Path to the generated HTML file

        Raises:
            TemplateNotFound: If the specified template doesn't exist
            FileNotFoundError: If output directory cannot be created
            PermissionError: If unable to write to output path
        """
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Prepare template context
        context = self._prepare_template_context(data)

        # Render template
        template = self.env.get_template(f"{report_type}.html")
        html_content = template.render(**context)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _prepare_template_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare template context with all necessary data.

        Args:
            data: Raw report data

        Returns:
            Template context dictionary
        """
        # Start with all original data
        context = dict(data)

        # Generate chart HTML
        if 'charts' in data:
            context['charts_html'] = self._generate_charts_html(data['charts'])

        # Add generation metadata
        context['generated_at'] = datetime.now().isoformat()
        context['version'] = "1.0.0"

        return context

    def _generate_charts_html(self, charts: Dict[str, Any]) -> Dict[str, str]:
        """
        Convert Plotly chart objects to HTML strings.

        Args:
            charts: Dictionary of chart name -> Plotly figure objects

        Returns:
            Dictionary of chart name -> HTML string
        """
        charts_html = {}

        for chart_name, chart_fig in charts.items():
            if hasattr(chart_fig, 'to_html'):
                # Generate HTML for Plotly figure
                chart_html = chart_fig.to_html(
                    include_plotlyjs='cdn',
                    div_id=f'chart-{chart_name}'
                )
                charts_html[chart_name] = chart_html
            else:
                # Fallback for non-Plotly objects
                charts_html[chart_name] = f'<div id="chart-{chart_name}">Chart not available</div>'

        return charts_html