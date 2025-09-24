"""Check types."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from http.cookiejar import CookieJar
from typing import Literal

import httpx


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


@dataclass
class SiteCheckResult:
    """The result of a site check."""

    url: str
    check_results: list[CheckResponse]


@dataclass(kw_only=True)
class _BaseCheck(ABC):
    """Base class for all checks."""

    check_id: str
    name: str
    success: bool
    severity: SeverityWeight
    success_message: str
    failure_message: str
    depends_on: str | None = None

    @abstractmethod
    def check(self, context: SiteCheckContext) -> bool:
        """Run the check and return the result."""
        ...

    def run(self, context: SiteCheckContext, previous_results: dict[str, CheckResponse]) -> CheckResponse:
        """Run the header check."""
        if self.depends_on:
            dependent_result = previous_results.get(self.depends_on)

            if not dependent_result or dependent_result.result == CheckResult.FAILURE:
                return CheckResponse(
                    name=self.name,
                    result=CheckResult.SKIPPED,
                    severity_score=SeverityWeight.NONE,
                    message=f"Check skipped due to failed or missing dependency: {self.depends_on}",
                )

        check_result = self.check(context)

        result = CheckResult.SUCCESS if check_result == self.success else CheckResult.FAILURE

        return CheckResponse(
            name=self.name,
            result=result,
            severity_score=self.severity,
            message=self.success_message if result == CheckResult.SUCCESS else self.failure_message,
        )


@dataclass
class ContentCheck(_BaseCheck):
    """A content check.

    Checks for specific content in the response.
    Takes an optional path to check a different URL.
    """

    content: str
    path: str = ""

    def check(self, context: SiteCheckContext) -> bool:
        """Check if the response body contains the expected content."""
        response_content: str = ""

        if self.path:
            # Append the path to the url
            new_url = httpx.URL(context.url).join(self.path)

            response = context.client.get(new_url)
            response_content = response.text

        else:
            response_content = context.content

        if response_content == "":
            return False

        return self.content in response_content


@dataclass
class CookieCheck(_BaseCheck):
    """A cookie check."""

    cookie_name: str
    cookie_value: str = ""

    def check(self, context: SiteCheckContext) -> bool:
        """Check if a specific cookie is present and optionally if it matches a given value."""
        if not context.cookies:
            return False

        for cookie in context.cookies:
            if cookie.name == self.cookie_name:
                if self.cookie_value and cookie.value == self.cookie_value:
                    return True

                if not self.cookie_value:
                    return True

        return False


@dataclass
class CookieHttpOnlyCheck(_BaseCheck):
    """A cookie HttpOnly check."""

    cookie_name: str

    def check(self, context: SiteCheckContext) -> bool:
        """Check if a specific cookie is marked as HttpOnly."""
        if not context.cookies:
            return False

        for cookie in context.cookies:
            if cookie.name == self.cookie_name:
                return cookie.has_nonstandard_attr("HttpOnly")

        return False


@dataclass
class CookieSameSiteCheck(_BaseCheck):
    """A cookie SameSite check."""

    cookie_name: str
    samesite_value: Literal["Strict", "Lax", "None"]

    def check(self, context: SiteCheckContext) -> bool:
        """Check if a specific cookie has a SameSite attribute."""
        if not context.cookies:
            return False

        for cookie in context.cookies:
            if cookie.name == self.cookie_name:
                return cookie.get_nonstandard_attr("SameSite") == self.samesite_value

        return False


@dataclass
class CookieSecureCheck(_BaseCheck):
    """A cookie secure check.

    Checks if the specified cookie is marked as Secure.
    """

    cookie_name: str

    def check(self, context: SiteCheckContext) -> bool:
        """Check if a specific cookie is marked as Secure."""
        if not context.cookies:
            return False

        for cookie in context.cookies:
            if cookie.name == self.cookie_name:
                return cookie.secure

        return False


@dataclass
class HeaderCheck(_BaseCheck):
    """A header check."""

    header_name: str
    header_value: str = ""

    def check(self, context: SiteCheckContext) -> bool:
        """Check if a specific header is present and optionally if it matches a given value."""
        # Normalize header names to lowercase for case-insensitive comparison
        headers = {k.lower(): v for k, v in context.headers.items()}
        actual_value = headers.get(self.header_name.lower())
        if actual_value is None:
            return False

        # Compare header values case-insensitively if header_value is provided
        return not (self.header_value and actual_value.lower() != self.header_value.lower())


@dataclass
class PathCheck(_BaseCheck):
    """A path check.

    Checks if the specified path returns a successful response.

    Takes an optional status code to check against if you want to test for a specific status code.

    Returns True if the path is accessible or the status code matches.
    Returns False if the path is not accessible or the status code does not match.
    """

    path: str
    status_code: int | None = None

    def check(self, context: SiteCheckContext) -> bool:
        """Makes a request to the specified path and checks the response."""
        # Append the path to the url using the urlib module
        new_url = httpx.URL(context.url).join(self.path)

        response = context.client.get(new_url)

        if self.status_code:
            return response.status_code == self.status_code

        return bool(httpx.codes.is_success(response.status_code))


@dataclass
class SchemeCheck(_BaseCheck):
    """A scheme check.

    Checks if the URL scheme (http or https) that the request starts with matches the final scheme.

    `start_scheme` is the scheme to start with.
    `end_scheme` is the expected scheme after any redirects.
    """

    start_scheme: Literal["http", "https"]
    end_scheme: Literal["http", "https"]

    def check(self, context: SiteCheckContext) -> bool:
        """Check if the scheme of the URL in the request matches the final scheme."""
        # If the start scheme matches the original URL scheme, then we don't need a new request.
        if context.url.scheme == self.start_scheme:
            return context.response_url.scheme == self.end_scheme

        # Need to create a new URL with the specified start scheme
        new_url = context.url.copy_with(scheme=self.start_scheme)

        # And make a request to the new URL
        response = context.client.get(new_url)

        return response.url.scheme == self.end_scheme


def create_context(url: httpx.URL, client: httpx.Client, response: httpx.Response) -> SiteCheckContext:
    """Create a SiteCheckContext context object.

    Args:
        url: The URL to check.
        client: The HTTPX client to use for requests.
        response: The HTTPX response object from the initial request.

    Returns:
        A SiteCheckContext object containing the provided parameters.
    """
    return SiteCheckContext(
        url=url,
        client=client,
        headers=response.headers,
        cookies=response.cookies.jar,
        content=response.text,
        response_url=response.url,
    )


class SiteChecker:
    """Run all the checks for a given site."""

    def __init__(
        self,
        url: str,
        *,
        client: httpx.Client | None = None,
        user_agent: str = "DJCheckupBot/1.0 (+https://pypi.org/project/djcheckup/)",
        timeout: float = 10.0,
        follow_redirects: bool = True,
    ) -> None:
        """Initialize the SiteChecker with a URL and optional HTTPX client.

        Args:
            url: The URL to check.
            client: An optional HTTPX client to use for requests.
            user_agent: The User-Agent string to use for requests.
            timeout: The timeout for requests in seconds.
            follow_redirects: Whether to follow redirects.
        """
        self.url: httpx.URL = httpx.URL(url)
        self._client_provided = client is not None

        if client is not None:
            self.client = client
        else:
            self.client = httpx.Client(
                headers={"User-Agent": user_agent},
                timeout=timeout,
                follow_redirects=follow_redirects,
            )

    def close(self) -> None:
        """Close the HTTP client and release resources.

        Only close the client if it was created by this instance.
        """
        if not self._client_provided:
            self.client.close()

    # Context manager support for automatic cleanup
    def __enter__(self) -> "SiteChecker":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        """Context manager exit."""
        self.close()

    def run_first_check(self) -> CheckResponse:
        """Run the first check.

        This connects to the URL using httpx to check connectivity and then saves the page content, headers, and cookies
        into a context object for the remaining checks.
        """
        check_name = "Can I connect to your site?"
        severity_weight = SeverityWeight.HIGH
        success_message = "Connected to your site successfully."
        error_message = "Unable to connect to your site and no further checks can be performed."

        try:
            response = self.client.get(self.url)
            response.raise_for_status()

        except httpx.HTTPStatusError:
            return CheckResponse(
                name=check_name,
                result=CheckResult.FAILURE,
                severity_score=severity_weight,
                message=error_message,
            )

        self.context = create_context(self.url, self.client, response)

        return CheckResponse(
            name=check_name,
            result=CheckResult.SUCCESS,
            severity_score=severity_weight,
            message=success_message,
        )

    def run_checks(self, checks: Sequence[_BaseCheck]) -> SiteCheckResult:
        """Run all checks.

        Args:
            checks: Accepts any sequence (list, tuple, etc.) of check instances inheriting from _BaseCheck.

        Returns:
            A SiteCheckResult object containing the results of all checks.
        """
        # First, run the first check
        first_check = self.run_first_check()
        site_check_results = SiteCheckResult(url=str(self.url), check_results=[first_check])

        if first_check.result == CheckResult.FAILURE:
            return site_check_results

        # If the first check passes, run all other checks
        previous_results: dict[str, CheckResponse] = {"first_check": first_check}

        for check in checks:
            result = check.run(self.context, previous_results)
            site_check_results.check_results.append(result)
            previous_results[check.check_id] = result

        return site_check_results
