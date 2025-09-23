"""Run the DJ Checkup security scanner."""

from typing import Literal, overload

from djcheckup.check_defs import all_checks
from djcheckup.checks import SiteChecker, SiteCheckResult
from djcheckup.outputs import output_results_as_json


@overload
def run_checks(url: str, output_format: Literal["object"] = "object") -> SiteCheckResult: ...
@overload
def run_checks(url: str, output_format: Literal["json"]) -> str: ...


def run_checks(url: str, output_format: Literal["object", "json"] = "object") -> str | SiteCheckResult:
    """Run the DJ Checkup tool against a specific URL and returns a JSON string."""
    with SiteChecker(url) as checker:
        results = checker.run_checks(all_checks)

    if output_format not in {"object", "json"}:
        msg = f"Invalid output_format: {output_format!r}. Must be 'object' or 'json'."
        raise ValueError(msg)

    if output_format == "json":
        return output_results_as_json(results)

    # Default to object output
    return str(results)
