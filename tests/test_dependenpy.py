"""Tests for main features."""

import pytest

from dependenpy.cli import main
from dependenpy.dsm import DSM


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
def test_main_ok(args):
    """
    Main test method.

    Arguments:
        args: Command line arguments.
    """
    assert main(args) == 0


def test_main_not_ok():
    """Main test method."""
    assert main(["do not exist"]) == 1


def test_tree():
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


def test_inner_imports():
    """Test inner imports."""
    dsm = DSM("internal")
    module_i = dsm["internal.subpackage_a.subpackage_1.module_i"]
    assert len(module_i.dependencies) == 4
    assert module_i.cardinal(to=dsm["internal"]) == 3


def test_delayed_build():
    """Test delayed build."""
    dsm = DSM("internal", build_tree=False)
    dsm.build_tree()
    dsm.build_dependencies()
    assert len(dsm.submodules) == 6
