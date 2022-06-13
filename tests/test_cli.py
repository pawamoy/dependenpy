"""Tests for the `cli` module."""

import pytest

from dependenpy import cli


def test_main():
    """Basic CLI test."""
    with pytest.raises(SystemExit) as exit:  # noqa: PT012
        cli.main([])
        assert exit.code == 2


def test_show_help(capsys):
    """
    Show help.

    Arguments:
        capsys: Pytest fixture to capture output.
    """
    with pytest.raises(SystemExit):
        cli.main(["-h"])
    captured = capsys.readouterr()
    assert "dependenpy" in captured.out
