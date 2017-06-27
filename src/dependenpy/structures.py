# -*- coding: utf-8 -*-

"""dependenpy structures module."""

import json

from .helpers import PrintMixin


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

    def __init__(self, *nodes, value=-1, data=None, keys=None):
        """
        Initialization method.

        Arguments:
            *nodes (list of Node): the nodes from which to build the treemap.
        """
        # if nodes:
        #     matrix_lower_level = Matrix(*nodes, depth=2)
        #     matrix_current_level = Matrix(*nodes, depth=1)
        #     if value == -1:
        #         value = sum(c for row in matrix_current_level.data for c in row)
        #     splits = [0]
        #     key_comp = matrix_lower_level.keys[0].split('.')[0]
        #     i = 1
        #     for key in matrix_lower_level.keys[1:]:
        #         key = key.split('.')[0]
        #         if key != key_comp:
        #             splits.append(i)
        #             key_comp = key
        #         i += 1
        #     splits.append(i)
        #
        #     self.data = []
        #     for i in range(len(splits) - 1):
        #         self.data.append([])
        #         rows = matrix_lower_level.data[splits[i]:splits[i+1]]
        #         for j in range(len(splits) - 1):
        #             self.data[i].append([row[splits[j]:splits[j+1]] for row in rows])

        self.value = value

    def _to_csv(self, **kwargs):
        return ''

    def _to_json(self, **kwargs):
        return ''

    def _to_text(self, **kwargs):
        return ''


class Vertex(object):
    """Vertex class. Used in Graph class."""

    def __init__(self, name):
        """
        Initialization method.

        Args:
            name (str): name of the vertex.
        """
        self.name = name
        self.edges_in = set()
        self.edges_out = set()

    def __str__(self):
        return self.name

    def connect_to(self, vertex, weight=1):
        """
        Connect this vertex to another one.

        Args:
            vertex (Vertex): vertex to connect to.
            weight (int): weight of the edge.

        Returns:
            Edge: the newly created edge.
        """
        for edge in self.edges_out:
            if vertex == edge.vertex_in:
                return edge
        return Edge(self, vertex, weight)

    def connect_from(self, vertex, weight=1):
        """
        Connect another vertex to this one.

        Args:
            vertex (Vertex): vertex to connect from.
            weight (int): weight of the edge.

        Returns:
            Edge: the newly created edge.
        """
        for edge in self.edges_in:
            if vertex == edge.vertex_out:
                return edge
        return Edge(vertex, self, weight)


class Edge(object):
    """Edge class. Used in Graph class."""

    def __init__(self, vertex_out, vertex_in, weight=1):
        """
        Initialization method.

        Args:
            vertex_out (Vertex): source vertex (edge going out).
            vertex_in (Vertex): target vertex (edge going in).
            weight (int): weight of the edge.
        """
        self.vertex_out = None
        self.vertex_in = None
        self.weight = weight
        self.go_from(vertex_out)
        self.go_in(vertex_in)

    def __str__(self):
        return '%s --%d--> %s' % (
            self.vertex_out.name, self.weight, self.vertex_in.name)

    def go_from(self, vertex):
        """
        Tell the edge to go out from this vertex.

        Args:
            vertex (Vertex): vertex to go from.
        """
        if self.vertex_out:
            self.vertex_out.edges_out.remove(self)
        self.vertex_out = vertex
        vertex.edges_out.add(self)

    def go_in(self, vertex):
        """
        Tell the edge to go into this vertex.

        Args:
            vertex (Vertex): vertex to go into.
        """
        if self.vertex_in:
            self.vertex_in.edges_in.remove(self)
        self.vertex_in = vertex
        vertex.edges_in.add(self)


class Graph(PrintMixin):
    """
    Graph class.

    A class to build a graph given a list of nodes. After instantiation,
    it has two attributes: vertices, the set of nodes,
    and edges, the set of edges.
    """

    def __init__(self, *nodes, depth=0):
        """
        Initialization method.

        An intermediary matrix is built to ease the creation of the graph.

        Args:
            *nodes (list of DSM/Package/Module):
                the nodes on which to build the graph.
            depth (int): the depth of the intermediary matrix. See
                the documentation for Matrix class.
        """
        self.edges = set()
        vertices = []
        matrix = Matrix(*nodes, depth=depth)
        for key in matrix.keys:
            vertices.append(Vertex(key))
        for l, line in enumerate(matrix.data):
            for c, cell in enumerate(line):
                if cell > 0:
                    self.edges.add(Edge(vertices[l], vertices[c], weight=cell))
        self.vertices = set(vertices)

    def _to_csv(self, **kwargs):
        header = kwargs.pop('header', True)
        text = ['vertex_out,edge_weight,vertex_in\n' if header else '']
        for edge in self.edges:
            text.append('%s,%s,%s\n' % (
                edge.vertex_out.name, edge.weight, edge.vertex_in.name))
        for vertex in self.vertices:
            if not (vertex.edges_out or vertex.edges_in):
                text.append('%s,,\n' % vertex.name)
        return ''.join(text)

    def _to_json(self, **kwargs):
        return json.dumps({
            'vertices': [vertex.name for vertex in self.vertices],
            'edges': [{
                'out': edge.vertex_out.name,
                'weight': edge.weight,
                'in': edge.vertex_in.name
            } for edge in self.edges]
        }, **kwargs)

    def _to_text(self, **kwargs):
        return ''


def split_array(mdata, splits):
    data = []
    for i in range(len(splits) - 1):
        data.append([])
        rows = mdata[splits[i]:splits[i + 1]]
        for j in range(len(splits) - 1):
            data[i].append([row[splits[j]:splits[j + 1]] for row in rows])
        data[i].append([row[splits[-1]:] for row in rows])
    return data
