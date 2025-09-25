"""Tests for the CLI interface."""

import httpx
import pytest
from typer.testing import CliRunner

from djcheckup.checks import SiteCheckResult
from djcheckup.cli import app
from djcheckup.run import run_checks

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


def mock_response(request: httpx.Request) -> httpx.Response:
    """Return a barebones mock response."""
    return httpx.Response(
        status_code=200,
        content="Test response content.",
    )


@pytest.fixture
def mock_perfect_client():
    """Return a mock HTTPX client that returns a successful response with all cookies and headers."""
    mock_transport = httpx.MockTransport(mock_perfect_site)
    return httpx.Client(transport=mock_transport, follow_redirects=True)


@pytest.fixture
def mock_client():
    """Return a mock HTTPX client that returns a successful response with all cookies and headers."""
    mock_transport = httpx.MockTransport(mock_response)
    return httpx.Client(transport=mock_transport, follow_redirects=True)


def test_cli(mock_perfect_client, monkeypatch):
    """Test the CLI command with mocked HTTP client."""

    # Mock the SiteChecker to use our mock client
    def mock_site_checker_init(self, url: str, **_kwargs: object) -> None:
        self.url = httpx.URL(url)
        self.client = mock_perfect_client

    monkeypatch.setattr("djcheckup.checks.SiteChecker.__init__", mock_site_checker_init)

    runner = CliRunner()
    result = runner.invoke(app, [url])
    assert result.exit_code == 0
    assert "Can I connect to your site" in result.stdout
    assert "Connected to your site" in result.stdout
    assert "Skipped" not in result.stdout
    assert "Failed" not in result.stdout


def test_cli_with_failures(mock_client, monkeypatch):
    """Test the CLI command with mocked HTTP client."""

    # Mock the SiteChecker to use our mock client
    def mock_site_checker_init(self, url: str, **_kwargs: object) -> None:
        self.url = httpx.URL(url)
        self.client = mock_client
        self._client_provided = True

    monkeypatch.setattr("djcheckup.checks.SiteChecker.__init__", mock_site_checker_init)

    runner = CliRunner()
    result = runner.invoke(app, [url])
    output = result.stdout

    assert result.exit_code == 0
    assert "Can I connect to your site" in output
    assert "Connected to your site" in output
    assert "Success" in output
    assert "Skipped" in output
    assert "Failure" in output


def test_cli_json_output(mock_perfect_client, monkeypatch):
    """Test the CLI command with mocked HTTP client."""

    # Mock the SiteChecker to use our mock client
    def mock_site_checker_init(self, url: str, **_kwargs: object) -> None:
        self.url = httpx.URL(url)
        self.client = mock_perfect_client
        self._client_provided = True

    monkeypatch.setattr("djcheckup.checks.SiteChecker.__init__", mock_site_checker_init)

    runner = CliRunner()
    result = runner.invoke(app, [url, "--output-json"])
    assert result.exit_code == 0
    assert '"name": "Can I connect to your site?"' in result.stdout
    assert '"message": "Connected to your site successfully."' in result.stdout
    assert "Skipped" not in result.stdout
    assert "Failed" not in result.stdout


def test_run_checks_command(mock_perfect_client):
    """Test the run_checks command with mocked HTTP client."""
    result = run_checks(url, client=mock_perfect_client)
    assert isinstance(result, SiteCheckResult)


def test_run_checks_command_json(mock_perfect_client):
    """Test the run_checks command with mocked HTTP client."""
    result = run_checks(url, output_format="json", client=mock_perfect_client)
    assert isinstance(result, str)


def test_run_checks_command_unknown_output_format(mock_perfect_client):
    """Test the run_checks command with mocked HTTP client."""
    with pytest.raises(ValueError):
        run_checks(url, output_format="unknown", client=mock_perfect_client)  # type: ignore
