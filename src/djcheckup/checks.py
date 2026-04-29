"""Check types."""

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from http.cookiejar import CookieJar
from types import TracebackType
from typing import Literal

import httpxyz

from djcheckup.protocols import ClientProtocol, ResponseProtocol, UrlProtocol


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
    """Context object passed to all checks.

    Args:
        url (str): The URL being checked. Note: we use a string here so that the underlying HTTP client can handle it.
        client (ClientProtocol): The HTTP client to use for requests. Must match the `ClientProtocol` protocol.
        headers (Mapping[str, str]): The headers retrieved from the first response.
        cookies (CookieJar): The cookies retrieved from the first response.
        content (str): The content retrieved from the first response.
        response_url (UrlProtocol): The URL of the response after any redirects.
    """

    url: str
    client: ClientProtocol
    headers: Mapping[str, str]
    cookies: CookieJar
    content: str
    response_url: UrlProtocol


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
        """This is the check that needs to be run.

        Each check that is created, needs to implement a `check` method that returns a boolean result.

        Args:
            context: The site check context.

        Returns:
            True if the check passes, False otherwise.
        """
        ...

    def run(self, context: SiteCheckContext, previous_results: dict[str, CheckResponse]) -> CheckResponse:
        """Run the check.

        Args:
            context: The site check context.
            previous_results: A dictionary of previous check results.

        Returns:
            The check response.
        """
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
    Takes an optional path to check a specific path appended to the URL.
    """

    content: str
    path: str = ""

    def check(self, context: SiteCheckContext) -> bool:
        """Check if the response body contains the expected content."""
        response_content: str = ""

        if self.path:
            # Append the path to the url
            # We use httpxyz.URL to manipulate the URL, and then convert back to the str value.
            new_url = str(httpxyz.URL(context.url).join(self.path))

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
    """A cookie SameSite check.

    Checks that the cookie has the expected SameSite value.
    If the `samesite_value` is omitted, then it checks if the value is set to Lax or Strict.
    """

    cookie_name: str
    samesite_value: Literal["Strict", "Lax", "None"] | None = None

    def check(self, context: SiteCheckContext) -> bool:
        """Check if a specific cookie has a SameSite attribute."""
        if not context.cookies:
            return False

        for cookie in context.cookies:
            if cookie.name == self.cookie_name:
                if not self.samesite_value:
                    return cookie.get_nonstandard_attr("SameSite") in ["Lax", "Strict"]

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
    """A header check.

    Checks if a specific header name is present.
    If the header value is provided, also checks if it matches the actual value.
    """

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
        new_url: str = str(httpxyz.URL(context.url).join(self.path))

        response = context.client.get(new_url)

        if self.status_code:
            return response.status_code == self.status_code

        # Use the `codes` shortcut in HTTPXYZ to check the status code
        return bool(httpxyz.codes.is_success(response.status_code))


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
        # Even if an alternative client has been provided, we use the `URL` methods from HTTPXYZ.
        url = httpxyz.URL(context.url)
        if url.scheme == self.start_scheme:
            return context.response_url.scheme == self.end_scheme

        # Need to create a new URL with the specified start scheme
        new_url = str(httpxyz.URL(context.url).copy_with(scheme=self.start_scheme))

        # And make a request to the new URL
        response = context.client.get(new_url)

        return response.url.scheme == self.end_scheme


def create_context(url: str, client: ClientProtocol, response: ResponseProtocol) -> SiteCheckContext:
    """Create a SiteCheckContext context object.

    This function is called by the `first_check` method and is used to gather the response from the first check which
    is used by the subsequent checks.

    Args:
        url: The URL being checked.
        client: The HTTP client to use for any new requests.
        response: The HTTP response object from the initial request.

    Returns:
        A SiteCheckContext object containing the following fields:
        - url: The URL being checked.
        - client: The HTTP client to use for any new requests.
        - headers: The HTTP headers from the initial response.
        - cookies: The HTTP cookies from the initial response.
        - content: The response content as a string.
        - response_url: The URL of the final response (after any redirects).
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
        client: ClientProtocol | None = None,
        timeout: float = 10.0,
        follow_redirects: bool = True,
        verify: bool = True,
    ) -> None:
        """Initialize the SiteChecker with a URL and optional HTTP client.

        The HTTP client is defined in the ClientProtocol protocol and by default this will use HTTPXYZ, unless an
        alternative is provided. The alternative could be a custom HTTPXYZ client, or an HTTPX client will also work.

        Args:
            url (str): The URL to check.
            client (ClientProtocol): An optional HTTP client to use for requests.
            timeout (float): The timeout for requests in seconds.
            follow_redirects (bool): Whether to follow redirects.
            verify (bool): Whether to verify SSL certificates.
        """
        self.url = url
        self._client_provided = client is not None

        if client is not None:
            self.client = client
        else:
            self.client = httpxyz.Client(
                headers={"User-Agent": "DJCheckupBot/1.0 (+https://pypi.org/project/djcheckup/)"},
                timeout=timeout,
                follow_redirects=follow_redirects,
                verify=verify,
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

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        self.close()

    def run_first_check(self) -> CheckResponse:
        """Run the first check.

        The first check is responsible for checking connectivity to the URL provided, and setting up the initial
        `SiteCheckContext` context object, which is then used by all subsequent checks.

        The following steps are performed:

        - Create a `CheckResponse` class to return the result of the check. We set the result to failure.
        - Try a GET request to the URL provided.
        - If this fails, then modify the CheckResponse message, and return the failed result.
        - If this succeeds, we create a `SiteCheckContext` object with the response.
        - The `SiteCheckContext` object is added to the `context` attribute of the `SiteChecker` object.
        - Then we modify the `CheckResponse` to indicate the success with a successful message and return it.

        Returns:
            The `CheckResponse` object indicating the result of the check.
        """
        check_response = CheckResponse(
            name="Can I connect to your site?",
            severity_score=SeverityWeight.HIGH,
            result=CheckResult.FAILURE,
            message="",
        )

        try:
            response = self.client.get(self.url)
            response.raise_for_status()

        except Exception as e:
            error_name = type(e).__name__
            check_response.message = (
                f"Unable to connect to your site and no further checks can be performed. \n\n> **{error_name}**: `{e}`"
            )
            return check_response

        self.context = create_context(self.url, self.client, response)

        check_response.result = CheckResult.SUCCESS
        check_response.message = "Connected to your site successfully."

        return check_response

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
            try:
                result = check.run(self.context, previous_results)

            except Exception as e:
                error_name = type(e).__name__
                result = CheckResponse(
                    name=check.name,
                    result=CheckResult.FAILURE,
                    severity_score=check.severity,
                    message=f"An error occurred while running this check: \n\n> **{error_name}**: `{e}`",
                )

            site_check_results.check_results.append(result)
            previous_results[check.check_id] = result

        return site_check_results
