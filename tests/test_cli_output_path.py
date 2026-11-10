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

"""Tests for unwritable CLI output paths."""

from __future__ import annotations

import pytest

from dependenpy import main


def test_unwritable_output_path_is_a_clean_error(tmp_path: pytest.TempPath, capsys: pytest.CaptureFixture) -> None:
    """An `-o` path in a missing directory must be a clean error, not a traceback.

    Parameters:
        tmp_path: Pytest fixture for a temporary directory.
        capsys: Pytest fixture to capture output.
    """
    pkg = tmp_path / "mypkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "mod.py").write_text("import os\n")
    missing = tmp_path / "no-such-dir" / "out.txt"
    rc = main(["-o", str(missing), str(pkg)])
    assert rc == 2
    captured = capsys.readouterr()
    assert "Traceback" not in captured.err
    assert "out.txt" in captured.err
    assert not missing.parent.exists()
