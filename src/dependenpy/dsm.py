# -*- coding: utf-8 -*-

"""dependenpy dsm module."""

import ast
import os
import sys
from copy import deepcopy
from importlib.util import find_spec
from os.path import basename, dirname, exists, isdir, isfile, join, splitext


# TODO: add warnings for errors
# TODO: add option to reference a module path from another
# (example: os.path = posixpath)
# TODO: handle wrong subpackages (os.wrong)
# TODO: make DSM a root node (share some code with Package)
# TODO: write serializers/formatters to output DSM


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

    def print(self, output=sys.stdout, dependencies=True, matrix=True, depth=0):
        if matrix:
            keys, matrix = self.as_matrix(depth=depth)
            max_key_length = max(len(k) for k in keys)
            max_dep_length = len(str(max(j for i in matrix for j in i)))
            key_index_length = len(str(len(keys)))
            column_length = max(key_index_length, max_dep_length)
            # first line spacing
            output.write((' %s||' % (' ' * (max_key_length + key_index_length + 4))))
            # first line headers
            for i, _ in enumerate(keys):
                output.write(('{:^%s}|' % column_length).format(i))
            output.write('\n')
            # line of dashes
            output.write((' %s-+-%s-++' % (
                '-' * max_key_length, '-' * key_index_length)))
            for i, _ in enumerate(keys):
                output.write(('%s+' % ('-' * column_length)))
            output.write('\n')
            # lines
            for i, k in enumerate(keys):
                output.write((' {:>%s} | {:>%s} ||' % (max_key_length, key_index_length)).format(k, i))
                for v in matrix[i]:
                    output.write(('{:>%s}|' % column_length).format(v))
                output.write('\n')
            output.write('\n')
        if dependencies:
            output.write(str(self) + '\n')
            for p in self.packages:
                p.print(output=output, indent='  ')
        output.flush()

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

    def as_matrix(self, depth=0):
        modules = self.modules

        if depth < 1:
            keys = modules
        else:
            keys = []
            for m in modules:
                if m.depth <= depth:
                    keys.append(m)
                    continue
                package = m.package
                while package.depth > depth and package.package:
                    package = package.package
                if package not in keys:
                    keys.append(package)

        size = len(keys)
        matrix = [[0 for _ in range(size)] for __ in range(size)]
        keys = sorted(keys, key=lambda k: k.absolute_name())

        if depth < 1:
            for i, k in enumerate(keys):
                k.index = i
            for i, k in enumerate(keys):
                for d in k.dependencies:
                    if d.external:
                        continue
                    if isinstance(d.target, Module):
                        matrix[i][d.target.index] += 1
                    elif isinstance(d.target, Package):
                        for m in d.target.modules:
                            if m.name == '__init__':
                                matrix[i][m.index] += 1
                                break
        else:
            for i, k in enumerate(keys):
                for j, l in enumerate(keys):
                    matrix[i][j] = k.cardinal(to=l)
        return [k.absolute_name() for k in keys], matrix

    def as_dict(self):
        modules = self.modules
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

    # def as_treemap(self):
    #     packages = self.packages
    #     size = len(packages)
    #     treemap = [[(0, None) for _ in range(size)] for __ in range(size)]
    #     for i, p in enumerate(packages):
    #         for j, q in enumerate(packages):
    #             treemap[i][j][1] =

    @property
    def modules(self):
        modules = []
        for p in self.packages:
            modules.extend(p.submodules)
        return modules

    def _reset_cache(self):
        self._cache = {}


class _TreeNode(object):
    def __init__(self):
        self._depth = None

    def __contains__(self, item):
        if self == item:
            return True
        return False

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

    def absolute_name(self, depth=0):
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

    def __contains__(self, item):
        if self == item:
            return True
        if item in self.submodules:
            return True
        return False

    def print(self, output=sys.stdout, indent=''):
        output.write(indent + str(self) + '\n')
        for m in self.modules:
            m.print(output=output, indent=indent + '  ')
        for sp in self.subpackages:
            sp.print(output=output, indent=indent + '  ')

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
        submodules.extend(self.modules)
        for sp in self.subpackages:
            submodules.extend(sp.modules)
            submodules.extend(sp.submodules)
        return submodules

    def _reset_cache(self):
        self._cache = {}

    def cardinal(self, to):
        count = 0
        for m in self.submodules:
            count += m.cardinal(to)
        return count


class Module(_TreeNode):
    def __init__(self, name, path, package):
        super().__init__()
        self.name = name
        self.path = path
        self.package = package
        self.dependencies = []

    def __str__(self):
        return self.name

    def print(self, output=sys.stdout, indent=''):
        output.write(indent + str(self) + '\n')
        for d in self.dependencies:
            external = '! ' if d.external else ''
            output.write(indent + '  ' + external + str(d) + '\n')

    def build_dependencies(self):
        dsm = self.package.dsm
        for _import in self.parse_code():
            target = dsm.get_target(_import['target'])
            if target:
                what = _import['target'].split('.')[-1]
                if what != target.name:
                    _import['what'] = what
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

    def cardinal(self, to):
        valid_dependencies = (d for d in self.dependencies if not d.external)
        count = 0
        for d in valid_dependencies:
            if d.target in to:
                count += 1
        return count


class Dependency(object):
    def __init__(self, source, lineno, target, what=None):
        self.source = source
        self.lineno = lineno
        self.target = target
        self.what = what

    def __str__(self):
        return '%s imports %s%s (line %s)' % (
            self.source,
            '%s from ' % self.what if self.what else '',
            self.target if self.external else self.target.absolute_name(),
            self.lineno)

    @property
    def external(self):
        return isinstance(self.target, str)
