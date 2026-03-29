"""
Loguru Logger Configuration

Provides flexible logging setup with optional file output.
Supports environment variables for configuration without requiring code changes.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Union
from loguru import logger

# ==================== Environment Variable Constants ====================
ENV_LOG_LEVEL = "HYPER_EXTRACT_LOG_LEVEL"
ENV_LOG_FILE = "HYPER_EXTRACT_LOG_FILE"


def setup_logger(
    level: str = "INFO",
    log_file: Optional[Union[str, Path]] = None,
    rotation: str = "10 MB",
    retention: str = "10 days",
    serialize: bool = False,
) -> None:
    """
    Configure Loguru Logger with optional file output.
    
    This function can be called explicitly by users to override default configuration.
    Environment variables are checked first, then parameters, then defaults.
    
    Args:
        level: Log level (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
               Defaults to "INFO". Overridden by HYPER_EXTRACT_LOG_LEVEL env var.
        log_file: Path to log file. If None, only console output is used.
                  Defaults to None. Overridden by HYPER_EXTRACT_LOG_FILE env var.
        rotation: Log rotation size (e.g., "10 MB", "1 GB", "00:00").
        retention: Log retention duration (e.g., "10 days", "7 days").
        serialize: If True, outputs logs in JSON format (suitable for production).
    
    Examples:
        # Default: console only, INFO level
        setup_logger()
        
        # Add file logging via code
        setup_logger(level="DEBUG", log_file="logs/debug.log")
        
        # Using environment variables (recommended for deployment)
        # HYPER_EXTRACT_LOG_LEVEL=DEBUG
        # HYPER_EXTRACT_LOG_FILE=./logs/app.log
    """
    # Remove all existing handlers to prevent duplication
    logger.remove()

    # 1. Determine final configuration (environment variables have highest priority)
    final_level = os.getenv(ENV_LOG_LEVEL, level).upper()
    env_log_file = os.getenv(ENV_LOG_FILE)
    final_log_file = log_file if log_file else env_log_file

    # 2. Add console handler
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stderr,
        level=final_level,
        format=console_format,
        serialize=serialize,
        colorize=True,
    )

    # 3. Add file handler (only if path is configured)
    if final_log_file:
        log_path = Path(final_log_file)
        # Ensure parent directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            str(log_path),
            rotation=rotation,
            retention=retention,
            level="DEBUG",  # File captures more detailed information
            compression="zip",
            encoding="utf-8",
            enqueue=True,  # Asynchronous I/O for thread safety
            serialize=serialize,
        )


# ==================== Default Initialization ====================
# Initialize with sensible defaults on module import.
# This ensures users don't need explicit setup_logger() calls for basic usage.
# Environment variables will be checked and applied automatically.
setup_logger(level="DEBUG")

# Export public API
__all__ = ["logger", "setup_logger"]
