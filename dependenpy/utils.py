# -*- coding: utf-8 -*-

import os
import sys
import ast
import json
import csv
import collections


DEFAULT_OPTIONS = {
    'group_name': True,
    'group_index': True,
    'source_name': True,
    'source_index': True,
    'target_name': True,
    'target_index': True,
    'imports': True,
    'cardinal': True,
}


class DependencyMatrix:
    """A DependencyMatrix instance walks over modules in app_list to build
    its imports dictionnary. The call to compute_matrix will then build
    the matrices for all depths, i.e. the range from 1 to the maximum depth
    of all modules. A matrix for a specific depth regroups sub-modules that
    are deeper that this depth into their parent module. See this class as
    a square matrix allowing to zoom in and in into elements until max depth
    has been reached.
    """

    def __init__(self, packages, options=DEFAULT_OPTIONS):
        """Instantiate a DependencyMatrix object.
        :param packages: string / list / OrderedDict containing packages to scan
        """
        if isinstance(packages, str):
            self.packages = [[packages]]
            self.groups = None
        elif isinstance(packages, list):
            self.packages = [packages]
            self.groups = None
        elif isinstance(packages, collections.OrderedDict):
            self.packages = packages.values()
            self.groups = packages.keys()
        self.options = options
        self.modules = []
        self.imports = []
        self.max_depth = 0
        self._inside = {}

    def init_modules(self):
        """Build the extended module list by walking over the initial modules.
        Do not add external modules (only sub-modules of initial ones).
        """
        group = 0
        for package_group in self.packages:
            for package in package_group:
                module_path = self.resolve_path(package)
                if not module_path:
                    continue
                module_path = os.path.dirname(module_path)
                self.modules.extend(
                    self._walk(package, module_path, group))
            group += 1
        self.max_depth = max([len(m['name'].split('.')) for m in self.modules])

    def init_imports(self):
        if self.max_depth < 1:
            return
        source_index = 0
        for module in self.modules:
            imports_dicts = self._parse_imports(module)
            for key in imports_dicts.keys():
                target_index = self.module_index(key)
                self.imports.append({
                    'source_name': module['name'],
                    'source_index': source_index,
                    'target_index': target_index,
                    'target_name': self.modules[target_index]['name'],
                    'imports': imports_dicts[key],
                    'cardinal': len(imports_dicts[key]['import'])
                })
            source_index += 1

    def module_index(self, module):
        # we don't need to store results, since we have unique keys
        # see _parse_imports -> sum_from

        # case 1: module is already a target
        idx = 0
        for m in self.modules:
            if module == m['name']:
                return idx
            idx += 1
        # case 2: module is an __init__ target
        idx = 0
        for m in self.modules:
            if m['name'] == module+'.__init__':
                return idx
            idx += 1
        # case 3: module is a sub-module of a target
        idx = 0
        for m in self.modules:
            if module.startswith(m['name']+'.'):
                return idx
            idx += 1
        # should never reach this (see _parse_imports -> if is_inside(mod))
        return None

    def is_inside(self, module):
        pre_computed = self._inside.get(module, None)
        if pre_computed is not None:
            return pre_computed
        else:
            for package_group in self.packages:
                for package in package_group:
                    if module == package or module.startswith(package+'.'):
                        self._inside[module] = True
                        return True
            self._inside[module] = False
            return False

    def _parse_imports(self, module):
        """Return a list of dictionaries with importing module (by)
        and imported modules (from and import).
        :param module: dict containing module's path and name
        :return: the list of imports (as dicts following given options)
        """
        sum_from = collections.OrderedDict()
        code = open(module['path']).read()
        for node in ast.parse(code).body:
            if isinstance(node, ast.ImportFrom):
                if not node.module:
                    continue
                mod = node.module
                # We rebuild the module name if it is a relative import
                level = node.level
                if level > 0:
                    mod = os.path.splitext(module['name'])[0]
                    level -= 1
                    while level != 0:
                        mod = os.path.splitext(mod)[0]
                        level -= 1
                    mod += '.' + node.module
                if self.is_inside(mod):
                    if sum_from.get(mod, None):
                        sum_from[mod]['import'] += [n.name for n in node.names]
                    else:
                        sum_from[mod] = {
                            'by': module['name'],
                            'from': mod,
                            'import': [n.name for n in node.names]}
        return sum_from

    # @staticmethod
    # def _get_depth_dict(imports, max_depth):
    #     """Update a dictionary for a specific depth based on another dictionary.
    #     :param imports: *required* (dict); base dictionary
    #     :param max_depth: *required* (int); regroup all sub-modules deeper than max_depth
    #     :return: (dict); the new updated dictionary
    #     """
    #     new_dict = collections.OrderedDict()
    #     for key in imports.keys():
    #         value = imports[key]
    #         new_key = '.'.join(key.split('.')[:max_depth])
    #         if new_dict.get(new_key, None):
    #             new_dict[new_key].extend(value)
    #         else:
    #             new_dict[new_key] = value
    #     return new_dict

    def _walk(self, name, path, group, prefix=''):
        """Walk recursively into subdirectories of a directory and return a
        list of all Python files found (*.py).
        :param path: *required* (string); directory to scan
        :param prefix: *optional* (string); file paths prepended string
        :return: (list); the list of Python files
        """
        result = []
        for item in os.listdir(path):
            sub_item = os.path.join(path, item)
            if os.path.isdir(sub_item):
                result.extend(self._walk(
                    name, sub_item, group,
                    '%s%s/' % (prefix, os.path.basename(sub_item))))
            elif item.endswith('.py'):
                result.append({
                    'name': '%s.%s' % (
                        name, os.path.splitext(
                            prefix+item)[0].replace('/', '.')),
                    'path': sub_item,
                    'group_index': group,
                    'group_name': self.groups[group]
                })
        return result

    @staticmethod
    def resolve_path(mod):
        """Built-in method for getting a module's path within Python path.
        :param mod: *required* (string); the partial basename of the module
        :return: (string); the path to this module or None if not found
        """
        for path in sys.path:
            mod_path = os.path.join(path, mod.replace('.', '/'))
            if os.path.isdir(mod_path):
                mod_path += '/__init__.py'
                if os.path.exists(mod_path):
                    return mod_path
                return None
            elif os.path.exists(mod_path + '.py'):
                return mod_path + '.py'
        return None