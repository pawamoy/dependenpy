#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""TSP Component"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from functools import partial
from random import seed, uniform
from threading import Lock, Event

from sleipnir.components.manager import ComponentManager
from sleipnir.components.entrypoint import ExtensionPoint
from sleipnir.components.components import Component, implements

from sleipnir.core.thread import Task

from sleipnir.heuristics.routes import RouteFactory
from sleipnir.heuristics.solutions import Solutions
from sleipnir.heuristics.interfaces import marshal
from sleipnir.heuristics.interfaces.problem import IProblem


__all__ = ['TSP']

# local submodule requirements
from .interfaces import ITSP


class TSPError(Exception):
    """A TSPError"""


#pylint: disable-msg=E0602,R0903,W0232
class TSPKind(enum):
    """Type of TSP problem to solve"""

    SHORTEST, LONGEST = xrange(2)


class TSP(Component, ComponentManager):
    """
    An object to represent a TSP problem

    Use this class to operate over tsp problems and derivate. After
    define a valid tsp problem by loading (using IMarshal extension
    points) or by construction, asign it to one of the available
    algorithms to solve this kind of problem.
    """

    implements(IProblem)
    implements(ITSP)

    unmarshals = ExtensionPoint(marshal.IUnMarshal)

    def __init__(self):
        super(TSP, self).__init__()

        self._tsp = None
        self._tsp_lock = Lock()
        self._tsp_event = Event()
        self._tsp_event.set()

        # solutions stuff
        self._solutions = Solutions()

        # Custom properties for TSP problems
        self._routes = None
        self._cities = None

        # Algorithm default seed
        self._seed = None

    @property
    def routes(self):
        """returns a list of routes(edges) which compose TSP problem"""
        while not self._tsp_event.is_set():
            self._tsp_event.wait()
        return self._routes

    @property
    def locations(self):
        """returns a list of locations(nodes) which compose TSP problem"""
        while not self._tsp_event.is_set():
            self._tsp_event.wait()
        return self._cities

    @property
    def cities(self):
        """returns a list of cities which compose TSP problem"""
        return self.locations

    @property
    def sections(self):
        """Returns low level definition of the problem"""
        while not self._tsp_event.is_set():
            self._tsp_event.wait()
        return self._tsp

    @property
    def solutions(self):
        """Returns low level definition of the problem"""
        return self._solutions

    #pylint: disable-msg=R0201
    @property
    def kinds(self):
        """Get kind of solutions"""
        return TSPKind

    @property
    def seed(self):
        """Seed property accesor"""
        return self._seed

    @seed.setter
    def seed(self, value):
        """Seed property setter accesor"""
        self._seed = value

    def get_solutions(self, solution, **kwargs):
        """Get solutions available for solutions 'kind' of problem"""
        kwargs.setdefault('kind', TSPKind(solution.upper()))
        return self.solutions.get(**kwargs)

    def load_from(self, where):
        """
        Parse a TSP problem loaded from 'where' param

        Keyword arguments:
        where -- location of the problem. It could be a path to a
        file, a stream or a file descriptor
        """
        assert where is not None
        self._tsp_lock.acquire()
        for umo in self.unmarshals:
            try:
                tsp = umo.load(where)
            except Exception:
                pass
            break
        try:
            routes = RouteFactory.get_instance().create(tsp)
            cities = routes.cities
            self._tsp_event.clear()
            self._tsp = tsp
            self._cities, self._routes = cities, routes
            self._tsp_event.set()
            return self._tsp
        finally:
            self._tsp_lock.release()
        raise TSPError("Unable to unmarshal contents from %s", where[20:])

    def async_load_from(self, where, **kwargs):
        """Parse a TSP problem into it's own thread"""
        return Task(partial(self.load_from, where), **kwargs)

    def shuffle(self, locs=50, dist=100):
        """Create a new random problem"""
        seed(self)
        if not hasattr(dist, '__iter__'):
            dist = (0, dist,)

        with self._tsp_lock:
            # pylint: disable-msg=W0612,W0142
            routes = RouteFactory.get_instance().create(
                [[uniform(*dist) for c in xrange(locs)] for r in xrange(locs)])
            cities = routes.cities  # sugar self._routes.locations
            tsp = self._tsp.merge(routes, cities)
            self._tsp_event.clear()
            self._tsp = tsp
            self._cities, self._routes = cities, routes
            self._tsp_event.set()
