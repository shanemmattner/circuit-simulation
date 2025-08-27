"""
Component-to-SPICE model mapping for KiCad import enhancement.
Maps KiCad symbols to appropriate SPICE models using multiple strategies.
"""

import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from functools import lru_cache

from src.models.spice_loader import SpiceModelLoader


@dataclass
class ComponentModel:
    """Represents a mapped component with its SPICE model."""
    type: str                    # Component type (bjt_transistor, diode, etc.)
    spice_model: str            # SPICE model text or reference
    confidence: float           # Confidence in mapping (0.0 to 1.0)
    method: str                 # Mapping method used
    nodes: List[str]           # Node names for the component
    warning: Optional[str] = None


class ComponentTypeDetector:
    """
    Detect component type from KiCad symbols using pattern matching.
    
    Uses multiple clues:
    1. KiCad symbol library name (e.g., "Device:Q_NPN_BCE")
    2. Component value (e.g., "2N3904")
    3. Component reference (e.g., "Q1" indicates transistor)
    """
    
    def __init__(self):
        """Initialize the detector with pattern mappings."""
        
        # Symbol patterns for different component types
        # Order matters - more specific patterns first
        self.symbol_patterns = {
            # Voltage Regulators (check before opamps due to LM pattern overlap)
            'regulator_linear': [
                r'.*Regulator_Linear.*', r'.*:L78[0-9]+.*', r'.*:79[0-9]+.*',
                r'.*:L7[89][0-9]+.*', r'.*:78L[0-9]+.*'
            ],
            'regulator_switching': [
                r'.*Regulator_Switching.*', r'.*:LM25[0-9]+.*', r'.*Buck.*',
                r'.*Boost.*'
            ],
            
            # BJT Transistors
            'transistor_bjt_npn': [
                r'.*Q_NPN.*', r'.*NPN.*', r'.*:2N[0-9]+.*', r'.*:BC[0-9]+.*',
                r'.*Transistor_BJT:.*NPN.*', r'.*:Q_NPN_.*'
            ],
            'transistor_bjt_pnp': [
                r'.*Q_PNP.*', r'.*PNP.*', r'.*:2N[0-9]+P.*',
                r'.*Transistor_BJT:.*PNP.*', r'.*:Q_PNP_.*'
            ],
            
            # MOSFET Transistors  
            'transistor_mosfet_n': [
                r'.*Q_NMOS.*', r'.*NMOS.*', r'.*IRF[0-9]+N.*', r'.*FET.*N.*',
                r'.*Transistor_FET:.*N.*'
            ],
            'transistor_mosfet_p': [
                r'.*Q_PMOS.*', r'.*PMOS.*', r'.*IRF[0-9]+P.*', r'.*FET.*P.*',
                r'.*Transistor_FET:.*P.*'
            ],
            
            # Diodes
            'diode_signal': [
                r'.*:D$', r'.*:1N41[0-9]+.*', r'.*Signal.*'  # 1N41xx series are signal diodes
            ],
            'diode_power': [
                r'.*:1N4[0-9]+.*', r'.*Power.*Diode.*', r'.*Rectifier.*', r'.*Diode:1N4[0-9]+.*'
            ],
            'diode_zener': [
                r'.*D_Zener.*', r'.*Zener.*', r'.*:1N[0-9]+Z.*'
            ],
            'diode_led': [
                r'.*LED.*', r'.*Light.*Emitting.*'
            ],
            
            # Operational Amplifiers
            'opamp': [
                r'.*Amplifier_Operational.*', r'.*OpAmp.*', r'.*:LM[0-9]+.*',
                r'.*:TL[0-9]+.*', r'.*:AD[0-9]+.*'
            ],
            
            # Logic Gates
            'logic_gate': [
                r'.*74[A-Z]*[0-9]+.*', r'.*4[0-9]+.*', r'.*Logic.*',
                r'.*AND.*', r'.*OR.*', r'.*NOT.*', r'.*XOR.*'
            ]
        }
        
        # Value patterns (component values that indicate type)
        self.value_patterns = {
            'transistor_bjt_npn': [r'^2N[0-9]+$', r'^BC[0-9]+[^P]*$', r'^Q[0-9]+N$'],
            'transistor_bjt_pnp': [r'^2N[0-9]+P$', r'^BC[0-9]+P$', r'^Q[0-9]+P$'],
            'transistor_mosfet_n': [r'^IRF[0-9]+N?$', r'^2N[0-9]+N$'],
            'transistor_mosfet_p': [r'^IRF[0-9]+P$', r'^2N[0-9]+P$'],
            'diode_signal': [r'^1N[0-9]+$', r'^BAT[0-9]+$'],
            'diode_power': [r'^1N4[0-9]+$'],
            'diode_zener': [r'^1N[0-9]+Z$', r'^BZ[A-Z][0-9]+$'],
            'opamp': [r'^LM[0-9]+$', r'^TL[0-9]+$', r'^AD[0-9]+$']
        }
        
        # Reference patterns (component references that indicate type)
        self.reference_patterns = {
            'transistor_bjt': r'^Q[0-9]*$',
            'transistor_mosfet': r'^Q[0-9]*$',  # Same as BJT, need symbol to distinguish
            'diode': r'^D[0-9]*$',
            'opamp': r'^U[0-9]*$',
            'logic_gate': r'^U[0-9]*$',
            'regulator': r'^U[0-9]*$'
        }
    
    def detect_type(self, kicad_symbol: str, reference: str, value: str) -> str:
        """
        Detect component type from KiCad symbol, reference, and value.
        
        Args:
            kicad_symbol: KiCad symbol name (e.g., "Device:Q_NPN_BCE") 
            reference: Component reference (e.g., "Q1")
            value: Component value (e.g., "2N3904")
            
        Returns:
            String indicating component type (e.g., "transistor_bjt_npn")
        """
        
        # Strategy 1: Check symbol patterns first (most specific)
        symbol_type = self._match_symbol_patterns(kicad_symbol)
        if symbol_type:
            return symbol_type
            
        # Strategy 2: Check value patterns
        value_type = self._match_value_patterns(value)
        if value_type:
            return value_type
            
        # Strategy 3: Check reference patterns (least specific)
        ref_type = self._match_reference_patterns(reference)
        if ref_type:
            return ref_type
            
        # Strategy 4: Generic fallback based on reference prefix
        if reference:
            first_char = reference[0].upper()
            if first_char == 'Q':
                return 'transistor_bjt'  # Generic transistor
            elif first_char == 'D': 
                return 'diode'
            elif first_char == 'U':
                return 'ic'  # Generic IC
                
        # Strategy 5: Unknown component
        return 'unknown'
    
    def _match_symbol_patterns(self, symbol: str) -> Optional[str]:
        """Match KiCad symbol against symbol patterns."""
        for comp_type, patterns in self.symbol_patterns.items():
            for pattern in patterns:
                if re.match(pattern, symbol, re.IGNORECASE):
                    return comp_type
        return None
        
    def _match_value_patterns(self, value: str) -> Optional[str]:
        """Match component value against value patterns."""
        if not value or value.strip() == "":
            return None
            
        for comp_type, patterns in self.value_patterns.items():
            for pattern in patterns:
                if re.match(pattern, value, re.IGNORECASE):
                    return comp_type
        return None
        
    def _match_reference_patterns(self, reference: str) -> Optional[str]:
        """Match component reference against reference patterns."""
        if not reference or reference.strip() == "":
            return None
            
        for comp_type, pattern in self.reference_patterns.items():
            if re.match(pattern, reference, re.IGNORECASE):
                return comp_type
        return None
    
    def get_supported_types(self) -> List[str]:
        """Get list of all supported component types."""
        return list(self.symbol_patterns.keys()) + ['unknown']
    
    def get_type_info(self, comp_type: str) -> Dict[str, Any]:
        """Get information about a component type."""
        type_info = {
            'transistor_bjt_npn': {
                'description': 'NPN Bipolar Junction Transistor',
                'pins': ['collector', 'base', 'emitter'],
                'default_model': '2N3904'
            },
            'transistor_bjt_pnp': {
                'description': 'PNP Bipolar Junction Transistor', 
                'pins': ['collector', 'base', 'emitter'],
                'default_model': '2N3906'
            },
            'transistor_mosfet_n': {
                'description': 'N-Channel MOSFET',
                'pins': ['drain', 'gate', 'source', 'bulk'],
                'default_model': 'IRF540'
            },
            'transistor_mosfet_p': {
                'description': 'P-Channel MOSFET',
                'pins': ['drain', 'gate', 'source', 'bulk'], 
                'default_model': 'IRF9540'
            },
            'diode': {
                'description': 'Generic Diode',
                'pins': ['anode', 'cathode'],
                'default_model': '1N4148'
            },
            'diode_signal': {
                'description': 'Signal Diode',
                'pins': ['anode', 'cathode'],
                'default_model': '1N4148'
            },
            'diode_power': {
                'description': 'Power Diode',
                'pins': ['anode', 'cathode'],
                'default_model': '1N4007'
            },
            'diode_zener': {
                'description': 'Zener Diode',
                'pins': ['anode', 'cathode'],
                'default_model': '1N4733'
            },
            'diode_led': {
                'description': 'Light Emitting Diode',
                'pins': ['anode', 'cathode'],
                'default_model': 'LED_RED'
            },
            'opamp': {
                'description': 'Operational Amplifier',
                'pins': ['vplus', 'vminus', 'vout', 'vcc', 'vee'],
                'default_model': 'LM358'
            },
            'logic_gate': {
                'description': 'Logic Gate',
                'pins': ['inputs', 'outputs', 'vcc', 'gnd'],
                'default_model': '74HC00'
            },
            'regulator_linear': {
                'description': 'Linear Voltage Regulator',
                'pins': ['vin', 'vout', 'gnd'],
                'default_model': '7805'
            }
        }
        
        return type_info.get(comp_type, {
            'description': 'Unknown Component',
            'pins': [],
            'default_model': 'GENERIC'
        })


class ExactSymbolMatch:
    """
    Strategy for finding exact matches between KiCad symbols/values and SPICE models.
    
    Tries multiple approaches:
    1. Direct value match (e.g., value="2N3904" → load 2N3904 model)
    2. Symbol parsing (e.g., "Transistor_BJT:2N3904" → extract "2N3904")
    3. Library reference matching
    """
    
    def __init__(self, model_loader: SpiceModelLoader):
        """Initialize with model loader."""
        self.model_loader = model_loader
        self.detector = ComponentTypeDetector()
    
    def find_model(self, kicad_symbol: str, reference: str, value: str) -> Optional[ComponentModel]:
        """
        Find exact SPICE model match for KiCad component.
        
        Args:
            kicad_symbol: KiCad symbol (e.g., "Device:Q_NPN_BCE")
            reference: Component reference (e.g., "Q1")
            value: Component value (e.g., "2N3904")
            
        Returns:
            ComponentModel if exact match found, None otherwise
        """
        
        # Detect component type first
        comp_type = self.detector.detect_type(kicad_symbol, reference, value)
        if comp_type == "unknown":
            return None
            
        # Strategy 1: Try exact value match first (highest confidence)
        if value and value.strip():
            model = self._try_value_match(value.strip(), comp_type)
            if model:
                return ComponentModel(
                    type=comp_type,
                    spice_model=model,
                    confidence=1.0,  # Exact match
                    method="exact_value_match",
                    nodes=self._get_nodes_for_type(comp_type)
                )
        
        # Strategy 2: Try to extract model name from symbol
        symbol_model = self._extract_model_from_symbol(kicad_symbol)
        if symbol_model:
            model = self._try_value_match(symbol_model, comp_type)
            if model:
                return ComponentModel(
                    type=comp_type,
                    spice_model=model,
                    confidence=0.9,  # Very high confidence
                    method="exact_symbol_match", 
                    nodes=self._get_nodes_for_type(comp_type)
                )
        
        # No exact match found
        return None
    
    def _try_value_match(self, model_name: str, comp_type: str) -> Optional[str]:
        """Try to load a SPICE model by name."""
        try:
            # Map component type to loader method
            if comp_type.startswith('transistor_bjt'):
                return self.model_loader.load_transistor(model_name)
            elif comp_type.startswith('transistor_mosfet'):
                return self.model_loader.load_transistor(model_name)  # Same loader for now
            elif comp_type.startswith('diode'):
                return self.model_loader.load_diode(model_name)
            elif comp_type == 'opamp':
                return self.model_loader.load_opamp(model_name)
            elif comp_type.startswith('regulator'):
                # Try as opamp first, then transistor
                try:
                    return self.model_loader.load_opamp(model_name)
                except:
                    return self.model_loader.load_transistor(model_name)
            else:
                # Generic attempt - try transistor first (most common)
                try:
                    return self.model_loader.load_transistor(model_name)
                except:
                    try:
                        return self.model_loader.load_diode(model_name)
                    except:
                        return self.model_loader.load_opamp(model_name)
                        
        except Exception:
            # Model not found or loading failed
            return None
    
    def _extract_model_from_symbol(self, kicad_symbol: str) -> Optional[str]:
        """Extract model name from KiCad symbol."""
        
        # Common patterns in KiCad symbols
        patterns = [
            # "Transistor_BJT:2N3904" → "2N3904"
            r'.*:([A-Z0-9]+[0-9]+[A-Z]?)$',
            
            # "Device:2N3904" → "2N3904"  
            r'.*:([0-9][A-Z0-9]+)$',
            
            # "Linear:LM358" → "LM358"
            r'.*:([A-Z]{2,}[0-9]+[A-Z]*)$',
            
            # "74xx:74LS00" → "74LS00"
            r'.*:([0-9]{2}[A-Z]*[0-9]+)$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, kicad_symbol)
            if match:
                return match.group(1)
                
        return None
    
    def _get_nodes_for_type(self, comp_type: str) -> List[str]:
        """Get standard node names for component type."""
        type_info = self.detector.get_type_info(comp_type)
        return type_info.get('pins', [])
    
    @lru_cache(maxsize=256)
    def _cached_model_lookup(self, model_name: str, comp_type: str) -> Optional[str]:
        """Cached version of model lookup for performance."""
        return self._try_value_match(model_name, comp_type)


class FuzzySymbolMatch:
    """
    Strategy for finding similar matches when exact matches aren't available.
    
    Uses:
    1. Levenshtein distance for similar model names  
    2. Component type-based generic models
    3. Pattern matching for component families
    """
    
    def __init__(self, model_loader: SpiceModelLoader):
        """Initialize with model loader."""
        self.model_loader = model_loader
        self.detector = ComponentTypeDetector()
        
        # Generic models by type for fallback
        self.generic_models = {
            'transistor_bjt_npn': '2N3904',
            'transistor_bjt_pnp': '2N3906', 
            'transistor_mosfet_n': 'IRF540',
            'transistor_mosfet_p': 'IRF9540',
            'diode_signal': '1N4148',
            'diode_power': '1N4007',
            'diode_zener': '1N4733',
            'diode_led': 'LED_RED',
            'opamp': 'LM358',
            'logic_gate': '74HC00',
            'regulator_linear': '7805'
        }
    
    def find_model(self, kicad_symbol: str, reference: str, value: str) -> Optional[ComponentModel]:
        """
        Find similar SPICE model match for KiCad component.
        
        Returns:
            ComponentModel if similar match found, None otherwise
        """
        
        # Detect component type
        comp_type = self.detector.detect_type(kicad_symbol, reference, value)
        if comp_type == "unknown":
            return None
        
        # Strategy 1: Try fuzzy matching on value if provided
        if value and value.strip():
            fuzzy_model = self._find_similar_model(value.strip(), comp_type)
            if fuzzy_model:
                confidence = self._calculate_confidence(value.strip(), fuzzy_model['name'])
                return ComponentModel(
                    type=comp_type,
                    spice_model=fuzzy_model['model'],
                    confidence=confidence,
                    method="fuzzy_match",
                    nodes=self._get_nodes_for_type(comp_type),
                    warning=f"Using similar model {fuzzy_model['name']} instead of {value}"
                )
        
        # Strategy 2: Use generic model for component type
        generic_model_name = self.generic_models.get(comp_type)
        if generic_model_name:
            try:
                model = self._load_model_by_type(generic_model_name, comp_type)
                if model:
                    return ComponentModel(
                        type=comp_type,
                        spice_model=model,
                        confidence=0.5,  # Medium confidence for generic
                        method="generic_type_match",
                        nodes=self._get_nodes_for_type(comp_type),
                        warning=f"Using generic {comp_type} model {generic_model_name}"
                    )
            except Exception:
                pass  # Generic model not available, fall through
        
        # No fuzzy match found
        return None
    
    def _find_similar_model(self, target: str, comp_type: str) -> Optional[Dict[str, str]]:
        """Find similar model using fuzzy matching."""
        try:
            # Get available models for this component type
            available_models = self._get_available_models_for_type(comp_type)
            
            if not available_models:
                return None
            
            # Find the most similar model name
            best_match = None
            best_similarity = 0.0
            
            for model_name in available_models:
                similarity = self._calculate_similarity(target, model_name)
                if similarity > best_similarity and similarity > 0.6:  # Minimum threshold
                    best_similarity = similarity
                    best_match = model_name
            
            if best_match:
                model = self._load_model_by_type(best_match, comp_type)
                if model:
                    return {'name': best_match, 'model': model}
                    
        except Exception:
            pass  # Model loading failed
            
        return None
    
    def _get_available_models_for_type(self, comp_type: str) -> List[str]:
        """Get list of available models for component type."""
        try:
            if comp_type.startswith('transistor'):
                return self.model_loader.get_available_models("Transistor") or []
            elif comp_type.startswith('diode'):
                return self.model_loader.get_available_models("Diode") or []
            elif comp_type == 'opamp':
                return self.model_loader.get_available_models("Operational Amplifier") or []
            else:
                # Return some common models as fallback
                return ["2N3904", "1N4148", "LM358"]
        except Exception:
            return []
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using simplified metric."""
        
        str1 = str1.upper()
        str2 = str2.upper()
        
        # Simple similarity metrics
        if str1 == str2:
            return 1.0
        
        # Check if one is a substring of the other
        if str1 in str2 or str2 in str1:
            return 0.8
        
        # Check for common prefix/suffix
        common_prefix = 0
        for i, (c1, c2) in enumerate(zip(str1, str2)):
            if c1 == c2:
                common_prefix = i + 1
            else:
                break
        
        # Simple edit distance approximation
        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return 1.0
            
        prefix_score = common_prefix / max_len
        
        # Boost score for similar component families
        if self._same_component_family(str1, str2):
            prefix_score += 0.2
        
        return min(prefix_score, 1.0)
    
    def _same_component_family(self, str1: str, str2: str) -> bool:
        """Check if two model names are from the same component family."""
        
        # Component families
        families = [
            ['2N3904', '2N3906', '2N2222', '2N2907'],  # Common BJTs
            ['1N4148', '1N4007', '1N4001', '1N4004'],  # Common diodes
            ['LM358', 'LM324', 'LM741'],               # Common op-amps
            ['IRF540', 'IRF9540', 'IRF520', 'IRF640'] # Power MOSFETs
        ]
        
        for family in families:
            if str1 in family and str2 in family:
                return True
                
        return False
    
    def _load_model_by_type(self, model_name: str, comp_type: str) -> Optional[str]:
        """Load model using appropriate loader method."""
        try:
            if comp_type.startswith('transistor'):
                return self.model_loader.load_transistor(model_name)
            elif comp_type.startswith('diode'):
                return self.model_loader.load_diode(model_name) 
            elif comp_type == 'opamp':
                return self.model_loader.load_opamp(model_name)
            else:
                return None
        except Exception:
            return None
    
    def _get_nodes_for_type(self, comp_type: str) -> List[str]:
        """Get standard node names for component type."""
        type_info = self.detector.get_type_info(comp_type)
        return type_info.get('pins', [])
    
    def _calculate_confidence(self, original: str, matched: str) -> float:
        """Calculate confidence based on similarity."""
        similarity = self._calculate_similarity(original, matched)
        # Scale to reasonable confidence range for fuzzy matches (0.3 to 0.8)
        return 0.3 + (similarity * 0.5)


class DefaultBehavioral:
    """
    Fallback strategy that provides basic behavioral models for any component.
    
    Ensures that no component fails to import - everything gets some kind of model,
    even if it's just a basic behavioral approximation.
    """
    
    def __init__(self):
        """Initialize with behavioral model templates."""
        self.detector = ComponentTypeDetector()
        
        # Basic SPICE behavioral models for unknown components
        self.behavioral_models = {
            'transistor_bjt_npn': self._generic_npn_model,
            'transistor_bjt_pnp': self._generic_pnp_model,
            'transistor_bjt': self._generic_npn_model,  # Generic BJT fallback
            'transistor_mosfet_n': self._generic_nmos_model,
            'transistor_mosfet_p': self._generic_pmos_model,
            'transistor_mosfet': self._generic_nmos_model,  # Generic MOSFET fallback
            'diode': self._generic_diode_model,
            'opamp': self._generic_opamp_model,
            'ic': self._generic_opamp_model,  # Generic IC fallback
            'logic_gate': self._generic_logic_model,
            'regulator_linear': self._generic_regulator_model,
            'unknown': self._generic_resistor_model  # Ultimate fallback
        }
    
    def find_model(self, kicad_symbol: str, reference: str, value: str) -> ComponentModel:
        """
        Always returns a behavioral model - never fails.
        
        Returns:
            ComponentModel with basic behavioral model
        """
        
        # Detect component type (fallback to reference-based if needed)
        comp_type = self.detector.detect_type(kicad_symbol, reference, value)
        
        # Get behavioral model generator
        model_generator = self.behavioral_models.get(comp_type, self.behavioral_models['unknown'])
        
        # Generate behavioral SPICE model
        spice_model = model_generator(reference, value)
        
        return ComponentModel(
            type=comp_type if comp_type != "unknown" else "behavioral",
            spice_model=spice_model,
            confidence=0.2,  # Low confidence for behavioral
            method="default_behavioral",
            nodes=self._get_nodes_for_type(comp_type),
            warning=f"Using behavioral model for {reference} - may not be accurate"
        )
    
    def _generic_npn_model(self, ref: str, value: str) -> str:
        """Generate generic NPN transistor behavioral model."""
        return f"""
* Generic NPN Transistor Model for {ref}
.model {ref}_NPN NPN(BF=100 BR=1 IS=1e-14 VAF=100)
Q{ref}_behav %collector% %base% %emitter% {ref}_NPN
"""
    
    def _generic_pnp_model(self, ref: str, value: str) -> str:
        """Generate generic PNP transistor behavioral model."""
        return f"""
* Generic PNP Transistor Model for {ref}
.model {ref}_PNP PNP(BF=100 BR=1 IS=1e-14 VAF=100)
Q{ref}_behav %collector% %base% %emitter% {ref}_PNP
"""
    
    def _generic_nmos_model(self, ref: str, value: str) -> str:
        """Generate generic NMOS behavioral model."""
        return f"""
* Generic NMOS Model for {ref}
.model {ref}_NMOS NMOS(VTO=2 KP=50u LAMBDA=0.01)
M{ref}_behav %drain% %gate% %source% %bulk% {ref}_NMOS
"""
    
    def _generic_pmos_model(self, ref: str, value: str) -> str:
        """Generate generic PMOS behavioral model."""
        return f"""
* Generic PMOS Model for {ref}
.model {ref}_PMOS PMOS(VTO=-2 KP=25u LAMBDA=0.01)
M{ref}_behav %drain% %gate% %source% %bulk% {ref}_PMOS
"""
    
    def _generic_diode_model(self, ref: str, value: str) -> str:
        """Generate generic diode behavioral model."""
        return f"""
* Generic Diode Model for {ref}
.model {ref}_DIODE D(IS=1e-14 N=1 RS=0 CJO=1e-12)
D{ref}_behav %anode% %cathode% {ref}_DIODE
"""
    
    def _generic_opamp_model(self, ref: str, value: str) -> str:
        """Generate generic op-amp behavioral model using VCVS."""
        return f"""
* Generic Op-Amp Model for {ref}
* Behavioral model using voltage-controlled voltage source
E{ref}_behav %vout% 0 %vplus% %vminus% 100000
Rin{ref} %vplus% %vminus% 1MEG
Rout{ref} %vout% 0 75
"""
    
    def _generic_logic_model(self, ref: str, value: str) -> str:
        """Generate generic logic gate behavioral model."""
        return f"""
* Generic Logic Gate Model for {ref}
* Simple behavioral digital logic
.model {ref}_LOGIC D(IS=1e-15 N=1)
* Implement as voltage-controlled switch for now
* Full digital modeling requires specific logic family parameters
"""
    
    def _generic_regulator_model(self, ref: str, value: str) -> str:
        """Generate generic voltage regulator behavioral model."""
        # Try to extract output voltage from value or use 5V default
        output_voltage = "5"
        if value:
            # Look for voltage patterns in value
            voltage_match = re.search(r'(\d+)\.?(\d*)[Vv]?', value)
            if voltage_match:
                output_voltage = voltage_match.group(1)
                if voltage_match.group(2):
                    output_voltage += "." + voltage_match.group(2)
        
        return f"""
* Generic Linear Regulator Model for {ref}
* Behavioral voltage regulator
E{ref}_reg %vout% 0 VALUE={{max(0, min(V(%vin%) - 2, {output_voltage}))}}
Rreg{ref} %vout% 0 0.1
"""
    
    def _generic_resistor_model(self, ref: str, value: str) -> str:
        """Ultimate fallback - treat unknown component as resistor."""
        resistance = value if value and re.match(r'[\d.]+[kKmMuUnN]?', value) else "1k"
        return f"R{ref}_behav %pin1% %pin2% {resistance}"
    
    def _get_nodes_for_type(self, comp_type: str) -> List[str]:
        """Get standard node names for component type."""
        type_info = self.detector.get_type_info(comp_type)
        return type_info.get('pins', [])


class ComponentModelMapper:
    """
    Main orchestrator for component-to-model mapping.
    
    Uses a cascade of strategies:
    1. ExactSymbolMatch - Try exact matches first
    2. FuzzySymbolMatch - Try similar matches
    3. DefaultBehavioral - Always succeeds with behavioral models
    """
    
    def __init__(self, model_loader: SpiceModelLoader):
        """Initialize with model loader and all strategies."""
        self.model_loader = model_loader
        
        # Initialize strategies in priority order
        self.strategies = [
            ExactSymbolMatch(model_loader),
            FuzzySymbolMatch(model_loader), 
            DefaultBehavioral()  # Always succeeds
        ]
        
        # Cache for performance
        self._mapping_cache = {}
    
    def map_component(self, kicad_symbol: str, reference: str, value: str) -> ComponentModel:
        """
        Map KiCad component to appropriate SPICE model.
        
        This method always succeeds - it will find some model for any component.
        
        Args:
            kicad_symbol: KiCad symbol (e.g., "Device:Q_NPN_BCE") 
            reference: Component reference (e.g., "Q1")
            value: Component value (e.g., "2N3904")
            
        Returns:
            ComponentModel with appropriate SPICE model and metadata
        """
        
        # Create cache key
        cache_key = f"{kicad_symbol}|{reference}|{value}"
        
        # Check cache first
        if cache_key in self._mapping_cache:
            return self._mapping_cache[cache_key]
        
        # Try each strategy in order
        for strategy in self.strategies:
            result = strategy.find_model(kicad_symbol, reference, value)
            if result:
                # Cache the result
                self._mapping_cache[cache_key] = result
                return result
        
        # This should never happen because DefaultBehavioral always succeeds
        # But just in case, provide ultimate fallback
        return ComponentModel(
            type="unknown",
            spice_model=f"R{reference}_fallback %pin1% %pin2% 1k",
            confidence=0.1,
            method="emergency_fallback",
            nodes=[],
            warning="Emergency fallback - component may not work correctly"
        )
    
    def get_mapping_statistics(self) -> Dict[str, Any]:
        """Get statistics about mapping performance."""
        if not self._mapping_cache:
            return {"total_mappings": 0}
        
        methods = {}
        confidences = []
        types = {}
        
        for result in self._mapping_cache.values():
            # Count methods
            methods[result.method] = methods.get(result.method, 0) + 1
            
            # Track confidence distribution
            confidences.append(result.confidence)
            
            # Count component types
            types[result.type] = types.get(result.type, 0) + 1
        
        avg_confidence = sum(confidences) / len(confidences)
        
        return {
            "total_mappings": len(self._mapping_cache),
            "methods_used": methods,
            "component_types": types,
            "average_confidence": avg_confidence,
            "high_confidence_rate": len([c for c in confidences if c > 0.7]) / len(confidences)
        }
    
    def clear_cache(self):
        """Clear the mapping cache."""
        self._mapping_cache.clear()