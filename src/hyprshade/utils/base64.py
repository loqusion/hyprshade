from __future__ import annotations

from base64 import b64decode, b64encode
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from _typeshed import ReadableBuffer


ALTCHARS: Final[bytes] = b"-_"


def pathsafe_b64encode(path: str | ReadableBuffer) -> bytes:
    s = path.encode("utf-8") if isinstance(path, str) else path
    return b64encode(s, altchars=ALTCHARS).strip(b"=")


def pathsafe_b64decode(encoded_path: str | bytes) -> bytes:
    s = encoded_path.encode("utf-8") if isinstance(encoded_path, str) else encoded_path
    s += b"=" * (4 - len(s) % 4)
    return b64decode(s, altchars=ALTCHARS)
