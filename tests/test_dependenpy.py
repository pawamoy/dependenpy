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

import pytest

from dependenpy._internal.cli import main
from dependenpy._internal.dsm import DSM


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
    dsm = DSM("internal")
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
        assert dsm.get(item)


def test_inner_imports() -> None:
    """Test inner imports."""
    dsm = DSM("internal")
    module_i = dsm["internal.subpackage_a.subpackage_1.module_i"]
    assert len(module_i.dependencies) == 4  # ty:ignore[unresolved-attribute]
    assert module_i.cardinal(to=dsm["internal"]) == 3


def test_delayed_build() -> None:
    """Test delayed build."""
    dsm = DSM("internal", build_tree=False)
    dsm.build_tree()
    dsm.build_dependencies()
    assert len(dsm.submodules) == 6
