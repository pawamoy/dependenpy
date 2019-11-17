import pytest

from dependenpy import cli


def test_main():
    with pytest.raises(SystemExit) as exit:
        cli.main([])
        assert exit.code == 2
