# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m dependenpy` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `dependenpy.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `dependenpy.__main__` in `sys.modules`.

"""Module that contains the command line application."""

from __future__ import annotations

import argparse
import sys
from contextlib import contextmanager
from typing import List, Optional

from colorama import init

from dependenpy import __version__
from dependenpy.dsm import DSM
from dependenpy.helpers import CSV, FORMAT, JSON, guess_depth


def get_parser() -> argparse.ArgumentParser:
    """
    Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    parser = argparse.ArgumentParser(
        prog="dependenpy", add_help=False, description="Command line tool for dependenpy Python package."
    )
    mxg = parser.add_mutually_exclusive_group(required=False)

    parser.add_argument(
        "packages",
        metavar="PACKAGES",
        nargs=argparse.ONE_OR_MORE,
        help="The package list. Can be a comma-separated list. Each package "
        "must be either a valid path or a package in PYTHONPATH.",
    )
    parser.add_argument(
        "-d",
        "--depth",
        default=None,
        type=int,
        dest="depth",
        help="Specify matrix or graph depth. Default: best guess.",
    )
    parser.add_argument(
        "-f", "--format", choices=FORMAT, default="text", dest="format", help="Output format. Default: text."
    )
    mxg.add_argument(
        "-g",
        "--show-graph",
        action="store_true",
        dest="graph",
        default=False,
        help="Show the graph (no text format). Default: false.",
    )
    parser.add_argument(
        "-G",
        "--greedy",
        action="store_true",
        dest="greedy",
        default=False,
        help="Explore subdirectories even if they do not contain an "
        "__init__.py file. Can make execution slower. Default: false.",
    )
    parser.add_argument(
        "-h", "--help", action="help", default=argparse.SUPPRESS, help="Show this help message and exit."
    )
    parser.add_argument(
        "-i",
        "--indent",
        default=None,
        type=int,
        dest="indent",
        help="Specify output indentation. CSV will never be indented. "
        "Text will always have new-lines. JSON can be minified with "
        "a negative value. Default: best guess.",
    )
    mxg.add_argument(
        "-l",
        "--show-dependencies-list",
        action="store_true",
        dest="dependencies",
        default=False,
        help="Show the dependencies list. Default: false.",
    )
    mxg.add_argument(
        "-m",
        "--show-matrix",
        action="store_true",
        dest="matrix",
        default=False,
        help="Show the matrix. Default: true unless -g, -l or -t.",
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        dest="output",
        default=sys.stdout,
        help="Output to given file. Default: stdout.",
    )
    mxg.add_argument(
        "-t",
        "--show-treemap",
        action="store_true",
        dest="treemap",
        default=False,
        help="Show the treemap (work in progress). Default: false.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"dependenpy {__version__}",
        help="Show the current version of the program and exit.",
    )
    parser.add_argument(
        "-z",
        "--zero",
        dest="zero",
        default="0",
        help="Character to use for cells with value=0 (text matrix display only).",
    )

    return parser


@contextmanager
def _open_if_str(output):
    if isinstance(output, str):
        with open(output, "w") as fd:
            yield fd
    else:
        yield output


def _get_indent(opts):
    if opts.indent is None:
        if opts.format == CSV:
            return 0
        return 2
    elif opts.indent < 0 and opts.format == JSON:
        # special case for json.dumps indent argument
        return None
    return opts.indent


def _get_depth(opts, packages):
    return opts.depth or guess_depth(packages)


def _get_packages(opts):  # noqa: WPS231
    packages = []
    for arg in opts.packages:
        if "," in arg:
            for package in arg.split(","):
                if package not in packages:
                    packages.append(package)
        elif arg not in packages:
            packages.append(arg)
    return packages


def _run(opts, dsm):
    indent = _get_indent(opts)
    depth = _get_depth(opts, packages=dsm.base_packages)
    with _open_if_str(opts.output) as output:
        if opts.dependencies:
            dsm.print(format=opts.format, output=output, indent=indent)
        elif opts.matrix:
            dsm.print_matrix(format=opts.format, output=output, depth=depth, indent=indent, zero=opts.zero)
        elif opts.treemap:
            dsm.print_treemap(format=opts.format, output=output)
        elif opts.graph:
            dsm.print_graph(format=opts.format, output=output, depth=depth, indent=indent)


def main(args: Optional[List[str]] = None) -> int:  # noqa: WPS231
    """
    Run the main program.

    This function is executed when you type `dependenpy` or `python -m dependenpy`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code. 0 (OK), 1 (dsm empty) or 2 (error).
    """
    parser = get_parser()
    opts = parser.parse_args(args=args)
    if not (opts.matrix or opts.dependencies or opts.treemap or opts.graph):
        opts.matrix = True

    dsm = DSM(*_get_packages(opts), build_tree=True, build_dependencies=True, enforce_init=not opts.greedy)
    if dsm.empty:
        return 1

    # init colorama
    init()

    try:
        _run(opts, dsm)
    except BrokenPipeError:
        # avoid traceback
        return 2

    return 0
