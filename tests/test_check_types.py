"""Test the different types of checks."""

import httpx
import pytest

from djcheckup.checks import (
    CheckResult,
    ContentCheck,
    CookieCheck,
    CookieHttpOnlyCheck,
    CookieSameSiteCheck,
    CookieSecureCheck,
    HeaderCheck,
    PathCheck,
    SchemeCheck,
    SeverityWeight,
    create_context,
)

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
        headers=headers,
        content="Test response content.",
    )


def mock_response_404(request: httpx.Request) -> httpx.Response:
    """Return a fake response for any request."""
    return httpx.Response(
        status_code=404,
        content="Page not found.",
    )


def mock_response_redirect_to_https(request: httpx.Request) -> httpx.Response:
    """Return a fake response for any request."""
    if request.url.scheme == "http":
        return httpx.Response(
            status_code=301,
            headers={"Location": str(request.url.copy_with(scheme="https"))},
            request=request,
        )
    return httpx.Response(
        status_code=200,
        content="Test response content.",
    )


def mock_empty_response(request: httpx.Request) -> httpx.Response:
    """Return a fake response with no content."""
    return httpx.Response(
        status_code=200,
        content="",
    )


@pytest.fixture
def mock_client():
    """Return a mock HTTP client."""
    mock_transport = httpx.MockTransport(mock_response)
    return httpx.Client(transport=mock_transport)


@pytest.fixture
def mock_client_404():
    """Return a mock HTTP client."""
    mock_transport = httpx.MockTransport(mock_response_404)
    return httpx.Client(transport=mock_transport)


@pytest.fixture
def mock_client_redirect():
    """Return a mock HTTP client."""
    mock_transport = httpx.MockTransport(mock_response_redirect_to_https)
    return httpx.Client(transport=mock_transport, follow_redirects=True)


@pytest.fixture
def mock_client_empty():
    """Return a mock HTTP client."""
    mock_transport = httpx.MockTransport(mock_empty_response)
    return httpx.Client(transport=mock_transport)


@pytest.fixture
def context(mock_client):
    """Create a SiteCheckContext context object."""
    response = mock_client.get(url)
    return create_context(url=httpx.URL(url), client=mock_client, response=response)


@pytest.fixture
def context_404(mock_client_404):
    """Create a SiteCheckContext context object."""
    response = mock_client_404.get(url)
    return create_context(url=httpx.URL(url), client=mock_client_404, response=response)


@pytest.fixture
def context_redirect(mock_client_redirect):
    """Create a SiteCheckContext context object."""
    response = mock_client_redirect.get(url)
    return create_context(url=httpx.URL(url), client=mock_client_redirect, response=response)


@pytest.fixture
def context_empty(mock_client_empty):
    """Create a SiteCheckContext context object."""
    response = mock_client_empty.get(url)
    return create_context(url=httpx.URL(url), client=mock_client_empty, response=response)


def test_content_check(context):
    """Test the content check where the content exists."""
    content_check = ContentCheck(
        check_id="content_check",
        name="Test Content Check",
        content="Test response content",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert content_check.check(context) is True


def test_content_check_empty(context_empty):
    """Test the content check where the content is empty."""
    content_check = ContentCheck(
        check_id="content_check",
        name="Test Content Check",
        content="Test response content",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert content_check.check(context_empty) is False


def test_content_check_fail(context):
    """Test the content check where the content does not exist."""
    content_check_fail = ContentCheck(
        check_id="content_check_fail",
        name="Test Content Check",
        content="missing content",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert content_check_fail.check(context) is False


def test_content_check_path(context):
    """Test the content check where the content exists."""
    content_check_path = ContentCheck(
        check_id="content_check_path",
        name="Test Content Check",
        content="Test response content",
        path="/test",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert content_check_path.check(context) is True


def test_content_check_path_fail(context):
    """Test the content check where the content exists."""
    content_check_path_fail = ContentCheck(
        check_id="content_check_path_fail",
        name="Test Content Check",
        content="missing content",
        path="/test",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert content_check_path_fail.check(context) is False


def test_cookie_check(context):
    """Test the cookie check where the cookie exists."""
    cookie_check = CookieCheck(
        check_id="cookie_check",
        name="Test Cookie Check",
        cookie_name="test-simple-cookie1",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_check.check(context) is True


def test_cookie_check_empty(context_empty):
    """Test the cookie check where there are no cookies."""
    cookie_check = CookieCheck(
        check_id="cookie_check",
        name="Test Cookie Check",
        cookie_name="test-simple-cookie1",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_check.check(context_empty) is False


def test_cookie_check_fail(context):
    """Test the cookie check where the cookie does not exist."""
    cookie_check_fail = CookieCheck(
        check_id="cookie_check_fail",
        name="Test Cookie Check",
        cookie_name="missing-cookie",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_check_fail.check(context) is False


def test_cookie_value_check(context):
    """Test the cookie check where the cookie and value matches."""
    cookie_value_check = CookieCheck(
        check_id="cookie_value_check",
        name="Test Cookie Check",
        cookie_name="test-simple-cookie1",
        cookie_value="test-val1",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_value_check.check(context) is True


def test_cookie_value_check_fail(context):
    """Test the cookie check where the cookie exists but has the wrong value."""
    cookie_value_check_fail = CookieCheck(
        check_id="cookie_value_check_fail",
        name="Test Cookie Check",
        cookie_name="test-simple-cookie1",
        cookie_value="wrong-value",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_value_check_fail.check(context) is False


def test_cookie_value_check_missing_cookie(context):
    """Test the cookie check where the cookie does not exist but has the wrong value."""
    cookie_value_check_missing_cookie = CookieCheck(
        check_id="cookie_value_check_missing_cookie",
        name="Test Cookie Check",
        cookie_name="missing-cookie",
        cookie_value="test-val1",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_value_check_missing_cookie.check(context) is False


def test_cookie_httponly_check(context):
    """Test the cookie HttpOnly check where the cookie is marked as HttpOnly."""
    cookie_httponly_check = CookieHttpOnlyCheck(
        check_id="cookie_httponly_check",
        name="Test Cookie HttpOnly Check",
        cookie_name="test-complex-cookie2",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_httponly_check.check(context) is True


def test_cookie_httponly_check_depends_on(context):
    """Test the cookie HttpOnly check where the depends on a test that hasn't run."""
    cookie_httponly_check = CookieHttpOnlyCheck(
        check_id="cookie_httponly_check",
        depends_on="cookie_check",
        name="Test Cookie HttpOnly Check",
        cookie_name="test-complex-cookie2",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    check_result = cookie_httponly_check.run(context, previous_results={})
    assert check_result.result.value == CheckResult.SKIPPED.value


def test_cookie_httponly_check_empty(context_empty):
    """Test the cookie HttpOnly check where there are no cookies."""
    cookie_httponly_check = CookieHttpOnlyCheck(
        check_id="cookie_httponly_check",
        name="Test Cookie HttpOnly Check",
        cookie_name="test-complex-cookie2",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_httponly_check.check(context_empty) is False


def test_cookie_httponly_check_fail(context):
    """Test the cookie HttpOnly check where the cookie is not marked as HttpOnly."""
    cookie_httponly_check_fail = CookieHttpOnlyCheck(
        check_id="cookie_httponly_check_fail",
        name="Test Cookie HttpOnly Check",
        cookie_name="test-simple-cookie1",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_httponly_check_fail.check(context) is False


def test_cookie_httponly_check_missing_cookie(context):
    """Test the cookie HttpOnly check where the cookie does not exist."""
    cookie_httponly_check_missing_cookie = CookieHttpOnlyCheck(
        check_id="cookie_httponly_check_missing_cookie",
        name="Test Cookie HttpOnly Check",
        cookie_name="missing-cookie",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_httponly_check_missing_cookie.check(context) is False


def test_cookie_samesite_strict_check(context):
    """Test the cookie SameSite check where the cookie is marked as SameSite=Strict."""
    cookie_samesite_strict_check = CookieSameSiteCheck(
        check_id="cookie_samesite_strict_check",
        name="Test Cookie SameSite Check",
        cookie_name="test-complex-cookie2",
        samesite_value="Strict",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_samesite_strict_check.check(context) is True


def test_cookie_samesite_strict_check_empty(context_empty):
    """Test the cookie SameSite check where the cookie is marked as SameSite=Strict."""
    cookie_samesite_strict_check = CookieSameSiteCheck(
        check_id="cookie_samesite_strict_check",
        name="Test Cookie SameSite Check",
        cookie_name="test-complex-cookie2",
        samesite_value="Strict",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_samesite_strict_check.check(context_empty) is False


def test_cookie_samesite_lax_check_fail(context):
    """Test the cookie SameSite check where the cookie is marked as SameSite=Lax."""
    cookie_samesite_lax_check_fail = CookieSameSiteCheck(
        check_id="cookie_samesite_lax_check_fail",
        name="Test Cookie SameSite Check",
        cookie_name="test-complex-cookie2",
        samesite_value="Lax",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_samesite_lax_check_fail.check(context) is False


def test_cookie_samesite_none_check_fail(context):
    """Test the cookie SameSite check where the cookie is marked as SameSite=Lax."""
    cookie_samesite_lax_check_fail = CookieSameSiteCheck(
        check_id="cookie_samesite_lax_check_fail",
        name="Test Cookie SameSite Check",
        cookie_name="test-complex-cookie2",
        samesite_value="None",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_samesite_lax_check_fail.check(context) is False


def test_cookie_samesite_check_fail_no_samesite(context):
    """Test the cookie SameSite check where the cookie has no SameSite attribute."""
    cookie_samesite_lax_check_fail = CookieSameSiteCheck(
        check_id="cookie_samesite_lax_check_fail",
        name="Test Cookie SameSite Check",
        cookie_name="test-simple-cookie1",
        samesite_value="None",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_samesite_lax_check_fail.check(context) is False


def test_cookie_samesite_check_fail_missing_cookie(context):
    """Test the cookie SameSite check where the cookie is missing."""
    cookie_samesite_check_fail_missing_cookie = CookieSameSiteCheck(
        check_id="cookie_samesite_check_fail_missing_cookie",
        name="Test Cookie SameSite Check",
        cookie_name="missing-cookie",
        samesite_value="None",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_samesite_check_fail_missing_cookie.check(context) is False


def test_cookie_secure_check(context):
    """Test the cookie Secure check where the cookie is marked as Secure."""
    cookie_secure_check = CookieSecureCheck(
        check_id="cookie_secure_check",
        name="Test Cookie Secure Check",
        cookie_name="test-complex-cookie2",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_secure_check.check(context) is True


def test_cookie_secure_check_empty(context_empty):
    """Test the cookie Secure check where the cookie is marked as Secure."""
    cookie_secure_check = CookieSecureCheck(
        check_id="cookie_secure_check",
        name="Test Cookie Secure Check",
        cookie_name="test-complex-cookie2",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_secure_check.check(context_empty) is False


def test_cookie_secure_check_fail(context):
    """Test the cookie Secure check where the cookie is not marked as Secure."""
    cookie_secure_check_fail = CookieSecureCheck(
        check_id="cookie_secure_check_fail",
        name="Test Cookie Secure Check",
        cookie_name="test-simple-cookie1",
        success=False,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_secure_check_fail.check(context) is False


def test_cookie_secure_check_fail_missing_cookie(context):
    """Test the cookie Secure check where the cookie is missing."""
    cookie_secure_check_fail_missing_cookie = CookieSecureCheck(
        check_id="cookie_secure_check_fail_missing_cookie",
        name="Test Cookie Secure Check",
        cookie_name="missing-cookie",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert cookie_secure_check_fail_missing_cookie.check(context) is False


def test_header_check(context):
    """Test the header check where the header exists."""
    header_check = HeaderCheck(
        check_id="header_check",
        name="Test Header Check",
        header_name="test-header-name",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert header_check.check(context) is True


def test_header_check_fail(context):
    """Test the header check where the header does not exist."""
    header_check_fail = HeaderCheck(
        check_id="header_check_fail",
        name="Test Header Check",
        header_name="missing-header-name",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert header_check_fail.check(context) is False


def test_header_value_check(context):
    """Test the header value check where the header and value matches."""
    header_value_check = HeaderCheck(
        check_id="header_value_check",
        name="Test Header Check",
        header_name="test-header-name",
        header_value="test-header-value",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert header_value_check.check(context) is True


def test_header_value_check_fail(context):
    """Test the header value check where the header exists but has the wrong value."""
    header_value_check_fail = HeaderCheck(
        check_id="header_value_check_fail",
        name="Test Header Check",
        header_name="test-header-name",
        header_value="incorrect-value",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert header_value_check_fail.check(context) is False


def test_header_value_check_missing_header(context):
    """Test the header value check where the header does not exist but the value is correct."""
    header_value_check_missing_header = HeaderCheck(
        check_id="header_value_check_missing_header",
        name="Test Header Check",
        header_name="missing-header-name",
        header_value="test-header-value",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert header_value_check_missing_header.check(context) is False


def test_path_check(context):
    """Test the path check where the response is 200."""
    path_check = PathCheck(
        check_id="path_check",
        name="Test Path Check",
        path="/test/path",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert path_check.check(context) is True


def test_path_check_fail(context):
    """Test the path check where the response is 200 but checking for 404."""
    path_check_fail = PathCheck(
        check_id="path_check_fail",
        name="Test Path Check",
        path="/test/path",
        status_code=404,
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert path_check_fail.check(context) is False


def test_path_check_404(context_404):
    """Test the path check where the response is 404."""
    path_check_404 = PathCheck(
        check_id="path_check_404",
        name="Test Path Check",
        path="/test/path",
        status_code=404,
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert path_check_404.check(context_404) is True


def test_path_check_404_fail(context_404):
    """Test the path check where the response is 404 but no status code is provided (i.e. 200)."""
    path_check_404_fail = PathCheck(
        check_id="path_check_404_fail",
        name="Test Path Check",
        path="/test/path",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert path_check_404_fail.check(context_404) is False


def test_scheme_check(context):
    """Test the scheme check where the start and end scheme is https."""
    scheme_check = SchemeCheck(
        check_id="scheme_check",
        name="Test Scheme Check",
        start_scheme="https",
        end_scheme="https",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert scheme_check.check(context) is True


def test_scheme_check_http(context):
    """Test the scheme check where the start and end scheme is https."""
    scheme_check = SchemeCheck(
        check_id="scheme_check",
        name="Test Scheme Check",
        start_scheme="http",
        end_scheme="http",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert scheme_check.check(context) is True


def test_scheme_check_fail_https_http(context_redirect):
    """Test the scheme check where the start scheme is https and end scheme is http."""
    scheme_check_fail_https_http = SchemeCheck(
        check_id="scheme_check_fail_https_http",
        name="Test Scheme Check",
        start_scheme="https",
        end_scheme="http",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert scheme_check_fail_https_http.check(context_redirect) is False


def test_scheme_check_fail_http_https(context_redirect):
    """Test the scheme check where the start scheme is http and end scheme is https."""
    scheme_check_fail_http_https = SchemeCheck(
        check_id="scheme_check_fail_http_https",
        name="Test Scheme Check",
        start_scheme="http",
        end_scheme="https",
        success=True,
        severity=SeverityWeight.MEDIUM,
        success_message="Test success message",
        failure_message="""Test failure message""",
    )

    assert scheme_check_fail_http_https.check(context_redirect) is True
