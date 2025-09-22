"""DJ Checkup CLI package."""

import logging

from rich.logging import RichHandler

from djcheckup.run import run_checks

FORMAT = "%(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

logger = logging.getLogger("rich")

__all__ = ["run_checks"]
