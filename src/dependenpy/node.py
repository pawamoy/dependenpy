# -*- coding: utf-8 -*-

"""dependenpy node module."""

import json
import sys

from .structures import Graph, Matrix, TreeMap


class NodeMixin(object):
    """Shared code between DSM, Package and Module."""

    @property
    def ismodule(self):
        """Property to check if object is instance of Module."""
        return False

    @property
    def ispackage(self):
        """Property to check if object is instance of Package."""
        return False

    @property
    def isdsm(self):
        """Property to check if object is instance of DSM."""
        return False


class RootNode(object):
    """Shared code between DSM and Package."""

    def __init__(self, build_tree=True):
        """
        Initialization method.

        Args:
            build_tree (bool): whether to immediately build the tree or not.
        """
        self._target_cache = {}
        self._item_cache = {}
        self._contains_cache = {}
        self._matrix_cache = {}
        self._graph_cache = {}
        self._treemap_cache = None
        self.modules = []
        self.packages = []

        if build_tree:
            self.build_tree()

    def __contains__(self, item):
        """
        Get result of _contains, cache it and return it.

        Args:
            item (Package/Module): a package or module.

        Returns:
            bool: True if self contains item, False otherwise.
        """
        if item not in self._contains_cache:
            self._contains_cache[item] = self._contains(item)
        return self._contains_cache[item]

    def __getitem__(self, item):
        """
        Return the corresponding Package or Module object.

        Args:
            item (str): name of the package/module, dot-separated.

        Returns:
            Package/Module: corresponding object.
        """
        depth = item.count('.') + 1
        parts = item.split('.', 1)
        for m in self.modules:
            if parts[0] == m.name:
                if depth == 1:
                    return m
        for p in self.packages:
            if parts[0] == p.name:
                if depth == 1:
                    return p
                item = p.get(parts[1])
                if item:
                    return item
        raise KeyError(item)

    def __bool__(self):
        """
        Node as Boolean.

        Returns:
            bool: result of node.empty.

        """
        return bool(self.modules or self.packages)

    @property
    def empty(self):
        """
        Whether the node has neither modules nor packages.

        Returns:
            bool: True if empty, False otherwise.
        """
        return not bool(self)

    @property
    def submodules(self):
        """
        Property to return all sub-modules of the node, recursively.

        Returns:
            list of Module: the sub-modules.
        """
        submodules = []
        submodules.extend(self.modules)
        for p in self.packages:
            submodules.extend(p.submodules)
        return submodules

    def build_tree(self):
        """To be overridden."""
        raise NotImplementedError

    def _contains(self, item):
        """
        Whether given item is contained inside the node modules/packages.

        Args:
            item (Package/Module): a package or module.

        Returns:
            bool: True if self is item or item in self's packages/modules.
        """
        if self is item:
            return True
        for m in self.modules:
            if item in m:
                return True
        for p in self.packages:
            if item in p:
                return True
        return False

    def get(self, item):
        """
        Get item through ``__getitem__`` and cache the result.

        Args:
            item (str): name of package or module.

        Returns:
            Package/Module: the corresponding object.
        """
        if item not in self._item_cache:
            try:
                item = self.__getitem__(item)
            except KeyError:
                item = None
            self._item_cache[item] = item
        return self._item_cache[item]

    def get_target(self, target):
        """
        Get the result of _get_target, cache it and return it.

        Args:
            target (str): target to find.

        Returns:
            Package/Module: package containing target or corresponding module.
        """
        if target not in self._target_cache:
            self._target_cache[target] = self._get_target(target)
        return self._target_cache[target]

    def _get_target(self, target):
        """
        Get the Package or Module related to given target.

        Args:
            target (str): target to find.

        Returns:
            Package/Module: package containing target or corresponding module.
        """
        depth = target.count('.') + 1
        parts = target.split('.', 1)
        for m in self.modules:
            if parts[0] == m.name:
                if depth < 3:
                    return m
        for p in self.packages:
            if parts[0] == p.name:
                if depth == 1:
                    return p
                # pylama:ignore=W0212
                target = p._get_target(parts[1])
                if target:
                    return target
                # FIXME: can lead to internal dep instead of external
                # see example with django.contrib.auth.forms
                # importing forms from django
                # Idea: when parsing files with ast, record what objects
                # are defined in the module. Then check here if the given
                # part is one of these objects.
                if depth < 3:
                    return p
        return None

    def build_dependencies(self):
        """
        Recursively build the dependencies for sub-modules and sub-packages.

        Iterate on node's modules then packages and call their
        build_dependencies methods.
        """
        for m in self.modules:
            m.build_dependencies()
        for p in self.packages:
            p.build_dependencies()

    def print_graph(self, format=None, output=sys.stdout, depth=0, **kwargs):
        """
        Print the graph for self's nodes.

        Args:
            format (str): output format (csv, json or text).
            output (file): file descriptor on which to write.
            depth (int): depth of the graph.
        """
        graph = self.as_graph(depth=depth)
        graph.print(format=format, output=output, **kwargs)

    def print_matrix(self, format=None, output=sys.stdout, depth=0, **kwargs):
        """
        Print the matrix for self's nodes.

        Args:
            format (str): output format (csv, json or text).
            output (file): file descriptor on which to write.
            depth (int): depth of the matrix.
        """
        matrix = self.as_matrix(depth=depth)
        matrix.print(format=format, output=output, **kwargs)

    def print_treemap(self, format=None, output=sys.stdout, **kwargs):
        """
        Print the matrix for self's nodes.

        Args:
            format (str): output format (csv, json or text).
            output (file): file descriptor on which to write.
        """
        treemap = self.as_treemap()
        treemap.print(format=format, output=output, **kwargs)

    def _to_text(self, **kwargs):
        indent = kwargs.pop('indent', 2)
        base_indent = kwargs.pop('base_indent', None)
        if base_indent is None:
            base_indent = indent
            indent = 0
        text = [' ' * indent + str(self) + '\n']
        new_indent = indent + base_indent
        for m in self.modules:
            text.append(m._to_text(indent=new_indent, base_indent=base_indent))
        for p in self.packages:
            text.append(p._to_text(indent=new_indent, base_indent=base_indent))
        return ''.join(text)

    def _to_csv(self, **kwargs):
        header = kwargs.pop('header', True)
        modules = sorted(self.submodules, key=lambda x: x.absolute_name())
        text = ['module,path,target,lineno,what,external\n' if header else '']
        for m in modules:
            text.append(m._to_csv(header=False))
        return ''.join(text)

    def _to_json(self, **kwargs):
        return json.dumps(self.as_dict(), **kwargs)

    def as_dict(self):
        """
        Return the dependencies as a dictionary.

        Returns:
            dict: dictionary of dependencies.
        """
        return {
            'name': str(self),
            'modules': [m.as_dict() for m in self.modules],
            'packages': [p.as_dict() for p in self.packages]
        }

    def as_graph(self, depth=0):
        """
        Create a graph with self as node, cache it, return it.

        Args:
            depth (int): depth of the graph.

        Returns:
            Graph: an instance of Graph.
        """
        if depth in self._graph_cache:
            return self._graph_cache[depth]
        self._graph_cache[depth] = graph = Graph(self, depth=depth)
        return graph

    def as_matrix(self, depth=0):
        """
        Create a matrix with self as node, cache it, return it.

        Args:
            depth (int): depth of the matrix.

        Returns:
            Matrix: an instance of Matrix.
        """
        if depth in self._matrix_cache:
            return self._matrix_cache[depth]
        self._matrix_cache[depth] = matrix = Matrix(self, depth=depth)
        return matrix

    def as_treemap(self):
        """
        Return the dependencies as a TreeMap.

        Returns:
            TreeMap: instance of TreeMap.
        """
        if self._treemap_cache:
            return self._treemap_cache
        self._treemap_cache = treemap = TreeMap(self)
        return treemap


class LeafNode(object):
    """Shared code between Package and Module."""

    def __init__(self):
        """Initialization method."""
        self._depth_cache = None

    def __str__(self):
        """String method."""
        return self.absolute_name()

    @property
    def root(self):
        """
        Property to return the root of this node.

        Returns:
            Package: this node's root package.
        """
        node = self
        while node.package is not None:
            node = node.package
        return node

    @property
    def depth(self):
        """
        Property to tell the depth of the node in the tree.

        Returns:
            int: the node's depth in the tree.
        """
        if self._depth_cache is not None:
            return self._depth_cache
        depth, node = 1, self
        while node.package is not None:
            depth += 1
            node = node.package
        self._depth_cache = depth
        return depth

    def absolute_name(self, depth=0):
        """
        Return the absolute name of the node.

        Concatenate names from root to self within depth.

        Args:
            depth (int): maximum depth to go to.

        Returns:
            str: absolute name of the node (until given depth is reached).
        """
        node, node_depth = self, self.depth
        if depth < 1:
            depth = node_depth
        while node_depth > depth and node.package is not None:
            node = node.package
            node_depth -= 1
        names = []
        while node is not None:
            names.append(node.name)
            node = node.package
        return '.'.join(reversed(names))
