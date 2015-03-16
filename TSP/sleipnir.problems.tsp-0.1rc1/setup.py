#!/usr/bin/env python
# -*- mode: Python; indent-tabs-mode: nil; coding: utf-8  -*-

#
# Copyright 2010, 2011 Carlos Martín
# Copyright 2010, 2011 Universidad de Salamanca
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""Main Setup File"""

import os
import re
import sys

if sys.version_info < (2, 6):
    sys.stderr.write("Sleipnir requires Python 2.6 or higher.")
    sys.exit(0)

# Add seleipnir namspace
sys.path.insert(0, 'src')

# setuptools build required.
from setuptools.dist import Distribution
from setuptools import setup, find_packages


# pylint: disable-msg=R0904
class Dist(Distribution):
    """
    Custom Distribution Class to force creation of namespace dirs
    """
    NAMESPACE = "sleipnir"

    @staticmethod
    def _create_template(package, where):
        """Build namespace __init__.py file at 'where' location"""

        namespace = os.path.join(where, 'src', package)
        if not os.path.exists(namespace):
            try:
                os.makedirs(namespace, 0755)
                # write init contents
                init = open(os.path.join(namespace, "__init__.py"), "w")
                init.write("import pkg_resources\n")
                init.write("pkg_resources.declare_namespace(__name__)\n")
                init.close()
            except OSError:
                pass

    def __init__(self, *args, **kwargs):
        self._create_template(self.NAMESPACE, os.path.dirname(__file__))
        Distribution.__init__(self, *args, **kwargs)

# Load constants
Dist(dict(setup_requires=['sleipnir.components']))
from tsp import constants

# Peek author details
AUTHOR, EMAIL = re.match(r'^(.*) <(.*)>$', constants.__author__).groups()

setup(
    author             = AUTHOR,
    author_email       = EMAIL,
    classifiers        = constants.__classifiers__,
    description        = constants.__summary__,
    install_requires   = constants.__requires__,
    license            = constants.__license__,
    long_description   = constants.__long_description__,
    name               = constants.__appname__,
    packages           = find_packages(exclude=['tests']),
    test_suite         = 'tests',
    tests_require      = constants.__tests_requires__,
    url                = constants.__url__,
    version            = constants.__version__,
    zip_safe           = False,
    entry_points = """
    [%s]
      problems.tsp.problem   = tsp.problems:TSP
      problems.tsp.interface = tsp.interfaces:ITSP
    """ % constants.__entry_point__,
)
