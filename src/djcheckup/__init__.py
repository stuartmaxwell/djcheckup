"""DJ Checkup CLI package."""

from djcheckup.api import run_checks
from djcheckup.outputs import SiteCheckResultDict

__all__ = ["SiteCheckResultDict", "run_checks"]

__version__ = "1.0.0"
