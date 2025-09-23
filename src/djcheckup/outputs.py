"""Output formats for the site check results."""

import json
from dataclasses import asdict

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from djcheckup.checks import CheckResult, SeverityWeight, SiteCheckResult


def rich_output(check_results: SiteCheckResult) -> None:
    """Display results using Rich."""
    console = Console()

    table = Table(title=f"DJ Checkup Results for {check_results.url}", show_lines=True)

    table.add_column("Check", justify="left")
    table.add_column("Result", justify="left")
    table.add_column("Message", justify="left")

    for result in check_results.check_results:
        emoji = ""
        if result.result == CheckResult.SUCCESS:
            emoji = "🟢 "
        elif result.result == CheckResult.FAILURE:
            emoji = "🔴 "
        elif result.result == CheckResult.SKIPPED:
            emoji = "🟡 "
        display_result = emoji + result.result.value.capitalize()
        table.add_row(result.name, display_result, Markdown(result.message))

    console.print(Panel(table))


def json_encoder(obj: object) -> str | int:
    """Custom JSON encoder for non-serialisable types."""
    if isinstance(obj, SeverityWeight):
        return obj.value

    if isinstance(obj, CheckResult):
        return obj.value

    msg = f"Object of type {type(obj).__name__} is not JSON serialisable"
    raise TypeError(msg)


def output_results_as_json(results: SiteCheckResult) -> str:
    """Convert the results to JSON format."""
    return json.dumps(asdict(results), default=json_encoder)
