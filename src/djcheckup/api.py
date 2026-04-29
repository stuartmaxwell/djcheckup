"""Run the DJ Checkup security scanner."""

from typing import Literal, overload

from djcheckup.check_defs import all_checks
from djcheckup.checks import SiteChecker
from djcheckup.outputs import SiteCheckResultDict, sitecheck_as_dict, sitecheck_as_json
from djcheckup.protocols import ClientProtocol


@overload
def run_checks(
    url: str,
    output_format: Literal["object"] = "object",
    client: ClientProtocol | None = None,
) -> SiteCheckResultDict: ...
@overload
def run_checks(
    url: str,
    output_format: Literal["json"],
    client: ClientProtocol | None = None,
) -> str: ...


def run_checks(
    url: str,
    output_format: Literal["object", "json"] = "object",
    client: ClientProtocol | None = None,
) -> str | SiteCheckResultDict:
    """Run the DJ Checkup tool.

    This is the main interface to the DJ Checkup API. The quickest and easiest way to use this method is to just pass
    a URL, and you will get a `SiteCheckResultDict` object as a response.

    If you prefer to get a JSON response, you can set the `output_format` to `"json"`, and the results will be returned
    as a JSON string.

    By default, this uses the HTTPXYZ library with the following options:

    ```python
    httpxyz.Client(
        headers={"User-Agent": "DJCheckupBot/1.0 (+https://pypi.org/project/djcheckup/)"},
        timeout=10.0,
        follow_redirects=True,
        verify=True,
    )
    ```

    You can optionally create your own customized client with either the HTTPXYZ library, or the original HTTPX library,
    and pass this to the `client` parameter.

    Args:
        url (str): The URL to check.
        output_format (str): The format of the output, either "object" or "json" (default: "object").
        client (ClientProtocol | None): An optional HTTP client to use for requests.

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
