# -*- coding: utf-8 -*-

"""dependenpy finder module."""

from importlib.util import find_spec
from os.path import basename, exists, isdir, isfile, join, splitext


class PackageSpec(object):
    def __init__(self, name, path, limit_to=None):
        self.name = name
        self.path = path
        self.limit_to = limit_to or []

    def __key(self):
        return self.name, self.path

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    @property
    def ismodule(self):
        return self.path.endswith('.py')

    def add(self, spec):
        for limit in spec.limit_to:
            if limit not in self.limit_to:
                self.limit_to.append(limit)

    @staticmethod
    def combine(specs):
        new_specs = {}
        for spec in specs:
            if new_specs.get(spec, None) is None:
                new_specs[spec] = spec
            else:
                new_specs[spec].add(spec)
        return list(new_specs.values())


class LocalPackageFinder(object):
    def find(self, package):
        if not exists(package):
            return None
        # TODO: option to enforce or not presence of __init__.py
        if isdir(package) and isfile(join(package, '__init__.py')):
            name, path = basename(package), package
        elif isfile(package) and package.endswith('.py'):
            name, path = splitext(basename(package))[0], package
        else:
            return None
        return PackageSpec(name, path)


class InstalledPackageFinder(object):
    def find(self, package):
        spec = find_spec(package)
        if spec is None:
            return None
        limit = []
        if '.' in package:
            package, limit = package.split('.', 1)
            limit = [limit]
            spec = find_spec(package)
        if spec is not None:
            if spec.submodule_search_locations:
                path = spec.submodule_search_locations[0]
            elif spec.origin and spec.origin != 'built-in':
                path = spec.origin
            else:
                return None
            return PackageSpec(spec.name, path, limit)
        return None


class PackageFinder(object):
    def __init__(self, finders=None):
        if finders is None:
            self.finders = [LocalPackageFinder(), InstalledPackageFinder()]
        else:
            self.finders = [f() for f in finders]

    def find(self, package):
        for finder in self.finders:
            package_spec = finder.find(package)
            if package_spec:
                return package_spec
        raise ModuleNotFoundError(package)
