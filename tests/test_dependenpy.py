# -*- coding: utf-8 -*-

"""Main test script."""

from dependenpy.cli import main
from dependenpy.dsm import DSM, Dependency, Module, Package


def test_main():
    """Main test method."""
    main(['-lm', 'dependenpy'])


def test_tree():
    dsm = DSM('internal')


def test_inner_imports():
    dsm = DSM('internal')
    dsm.build_dependencies()
    module_i = dsm.packages
