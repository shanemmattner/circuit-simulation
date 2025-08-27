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
                # Handle both list format (tests) and dict format (real API)
                if isinstance(data, list):
                    circuits = data
                else:
                    circuits = data.get('circuits', [])
                logger.info(f"Successfully loaded {len(circuits)} circuits")
                return circuits
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
        url = f"{self.base_url}/api/circuits/{circuit_id}"
        log_api_request(logger, "GET", url)
        
        try:
            response = requests.get(url, timeout=5)
            log_api_request(logger, "GET", url, response.status_code)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Circuit not found: {circuit_id}")
                return None
        except requests.exceptions.RequestException as e:
            log_api_request(logger, "GET", url, error=str(e))
            return None
            
    def start_simulation(self, circuit_id: str, simulation_type: str, parameters: dict = None) -> Optional[Dict[str, Any]]:
        """Start a simulation for the specified circuit.
        
        Args:
            circuit_id: ID of the circuit to simulate
            simulation_type: Type of simulation (dc, ac, transient)
            parameters: Simulation parameters (default: empty dict)
            
        Returns:
            Simulation job status or None if failed
        """
        if parameters is None:
            parameters = {}
            
        url = f"{self.base_url}/api/circuits/{circuit_id}/simulate"
        payload = {
            "type": simulation_type,
            "parameters": parameters
        }
        
        log_api_request(logger, "POST", url)
        logger.info(f"Starting {simulation_type} simulation with parameters: {parameters}")
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            log_api_request(logger, "POST", url, response.status_code)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Simulation started - Job ID: {result.get('job_id')}")
                return result
            else:
                logger.error(f"Simulation failed: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            log_api_request(logger, "POST", url, error=str(e))
            return None
            
    def get_simulation_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get results for a completed simulation.
        
        Args:
            job_id: ID of the simulation job
            
        Returns:
            Simulation results or None if not found
        """
        url = f"{self.base_url}/api/simulations/{job_id}/results"
        log_api_request(logger, "GET", url)
        
        try:
            response = requests.get(url, timeout=5)
            log_api_request(logger, "GET", url, response.status_code)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Results not found for job: {job_id}")
                return None
        except requests.exceptions.RequestException as e:
            log_api_request(logger, "GET", url, error=str(e))
            return None