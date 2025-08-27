#!/usr/bin/env python3
"""
Generate an index page with links to all generated reports for easy viewing.
"""

from pathlib import Path
import os
import webbrowser
from datetime import datetime


def create_report_index():
    """Create an HTML index page with links to all reports"""
    reports_dir = Path("reports")
    
    if not reports_dir.exists():
        print("No reports directory found")
        return None
    
    # Find all HTML reports
    html_files = sorted(reports_dir.glob("*.html"))
    
    if not html_files:
        print("No HTML reports found")
        return None
    
    # Group reports by circuit and type
    reports_by_circuit = {}
    
    for html_file in html_files:
        name = html_file.name
        
        # Extract circuit name and report type
        if "_detailed_" in name:
            circuit_name = name.split("_detailed_")[0]
            report_type = "Detailed"
        elif "_quick_" in name:
            circuit_name = name.split("_quick_")[0]
            report_type = "Quick"
        elif "_executive_" in name:
            circuit_name = name.split("_executive_")[0]
            report_type = "Executive"
        else:
            circuit_name = name.replace(".html", "")
            report_type = "Report"
        
        if circuit_name not in reports_by_circuit:
            reports_by_circuit[circuit_name] = {}
        
        reports_by_circuit[circuit_name][report_type] = html_file
    
    # Create HTML index
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Circuit Simulation Reports - Index</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        
        h1 {{
            color: #007acc;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #007acc;
            padding-bottom: 15px;
        }}
        
        h2 {{
            color: #333;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        
        .circuit-group {{
            background: #fafafa;
            border-left: 4px solid #007acc;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 0 5px 5px 0;
        }}
        
        .circuit-name {{
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .report-links {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .report-link {{
            display: inline-block;
            padding: 8px 16px;
            background: #007acc;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
            transition: background-color 0.2s;
        }}
        
        .report-link:hover {{
            background: #005fa3;
        }}
        
        .report-link.detailed {{ background: #28a745; }}
        .report-link.detailed:hover {{ background: #1e7e34; }}
        
        .report-link.quick {{ background: #ffc107; color: #333; }}
        .report-link.quick:hover {{ background: #e0a800; }}
        
        .report-link.executive {{ background: #6f42c1; }}
        .report-link.executive:hover {{ background: #59359a; }}
        
        .summary {{
            background: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 25px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007acc;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 Circuit Simulation Reports</h1>
        
        <div class="summary">
            <strong>Report Collection:</strong> Professional circuit analysis reports with interactive Plotly visualizations
            <br><strong>Generated:</strong> {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(reports_by_circuit)}</div>
                <div class="stat-label">Circuit Types</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(html_files)}</div>
                <div class="stat-label">Total Reports</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(len(reports) for reports in reports_by_circuit.values())}</div>
                <div class="stat-label">Report Variants</div>
            </div>
        </div>
"""
    
    for circuit_name, reports in sorted(reports_by_circuit.items()):
        # Clean up circuit name for display
        display_name = circuit_name.replace("_", " ").replace("-", "-")
        
        html_content += f"""
        <div class="circuit-group">
            <div class="circuit-name">{display_name}</div>
            <div class="report-links">
"""
        
        # Add links for each report type
        for report_type in ["Detailed", "Quick", "Executive"]:
            if report_type in reports:
                css_class = report_type.lower()
                html_content += f"""
                <a href="{reports[report_type].name}" class="report-link {css_class}" target="_blank">
                    📊 {report_type} Analysis
                </a>
"""
        
        html_content += """
            </div>
        </div>
"""
    
    html_content += f"""
        
        <div class="footer">
            <p>🚀 Generated by circuit-simulation report testing system</p>
            <p>Click any report link to open the interactive analysis in a new tab</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Save index file
    index_path = reports_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 Created report index: {index_path}")
    return index_path


def main():
    """Main function"""
    print("🌐 Creating Report Index Page")
    print("=" * 40)
    
    index_path = create_report_index()
    
    if index_path:
        print(f"✅ Index created successfully!")
        print(f"🔗 File: {index_path.absolute()}")
        
        # Try to open in browser
        try:
            webbrowser.open(f"file://{index_path.absolute()}")
            print("🌐 Opening in your default web browser...")
        except Exception as e:
            print(f"⚠️  Could not auto-open browser: {e}")
            print(f"💡 Manually open: file://{index_path.absolute()}")
    
    else:
        print("❌ Failed to create index")


if __name__ == "__main__":
    main()