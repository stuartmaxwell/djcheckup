"""Output the results as JSON."""

import json
from dataclasses import asdict

import httpx

from djcheckup.checks import CheckResult, SeverityWeight, SiteCheckResult


def custom_encoder(obj: object) -> str | int:
    """Custom JSON encoder for non-serializable types."""
    if isinstance(obj, SeverityWeight):
        return int(obj.value)

    if isinstance(obj, CheckResult):
        return str(obj.value)

    if isinstance(obj, httpx.URL):
        return str(obj)

    msg = f"Object of type {type(obj).__name__} is not JSON serializable"
    raise TypeError(msg)


def output_results_as_json(results: SiteCheckResult) -> str:
    """Convert the results to JSON format."""
    return json.dumps(asdict(results), default=custom_encoder)
