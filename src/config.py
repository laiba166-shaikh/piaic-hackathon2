"""
Configuration and logging setup for Phase 1 CLI Todo App.

This module provides:
- Logging configuration with structured format
- Application constants
- Environment variable management
"""
import logging
import os
from pathlib import Path

# Application metadata
APP_NAME = "Todo CLI"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Phase 1 CLI Todo App - In-Memory Task Manager"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    """
    Configure structured logging for the application.

    Format: [TIMESTAMP] [LEVEL] [MODULE] - MESSAGE
    Example: 2025-12-13 10:30:45 [INFO] src.cli.main - Starting Todo CLI

    Level: Controlled by LOG_LEVEL environment variable (default: INFO)
    """
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Initialize logging when module is imported
setup_logging()
