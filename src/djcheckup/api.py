"""Run the DJ Checkup security scanner."""

from typing import Literal, overload

import httpx

from djcheckup.check_defs import all_checks
from djcheckup.checks import SiteChecker
from djcheckup.outputs import SiteCheckResultDict, sitecheck_as_dict, sitecheck_as_json


@overload
def run_checks(
    url: str,
    output_format: Literal["object"] = "object",
    client: httpx.Client | None = None,
) -> SiteCheckResultDict: ...
@overload
def run_checks(url: str, output_format: Literal["json"], client: httpx.Client | None = None) -> str: ...


def run_checks(
    url: str,
    output_format: Literal["object", "json"] = "object",
    client: httpx.Client | None = None,
) -> str | SiteCheckResultDict:
    """Run the DJ Checkup tool.

    Args:
        url: The URL to check.
        output_format: The format of the output, either "object" or "json" (default: "object").
        client: An optional HTTPX client to use for requests.

    Returns:
        The result of the checks, either as a JSON string or a SiteCheckResult object.
    """
    with SiteChecker(url, client=client) as checker:
        results = checker.run_checks(all_checks)

    if output_format not in {"object", "json"}:
        msg = f"Invalid output_format: {output_format!r}. Must be 'object' or 'json'."
        raise ValueError(msg)

    if output_format == "json":
        return sitecheck_as_json(results)

    # Default to object output
    return sitecheck_as_dict(results)
