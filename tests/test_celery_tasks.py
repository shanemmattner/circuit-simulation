"""
Tests for Celery background tasks.

Tests task creation, configuration, and basic functionality.
"""

import pytest
from unittest.mock import Mock, patch
from src.api.workers.celery_app import celery_app
from src.api.workers.tasks import run_simulation, cleanup_old_results


class TestCeleryConfiguration:
    """Test Celery app configuration."""

    def test_celery_app_created(self):
        """Test that Celery app is properly configured."""
        assert celery_app.main == "circuit_simulation"
        assert "src.api.workers.tasks" in celery_app.conf.include
        
    def test_celery_settings(self):
        """Test Celery configuration settings."""
        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.result_serializer == "json"
        assert celery_app.conf.timezone == "UTC"
        assert celery_app.conf.enable_utc == True

    def test_task_routing(self):
        """Test task routing configuration."""
        routes = celery_app.conf.task_routes
        assert "src.api.workers.tasks.run_simulation" in routes
        assert routes["src.api.workers.tasks.run_simulation"]["queue"] == "simulations"


class TestSimulationTask:
    """Test simulation background task."""

    @patch('src.api.workers.tasks.CircuitService')
    @patch('src.api.workers.tasks.SimulationEngine')
    def test_run_simulation_task_structure(self, mock_engine, mock_circuit_service):
        """Test simulation task is properly defined."""
        # Verify task is registered
        assert "src.api.workers.tasks.run_simulation" in celery_app.tasks
        
        # Verify task function exists and is callable
        task_func = run_simulation
        assert callable(task_func)
        
        # Verify task has correct name
        assert task_func.name == "src.api.workers.tasks.run_simulation"

    def test_cleanup_task_structure(self):
        """Test cleanup task is properly defined."""
        # Verify task is registered
        assert "src.api.workers.tasks.cleanup_old_results" in celery_app.tasks
        
        # Verify task function exists
        task_func = cleanup_old_results
        assert callable(task_func)

    @patch('src.api.workers.tasks.CircuitService')
    @patch('src.api.workers.tasks.SimulationEngine')
    def test_simulation_task_parameters(self, mock_engine, mock_circuit_service):
        """Test simulation task parameter validation."""
        # Skip this test if Redis is not available
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
        except:
            pytest.skip("Redis not available for Celery testing")
        
        # Mock circuit service
        mock_circuit_service.return_value.get_circuit_object.return_value = None
        
        # Test that task raises error for missing circuit
        with pytest.raises(ValueError, match="not found"):
            run_simulation.apply(args=[
                "test-job-123",
                "invalid-circuit-id", 
                "dc",
                {}
            ]).get()

    def test_cleanup_task_execution(self):
        """Test cleanup task can execute."""
        # This should run without errors
        result = cleanup_old_results.apply().get()
        assert result == "Cleanup completed"


class TestCeleryIntegration:
    """Test Celery integration aspects."""

    def test_task_discovery(self):
        """Test that tasks are properly discovered."""
        task_names = list(celery_app.tasks.keys())
        
        # Check expected tasks are registered
        expected_tasks = [
            "src.api.workers.tasks.run_simulation",
            "src.api.workers.tasks.cleanup_old_results"
        ]
        
        for task_name in expected_tasks:
            assert task_name in task_names

    def test_redis_url_configuration(self):
        """Test Redis URL is properly configured."""
        # Should default to localhost if no env var
        assert "redis://" in celery_app.conf.broker_url
        assert "redis://" in celery_app.conf.result_backend