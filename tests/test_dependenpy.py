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

"""Tests for main features."""

from __future__ import annotations

import importlib
import io
import json
from typing import TYPE_CHECKING

import pytest

from dependenpy import Matrix, Module, Package, Scan, main

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    "args",
    [
        ["-l", "dependenpy"],
        ["-m", "dependenpy"],
        ["-t", "dependenpy"],
        ["dependenpy", "-d100"],
        ["dependenpy,internal,dependenpy"],
    ],
)
def test_main_ok(args: list[str]) -> None:
    """Main test method.

    Arguments:
        args: Command line arguments.
    """
    assert main(args) == 0


def test_main_not_ok() -> None:
    """Main test method."""
    assert main(["do not exist"]) == 1


def test_tree() -> None:
    """Test the built tree."""
    scan = Scan("internal")
    items = [
        "internal",
        "internal.subpackage_a",
        "internal.subpackage_a.subpackage_1",
        "internal.subpackage_a.subpackage_1.__init__",
        "internal.subpackage_a.subpackage_1.module_i",
        "internal.subpackage_a.__init__",
        "internal.subpackage_a.module_1",
        "internal.__init__",
        "internal.module_a",
    ]

    for item in items:
        assert scan.get(item)


def test_inner_imports() -> None:
    """Test inner imports."""
    scan = Scan("internal")
    module_i = scan["internal.subpackage_a.subpackage_1.module_i"]

    assert len(module_i.dependencies) == 4  # ty:ignore[unresolved-attribute]
    assert module_i.cardinal(to=scan["internal"]) == 3


def test_delayed_build() -> None:
    """Test delayed build."""
    scan = Scan("internal", build_tree=False)

    scan.build_tree()
    scan.build_dependencies()

    assert len(scan.submodules) == 6


def test_matrix_and_graph(tmp_path: Path) -> None:
    """Count directed imports and group them by package depth."""
    # Two imports point to the same module; one import is outside the package.
    package_path = tmp_path / "sample"
    package_path.mkdir()
    (package_path / "__init__.py").write_text("", encoding="utf-8")
    (package_path / "source.py").write_text(
        "from .target import first\nfrom .target import second\nimport outside\n",
        encoding="utf-8",
    )
    (package_path / "target.py").write_text("first = 1\nsecond = 2\n", encoding="utf-8")

    scan = Scan(str(package_path))
    data = scan.as_matrix()
    grouped = scan.as_matrix(depth=1)
    graph = scan.as_graph()

    # Rows import columns, and the external import does not enter the grid.
    assert isinstance(data, Matrix)
    assert data.keys == ["sample.__init__", "sample.source", "sample.target"]
    assert data.data == [[0, 0, 0], [0, 0, 2], [0, 0, 0]]
    assert data.total == 2
    assert grouped.keys == ["sample"]
    assert grouped.data == [[2]]
    assert scan.as_matrix() is data
    assert len(graph.edges) == 1
    edge = next(iter(graph.edges))

    assert edge.vertex_out is not None
    assert edge.vertex_in is not None
    assert (edge.vertex_out.name, edge.vertex_in.name, edge.weight) == ("sample.source", "sample.target", 2)

    # Children retain their parent scan for dependency resolution.
    package = scan["sample"]
    source = scan["sample.source"]

    assert scan.is_scan
    assert isinstance(package, Package)
    assert package.scan is scan
    assert not package.is_scan
    assert isinstance(source, Module)
    assert source.scan is scan
    assert not source.is_scan


@pytest.mark.parametrize("output_format", ["json", "csv", "text"])
def test_matrix_output(output_format: str) -> None:
    """Print dependency counts with row and column labels."""
    data = Matrix.cast(["source", "target"], [[0, 2], [0, 0]])
    output = io.StringIO()

    data.print(format=output_format, output=output)
    text = output.getvalue()

    if output_format == "json":
        assert json.loads(text) == {"keys": ["source", "target"], "data": [[0, 2], [0, 0]]}
    elif output_format == "csv":
        assert text == "module,\nsource,target\nsource,0,2\ntarget,0,0\n"
    else:
        assert "source" in text
        assert "target" in text
        assert "2" in text


def test_matrix_cast_copies_inputs() -> None:
    """Keep cast data independent of later changes to its inputs."""
    keys = ["source", "target"]
    counts = [[0, 2], [0, 0]]

    data = Matrix.cast(keys, counts)
    keys[0] = "changed"
    counts[0][1] = 99

    assert data.keys == ["source", "target"]
    assert data.data == [[0, 2], [0, 0]]


def test_deprecated_structures_import() -> None:
    """Resolve the legacy module import with a warning that identifies the public API."""
    module = importlib.import_module("dependenpy.structures")

    with pytest.warns(DeprecationWarning, match="Import from `dependenpy` directly") as warnings:
        legacy_class = module.Matrix

    assert legacy_class is Matrix
    assert warnings[0].filename == __file__
