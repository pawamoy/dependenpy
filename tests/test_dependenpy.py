# -*- coding: utf-8 -*-

"""Main test script."""

from dependenpy.cli import main
from dependenpy.dsm import DSM, Dependency, Module, Package


def test_main():
    """Main test method."""
    assert main(['-l', 'dependenpy']) == 0
    assert main(['-m', 'dependenpy']) == 0
    assert main(['-t', 'dependenpy']) == 0
    assert main(['dependenpy', '-d100']) == 0
    assert main(['do not exist']) == 1
    assert main(['dependenpy,internal,dependenpy']) == 0


def test_package_spec():
    pass


def test_tree():
    dsm = DSM('internal')
    assert dsm.get('internal')
    assert dsm.get('internal.subpackage_a')
    assert dsm.get('internal.subpackage_a.subpackage_1')
    assert dsm.get('internal.subpackage_a.subpackage_1.__init__')
    assert dsm.get('internal.subpackage_a.subpackage_1.module_i')
    assert dsm.get('internal.subpackage_a.__init__')
    assert dsm.get('internal.subpackage_a.module_1')
    assert dsm.get('internal.__init__')
    assert dsm.get('internal.module_a')


def test_inner_imports():
    dsm = DSM('internal')
    module_i = dsm['internal.subpackage_a.subpackage_1.module_i']
    assert len(module_i.dependencies) == 4
    assert module_i.cardinal(to=dsm['internal']) == 3


def test_delayed_build():
    dsm = DSM('internal', build_tree=False)
    dsm.build_tree()
    dsm.build_dependencies()
    assert len(dsm.submodules) == 6
