"""
WebSocket routes for real-time simulation updates.

Provides WebSocket endpoints for live simulation progress monitoring
and client-server communication.
"""

import json
import logging
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.api.routes.circuits import circuit_service
from src.api.services.simulation_service import SimulationService

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)

# Global simulation service instance
simulation_service = SimulationService(circuit_service)


# Connection manager for WebSocket clients
class ConnectionManager:
    """Manages WebSocket connections for simulation updates."""

    def __init__(self):
        # Map job_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        """Accept WebSocket connection and add to job group."""
        await websocket.accept()

        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()

        self.active_connections[job_id].add(websocket)
        logger.info(
            f"WebSocket connected for job {job_id}. Total connections: {len(self.active_connections[job_id])}"
        )

        # Send initial connection message
        await self.send_personal_message(
            {
                "type": "connection",
                "job_id": job_id,
                "message": "Connected to simulation updates",
                "timestamp": self._get_timestamp(),
            },
            websocket,
        )

    def disconnect(self, websocket: WebSocket, job_id: str):
        """Remove WebSocket connection from job group."""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)

            # Clean up empty job groups
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

        logger.info(f"WebSocket disconnected for job {job_id}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")

    async def broadcast_to_job(self, message: dict, job_id: str):
        """Broadcast message to all WebSocket connections for a job."""
        if job_id not in self.active_connections:
            return

        # Create copy of connections to avoid modification during iteration
        connections = self.active_connections[job_id].copy()

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to WebSocket: {e}")
                # Remove failed connection
                self.active_connections[job_id].discard(connection)

    async def send_progress_update(
        self, job_id: str, progress: float, message: str, status: str = "running"
    ):
        """Send progress update to all clients watching a job."""
        update_message = {
            "type": "progress",
            "job_id": job_id,
            "data": {"progress": progress, "message": message, "status": status},
            "timestamp": self._get_timestamp(),
        }

        await self.broadcast_to_job(update_message, job_id)

    async def send_result_notification(self, job_id: str, status: str, results: dict = None):
        """Send simulation completion notification."""
        result_message = {
            "type": "result",
            "job_id": job_id,
            "data": {
                "status": status,
                "results_available": results is not None,
                "message": f"Simulation {status}",
            },
            "timestamp": self._get_timestamp(),
        }

        await self.broadcast_to_job(result_message, job_id)

    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        from datetime import datetime

        return datetime.now().isoformat()


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/simulation/{job_id}")
async def websocket_simulation_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time simulation updates.

    Args:
        websocket: WebSocket connection
        job_id: Simulation job identifier
    """
    await manager.connect(websocket, job_id)

    try:
        while True:
            # Listen for client messages
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_client_message(websocket, job_id, message)
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": manager._get_timestamp(),
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
        logger.info(f"WebSocket client disconnected from job {job_id}")


async def handle_client_message(websocket: WebSocket, job_id: str, message: dict):
    """
    Handle messages received from WebSocket clients.

    Args:
        websocket: WebSocket connection
        job_id: Simulation job identifier
        message: Message from client
    """
    message_type = message.get("type", "")

    if message_type == "command":
        action = message.get("action", "")

        if action == "cancel":
            # Cancel the simulation
            cancelled = simulation_service.cancel_simulation(job_id)

            if cancelled:
                # Send acknowledgment
                await manager.send_personal_message(
                    {
                        "type": "command_ack",
                        "action": "cancel",
                        "message": "Simulation cancellation requested",
                        "timestamp": manager._get_timestamp(),
                    },
                    websocket,
                )

                # Broadcast cancellation to all clients watching this job
                await manager.send_result_notification(job_id, "cancelled")
            else:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Failed to cancel simulation (job not found or already completed)",
                        "timestamp": manager._get_timestamp(),
                    },
                    websocket,
                )

        elif action == "status":
            # Send current simulation status
            status = simulation_service.get_simulation_status(job_id)

            if status:
                await manager.send_personal_message(
                    {
                        "type": "status_update",
                        "job_id": job_id,
                        "data": {
                            "status": status.status,
                            "progress": status.progress,
                            "message": status.message or "Simulation in progress",
                        },
                        "timestamp": manager._get_timestamp(),
                    },
                    websocket,
                )
            else:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Simulation job not found",
                        "timestamp": manager._get_timestamp(),
                    },
                    websocket,
                )
        else:
            await manager.send_personal_message(
                {
                    "type": "error",
                    "message": f"Unknown command action: {action}",
                    "timestamp": manager._get_timestamp(),
                },
                websocket,
            )

    elif message_type == "ping":
        # Respond to ping with pong
        await manager.send_personal_message(
            {
                "type": "pong",
                "message": "WebSocket connection active",
                "timestamp": manager._get_timestamp(),
            },
            websocket,
        )

    else:
        await manager.send_personal_message(
            {
                "type": "error",
                "message": f"Unknown message type: {message_type}",
                "timestamp": manager._get_timestamp(),
            },
            websocket,
        )


# Export connection manager for use by simulation service
def get_websocket_manager() -> ConnectionManager:
    """Get the global WebSocket connection manager."""
    return manager
