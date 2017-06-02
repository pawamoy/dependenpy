# -*- coding: utf-8 -*-

"""dependenpy printer module."""

import sys

CSV = 'csv'
JSON = 'json'
TEXT = 'text'
FORMAT = (CSV, JSON, TEXT)


class PrintMixin(object):
    """Print mixin class."""

    def print(self, format=TEXT, output=sys.stdout, **kwargs):
        """
        Print the object in a file or on standard output by default.

        Args:
            format (str): output format (csv, json or text).
            output (file):
                descriptor to an opened file (default to standard output).
            **kwargs (): additional arguments.
        """
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
