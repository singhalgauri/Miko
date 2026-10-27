# Owner: Person 2
# Purpose: Logging setup for Miko backend
# TODO(person2): Add structured JSON logging and log rotation to file

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configures and returns the root logger for Miko."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger("miko")


logger = setup_logging()
