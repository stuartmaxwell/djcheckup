"""Run all the checks!"""

import httpx

from djcheckup_cli import logger
from djcheckup_cli.check_types import _BaseCheck
from djcheckup_cli.dataclasses import CheckResponse, SiteCheckContext
from djcheckup_cli.enums import CheckResult, SeverityWeight


class SiteChecker:
    """Run all the checks for a given site."""

    def __init__(self, url: str) -> None:
        """Initialize the SiteChecker with a URL."""
        self.url: httpx.URL = httpx.URL(url)
        self.user_agent: str = "DJCheckupBot/1.0 (+https://djcheckup.com/bot-info)"
        self.timeout: float = 10.0
        self.client: httpx.Client = httpx.Client(
            headers={"User-Agent": self.user_agent},
            timeout=self.timeout,
            follow_redirects=True,
        )

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self.client.close()

    def run_first_check(self) -> CheckResponse:
        """Run the first check.

        This connects to the URL using httpx to check connectivity and then saves the page content, headers, and cookies
        into a context object for the remaining checks.
        """
        logger.info(f"Running first check for {self.url}")

        try:
            response = self.client.get(self.url)
            response.raise_for_status()
            logger.debug(f"Successfully connected to {self.url}")

        except httpx.RequestError:
            logger.exception(f"Error connecting to {self.url}")
            return CheckResponse(
                name="Can I connect to your site?",
                result=CheckResult.FAILURE,
                severity_score=SeverityWeight.HIGH,
                message="I was unable to connect to the site.",
            )

        self.context = SiteCheckContext(
            url=self.url,
            client=self.client,
            headers=response.headers,
            cookies=response.cookies.jar,
            content=response.text,
            response_url=response.url,
        )

        logger.info(f"Finished first check for {self.url}")

        return CheckResponse(
            name="Can I connect to your site?",
            result=CheckResult.SUCCESS,
            severity_score=SeverityWeight.NONE,
            message="I was able to connect to the site.",
        )

    def run_checks(self, checks: list[_BaseCheck]) -> list[CheckResponse]:
        """Run all checks."""
        # First, run the first check
        first_check = self.run_first_check()
        if first_check.result is False:
            return [first_check]

        # If the first check passes, run all other checks
        results: list[CheckResponse] = [first_check]
        previous_results: dict[str, CheckResponse] = {"first_check": first_check}

        for check in checks:
            result = check.run(self.context, previous_results)
            results.append(result)
            previous_results[check.check_id] = result
            logger.debug(f"Finished running check: {check.name}")

        # Close the HTTP client
        self.client.close()

        return results
