#!/usr/bin/env python3
"""
Analyze Real KiCad Board Netlist

This script analyzes a real professional KiCad netlist file to understand its complexity
and test our import capabilities.
"""

from pathlib import Path
import re
import json
from collections import defaultdict, Counter


def analyze_kicad_netlist_structure(netlist_path):
    """Analyze the structure of a KiCad netlist file"""
    print(f"🔍 Analyzing KiCad Netlist: {netlist_path}")
    print("=" * 60)
    
    if not Path(netlist_path).exists():
        print(f"❌ File not found: {netlist_path}")
        return None
    
    try:
        with open(netlist_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return None
    
    analysis = {
        "file_size": len(content),
        "file_size_kb": round(len(content) / 1024, 2),
        "lines": len(content.split('\n')),
    }
    
    print(f"📊 File Size: {analysis['file_size_kb']} KB ({analysis['lines']:,} lines)")
    
    # Extract design metadata
    design_match = re.search(r'\(design.*?\(source "([^"]+)"\)', content, re.DOTALL)
    if design_match:
        analysis["source_file"] = design_match.group(1)
        print(f"📁 Source File: {Path(design_match.group(1)).name}")
    
    # Find tool information
    tool_match = re.search(r'\(tool "([^"]+)"\)', content)
    if tool_match:
        analysis["tool"] = tool_match.group(1)
        print(f"🔧 Tool: {analysis['tool']}")
    
    # Find project metadata
    textvars = re.findall(r'\(textvar \(name "([^"]+)"\) "([^"]+)"\)', content)
    if textvars:
        analysis["project_info"] = dict(textvars)
        print(f"📋 Project: {analysis['project_info'].get('PROJECT_NAME', 'Unknown')}")
        print(f"🏢 Company: {analysis['project_info'].get('COMPANY', 'Unknown')}")
        print(f"👨‍💻 Designer: {analysis['project_info'].get('DESIGNER', 'Unknown')}")
        print(f"📦 Revision: {analysis['project_info'].get('REVISION', 'Unknown')}")
    
    # Count sheets
    sheet_pattern = r'\(sheet \(number "(\d+)"\) \(name "([^"]+)"\)'
    sheets = re.findall(sheet_pattern, content)
    analysis["sheets"] = sheets
    print(f"📄 Sheets: {len(sheets)}")
    for num, name in sheets[:10]:  # Show first 10
        print(f"   {num}: {name}")
    if len(sheets) > 10:
        print(f"   ... and {len(sheets) - 10} more sheets")
    
    # Count components
    comp_pattern = r'\(comp \(ref "([^"]+)"\)'
    components = re.findall(comp_pattern, content)
    analysis["components"] = components
    analysis["component_count"] = len(components)
    
    # Analyze component types
    component_types = defaultdict(int)
    for comp in components:
        # Extract prefix (e.g., U, R, C, etc.)
        prefix = re.match(r'([A-Z]+)', comp)
        if prefix:
            component_types[prefix.group(1)] += 1
        else:
            component_types["OTHER"] += 1
    
    analysis["component_types"] = dict(component_types)
    
    print(f"🔌 Components: {analysis['component_count']:,} total")
    for comp_type, count in sorted(component_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / analysis['component_count']) * 100
        print(f"   {comp_type}: {count:,} ({percentage:.1f}%)")
    
    # Count nets
    net_pattern = r'\(net \(code \d+\) \(name "([^"]+)"\)'
    nets = re.findall(net_pattern, content)
    analysis["nets"] = nets
    analysis["net_count"] = len(nets)
    print(f"🕸️  Nets: {analysis['net_count']:,} total")
    
    # Find power nets
    power_nets = [net for net in nets if any(keyword in net.upper() for keyword in 
                  ['VCC', 'VDD', 'VBAT', 'VBUS', 'PWR', '+3V', '+5V', '+12V', 'POWER'])]
    ground_nets = [net for net in nets if any(keyword in net.upper() for keyword in 
                   ['GND', 'GROUND', 'AGND', 'DGND', 'PGND'])]
    
    if power_nets:
        print(f"⚡ Power nets ({len(power_nets)}): {', '.join(power_nets[:5])}")
        if len(power_nets) > 5:
            print(f"    ... and {len(power_nets) - 5} more")
    
    if ground_nets:
        print(f"🔗 Ground nets ({len(ground_nets)}): {', '.join(ground_nets[:5])}")
    
    # Find footprints
    footprint_pattern = r'\(footprint "([^"]+)"\)'
    footprints = re.findall(footprint_pattern, content)
    analysis["footprints"] = footprints
    footprint_counts = Counter(footprints)
    analysis["unique_footprints"] = len(footprint_counts)
    
    print(f"👣 Footprints: {analysis['unique_footprints']} unique types")
    for footprint, count in footprint_counts.most_common(5):
        print(f"   {footprint}: {count}x")
    
    # Analyze complexity
    complexity_score = 0
    complexity_factors = []
    
    if analysis['component_count'] > 100:
        factor = min((analysis['component_count'] - 100) // 50, 5)
        complexity_score += factor
        complexity_factors.append(f"High component count (+{factor})")
    
    if analysis['net_count'] > 200:
        factor = min((analysis['net_count'] - 200) // 100, 5)
        complexity_score += factor
        complexity_factors.append(f"High net count (+{factor})")
    
    if len(sheets) > 5:
        factor = min(len(sheets) - 5, 3)
        complexity_score += factor
        complexity_factors.append(f"Multi-sheet design (+{factor})")
    
    if analysis['unique_footprints'] > 50:
        factor = min((analysis['unique_footprints'] - 50) // 25, 3)
        complexity_score += factor
        complexity_factors.append(f"Diverse footprints (+{factor})")
    
    analysis["complexity_score"] = complexity_score
    analysis["complexity_factors"] = complexity_factors
    
    print(f"\n📊 Complexity Analysis:")
    print(f"   Complexity Score: {complexity_score}/16")
    if complexity_score <= 5:
        complexity_level = "🟢 Moderate"
    elif complexity_score <= 10:
        complexity_level = "🟡 High"
    else:
        complexity_level = "🔴 Very High"
    print(f"   Complexity Level: {complexity_level}")
    
    for factor in complexity_factors:
        print(f"   • {factor}")
    
    return analysis


def test_kicad_import_capability(netlist_path):
    """Test if we can import this KiCad netlist"""
    print(f"\n🧪 Testing Import Capability")
    print("=" * 40)
    
    # Test with our existing KiCad parser
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from circuit_sim.io.parsers.kicad_parser import KiCadNetlistParser
        
        parser = KiCadNetlistParser()
        print("✅ KiCad parser imported successfully")
        
        # Try parsing (this might fail due to complexity)
        try:
            with open(netlist_path, 'r') as f:
                content = f.read()
            
            print("🔄 Attempting to parse netlist...")
            circuit = parser.parse_content(content)
            
            print(f"✅ Parsing successful!")
            print(f"   Circuit name: {circuit.name}")
            print(f"   Components parsed: {len(circuit.components)}")
            
            return True, circuit
            
        except Exception as e:
            print(f"⚠️  Parsing failed: {e}")
            return False, str(e)
            
    except ImportError as e:
        print(f"❌ Could not import KiCad parser: {e}")
        return False, str(e)


def main():
    """Main analysis function"""
    netlist_path = "/home/shane/Desktop/skip_repos/electronics/PCB/PRE_EVT_AKA_MOGO_V2/control_board/ACTIVE/combined_control_obake_0_13/control_board/control_board.net"
    
    # Analyze structure
    analysis = analyze_kicad_netlist_structure(netlist_path)
    
    if analysis:
        # Test import capability
        success, result = test_kicad_import_capability(netlist_path)
        
        # Save analysis
        output_file = "kicad_board_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"\n💾 Analysis saved to: {output_file}")
        
        print(f"\n🎯 Summary:")
        print(f"   Professional KiCad board with {analysis['component_count']:,} components")
        print(f"   {len(analysis['sheets'])} hierarchical sheets")
        print(f"   {analysis['net_count']:,} nets with complex routing")
        print(f"   Complexity level: {analysis.get('complexity_score', 0)}/16")
        
        if success:
            print(f"   ✅ Successfully importable for simulation!")
        else:
            print(f"   ⚠️  Import challenges: {result}")


if __name__ == "__main__":
    main()