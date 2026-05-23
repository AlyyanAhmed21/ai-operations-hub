# backend/utils/logger.py
import logging
import sys

def get_logger(name: str = "AIOpsHub"):
    """Configures and returns a professional logger."""
    logger = logging.getLogger(name)
    
    # Prevent adding multiple handlers if logger is called multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatter and add it to the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to the logger
        logger.addHandler(console_handler)
        
    return logger

# Create a default logger instance to import across the app
logger = get_logger()