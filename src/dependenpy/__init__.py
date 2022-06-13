"""
Dependenpy package.

Show the inter-dependencies between modules of Python packages.

With dependenpy you will be able to analyze the internal dependencies in
your Python code, i.e. which module needs which other module. You will then
be able to build a dependency matrix and use it for other purposes.

If you read this message, you probably want to learn about the library and not the command-line tool:
please refer to the README.md included in this package to get the link to the official documentation.
"""

from __future__ import annotations

from dependenpy.dsm import DSM, Dependency, Module, Package
from dependenpy.structures import Matrix, TreeMap

__all__: list[str] = ["DSM", "Dependency", "Matrix", "Module", "Package", "TreeMap"]  # noqa: WPS410
__version__ = "3.3.0"  # noqa: WPS410
