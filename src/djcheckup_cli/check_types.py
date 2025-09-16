"""Check types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

import httpx

from djcheckup_cli import logger
from djcheckup_cli.dataclasses import CheckResponse, SiteCheckContext
from djcheckup_cli.enums import CheckResult, SeverityWeight


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
                logger.info(f"Skipping check '{self.name}' because it depends on failed check '{self.depends_on}'.")

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
            logger.info(f"Header '{self.header_name}' not found: {context.headers}")
            return False

        # Compare header values case-insensitively if header_value is provided
        if self.header_value and actual_value.lower() != self.header_value.lower():
            logger.info(f"Header '{self.header_name}' value '{actual_value}' doesn't match '{self.header_value}'.")
            return False

        logger.debug(f"Header '{self.header_name}' is present with value '{actual_value}'.")
        return True


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
        response_content: str | None = ""

        if self.path:
            # Append the path to the url
            new_url = httpx.URL(context.url).join(self.path)
            logger.info(f"Making request to {new_url}")

            response = context.client.get(new_url)
            response_content = response.text

        else:
            response_content = context.content

        if response_content is None:
            logger.warning("No response content to check.")
            return False

        if self.content not in response_content:
            logger.debug("Response body does not contain expected content.")
            return False

        logger.debug("Response body contains expected content.")
        return True


@dataclass
class CookieCheck(_BaseCheck):
    """A cookie check."""

    cookie_name: str
    cookie_value: str = ""

    def check(self, context: SiteCheckContext) -> bool:
        """Check if a specific cookie is present and optionally if it matches a given value."""
        if context.cookies is None:
            logger.warning("No response cookies to check.")
            return False

        for cookie in context.cookies:
            if cookie.name == self.cookie_name:
                if self.cookie_value and cookie.value == self.cookie_value:
                    logger.info(
                        f"Cookie '{self.cookie_name}' value '{cookie.value}' doesn't match '{self.cookie_value}'.",
                    )
                    return True

                if not self.cookie_value:
                    logger.debug(f"Cookie '{self.cookie_name}' is present.")
                    return True

        logger.debug(f"Cookie '{self.cookie_name}' is not present.")
        return False


@dataclass
class CookieHttpOnlyCheck(_BaseCheck):
    """A cookie HttpOnly check."""

    cookie_name: str

    def check(self, context: SiteCheckContext) -> bool:
        """Check if a specific cookie is marked as HttpOnly."""
        if context.cookies is None:
            logger.warning("No response cookies to check.")
            return False

        for cookie in context.cookies:
            if cookie.name == self.cookie_name:
                return cookie.has_nonstandard_attr("HttpOnly")

        logger.info(f"Cookie '{self.cookie_name}' was not found.")
        return False


@dataclass
class CookieSameSiteCheck(_BaseCheck):
    """A cookie SameSite check."""

    cookie_name: str
    samesite_value: Literal["Strict", "Lax", "None"]

    def check(self, context: SiteCheckContext) -> bool:
        """Check if a specific cookie has a SameSite attribute."""
        if context.cookies is None:
            logger.warning("No response cookies to check.")
            return False

        for cookie in context.cookies:
            if cookie.name == self.cookie_name:
                return cookie.get_nonstandard_attr("SameSite") == self.samesite_value

        logger.info(f"Cookie '{self.cookie_name}' was not found.")
        return False


@dataclass
class CookieSecureCheck(_BaseCheck):
    """A cookie secure check.

    Checks if the specified cookie is marked as Secure.
    """

    cookie_name: str

    def check(self, context: SiteCheckContext) -> bool:
        """Check if a specific cookie is marked as Secure."""
        if context.cookies is None:
            logger.warning("No response cookies to check.")
            return False

        for cookie in context.cookies:
            if cookie.name == self.cookie_name:
                logger.debug(f"Found cookie '{self.cookie_name}': {cookie}, with attributes {cookie.__dict__}")
                return cookie.secure

        logger.info(f"Cookie '{self.cookie_name}' was not found.")
        return False


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
        logger.info(f"Making request to {new_url}")

        response = context.client.get(new_url)
        logger.info(f"Response status code: {response.status_code}")

        if httpx.codes.is_success(response.status_code):
            logger.debug(f"Request to {new_url} succeeded.")
            return True

        logger.debug(f"Request to {new_url} failed with status code {response.status_code}.")
        return False


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
        if context.url.scheme == self.start_scheme and context.response_url.scheme == self.end_scheme:
            logger.debug(f"URL '{context.url}' scheme matches expected scheme '{self.end_scheme}'.")
            return True

        # Need to create a new URL with the specified start scheme
        new_url = context.url.copy_with(scheme=self.start_scheme)
        logger.debug(f"Created new URL '{new_url}' with scheme '{self.end_scheme}'.")

        # And make a request to the new URL
        response = context.client.get(new_url)

        if response.url.scheme == self.end_scheme:
            logger.debug(f"Request to {new_url} succeeded.")
            return True

        logger.debug(f"URL '{context.url}' matches scheme '{self.start_scheme}' to '{self.end_scheme}'.")
        return False
