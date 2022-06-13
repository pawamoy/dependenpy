"""dependenpy printer module."""

from __future__ import annotations

import sys
from typing import IO, Any

CSV = "csv"
JSON = "json"
TEXT = "text"
FORMAT = (CSV, JSON, TEXT)


class PrintMixin(object):
    """Print mixin class."""

    def print(self, format: str | None = TEXT, output: IO = sys.stdout, **kwargs: Any):  # noqa: A002,A003
        """
        Print the object in a file or on standard output by default.

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

    def _to_text(self, **kwargs):
        raise NotImplementedError

    def _to_csv(self, **kwargs):
        raise NotImplementedError

    def _to_json(self, **kwargs):
        raise NotImplementedError


def guess_depth(packages: list[str]) -> int:
    """
    Guess the optimal depth to use for the given list of arguments.

    Args:
        packages: List of packages.

    Returns:
        Guessed depth to use.
    """
    if len(packages) == 1:
        return packages[0].count(".") + 2
    return min(package.count(".") for package in packages) + 1
