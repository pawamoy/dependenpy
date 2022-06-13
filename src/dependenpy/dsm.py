"""
dependenpy dsm module.

This is the core module of dependenpy. It contains the following classes:

- [`DSM`][dependenpy.dsm.DSM]: to create a DSM-capable object for a list of packages,
- [`Package`][dependenpy.dsm.Package]: which represents a Python package,
- [`Module`][dependenpy.dsm.Module]: which represents a Python module,
- [`Dependency`][dependenpy.dsm.Dependency]: which represents a dependency between two modules.
"""

from __future__ import annotations

import ast
import json
import sys
from os import listdir
from os.path import isdir, isfile, join, splitext
from pathlib import Path
from typing import List

from dependenpy.finder import Finder, PackageSpec
from dependenpy.helpers import PrintMixin
from dependenpy.node import LeafNode, NodeMixin, RootNode


class DSM(RootNode, NodeMixin, PrintMixin):
    """
    DSM-capable class.

    Technically speaking, a DSM instance is not a real DSM but more a tree
    representing the Python packages structure. However, it has the
    necessary methods to build a real DSM in the form of a square matrix,
    a dictionary or a tree-map.
    """

    def __init__(
        self, *packages: str, build_tree: bool = True, build_dependencies: bool = True, enforce_init: bool = True
    ):
        """
        Initialization method.

        Args:
            *packages: list of packages to search for.
            build_tree: auto-build the tree or not.
            build_dependencies: auto-build the dependencies or not.
            enforce_init: if True, only treat directories if they contain an `__init__.py` file.
        """
        self.base_packages = packages
        self.finder = Finder()
        self.specs = []
        self.not_found = []
        self.enforce_init = enforce_init

        specs = []
        for package in packages:
            spec = self.finder.find(package, enforce_init=enforce_init)
            if spec:
                specs.append(spec)
            else:
                self.not_found.append(package)

        if not specs:
            print("** dependenpy: DSM empty.", file=sys.stderr)

        self.specs = PackageSpec.combine(specs)

        for module in self.not_found:
            print(f"** dependenpy: Not found: {module}.", file=sys.stderr)

        super().__init__(build_tree)

        if build_tree and build_dependencies:
            self.build_dependencies()

    def __str__(self):
        packages_names = ", ".join([package.name for package in self.packages])
        return f"Dependency DSM for packages: [{packages_names}]"

    @property
    def isdsm(self) -> bool:
        """
        Inherited from NodeMixin. Always True.

        Returns:
            Whether this object is a DSM.
        """
        return True

    def build_tree(self):
        """Build the Python packages tree."""
        for spec in self.specs:
            if spec.ismodule:
                self.modules.append(Module(spec.name, spec.path, dsm=self))
            else:
                self.packages.append(
                    Package(
                        spec.name,
                        spec.path,
                        dsm=self,
                        limit_to=spec.limit_to,
                        build_tree=True,
                        build_dependencies=False,
                        enforce_init=self.enforce_init,
                    )
                )


class Package(RootNode, LeafNode, NodeMixin, PrintMixin):  # noqa: WPS215
    """
    Package class.

    This class represent Python packages as nodes in a tree.
    """

    def __init__(
        self,
        name: str,
        path: str,
        dsm: DSM = None,
        package: "Package" = None,
        limit_to: List[str] = None,
        build_tree: bool = True,
        build_dependencies: bool = True,
        enforce_init: bool = True,
    ):
        """
        Initialization method.

        Args:
            name: name of the package.
            path: path to the package.
            dsm: parent DSM.
            package: parent package.
            limit_to: list of string to limit the recursive tree-building to what is specified.
            build_tree: auto-build the tree or not.
            build_dependencies: auto-build the dependencies or not.
            enforce_init: if True, only treat directories if they contain an `__init__.py` file.
        """
        self.name = name
        self.path = path
        self.package = package
        self.dsm = dsm
        self.limit_to = limit_to or []
        self.enforce_init = enforce_init

        RootNode.__init__(self, build_tree)  # noqa: WPS609
        LeafNode.__init__(self)  # noqa: WPS609

        if build_tree and build_dependencies:
            self.build_dependencies()

    @property
    def ispackage(self) -> bool:
        """
        Inherited from NodeMixin. Always True.

        Returns:
            Whether this object is a package.
        """
        return True

    @property
    def issubpackage(self) -> bool:
        """
        Property to tell if this node is a sub-package.

        Returns:
            This package has a parent.
        """
        return self.package is not None

    @property
    def isroot(self) -> bool:
        """
        Property to tell if this node is a root node.

        Returns:
            This package has no parent.
        """
        return self.package is None

    def split_limits_heads(self) -> tuple[list[str], list[str]]:
        """
        Return first parts of dot-separated strings, and rest of strings.

        Returns:
            The heads and rest of the strings.
        """
        heads = []
        new_limit_to = []
        for limit in self.limit_to:
            if "." in limit:
                name, limit = limit.split(".", 1)  # noqa: WPS440
                heads.append(name)
                new_limit_to.append(limit)
            else:
                heads.append(limit)
        return heads, new_limit_to

    def build_tree(self):  # noqa: WPS231
        """Build the tree for this package."""
        for module in listdir(self.path):
            abs_m = join(self.path, module)
            if isfile(abs_m) and module.endswith(".py"):
                name = splitext(module)[0]
                if not self.limit_to or name in self.limit_to:
                    self.modules.append(Module(name, abs_m, self.dsm, self))
            elif isdir(abs_m):
                if isfile(join(abs_m, "__init__.py")) or not self.enforce_init:
                    heads, new_limit_to = self.split_limits_heads()
                    if not heads or module in heads:
                        self.packages.append(
                            Package(
                                module,
                                abs_m,
                                self.dsm,
                                self,
                                new_limit_to,
                                build_tree=True,
                                build_dependencies=False,
                                enforce_init=self.enforce_init,
                            )
                        )

    def cardinal(self, to) -> int:
        """
        Return the number of dependencies of this package to the given node.

        Args:
            to (Package/Module): target node.

        Returns:
            Number of dependencies.
        """
        return sum(module.cardinal(to) for module in self.submodules)


class Module(LeafNode, NodeMixin, PrintMixin):  # noqa: WPS338
    """
    Module class.

    This class represents a Python module (a Python file).
    """

    RECURSIVE_NODES = (ast.ClassDef, ast.FunctionDef, ast.If, ast.IfExp, ast.Try, ast.With, ast.ExceptHandler)

    def __init__(self, name, path, dsm=None, package=None):
        """
        Initialization method.

        Args:
            name (str): name of the module.
            path (str): path to the module.
            dsm (DSM): parent DSM.
            package (Package): parent Package.
        """
        super().__init__()
        self.name = name
        self.path = path
        self.package = package
        self.dsm = dsm
        self.dependencies = []

    def __contains__(self, item) -> bool:
        """
        Whether given item is contained inside this module.

        Args:
            item (Package/Module): a package or module.

        Returns:
            True if self is item or item is self's package and
                self if an `__init__` module.
        """
        if self is item:
            return True
        elif self.package is item and self.name == "__init__":
            return True
        return False

    @property
    def ismodule(self) -> bool:
        """
        Inherited from NodeMixin. Always True.

        Returns:
            Whether this object is a module.
        """
        return True

    def as_dict(self, absolute: bool = False) -> dict:
        """
        Return the dependencies as a dictionary.

        Arguments:
            absolute: Whether to use the absolute name.

        Returns:
            dict: dictionary of dependencies.
        """
        return {
            "name": self.absolute_name() if absolute else self.name,
            "path": self.path,
            "dependencies": [
                {
                    # 'source': d.source.absolute_name(),  # redundant
                    "target": dep.target if dep.external else dep.target.absolute_name(),
                    "lineno": dep.lineno,
                    "what": dep.what,
                    "external": dep.external,
                }
                for dep in self.dependencies
            ],
        }

    def _to_text(self, **kwargs):
        indent = kwargs.pop("indent", 2)
        base_indent = kwargs.pop("base_indent", None)
        if base_indent is None:
            base_indent = indent
            indent = 0
        text = [" " * indent + self.name + "\n"]
        new_indent = indent + base_indent
        for dep in self.dependencies:
            external = "! " if dep.external else ""
            text.append(" " * new_indent + external + str(dep) + "\n")
        return "".join(text)

    def _to_csv(self, **kwargs):
        header = kwargs.pop("header", True)
        text = ["module,path,target,lineno,what,external\n" if header else ""]
        name = self.absolute_name()
        for dep in self.dependencies:
            target = dep.target if dep.external else dep.target.absolute_name()
            text.append(f"{name},{self.path},{target},{dep.lineno},{dep.what or ''},{dep.external}\n")
        return "".join(text)

    def _to_json(self, **kwargs):
        absolute = kwargs.pop("absolute", False)
        return json.dumps(self.as_dict(absolute=absolute), **kwargs)

    def build_dependencies(self):
        """
        Build the dependencies for this module.

        Parse the code with ast, find all the import statements, convert
        them into Dependency objects.
        """
        highest = self.dsm or self.root
        if self is highest:
            highest = LeafNode()
        for import_ in self.parse_code():
            target = highest.get_target(import_["target"])
            if target:
                what = import_["target"].split(".")[-1]
                if what != target.name:
                    import_["what"] = what
                import_["target"] = target
            self.dependencies.append(Dependency(source=self, **import_))

    def parse_code(self) -> list[dict]:
        """
        Read the source code and return all the import statements.

        Returns:
            list of dict: the import statements.
        """
        code = Path(self.path).read_text(encoding="utf-8")
        try:
            body = ast.parse(code).body
        except SyntaxError:
            code = code.encode("utf-8")  # type: ignore[assignment]
            try:  # noqa: WPS505
                body = ast.parse(code).body
            except SyntaxError:
                return []
        return self.get_imports(body)

    def get_imports(self, ast_body) -> list[dict]:  # noqa: WPS231,WPS615
        """
        Return all the import statements given an AST body (AST nodes).

        Args:
            ast_body (compiled code's body): the body to filter.

        Returns:
            The import statements.
        """
        imports: list[dict] = []
        for node in ast_body:
            if isinstance(node, ast.Import):
                imports.extend({"target": name.name, "lineno": node.lineno} for name in node.names)
            elif isinstance(node, ast.ImportFrom):
                for name in node.names:
                    abs_name = self.absolute_name(self.depth - node.level) + "." if node.level > 0 else ""
                    node_module = node.module + "." if node.module else ""
                    name = abs_name + node_module + name.name  # type: ignore[assignment]
                    imports.append({"target": name, "lineno": node.lineno})
            elif isinstance(node, Module.RECURSIVE_NODES):
                imports.extend(self.get_imports(node.body))
                if isinstance(node, ast.Try):
                    imports.extend(self.get_imports(node.finalbody))
        return imports

    def cardinal(self, to) -> int:
        """
        Return the number of dependencies of this module to the given node.

        Args:
            to (Package/Module): the target node.

        Returns:
            Number of dependencies.
        """
        return len([dep for dep in self.dependencies if not dep.external and dep.target in to])


class Dependency(object):
    """
    Dependency class.

    Represent a dependency from a module to another.
    """

    def __init__(self, source, lineno, target, what=None):
        """
        Initialization method.

        Args:
            source (Module): source Module.
            lineno (int): number of line at which import statement occurs.
            target (str/Module/Package): the target node.
            what (str): what is imported (optional).
        """
        self.source = source
        self.lineno = lineno
        self.target = target
        self.what = what

    def __str__(self):
        what = f"{self.what or ''} from "
        target = self.target if self.external else self.target.absolute_name()
        return f"{self.source.name} imports {what}{target} (line {self.lineno})"

    @property
    def external(self) -> bool:
        """
        Property to tell if the dependency's target is a valid node.

        Returns:
            Whether the dependency's target is a valid node.
        """
        return isinstance(self.target, str)
