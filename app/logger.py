import logging
import os
from logging.handlers import RotatingFileHandler
import sys
import traceback


def setup_logger(name, log_file="app.log", level=None):
    """Configure and return a logger instance"""
    
    # Determine log level from environment or default to DEBUG for more detailed logging
    if level is None:
        log_level_str = os.getenv('LOG_LEVEL', 'DEBUG').upper()
        level = getattr(logging, log_level_str, logging.DEBUG)
    
    # Enhanced formatter with thread info, function name, and line number
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - [%(threadName)s] - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s"
    )

    # Console handler with DEBUG level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # File handler with rotation and DEBUG level
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers and add new ones
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Add exception hook to log unhandled exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Call the default handler for KeyboardInterrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    return logger


# Create main logger with debug level
main_logger = setup_logger("app", level=logging.DEBUG)

# Log startup information
main_logger.debug("Logger initialized with DEBUG level")
main_logger.debug(f"Python version: {sys.version}")
main_logger.debug(f"Current working directory: {os.getcwd()}")
