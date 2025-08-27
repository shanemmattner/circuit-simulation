"""
Tests for job service functionality.

Tests job submission, status tracking, and fallback behavior.
"""

from unittest.mock import MagicMock, patch

from src.api.services.job_service import JobService


class TestJobService:
    """Test job service functionality."""

    def test_job_service_initialization(self):
        """Test job service initializes correctly."""
        job_service = JobService()

        # Should initialize without errors
        assert job_service is not None
        assert hasattr(job_service, "use_celery")

    def test_celery_availability_check(self):
        """Test Celery availability detection."""
        # Mock Redis connection to fail
        with patch("redis.from_url") as mock_from_url:
            mock_redis = MagicMock()
            mock_redis.ping.side_effect = Exception("Connection failed") 
            mock_from_url.return_value = mock_redis
            
            job_service = JobService()

            # Without Redis connection, should default to direct execution
            assert job_service.use_celery == False

    def test_submit_direct_job(self):
        """Test direct job submission (fallback mode)."""
        job_service = JobService()

        # Force direct mode
        job_service.use_celery = False

        result = job_service.submit_simulation_job(
            job_id="test-123",
            circuit_id="circuit-456",
            sim_type="dc",
            parameters={"analysis": "operating_point"},
        )

        assert result["job_id"] == "test-123"
        assert result["status"] == "pending"
        assert result["backend"] == "direct"
        assert "submitted_at" in result

    def test_job_service_with_mock_celery(self):
        """Test job service behavior with mocked Celery."""
        # Mock Redis connection to fail
        with patch("redis.from_url") as mock_from_url:
            mock_redis = MagicMock()
            mock_redis.ping.side_effect = Exception("Connection failed") 
            mock_from_url.return_value = mock_redis
            
            # Test that job service can be created and defaults to direct mode
            job_service = JobService()

            # Without proper Redis/Celery setup, should use direct mode
            assert job_service.use_celery == False

    def test_get_job_status_without_celery(self):
        """Test job status retrieval when Celery unavailable."""
        job_service = JobService()
        job_service.use_celery = False

        # Should return None when Celery not available
        status = job_service.get_job_status("test-job-123")
        assert status is None

    def test_cancel_job_without_celery(self):
        """Test job cancellation when Celery unavailable."""
        job_service = JobService()
        job_service.use_celery = False

        # Should return False when Celery not available
        cancelled = job_service.cancel_job("test-job-123")
        assert cancelled == False

    def test_job_service_redis_connection_error(self):
        """Test job service handles Redis connection errors."""
        # Mock Redis connection failure
        with patch("redis.from_url") as mock_from_url:
            mock_redis = MagicMock()
            mock_redis.ping.side_effect = Exception("Redis connection failed") 
            mock_from_url.return_value = mock_redis
            
            # Without Redis available, should fall back to direct execution
            job_service = JobService()

            # Should fall back to direct execution
            assert job_service.use_celery == False

    def test_job_service_logging(self):
        """Test that job service logs appropriately."""
        with patch("src.api.services.job_service.logger") as mock_logger:
            with patch("redis.from_url") as mock_from_url:
                mock_redis = MagicMock()
                mock_redis.ping.side_effect = Exception("Connection failed") 
                mock_from_url.return_value = mock_redis
                
                job_service = JobService()

                # Should have logged the fallback to direct execution
                mock_logger.info.assert_called_with("Celery not available, using direct execution")
