"""
Simulation service for managing simulation jobs.

Handles job creation, status tracking, execution, and result storage.
"""

import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.api.models.simulation import SimulationRequest, SimulationStatus, SimulationType
from src.api.services.circuit_service import CircuitService
from src.circuit_sim.simulator.engine import SimulationEngine


class SimulationService:
    """Service for managing simulation jobs."""

    def __init__(self, circuit_service: CircuitService):
        """Initialize simulation service."""
        self.circuit_service = circuit_service
        self.engine = SimulationEngine()
        self._jobs: Dict[str, dict] = {}

    def start_simulation(
        self, 
        circuit_id: str, 
        sim_request: SimulationRequest
    ) -> SimulationStatus:
        """
        Start a new simulation job.
        
        Args:
            circuit_id: Circuit to simulate
            sim_request: Simulation parameters
            
        Returns:
            SimulationStatus with job details
            
        Raises:
            ValueError: If circuit not found
        """
        # Verify circuit exists
        circuit = self.circuit_service.get_circuit_object(circuit_id)
        if not circuit:
            raise ValueError("Circuit not found")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create job record
        now = datetime.now()
        job_record = {
            "job_id": job_id,
            "circuit_id": circuit_id,
            "type": sim_request.type,
            "parameters": sim_request.parameters,
            "priority": sim_request.priority,
            "status": "pending",
            "progress": 0.0,
            "eta_seconds": None,
            "message": "Simulation queued",
            "created_at": now,
            "started_at": None,
            "completed_at": None,
            "results": None,
            "error": None
        }
        
        self._jobs[job_id] = job_record
        
        # For MVP, run simulation immediately (no queue)
        # In production, this would be queued for background processing
        self._execute_simulation(job_id)
        
        return SimulationStatus(**job_record)

    def get_simulation_status(self, job_id: str) -> Optional[SimulationStatus]:
        """
        Get simulation job status.
        
        Args:
            job_id: Job identifier
            
        Returns:
            SimulationStatus if found, None otherwise
        """
        job_record = self._jobs.get(job_id)
        if not job_record:
            return None
            
        return SimulationStatus(**job_record)

    def cancel_simulation(self, job_id: str) -> bool:
        """
        Cancel a simulation job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancelled, False if not found
        """
        job_record = self._jobs.get(job_id)
        if not job_record:
            return False
        
        if job_record["status"] in ["pending", "running"]:
            job_record["status"] = "cancelled"
            job_record["message"] = "Simulation cancelled by user"
            job_record["completed_at"] = datetime.now()
        
        return True

    def list_simulations(self, skip: int = 0, limit: int = 100) -> Dict:
        """
        List all simulation jobs with pagination.
        
        Args:
            skip: Number of jobs to skip
            limit: Maximum number of jobs to return
            
        Returns:
            Dictionary with simulations list and total count
        """
        jobs = list(self._jobs.values())
        total = len(jobs)
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        paginated_jobs = jobs[skip:skip + limit]
        
        # Convert to response format
        simulation_statuses = [SimulationStatus(**job) for job in paginated_jobs]
        
        return {
            "simulations": simulation_statuses,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    def get_simulation_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get simulation results.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Results dictionary if available, None otherwise
        """
        job_record = self._jobs.get(job_id)
        if not job_record or job_record["status"] != "completed":
            return None
            
        return job_record.get("results")

    def execute_pending_simulation(self, job_id: str) -> bool:
        """
        Execute a pending simulation (for testing).
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if executed, False if not found or not pending
        """
        job_record = self._jobs.get(job_id)
        if not job_record or job_record["status"] != "pending":
            return False
            
        self._execute_simulation(job_id)
        return True

    def _execute_simulation(self, job_id: str) -> None:
        """
        Execute simulation job with WebSocket progress updates.
        
        Args:
            job_id: Job identifier
        """
        job_record = self._jobs[job_id]
        
        try:
            # Update status to running
            job_record["status"] = "running"
            job_record["started_at"] = datetime.now()
            job_record["message"] = "Simulation in progress"
            job_record["progress"] = 10.0
            
            # Send WebSocket update for simulation start
            self._send_websocket_update(job_id, 10.0, "Initializing simulation...")
            
            # Get circuit
            circuit = self.circuit_service.get_circuit_object(job_record["circuit_id"])
            
            # Update progress
            job_record["progress"] = 30.0
            self._send_websocket_update(job_id, 30.0, "Building circuit model...")
            
            # Run simulation based on type
            if job_record["type"] == SimulationType.DC:
                job_record["progress"] = 60.0
                self._send_websocket_update(job_id, 60.0, "Running DC analysis...")
                
                results = self.engine.simulate_dc(circuit)
                job_record["message"] = "DC analysis complete"
                
            elif job_record["type"] == SimulationType.TRANSIENT:
                job_record["progress"] = 60.0
                self._send_websocket_update(job_id, 60.0, "Running transient analysis...")
                
                params = job_record["parameters"]
                stop_time = params.get("stop_time", 0.001)
                step_time = params.get("step_time")
                results = self.engine.simulate_transient(circuit, stop_time, step_time)
                job_record["message"] = "Transient analysis complete"
                
            else:
                raise ValueError(f"Unsupported simulation type: {job_record['type']}")
            
            # Update progress
            job_record["progress"] = 90.0
            self._send_websocket_update(job_id, 90.0, "Processing results...")
            
            # Store results
            job_record["results"] = {
                "voltages": results.voltages,
                "currents": results.currents,
                "time": results.time.tolist() if results.time is not None else None,
                "metadata": results.metadata
            }
            
            # Complete simulation
            job_record["status"] = "completed"
            job_record["progress"] = 100.0
            job_record["completed_at"] = datetime.now()
            
            # Send completion WebSocket update
            self._send_websocket_completion(job_id, "completed", job_record["results"])
            
        except Exception as e:
            # Handle simulation errors
            job_record["status"] = "failed"
            job_record["error"] = str(e)
            job_record["message"] = f"Simulation failed: {str(e)}"
            job_record["completed_at"] = datetime.now()
            
            # Send failure WebSocket update
            self._send_websocket_completion(job_id, "failed")

    def _send_websocket_update(self, job_id: str, progress: float, message: str):
        """
        Send WebSocket progress update (if WebSocket manager available).
        
        Args:
            job_id: Job identifier
            progress: Progress percentage (0-100)
            message: Progress message
        """
        try:
            # Import here to avoid circular imports
            from ..routes.websocket import get_websocket_manager
            
            manager = get_websocket_manager()
            
            # Schedule WebSocket update (async)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(manager.send_progress_update(job_id, progress, message))
            except RuntimeError:
                # No event loop running, skip WebSocket update
                pass
                
        except ImportError:
            # WebSocket manager not available, skip update
            pass

    def _send_websocket_completion(self, job_id: str, status: str, results: Optional[Dict] = None):
        """
        Send WebSocket completion notification.
        
        Args:
            job_id: Job identifier
            status: Final status (completed, failed, cancelled)
            results: Simulation results if available
        """
        try:
            # Import here to avoid circular imports
            from ..routes.websocket import get_websocket_manager
            
            manager = get_websocket_manager()
            
            # Schedule WebSocket notification (async)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(manager.send_result_notification(job_id, status, results))
            except RuntimeError:
                # No event loop running, skip WebSocket update
                pass
                
        except ImportError:
            # WebSocket manager not available, skip notification
            pass