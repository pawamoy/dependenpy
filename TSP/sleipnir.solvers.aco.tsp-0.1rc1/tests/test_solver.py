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

__all__ = ['TestSimpleAcoTSP', ]

# Submodule requirements
from sleipnir.heuristics.evaluators import Any
from sleipnir.heuristics.helpers.solver import SolverFactory
from sleipnir.heuristics.helpers.problem import ProblemFactory


#pylint: disable-msg=R0903,R0904
class TestSimpleAcoTSP(TestCaseLoader):
    """Check if helpers are operative"""

    def __init__(self, *args):
        super(TestSimpleAcoTSP, self).__init__(*args)
        self.counter = self.partial = None

    def test_solver_aco_tsp(self):
        """Check that Aco TSP is registered"""

        sol = SolverFactory(self._manager)
        aco = sol.create(size=1).pop()
        assert aco

    def test_solver_from_tsp(self):
        """
        Check that a solver can obtain a solution from a TSP
        object
        """
        def errback(error):
            """dummy error callback"""
            return False

        def callback(result, wrapper):
            """dummy callback"""
            if wrapper.total in self.stops:
                del self.stops[0]
            else:
                self.assertTrue(result[1] > self.result_len)
            if wrapper.state in ('finished',):
                problem = wrapper.problem
                self.assertTrue(len(self.stops) == 0)
                self.assertEqual(self.iterations, wrapper.total)
                self.result = result
                return result
            else:
                return None

        def callback2(result, wrapper):
            if wrapper.state in ('finished',):
                return result
            else:
                self.assertEqual(result, None)
                return result

        # start test
        self.result_len = 0
        self.percentage = 20
        self.iterations = 100
        self.stops = \
        range(0, self.iterations, self.iterations * self.percentage / 100)[1:]

        aco = SolverFactory(self._manager).create(size=1).pop()
        # aco args
        aco_kwargs = {
            'iters':   self.iterations,
            'partial': Any(
                [(self.iterations, str(self.percentage) + '%'),
                 'longest',
                 '1s',
                 ])
            }
        # register callbacks
        aco.register_errback(errback)
        aco.register_callback(callback)
        aco.register_callback(callback2)
        aco.register_inprogress(callback)
        aco.register_inprogress(callback2)

        for tsp_file in DATA().tsp:
            factory = ProblemFactory(self._manager)
            tso = factory.create(lambda x: x.query('ITSP')).pop()
            tso.load_from(where=tsp_file)  # Fixme: Replace by a Fake TSP
            tso.seed = 1
            aco.run(aco.prepare(tso, 'longest', **aco_kwargs))
            self.assertTrue(
                self.result in tso.get_solutions('longest', **aco_kwargs))


#pylint: disable-msg=C0103
main_suite = create_suite([TestSimpleAcoTSP, ])

if __name__ == '__main__':
    # pylint: disable-msg=E1120
    run_suite()
