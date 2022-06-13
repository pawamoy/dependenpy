"""dependenpy node module."""

from __future__ import annotations

import json
import sys
from typing import IO, TYPE_CHECKING, Any

from dependenpy.structures import Graph, Matrix, TreeMap

if TYPE_CHECKING:
    from dependenpy.dsm import Module, Package


class NodeMixin(object):
    """Shared code between DSM, Package and Module."""

    @property
    def ismodule(self) -> bool:
        """
        Property to check if object is instance of Module.

        Returns:
            Whether this object is a module.
        """
        return False

    @property
    def ispackage(self) -> bool:
        """
        Property to check if object is instance of Package.

        Returns:
            Whether this object is a package.
        """
        return False

    @property
    def isdsm(self) -> bool:
        """
        Property to check if object is instance of DSM.

        Returns:
            Whether this object is a DSM.
        """
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

    def __contains__(self, item: Package | Module) -> bool:
        """
        Get result of _contains, cache it and return it.

        Args:
            item: A package or module.

        Returns:
            True if self contains item, False otherwise.
        """
        if item not in self._contains_cache:
            self._contains_cache[item] = self._contains(item)
        return self._contains_cache[item]

    def __getitem__(self, item: str) -> Package | Module:  # noqa: WPS231
        """
        Return the corresponding Package or Module object.

        Args:
            item: Name of the package/module, dot-separated.

        Raises:
            KeyError: When the package or module cannot be found.

        Returns:
            The corresponding object.
        """
        depth = item.count(".") + 1
        parts = item.split(".", 1)
        for module in self.modules:
            if parts[0] == module.name:
                if depth == 1:
                    return module
        for package in self.packages:
            if parts[0] == package.name:
                if depth == 1:
                    return package
                obj = package.get(parts[1])
                if obj:
                    return obj
        raise KeyError(item)

    def __bool__(self) -> bool:
        """
        Node as Boolean.

        Returns:
            Result of node.empty.

        """
        return bool(self.modules or self.packages)

    @property
    def empty(self) -> bool:
        """
        Whether the node has neither modules nor packages.

        Returns:
            True if empty, False otherwise.
        """
        return not bool(self)

    @property
    def submodules(self) -> list[Module]:
        """
        Property to return all sub-modules of the node, recursively.

        Returns:
            The sub-modules.
        """
        submodules = []
        submodules.extend(self.modules)
        for package in self.packages:
            submodules.extend(package.submodules)
        return submodules

    def build_tree(self):
        """To be overridden."""  # noqa: DAR401
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
        for module in self.modules:
            if item in module:
                return True
        for package in self.packages:
            if item in package:
                return True
        return False

    def get(self, item: str) -> Package | Module:
        """
        Get item through `__getitem__` and cache the result.

        Args:
            item: Name of package or module.

        Returns:
            The corresponding object.
        """
        if item not in self._item_cache:
            try:
                obj = self.__getitem__(item)
            except KeyError:
                obj = None
            self._item_cache[item] = obj
        return self._item_cache[item]

    def get_target(self, target: str) -> Package | Module:
        """
        Get the result of _get_target, cache it and return it.

        Args:
            target: Target to find.

        Returns:
            Package containing target or corresponding module.
        """
        if target not in self._target_cache:
            self._target_cache[target] = self._get_target(target)
        return self._target_cache[target]

    def _get_target(self, target):  # noqa: WPS231
        """
        Get the Package or Module related to given target.

        Args:
            target (str): target to find.

        Returns:
            Package/Module: package containing target or corresponding module.
        """
        depth = target.count(".") + 1
        parts = target.split(".", 1)
        for module in self.modules:
            if parts[0] == module.name:
                if depth < 3:
                    return module
        for package in self.packages:
            if parts[0] == package.name:
                if depth == 1:
                    return package
                target = package._get_target(parts[1])  # noqa: WPS437
                if target:
                    return target
                # FIXME: can lead to internal dep instead of external
                # see example with django.contrib.auth.forms
                # importing forms from django
                # Idea: when parsing files with ast, record what objects
                # are defined in the module. Then check here if the given
                # part is one of these objects.
                if depth < 3:
                    return package
        return None

    def build_dependencies(self):
        """
        Recursively build the dependencies for sub-modules and sub-packages.

        Iterate on node's modules then packages and call their
        build_dependencies methods.
        """
        for module in self.modules:
            module.build_dependencies()
        for package in self.packages:
            package.build_dependencies()

    def print_graph(
        self, format: str | None = None, output: IO = sys.stdout, depth: int = 0, **kwargs: Any  # noqa: A002
    ):
        """
        Print the graph for self's nodes.

        Args:
            format: Output format (csv, json or text).
            output: File descriptor on which to write.
            depth: Depth of the graph.
            **kwargs: Additional keyword arguments passed to `graph.print`.
        """
        graph = self.as_graph(depth=depth)
        graph.print(format=format, output=output, **kwargs)

    def print_matrix(
        self, format: str | None = None, output: IO = sys.stdout, depth: int = 0, **kwargs: Any  # noqa: A002
    ):
        """
        Print the matrix for self's nodes.

        Args:
            format: Output format (csv, json or text).
            output: File descriptor on which to write.
            depth: Depth of the matrix.
            **kwargs: Additional keyword arguments passed to `matrix.print`.
        """
        matrix = self.as_matrix(depth=depth)
        matrix.print(format=format, output=output, **kwargs)

    def print_treemap(self, format: str | None = None, output: IO = sys.stdout, **kwargs: Any):  # noqa: A002
        """
        Print the matrix for self's nodes.

        Args:
            format: Output format (csv, json or text).
            output: File descriptor on which to write.
            **kwargs: Additional keyword arguments passed to `treemap.print`.
        """
        treemap = self.as_treemap()
        treemap.print(format=format, output=output, **kwargs)

    def _to_text(self, **kwargs):
        indent = kwargs.pop("indent", 2)
        base_indent = kwargs.pop("base_indent", None)
        if base_indent is None:
            base_indent = indent
            indent = 0
        text = [" " * indent + str(self) + "\n"]
        new_indent = indent + base_indent
        for module in self.modules:
            text.append(module._to_text(indent=new_indent, base_indent=base_indent))  # noqa: WPS437
        for package in self.packages:
            text.append(package._to_text(indent=new_indent, base_indent=base_indent))  # noqa: WPS437
        return "".join(text)

    def _to_csv(self, **kwargs):
        header = kwargs.pop("header", True)
        modules = sorted(self.submodules, key=lambda mod: mod.absolute_name())
        text = ["module,path,target,lineno,what,external\n" if header else ""]
        for module in modules:
            text.append(module._to_csv(header=False))  # noqa: WPS437
        return "".join(text)

    def _to_json(self, **kwargs):
        return json.dumps(self.as_dict(), **kwargs)

    def as_dict(self) -> dict:
        """
        Return the dependencies as a dictionary.

        Returns:
            Dictionary of dependencies.
        """
        return {
            "name": str(self),
            "modules": [module.as_dict() for module in self.modules],
            "packages": [package.as_dict() for package in self.packages],
        }

    def as_graph(self, depth: int = 0) -> Graph:
        """
        Create a graph with self as node, cache it, return it.

        Args:
            depth: Depth of the graph.

        Returns:
            An instance of Graph.
        """
        if depth not in self._graph_cache:
            self._graph_cache[depth] = Graph(self, depth=depth)
        return self._graph_cache[depth]

    def as_matrix(self, depth: int = 0) -> Matrix:
        """
        Create a matrix with self as node, cache it, return it.

        Args:
            depth: Depth of the matrix.

        Returns:
            An instance of Matrix.
        """
        if depth not in self._matrix_cache:
            self._matrix_cache[depth] = Matrix(self, depth=depth)  # type: ignore[arg-type]
        return self._matrix_cache[depth]

    def as_treemap(self) -> TreeMap:
        """
        Return the dependencies as a TreeMap.

        Returns:
            An instance of TreeMap.
        """
        if not self._treemap_cache:
            self._treemap_cache = TreeMap(self)
        return self._treemap_cache


class LeafNode(object):
    """Shared code between Package and Module."""

    def __init__(self):
        """Initialization method."""
        self._depth_cache = None

    def __str__(self):
        return self.absolute_name()

    @property
    def root(self) -> Package:
        """
        Property to return the root of this node.

        Returns:
            Package: this node's root package.
        """
        node: Package = self  # type: ignore[assignment]
        while node.package is not None:
            node = node.package
        return node

    @property
    def depth(self) -> int:
        """
        Property to tell the depth of the node in the tree.

        Returns:
            The node's depth in the tree.
        """
        if self._depth_cache is not None:
            return self._depth_cache
        node: Package
        depth, node = 1, self  # type: ignore[assignment]
        while node.package is not None:
            depth += 1
            node = node.package
        self._depth_cache = depth
        return depth

    def absolute_name(self, depth: int = 0) -> str:
        """
        Return the absolute name of the node.

        Concatenate names from root to self within depth.

        Args:
            depth: Maximum depth to go to.

        Returns:
            Absolute name of the node (until given depth is reached).
        """
        node: Package
        node, node_depth = self, self.depth  # type: ignore[assignment]
        if depth < 1:
            depth = node_depth
        while node_depth > depth and node.package is not None:
            node = node.package
            node_depth -= 1
        names = []
        while node is not None:
            names.append(node.name)
            node = node.package  # type: ignore[assignment]
        return ".".join(reversed(names))
