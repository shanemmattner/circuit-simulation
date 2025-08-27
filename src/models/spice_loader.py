"""SPICE model loader for KiCad-Spice-Library integration."""

import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from functools import lru_cache


class ModelNotFoundError(Exception):
    """Exception raised when a SPICE model cannot be found."""
    
    def __init__(self, model_name: str, searched_paths: List[Path] = None):
        self.model_name = model_name
        self.searched_paths = searched_paths or []
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format error message with search details."""
        msg = f"Model '{self.model_name}' not found."
        if self.searched_paths:
            paths_str = "\n  ".join(str(p) for p in self.searched_paths[:5])
            msg += f"\nSearched in:\n  {paths_str}"
            if len(self.searched_paths) > 5:
                msg += f"\n  ... and {len(self.searched_paths) - 5} more locations"
        return msg


class SpiceModelLoader:
    """Load SPICE models from KiCad-Spice-Library."""
    
    def __init__(self, library_path: Optional[Path] = None):
        """Initialize the SPICE model loader.
        
        Args:
            library_path: Path to KiCad-Spice-Library. If None, uses default.
        """
        if library_path is None:
            # Default path relative to project root
            project_root = Path(__file__).parent.parent.parent
            library_path = project_root / "submodules" / "KiCad-Spice-Library"
        
        self.library_path = library_path
        self.models_path = library_path / "Models" if library_path.exists() else None
        self.model_cache: Dict[str, str] = {}
        
        # Priority order for searching
        self.search_priority = [
            "Manufacturer",
            "Operational Amplifier", 
            "Transistor",
            "Diode",
            "Digital Logic",
            "uncategorized/spice_complete",
            "uncategorized"
        ]
    
    def load_transistor(self, model_name: str) -> str:
        """Load a transistor model.
        
        Args:
            model_name: Transistor model name (e.g., '2N3904', 'BC547')
            
        Returns:
            SPICE model definition string
            
        Raises:
            ModelNotFoundError: If model cannot be found
        """
        # Check cache first
        cache_key = f"transistor_{model_name}"
        if cache_key in self.model_cache:
            return self.model_cache[cache_key]
        
        # Search for model files
        search_paths = [
            self.models_path / "Transistor",
            self.models_path / "Manufacturer",
            self.models_path / "uncategorized"
        ]
        
        model = self._search_and_load(model_name, search_paths)
        if model:
            self.model_cache[cache_key] = model
            return model
        
        raise ModelNotFoundError(model_name, search_paths)
    
    def load_opamp(self, model_name: str) -> str:
        """Load an operational amplifier model.
        
        Args:
            model_name: Op-amp model name (e.g., 'LM358', 'TL072')
            
        Returns:
            SPICE model definition string
            
        Raises:
            ModelNotFoundError: If model cannot be found
        """
        # Check cache first
        cache_key = f"opamp_{model_name}"
        if cache_key in self.model_cache:
            return self.model_cache[cache_key]
        
        # Search for model files
        search_paths = [
            self.models_path / "Operational Amplifier",
            self.models_path / "Manufacturer" / "Texas Instruments",
            self.models_path / "Manufacturer",
            self.models_path / "uncategorized"
        ]
        
        model = self._search_and_load(model_name, search_paths)
        if model:
            self.model_cache[cache_key] = model
            return model
        
        raise ModelNotFoundError(model_name, search_paths)
    
    def load_diode(self, model_name: str) -> str:
        """Load a diode model.
        
        Args:
            model_name: Diode model name (e.g., '1N4148', '1N4007')
            
        Returns:
            SPICE model definition string
            
        Raises:
            ModelNotFoundError: If model cannot be found
        """
        # Check cache first
        cache_key = f"diode_{model_name}"
        if cache_key in self.model_cache:
            return self.model_cache[cache_key]
        
        # Search for model files
        search_paths = [
            self.models_path / "Diode",
            self.models_path / "Manufacturer",
            self.models_path / "uncategorized"
        ]
        
        model = self._search_and_load(model_name, search_paths)
        if model:
            self.model_cache[cache_key] = model
            return model
        
        raise ModelNotFoundError(model_name, search_paths)
    
    def load_555_timer(self) -> str:
        """Load NE555 timer model.
        
        Returns:
            SPICE model definition string
            
        Raises:
            ModelNotFoundError: If model cannot be found
        """
        # Check cache first
        cache_key = "555_timer"
        if cache_key in self.model_cache:
            return self.model_cache[cache_key]
        
        # Known location for 555 timer
        timer_paths = [
            self.models_path / "uncategorized" / "spice_complete" / "SGS555.LIB",
            self.models_path / "Manufacturer",
        ]
        
        for path in timer_paths:
            if path.exists():
                if path.is_file():
                    model = path.read_text()
                    self.model_cache[cache_key] = model
                    return model
                else:
                    # Search in directory
                    model = self._search_and_load("555", [path])
                    if model:
                        self.model_cache[cache_key] = model
                        return model
        
        raise ModelNotFoundError("555 Timer", timer_paths)
    
    def load_passive(self, component_type: str, value: float) -> str:
        """Load a passive component model (R, L, C).
        
        Args:
            component_type: 'R', 'L', or 'C'
            value: Component value (ohms, henries, or farads)
            
        Returns:
            SPICE component definition string
        """
        if component_type == "R":
            # Format resistor value
            return self._format_resistor(value)
        elif component_type == "C":
            # Format capacitor value
            return self._format_capacitor(value)
        elif component_type == "L":
            # Format inductor value
            return self._format_inductor(value)
        else:
            raise ValueError(f"Unknown component type: {component_type}")
    
    def get_available_models(self, category: str) -> List[str]:
        """Get list of available models in a category.
        
        Args:
            category: Model category ('opamp', 'transistor', 'diode')
            
        Returns:
            List of available model names
        """
        models = []
        
        if category.lower() == "opamp":
            search_dirs = [
                self.models_path / "Operational Amplifier",
                self.models_path / "Manufacturer" / "Texas Instruments"
            ]
        elif category.lower() == "transistor":
            search_dirs = [
                self.models_path / "Transistor",
                self.models_path / "Manufacturer" / "TRT-Electronics"
            ]
        elif category.lower() == "diode":
            search_dirs = [self.models_path / "Diode"]
        else:
            return models
        
        for dir_path in search_dirs:
            if dir_path and dir_path.exists():
                for file_path in dir_path.glob("*.lib"):
                    # Extract model names from filename
                    model_name = file_path.stem.upper()
                    if model_name not in models:
                        models.append(model_name)
                for file_path in dir_path.glob("*.mod"):
                    model_name = file_path.stem.upper()
                    if model_name not in models:
                        models.append(model_name)
        
        return sorted(models)
    
    def _find_model_files(self, model_name: str, prioritize: bool = True) -> List[Path]:
        """Find all files that might contain the model.
        
        Args:
            model_name: Name of the model to find
            prioritize: Whether to sort by priority
            
        Returns:
            List of file paths that might contain the model
        """
        if not self.models_path or not self.models_path.exists():
            return []
        
        results = []
        search_pattern = model_name.lower()
        
        # Search for files matching the model name
        for ext in ["*.lib", "*.mod", "*.cir", "*.LIB", "*.MOD"]:
            for file_path in self.models_path.rglob(ext):
                if search_pattern in file_path.stem.lower():
                    results.append(file_path)
                # Also check file content for model definition
                elif file_path.stat().st_size < 1_000_000:  # Only check files < 1MB
                    try:
                        content = file_path.read_text(errors='ignore').lower()
                        if f".model {search_pattern}" in content or f".subckt {search_pattern}" in content:
                            results.append(file_path)
                    except:
                        pass
        
        if prioritize:
            # Sort by priority (manufacturer first, etc.)
            def priority_key(path: Path) -> int:
                path_str = str(path).lower()
                for i, priority_dir in enumerate(self.search_priority):
                    if priority_dir.lower() in path_str:
                        return i
                return len(self.search_priority)
            
            results.sort(key=priority_key)
        
        return results
    
    def _search_and_load(self, model_name: str, search_paths: List[Path]) -> Optional[str]:
        """Search for and load a model from given paths.
        
        Args:
            model_name: Name of the model
            search_paths: Paths to search
            
        Returns:
            Model string if found, None otherwise
        """
        for base_path in search_paths:
            if not base_path or not base_path.exists():
                continue
            
            # Try direct file match with various case combinations
            name_variations = [
                model_name,
                model_name.lower(),
                model_name.upper(),
                model_name.replace("N", "n"),  # Handle 2N3904 -> 2n3904
            ]
            
            for name_var in name_variations:
                for ext in [".lib", ".mod", ".LIB", ".MOD"]:
                    file_path = base_path / f"{name_var}{ext}"
                    if file_path.exists():
                        content = file_path.read_text(errors='ignore')
                        # Return the whole file for single-model files
                        if content.count(".model") == 1 or content.count(".subckt") == 1:
                            return content
                        # Extract specific model from multi-model files
                        model = self._extract_model(content, model_name)
                        if model:
                            return model
            
            # Search in subdirectories
            if base_path.is_dir():
                for ext in ["*.lib", "*.mod", "*.LIB", "*.MOD"]:
                    for file_path in base_path.rglob(ext):
                        # Check filename first
                        if model_name.lower() in file_path.stem.lower():
                            content = file_path.read_text(errors='ignore')
                            # For exact filename matches, return whole content if it's a single model
                            if file_path.stem.lower() == model_name.lower():
                                if content.count(".model") <= 2 and content.count(".subckt") <= 2:
                                    return content
                            # Otherwise extract specific model
                            model = self._extract_model(content, model_name)
                            if model:
                                return model
                        
                        # Check content for models (only for smaller files)
                        elif file_path.stat().st_size < 500_000:
                            try:
                                content = file_path.read_text(errors='ignore')
                                model = self._extract_model(content, model_name)
                                if model:
                                    return model
                            except:
                                pass
        
        return None
    
    def _extract_model(self, lib_content: str, model_name: str) -> Optional[str]:
        """Extract specific model from library file content.
        
        Args:
            lib_content: Library file content
            model_name: Model to extract
            
        Returns:
            Extracted model string or None
        """
        lines = lib_content.split('\n')
        model_lines = []
        in_model = False
        in_subckt = False
        
        # Try various case combinations for the model name
        model_names = [model_name, model_name.lower(), model_name.upper()]
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if this is the start of our model
            if not in_model:
                for name in model_names:
                    if f".model {name.lower()}" in line_lower or f".subckt {name.lower()}" in line_lower:
                        in_model = True
                        if ".subckt" in line_lower:
                            in_subckt = True
                        model_lines.append(line)
                        break
            # If we're in a model, collect lines
            elif in_model:
                # Check for end of subcircuit
                if in_subckt and line_lower.strip().startswith('.ends'):
                    model_lines.append(line)
                    break
                # Check for start of next model/subckt (end of current model)
                elif line_lower.strip().startswith('.model') or line_lower.strip().startswith('.subckt'):
                    break
                # Add line to current model
                else:
                    model_lines.append(line)
        
        if model_lines:
            return '\n'.join(model_lines)
        return None
    
    def _format_resistor(self, value: float) -> str:
        """Format resistor value for SPICE."""
        if value >= 1e6:
            return f"R value={value/1e6:.0f}Meg"
        elif value >= 1e3:
            return f"R value=1k" if value == 1000 else f"R value={value/1e3:.1f}k"
        else:
            return f"R value={value:.0f}"
    
    def _format_capacitor(self, value: float) -> str:
        """Format capacitor value for SPICE."""
        if value >= 1e-6:
            return f"C value=1u" if value == 1e-6 else f"C value={value*1e6:.1f}u"
        elif value >= 1e-9:
            return f"C value={value*1e9:.1f}n"
        else:
            return f"C value={value*1e12:.1f}p"
    
    def _format_inductor(self, value: float) -> str:
        """Format inductor value for SPICE."""
        if value >= 1e-3:
            return f"L value=1m" if value == 1e-3 else f"L value={value*1e3:.1f}m"
        elif value >= 1e-6:
            return f"L value={value*1e6:.1f}u"
        else:
            return f"L value={value*1e9:.1f}n"