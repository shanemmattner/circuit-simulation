"""
KiCad netlist format detection.
Handles different KiCad versions and format variations gracefully.
"""

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class KiCadVersion(Enum):
    """Known KiCad versions and their characteristics."""
    V4_LEGACY = "4.x"
    V5_STABLE = "5.x"
    V6_MODERN = "6.x"
    V7_LATEST = "7.x"
    V8_FUTURE = "8.x"
    UNKNOWN = "unknown"


@dataclass
class FormatInfo:
    """Information about detected KiCad netlist format."""
    version: KiCadVersion
    format_type: str
    supported: bool
    confidence: float  # 0.0 to 1.0
    features: Dict[str, Any]  # Format-specific capabilities
    warnings: list[str]  # Any issues detected
    
    def __str__(self):
        support_status = "✓ Supported" if self.supported else "⚠ Limited support"
        return f"KiCad {self.version.value} ({self.format_type}) - {support_status}"


class FormatDetector:
    """
    Detect KiCad netlist format version and characteristics.
    Helps parser choose appropriate strategies.
    """
    
    def __init__(self):
        self.detection_patterns = {
            KiCadVersion.V4_LEGACY: [
                r'\(export\s+\(version\s+"?D"?\)',
                r'\(export\s+\(version\s+"?4\.',
                r'Eeschema.*\(4\.\d+\.\d+',
            ],
            KiCadVersion.V5_STABLE: [
                r'\(export\s+\(version\s+"?E"?\)', 
                r'\(export\s+\(version\s+"?5\.',
                r'Eeschema.*\(5\.\d+\.\d+',
            ],
            KiCadVersion.V6_MODERN: [
                r'\(kicad_netlist\s+\(version\s+"?6\.',
                r'Eeschema.*\(6\.\d+\.\d+',
                r'\(kicad_netlist\s+\(version\s+6',
            ],
            KiCadVersion.V7_LATEST: [
                r'\(kicad_netlist\s+\(version\s+"?7\.',
                r'Eeschema.*\(7\.\d+\.\d+',
            ],
            KiCadVersion.V8_FUTURE: [
                r'\(kicad_netlist\s+\(version\s+"?8\.',
                r'Eeschema.*\(8\.\d+\.\d+',
            ]
        }
    
    def detect_format(self, content: str) -> FormatInfo:
        """
        Analyze netlist content and determine format characteristics.
        
        Args:
            content: Raw netlist content
            
        Returns:
            FormatInfo with detection results
        """
        # Try to detect version
        version, confidence = self._detect_version(content)
        
        # Determine format type
        format_type = self._determine_format_type(content, version)
        
        # Check what features are present
        features = self._analyze_features(content, version)
        
        # Determine support level
        supported, warnings = self._check_support(version, features)
        
        return FormatInfo(
            version=version,
            format_type=format_type,
            supported=supported,
            confidence=confidence,
            features=features,
            warnings=warnings
        )
    
    def _detect_version(self, content: str) -> tuple[KiCadVersion, float]:
        """Detect KiCad version from content patterns."""
        
        # Check each version's patterns
        for version, patterns in self.detection_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    confidence = 0.9 if "version" in pattern else 0.7
                    return version, confidence
        
        # Fallback detection based on structure
        if "(export" in content and "(components" in content:
            return KiCadVersion.V4_LEGACY, 0.3
        elif "(kicad_netlist" in content:
            return KiCadVersion.V6_MODERN, 0.3
        else:
            return KiCadVersion.UNKNOWN, 0.0
    
    def _determine_format_type(self, content: str, version: KiCadVersion) -> str:
        """Determine the specific format characteristics."""
        
        if version in [KiCadVersion.V6_MODERN, KiCadVersion.V7_LATEST, KiCadVersion.V8_FUTURE]:
            return "modern_sexpr"  # S-expression format
        elif version in [KiCadVersion.V4_LEGACY, KiCadVersion.V5_STABLE]:
            return "legacy_sexpr"
        else:
            # Analyze structure to guess
            if "(kicad_netlist" in content:
                return "modern_sexpr"
            elif "(export" in content:
                return "legacy_sexpr"
            else:
                return "unknown"
    
    def _analyze_features(self, content: str, version: KiCadVersion) -> Dict[str, Any]:
        """Analyze what features are present in this netlist."""
        features = {
            "has_components": bool(re.search(r'\(components?', content)),
            "has_nets": bool(re.search(r'\(nets?', content)),
            "has_libparts": bool(re.search(r'\(libparts', content)),
            "has_libraries": bool(re.search(r'\(libraries', content)),
            "has_design_rules": bool(re.search(r'\(design', content)),
            "component_count": len(re.findall(r'\(comp\s', content)),
            "net_count": len(re.findall(r'\(net\s', content)),
            "hierarchical": bool(re.search(r'[/\\]', content)),  # Hierarchical names
            "quoted_values": '"' in content,
            "multiline_format": self._detect_multiline_format(content)
        }
        
        return features
    
    def _detect_multiline_format(self, content: str) -> bool:
        """Check if components span multiple lines."""
        # Look for component definitions that span multiple lines
        # This pattern should capture complete component blocks
        comp_blocks = re.findall(r'\(comp\s.*?(?=\(comp|\(nets|\(libparts|\)$)', content, re.DOTALL)
        
        for block in comp_blocks:
            if '\n' in block and len(block.split('\n')) > 2:  # More than just opening line
                return True
        
        # Alternative check: look for component ref followed by newlines and then other fields        
        if re.search(r'\(comp\s+\(ref[^)]+\)\s*\n\s*\((?:footprint|libsource|value)', content):
            return True
                
        return False
    
    def _check_support(self, version: KiCadVersion, features: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Check if this format is supported and note any limitations."""
        warnings = []
        
        # Version support matrix
        if version == KiCadVersion.UNKNOWN:
            warnings.append("Unknown KiCad version - parsing may fail")
            return False, warnings
        
        if version in [KiCadVersion.V4_LEGACY, KiCadVersion.V5_STABLE, 
                      KiCadVersion.V6_MODERN, KiCadVersion.V7_LATEST]:
            supported = True
        else:
            supported = False
            warnings.append(f"KiCad {version.value} is not fully tested")
        
        # Feature-based warnings
        if not features.get("has_components", False):
            warnings.append("No components section found")
            
        if not features.get("has_nets", False):
            warnings.append("No nets section found - connectivity may be lost")
            
        if features.get("component_count", 0) > 1000:
            warnings.append("Large netlist (>1000 components) - parsing may be slow")
            
        if features.get("hierarchical", False):
            warnings.append("Hierarchical design detected - some features may not work")
        
        if features.get("multiline_format", False):
            warnings.append("Multi-line component format - using advanced parser")
        
        return supported, warnings
    
    def get_parser_recommendations(self, format_info: FormatInfo) -> Dict[str, Any]:
        """Get recommended parser settings based on detected format."""
        
        recommendations = {
            "use_value_extractor": True,  # Always use robust value extraction
            "strict_parsing": format_info.confidence > 0.8,
            "multiline_support": format_info.features.get("multiline_format", False),
            "quoted_value_handling": format_info.features.get("quoted_values", True),
            "hierarchical_support": format_info.features.get("hierarchical", False)
        }
        
        # Version-specific recommendations
        if format_info.version == KiCadVersion.V4_LEGACY:
            recommendations.update({
                "component_section_name": "components",
                "nets_section_name": "nets", 
                "expect_libparts": True
            })
        elif format_info.version in [KiCadVersion.V6_MODERN, KiCadVersion.V7_LATEST]:
            recommendations.update({
                "modern_format": True,
                "enhanced_properties": True,
                "symbol_library_support": True
            })
        
        return recommendations