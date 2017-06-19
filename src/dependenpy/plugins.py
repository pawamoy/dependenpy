# -*- coding: utf-8 -*-

"""dependenpy plugins module."""

try:
    from archan import Provider, Argument, DSM as ArchanDSM
    from .dsm import DSM as DependenpyDSM
    from .helpers import guess_depth

    class InternalDependencies(Provider):
        """Dependenpy provider for Archan."""

        identifier = 'dependenpy.InternalDependencies'
        name = 'Internal Dependencies'
        description = 'Provide matrix data about internal dependencies ' \
                      'in a set of packages.'
        arguments = (
            Argument('packages', list, 'The list of packages to check for.'),
            Argument('enforce_init', bool, default=True,
                     description='Whether to assert presence of '
                     '__init__.py files in directories.'),
            Argument('depth', int, 'The depth of the matrix to generate.'),
        )

        def get_dsm(self, packages, enforce_init=True, depth=None):
            """
            Provide matrix data for internal dependencies in a set of packages.

            Args:
                *packages (list): the list of packages to check for.
                enforce_init (bool):
                    whether to assert presence of __init__.py files
                    in directories.
                depth (int): the depth of the matrix to generate.

            Returns:
                archan.DSM: instance of archan DSM.
            """
            dsm = DependenpyDSM(*packages, enforce_init=enforce_init)
            if depth is None:
                depth = guess_depth(packages)
            matrix = dsm.as_matrix(depth=depth)
            return ArchanDSM(data=matrix.data, entities=matrix.keys)

except ImportError:
    class InternalDependencies(object):
        """Empty dependenpy provider."""
