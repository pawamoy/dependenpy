# -*- coding: utf-8 -*-

"""
Dependenpy package.

With dependenpy you will be able to analyze the internal dependencies in
your Python code, i.e. which module needs which other module. You will then
be able to build a dependency matrix and use it for other purposes.
"""

from .dsm import DSM, Dependency, Module, Package
from .structures import Matrix, TreeMap

__all__ = ('DSM', 'Dependency', 'Matrix', 'Module', 'Package', 'TreeMap')
__version__ = '3.2.0'
