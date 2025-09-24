"""Test the SiteChecker class and related functionality."""

import httpx
import pytest

from src.djcheckup.checks import CheckResult, SiteChecker

url = "https://example.com"


def mock_response(request: httpx.Request) -> httpx.Response:
    """Return a fake response for any request."""
    return httpx.Response(
        status_code=200,
        headers={"test-header-name": "test-header-value"},
        content="Test response content.",
    )


@pytest.fixture
def mock_client():
    """Return a mock HTTP client."""
    mock_transport = httpx.MockTransport(mock_response)
    return httpx.Client(transport=mock_transport)


def test_first_check(mock_client):
    """Test the first check."""
    checker = SiteChecker(url=url, client=mock_client)

    # Example: check for the presence of the X-Frame-Options header
    result = checker.run_checks([])

    # Assert the check passed (header is present)
    assert result.check_results[0].name == "Can I connect to your site?"
    assert result.check_results[0].result.value == CheckResult.SUCCESS.value
