"""Tests for the `cli` module."""

from __future__ import annotations

import pytest

from dependenpy import cli


def test_main() -> None:
    """Basic CLI test."""
    with pytest.raises(SystemExit) as exit:  # noqa: PT012
        cli.main([])
        assert exit.code == 2


def test_show_help(capsys: pytest.CaptureFixture) -> None:
    """Show help.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["-h"])
    captured = capsys.readouterr()
    assert "dependenpy" in captured.out
