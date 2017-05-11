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

from .dsm import DSM

parser = argparse.ArgumentParser(
    description='Command line tool for dependenpy Python package.')
parser.add_argument('packages', metavar='PACKAGES', nargs=argparse.ONE_OR_MORE,
                    help='The package list.')


def main(args=None):
    """Main function."""
    args = parser.parse_args(args=args)
    dsm = DSM(*args.packages)
    dsm.build_dependencies()
    dsm.print()
