import logging
import os
from datetime import datetime

# Create logs directory
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Log file name with timestamp
log_file = os.path.join(LOGS_DIR, f"logistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)

def get_logger(name):
    """Get a logger instance with the given name."""
    return logging.getLogger(name)
