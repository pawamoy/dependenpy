#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""A simple solver for TSP problems with ACO metaheuristic"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Add here required modules
from functools import partial

# Sleipnir dependences
from sleipnir.heuristics.interfaces import solver
from sleipnir.core.thread import Task
from sleipnir.components.components import implements, Component

__all__ = ['Solver']

# Local dependences
from .ants import shortest, longest


#pylint: disable-msg=R0201
class Solver(Component):
    """
    A Solver for TSP problems following ACO metaheruistic
    """
    implements(solver.ISolver)

    def __init__(self):
        super(Solver, self).__init__()
        self._callbacks = {
            'callback'  : [],  # called when algorithm is finished
            'errback'   : [],  # called when an error occurs
            'inprogress': [],  # called when partial is defined
            'cleanup':    [],  # code to be executed at cleanup
            }

    def __getattr__(self, name):
        try:
            opr, cb_type = name.split('_')[:2]
            # pylint: disable-msg=W0108
            if cb_type in self._callbacks:
                if opr in ('prepend',):
                    return lambda x: self._callbacks[cb_type].insert(0, x)
                if opr in ('append', 'register',):
                    return lambda x: self._callbacks[cb_type].append(x)
                if opr in ('remove', 'unregister',):
                    return lambda x: self._callbacks[cb_type].remove(x)
        except (ValueError, IndexError,):
            pass
        raise AttributeError(
            "'%s' instance has no attribute '%s'" %
            (self.__class__.__name__, name, ))

    #pylint: disable-msg=W0142
    def prepare(self, problem, solution=None, **kwargs):
        """Prepare a runnable task to be executed"""
        def _add_solution(result):
            """Add solution to collection"""
            return problem.solutions.add(result, **kwargs)

        # create a task for workers
        kinds = problem.kinds
        if solution is None:
            solution = kinds.__members__[0]
        elif type(solution) in (str, unicode,):
            solution = kinds(solution.upper())
        kwargs.setdefault('kind', solution)

        # peek heuristic
        htsp = longest if solution == kinds.LONGEST else shortest
        task = Task(partial(htsp, problem, **kwargs))

        # now register callback and solution updater
        task.register_all(**self._callbacks)
        task.append_callback(_add_solution)
        return task

    def run(self, task):
        """Start a task and wait till ends"""
        task.start()
        task.wait()

    def start(self, task):
        """Start a task in background"""
        task.start()

    def wait(self, task, remain=None):
        """Wait for task to be finished"""
        task.wait(remain)

    def is_running(self, task):
        """Check if solver is currently running a task"""
        return not (task.is_finished() or task.is_cancelled())

    def stop(self, task):
        """Stop current execution"""
        task.cancel()

    @classmethod
    def can_handle(cls, problem):
        """Check if problem could be solved whith this solver"""
        return problem.query('ITSP')
