#!/usr/bin/env python3
"""
Manual testing script for enhanced KiCad parser with model library integration.
Run this script to interactively test the parser capabilities.
"""

from src.io.parsers.kicad_parser import KiCadParser
from pathlib import Path


def test_real_kicad_file():
    """Test with the actual KiCad file we have."""
    print("🔍 Test 1: Real KiCad File")
    print("=" * 50)
    
    parser = KiCadParser()
    netlist_path = Path("tests/fixtures/netlist_io/kicad/resistor_divider.net")
    
    if not netlist_path.exists():
        print("❌ Real KiCad file not found")
        return
    
    with open(netlist_path, 'r') as f:
        content = f.read()
    
    print(f"📁 File: {netlist_path}")
    
    # Test format detection
    format_info = parser.detect_format(content)
    print(f"\n🔍 Format Detection:")
    print(f"  Version: KiCad {format_info.version.value}")
    print(f"  Format: {format_info.format_type}")
    print(f"  Supported: {'✅' if format_info.supported else '⚠️'}")
    print(f"  Components: {format_info.features.get('component_count', 0)}")
    print(f"  Nets: {format_info.features.get('net_count', 0)}")
    
    # Parse with enhanced method
    result = parser.parse_content_with_result(content)
    
    print(f"\n⚙️ Enhanced Parsing Results:")
    print(result.summary())
    
    print(f"\n🔌 Circuit Details:")
    for comp in result.circuit.components:
        comp_type = comp.get('type', 'unknown')
        name = comp.get('name', 'unnamed') 
        if comp_type == 'resistor':
            value = comp.get('resistance', 'unknown')
        elif comp_type == 'capacitor':
            value = comp.get('capacitance', 'unknown')
        else:
            value = comp.get('model', 'no_model')
        print(f"  • {name}: {comp_type} = {value}")


def test_mixed_component_circuit():
    """Test with a manually created circuit containing various components."""
    print("\n\n🧪 Test 2: Mixed Component Circuit")
    print("=" * 50)
    
    # Create test content with transistors, diodes, op-amps
    mixed_content = """(export (version D)
  (components
    (comp (ref R1)
      (value 10k)
      (libsource (lib Device) (part R)))
    (comp (ref Q1)
      (value 2N3904)
      (libsource (lib Device) (part Q_NPN_BCE)))
    (comp (ref D1)
      (value 1N4148)
      (libsource (lib Device) (part D)))
    (comp (ref U1)
      (value LM358)
      (libsource (lib Amplifier_Operational) (part LM358)))
    (comp (ref Q2)
      (value IRF540)
      (libsource (lib Device) (part Q_NMOS_GSD)))
    (comp (ref D2)
      (value)
      (libsource (lib Device) (part LED)))
    (comp (ref U2)
      (value 7805)
      (libsource (lib Regulator_Linear) (part L7805)))
    (comp (ref U3)
      (value 74HC00)
      (libsource (lib 74xx) (part 74HC00)))
    (comp (ref C1)
      (value 100uF)
      (libsource (lib Device) (part C)))))"""
    
    parser = KiCadParser()
    
    print("📝 Test Content: 9 components with various types")
    print("  R1 (resistor), Q1 (BJT), D1 (diode), U1 (op-amp)")
    print("  Q2 (MOSFET), D2 (LED), U2 (regulator), U3 (logic), C1 (cap)")
    
    result = parser.parse_content_with_result(mixed_content)
    
    print(f"\n📊 Results:")
    print(result.summary())
    
    print(f"\n🔧 Component Analysis:")
    for comp in result.circuit.components:
        name = comp.get('name', 'unnamed')
        comp_type = comp.get('type', 'unknown') 
        model = comp.get('model', 'no_model')
        
        print(f"  • {name}: {comp_type}")
        if model != 'no_model':
            print(f"    📚 Model: {model}")
    
    # Show model mapping statistics
    if hasattr(parser, 'model_mapper') and parser.model_mapper:
        stats = parser.model_mapper.get_mapping_statistics()
        print(f"\n📈 Model Mapping Performance:")
        print(f"  Total mappings: {stats.get('total_mappings', 0)}")
        print(f"  Methods: {stats.get('methods_used', {})}")
        print(f"  Avg confidence: {stats.get('average_confidence', 0):.2%}")
        print(f"  High confidence rate: {stats.get('high_confidence_rate', 0):.2%}")
    
    return result


def test_error_handling():
    """Test error handling with problematic content.""" 
    print("\n\n⚠️ Test 3: Error Handling")
    print("=" * 50)
    
    problematic_content = """(export (version D)
  (components
    (comp (ref R1) (value 10k) (libsource (lib Device) (part R)))
    (comp (ref Q1) (value UNKNOWN_TRANSISTOR) (libsource (lib Device) (part Q_NPN)))
    (comp (ref U1) (value) (libsource (lib Unknown) (part WeirdIC)))
    (comp (ref X1) (value SomeValue) (libsource (lib Mystery) (part AlienComponent)))
    INVALID_SYNTAX_HERE))"""
    
    parser = KiCadParser()
    
    print("📝 Testing problematic content with:")
    print("  ✓ Valid resistor")  
    print("  ? Unknown transistor model")
    print("  ? Empty value IC")
    print("  ? Completely unknown component")
    print("  ❌ Invalid syntax")
    
    result = parser.parse_content_with_result(problematic_content)
    
    print(f"\n📊 Error Handling Results:")
    print(result.summary())
    
    print(f"\n🔧 What Got Imported:")
    for comp in result.circuit.components:
        name = comp.get('name', 'unnamed')
        comp_type = comp.get('type', 'unknown')
        model = comp.get('model', 'no_model')
        print(f"  ✓ {name}: {comp_type} (model: {model})")
    
    print(f"\n📋 Full Report:")
    print(result.detailed_report())


def test_component_type_detection():
    """Test component type detection in isolation.""" 
    print("\n\n🔬 Test 4: Component Type Detection")
    print("=" * 50)
    
    from src.io.parsers.component_model_mapper import ComponentTypeDetector
    
    detector = ComponentTypeDetector()
    
    # Test various KiCad symbols
    test_cases = [
        ("Device:Q_NPN_BCE", "Q1", "2N3904"),
        ("Device:Q_PNP_BCE", "Q2", "2N3906"), 
        ("Device:Q_NMOS_GSD", "Q3", "IRF540"),
        ("Device:D", "D1", "1N4148"),
        ("Device:D_Zener", "D2", "1N4733"),
        ("Device:LED", "D3", ""),
        ("Amplifier_Operational:LM358", "U1", ""),
        ("74xx:74HC00", "U2", ""),
        ("Regulator_Linear:L7805", "U3", ""),
        ("Unknown:Mystery", "X1", "Unknown"),
    ]
    
    print("🔍 Component Type Detection Results:")
    for symbol, ref, value in test_cases:
        detected_type = detector.detect_type(symbol, ref, value)
        type_info = detector.get_type_info(detected_type)
        print(f"  {ref}: {symbol}")
        print(f"     → {detected_type} ({type_info.get('description', 'Unknown')})")
        print(f"     → Default model: {type_info.get('default_model', 'None')}")
        print()


def interactive_test():
    """Interactive test where user can input KiCad content."""
    print("\n\n💬 Test 5: Interactive Testing") 
    print("=" * 50)
    print("Enter KiCad netlist content (paste and press Ctrl+D when done):")
    print("Example:")
    print('(comp (ref Q1) (value 2N3904) (libsource (lib Device) (part Q_NPN_BCE)))')
    print()
    
    try:
        # Read multi-line input
        lines = []
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
        
        user_content = '\n'.join(lines)
        
        if user_content.strip():
            parser = KiCadParser()
            result = parser.parse_content_with_result(user_content)
            
            print(f"\n📊 Your Results:")
            print(result.summary())
            
            if result.circuit.components:
                print(f"\n🔌 Components Created:")
                for comp in result.circuit.components:
                    name = comp.get('name', 'unnamed')
                    comp_type = comp.get('type', 'unknown')
                    model = comp.get('model', 'no_model')
                    print(f"  ✓ {name}: {comp_type} (model: {model})")
        else:
            print("No content provided.")
            
    except KeyboardInterrupt:
        print("\nInteractive test cancelled.")


if __name__ == "__main__":
    print("🎯 Enhanced KiCad Parser Manual Testing Suite")
    print("🚀 Phase 3: Model Library Integration Demo")
    print("=" * 60)
    
    test_real_kicad_file()
    test_mixed_component_circuit() 
    test_error_handling()
    test_component_type_detection()
    
    print("\n" + "="*60)
    print("🎉 All manual tests completed!")
    print("\nKey capabilities demonstrated:")
    print("  ✅ Real KiCad file parsing")
    print("  ✅ Mixed component type support")
    print("  ✅ Robust error handling")
    print("  ✅ Intelligent component detection")
    print("  ✅ Automatic SPICE model assignment")
    print("\n💡 Try the interactive test below if you want to test custom content!")
    
    # Uncomment to enable interactive testing
    # interactive_test()