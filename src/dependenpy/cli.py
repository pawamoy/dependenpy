# -*- coding: utf-8 -*-

"""
Module that contains the command line application.

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

from . import __version__
from .dsm import DSM
from .helpers import CSV, FORMAT, JSON, guess_depth


def get_parser():
    """Return a parser for the command-line arguments."""
    parser = argparse.ArgumentParser(
        add_help=False,
        description='Command line tool for dependenpy Python package.')
    mxg = parser.add_mutually_exclusive_group(required=False)

    parser.add_argument(
        'packages', metavar='PACKAGES', nargs=argparse.ONE_OR_MORE,
        help='The package list. Can be a comma-separated list. Each package '
             'must be either a valid path or a package in PYTHONPATH.')
    parser.add_argument(
        '-d', '--depth', default=None, type=int, dest='depth',
        help='Specify matrix or graph depth. Default: best guess.')
    parser.add_argument(
        '-f', '--format', choices=FORMAT, default='text',
        dest='format', help='Output format. Default: text.')
    mxg.add_argument(
        '-g', '--show-graph', action='store_true', dest='graph', default=False,
        help='Show the graph (no text format). Default: false.')
    parser.add_argument(
        '-G', '--greedy', action='store_true', dest='greedy', default=False,
        help='Explore subdirectories even if they do not contain an '
             '__init__.py file. Can make execution slower. Default: false.')
    parser.add_argument(
        '-h', '--help', action='help', default=argparse.SUPPRESS,
        help='Show this help message and exit.')
    parser.add_argument(
        '-i', '--indent', default=None, type=int, dest='indent',
        help='Specify output indentation. CSV will never be indented. '
             'Text will always have new-lines. JSON can be minified with '
             'a negative value. Default: best guess.')
    mxg.add_argument(
        '-l', '--show-dependencies-list', action='store_true',
        dest='dependencies', default=False,
        help='Show the dependencies list. Default: false.')
    mxg.add_argument(
        '-m', '--show-matrix', action='store_true',
        dest='matrix', default=False,
        help='Show the matrix. Default: true unless -g, -l or -t.')
    parser.add_argument(
        '-o', '--output', action='store', dest='output', default=sys.stdout,
        help='Output to given file. Default: stdout.')
    mxg.add_argument(
        '-t', '--show-treemap', action='store_true',
        dest='treemap', default=False,
        help='Show the treemap (work in progress). Default: false.')
    parser.add_argument(
        '-v', '--version', action='version',
        version='dependenpy %s' % __version__,
        help='Show the current version of the program and exit.')
    return parser


def main(args=None):
    """
    Main function.

    This function is the command line entry point.

    Args:
        args (list of str): the arguments passed to the program.

    Returns:
        int: return code being 0 (OK), 1 (dsm empty) or 2 (error).
    """
    parser = get_parser()
    args = parser.parse_args(args=args)

    if not (args.matrix or args.dependencies or args.treemap or args.graph):
        args.matrix = True

    # split comma-separated args
    packages = []
    for arg in args.packages:
        if ',' in arg:
            for package in arg.split(','):
                if package not in packages:
                    packages.append(package)
        elif arg not in packages:
            packages.append(arg)

    # guess convenient depth
    depth = args.depth
    if depth is None:
        depth = guess_depth(packages)

    # open file if not stdout
    output = args.output
    if isinstance(output, str):
        output = open(output, 'w')

    dsm = DSM(*packages, build_tree=True, build_dependencies=True,
              enforce_init=not args.greedy)

    if dsm.empty:
        return 1

    indent = args.indent
    if indent is None:
        if args.format == CSV:
            indent = 0
        else:
            indent = 2
    elif indent < 0 and args.format == JSON:
        # special case for json.dumps indent argument
        indent = None

    try:
        if args.dependencies:
            dsm.print(format=args.format, output=output, indent=indent)
        elif args.matrix:
            dsm.print_matrix(format=args.format, output=output,
                             depth=depth, indent=indent)
        elif args.treemap:
            dsm.print_treemap(format=args.format, output=output)
        elif args.graph:
            dsm.print_graph(format=args.format, output=output,
                            depth=depth, indent=indent)
    except BrokenPipeError:
        # avoid traceback
        return 2

    return 0
