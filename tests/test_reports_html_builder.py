"""
Test cases for HTML report builder.

Tests HTML template rendering and report generation functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from jinja2 import Environment, DictLoader

from circuit_sim.reports.builders.html_builder import HTMLBuilder


class TestHTMLBuilder:
    """Test the HTMLBuilder class."""

    def setup_method(self):
        """Setup test fixtures."""
        # Create a mock Jinja2 environment with test templates
        test_templates = {
            'detailed.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ metadata.circuit_name }} - Circuit Analysis Report</title>
</head>
<body>
    <h1>{{ metadata.circuit_name }}</h1>
    <p>{{ metadata.description }}</p>
    <div>Components: {{ metadata.component_count }}</div>
    <div>Generated: {{ metadata.generated_at }}</div>
</body>
</html>
            ''',
            'quick.html': '''
<html>
<body>
    <h1>Quick Report: {{ metadata.circuit_name }}</h1>
    <p>{{ summary.text }}</p>
</body>
</html>
            '''
        }
        
        self.test_env = Environment(loader=DictLoader(test_templates))
        self.builder = HTMLBuilder(self.test_env)

    def test_html_builder_initialization(self):
        """Test HTML builder initializes correctly."""
        assert self.builder is not None
        assert self.builder.env is not None

    def test_build_detailed_report(self):
        """Test building a detailed HTML report."""
        # Mock report data
        report_data = {
            'metadata': {
                'circuit_name': 'Test Circuit',
                'description': 'A test circuit for validation',
                'component_count': 3,
                'generated_at': '2025-08-27T10:00:00'
            },
            'charts': {
                'dc_voltages': Mock()
            }
        }

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp_file:
            output_path = tmp_file.name

        try:
            result_path = self.builder.build(report_data, 'detailed', output_path)
            
            assert result_path == output_path
            assert os.path.exists(output_path)
            
            # Read and verify content
            with open(output_path, 'r') as f:
                content = f.read()
                
            assert 'Test Circuit' in content
            assert 'A test circuit for validation' in content
            assert 'Components: 3' in content
            assert '2025-08-27T10:00:00' in content
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_build_quick_report(self):
        """Test building a quick HTML report."""
        report_data = {
            'metadata': {
                'circuit_name': 'Quick Test',
            },
            'summary': {
                'text': 'This is a quick summary.'
            }
        }

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp_file:
            output_path = tmp_file.name

        try:
            result_path = self.builder.build(report_data, 'quick', output_path)
            
            assert result_path == output_path
            assert os.path.exists(output_path)
            
            with open(output_path, 'r') as f:
                content = f.read()
                
            assert 'Quick Test' in content
            assert 'This is a quick summary.' in content
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_build_with_charts(self):
        """Test building report with Plotly charts."""
        # Mock Plotly figure
        mock_chart = Mock()
        mock_chart.to_html.return_value = '<div id="chart">Mock Chart HTML</div>'
        
        report_data = {
            'metadata': {
                'circuit_name': 'Chart Test',
                'description': 'Test with charts',
                'component_count': 1,
                'generated_at': '2025-08-27T10:00:00'
            },
            'charts': {
                'dc_voltages': mock_chart,
                'transient_voltages': mock_chart
            }
        }

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp_file:
            output_path = tmp_file.name

        try:
            result_path = self.builder.build(report_data, 'detailed', output_path)
            
            # Verify charts were processed
            assert mock_chart.to_html.call_count == 2
            
            # Check calls were made with correct parameters
            calls = mock_chart.to_html.call_args_list
            for call in calls:
                args, kwargs = call
                assert 'include_plotlyjs' in kwargs
                assert 'div_id' in kwargs
                
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_build_invalid_template_type(self):
        """Test building with invalid template type."""
        report_data = {
            'metadata': {'circuit_name': 'Test'}
        }
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp_file:
            output_path = tmp_file.name

        try:
            with pytest.raises(Exception):  # Should raise template not found error
                self.builder.build(report_data, 'nonexistent', output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_build_creates_output_directory(self):
        """Test that build creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, 'subdir', 'report.html')
            
            report_data = {
                'metadata': {'circuit_name': 'Test'},
                'summary': {'text': 'Test'}
            }
            
            result_path = self.builder.build(report_data, 'quick', output_path)
            
            assert result_path == output_path
            assert os.path.exists(output_path)
            assert os.path.exists(os.path.dirname(output_path))

    def test_chart_html_generation(self):
        """Test proper chart HTML generation and embedding."""
        mock_chart = Mock()
        mock_chart.to_html.return_value = '<div id="test-chart">Chart Content</div>'
        
        report_data = {
            'metadata': {
                'circuit_name': 'Chart HTML Test',
                'description': 'Testing chart embedding',
                'component_count': 2,
                'generated_at': '2025-08-27T10:00:00'
            },
            'charts': {
                'test_chart': mock_chart
            }
        }
        
        # Test the chart HTML generation
        charts_html = self.builder._generate_charts_html(report_data['charts'])
        
        assert 'test_chart' in charts_html
        assert '<div id="test-chart">Chart Content</div>' in charts_html['test_chart']
        
        # Verify to_html was called with correct parameters
        mock_chart.to_html.assert_called_once_with(
            include_plotlyjs='cdn',
            div_id='chart-test_chart'
        )

    def test_template_context_preparation(self):
        """Test that template context is properly prepared."""
        report_data = {
            'metadata': {'circuit_name': 'Context Test'},
            'charts': {'test': Mock()},
            'metrics': {'power': 1.5},
            'summary': {'text': 'Summary'}
        }
        
        context = self.builder._prepare_template_context(report_data)
        
        # Should include all original data
        assert context['metadata'] == report_data['metadata']
        assert context['metrics'] == report_data['metrics']
        assert context['summary'] == report_data['summary']
        
        # Should add charts_html
        assert 'charts_html' in context
        
        # Should add generation metadata
        assert 'generated_at' in context
        assert 'version' in context

    def test_error_handling_template_render(self):
        """Test error handling during template rendering."""
        # Create template with actual syntax error
        bad_templates = {
            'bad.html': '{{ undefined_variable.missing.method() }}'
        }
        
        from jinja2 import Environment, DictLoader, StrictUndefined
        bad_env = Environment(loader=DictLoader(bad_templates), undefined=StrictUndefined)
        builder = HTMLBuilder(bad_env)
        
        report_data = {'metadata': {'circuit_name': 'Test'}}
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp_file:
            output_path = tmp_file.name

        try:
            with pytest.raises(Exception):
                builder.build(report_data, 'bad', output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_file_write_error_handling(self):
        """Test handling of file write errors."""
        report_data = {
            'metadata': {'circuit_name': 'Write Test'},
            'summary': {'text': 'Test'}
        }
        
        # Try to write to read-only location (should fail gracefully)
        invalid_path = '/root/readonly/report.html'
        
        with pytest.raises((PermissionError, OSError, FileNotFoundError)):
            self.builder.build(report_data, 'quick', invalid_path)

    @patch('plotly.graph_objects.Figure')
    def test_large_report_handling(self, mock_figure):
        """Test handling of reports with many charts."""
        # Create mock charts
        mock_chart = Mock()
        mock_chart.to_html.return_value = '<div>Chart</div>'
        
        # Large number of charts
        charts = {f'chart_{i}': mock_chart for i in range(20)}
        
        report_data = {
            'metadata': {
                'circuit_name': 'Large Report',
                'description': 'Report with many charts',
                'component_count': 50,
                'generated_at': '2025-08-27T10:00:00'
            },
            'charts': charts
        }

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp_file:
            output_path = tmp_file.name

        try:
            result_path = self.builder.build(report_data, 'detailed', output_path)
            
            assert os.path.exists(result_path)
            
            # Verify all charts were processed
            assert mock_chart.to_html.call_count == 20
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)