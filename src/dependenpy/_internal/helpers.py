from __future__ import annotations

import sys
from typing import IO, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence


CSV = "csv"
"""CSV format."""
JSON = "json"
"""JSON format."""
TEXT = "text"
"""Plain text format."""
FORMAT = (CSV, JSON, TEXT)
"""Supported output formats."""


class PrintMixin:
    """Print mixin class."""

    def print(self, format: str | None = TEXT, output: IO = sys.stdout, **kwargs: Any) -> None:  # noqa: A002
        """Print the object in a file or on standard output by default.

        Args:
            format: output format (csv, json or text).
            output: descriptor to an opened file (default to standard output).
            **kwargs: additional arguments.
        """
        if format is None:
            format = TEXT

        if format != TEXT:
            kwargs.pop("zero", "")

        if format == TEXT:
            print(self._to_text(**kwargs), file=output)
        elif format == CSV:
            print(self._to_csv(**kwargs), file=output)
        elif format == JSON:
            print(self._to_json(**kwargs), file=output)

    def _to_text(self, **kwargs: Any) -> str:
        raise NotImplementedError

    def _to_csv(self, **kwargs: Any) -> str:
        raise NotImplementedError

    def _to_json(self, **kwargs: Any) -> str:
        raise NotImplementedError


def guess_depth(packages: Sequence[str]) -> int:
    """Guess the optimal depth to use for the given list of arguments.

    Args:
        packages: List of packages.

    Returns:
        Guessed depth to use.
    """
    if len(packages) == 1:
        return packages[0].count(".") + 2
    return min(package.count(".") for package in packages) + 1
