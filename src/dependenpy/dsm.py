# -*- coding: utf-8 -*-

"""
dependenpy dsm module.

This is the core module of dependenpy. It contains the following classes:

- ``DSM``: to create a DSM-capable object for a list of packages,
- ``Package``: which represents a Python package,
- ``Module``: which represents a Python module,
- ``Dependency``: which represents a dependency between two modules,
- ``Matrix``: to create a matrix (two-dimensions square array plus keys) given
  a list of DSMs, packages and/or modules.

It also contains private classes to share some code between ``DSM``,
``Package`` and ``Module``: ``_Node``, ``_DSMPackageNode`` and
``_PackageModuleNode``. They are called nodes because the layout of a Python
package is a tree.
"""

import ast
import json
import os
import sys
from os.path import isdir, isfile, join, splitext

from .finder import PackageFinder, PackageSpec


CSV = 'csv'
JSON = 'json'
TEXT = 'text'
FORMAT = (CSV, JSON, TEXT)


class _PrintMixin(object):
    def print(self, output=sys.stdout, format=TEXT, **kwargs):
        """
        Print the object in a file or on standard output by default.

        Args:
            format (str): output format (csv, json or text).
            output (file):
                descriptor to an opened file (default to standard output).
            **kwargs (): additional arguments.
        """
        if format == TEXT:
            print(self._to_text(**kwargs), file=output)
        elif format == CSV:
            print(self._to_csv(**kwargs), file=output)
        elif format == JSON:
            print(self._to_json(**kwargs), file=output)

    def _to_text(self, **kwargs):
        raise NotImplementedError

    def _to_csv(self, **kwargs):
        raise NotImplementedError

    def _to_json(self, **kwargs):
        raise NotImplementedError


class _Node(object):
    """Shared code between DSM, Package and Module."""

    @property
    def ismodule(self):
        """Property to check if object is instance of Module."""
        return isinstance(self, Module)

    @property
    def ispackage(self):
        """Property to check if object is instance of Package."""
        return isinstance(self, Package)

    @property
    def isdsm(self):
        """Property to check if object is instance of DSM."""
        return isinstance(self, DSM)


class _DSMPackageNode(_Node):
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
        """To be overriden."""
        pass

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

    def print_matrix(self, format=TEXT, output=sys.stdout, depth=0, **kwargs):
        """
        Print the matrix for self's nodes.

        Args:
            format (str): output format (csv, json or text).
            output (file): file descriptor on which to write.
            depth (int): depth of the matrix.
        """
        matrix = self.as_matrix(depth=depth)
        matrix.print(format=format, output=output, **kwargs)

    def print_treemap(self, format=TEXT, output=sys.stdout, **kwargs):
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


class _PackageModuleNode(_Node):
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


class DSM(_DSMPackageNode, _PrintMixin):
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
        self.finder = PackageFinder()
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
        """String method."""
        return 'Dependency DSM for packages: [%s]' % ', '.join(
            [p.name for p in self.packages])

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


class Package(_DSMPackageNode, _PackageModuleNode, _PrintMixin):
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

        _DSMPackageNode.__init__(self, build_tree)
        _PackageModuleNode.__init__(self)

        if build_tree and build_dependencies:
            self.build_dependencies()

    @property
    def is_subpackage(self):
        """
        Property to tell if this node is a sub-package.

        Returns:
            bool: this package has a parent.
        """
        return self.package is not None

    @property
    def is_root(self):
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
        for m in os.listdir(self.path):
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


class Module(_PackageModuleNode, _PrintMixin):
    """
    Module class.

    This class represents a Python module (a Python file).
    """

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
            highest = _PackageModuleNode()
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
            elif isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                # recursion here to get semi-dynamic imports
                imports.extend(self.get_imports(node.body))
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
        """String method."""
        return '%s imports %s%s (line %s)' % (
            self.source.name,
            '%s from ' % self.what if self.what else '',
            self.target if self.external else self.target.absolute_name(),
            self.lineno)

    @property
    def external(self):
        """Property to tell if the dependency's target is a valid node."""
        return isinstance(self.target, str)


class Matrix(_PrintMixin):
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


class TreeMap(_PrintMixin):
    """TreeMap class."""

    def __init__(self, *nodes):
        """
        Initialization method.

        Arguments:
            *nodes (list of Node): the nodes from which to build the treemap.
        """
        pass  # TODO: implement TreeMap

    def _to_csv(self, **kwargs):
        return ''

    def _to_json(self, **kwargs):
        return ''

    def _to_text(self, **kwargs):
        return ''
