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

from __future__ import annotations

import argparse
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, TextIO

from colorama import init

from dependenpy._internal import debug
from dependenpy._internal.dsm import DSM
from dependenpy._internal.helpers import CSV, FORMAT, JSON, guess_depth

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence


class _DebugInfo(argparse.Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        debug._print_debug_info()
        sys.exit(0)


def get_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    parser = argparse.ArgumentParser(
        prog="dependenpy",
        add_help=False,
        description="Command line tool for dependenpy Python package.",
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
        "-f",
        "--format",
        choices=FORMAT,
        default="text",
        dest="format",
        help="Output format. Default: text.",
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
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
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
        version=f"dependenpy {debug._get_version()}",
        help="Show the current version of the program and exit.",
    )
    parser.add_argument(
        "-z",
        "--zero",
        dest="zero",
        default="0",
        help="Character to use for cells with value=0 (text matrix display only).",
    )

    parser.add_argument("--debug-info", action=_DebugInfo, help="Print debug information.")
    return parser


@contextmanager
def _open_if_str(output: str | TextIO) -> Iterator[TextIO]:
    if isinstance(output, str):
        with open(output, "w") as fd:
            yield fd
    else:
        yield output


def _get_indent(opts: argparse.Namespace) -> int | None:
    if opts.indent is None:
        if opts.format == CSV:
            return 0
        return 2
    if opts.indent < 0 and opts.format == JSON:
        # special case for json.dumps indent argument
        return None
    return opts.indent


def _get_depth(opts: argparse.Namespace, packages: Sequence[str]) -> int:
    return opts.depth or guess_depth(packages)


def _get_packages(opts: argparse.Namespace) -> list[str]:
    packages = []
    for arg in opts.packages:
        if "," in arg:
            for package in arg.split(","):
                if package not in packages:
                    packages.append(package)
        elif arg not in packages:
            packages.append(arg)
    return packages


def _run(opts: argparse.Namespace, dsm: DSM) -> None:
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


def main(args: list[str] | None = None) -> int:
    """Run the main program.

    This function is executed when you type `dependenpy` or `python -m dependenpy`.

    Parameters:
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
