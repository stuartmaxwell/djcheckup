"""Supporting enums."""

from enum import Enum


class SeverityWeight(Enum):
    """Severity weight for the security score."""

    NONE = 0
    LOW = 5
    MEDIUM = 15
    HIGH = 30
    CRITICAL = 50


class CheckResult(Enum):
    """Possible results of a check."""

    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"
