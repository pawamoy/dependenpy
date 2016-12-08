# -*- coding: utf-8 -*-

"""
A simple algorithm for solving the Travelling Salesman Problem.

Finds a suboptimal solution.
"""

from __future__ import division, print_function, unicode_literals

from array import array as pyarray
from itertools import islice

from future.utils import bytes_to_native_str

if "xrange" not in globals():
    # py3
    xrange = range
else:
    # py2
    pass


def optimize_solution(distances, connections):
    """Try to optimize solution, found by the greedy algorithm."""
    n = len(connections)
    path = restore_path(connections)

    def ds(i, j):  # distance between ith and jth points of path
        return distances[path[i]][path[j]]

    d_total = 0.0
    optimizations = 0
    for a in range(n - 1):
        b = a + 1
        for c in range(b + 2, n - 1):
            d = c + 1
            delta_d = ds(a, b) + ds(c, d) - (ds(a, c) + ds(b, d))
            if delta_d > 0:
                d_total += delta_d
                optimizations += 1
                connections[path[a]].remove(path[b])
                connections[path[a]].append(path[c])
                connections[path[b]].remove(path[a])
                connections[path[b]].append(path[d])

                connections[path[c]].remove(path[d])
                connections[path[c]].append(path[a])
                connections[path[d]].remove(path[c])
                connections[path[d]].append(path[b])
                path[:] = restore_path(connections)

    return optimizations, d_total


def restore_path(connections):
    """
    Take array of connections and returns a path.

    Connections is array of lists with 1 or 2 elements.
    These elements are indices of teh vertices, connected to this vertex
    Guarantees that first index < last index.
    """
    # there are 2 nodes with valency 1 - start and end. Get them.
    start, end = [idx for idx, conn in enumerate(connections)
                  if len(conn) == 1]
    path = [start]
    prev_point = None
    cur_point = start
    while True:
        next_points = [pnt for pnt in connections[cur_point]
                       if pnt != prev_point]
        if not next_points:
            break
        next_point = next_points[0]
        path.append(next_point)
        prev_point, cur_point = cur_point, next_point
    return path


def pairs_by_dist(n, distances):
    """
    Sort coordinate pairs by distance.

    Args:
        n (int):
        distances (list of pairs): the coordinate pairs.

    Returns:
        list: the sorted coordinate pairs.
    """
    # Sort coordinate pairs by distance
    indices = [None] * (n * (n - 1) // 2)
    idx = 0
    for i in range(n):
        for j in range(i + 1, n):
            indices[idx] = (i, j)
            idx += 1

    indices.sort(key=lambda ij: distances[ij[0]][ij[1]])
    return indices


def solve_tsp(distances, optim_steps=3, pairs=pairs_by_dist):
    """
    Given a distance matrix, finds a solution for the TSP problem.

    Return list of vertex indices.
    Guarantee that the first index is lower than the last.
    """
    n = len(distances)
    if n == 0:
        return []
    if n == 1:
        return [0]
    for row in distances:
        if len(row) != n:
            raise ValueError("Matrix is not square")

    # State of the TSP solver algorithm.
    # Initially, each node has 2 sticky ends
    node_valency = pyarray(bytes_to_native_str(b'i'), [2]) * n

    # for each node, stores 1 or 2 connected nodes
    connections = [[] for i in range(n)]

    def join_segments(sorted_pairs):
        # segments of nodes. Initially, each segment contains only 1 node
        segments = [[i] for i in range(n)]

        def filtered_pairs():
            # Generate sequence of
            for ij in sorted_pairs:
                i, j = ij
                if (not node_valency[i] or
                        not node_valency[j] or
                        (segments[i] is segments[j])):
                    continue
                yield ij

        for i, j in islice(filtered_pairs(), n - 1):
            node_valency[i] -= 1
            node_valency[j] -= 1
            connections[i].append(j)
            connections[j].append(i)
            # Merge segment J into segment I.
            seg_i = segments[i]
            seg_j = segments[j]
            if len(seg_j) > len(seg_i):
                seg_i, seg_j = seg_j, seg_i
                i, j = j, i
            for node_idx in seg_j:
                segments[node_idx] = seg_i
            seg_i.extend(seg_j)

    join_segments(pairs(n, distances))

    for passn in range(optim_steps):
        nopt, dtotal = optimize_solution(distances, connections)
        if nopt == 0:
            break

    path = restore_path(connections)
    return path
