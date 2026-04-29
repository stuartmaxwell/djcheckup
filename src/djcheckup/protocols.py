"""Protocol definitions for djcheckup."""

from collections.abc import Mapping
from http.cookiejar import CookieJar
from typing import Any, Protocol


class UrlProtocol(Protocol):
    def __str__(self) -> str: ...

    @property
    def scheme(self) -> str: ...


class CookiesProtocol(Protocol):
    @property
    def jar(self) -> CookieJar: ...


class ResponseProtocol(Protocol):
    @property
    def status_code(self) -> int: ...

    @property
    def text(self) -> str: ...

    @property
    def url(self) -> UrlProtocol: ...

    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def cookies(self) -> CookiesProtocol: ...

    def raise_for_status(self) -> "ResponseProtocol": ...


class ClientProtocol(Protocol):
    def get(self, url: Any, *args: Any, **kwargs: Any) -> ResponseProtocol: ...

    def close(self) -> None: ...
