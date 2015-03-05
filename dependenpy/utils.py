# -*- coding: utf-8 -*-

# Copyright (c) 2015 Timothée Mazzucotelli
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""dependenpy utils module.

This is the main and only module of dependenpy package.
This module contains:

    a class, DependencyMatrix: the class building your dependency matrix.
    a function, resolve_path: transforms a module name into an absolute path.
    a dictionary, DEFAULT_OPTIONS: contains the filter options for JSON output.

"""

import os
import sys
import ast
import json
import csv
import StringIO
import collections


#: Filter default options for JSON output
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


def resolve_path(module):
    """Built-in method for getting a module's path within Python path.

    :param module: str, the name of the module
    :return: str, absolute path to this module, None if not found
    """
    for path in sys.path:
        module_path = os.path.join(path, module.replace('.', os.sep))
        if os.path.isdir(module_path):
            module_path = '%s%s__init__.py' % (module_path, os.sep)
            if os.path.exists(module_path):
                return module_path
            return None
        elif os.path.exists(module_path + '.py'):
            return module_path + '.py'
    return None


# TODO: Add exclude option
# TODO: Replace OrderedDict by a list (easier to use)
class DependencyMatrix(object):
    """Dependency Matrix data builder.
    """

    def __init__(self, packages, path_resolver=resolve_path):
        """Instantiate a DependencyMatrix object.

        :param packages: str/list/OrderedDict: packages to scan
        :param path_resolver: callable, finds the absolute path of a module
        :raise AttributeError: when `packages` has wrong type
        """
        #: list of list of str: the packages used to build the data,
        #: optionally organized by groups
        self.packages = None
        self.groups = None  #: list of str: the names of the groups
        if isinstance(packages, str):
            self.packages = [[packages]]
            self.groups = ['']
        elif isinstance(packages, list):
            if all([isinstance(p, list) for p in packages]):
                self.packages = packages
            else:
                self.packages = [packages]
            self.groups = ['']
        elif isinstance(packages, collections.OrderedDict):
            self.packages = packages.values()
            self.groups = packages.keys()
        else:
            raise AttributeError
        #: callable: the method that find the path of a module
        self.path_resolver = path_resolver
        #: list of dict: the list of all packages' modules, containing
        #: name, path, group_index and group_name
        self.modules = []
        #: list of dict: the list of all modules' imports, containing
        #: cardinal, source_index, source_name, target_index, target_name,
        #: and imports dicts themselves (by, from, import)
        self.imports = []
        #: int: the maximum module depth
        self.max_depth = 0
        #: list of dict: one matrix for each depth, containing the
        #: list of modules and the list of imports
        self.matrices = []
        self._inside = {}
        self._modules_are_built = False
        self._imports_are_built = False
        self._matrices_are_built = False

    def __eq__(self, other):
        return all([self.packages == other.packages,
                    self.groups == other.groups,
                    self.max_depth == other.max_depth,
                    self.modules == other.modules,
                    self.imports == other.imports,
                    self.matrices == other.matrices,
                    self._inside == other._inside,
                    self._modules_are_built == other._modules_are_built,
                    self._imports_are_built == other._imports_are_built,
                    self._matrices_are_built == other._matrices_are_built])

    def build(self):
        """Shortcut for building modules, imports and matrices.

        :return: self, with built data
        """
        return self.build_modules().build_imports().build_matrices()

    def build_modules(self):
        """Build the module list with all python files in the given packages.
        Also compute the maximum depth.

        :return: self, with built modules
        """
        if self._modules_are_built:
            return self
        group = 0
        for package_group in self.packages:
            for package in package_group:
                module_path = self.path_resolver(package)
                if not module_path:
                    continue
                module_path = os.path.dirname(module_path)
                self.modules.extend(
                    self._walk(package, module_path, group))
            group += 1
        self.max_depth = max([len(m['name'].split('.')) for m in self.modules])
        self._modules_are_built = True
        return self

    def build_imports(self):
        """Build the big list of imports.

        :return: self, with built imports
        """
        if not self._modules_are_built or self._imports_are_built:
            return self
        source_index = 0
        for module in self.modules:
            imports_dicts = self.parse_imports(module)
            for key in imports_dicts.keys():
                target_index = self.module_index(key)
                # it happens sometimes (tricky/wrong imports in code)
                if target_index is not None:
                    self.imports.append({
                        'source_name': module['name'],
                        'source_index': source_index,
                        'target_index': target_index,
                        'target_name': self.modules[target_index]['name'],
                        'imports': [imports_dicts[key]],
                        'cardinal': len(imports_dicts[key]['import'])
                    })
            source_index += 1
        self._imports_are_built = True
        return self

    def build_matrices(self):
        """Build the matrices for each depth. Starts with the last one
        (maximum depth), and ascend through the levels
        until depth 1 is reached.

        :return: self, with built matrices
        """
        if not self._imports_are_built or self._matrices_are_built:
            return self
        md = self.max_depth
        self.matrices = [None for x in range(0, md)]
        self.matrices[md-1] = {'modules': self.modules,
                               'imports': self.imports}
        md -= 1
        while md > 0:
            self.matrices[md-1] = self._build_up_matrix(md)
            md -= 1
        self._matrices_are_built = True
        return self

    def module_index(self, module):
        """Return index of given (sub)module in the built list of modules.

        :param module: str, represents the module name (pack.mod.submod)
        :return: int, the index of the module, None if not found
        """
        # We don't need to store results, since we have unique keys
        # See parse_imports -> sum_from

        # FIXME: what is the most efficient? 3 loops with 1 comparison
        # or 1 loop with 3 comparisons? In the second case: are we sure
        # we get an EXACT result (order of comparisons)?

        # Case 1: module is already a target
        idx = 0
        for m in self.modules:
            if module == m['name']:
                return idx
            idx += 1
        # Case 2: module is an __init__ target
        idx = 0
        for m in self.modules:
            if m['name'] == module+'.__init__':
                return idx
            idx += 1
        # Case 3: module is the sub-module of a target
        idx = 0
        for m in self.modules:
            if module.startswith(m['name']+'.'):
                return idx
            idx += 1
        # We should never reach this (see parse_imports -> if contains(mod))
        return None

    def contains(self, module):
        """Check if the specified module is part of the packages list.

        :param module: str, represents the module name (pack.mod.submod)
        :return: bool, True if yes, False if not
        """
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

    def parse_imports(self, module, force=False):
        """Return a dictionary of dictionaries with importing module (by)
        and imported modules (from and import). Keys are the importing modules.

        :param module: dict, contains module's path and name
        :param force: bool, force append even if module is not part of packages
        :return: dict of dict, imports
        """
        sum_from = collections.OrderedDict()
        code = open(module['path']).read()
        for node in ast.parse(code).body:
            if isinstance(node, ast.ImportFrom):
                mod = node.module
                level = node.level
                # We ignore local imports (from . import)
                # But not up imports (from .. import)
                if not mod and level < 2:
                    continue
                # We rebuild the module name if it is a relative import
                # FIXME: what if it goes up higher than len(module.split('.'))?
                if level > 0:
                    mod = os.path.splitext(module['name'])[0]
                    level -= 1
                    while level != 0:
                        mod = os.path.splitext(mod)[0]
                        level -= 1
                    mod += '.' + node.module if node.module else ''
                if self.contains(mod) or force:
                    if sum_from.get(mod, None):
                        sum_from[mod]['import'] += [n.name for n in node.names]
                    else:
                        sum_from[mod] = {
                            'by': module['name'],
                            'from': mod,
                            'import': [n.name for n in node.names]}
        return sum_from

    def _build_up_matrix(self, down_level):
        """Build matrix data based on the matrix below it (with depth+1).

        :param down_level: int, depth of the below matrix
        :return: dict, matrix data
        """
        # First we build the new module list
        up_modules, up_imports = [], []
        seen_module, seen_import = {}, {}
        modules_indexes = {}
        index_old, index_new = 0, -1
        for m in self.matrices[down_level]['modules']:
            up_module = '.'.join(m['name'].split('.')[:down_level])
            # FIXME: We could maybe get rid of path...
            if seen_module.get(up_module, None) is not None:
                # seen_module[up_module]['path'] += ', ' + m['path']
                pass
            else:
                seen_module[up_module] = {
                    'name': up_module,
                    # 'path': m['path'],
                    'group_name': m['group_name'],
                    'group_index': m['group_index']
                }
                up_modules.append(seen_module[up_module])
                index_new += 1
            modules_indexes[index_old] = {'index': index_new,
                                          'name': up_module}
            index_old += 1

        # Then we build the new imports list
        for i in self.matrices[down_level]['imports']:
            new_source_index = modules_indexes[i['source_index']]['index']
            new_source_name = modules_indexes[i['source_index']]['name']
            new_target_index = modules_indexes[i['target_index']]['index']
            new_target_name = modules_indexes[i['target_index']]['name']
            seen_id = (new_source_index, new_target_index)
            if seen_import.get(seen_id, None) is not None:
                seen_import[seen_id]['cardinal'] += i['cardinal']
                seen_import[seen_id]['imports'] += i['imports']
            else:
                seen_import[seen_id] = {
                    'cardinal': i['cardinal'],
                    'imports': i['imports'],
                    'source_name': new_source_name,
                    'source_index': new_source_index,
                    'target_name': new_target_name,
                    'target_index': new_target_index,
                }
                up_imports.append(seen_import[seen_id])

        # We return the new dict of modules / imports
        return {'modules': up_modules, 'imports': up_imports}

    # TODO: Add exclude option
    def _walk(self, name, path, group, prefix=''):
        """Walk recursively into subdirectories of a package directory
        and return a list of all Python files found (*.py).

        :param name: str, name of the package
        :param path: str, path of the package
        :param group: int, group index of the package
        :param prefix: str, used by recursion, file paths prepended string
        :return: list of dict, contains name, path, group_index and group_name
        """
        result = []
        for item in os.listdir(path):
            sub_item = os.path.join(path, item)
            if os.path.isdir(sub_item):
                result.extend(self._walk(
                    name, sub_item, group,
                    '%s%s%s' % (prefix, os.path.basename(sub_item), os.sep)))
            elif item.endswith('.py'):
                result.append({
                    'name': '%s.%s' % (
                        name, os.path.splitext(
                            prefix+item)[0].replace(os.sep, '.')),
                    'path': sub_item,
                    'group_index': group,
                    'group_name': self.groups[group]
                })
        return result

    def to_json(self):
        """Return self as a JSON string (without path_resolver callable).
        This method is just a way to serialize the object itself.

        :return: str, a JSON dump of self
        """
        return json.dumps({
            'packages': self.packages,
            'groups': self.groups,
            # 'path_resolver': self.path_resolver,
            'modules': self.modules,
            'imports': self.imports,
            'max_depth': self.max_depth,
            'matrices': self.matrices,
            '_inside': self._inside,
            '_modules_are_built': self._modules_are_built,
            '_imports_are_built': self._imports_are_built,
            '_matrices_are_built': self._matrices_are_built,
        })

    @staticmethod
    def _option_filter(matrix, options):
        """Return a light version of matrix data based on given options.

        :param matrix: dict, a matrix from self.matrices
        :param options: dict of bool, keys are group_name, group_index,
            source_name, source_index, target_name, target_index,
            imports and cardinal
        :return: dict, the filtered matrix data
        """
        if not options['group_name']:
            for item in matrix['modules']:
                del item['group_name']
        if not options['group_index']:
            for item in matrix['modules']:
                del item['group_index']
        if not options['source_name']:
            for item in matrix['imports']:
                del item['source_name']
        if not options['source_index']:
            for item in matrix['imports']:
                del item['source_index']
        if not options['target_name']:
            for item in matrix['imports']:
                del item['target_name']
        if not options['target_index']:
            for item in matrix['imports']:
                del item['target_index']
        if not options['imports']:
            for item in matrix['imports']:
                del item['imports']
        if not options['cardinal']:
            for item in matrix['imports']:
                del item['cardinal']
        return matrix

    def get_matrix(self, matrix):
        """Return a copy of the specified matrix data.
        The given index is casted into [0 .. max_depth] range.

        :param matrix: int, index/depth. Zero means max_depth.
        :return: dict, copy of the matrix data
        """
        i = int(matrix)
        if i == 0 or i > self.max_depth:
            m = self.max_depth-1
        elif i < 0:
            m = 0
        else:
            m = i-1
        return dict(self.matrices[m])

    def matrix_to_json(self, matrix, options=DEFAULT_OPTIONS):
        """Return a matrix from self.matrices as a JSON string.

        :param matrix: int, index/depth of matrix (from 1 to max_depth,
            0 is equivalent to max_depth)
        :param options: dict, filter options
        :return: str, a JSON dump of the matrix data
        """
        return json.dumps(
            DependencyMatrix._option_filter(
                self.get_matrix(matrix), options))

    def matrix_to_csv(self, matrix, file_object=None):
        """Return a matrix from self.matrices as a CSV array. No filter options
        here because we output only the list of modules and the cardinals.

        :param matrix: int, index/depth of matrix (from 1 to max_depth,
            0 is equivalent to max_depth)
        :param file_object: File, if given, csv will write in this file object
            and return it modified instead of writing in a string buffer and
            return the text.
        :return: File, if file_object is given, else str
        """
        # where to write csv
        if file_object:
            si = None
            cw = csv.writer(file_object)
        else:
            si = StringIO.StringIO()
            cw = csv.writer(si)

        # matrix data
        data = self.get_matrix(matrix)

        # search for each cell, will be 0 if not found
        csv_cells = {}
        for i in data['imports']:
            csv_cells[(i['source_index'], i['target_index'])] = i['cardinal']

        # write the first line (columns)
        cw.writerow([''] + [m['name'] for m in data['modules']])

        # compute and write the lines
        l = len(data['modules'])
        for i in range(0, l):
            # name of module
            line = [data['modules'][i]['name']]
            for j in range(0, l):
                cell = csv_cells.get((i, j), None)
                if cell is not None:
                    line.append(cell)
                else:
                    line.append(0)
            # write the line
            cw.writerow(line)

        # return the result
        if si:
            return si.getvalue().strip('\r\n')
        elif file_object:
            return file_object
