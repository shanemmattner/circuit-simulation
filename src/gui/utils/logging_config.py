"""Logging configuration for Circuit Analysis Dashboard."""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_gui_logging(log_file: str = "logs/gui_session.log") -> logging.Logger:
    """Set up comprehensive logging for GUI sessions.
    
    Args:
        log_file: Path to log file for session logs
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler  
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logger = logging.getLogger('gui')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log session start
    logger.info(f"=== GUI Session Started: {datetime.now()} ===")
    
    return logger


def log_api_request(logger: logging.Logger, method: str, url: str, status_code: int = None, error: str = None):
    """Log API request details.
    
    Args:
        logger: Logger instance
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        status_code: Response status code
        error: Error message if request failed
    """
    if error:
        logger.error(f"API {method} {url} - ERROR: {error}")
    elif status_code:
        level = logging.INFO if 200 <= status_code < 300 else logging.WARNING
        logger.log(level, f"API {method} {url} - Status: {status_code}")
    else:
        logger.debug(f"API {method} {url} - Starting request")


def log_callback_execution(logger: logging.Logger, callback_name: str, inputs: dict, success: bool = True, error: str = None):
    """Log Dash callback execution details.
    
    Args:
        logger: Logger instance
        callback_name: Name of the callback function
        inputs: Input values that triggered the callback
        success: Whether callback executed successfully
        error: Error message if callback failed
    """
    if success:
        logger.info(f"Callback {callback_name} executed - Inputs: {inputs}")
    else:
        logger.error(f"Callback {callback_name} failed - Inputs: {inputs} - Error: {error}")


def log_user_interaction(logger: logging.Logger, action: str, details: dict = None):
    """Log user interactions for analysis.
    
    Args:
        logger: Logger instance
        action: Description of user action
        details: Additional details about the interaction
    """
    if details:
        logger.info(f"User Action: {action} - Details: {details}")
    else:
        logger.info(f"User Action: {action}")
        

# Export main setup function
__all__ = ['setup_gui_logging', 'log_api_request', 'log_callback_execution', 'log_user_interaction']