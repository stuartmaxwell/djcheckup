"""DJ Checkup CLI package."""

import logging

from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

logger = logging.getLogger("rich")

__version__ = "0.1.1"
