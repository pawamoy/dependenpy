# -*- coding: utf-8 -*-
import os
import sys
import ast
import json
import csv
import collections


class Elem:
    """An element in the matrix, containing a list of imports.
    It is generally associated to a single file (or python module).
    """

    def __init__(self):
        self._imports = []

    def __len__(self):
        l = 0
        for i in self._imports:
            l += len(i['import'])
        return l

    def add(self, imports):
        """Add imports to this matrix element.
        """
        self._imports.append(imports)

    def serialize(self):
        return self._imports

    def to_json(self):
        return json.dumps(self.serialize())


class Matrix:
    """A matrix of elements containing lists of imports.
    Each instance is the matrix of a dependency matrix for a specific depth.
    """

    def __init__(self, imports_dict, max_depth=False):
        self._keys = imports_dict.keys()
        l = len(self._keys)
        self._data = [[Elem() for x in range(l)] for x in range(l)]
        if max_depth:
            self._fill_max_depth(imports_dict)
        else:
            self._fill(imports_dict)

    def __len__(self):
        return len(self._keys)

    def _fill_max_depth(self, imports_dict):
        """Fill the matrix without doing any module regrouping.
        """
        # This is the max depth matrix, we just have to fill
        # the matrix with all values in imports_dict.
        i = 0
        for values in imports_dict.values():
            for value in values:
                try:
                    j = self._keys.index(value['from'])
                    self._data[i][j].add(value)
                except ValueError:
                    pass
            i += 1

    def _fill(self, imports_dict):
        """Fill the matrix by doing module regrouping on the given keys.
        """
        i = 0
        for values in imports_dict.values():
            for value in values:
                # Here we cannot search the from value in keys since it might
                # not be in, so instead we loop over the keys and check if the
                # from value is equal to the key or is a sub-module of it.
                j = 0
                for k in self._keys:
                    if value['from'] == k or value['from'].startswith(k + '.'):
                        self._data[i][j].add(value)
                        break
                    j += 1
            i += 1

    def serialize(self, grouping=None):
        nodes = []
        if grouping:
            for k in self._keys:
                gi = 1
                for group in grouping:
                    b = False
                    for g in group:
                        if k == g or k.startswith(g + '.'):
                            nodes.append({"name": k, "group": gi})
                            b = True
                            break
                    if b:
                        break
                    gi += 1
        else:
            for k in self._keys:
                nodes.append({"name": k, "group": 1})

        links = []
        i = 0
        for row in self._data:
            j = 0
            for e in row:
                l = len(e)
                if l > 0:
                    links.append({"source": i, "target": j, "value": l})
                j += 1
            i += 1
        return {"nodes": nodes, "links": links}

    def to_json(self, grouping=None):
        return json.dumps(self.serialize(grouping))

    def to_csv(self):
        array = [self._keys]
        i = 0
        for row in self._data:
            line = [self._keys[i]]
            for e in row:
                line.append(len(e))
            i += 1
            array.append(line)
        return str(array).replace('[', '').replace(']', '\n')


class DependencyMatrix:
    """A DependencyMatrix instance walks over modules in app_list to build
    its imports dictionnary. The call to compute_matrix will then build
    the matrices for all depths, i.e. the range from 1 to the maximum depth
    of all modules. A matrix for a specific depth regroups sub-modules that
    are deeper that this depth into their parent module. See this class as
    a square matrix allowing to zoom in and in into elements until max depth
    has been reached.
    """

    def __init__(self, app_list, path_method=None):
        """Instantiate a DependencyMatrix object.
        :param app_list: *required* (tuple); the list of apps you want to scan
        :param path_method: *optional* (callable); the method to determine a module path within python path
        """
        self._all_modules = []
        if isinstance(app_list[0], list):
            self._inside_modules = []
            for app in app_list:
                self._inside_modules.extend(app)
            self._order = app_list
        else:
            self._inside_modules = app_list
            self._order = None
        self.imports = {}
        self.max_depth = 0
        if path_method:
            self._get_module_path = path_method
        else:
            self._get_module_path = DependencyMatrix._get_module_path_
        self._get_modules()
        self._get_imports()
        self._get_max_depth()
        self.matrices = [None for x in range(self.max_depth)]

    def compute_matrix(self):
        """Build the matrices for all depths. Call is explicit because users
        might not want to build matrices, but just get imports dictionnary.
        """
        self.matrices[self.max_depth - 1] = Matrix(self.imports,
                                                   max_depth=True)
        depth = self.max_depth - 1
        depth_dict = self.imports
        while depth > 0:
            depth_dict = DependencyMatrix._get_depth_dict(depth_dict, depth)
            self.matrices[depth - 1] = Matrix(depth_dict)
            depth -= 1

    def get_matrix(self, depth=0):
        """Returns the built matrix for the specified depth.
        :param depth: *optional* (int); Which matrix to return. Default 0 (=max)
        :return: A Matrix instance for the specified depth.
        """
        if depth >= self.max_depth or depth == 0:
            depth = self.max_depth
        return self.matrices[depth - 1]

    def _get_modules(self):
        """Build the extended module list by walking over the initial modules.
        Do not add external modules (only sub-modules of initial ones).
        """
        for app in self._inside_modules:
            module = self._get_module_path(app)
            if not module:
                continue
            module = os.path.dirname(module)
            for f in DependencyMatrix._walk(module):
                if f.endswith('.py'):
                    mod_name = app + '.' + os.path.splitext(f)[0].replace('/',
                                                                          '.')
                    self._all_modules.append(mod_name)
        # We remove duplicates
        seen = set()
        seen_add = seen.add
        am = self._all_modules
        self._all_modules = [x for x in am if not (x in seen or seen_add(x))]

    def _get_imports(self):
        """Build the imports dictionary from the extended module list. Parse
        every module and retrieve its imports.
        """
        for mod in self._all_modules:
            mod_path = self._get_module_path(mod)
            if mod_path:
                # We append .__init__ if necessary
                if '__init__' in mod:
                    mod_name = mod
                elif '__init__' in mod_path:
                    mod_name = mod + '.__init__'
                else:
                    mod_name = mod
                self.imports[mod_name] = self._get_from_import(
                    mod_path, mod_name)
        # We reorder the imports only ONE time, here,
        # and it will be passed to all sub-depth dicts
        if self._order:
            ordered_dict = collections.OrderedDict()
            for part in self._order:
                roots = [module.split('.')[0] for module in part]
                for key in self.imports.keys():
                    if key.split('.')[0] in roots:
                        ordered_dict[key] = self.imports.pop(key)
            self.imports = ordered_dict

    def _get_max_depth(self):
        """Compute max depth based on imports dictionary's keys.
        """
        self.max_depth = DependencyMatrix._max_depth(self.imports.keys())

    @staticmethod
    def _get_from_import(py_file, module):
        """Return a list of dictionaries with importing module (by)
        and imported modules (from and import).
        :param py_file: *required* (string); file to parse
        :param module: *required* (string); file's name as a python module
        :return:
        """
        result = []
        code = open(py_file).read()
        for node in ast.parse(code).body:
            if isinstance(node, ast.ImportFrom):
                if not node.module:
                    continue
                mod = node.module
                # We rebuild the module name when it is like .* or ..* or ...*
                level = node.level
                if level > 0:
                    mod = os.path.splitext(module)[0]
                    level -= 1
                    while level != 0:
                        mod = os.path.splitext(mod)[0]
                        level -= 1
                    mod += '.' + node.module
                temp_list = []
                for name in node.names:
                    temp_list.append(name.name)
                result.append({
                    'by': module, 'from': mod, 'import': temp_list})
        return result

    @staticmethod
    def _get_depth_dict(imports, max_depth):
        """Update a dictionary for a specific depth based on another dictionary.
        :param imports: *required* (dict); base dictionary
        :param max_depth: *required* (int); regroup all sub-modules deeper than max_depth
        :return: (dict); the new updated dictionary
        """
        new_dict = collections.OrderedDict()
        for key in imports.keys():
            value = imports[key]
            new_key = '.'.join(key.split('.')[:max_depth])
            if new_dict.get(new_key, None):
                new_dict[new_key].extend(value)
            else:
                new_dict[new_key] = value
        return new_dict

    @staticmethod
    def _get_module_path_(mod):
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

    @staticmethod
    def _max_depth(seq):
        """Return the maximum depth of a module in a list of modules.
        :param seq: *required* (list); python modules list (*.*.*)
        :return: (int); the maximum depth
        """
        d = 0
        for m in seq:
            m_depth = len(m.split('.'))
            if m_depth > d:
                d = m_depth
        return d

    @staticmethod
    def _walk(path, prefix=''):
        """Walk recursively into subdirectories of a directory and return a
        list of all found Python files (*.py).
        :param path: *required* (string); directory to scan
        :param prefix: *optional* (string); file paths prepended string
        :return: (list); the list of Python files
        """
        result = []
        for item in os.listdir(path):
            sub_item = os.path.join(path, item)
            if os.path.isdir(sub_item):
                result.extend(DependencyMatrix._walk(
                    sub_item, prefix + os.path.basename(sub_item) + '/'))
            else:
                result.append(prefix + item)
        return result

    def serialize(self):
        return {
            'max_depth': self.max_depth,
            'matrix': [m.serialize(self._order) for m in self.matrices]
        }

    def to_json(self):
        return json.dumps(self.serialize())

    def to_csv(self):
        return str([m.to_csv()
                    for m in self.matrices
                    ]).replace('[', '').replace(']', '\n')
