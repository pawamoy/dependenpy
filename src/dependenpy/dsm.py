# -*- coding: utf-8 -*-

"""dependenpy dsm module."""

import ast
import os
import sys
from copy import deepcopy
from os.path import isdir, isfile, join, splitext

from .finder import PackageFinder, PackageSpec


# TODO: add warnings for errors
# TODO: add option to reference a module path from another
# (example: os.path = posixpath)
# TODO: handle wrong subpackages (os.wrong)
# TODO: make DSM a root node (share some code with Package)

class _DSMPackageSharedNode(object):
    def __init__(self, build_tree=True):
        self._target_cache = {}
        self._item_cache = {}
        self._contains_cache = {}
        self._build_tree = build_tree
        self.modules = []
        self.packages = []

        if build_tree:
            self.build_tree()

    def __contains__(self, item):
        if item not in self._contains_cache:
            self._contains_cache[item] = self._contains(item)
        return self._contains_cache[item]

    def __getitem__(self, item):
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

    @property
    def submodules(self):
        submodules = []
        submodules.extend(self.modules)
        for p in self.packages:
            submodules.extend(p.submodules)
        return submodules

    def build_tree(self):
        pass  # to be overriden

    def _contains(self, item):
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
        if item not in self._item_cache:
            try:
                item = self.__getitem__(item)
            except KeyError:
                item = None
            self._item_cache[item] = item
        return self._item_cache[item]

    def get_target(self, target):
        if target not in self._target_cache:
            self._target_cache[target] = self._get_target(target)
        return self._target_cache[target]

    def _get_target(self, target):
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
                target = p._get_target(parts[1])
                if target:
                    return target
                if depth < 3:
                    return p
        return None

    def build_dependencies(self):
        for m in self.modules:
            m.build_dependencies()
        for p in self.packages:
            p.build_dependencies()

    def print(self,
              output=sys.stdout,
              matrix=True,
              dependencies=True,
              depth=0,
              indent=''):
        if matrix:
            self.print_matrix(output, depth)
        if dependencies:
            self.print_dependencies(output, indent)

    def print_matrix(self, output=sys.stdout, depth=0):
        keys, matrix = self.as_matrix(depth=depth)
        max_key_length = max(len(k) for k in keys)
        max_dep_length = len(str(max(j for i in matrix for j in i)))
        key_col_length = len(str(len(keys)))
        key_line_length = max(key_col_length, 2)
        column_length = max(key_col_length, max_dep_length)
        # first line left headers
        print((' {:>%s} | {:>%s} ||' % (
            max_key_length, key_line_length
        )).format('Module', 'Id'), file=output, end='')
        # first line column headers
        for i, _ in enumerate(keys):
            print(('{:^%s}|' % column_length).format(i),
                  file=output, end='')
        print('')
        # line of dashes
        print((' %s-+-%s-++' % ('-' * max_key_length,
                                '-' * key_line_length)),
              file=output, end='')
        for i, _ in enumerate(keys):
            print(('%s+' % ('-' * column_length)), file=output, end='')
        print('')
        # lines
        for i, k in enumerate(keys):
            print((' {:>%s} | {:>%s} ||' % (
                max_key_length, key_line_length
            )).format(k, i), file=output, end='')
            for v in matrix[i]:
                print(('{:>%s}|' % column_length).format(v),
                      file=output, end='')
            print('')
        print('')

    def print_dependencies(self, output=sys.stdout, indent=''):
        print(indent + str(self), file=output)
        for m in self.modules:
            m.print_dependencies(output=output, indent=indent + '  ')
        for p in self.packages:
            p.print_dependencies(output=output, indent=indent + '  ')

    def as_matrix(self, depth=0):
        modules = self.submodules

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
        # packages = self.packages
        # size = len(packages)
        # treemap = [[(0, None) for _ in range(size)] for __ in range(size)]
        # for i, p in enumerate(packages):
        #     for j, q in enumerate(packages):
        #         treemap[i][j][1] =
        pass


class _PackageModuleSharedNode(object):
    def __init__(self):
        self._depth_cache = None

    def __str__(self):
        return self.absolute_name()

    @property
    def root(self):
        node = self
        while node.package is not None:
            node = node.package
        return node

    @property
    def depth(self):
        if self._depth_cache is not None:
            return self._depth_cache
        depth, node = 1, self
        while node.package is not None:
            depth += 1
            node = node.package
        self._depth_cache = depth
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


class DSM(_DSMPackageSharedNode):
    def __init__(self, *packages, build_tree=True, build_dependencies=True):
        self.finder = PackageFinder()

        specs = []
        for package in packages:
            try:
                specs.append(self.finder.find(package))
            except ModuleNotFoundError:
                pass

        self.specs = PackageSpec.combine(specs)

        super().__init__(build_tree)

        if build_tree and build_dependencies:
            self.build_dependencies()

    def __str__(self):
        return 'Dependency DSM for packages: [%s]' % ', '.join(
            [p.name for p in self.packages])

    def build_tree(self):
        for spec in self.specs:
            if spec.ismodule:
                self.modules.append(Module(spec.name, spec.path, dsm=self))
            else:
                self.packages.append(Package(
                    spec.name, spec.path,
                    dsm=self, limit_to=spec.limit_to,
                    build_tree=self._build_tree,
                    build_dependencies=False))


class Package(_DSMPackageSharedNode, _PackageModuleSharedNode):
    def __init__(self,
                 name,
                 path,
                 dsm=None,
                 package=None,
                 limit_to=None,
                 build_tree=True,
                 build_dependencies=True):
        self.name = name
        self.path = path
        self.package = package
        self.dsm = dsm
        self.limit_to = limit_to or []

        _DSMPackageSharedNode.__init__(self, build_tree)
        _PackageModuleSharedNode.__init__(self)

        if build_tree and build_dependencies:
            self.build_dependencies()

    @property
    def is_subpackage(self):
        return self.package is not None

    @property
    def is_root(self):
        return self.package is None

    def build_tree(self):
        for m in os.listdir(self.path):
            abs_m = join(self.path, m)
            if isfile(abs_m) and m.endswith('.py'):
                name = splitext(m)[0]
                if not self.limit_to or name in self.limit_to:
                    self.modules.append(Module(name, abs_m, self.dsm, self))
            elif isdir(abs_m) and isfile(join(abs_m, '__init__.py')):
                names = []
                new_limit_to = []
                if self.limit_to:
                    for l in self.limit_to:
                        if '.' in l:
                            name, l = l.split('.')
                            names.append(name)
                            new_limit_to.append(l)
                        else:
                            names.append(l)
                if not names or m in names:
                    self.packages.append(
                        Package(m, abs_m, self.dsm, self, new_limit_to,
                                build_tree=self._build_tree,
                                build_dependencies=False))

    def cardinal(self, to):
        count = 0
        for m in self.submodules:
            count += m.cardinal(to)
        return count


class Module(_PackageModuleSharedNode):
    def __init__(self, name, path, dsm=None, package=None):
        super().__init__()
        self.name = name
        self.path = path
        self.package = package
        self.dsm = dsm
        self.dependencies = []

    # override _TreeNode's
    def __contains__(self, item):
        if self is item:
            return True
        elif self.package is item and self.name == '__init__':
            return True
        return False

    def print_dependencies(self, output=sys.stdout, indent=''):
        print(indent + self.name, file=output)
        for d in self.dependencies:
            external = '! ' if d.external else ''
            print(indent + '  ' + external + str(d), file=output)

    def build_dependencies(self):
        highest = self.dsm or self.root
        if self is highest:
            highest = _PackageModuleSharedNode()
        for _import in self.parse_code():
            target = highest.get_target(_import['target'])
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
