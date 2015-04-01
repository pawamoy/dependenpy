# -*- coding: utf-8 -*-

# Copyright (c) 2015 Timothée Mazzucotelli
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""dependenpy utils module.

This is the main and only module of dependenpy package.
This module contains:

    a class, MatrixBuilder: the class building your dependency matrix data.
    a class, Matrix: the class containing the 2-dimensions array of integers
    a function, resolve_path: transforms a module name into an absolute path.

"""

import os
import sys
import ast
import json
import csv
from collections import OrderedDict
from dependenpy.greedy import solve_tsp

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


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


class Matrix(object):
    """Matrix class.
    """

    def __init__(self, depth, modules, imports):
        #: int: the current depth of this matrix
        self.depth = depth
        #: int: the size of this square matrix (nb rows/columns)
        self.size = len(modules)

        #: dict of tuple: the available sorting orders.
        #: First value of tuple is bool: order is computed or not.
        #: Second value of tuple is callable: the class method that compute
        #: the order
        self.orders = {
            'name': [False, self._compute_name_order],
            'group': [True, self._compute_group_order],
            'import': [False, self._compute_import_order],
            'export': [False, self._compute_export_order],
            'similarity': [False, self._compute_similarity_order]}
        # TODO: add import+export order

        #: dict of dict: for each module identified by a key (currently
        #: its name), stores the value of its name, group, imports cardinal,
        #: exports cardinal, and the corresponding order indexes.
        #: Orders are dict with 2 values: False for ascendant order,
        #: True for descendant order (think of reverse=False/True)
        self.modules = OrderedDict()
        m_index = 0
        for module in modules:
            self.modules[module['name']] = {
                'name': module['name'],
                'group': module['group'],
                'cardinal': {'imports': 0, 'exports': 0},
                'order': {}}
            for order in self.orders.keys():
                self.modules[module['name']]['order'][order] = {}
            # we can fill group order at initialization
            self.modules[module['name']]['order']['group'][False] = m_index
            # FIXME: temporary until group order computing method is coded
            self.modules[module['name']]['order']['group'][True] = m_index
            m_index += 1

        for i in imports:
            cardinal = i['cardinal']
            self.modules[i['source_name']]['cardinal']['imports'] += cardinal
            self.modules[i['target_name']]['cardinal']['exports'] += cardinal

        #: list of dict: every dependencies between the modules, containing
        #: the source and target names, the source and target position
        #: (according to current order), the list of imports, and the
        #: number of imports and exports (cardinals)
        self.dependencies = imports

        #: list of str: the ordered list of modules' groups
        self.groups = [m['group']['name'] for m in modules]
        #: list of str: the ordered list of modules' names
        self.keys = [m['name'] for m in modules]

        #: list of list of int: the concrete matrix with numeric values
        self.matrix = None
        self._update_matrix()

    def __str__(self):
        return '%s' % self.matrix

    def __eq__(self, other):
        return all([
            self.depth == other.depth,
            self.size == other.size,
            self.modules == other.modules,
            self.dependencies == other.dependencies,
            self.groups == other.groups,
            self.keys == other.keys,
            self.matrix == other.matrix,
        ])

    def build_up_matrix(self):
        """Build matrix data based on the matrix below it (with depth+1).

        :return: :class:`Matrix` instance
        """
        # First we build the new module list
        up_modules, up_dependencies = [], []
        seen_module, seen_import = {}, {}
        modules_indexes = {}
        index_old, index_new = 0, -1
        for k in self.keys:
            up_module = '.'.join(k.split('.')[:self.depth-1])
            if seen_module.get(up_module, None) is None:
                seen_module[up_module] = {'name': up_module,
                                          'group': self.modules[k]['group']}
                up_modules.append(seen_module[up_module])
                index_new += 1
            modules_indexes[index_old] = {'index': index_new,
                                          'name': up_module}
            index_old += 1

        # Then we build the new dependencies list
        for d in self.dependencies:
            new_source_index = modules_indexes[d['source_index']]['index']
            new_source_name = modules_indexes[d['source_index']]['name']
            new_target_index = modules_indexes[d['target_index']]['index']
            new_target_name = modules_indexes[d['target_index']]['name']
            seen_id = (new_source_index, new_target_index)
            if seen_import.get(seen_id, None) is not None:
                seen_import[seen_id]['cardinal'] += d['cardinal']
                seen_import[seen_id]['imports'] += d['imports']
            else:
                seen_import[seen_id] = {
                    'cardinal': d['cardinal'],
                    'imports': list(d['imports']),
                    'source_name': new_source_name,
                    'source_index': new_source_index,
                    'target_name': new_target_name,
                    'target_index': new_target_index,
                }
                up_dependencies.append(seen_import[seen_id])

        # We return the new Matrix
        return Matrix(self.depth-1, up_modules, up_dependencies)
        # TODO: optimization: we could compute orders for max_depth matrix
        # and reuse them in some way for above matrices

    def sort(self, order, reverse=False):
        try:
            self.compute_order(order)
        except KeyError:
            print('Order %s does not match any of these: %s' % (
                order, self.orders.keys()))
            return

        # pylint: disable=line-too-long
        for d in self.dependencies:
            d['source_index'] = self.modules[d['source_name']]['order'][order][reverse]  # noqa
            d['target_index'] = self.modules[d['target_name']]['order'][order][reverse]  # noqa

        self._update_matrix()
        # TODO: update keys and groups

    def compute_orders(self):
        for order in self.orders.keys():
            self.compute_order(order)

    def compute_order(self, order):
        """Compute the index order according to a criteria.
        The available criteria are listed in self.orders keys.

        :param order: str, order criteria to use
        :raise: KeyError when order key is not in self.orders dict
        """
        if self.orders[order][0]:
            return
        self.orders[order][1]()

    def _write_order(self, order, sorted_keys):
        l = len(sorted_keys)
        for i in range(l):
            self.modules[sorted_keys[i]]['order'][order][False] = i
        for i in range(l):
            self.modules[sorted_keys[i]]['order'][order][True] = l-1-i
        self.orders[order][0] = True

    def _compute_name_order(self):
        sorted_keys = sorted(self.keys)
        self._write_order('name', sorted_keys)

    def _compute_import_order(self):
        sorted_keys = sorted(
            self.modules,
            key=lambda x: self.modules[x]['cardinal']['imports'])
        self._write_order('import', sorted_keys)

    def _compute_export_order(self):
        sorted_keys = sorted(
            self.modules,
            key=lambda x: self.modules[x]['cardinal']['exports'])
        self._write_order('export', sorted_keys)

    def _compute_similarity_order(self):
        # we initialize name-index correspondences
        co = {}
        for i in range(self.size):
            co[i] = self.keys[i]
            co[self.keys[i]] = i

        # we prepare the square symmetric distance matrix
        matrix = [[0 for x in range(self.size)] for x in range(self.size)]

        # we compute the similarities and fill the matrix
        l = len(self.dependencies)
        for id1 in range(l-1):
            for id2 in range(id1+1, l):
                d1 = self.dependencies[id1]
                d2 = self.dependencies[id2]
                sn1, sn2 = d1['source_name'], d2['source_name']
                if sn1 != sn2:
                    n, i, j = 0, co[sn1], co[sn2]
                    for di1 in d1['imports']:
                        for di2 in d2['imports']:
                            if di1['from'] == di2['from']:
                                n += len([0 for x in di1['import']
                                          if x in di2['import']])

                    if n > 0:
                        s = matrix[i][j] + n
                        matrix[i][j] = s
                        matrix[j][i] = s

        # we compute the order with a TSP solver, set the sorted keys and save
        order = solve_tsp(matrix)
        sorted_keys = [co[k] for k in order]
        self._write_order('similarity', sorted_keys)

    def _compute_group_order(self):
        pass
        # TODO: code this method
        # self._write_order('group', sorted_keys)

    def _update_matrix(self):
        self.matrix = [[0 for x in range(self.size)] for x in range(self.size)]
        for d in self.dependencies:
            self.matrix[d['source_index']][d['target_index']] += d['cardinal']

    def to_json(self):
        """Return a matrix from self.matrices as a JSON string.

        :param matrix: int, index/depth of matrix (from 1 to max_depth,
            0 is equivalent to max_depth)
        :return: str, a JSON dump of the matrix
        """
        return json.dumps({'depth': self.depth,
                           'size': self.size,
                           'modules': self.modules,
                           'dependencies': self.dependencies,
                           'keys': self.keys,
                           'groups': self.groups,
                           'matrix': self.matrix,
                           'orders': self.orders.keys()})

    def to_csv(self, file_object=None):
        """Return the matrix as a CSV array.

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
            si = StringIO()
            cw = csv.writer(si)

        # write the first line (columns)
        cw.writerow([''] + self.keys)

        # write the lines
        for i in range(0, self.size):
            cw.writerow([self.keys[i]] + self.matrix[i])

        # return the result
        if si:
            return si.getvalue().strip('\r\n')
        elif file_object:
            return file_object


# TODO: Add exclude option
class MatrixBuilder(object):
    """Dependency matrix data builder.
    """

    def __init__(self, packages, path_resolver=resolve_path):
        """Instantiate a MatrixBuilder object.

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
        # TODO: Replace OrderedDict by a list (easier to use)
        elif isinstance(packages, OrderedDict):
            self.packages = packages.values()
            self.groups = packages.keys()
        else:
            raise AttributeError
        #: callable: the method that find the path of a module
        self.path_resolver = path_resolver
        #: list of dict: the list of all packages' modules, containing
        #: name, path, group index and group name
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
        if self.modules:
            self.max_depth = max([len(m['name'].split('.'))
                                  for m in self.modules])
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
                        'target_name': self.modules[target_index]['name'],
                        'target_index': target_index,
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
        self.matrices[md-1] = Matrix(md, self.modules, self.imports)
        md -= 1
        while md > 0:
            self.matrices[md-1] = self.matrices[md].build_up_matrix()
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
            if m['name'] == module + '.__init__':
                return idx
            idx += 1
        # Case 3: module is the sub-module of a target
        idx = 0
        for m in self.modules:
            if module.startswith(m['name'] + '.'):
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
                    if module == package or module.startswith(package + '.'):
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
        sum_from = OrderedDict()
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

    # TODO: Add exclude option
    def _walk(self, name, path, group, prefix=''):
        """Walk recursively into subdirectories of a package directory
        and return a list of all Python files found (*.py).

        :param name: str, name of the package
        :param path: str, path of the package
        :param group: int, group index of the package
        :param prefix: str, used by recursion, file paths prepended string
        :return: list of dict, contains name, path, group index and group name
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
                            prefix + item)[0].replace(os.sep, '.')),
                    'path': sub_item,
                    'group': {'index': group, 'name': self.groups[group]}
                })
        # Ensure resulting list of files is always in the same order
        return sorted(result, key=lambda k: k['name'])

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
            'matrices': [m.to_json() for m in self.matrices],
            '_inside': self._inside,
            '_modules_are_built': self._modules_are_built,
            '_imports_are_built': self._imports_are_built,
            '_matrices_are_built': self._matrices_are_built,
        })

    def get_matrix(self, matrix):
        """Return the specified matrix.
        The given index is casted into [0 .. max_depth] range.

        :param matrix: int, index/depth. Zero means max_depth.
        :return: Matrix instance
        """
        if not self._matrices_are_built:
            print('Matrices are not built. Use build() method first.')
            return None
        i = int(matrix)
        if i == 0 or i > self.max_depth:
            m = self.max_depth - 1
        elif i < 0:
            m = 0
        else:
            m = i - 1
        return self.matrices[m]
