"""Requests test helpers."""

from collections.abc import Callable, Iterable, Mapping
from http.cookies import SimpleCookie

import requests
from requests.adapters import BaseAdapter
from requests.cookies import RequestsCookieJar, create_cookie
from requests.models import PreparedRequest, Response
from requests.structures import CaseInsensitiveDict

ResponseHandler = Callable[[PreparedRequest], Response]
Headers = Mapping[str, str] | Iterable[tuple[str, str]]


class MockAdapter(BaseAdapter):
    """Route Requests traffic to an in-process response handler."""

    def __init__(self, handler: ResponseHandler) -> None:
        """Initialize the adapter with its response handler."""
        self.handler = handler
        self.closed = False
        self.last_timeout: float | tuple[float, float] | tuple[float, None] | None = None
        self.last_verify: bool | str = True

    def send(  # noqa: PLR0913, PLR0917
        self,
        request: PreparedRequest,
        stream: bool = False,  # noqa: FBT001, FBT002
        timeout: float | tuple[float, float] | tuple[float, None] | None = None,
        verify: bool | str = True,  # noqa: FBT001, FBT002
        cert: bytes | str | tuple[bytes | str, bytes | str] | None = None,
        proxies: Mapping[str, str] | None = None,
    ) -> Response:
        """Return the response produced by the configured handler."""
        self.last_timeout = timeout
        self.last_verify = verify
        response = self.handler(request)
        response.request = request
        assert request.url is not None
        response.url = request.url
        return response

    def close(self) -> None:
        """Mark this adapter as closed."""
        self.closed = True


def create_mock_client(handler: ResponseHandler) -> requests.Session:
    """Create a Requests session backed by a mock adapter."""
    session = requests.Session()
    adapter = MockAdapter(handler)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def create_response(
    request: PreparedRequest,
    *,
    status_code: int,
    headers: Headers | None = None,
    content: str = "",
) -> Response:
    """Build a Requests response, including cookies from Set-Cookie headers."""
    header_items = list(headers.items() if isinstance(headers, Mapping) else headers or [])
    response = Response()
    response.status_code = status_code
    response.headers = CaseInsensitiveDict(header_items)
    response._content = content.encode()
    response.encoding = "utf-8"
    response.request = request
    assert request.url is not None
    response.url = request.url
    response.cookies = _cookies_from_headers(header_items)
    return response


def _cookies_from_headers(headers: Iterable[tuple[str, str]]) -> RequestsCookieJar:
    jar = RequestsCookieJar()

    for name, value in headers:
        if name.lower() != "set-cookie":
            continue

        parsed_cookie = SimpleCookie()
        parsed_cookie.load(value)

        for morsel in parsed_cookie.values():
            rest: dict[str, str | None] = {}
            if morsel["httponly"]:
                rest["HttpOnly"] = None
            if morsel["samesite"]:
                rest["SameSite"] = morsel["samesite"]

            jar.set_cookie(
                create_cookie(
                    name=morsel.key,
                    value=morsel.value,
                    path=morsel["path"] or "/",
                    secure=bool(morsel["secure"]),
                    rest=rest,
                ),
            )

    return jar
