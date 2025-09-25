"""Tests the check definitions."""

import httpx
import pytest

from djcheckup.check_defs import all_checks
from djcheckup.checks import CheckResult, SiteChecker

url = "https://example.com"


def mock_perfect_site(request: httpx.Request) -> httpx.Response:
    """Return a mock response that mimics a perfect Django site."""
    if request.url.path in ["/admin", "/a/b/c/d/e/f/g/h/i/j/xyz/", "/accounts/login"]:
        return httpx.Response(
            status_code=404,
            content="Page not found.",
        )

    if request.url.scheme == "http":
        return httpx.Response(
            status_code=301,
            headers={"Location": str(request.url.copy_with(scheme="https"))},
            request=request,
        )

    headers = [
        ("X-Frame-Options", "xxx"),
        ("Strict-Transport-Security", "xxx"),
        ("Set-Cookie", "csrftoken=xxx; Path=/; HttpOnly; Secure; SameSite=Lax"),
        ("Set-Cookie", "sessionid=xxx; Path=/; HttpOnly; Secure; SameSite=Lax"),
    ]

    return httpx.Response(
        status_code=200,
        headers=headers,
        content="Test response content.",
    )


@pytest.fixture
def mock_client():
    """Return a mock HTTPX client that returns a successful response with all cookies and headers."""
    mock_transport = httpx.MockTransport(mock_perfect_site)
    return httpx.Client(transport=mock_transport, follow_redirects=True)


def test_all_checks(mock_client):
    """Test that all checks pass on a perfect site."""
    checker = SiteChecker(url=url, client=mock_client)
    results = checker.run_checks(all_checks)

    for check_result in results.check_results:
        assert check_result.result.value == CheckResult.SUCCESS.value, (
            f"Check {check_result.name} failed: {check_result.message}"
        )
