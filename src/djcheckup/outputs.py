"""Output formats for the site check results."""

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from enum import Enum
from typing import TypeAlias, TypedDict

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from djcheckup.checks import CheckResult, SiteCheckResult


class CheckResponseDict(TypedDict):
    """Represents the response for a single check."""

    name: str
    result: str  # from CheckResult
    severity_score: int  # from SeverityWeight
    message: str


class SiteCheckResultDict(TypedDict):
    """Represents the response for a site check."""

    url: str
    check_results: list[CheckResponseDict]


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

        if result.result == CheckResult.FAILURE:
            emoji = "🔴 "

        if result.result == CheckResult.SKIPPED:
            emoji = "🟡 "

        display_result = emoji + result.result.value.capitalize()
        table.add_row(result.name, display_result, Markdown(result.message))

    console.print(Panel(table))


JSONValue: TypeAlias = str | int | Mapping[str, "JSONValue"] | Sequence["JSONValue"]  # noqa: UP040 3.10 3.11


def normalize_for_json(obj: JSONValue) -> JSONValue:
    """Recursively convert a dict with Enums to a json-serialisable dict.

    This is used to convert the SiteCheckResult object to one that can be converted directly to JSON.
    """
    # dict-like objects
    if isinstance(obj, Mapping):
        return {k: normalize_for_json(v) for k, v in obj.items()}

    # list-like objects
    if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
        return [normalize_for_json(v) for v in obj]

    # Enums, e.g. SeverityWeight and CheckResult
    if isinstance(obj, Enum):
        return obj.value

    if isinstance(obj, (str, int)):
        return obj

    # The following code should never be reached
    msg = f"Unexpected type: {type(obj)}"  # pragma: no cover
    raise TypeError(msg)  # pragma: no cover


def sitecheck_as_dict(site_result: SiteCheckResult) -> SiteCheckResultDict:
    """Convert SiteCheckResult into JSON-serialisable dict."""
    return normalize_for_json(asdict(site_result))  # type: ignore  # noqa: PGH003


def sitecheck_as_json(site_result: SiteCheckResult) -> str:
    """Convert SiteCheckResult into JSON string."""
    data = sitecheck_as_dict(site_result)
    return json.dumps(data)
