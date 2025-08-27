"""
Celery tasks for background simulation processing.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from ...circuit_sim.simulator.engine import SimulationEngine
from ..services.circuit_service import CircuitService
from .celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def run_simulation(
    self, job_id: str, circuit_id: str, sim_type: str, parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Background task to run circuit simulation.

    Args:
        job_id: Simulation job identifier
        circuit_id: Circuit to simulate
        sim_type: Type of simulation (dc, transient, ac)
        parameters: Simulation parameters

    Returns:
        Simulation results dictionary
    """
    try:
        logger.info(f"Starting simulation task {job_id} for circuit {circuit_id}")

        # Update task progress
        self.update_state(
            state="PROGRESS",
            meta={"progress": 10, "message": "Initializing simulation...", "job_id": job_id},
        )

        # Get circuit (would normally be from database)
        # For MVP, we'll need to pass circuit data directly
        circuit_service = CircuitService()
        circuit = circuit_service.get_circuit_object(circuit_id)

        if not circuit:
            raise ValueError(f"Circuit {circuit_id} not found")

        # Create simulation engine
        engine = SimulationEngine()

        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={"progress": 30, "message": f"Running {sim_type} analysis...", "job_id": job_id},
        )

        # Run simulation based on type
        if sim_type == "dc":
            results = engine.simulate_dc(circuit)
            message = "DC analysis complete"
        elif sim_type == "transient":
            stop_time = parameters.get("stop_time", 0.001)
            step_time = parameters.get("step_time")
            results = engine.simulate_transient(circuit, stop_time, step_time)
            message = "Transient analysis complete"
        else:
            raise ValueError(f"Unsupported simulation type: {sim_type}")

        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={"progress": 90, "message": "Processing results...", "job_id": job_id},
        )

        # Format results for JSON serialization
        simulation_results = {
            "voltages": results.voltages,
            "currents": results.currents,
            "time": results.time.tolist() if results.time is not None else None,
            "metadata": results.metadata,
            "job_id": job_id,
            "completed_at": datetime.now().isoformat(),
            "message": message,
        }

        logger.info(f"Simulation task {job_id} completed successfully")
        return simulation_results

    except Exception as e:
        logger.error(f"Simulation task {job_id} failed: {str(e)}")

        # Update task with failure
        self.update_state(
            state="FAILURE",
            meta={
                "progress": 0,
                "message": f"Simulation failed: {str(e)}",
                "job_id": job_id,
                "error": str(e),
            },
        )
        raise


@celery_app.task
def cleanup_old_results():
    """
    Periodic task to clean up old simulation results.
    """
    logger.info("Running cleanup of old simulation results")
    # In production, this would clean up database records and files
    # For MVP, results are stored in memory so no cleanup needed
    return "Cleanup completed"
