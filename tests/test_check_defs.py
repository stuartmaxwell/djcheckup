"""Tests the check definitions."""

from urllib.parse import urlsplit, urlunsplit

import pytest
from requests.models import PreparedRequest, Response

from djcheckup.check_defs import all_checks
from djcheckup.checks import CheckResult, SiteChecker
from tests.http import create_mock_client, create_response

url = "https://example.com"


def mock_perfect_site(request: PreparedRequest) -> Response:
    """Return a mock response that mimics a perfect Django site."""
    request_url = urlsplit(request.url)
    if request_url.path in ["/admin", "/a/b/c/d/e/f/g/h/i/j/xyz/", "/accounts/login"]:
        return create_response(
            request,
            status_code=404,
            content="Page not found.",
        )

    if request_url.scheme == "http":
        return create_response(
            request,
            status_code=301,
            headers={"Location": urlunsplit(request_url._replace(scheme="https"))},
        )

    headers = [
        ("X-Frame-Options", "xxx"),
        ("Strict-Transport-Security", "xxx"),
        ("Set-Cookie", "csrftoken=xxx; Path=/; HttpOnly; Secure; SameSite=Lax"),
        ("Set-Cookie", "sessionid=xxx; Path=/; HttpOnly; Secure; SameSite=Lax"),
    ]

    return create_response(
        request,
        status_code=200,
        headers=headers,
        content="Test response content.",
    )


@pytest.fixture
def mock_client():
    """Return a mock Requests client that returns a successful response with all cookies and headers."""
    return create_mock_client(mock_perfect_site)


def test_all_checks(mock_client):
    """Test that all checks pass on a perfect site."""
    checker = SiteChecker(url=url, client=mock_client)
    results = checker.run_checks(all_checks)

    for check_result in results.check_results:
        assert check_result.result.value == CheckResult.SUCCESS.value, (
            f"Check {check_result.name} failed: {check_result.message}"
        )
