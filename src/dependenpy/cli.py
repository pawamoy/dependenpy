# -*- coding: utf-8 -*-

"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later,
  but that will cause problems: the code will get executed twice:

  - When you run `python -mdependenpy` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``dependenpy.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``dependenpy.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import argparse
import sys

from .dsm import DSM

parser = argparse.ArgumentParser(
    add_help=False,
    description='Command line tool for dependenpy Python package.')

parser.add_argument('-d', '--depth', default='-1', type=int, dest='depth',
                    help='Matrix depth. Default: 2 if one package, '
                         'otherwise 1.')
parser.add_argument('-l', '--show-dependencies-list', action='store_true',
                    dest='dependencies', default=False,
                    help='Show the dependencies list. Default: false.')
parser.add_argument('-m', '--show-matrix', action='store_true',
                    dest='matrix', default=False,
                    help='Show the matrix. Default: false.')
parser.add_argument('-o', '--output', action='store', dest='output',
                    default=sys.stdout,
                    help='File to write to. Default: stdout.')
parser.add_argument('-v', '--version', action='version',
                    version='%(prog)s 1.0',
                    help="Show program's version number and exit.")
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                    help='Show this help message and exit.')
parser.add_argument('packages', metavar='PACKAGES', nargs=argparse.ONE_OR_MORE,
                    help='The package list. Can be a comma-separated list. '
                         'Each package must be either '
                         'a valid path or a package in PYTHONPATH.')


def main(args=None):
    """Main function."""
    args = parser.parse_args(args=args)

    if not (args.matrix or args.dependencies):
        args.matrix = True

    packages = []
    for package in args.packages:
        if ',' in package:
            for p in package.split(','):
                if p not in packages:
                    packages.append(p)
        elif package not in packages:
            packages.append(package)

    dsm = DSM(*packages)
    dsm.build_dependencies()

    depth = args.depth
    if depth == -1:
        depth = 2 if len(packages) == 1 else 1

    if isinstance(args.output, str):
        args.output = open(args.output, 'w')

    try:
        dsm.print(output=args.output,
                  dependencies=args.dependencies,
                  matrix=args.matrix,
                  depth=depth)
    except BrokenPipeError:
        return 1

    return 0
