"""math utilities."""


def ceil_to_kib(int_: int) -> int:
    """Return the ceiling of an integer to the nearest kibibyte."""
    return int_ - int_ % -1024
