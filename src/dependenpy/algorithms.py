"""dependenpy alogorithms module.

https://dsmweb.org/sequencing-a-dsm/
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, List, Tuple

from dependenpy.structures import Matrix

if TYPE_CHECKING:
    from dependenpy.dsm import DSM, Module, Package


class DsmMatrix(Matrix):
    """_summary_."""

    def __init__(self, *nodes: DSM | Package | Module, depth: int = 0):
        """_summary_.

        Args:
            *nodes: The nodes on which to build the matrix.
            depth: The depth of the matrix. This depth is always
                absolute, meaning that building a matrix with a sub-package
                "A.B.C" and a depth of 1 will return a matrix of size 1,
                containing A only. To see the matrix for the sub-modules and
                sub-packages in C, you will have to give depth=4.
        """
        super().__init__(*nodes, depth=depth)
        self.front = 0
        self.back = len(self.keys)
        self.info = {item: {} for item in self.keys}  # assumes items are strings...

    @property
    def rank(self):
        return len(self.keys)

    @staticmethod
    def create(matrix: Matrix) -> DsmMatrix:  # noqa: WPS602
        """_summary_.

        Args:
            matrix (Matrix): _description_

        Returns:
            DsmMatrix: _description_
        """
        result = DsmMatrix()
        result.keys = copy.deepcopy(matrix.keys)
        result.key_info = copy.deepcopy(matrix.key_info)
        result.data = copy.deepcopy(matrix.data)
        result.front = 0
        result.back = result.rank
        return result

    def copy(self) -> DsmMatrix:
        """_summary_.

        Returns:
            DsmMatrix: The return value.
        """
        result = DsmMatrix()
        result.keys = copy.deepcopy(self.keys)
        result.key_info = copy.deepcopy(self.key_info)
        result.data = copy.deepcopy(self.data)
        result.front = self.front
        result.back = self.back
        return result

    def index_of(self, name: Any) -> int:
        """_summary_.

        Args:
            name (Any): _description_

        Returns:
            int: _description_
        """
        return self.keys.index(name)

    def get_inputs(self, index: int) -> list:
        return self.data[index]

    def get_outputs(self, index: int) -> list:
        return [item[index] for item in self.data]

    def has_inputs(self, index: int) -> bool:
        return any(self.get_inputs(index))

    def has_outputs(self, index: int) -> bool:
        return any(self.get_outputs(index))

    def sequence(self) -> DsmMatrix:
        """Reorder elements in matrix so that they are as close as possible to diagonal.

        Identify loops and clusters of interdependent modules.

        1. For each element, if it does not depend on any other (empty column), move to beginning and ignore hereafter.
        2. For each element, if nobody depends on it (empty row), move to end and ignore hereafter.
        3. For the rest of the elements, find loops by decomposition or partition
        4. Collapse each loop into onecompounded element, and go to step 1.

        Args:
            matrix (DsmMatrix): _description_
        """
        result1 = self
        for item in range(result1.front, result1.back):
            print("---", item, result1.front, result1.back)
            if not self.has_inputs(item):
                # print(">")
                result1 = result1.element_to_back(item)
            elif not self.has_outputs(item):
                # print("<")
                result1 = result1.element_to_front(item)
            else:
                # print("=")
                pass
        return result1

    def decompose(self):
        """_summary_.

        Args:
            matrix (DsmMatrix): _description_
        """

    def partition(self) -> List[Tuple[str, int]]:
        """Builds a hierarchy of elements.

        Inside a level the elements are either not connected to each other, or are part of the same circuit at that level.

        The top level is composed of all elements that require no input or are independent from all other elements.
        Removing these elements from the matrix, leaves a new matrix whose top level is the secont level of the original one.
        In this manner, all levels can be identified.

        For each element,list the set of their inputs (including the element itself), the set of the outputs
        (including the element itself) and the intersection of these sets.
        If the input set equals the intersection set, it is a top element.
        After identifying all top elements, remove them and proceed recursively.

        The result is an list of tuples (element, level), where the top level is 1.

        Args:
            matrix (DsmMatrix): _description_

        Returns:
            List[Tuple[str, int]]: _description_
        """
        return []

    def _switch_rows(self, source: int, target: int) -> DsmMatrix:
        """Returns a matrix with the given rows switched.

        Args:
            source: (int): _description_
            target (int): _description_

        Returns:
            DsmMatrix: _description_
        """
        result = self.copy()
        ii, jj = result.data[target], result.data[source]
        result.data[source] = ii
        result.data[target] = jj
        return result

    def _switch_columns(self, source: int, target: int) -> DsmMatrix:
        """Returns a matrix with the given columns switched.

        Args:
            source: (int): _description_
            target (int): _description_

        Returns:
            DsmMatrix: _description_
        """
        result = self.copy()
        size = result.rank
        for ix in range(0, size):
            ii, jj = result.data[ix][target], result.data[ix][source]
            result.data[ix][source] = ii
            result.data[ix][target] = jj
        return result

    def switch_elements(self, source: int, target: int) -> DsmMatrix:
        """Returns a matrix with the given rows and columns switched, as well as the keys.

        Args:
            source: (int): _description_
            target (int): _description_

        Returns:
            DsmMatrix: _description_
        """
        result = self._switch_rows(source, target)
        result = result._switch_columns(source, target)
        ii, jj = result.keys[target], result.keys[source]
        result.keys[source] = ii
        result.keys[target] = jj
        return result

    def element_to_front(self, index: int) -> DsmMatrix:
        """Switch index with matrix.front, and increment matrix.front.

        Args:
            matrix (DsmMatrix): _description_
            index (int): _description_

        Returns:
            DsmMatrix: _description_
        """
        if index <= self.front:
            return self
        result = self.switch_elements(index, self.front)
        result.front += 1
        return result

    def element_to_back(self, index: int) -> DsmMatrix:
        """Switch index with matrix.back, and decrement matrix.back.

        Args:
            matrix (DsmMatrix): _description_
            index (int): _description_

        Returns:
            DsmMatrix: _description_
        """
        if index >= self.back:
            return self
        result = self.switch_elements(index, self.back - 1)
        result.back -= 1
        return result

    def reachability(self):
        """Return the reachability matrix.

        In this matrix, an 1 in cell (i,j) means there is a path going from i to j.
        """
        return self._plus_unity()._as_boolean()._power(self.rank)._as_boolean()

    def _power(self, power: int):
        result = self.copy()
        if power < 2:
            return result
        for _ in range(power - 1):
            result.data = _multiply(result.data, self.data)
        return result

    def _as_boolean(self):
        result = self.copy()
        for ii in range(result.rank):
            for jj in range(result.rank):
                if result.data[ii][jj]:
                    result.data[ii][jj] = 1
        return result

    def _plus_unity(self):
        result = self.copy()
        for ii in range(result.rank):
            result.data[ii][ii] += 1
        return result

    def is_top_level_element(self, index: int) -> bool:
        reach = int("".join(str(x) for x in self.data[index]), 2)
        ante = int("".join(str(x) for x in [r[index] for r in self.data]), 2)
        return reach & ante == ante

    def remove_element(self, index: int) -> DsmMatrix:
        result = self.copy()
        del result.keys[index]
        del result.data[index]
        for cc in result.data:
            del cc[index]
        return result

    def reorder(self, new_keys: List[str]):
        swaps = _find_swaps(self.keys, new_keys)
        result = self.copy()
        for ii, jj in swaps:
            result = result.switch_elements(ii, jj)
        return result

    def levelize(self):
        levels = self.get_levels()
        for ix, ks in enumerate(levels):
            for k in ks:
                self.key_info[k].level=ix
        return self.reorder(_flatten(levels))

    def get_levels(self):
        m = self.reachability()
        levels = []
        while m.rank > 1:
            tops = []
            for ii in range(m.rank):
                if m.is_top_level_element(ii):
                    tops.append(ii)
            levels.append([m.keys[x] for x in tops])
            for index, ii in enumerate(tops):
                m = m.remove_element(ii - index)
        if m.keys:
            levels.append(m.keys)
        return levels


def _multiply(matrix1, matrix2):
    """Multiply two matrices"""
    return [[sum(a * b for a, b in zip(row, col)) for col in zip(*matrix2)] for row in matrix1]


def _find_swaps(source, target):
    source = copy.copy(source)
    target = copy.copy(target)
    result = []
    for index in range(len(source)):
        if source[index] == target[index]:
            continue
        dest = source.index(target[index])
        result.append((index, dest))
        source[index], source[dest] = source[dest], source[index]

    return result


def _flatten(alist):
    return [x for xs in alist for x in xs]
