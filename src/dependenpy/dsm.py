# -*- coding: utf-8 -*-

"""
dependenpy dsm module.

This is the core module of dependenpy. It contains the following classes:

- :class:`DSM`: to create a DSM-capable object for a list of packages,
- :class:`Package`: which represents a Python package,
- :class:`Module`: which represents a Python module,
- :class:`Dependency`: which represents a dependency between two modules.
"""

import ast
import json
import sys
from os import listdir
from os.path import isdir, isfile, join, splitext

from .finder import Finder, PackageSpec
from .helpers import PrintMixin
from .node import LeafNode, NodeMixin, RootNode


class DSM(RootNode, NodeMixin, PrintMixin):
    """
    DSM-capable class.

    Technically speaking, a DSM instance is not a real DSM but more a tree
    representing the Python packages structure. However, it has the
    necessary methods to build a real DSM in the form of a square matrix,
    a dictionary or a tree-map.
    """

    def __init__(self,
                 *packages,
                 build_tree=True,
                 build_dependencies=True,
                 enforce_init=True):
        """
        Initialization method.

        Args:
            *packages (args): list of packages to search for.
            build_tree (bool): auto-build the tree or not.
            build_dependencies (bool): auto-build the dependencies or not.
            enforce_init (bool):
                if True, only treat directories if they contain an
                ``__init__.py`` file.
        """
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
            print('** dependenpy: DSM empty.', file=sys.stderr)

        self.specs = PackageSpec.combine(specs)

        for m in self.not_found:
            print('** dependenpy: Not found: %s.' % m, file=sys.stderr)

        super().__init__(build_tree)

        if build_tree and build_dependencies:
            self.build_dependencies()

    def __str__(self):
        return 'Dependency DSM for packages: [%s]' % ', '.join(
            [p.name for p in self.packages])

    @property
    def isdsm(self):
        """Inherited from NodeMixin. Always True."""
        return True

    def build_tree(self):
        """Build the Python packages tree."""
        for spec in self.specs:
            if spec.ismodule:
                self.modules.append(Module(spec.name, spec.path, dsm=self))
            else:
                self.packages.append(Package(
                    spec.name, spec.path,
                    dsm=self, limit_to=spec.limit_to,
                    build_tree=True,
                    build_dependencies=False,
                    enforce_init=self.enforce_init))


class Package(RootNode, LeafNode, NodeMixin, PrintMixin):
    """
    Package class.

    This class represent Python packages as nodes in a tree.
    """

    def __init__(self,
                 name,
                 path,
                 dsm=None,
                 package=None,
                 limit_to=None,
                 build_tree=True,
                 build_dependencies=True,
                 enforce_init=True):
        """
        Initialization method.

        Args:
            name (str): name of the package.
            path (str): path to the package.
            dsm (DSM): parent DSM.
            package (Package): parent package.
            limit_to (list of str):
                list of string to limit the recursive tree-building to
                what is specified.
            build_tree (bool): auto-build the tree or not.
            build_dependencies (bool): auto-build the dependencies or not.
            enforce_init (bool):
                if True, only treat directories if they contain an
                ``__init__.py`` file.
        """
        self.name = name
        self.path = path
        self.package = package
        self.dsm = dsm
        self.limit_to = limit_to or []
        self.enforce_init = enforce_init

        RootNode.__init__(self, build_tree)
        LeafNode.__init__(self)

        if build_tree and build_dependencies:
            self.build_dependencies()

    @property
    def ispackage(self):
        """Inherited from NodeMixin. Always True."""
        return True

    @property
    def issubpackage(self):
        """
        Property to tell if this node is a sub-package.

        Returns:
            bool: this package has a parent.
        """
        return self.package is not None

    @property
    def isroot(self):
        """
        Property to tell if this node is a root node.

        Returns:
            bool: this package has no parent.
        """
        return self.package is None

    def split_limits_heads(self):
        """
        Return first parts of dot-separated strings, and rest of strings.

        Returns:
            (list of str, list of str): the heads and rest of the strings.
        """
        heads = []
        new_limit_to = []
        for limit in self.limit_to:
            if '.' in limit:
                name, limit = limit.split('.', 1)
                heads.append(name)
                new_limit_to.append(limit)
            else:
                heads.append(limit)
        return heads, new_limit_to

    def build_tree(self):
        """Build the tree for this package."""
        for m in listdir(self.path):
            abs_m = join(self.path, m)
            if isfile(abs_m) and m.endswith('.py'):
                name = splitext(m)[0]
                if not self.limit_to or name in self.limit_to:
                    self.modules.append(Module(name, abs_m, self.dsm, self))
            elif isdir(abs_m):
                if isfile(join(abs_m, '__init__.py')) or not self.enforce_init:
                    heads, new_limit_to = self.split_limits_heads()
                    if not heads or m in heads:
                        self.packages.append(
                            Package(m, abs_m, self.dsm, self, new_limit_to,
                                    build_tree=True,
                                    build_dependencies=False,
                                    enforce_init=self.enforce_init))

    def cardinal(self, to):
        """
        Return the number of dependencies of this package to the given node.

        Args:
            to (Package/Module): target node.

        Returns:
            int: number of dependencies.
        """
        return sum(m.cardinal(to) for m in self.submodules)


class Module(LeafNode, NodeMixin, PrintMixin):
    """
    Module class.

    This class represents a Python module (a Python file).
    """

    RECURSIVE_NODES = (
        ast.ClassDef, ast.FunctionDef, ast.If, ast.IfExp, ast.Try,
        ast.With, ast.ExceptHandler)

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

    def __contains__(self, item):
        """
        Whether given item is contained inside this module.

        Args:
            item (Package/Module): a package or module.

        Returns:
            bool:
                True if self is item or item is self's package and
                self if an ``__init__`` module.
        """
        if self is item:
            return True
        elif self.package is item and self.name == '__init__':
            return True
        return False

    @property
    def ismodule(self):
        """Inherited from NodeMixin. Always True."""
        return True

    def as_dict(self, absolute=False):
        """
        Return the dependencies as a dictionary.

        Returns:
            dict: dictionary of dependencies.
        """
        return {
            'name': self.absolute_name() if absolute else self.name,
            'path': self.path,
            'dependencies': [{
                # 'source': d.source.absolute_name(),  # redundant
                'target': d.target if d.external else d.target.absolute_name(),
                'lineno': d.lineno,
                'what': d.what,
                'external': d.external
            } for d in self.dependencies]
        }

    def _to_text(self, **kwargs):
        indent = kwargs.pop('indent', 2)
        base_indent = kwargs.pop('base_indent', None)
        if base_indent is None:
            base_indent = indent
            indent = 0
        text = [' ' * indent + self.name + '\n']
        new_indent = indent + base_indent
        for d in self.dependencies:
            external = '! ' if d.external else ''
            text.append(' ' * new_indent + external + str(d) + '\n')
        return ''.join(text)

    def _to_csv(self, **kwargs):
        header = kwargs.pop('header', True)
        text = ['module,path,target,lineno,what,external\n' if header else '']
        name = self.absolute_name()
        for d in self.dependencies:
            text.append('%s,%s,%s,%s,%s,%s\n' % (
                name, self.path,
                d.target if d.external else d.target.absolute_name(),
                d.lineno, d.what if d.what else '', d.external
            ))
        return ''.join(text)

    def _to_json(self, **kwargs):
        absolute = kwargs.pop('absolute', False)
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
        for _import in self.parse_code():
            target = highest.get_target(_import['target'])
            if target:
                what = _import['target'].split('.')[-1]
                if what != target.name:
                    _import['what'] = what
                _import['target'] = target
            self.dependencies.append(Dependency(source=self, **_import))

    def parse_code(self):
        """
        Read the source code and return all the import statements.

        Returns:
            list of dict: the import statements.
        """
        code = open(self.path, encoding='utf-8').read()
        try:
            body = ast.parse(code).body
        except SyntaxError:
            try:
                code = code.encode('utf-8')
                body = ast.parse(code).body
            except SyntaxError:
                return []
        return self.get_imports(body)

    def get_imports(self, ast_body):
        """
        Return all the import statements given an AST body (AST nodes).

        Args:
            ast_body (compiled code's body): the body to filter.

        Returns:
            list of dict: the import statements.
        """
        imports = []
        for node in ast_body:
            if isinstance(node, ast.Import):
                imports.extend({'target': name.name, 'lineno': node.lineno}
                               for name in node.names)
            elif isinstance(node, ast.ImportFrom):
                for name in node.names:
                    name = (
                        self.absolute_name(self.depth - node.level) + '.'
                        if node.level > 0 else ''
                    ) + (
                        node.module + '.' if node.module else ''
                    ) + name.name
                    imports.append({'target': name, 'lineno': node.lineno})
            elif isinstance(node, Module.RECURSIVE_NODES):
                imports.extend(self.get_imports(node.body))
                if isinstance(node, ast.Try):
                    imports.extend(self.get_imports(node.finalbody))
        return imports

    def cardinal(self, to):
        """
        Return the number of dependencies of this module to the given node.

        Args:
            to (Package/Module): the target node.

        Returns:
            int: number of dependencies.
        """
        return sum(1 for _ in filter(
            lambda d: not d.external and d.target in to, self.dependencies))


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
        return '%s imports %s%s (line %s)' % (
            self.source.name,
            '%s from ' % self.what if self.what else '',
            self.target if self.external else self.target.absolute_name(),
            self.lineno)

    @property
    def external(self):
        """Property to tell if the dependency's target is a valid node."""
        return isinstance(self.target, str)
