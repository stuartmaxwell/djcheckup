"""Supporting dataclasses."""

from dataclasses import dataclass
from http.cookiejar import CookieJar

import httpx

from djcheckup_cli.enums import CheckResult, SeverityWeight


@dataclass
class SiteCheckContext:
    """Context object passed to all checks."""

    url: httpx.URL
    client: httpx.Client
    headers: httpx.Headers
    cookies: CookieJar
    content: str
    response_url: httpx.URL


@dataclass
class CheckResponse:
    """The response from an individual check."""

    name: str
    result: CheckResult
    severity_score: SeverityWeight
    message: str
