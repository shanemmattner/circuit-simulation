"""
PDF report builder using ReportLab.

This module provides the PDFBuilder class that generates professional
PDF reports with charts, tables, and proper formatting.
"""

import os
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import utils


class PDFBuilder:
    """Build PDF reports from template data."""

    def __init__(self):
        """Initialize the PDF builder."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for PDF reports."""
        self.styles.add(
            ParagraphStyle(
                name="CircuitTitle",
                parent=self.styles["Heading1"],
                fontSize=18,
                spaceAfter=12,
                textColor=colors.HexColor("#1a1a2e"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=14,
                spaceAfter=8,
                textColor=colors.HexColor("#16213e"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CircuitBody",
                parent=self.styles["Normal"],
                fontSize=10,
                spaceAfter=6,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="MetricLabel",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.gray,
            )
        )

    def build(
        self, data: Dict[str, Any], report_type: str, output_path: str
    ) -> str:
        """
        Build a PDF report from template data.

        Args:
            data: Report data dictionary containing metadata, charts, etc.
            report_type: Type of report ('detailed', 'quick', 'executive')
            output_path: Full path where PDF file should be saved

        Returns:
            Path to the generated PDF file

        Raises:
            FileNotFoundError: If output directory cannot be created
            PermissionError: If unable to write to output path
        """
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
            pagesize=A4,
        )

        # Build story (content elements)
        story = self._build_story(data, report_type)

        # Generate PDF
        doc.build(story)

        return output_path

    def _build_story(self, data: Dict[str, Any], report_type: str) -> list:
        """
        Build the PDF story (content elements).

        Args:
            data: Report data dictionary
            report_type: Type of report

        Returns:
            List of flowable elements
        """
        story = []

        # Title
        story.extend(self._create_title_section(data))

        # Metadata section
        story.extend(self._create_metadata_section(data))

        # Circuit components table
        story.extend(self._create_components_section(data))

        # Results section
        story.extend(self._create_results_section(data))

        # Charts section
        story.extend(self._create_charts_section(data))

        # Metrics section
        story.extend(self._create_metrics_section(data))

        # Summary section
        story.extend(self._create_summary_section(data))

        # Footer
        story.extend(self._create_footer())

        return story

    def _create_title_section(self, data: Dict[str, Any]) -> list:
        """Create the title section."""
        elements = []
        metadata = data.get("metadata", {})

        title = Paragraph(
            f"Circuit Analysis Report: {metadata.get('circuit_name', 'Unknown')}",
            self.styles["CircuitTitle"],
        )
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))

        return elements

    def _create_metadata_section(self, data: Dict[str, Any]) -> list:
        """Create the metadata section."""
        elements = []
        metadata = data.get("metadata", {})
        circuit = data.get("circuit", {})

        # Report info
        elements.append(Paragraph("Report Information", self.styles["SectionHeader"]))
        
        info_data = [
            ["Report Type:", metadata.get("report_type", "N/A").title()],
            ["Analysis Type:", metadata.get("analysis_type", "N/A").upper()],
            ["Generated:", metadata.get("generated_at", "N/A")],
            ["Version:", metadata.get("version", "N/A")],
        ]

        table = Table(info_data, colWidths=[1.5 * inch, 3 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.gray),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

        # Circuit info
        elements.append(Paragraph("Circuit Overview", self.styles["SectionHeader"]))

        circuit_data = [
            ["Components:", str(circuit.get("total_components", 0))],
            ["Nodes:", str(circuit.get("total_nodes", 0))],
        ]

        table = Table(circuit_data, colWidths=[1.5 * inch, 3 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.gray),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

        return elements

    def _create_components_section(self, data: Dict[str, Any]) -> list:
        """Create the components section with table."""
        elements = []
        circuit = data.get("circuit", {})
        components = circuit.get("components", [])

        if not components:
            return elements

        elements.append(Paragraph("Components", self.styles["SectionHeader"]))

        # Table header
        table_data = [["Name", "Type", "Value", "Nodes"]]

        for comp in components:
            table_data.append(
                [
                    comp.get("name", "N/A"),
                    comp.get("type", "N/A"),
                    comp.get("value", "N/A"),
                    comp.get("nodes", "N/A"),
                ]
            )

        table = Table(table_data, colWidths=[1 * inch, 1.25 * inch, 1.25 * inch, 1.5 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

        return elements

    def _create_results_section(self, data: Dict[str, Any]) -> list:
        """Create the results section."""
        elements = []
        results = data.get("results", {})

        elements.append(Paragraph("Analysis Results", self.styles["SectionHeader"]))

        results_data = []
        if "analysis_type" in results:
            results_data.append(["Analysis Type", results["analysis_type"].upper()])
        if "execution_time" in results:
            results_data.append(["Execution Time", str(results["execution_time"])])

        if results_data:
            table = Table(results_data, colWidths=[1.5 * inch, 3 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("TEXTCOLOR", (0, 0), (0, -1), colors.gray),
                    ]
                )
            )
            elements.append(table)

        elements.append(Spacer(1, 0.3 * inch))
        return elements

    def _create_charts_section(self, data: Dict[str, Any]) -> list:
        """Create the charts section."""
        elements = []
        charts = data.get("charts", {})

        if not charts:
            return elements

        elements.append(Paragraph("Visualizations", self.styles["SectionHeader"]))

        for chart_name, chart_fig in charts.items():
            elements.append(Paragraph(chart_name.replace("_", " ").title(), self.styles["CircuitBody"]))
            
            try:
                # Save chart to temporary PNG
                img_buffer = BytesIO()
                chart_fig.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
                img_buffer.seek(0)
                
                # Create image with aspect ratio
                img = utils.ImageReader(img_buffer)
                iw, ih = img.getSize()
                aspect = ih / float(iw)
                
                # Scale to fit page width (max 6 inches)
                width = min(6 * inch, iw / 72 * inch)
                height = width * aspect
                
                img_element = Image(img_buffer, width=width, height=height)
                elements.append(img_element)
                elements.append(Spacer(1, 0.2 * inch))
            except Exception:
                # Skip charts that can't be rendered
                elements.append(Paragraph("[Chart unavailable]", self.styles["MetricLabel"]))

        elements.append(Spacer(1, 0.3 * inch))
        return elements

    def _create_metrics_section(self, data: Dict[str, Any]) -> list:
        """Create the metrics section."""
        elements = []
        metrics = data.get("metrics", {})

        if not metrics:
            return elements

        elements.append(Paragraph("Calculated Metrics", self.styles["SectionHeader"]))

        metrics_data = []
        for key, value in metrics.items():
            label = key.replace("_", " ").title()
            if isinstance(value, float):
                formatted_value = f"{value:.4g}"
            else:
                formatted_value = str(value)
            metrics_data.append([label, formatted_value])

        if metrics_data:
            table = Table(metrics_data, colWidths=[2 * inch, 2.5 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("TEXTCOLOR", (0, 0), (0, -1), colors.gray),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
                        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                    ]
                )
            )
            elements.append(table)

        elements.append(Spacer(1, 0.3 * inch))
        return elements

    def _create_summary_section(self, data: Dict[str, Any]) -> list:
        """Create the summary section."""
        elements = []
        summary = data.get("summary", {})

        elements.append(Paragraph("Summary", self.styles["SectionHeader"]))

        # Summary text
        summary_text = summary.get("text", "No summary available.")
        elements.append(Paragraph(summary_text, self.styles["CircuitBody"]))
        elements.append(Spacer(1, 0.2 * inch))

        # Key findings
        findings = summary.get("key_findings", [])
        if findings:
            elements.append(Paragraph("Key Findings", self.styles["CircuitBody"]))
            for finding in findings:
                elements.append(Paragraph(f"• {finding}", self.styles["CircuitBody"]))
            elements.append(Spacer(1, 0.2 * inch))

        # Recommendations
        recommendations = summary.get("recommendations", [])
        if recommendations:
            elements.append(Paragraph("Recommendations", self.styles["CircuitBody"]))
            for rec in recommendations:
                elements.append(Paragraph(f"• {rec}", self.styles["CircuitBody"]))

        return elements

    def _create_footer(self) -> list:
        """Create the footer section."""
        elements = []
        elements.append(PageBreak())
        
        footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        footer = Paragraph(footer_text, self.styles["MetricLabel"])
        elements.append(footer)
        
        return elements
