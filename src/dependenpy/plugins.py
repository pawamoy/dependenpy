# -*- coding: utf-8 -*-

"""dependenpy plugins module."""

from dependenpy.dsm import DSM as DependenpyDSM  # noqa: N811
from dependenpy.helpers import guess_depth

try:
    import archan
except ImportError:

    class InternalDependencies(object):  # type: ignore
        """Empty dependenpy provider."""

else:

    class InternalDependencies(archan.Provider):  # type: ignore  # noqa: WPS440
        """Dependenpy provider for Archan."""

        identifier = "dependenpy.InternalDependencies"
        name = "Internal Dependencies"
        description = "Provide matrix data about internal dependencies in a set of packages."
        argument_list = (
            archan.Argument("packages", list, "The list of packages to check for."),
            archan.Argument(
                "enforce_init",
                bool,
                default=True,
                description="Whether to assert presence of __init__.py files in directories.",
            ),
            archan.Argument("depth", int, "The depth of the matrix to generate."),
        )

        def get_data(self, packages, enforce_init: bool = True, depth: int = None):
            """
            Provide matrix data for internal dependencies in a set of packages.

            Args:
                packages: the list of packages to check for.
                enforce_init: whether to assert presence of __init__.py files in directories.
                depth: the depth of the matrix to generate.

            Returns:
                archan.DSM: instance of archan DSM.
            """
            dsm = DependenpyDSM(*packages, enforce_init=enforce_init)
            if depth is None:
                depth = guess_depth(packages)
            matrix = dsm.as_matrix(depth=depth)
            return archan.DesignStructureMatrix(data=matrix.data, entities=matrix.keys)
