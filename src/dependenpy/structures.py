# -*- coding: utf-8 -*-

"""dependenpy structures module."""

import json

from .printer import PrintMixin


class Matrix(PrintMixin):
    """
    Matrix class.

    A class to build a matrix given a list of nodes. After instantiation,
    it has two attributes: data, a 2-dimensions array, and keys, the names
    of the entities in the corresponding order.
    """

    def __init__(self, *nodes, depth=0):
        """
        Initialization method.

        Args:
            *nodes (list of DSM/Package/Module):
                the nodes on which to build the matrix.
            depth (int): the depth of the matrix. This depth is always
                absolute, meaning that building a matrix with a sub-package
                "A.B.C" and a depth of 1 will return a matrix of size 1,
                containing A only. To see the matrix for the sub-modules and
                sub-packages in C, you will have to give depth=4.
        """
        modules = []
        for node in nodes:
            if node.ismodule:
                modules.append(node)
            elif node.ispackage or node.isdsm:
                modules.extend(node.submodules)

        if depth < 1:
            keys = modules
        else:
            keys = []
            for m in modules:
                if m.depth <= depth:
                    keys.append(m)
                    continue
                package = m.package
                while (package.depth > depth and
                       package.package and
                       package not in nodes):
                    package = package.package
                if package not in keys:
                    keys.append(package)

        size = len(keys)
        data = [[0 for _ in range(size)] for __ in range(size)]
        keys = sorted(keys, key=lambda k: k.absolute_name())

        if depth < 1:
            for i, k in enumerate(keys):
                k.index = i
            for i, k in enumerate(keys):
                for d in k.dependencies:
                    if d.external:
                        continue
                    if d.target.ismodule and d.target in keys:
                        data[i][d.target.index] += 1
                    elif d.target.ispackage:
                        m = d.target.get('__init__')
                        if m is not None and m in keys:
                            data[i][m.index] += 1
        else:
            for i, k in enumerate(keys):
                for j, l in enumerate(keys):
                    data[i][j] = k.cardinal(to=l)

        self.size = size
        self.keys = [k.absolute_name() for k in keys]
        self.data = data

    @staticmethod
    def cast(keys, data):
        """Cast a set of keys and an array to a Matrix object."""
        matrix = Matrix()
        matrix.keys = keys
        matrix.data = data
        return matrix

    @property
    def total(self):
        """Return the total number of dependencies within this matrix."""
        return sum(j for i in self.data for j in i)

    def _to_csv(self, **kwargs):
        text = ['module,', ','.join(self.keys), '\n']
        for i, k in enumerate(self.keys):
            text.append('%s,%s\n' % (k, ','.join(map(str, self.data[i]))))
        return ''.join(text)

    def _to_json(self, **kwargs):
        return json.dumps({'keys': self.keys, 'data': self.data}, **kwargs)

    def _to_text(self, **kwargs):
        if not self.keys or not self.data:
            return ''
        max_key_length = max(len(k) for k in self.keys)
        max_dep_length = len(str(max(j for i in self.data for j in i)))
        key_col_length = len(str(len(self.keys)))
        key_line_length = max(key_col_length, 2)
        column_length = max(key_col_length, max_dep_length)

        # first line left headers
        text = [('\n {:>%s} | {:>%s} ||' % (
            max_key_length, key_line_length
        )).format('Module', 'Id')]
        # first line column headers
        for i, _ in enumerate(self.keys):
            text.append(('{:^%s}|' % column_length).format(i))
        text.append('\n')
        # line of dashes
        text.append((' %s-+-%s-++' % (
            '-' * max_key_length, '-' * key_line_length)))
        for i, _ in enumerate(self.keys):
            text.append('%s+' % ('-' * column_length))
        text.append('\n')
        # lines
        for i, k in enumerate(self.keys):
            text.append((' {:>%s} | {:>%s} ||' % (
                max_key_length, key_line_length
            )).format(k, i))
            for v in self.data[i]:
                text.append(('{:>%s}|' % column_length).format(v))
            text.append('\n')
        text.append('\n')

        return ''.join(text)


class TreeMap(PrintMixin):
    """TreeMap class."""

    def __init__(self, *nodes):
        """
        Initialization method.

        Arguments:
            *nodes (list of Node): the nodes from which to build the treemap.
        """
        # For each couple of subpackages of same depth, starting at max depth
        # if same packages (diagonal), create corresponding matrix
        # else (things get complicated):
        # create non-square matrix
        # with node1's keys as lines and node2's keys as columns
        # go up, combining
        pass  # TODO: implement TreeMap

    def _to_csv(self, **kwargs):
        return ''

    def _to_json(self, **kwargs):
        return ''

    def _to_text(self, **kwargs):
        return ''
