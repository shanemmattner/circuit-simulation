"""API client for connecting GUI to circuit simulation backend."""

import requests
from typing import List, Dict, Any, Optional
import logging

try:
    from src.gui.utils.logging_config import log_api_request
except ImportError:
    # For direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.gui.utils.logging_config import log_api_request

logger = logging.getLogger('gui.api_client')


class CircuitAPIClient:
    """Client for interacting with circuit simulation REST API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize API client.
        
        Args:
            base_url: Base URL for the API server
        """
        self.base_url = base_url.rstrip('/')
        
    def get_circuits(self) -> List[Dict[str, Any]]:
        """Get list of all available circuits.
        
        Returns:
            List of circuit dictionaries with id, name, etc.
        """
        url = f"{self.base_url}/api/circuits"
        log_api_request(logger, "GET", url)
        
        try:
            response = requests.get(url, timeout=5)
            log_api_request(logger, "GET", url, response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully loaded {len(data.get('circuits', []))} circuits")
                return data.get('circuits', [])
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            log_api_request(logger, "GET", url, error=str(e))
            return []
            
    def get_circuit_options(self) -> List[Dict[str, str]]:
        """Get circuit list formatted for Dash dropdown.
        
        Returns:
            List of options with 'label' and 'value' keys for dropdown
        """
        circuits = self.get_circuits()
        return [
            {"label": circuit["name"], "value": circuit["id"]}
            for circuit in circuits
        ]
        
    def get_circuit_details(self, circuit_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific circuit.
        
        Args:
            circuit_id: ID of the circuit to fetch
            
        Returns:
            Circuit details dictionary or None if not found
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/circuits/{circuit_id}", 
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Circuit not found: {circuit_id}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch circuit {circuit_id}: {e}")
            return None