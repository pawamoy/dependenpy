# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2020, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Dependenpy package.

Show the inter-dependencies between modules of Python packages.

With dependenpy you will be able to analyze the internal dependencies in
your Python code, i.e. which module needs which other module. You will then
be able to build a dependency matrix and use it for other purposes.

If you read this message, you probably want to learn about the library and not the command-line tool:
please refer to the README.md included in this package to get the link to the official documentation.
"""

from __future__ import annotations

from dependenpy._internal.cli import get_parser, main
from dependenpy._internal.dsm import DSM, Dependency, Module, Package
from dependenpy._internal.finder import Finder, InstalledPackageFinder, LocalPackageFinder, PackageFinder, PackageSpec
from dependenpy._internal.helpers import CSV, FORMAT, JSON, TEXT, PrintMixin, guess_depth
from dependenpy._internal.node import LeafNode, NodeMixin, RootNode
from dependenpy._internal.plugins import InternalDependencies
from dependenpy._internal.structures import Edge, Graph, Matrix, TreeMap, Vertex

__all__: list[str] = [
    "CSV",
    "DSM",
    "FORMAT",
    "JSON",
    "TEXT",
    "Dependency",
    "Edge",
    "Finder",
    "Graph",
    "InstalledPackageFinder",
    "InternalDependencies",
    "LeafNode",
    "LocalPackageFinder",
    "Matrix",
    "Module",
    "NodeMixin",
    "Package",
    "PackageFinder",
    "PackageSpec",
    "PrintMixin",
    "RootNode",
    "TreeMap",
    "Vertex",
    "get_parser",
    "guess_depth",
    "main",
]
