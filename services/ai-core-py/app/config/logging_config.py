# services/ai-core-py/app/config/logging_config.py
import logging
import sys

def setup_logging():
    """
    Configures the root logger for the application.
    This should be called once at the very beginning of the application startup.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s:%(lineno)d) - %(message)s",
        stream=sys.stdout,  # Log to the console
    )