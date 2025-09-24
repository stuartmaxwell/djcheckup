"""Test the different types of checks."""

import httpx
import pytest

from src.djcheckup.checks import HeaderCheck, SeverityWeight, create_context

url = "https://example.com"


def mock_response(request: httpx.Request) -> httpx.Response:
    """Return a fake response for any request."""
    headers = [
        ("test-header-name", "test-header-value"),
        ("Set-Cookie", "test-simple-cookie1=test-val1; Path=/"),
        ("Set-Cookie", "test-complex-cookie2=test-val2; Path=/; HttpOnly; Secure; SameSite=Strict"),
    ]
    return httpx.Response(
        status_code=200,
        headers=dict(headers),
        content="Test response content.",
    )


@pytest.fixture
def mock_client():
    """Return a mock HTTP client."""
    mock_transport = httpx.MockTransport(mock_response)
    return httpx.Client(transport=mock_transport)


@pytest.fixture
def context(mock_client):
    """Create a SiteCheckContext context object."""
    response = mock_client.get(url)
    return create_context(url=httpx.URL(url), client=mock_client, response=response)


def test_header_check(context):
    """Test the header check where the header exists."""
    test_header_check = HeaderCheck(
        check_id="test_header_check",
        name="Test Header Check",
        header_name="test-header-name",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert test_header_check.check(context) is True


def test_header_check_fail(context):
    """Test the header check where the header does not exist."""
    test_header_check_fail = HeaderCheck(
        check_id="test_header_check",
        name="Test Header Check",
        header_name="missing-header-name",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert test_header_check_fail.check(context) is False


def test_header_value_check(context):
    """Test the header value check where the header and value matches."""
    test_header_value_check = HeaderCheck(
        check_id="test_header_check",
        name="Test Header Check",
        header_name="test-header-name",
        header_value="test-header-value",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert test_header_value_check.check(context) is True


def test_header_value_check_fail(context):
    """Test the header value check where the header exists but has the wrong value."""
    test_header_value_check_fail = HeaderCheck(
        check_id="test_header_check",
        name="Test Header Check",
        header_name="test-header-name",
        header_value="incorrect-value",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert test_header_value_check_fail.check(context) is False


def test_header_value_check_missing_header(context):
    """Test the header value check where the header does not exist but the value is correct."""
    test_header_value_check_fail = HeaderCheck(
        check_id="test_header_check",
        name="Test Header Check",
        header_name="missing-header-name",
        header_value="test-header-value",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert test_header_value_check_fail.check(context) is False
