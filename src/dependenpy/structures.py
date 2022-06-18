"""dependenpy structures module."""

from __future__ import annotations

import copy
import json
from typing import TYPE_CHECKING, Any

from colorama import Style

from dependenpy.helpers import PrintMixin

if TYPE_CHECKING:
    from dependenpy.dsm import DSM, Module, Package


class Matrix(PrintMixin):
    """
    Matrix class.

    A class to build a matrix given a list of nodes. After instantiation,
    it has two attributes: data, a 2-dimensions array, and keys, the names
    of the entities in the corresponding order.
    """

    def __init__(self, *nodes: DSM | Package | Module, depth: int = 0):  # noqa: WPS231
        """
        Initialization method.

        Args:
            *nodes: The nodes on which to build the matrix.
            depth: The depth of the matrix. This depth is always
                absolute, meaning that building a matrix with a sub-package
                "A.B.C" and a depth of 1 will return a matrix of size 1,
                containing A only. To see the matrix for the sub-modules and
                sub-packages in C, you will have to give depth=4.
        """
        modules: list[Module] = []
        for node in nodes:
            if node.ismodule:
                modules.append(node)  # type: ignore[arg-type]
            elif node.ispackage or node.isdsm:
                modules.extend(node.submodules)  # type: ignore[union-attr]

        if depth < 1:
            keys = modules
        else:
            keys = []
            for module in modules:
                if module.depth <= depth:
                    keys.append(module)
                    continue
                package = module.package
                while package.depth > depth and package.package and package not in nodes:
                    package = package.package
                if package not in keys:
                    keys.append(package)

        size = len(keys)
        data = [[0] * size for _ in range(size)]  # noqa: WPS435
        keys = sorted(keys, key=lambda key: key.absolute_name())

        if depth < 1:
            for index, key in enumerate(keys):  # noqa: WPS440
                key.index = index  # type: ignore[attr-defined]
            for index, key in enumerate(keys):  # noqa: WPS440
                for dep in key.dependencies:
                    if dep.external:
                        continue
                    if dep.target.ismodule and dep.target in keys:
                        data[index][dep.target.index] += 1
                    elif dep.target.ispackage:
                        init = dep.target.get("__init__")
                        if init is not None and init in keys:
                            data[index][init.index] += 1
        else:
            for row, row_key in enumerate(keys):
                for col, col_key in enumerate(keys):
                    data[row][col] = row_key.cardinal(to=col_key)

        self.size = size
        self.keys = [key.absolute_name() for key in keys]  # noqa: WPS441
        self.data = data

    @staticmethod  # noqa: WPS602
    def cast(keys: list[str], data: list[list[int]]) -> Matrix:  # noqa: WPS602
        """
        Cast a set of keys and an array to a Matrix object.

        Arguments:
            keys: The matrix keys.
            data: The matrix data.

        Returns:
            A new matrix.
        """
        matrix = Matrix()
        matrix.keys = copy.deepcopy(keys)
        matrix.data = copy.deepcopy(data)
        return matrix

    @property
    def total(self) -> int:
        """
        Return the total number of dependencies within this matrix.

        Returns:
            The total number of dependencies.
        """
        return sum(cell for line in self.data for cell in line)

    def _to_csv(self, **kwargs):
        text = ["module,", ",".join(self.keys)]
        for index, key in enumerate(self.keys):
            line = ",".join(map(str, self.data[index]))
            text.append(f"{key},{line}")
        return "\n".join(text)

    def _to_json(self, **kwargs):
        return json.dumps({"keys": self.keys, "data": self.data}, **kwargs)

    def _to_text(self, **kwargs):
        if not self.keys or not self.data:
            return ""
        zero = kwargs.pop("zero", "0")
        max_key_length = max(len(key) for key in self.keys + ["Module"])
        max_dep_length = max([len(str(col)) for line in self.data for col in line] + [len(zero)])
        key_col_length = len(str(len(self.keys)))
        key_line_length = max(key_col_length, 2)
        column_length = max(key_col_length, max_dep_length)
        bold = Style.BRIGHT
        reset = Style.RESET_ALL

        # first line left headers
        text = [f"\n {bold}{'Module':>{max_key_length}}{reset} │ {bold}{'Id':>{key_line_length}}{reset} │"]
        # first line column headers
        for index, _ in enumerate(self.keys):
            text.append(f"{bold}{index:^{column_length}}{reset}│")
        text.append("\n")
        # line of dashes
        text.append(f" {'─' * max_key_length}─┼─{'─' * key_line_length}─┼")
        for _ in range(len(self.keys) - 1):
            text.append(f"{'─' * column_length}┼")
        text.append(f"{'─' * column_length}┤")
        text.append("\n")
        # lines
        for index, key in enumerate(self.keys):  # noqa: WPS440
            text.append(f" {key:>{max_key_length}} │ {bold}{index:>{key_line_length}}{reset} │")
            for value in self.data[index]:
                text.append((f"{value if value else zero:>{column_length}}│"))
            text.append("\n")
        text.append("\n")

        return "".join(text)


class TreeMap(PrintMixin):
    """TreeMap class."""

    def __init__(self, *nodes: Any, value: int = -1):
        """
        Initialization method.

        Arguments:
            *nodes: the nodes from which to build the treemap.
            value: the value of the current area.
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
        return ""

    def _to_json(self, **kwargs):
        return ""

    def _to_text(self, **kwargs):
        return ""


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

    def connect_to(self, vertex: Vertex, weight: int = 1) -> Edge:
        """
        Connect this vertex to another one.

        Args:
            vertex: Vertex to connect to.
            weight: Weight of the edge.

        Returns:
            The newly created edge.
        """
        for edge in self.edges_out:
            if vertex == edge.vertex_in:
                return edge
        return Edge(self, vertex, weight)

    def connect_from(self, vertex: Vertex, weight: int = 1) -> Edge:
        """
        Connect another vertex to this one.

        Args:
            vertex: Vertex to connect from.
            weight: Weight of the edge.

        Returns:
            The newly created edge.
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
        return f"{self.vertex_out.name} --{self.weight}--> {self.vertex_in.name}"

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
        for line_index, line in enumerate(matrix.data):
            for col_index, cell in enumerate(line):
                if cell > 0:
                    self.edges.add(Edge(vertices[line_index], vertices[col_index], weight=cell))
        self.vertices = set(vertices)

    def _to_csv(self, **kwargs):
        header = kwargs.pop("header", True)
        text = ["vertex_out,edge_weight,vertex_in\n" if header else ""]
        for edge in self.edges:
            text.append(f"{edge.vertex_out.name},{edge.weight},{edge.vertex_in.name}\n")
        for vertex in self.vertices:
            if not (vertex.edges_out or vertex.edges_in):
                text.append("{vertex.name},,\n")
        return "".join(text)

    def _to_json(self, **kwargs):
        return json.dumps(
            {
                "vertices": [vertex.name for vertex in self.vertices],
                "edges": [
                    {"out": edge.vertex_out.name, "weight": edge.weight, "in": edge.vertex_in.name}
                    for edge in self.edges
                ],
            },
            **kwargs,
        )

    def _to_text(self, **kwargs):
        return ""
