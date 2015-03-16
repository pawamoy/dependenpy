#!/usr/bin/python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
This program generates a random array of distances between cities, then uses
Ant Colony Optimization to find a short path traversing all the cities --
the Travelling Salesman Problem.

In this version of Ant Colony Optimization each ant starts in a random city.
Paths are randomly chosed with probability inversely proportional to to the
distance to the next city.  At the end of its travel the ant updates the
pheromone matrix with its path if this path is the shortest one yet found.
The probability of later ants taking a path is increased by the pheromone
value on that path.  Pheromone values evaporate (decrease) over time.

In this impementation weights between cities actually represent
(maxDistance - dist), so we are trying to maximize the score.

Usage: ant seed boost iterations cities
  seed         seed for random number generator (1,2,3...).
               This seed controls the city distance array.  Remote
               executions have their seed values fixed (1,2) so each will
               produce a different result.
  boost        pheromone boost for best path.  5 appears good.
               0 disables pheromones, providing random search.
  iterations   number of ants to be run.
  cities       number of cities.
"""

from __future__ import absolute_import

__author__  = "Eric Rollins (2008), Leonardo Maffi (2010)"
__license__ = "See LICENSE file for details"

# Add here required modules
from random import seed, uniform, randrange
from itertools import izip, chain
from operator import gt, lt

# Sleipnir dependences
from sleipnir.core.operators import Cast
from sleipnir.heuristics.exceptions import PartialStop
from sleipnir.core.decorator import profile

# import optimizations
try:
    #pylint: disable-msg=E0611
    from . import _aco
except ImportError:
    pass


__all__ = ['shortest', 'longest']

#pylint: disable-msg=C0103
try:
    fast_seed = _aco.fast_seed
except (NameError, AttributeError,):
    fast_seed = seed


def path_length(cities, path):
    """Get total weight for a path"""
    pairs = izip(path, chain(path[1:], [path[0]]))
    return sum([cities[r][c] for r, c in pairs])


def update_pherom(pher, path, boost):
    """Boosts pheromones for cities on path."""
    for row, col in izip(path, chain(path[1:], [path[0]])):
        pher[row][col] += boost


def create_pherom_py(size):
    """Create a pherom matrix"""
    #pylint: disable-msg=W0612
    return [[uniform(0, 0) for c in xrange(size)] for r in xrange(size)]

try:
    create_pherom = _aco.create_pherom
except (NameError, AttributeError,):
    create_pherom = create_pherom_py


def evaporate_pherom_py(pher, size, miter, boost):
    """Evaporate pheromone"""
    decr = boost / float(miter)
    for row in pher:
        for c in xrange(size):
            if row[c] > decr:
                row[c] -= decr
            else:
                row[c] = 0.0

try:
    evaporate_pherom = _aco.evaporate_pherom
except (NameError, AttributeError,):
    evaporate_pherom = evaporate_pherom_py


def sum_weights_py(cities, size, pherom, used, current):
    """Sum weights for all paths to cities adjacent to current."""
    rtotal = 0.0
    for city in xrange(size):
        if not used[city]:
            rtotal += cities[current][city] * (1.0 + pherom[current][city])
    return rtotal

try:
    sum_weights = _aco.sum_weights
except (NameError, AttributeError,):
    sum_weights = sum_weights_py


def find_sum_weights_py(cities, size, pher, used, current, sought_total):
    """Returns city at sought_total."""
    rtotal = 0.0
    ctnext = 0
    for city in xrange(size):
        if rtotal >= sought_total:
            break
        if not used[city]:
            rtotal += cities[current][city] * (1.0 + pher[current][city])
            ctnext = city
    return ctnext

try:
    find_sum_weights = _aco.find_sum_weights
except (NameError, AttributeError,):
    find_sum_weights = find_sum_weights_py


def gen_path_py(cities, size, pher):
    """Generate a candidate path"""

    # peek a random city
    current = randrange(size)
    # init path
    path = [0] * size
    path[0] = current
    pos_path = 1
    # mark as used
    used = [0] * size
    used[current] = 1
    nused = 1
    # iterate
    while nused < size:
        sweight = sum_weights(cities, size, pher, used, current)
        rnd_val = uniform(0, sweight)
        current = find_sum_weights(cities, size, pher, used, current, rnd_val)
        path[pos_path] = current
        pos_path += 1
        if not used[current]:
            nused += 1
            used[current] = 1
    return path

try:
    gen_path = _aco.gen_path
except (NameError, AttributeError,):
    gen_path = gen_path_py


def validate(kwargs):
    """Set kwargs dictionary in a consistent state"""

    kwargs.setdefault('seed',  1)
    kwargs.setdefault('boost', 5)
    kwargs.setdefault('iters', 1000)
    kwargs.setdefault('partial', kwargs['iters'])
    return kwargs


def prepare(wrapper, problem, kwargs):
    """Deploy initial data to perform a TSP calculation"""

    # seed values
    if not problem.seed:
        problem.seed = hash(wrapper)
    fast_seed(problem.seed)

    # Read only attributes available for callbacks
    wrapper.total = 1
    wrapper.result = ([], 0.0,)
    wrapper.kwargs = validate(kwargs)
    wrapper.solver = 'Ant Colony Optimization v1.0, Dorigo et al. (Python)'

    cast = Cast.get_instance()
    # Size of locations isn'e have to be size of weight matrix. Even matrix
    # could be MxN where M is len(locations) and N is len(locations)/4*4
    weight = cast.get(cast.get(problem.routes, list).weight)(4)
    pherom = create_pherom(len(weight[0]))

    # private to Algorithm
    wrapper._aco = (weight, pherom,)


@profile()
def calculate(wrapper, ops=gt):
    """Calculate TSP Path based on operator (longest or shortest)"""

    # previous stored values
    best_path, best_length = wrapper.result

    # Aco Algorithm implementation data
    # pylint: disable-msg = W0212
    weight, pherom = wrapper._aco
    weight_size, pherom_size = len(weight), len(pherom[0])

    # User stops
    boost, iters = wrapper.boost, wrapper.iters
    evaluate = wrapper.partial.evaluate

    try:
        for counter in xrange(wrapper.total - 1, wrapper.iters):
            path = gen_path(weight, weight_size, pherom)
            length = path_length(weight, path)
            # if best path, update pheroms
            if ops(length, best_length):
                best_path, best_length = path, length
                # Remember we are trying to maximize score.
                update_pherom(pherom, path, boost)
            # evaporate pheromone, Always
            evaporate_pherom(pherom, pherom_size, iters, boost)
            # update length local var
            if evaluate(length=length, percentage=counter + 1):
                raise PartialStop
    finally:
        # update wrapper
        wrapper.total = counter + 1
        wrapper.result = (best_path, best_length,)
    # return
    return wrapper.result


def aco(problem, wrapper, ops, **kwargs):
    """
    Calculate a solution to problem based on initial state, heuristic
    params and other stuff
    """
    # process wrapper
    if not hasattr(wrapper, '_aco'):
        problem.routes.update()
        with problem.routes:
            prepare(wrapper, problem, kwargs)

    while wrapper.total < wrapper.iters:
        try:
            calculate(wrapper, ops)
            wrapper.state = 'finished'
            wrapper.finished = True
        except PartialStop:
            wrapper.state = 'inprogress'
            wrapper.finished = False
            break
    # finally, return best result
    return wrapper.result


def shortest(problem, wrapper, **kwargs):
    """Calculate Shortest TSP"""
    return aco(problem, wrapper, lt, **kwargs)


def longest(problem, wrapper, **kwargs):
    """Calculate Longest TSP"""
    return aco(problem, wrapper, gt, **kwargs)
