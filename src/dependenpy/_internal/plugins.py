from __future__ import annotations

from dependenpy._internal.dsm import DSM as DependenpyDSM  # noqa: N811
from dependenpy._internal.helpers import guess_depth

try:
    import archan
except ImportError:

    class InternalDependencies:
        """Empty dependenpy provider."""

else:

    class InternalDependencies(archan.Provider):  # type: ignore[no-redef]
        """Dependenpy provider for Archan."""

        identifier = "dependenpy.InternalDependencies"
        """Identifier of the provider."""
        name = "Internal Dependencies"
        """Name of the provider."""
        description = "Provide matrix data about internal dependencies in a set of packages."
        """Description of the provider."""
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
        """List of arguments for the provider."""

        def get_data(
            self,
            packages: list[str],
            enforce_init: bool = True,  # noqa: FBT001,FBT002
            depth: int | None = None,
        ) -> archan.DSM:
            """Provide matrix data for internal dependencies in a set of packages.

            Args:
                packages: the list of packages to check for.
                enforce_init: whether to assert presence of __init__.py files in directories.
                depth: the depth of the matrix to generate.

            Returns:
                Instance of archan DSM.
            """
            dsm = DependenpyDSM(*packages, enforce_init=enforce_init)
            if depth is None:
                depth = guess_depth(packages)
            matrix = dsm.as_matrix(depth=depth)
            return archan.DesignStructureMatrix(data=matrix.data, entities=matrix.keys)
