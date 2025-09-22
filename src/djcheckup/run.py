"""Run the DJ Checkup security scanner."""

from djcheckup.check_defs import all_checks
from djcheckup.checks import SiteChecker
from djcheckup.output_json import output_results_as_json


def run_checks(url: str) -> str:
    """Run the DJ Checkup tool against a specific URL and returns a JSON string."""
    checker = SiteChecker(url)
    results = checker.run_checks(all_checks)

    return output_results_as_json(results)
