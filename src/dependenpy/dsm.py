# -*- coding: utf-8 -*-

"""
dependenpy utils module.

This is the main and only module of dependenpy package.
"""

import ast
import os
from importlib.util import find_spec
from os.path import basename, dirname, exists, isdir, isfile, join, splitext


# TODO: add warnings for errors
# TODO: add option to reference a module path from another
# (example: os.path = posixpath)
# TODO: handle wrong subpackages (os.wrong)
# TODO: make DSM a root node (share some code with Package)

class DSM(object):
    def __init__(self, *packages):
        self._cache = {}
        self.packages = []
        for p in packages:
            if exists(p):
                if isdir(p) and isfile(join(p, '__init__.py')):
                    self.packages.append(Package(basename(p), p, self))
                elif isfile(p) and p.endswith('__init__.py'):
                    p = dirname(p)
                    self.packages.append(Package(basename(p), p, self))
            else:
                spec = find_spec(p)
                if spec is not None:
                    if spec.submodule_search_locations:
                        path = spec.submodule_search_locations[0]
                    elif spec.origin and spec.origin != 'built-in':
                        path = spec.origin
                    else:
                        continue
                    package = Package(spec.name, path, self)
                    self.packages.append(package)

    def __str__(self):
        return 'Dependency DSM for packages: [%s]' % ', '.join(
            [str(p) for p in self.packages])

    def print(self):
        print(self)
        for p in self.packages:
            p.print(indent='  ')

    def build_dependencies(self):
        for p in self.packages:
            p.build_dependencies()

    def get_target(self, target):
        if target not in self._cache:
            self._cache[target] = self._get_target(target)
        return self._cache[target]

    def _get_target(self, target):
        parts = target
        if isinstance(parts, str):
            parts = target.split('.')
        for p in self.packages:
            if parts[0] == p.name:
                if len(parts) == 1:
                    return p
                target = p.get_target(parts[1:])
                if target:
                    return target
                if len(parts) < 3:
                    return p
        return None

    def matrix(self, depth):
        matrix = [[0 for _ in range(len(self.modules))] for __ in range(len(self.modules))]
        modules = sorted(self.get_modules(depth), key=lambda x: x.absolute_name())
        for i, m in enumerate(modules):
            m.index = i
        for i, m in enumerate(modules):
            for d in m.dependencies:
                matrix[i][m.index] += 1

    @property
    def modules(self):
        modules = []
        for p in self.packages:
            modules.extend(p.modules)
            modules.extend(p.submodules)
        return modules

    def _reset_cache(self):
        self._cache = {}


class _TreeNode(object):
    def __init__(self):
        self._depth = None

    @property
    def root(self):
        node = self
        while node.package is not None:
            node = node.package
        return node

    @property
    def depth(self):
        if self._depth is not None:
            return self._depth
        depth, node = 1, self
        while node.package is not None:
            depth += 1
            node = node.package
        self._depth = depth
        return depth

    def absolute_name(self, depth=-1):
        node, node_depth = self, self.depth
        if depth < 0:
            depth = node_depth
        while node_depth > depth and node.package is not None:
            node = node.package
            node_depth -= 1
        names = []
        while node is not None:
            names.append(node.name)
            node = node.package
        return '.'.join(reversed(names))


class Package(_TreeNode):
    def __init__(self, name, path, dsm, package=None):
        super().__init__()
        self._cache = {}
        self.name = name
        self.path = path
        self.package = package
        self.subpackages = []
        self.modules = []
        self.dsm = dsm
        if isfile(path):
            self.modules.append(Module(name, path, self))
            return
        for m in os.listdir(path):
            abs_m = join(path, m)
            if isfile(abs_m) and m.endswith('.py'):
                self.modules.append(Module(
                    splitext(m)[0], abs_m, self))
            elif isdir(abs_m) and isfile(join(abs_m, '__init__.py')):
                self.subpackages.append(Package(m, abs_m, dsm, self))

    def __str__(self):
        return self.name

    def print(self, indent=''):
        print(indent + str(self))
        for m in self.modules:
            m.print(indent=indent + '  ')
        for sp in self.subpackages:
            sp.print(indent=indent + '  ')

    @property
    def is_subpackage(self):
        return self.package is not None

    @property
    def is_root(self):
        return self.package is None

    def build_dependencies(self):
        for m in self.modules:
            m.build_dependencies()
        for sp in self.subpackages:
            sp.build_dependencies()

    def get_target(self, target):
        parts = target
        if isinstance(parts, str):
            parts = target.split('.')
        for m in self.modules:
            if parts[0] == m.name:
                if len(parts) < 3:
                    return m
        for sp in self.subpackages:
            if parts[0] == sp.name:
                if len(parts) == 1:
                    return sp
                target = sp.get_target(parts[1:])
                if target:
                    return target
                if len(parts) < 3:
                    return sp
        return None

    @property
    def submodules(self):
        submodules = []
        for sp in self.subpackages:
            submodules.extend(sp.modules)
            submodules.extend(sp.submodules)
        return submodules

    def _reset_cache(self):
        self._cache = {}


class Module(_TreeNode):
    def __init__(self, name, path, package):
        super().__init__()
        self.name = name
        self.path = path
        self.package = package
        self.dependencies = []

    def __str__(self):
        return self.name

    def print(self, indent=''):
        print(indent + str(self))
        for d in self.dependencies:
            external = '! ' if d.external else ''
            print(indent + '  ' + external + str(d))

    def build_dependencies(self):
        dsm = self.package.dsm
        for _import in self.parse_code():
            target = dsm.get_target(_import['target'])
            if target:
                _import['target'] = target
            self.dependencies.append(Dependency(source=self, **_import))

    def parse_code(self):
        code = open(self.path, encoding='utf-8').read()
        try:
            body = ast.parse(code).body
        except SyntaxError:
            code = code.encode('utf-8')
            body = ast.parse(code).body
        return self.get_imports(body)

    def get_imports(self, ast_body):
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


class Dependency(object):
    def __init__(self, source, lineno, target):
        self.source = source
        self.lineno = lineno
        self.target = target

    def __str__(self):
        return '%s imports %s (line %s)' % (
            self.source,
            self.target if self.external else self.target.absolute_name(),
            self.lineno)

    @property
    def external(self):
        return isinstance(self.target, str)
