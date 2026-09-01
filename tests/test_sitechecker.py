"""Test the SiteChecker class and related functionality."""

from urllib.parse import urlsplit, urlunsplit

import pytest
import requests
from requests.models import PreparedRequest, Response

from djcheckup.checks import CheckResult, PathCheck, RequestsClient, SeverityWeight, SiteChecker
from tests.http import MockAdapter, create_mock_client, create_response

url = "https://example.com"
DEFAULT_TIMEOUT = 10.0
CUSTOM_TIMEOUT = 5.0


def mock_response(request: PreparedRequest) -> Response:
    """Return a fake response for any request."""
    # If the path matches /fail, raise a connection error
    if urlsplit(request.url).path == "/fail":
        msg = "Connection error."
        raise requests.ConnectionError(msg)
    return create_response(
        request,
        status_code=200,
        headers={"test-header-name": "test-header-value"},
        content="Test response content.",
    )


def mock_response_404(request: PreparedRequest) -> Response:
    """Return a fake response for any request."""
    return create_response(
        request,
        status_code=404,
        content="Page not found.",
    )


@pytest.fixture
def mock_client_404():
    """Return a mock HTTP client."""
    return create_mock_client(mock_response_404)


@pytest.fixture
def mock_client():
    """Return a mock HTTP client."""
    return create_mock_client(mock_response)


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
    """Test the SiteChecker class when not getting a custom Requests client passed to it."""

    def mock_requests_client(*_args: object, **_kwargs: object) -> requests.Session:
        return mock_client

    monkeypatch.setattr("djcheckup.checks.RequestsClient", mock_requests_client)

    checker = SiteChecker(url=url)
    assert checker._client_provided is False
    adapter = checker.client.get_adapter(url)
    assert isinstance(adapter, MockAdapter)
    checker.close()
    assert adapter.closed is True


def test_sitechecker_passes_options_to_client(monkeypatch):
    """Test that SiteChecker passes its request options to RequestsClient."""
    captured_kwargs = {}

    """
    This `MockClient` pretends to be a Requests client, but all it does is capture the kwargs passed to it.
    """

    class MockClient:
        def __init__(self, **kwargs: object) -> None:
            captured_kwargs.update(kwargs)

        def close(self) -> None:
            pass

    monkeypatch.setattr("djcheckup.checks.RequestsClient", MockClient)

    # Test default (verify=True)
    captured_kwargs.clear()
    checker = SiteChecker(url=url)
    assert captured_kwargs.get("timeout") == DEFAULT_TIMEOUT
    assert captured_kwargs.get("follow_redirects") is True
    assert captured_kwargs.get("verify") is True
    checker.close()

    # Test verify=False
    captured_kwargs.clear()
    checker = SiteChecker(url=url, verify=False)
    assert captured_kwargs.get("verify") is False
    checker.close()


def test_requests_client_configuration():
    """Test that the default Requests client stores DJ Checkup's request defaults."""
    client = RequestsClient(timeout=CUSTOM_TIMEOUT, follow_redirects=False, verify=False)

    def redirect_to_https(request: PreparedRequest) -> Response:
        assert isinstance(request.url, str)
        request_url = urlsplit(request.url)
        return create_response(
            request,
            status_code=301,
            headers={"Location": urlunsplit(request_url._replace(scheme="https"))},
        )

    adapter = MockAdapter(redirect_to_https)
    client.mount("http://", adapter)

    assert client.timeout == CUSTOM_TIMEOUT
    assert client.follow_redirects is False
    assert client.verify is False
    assert client.headers["User-Agent"] == "DJCheckupBot/1.0 (+https://pypi.org/project/djcheckup/)"

    response = client.get("http://example.com")

    assert response.status_code == requests.codes.moved_permanently
    assert response.history == []
    assert adapter.last_timeout == CUSTOM_TIMEOUT
    assert adapter.last_verify is False

    client.close()
