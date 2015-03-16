#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Sleipnir TSP Solver Plugin constants"""

from __future__ import absolute_import

__author__           = 'Carlos Martín <cmartin@liberalia.net>'
__version__          = '0.1rc1'
__date__             = '2011-01-04'
__license__          = 'GNU General Public License, version 2'

__namespace__        = "sleipnir"
__modname__          = "aco_tsp"
__family__           = "solvers"
__appname__          = __namespace__ + '.' + __family__ + '.aco.tsp'
__title__            = 'TSP Solver Plugin'
__release__          = '1'
__summary__          = 'A TSP Solver'
__url__              = 'http://sleipnir.liberalia.net/'
__copyright__        = '© 2010, 2011 Carlos Martín'

__classifiers__      = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development',
    ]

__long_description__ = """\
Add Here a a description to this package
"""

__requires__       = [
    __namespace__ + '.components      >= 0.1rc3',
    __namespace__ + '.core            >= 0.1rc2',
    __namespace__ + '.heuristics      >= 0.1rc2',
    __namespace__ + '.problems.tsp    >= 0.1rc1',
    ]
__tests_requires__ = [
    __namespace__ + '.components      >= 0.1rc3',
    __namespace__ + '.core            >= 0.1rc2',
    __namespace__ + '.heuristics      >= 0.1rc2',
    __namespace__ + '.marshals.tsplib >= 0.1rc1',
    __namespace__ + '.problems.tsp    >= 0.1rc1',  
    __namespace__ + '.testing         >= 0.1rc6',
    ]


def __get_entry_point():
    """Get Sleipnir.Components defined Entry Point"""
    from sleipnir.components import constants
    return constants.__entry_point__

__entry_point__ = __get_entry_point()
