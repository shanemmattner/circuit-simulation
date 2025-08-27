"""
Job service for managing background simulation tasks.

Provides abstraction over Celery for job execution with fallback to direct execution.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class JobService:
    """Service for managing background jobs."""

    def __init__(self):
        """Initialize job service."""
        self.use_celery = self._check_celery_available()
        if self.use_celery:
            try:
                from ..workers.tasks import run_simulation
                self.run_simulation_task = run_simulation
                logger.info("Celery backend enabled for job processing")
            except ImportError:
                self.use_celery = False
                logger.warning("Celery import failed, falling back to direct execution")
        else:
            logger.info("Celery not available, using direct execution")

    def _check_celery_available(self) -> bool:
        """
        Check if Celery and Redis are available.
        
        Returns:
            True if Celery can be used, False otherwise
        """
        try:
            import redis
            import celery
            
            # Check if Redis is accessible
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            r = redis.from_url(redis_url)
            r.ping()  # This will raise an exception if Redis is not available
            
            return True
        except Exception as e:
            logger.info(f"Celery/Redis not available: {e}")
            return False

    def submit_simulation_job(
        self, 
        job_id: str,
        circuit_id: str, 
        sim_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit a simulation job for background processing.
        
        Args:
            job_id: Job identifier
            circuit_id: Circuit to simulate
            sim_type: Type of simulation
            parameters: Simulation parameters
            
        Returns:
            Job submission result
        """
        if self.use_celery:
            return self._submit_celery_job(job_id, circuit_id, sim_type, parameters)
        else:
            return self._submit_direct_job(job_id, circuit_id, sim_type, parameters)

    def _submit_celery_job(
        self,
        job_id: str,
        circuit_id: str,
        sim_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit job to Celery queue."""
        try:
            # Submit task to Celery
            task = self.run_simulation_task.apply_async(
                args=[job_id, circuit_id, sim_type, parameters],
                task_id=job_id
            )
            
            return {
                "job_id": job_id,
                "task_id": task.id,
                "status": "queued",
                "backend": "celery",
                "submitted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to submit Celery job {job_id}: {e}")
            # Fallback to direct execution
            return self._submit_direct_job(job_id, circuit_id, sim_type, parameters)

    def _submit_direct_job(
        self,
        job_id: str,
        circuit_id: str,
        sim_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute job directly (fallback when Celery unavailable)."""
        logger.info(f"Executing job {job_id} directly (no queue)")
        
        return {
            "job_id": job_id,
            "task_id": job_id,
            "status": "pending",
            "backend": "direct",
            "submitted_at": datetime.now().isoformat()
        }

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status from Celery if available.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status dictionary or None if not found
        """
        if not self.use_celery:
            return None
            
        try:
            from ..workers.celery_app import celery_app
            
            # Get task result
            result = celery_app.AsyncResult(job_id)
            
            if result.state == "PENDING":
                return {
                    "job_id": job_id,
                    "status": "pending",
                    "progress": 0,
                    "message": "Job queued"
                }
            elif result.state == "PROGRESS":
                return {
                    "job_id": job_id,
                    "status": "running",
                    "progress": result.info.get("progress", 0),
                    "message": result.info.get("message", "Running simulation")
                }
            elif result.state == "SUCCESS":
                return {
                    "job_id": job_id,
                    "status": "completed",
                    "progress": 100,
                    "message": "Simulation completed",
                    "results": result.result
                }
            elif result.state == "FAILURE":
                return {
                    "job_id": job_id,
                    "status": "failed",
                    "progress": 0,
                    "message": f"Simulation failed: {str(result.info)}",
                    "error": str(result.info)
                }
            else:
                return {
                    "job_id": job_id,
                    "status": result.state.lower(),
                    "progress": 0,
                    "message": f"Job in state: {result.state}"
                }
                
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {e}")
            return None

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a background job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        if not self.use_celery:
            return False
            
        try:
            from ..workers.celery_app import celery_app
            
            # Revoke the task
            celery_app.control.revoke(job_id, terminate=True)
            
            logger.info(f"Cancelled job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False