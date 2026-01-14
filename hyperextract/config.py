# hyperextract/config.py
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# 1. Auto load .env
# Find the .env file in the project root directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 2. Configure Loguru
# Remove default handler (to avoid duplication or inconsistent formatting)
logger.remove()

# Add console output (development mode level can be DEBUG)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Add file output (automatic rotation, save log files)
logger.add(
    "logs/hyperextract.log",
    rotation="10 MB",  # Split file when it exceeds 10MB
    retention="10 days",  # Only keep recent 10 days
    level="DEBUG",  # Record more detailed information in file
    compression="zip",  # Compress historical logs
)


# Export logger for use in other modules
__all__ = ["logger"]