"""Test the SiteChecker class and related functionality."""

import httpx
import pytest

from djcheckup.checks import CheckResult, PathCheck, SeverityWeight, SiteChecker

url = "https://example.com"


def mock_response(request: httpx.Request) -> httpx.Response:
    """Return a fake response for any request."""
    # If the path matches /fail, raise a connection error
    if request.url.path == "/fail":
        msg = "Connection error."
        raise httpx.ConnectError(msg)
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


def test_second_check_fails(mock_client):
    """Test the second check fails."""
    checker = SiteChecker(url=url, client=mock_client)

    # create a dummy check
    dummy_check = PathCheck(
        check_id="failing_check",
        name="Failing Check",
        path="/fail",
        success=False,
        severity=SeverityWeight.HIGH,
        success_message="Success",
        failure_message="Fail",
    )

    result = checker.run_checks([dummy_check])

    # Assert the first check
    assert result.check_results[0].name == "Can I connect to your site?"
    assert result.check_results[0].result.value == CheckResult.SUCCESS.value

    # Assert the second check failed
    assert result.check_results[1].name == "Failing Check"
    assert result.check_results[1].result.value == CheckResult.FAILURE.value
    assert "An error occurred while running this check" in result.check_results[1].message


def test_sitechecker_init(mock_client, monkeypatch):
    """Test the SiteChecker class when not getting a custom HTTPX client passed to it."""

    def mock_httpx_client(*_args: object, **_kwargs: object) -> httpx.Client:
        return mock_client

    monkeypatch.setattr("httpx.Client", mock_httpx_client)

    checker = SiteChecker(url=url)
    assert checker._client_provided is False
    checker.close()
    assert checker.client.is_closed


def test_sitechecker_passes_verify_to_client(monkeypatch):
    """Test that SiteChecker passes the verify parameter to httpx.Client."""
    captured_kwargs = {}

    """
    This `MockClient` pretends to be an HTTPX client, but all it does is capture the kwargs passed to it.
    """

    class MockClient:
        def __init__(self, **kwargs: object) -> None:
            captured_kwargs.update(kwargs)

        def close(self) -> None:
            pass

    # Patch httpx.Client to capture arguments
    monkeypatch.setattr("httpx.Client", MockClient)

    # Test default (verify=True)
    captured_kwargs.clear()
    checker = SiteChecker(url=url)
    assert captured_kwargs.get("verify") is True
    checker.close()

    # Test verify=False
    captured_kwargs.clear()
    checker = SiteChecker(url=url, verify=False)
    assert captured_kwargs.get("verify") is False
    checker.close()
