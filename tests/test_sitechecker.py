"""Test the SiteChecker class and related functionality."""

import httpx
import pytest

from djcheckup.checks import CheckResult, SiteChecker

url = "https://example.com"


def mock_response(request: httpx.Request) -> httpx.Response:
    """Return a fake response for any request."""
    return httpx.Response(
        status_code=200,
        headers={"test-header-name": "test-header-value"},
        content="Test response content.",
    )


def mock_response_404(request: httpx.Request) -> httpx.Response:
    """Return a fake response for any request."""
    return httpx.Response(
        status_code=404,
        content="Page not found.",
    )


@pytest.fixture
def mock_client_404():
    """Return a mock HTTP client."""
    mock_transport = httpx.MockTransport(mock_response_404)
    return httpx.Client(transport=mock_transport)


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


def test_first_check_fails(mock_client_404):
    """Test the first check fails."""
    checker = SiteChecker(url=url, client=mock_client_404)

    # Example: check for the presence of the X-Frame-Options header
    result = checker.run_checks([])

    # Assert the check failed (header is missing)
    assert result.check_results[0].name == "Can I connect to your site?"
    assert result.check_results[0].result.value == CheckResult.FAILURE.value


def test_sitechecker_init(mock_client, monkeypatch):
    """Test the SiteChecker class when not getting a custom HTTPX client passed to it."""

    def mock_httpx_client(*_args: object, **_kwargs: object) -> httpx.Client:
        return mock_client

    monkeypatch.setattr("httpx.Client", mock_httpx_client)

    checker = SiteChecker(url=url)
    assert checker._client_provided is False
    checker.close()
    assert checker.client.is_closed
