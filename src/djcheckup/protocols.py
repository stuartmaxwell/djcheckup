"""Protocol definitions for djcheckup."""

from collections.abc import Mapping
from http.cookiejar import CookieJar
from typing import Any, Protocol


class ResponseProtocol(Protocol):
    @property
    def status_code(self) -> int: ...

    @property
    def text(self) -> str: ...

    @property
    def url(self) -> str: ...

    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def cookies(self) -> CookieJar: ...

    def raise_for_status(self) -> None: ...


class ClientProtocol(Protocol):
    def get(self, url: Any, *args: Any, **kwargs: Any) -> ResponseProtocol: ...

    def close(self) -> None: ...
