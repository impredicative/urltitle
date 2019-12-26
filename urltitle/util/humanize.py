"""humanize utilities."""
from typing import Optional

from humanize import naturalsize


def _humanize_bytes(num_bytes: int) -> str:
    return naturalsize(num_bytes, gnu=True, format="%.0f")


def humanize_bytes(num_bytes: Optional[int]) -> Optional[str]:
    """Return an optional number of bytes as a humanized string."""
    return _humanize_bytes(num_bytes) if num_bytes is not None else None


def humanize_len(text: bytes) -> str:
    """Return the length of a bytes object as a humanized string."""
    return _humanize_bytes(len(text))
