"""dependenpy finder module."""

from __future__ import annotations

from importlib.util import find_spec
from os.path import basename, exists, isdir, isfile, join, splitext
from typing import Any, List, Type


class PackageSpec(object):
    """Holder for a package specification (given as argument to DSM)."""

    def __init__(self, name, path, limit_to=None):
        """
        Initialization method.

        Args:
            name (str): name of the package.
            path (str): path to the package.
            limit_to (list of str): limitations.
        """
        self.name = name
        self.path = path
        self.limit_to = limit_to or []

    def __hash__(self):
        return hash((self.name, self.path))

    @property
    def ismodule(self) -> bool:
        """
        Property to tell if the package is in fact a module (a file).

        Returns:
            Whether this package is in fact a module.
        """
        return self.path.endswith(".py")

    def add(self, spec: PackageSpec) -> None:
        """
        Add limitations of given spec to self's.

        Args:
            spec: Another spec.
        """
        for limit in spec.limit_to:
            if limit not in self.limit_to:
                self.limit_to.append(limit)

    @staticmethod  # noqa: WPS602
    def combine(specs: list[PackageSpec]) -> list[PackageSpec]:  # noqa: WPS602
        """
        Combine package specifications' limitations.

        Args:
            specs: The package specifications.

        Returns:
            The new, merged list of PackageSpec.
        """
        new_specs: dict[PackageSpec, PackageSpec] = {}
        for spec in specs:
            if new_specs.get(spec, None) is None:
                new_specs[spec] = spec
            else:
                new_specs[spec].add(spec)
        return list(new_specs.values())


class PackageFinder(object):
    """Abstract package finder class."""

    def find(self, package: str, **kwargs: Any) -> PackageSpec | None:
        """
        Find method.

        Args:
            package: package to find.
            **kwargs: additional keyword arguments.

        Returns:
            Package spec or None.
        """  # noqa: DAR202,DAR401
        raise NotImplementedError


class LocalPackageFinder(PackageFinder):
    """Finder to find local packages (directories on the disk)."""

    def find(self, package: str, **kwargs: Any) -> PackageSpec | None:
        """
        Find method.

        Args:
            package: package to find.
            **kwargs: additional keyword arguments.

        Returns:
            Package spec or None.
        """
        if not exists(package):
            return None
        name, path = None, None
        enforce_init = kwargs.pop("enforce_init", True)
        if isdir(package):
            if isfile(join(package, "__init__.py")) or not enforce_init:
                name, path = basename(package), package
        elif isfile(package) and package.endswith(".py"):
            name, path = splitext(basename(package))[0], package
        if name and path:
            return PackageSpec(name, path)
        return None


class InstalledPackageFinder(PackageFinder):
    """Finder to find installed Python packages using importlib."""

    def find(self, package: str, **kwargs: Any) -> PackageSpec | None:
        """
        Find method.

        Args:
            package: package to find.
            **kwargs: additional keyword arguments.

        Returns:
            Package spec or None.
        """
        spec = find_spec(package)
        if spec is None:
            return None
        if "." in package:
            package, rest = package.split(".", 1)
            limit = [rest]
            spec = find_spec(package)
        else:
            limit = []
        if spec is not None:
            if spec.submodule_search_locations:
                path = spec.submodule_search_locations[0]
            elif spec.origin and spec.origin != "built-in":
                path = spec.origin
            else:
                return None
            return PackageSpec(spec.name, path, limit)
        return None


class Finder(object):
    """
    Main package finder class.

    Initialize it with a list of package finder classes (not instances).
    """

    def __init__(self, finders: List[Type] = None):
        """
        Initialization method.

        Args:
            finders: list of package finder classes (not instances) in a specific
                order. Default: [LocalPackageFinder, InstalledPackageFinder].
        """
        if finders is None:
            self.finders = [LocalPackageFinder(), InstalledPackageFinder()]
        else:
            self.finders = [finder() for finder in finders]

    def find(self, package: str, **kwargs: Any) -> PackageSpec | None:
        """
        Find a package using package finders.

        Return the first package found.

        Args:
            package: package to find.
            **kwargs: additional keyword arguments used by finders.

        Returns:
            Package spec or None.
        """
        for finder in self.finders:
            package_spec = finder.find(package, **kwargs)
            if package_spec:
                return package_spec
        return None
