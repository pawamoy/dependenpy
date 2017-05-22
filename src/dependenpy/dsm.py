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
import os
import sys
from copy import deepcopy
from os.path import isdir, isfile, join, splitext

from .finder import PackageFinder, PackageSpec


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

    def print(self,
              matrix=True,
              dependencies=True,
              output=sys.stdout,
              **kwargs):
        """
        Shortcut to call print methods.

        Args:
            matrix (bool): whether to print matrix or not.
            dependencies (bool): whether to print dependencies list or not.
            output (file): file descriptor on which to write.
            **kwargs (): additional keyword arguments to related print methods.
        """
        if matrix:
            depth = kwargs.pop('depth', 0)
            self.print_matrix(depth=depth, output=output)
        if dependencies:
            indent = kwargs.pop('indent', '')
            self.print_dependencies(indent=indent, output=output)

    def print_matrix(self, depth=0, output=sys.stdout):
        """
        Print the matrix for self's nodes.

        Args:
            depth (int): depth of the matrix.
            output (file): file descriptor on which to write.
        """
        matrix = self.as_matrix(depth=depth)
        matrix.print(output=output)

    def print_dependencies(self, indent='', output=sys.stdout):
        """
        Print the dependencies for self's nodes.

        Args:
            indent (str): indent as spaces (add two spaces each recursion).
            output (file): file descriptor on which to write.
        """
        print(indent + str(self), file=output)
        for m in self.modules:
            m.print_dependencies(indent=indent + '  ', output=output)
        for p in self.packages:
            p.print_dependencies(indent=indent + '  ', output=output)

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
        matrix = Matrix(self, depth=depth)
        self._matrix_cache[depth] = matrix
        return self._matrix_cache[depth]

    def as_dict(self):
        """
        Return the dependencies as a dictionary.

        Returns:
            dict: the dependencies.
        """
        modules = self.submodules
        dictionary = {}
        base_dict = {m.absolute_name(): 0 for m in modules}
        for m in modules:
            name = m.absolute_name()
            if dictionary.get(name, None) is None:
                dictionary[name] = deepcopy(base_dict)
            for d in m.dependencies:
                if isinstance(d.target, str):
                    continue
                target_name = d.target.absolute_name()
                dictionary[name][target_name] += 1
        return dictionary

    def as_treemap(self):
        """
        Return the dependencies as a TreeMap.

        Returns:
            TreeMap: instance of TreeMap.
        """
        # packages = self.packages
        # size = len(packages)
        # treemap = [[(0, None) for _ in range(size)] for __ in range(size)]
        # for i, p in enumerate(packages):
        #     for j, q in enumerate(packages):
        #         treemap[i][j][1] =
        pass


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


class DSM(_DSMPackageNode):
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


class Package(_DSMPackageNode, _PackageModuleNode):
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


class Module(_PackageModuleNode):
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

    def print_dependencies(self, indent='', output=sys.stdout):
        """
        Print the dependencies of this module.

        Args:
            output (file): opened file to write to.
            indent (str): indentation string.
        """
        print(indent + self.name, file=output)
        for d in self.dependencies:
            external = '! ' if d.external else ''
            print(indent + '  ' + external + str(d), file=output)

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


class Matrix(object):
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
                    if d.external or d.target.absolute_name() not in keys:
                        continue
                    if isinstance(d.target, Module):
                        data[i][d.target.index] += 1
                    elif isinstance(d.target, Package):
                        for m in d.target.modules:
                            if m.name == '__init__':
                                data[i][m.index] += 1
                                break
        else:
            for i, k in enumerate(keys):
                for j, l in enumerate(keys):
                    data[i][j] = k.cardinal(to=l)

        self.keys = [k.absolute_name() for k in keys]
        self.data = data

    def print(self, output=sys.stdout):
        """
        Print the matrix in a file or on standard output by default.

        Args:
            output (file):
                descriptor to an opened file (default to standard output).
        """
        max_key_length = max(len(k) for k in self.keys)
        max_dep_length = len(str(max(j for i in self.data for j in i)))
        key_col_length = len(str(len(self.keys)))
        key_line_length = max(key_col_length, 2)
        column_length = max(key_col_length, max_dep_length)
        print('', file=output)
        # first line left headers
        print((' {:>%s} | {:>%s} ||' % (
            max_key_length, key_line_length
        )).format('Module', 'Id'), file=output, end='')
        # first line column headers
        for i, _ in enumerate(self.keys):
            print(('{:^%s}|' % column_length).format(i),
                  file=output, end='')
        print('')
        # line of dashes
        print((' %s-+-%s-++' % ('-' * max_key_length,
                                '-' * key_line_length)),
              file=output, end='')
        for i, _ in enumerate(self.keys):
            print(('%s+' % ('-' * column_length)), file=output, end='')
        print('')
        # lines
        for i, k in enumerate(self.keys):
            print((' {:>%s} | {:>%s} ||' % (
                max_key_length, key_line_length
            )).format(k, i), file=output, end='')
            for v in self.data[i]:
                print(('{:>%s}|' % column_length).format(v),
                      file=output, end='')
            print('')
        print('')


class TreeMap(object):
    """TreeMap class."""
