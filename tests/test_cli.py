"""Tests for the CLI."""

from __future__ import annotations

import pytest

from dependenpy import main
from dependenpy._internal import debug


def test_main() -> None:
    """Basic CLI test."""
    with pytest.raises(SystemExit) as exit:  # noqa: PT012
        main([])
        assert exit.code == 2  # type: ignore[attr-defined]


def test_show_help(capsys: pytest.CaptureFixture) -> None:
    """Show help.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        main(["-h"])
    captured = capsys.readouterr()
    assert "dependenpy" in captured.out


def test_show_version(capsys: pytest.CaptureFixture) -> None:
    """Show version.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        main(["-v"])
    captured = capsys.readouterr()
    assert debug._get_version() in captured.out


def test_show_debug_info(capsys: pytest.CaptureFixture) -> None:
    """Show debug information.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        main(["--debug-info"])
    captured = capsys.readouterr().out.lower()
    assert "python" in captured
    assert "system" in captured
    assert "environment" in captured
    assert "packages" in captured
