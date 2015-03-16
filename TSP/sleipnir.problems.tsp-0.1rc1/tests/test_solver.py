#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Test classes for sleipnir.plugins.solvers"""

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here required modules
from functools import partial

# Testing requiements
from sleipnir.testing.data import DATA
from sleipnir.testing.components import TestCaseLoader
from sleipnir.testing.test import create_suite, run_suite

__all__ = ['TestTSP', ]

# Test requirements
from sleipnir.heuristics.evaluators import Any
from sleipnir.heuristics.interfaces.solver import ISolver
from sleipnir.heuristics.helpers.solver import SolverFactory
from sleipnir.heuristics.helpers.problem import ProblemFactory


#pylint: disable-msg=R0903,R0904
class TestTSP(TestCaseLoader):
    """Check if helpers are operative"""

    def __init__(self, *args):
        super(TestTSP, self).__init__(*args)

    def test_dummy(self):
        """Dummy test"""
        self.assertTrue


def additional_tests():
    """Returns aditional tests"""
    return create_suite([TestTSP, ])

#pylint: disable-msg=C0103
main_suite = additional_tests()

if __name__ == '__main__':
    #pylint: disable-msg=E1120
    run_suite()
