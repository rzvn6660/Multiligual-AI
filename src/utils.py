import logging
import sys

def setup_logger(name):
    """
    Sets up a logger with standard formatting.
    """
    # Ensure stdout handles UTF-8 (Vital for Windows)
    if hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
            
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(handler)
        
        # Also log to file with UTF-8 encoding
        file_handler = logging.FileHandler("server_debug.log", encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
