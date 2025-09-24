"""Tests the check definitions."""

import httpx
import pytest

from src.djcheckup.check_defs import xframe_header_check
from src.djcheckup.checks import CheckResult, SiteChecker

url = "https://example.com"


def mock_response(request: httpx.Request):
    """Return a fake response for any request."""
    return httpx.Response(
        status_code=200,
        headers={"X-Frame-Options": "mocked"},
        content="Hello from mock!",
    )


@pytest.fixture
def mock_client():
    """Return a mock HTTP client."""
    mock_transport = httpx.MockTransport(mock_response)
    return httpx.Client(transport=mock_transport)


def test_xframe_header_check(mock_client):
    """Set up the mock transport and client."""
    # Create a SiteChecker with the mock client
    checker = SiteChecker(url=url, client=mock_client)

    # Example: check for the presence of the X-Frame-Options header
    result = checker.run_checks([xframe_header_check])

    # Assert the check passed (header is present)
    assert result.check_results[1].name == "Is the X-Frame-Options header set?"
    assert result.check_results[1].result.value == CheckResult.SUCCESS.value
