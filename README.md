# Dependenpy

[![ci](https://github.com/pawamoy/dependenpy/workflows/ci/badge.svg)](https://github.com/pawamoy/dependenpy/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://pawamoy.github.io/dependenpy/)
[![pypi version](https://img.shields.io/pypi/v/dependenpy.svg)](https://pypi.org/project/dependenpy/)

Show the inter-dependencies between modules of Python packages.

`dependenpy` allows you to build a dependency matrix for a set of Python packages.
To do this, it reads and searches the source code for import statements.

![demo](demo.svg)

## Requirements

Dependenpy requires Python 3.6 or above.

<details>
<summary>To install Python 3.6, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```bash
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these three lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
export PYENV_ROOT="${HOME}/.pyenv"
eval "$(pyenv init -)"

# install Python 3.6
pyenv install 3.6.8

# make it available globally
pyenv global system 3.6.8
```
</details>

## Installation

With `pip`:
```bash
python3.6 -m pip install dependenpy
```

With [`pipx`](https://github.com/pipxproject/pipx):
```bash
python3.6 -m pip install --user pipx

pipx install --python python3.6 dependenpy
```

## Usage (as a library)

```python
from dependenpy import DSM

# create DSM
dsm = DSM('django')

# transform as matrix
matrix = dsm.as_matrix(depth=2)

# initialize with many packages
dsm = DSM('django', 'meerkat', 'appsettings', 'dependenpy', 'archan')
with open('output', 'w') as output:
    dsm.print(format='json', indent=2, output=output)

# access packages and modules
meerkat = dsm['meerkat']  # or dsm.get('meerkat')
finder = dsm['dependenpy.finder']  # or even dsm['dependenpy']['finder']

# instances of DSM and Package all have print, as_matrix, etc. methods
meerkat.print_matrix(depth=2)
```

This package was originally design to work in a Django project.
The Django package [django-meerkat](https://github.com/Genida/django-meerkat)
uses it to display the matrices with Highcharts.

## Usage (command-line)

```
usage: gen-readme-data.py [-d DEPTH] [-f {csv,json,text}] [-g] [-G] [-h]
                          [-i INDENT] [-l] [-m] [-o OUTPUT] [-t] [-v]
                          PACKAGES [PACKAGES ...]

Command line tool for dependenpy Python package.

positional arguments:
  PACKAGES              The package list. Can be a comma-separated list. Each
                        package must be either a valid path or a package in
                        PYTHONPATH.

optional arguments:
  -d DEPTH, --depth DEPTH
                        Specify matrix or graph depth. Default: best guess.
  -f {csv,json,text}, --format {csv,json,text}
                        Output format. Default: text.
  -g, --show-graph      Show the graph (no text format). Default: false.
  -G, --greedy          Explore subdirectories even if they do not contain an
                        __init__.py file. Can make execution slower. Default:
                        false.
  -h, --help            Show this help message and exit.
  -i INDENT, --indent INDENT
                        Specify output indentation. CSV will never be
                        indented. Text will always have new-lines. JSON can be
                        minified with a negative value. Default: best guess.
  -l, --show-dependencies-list
                        Show the dependencies list. Default: false.
  -m, --show-matrix     Show the matrix. Default: true unless -g, -l or -t.
  -o OUTPUT, --output OUTPUT
                        Output to given file. Default: stdout.
  -t, --show-treemap    Show the treemap (work in progress). Default: false.
  -v, --version         Show the current version of the program and exit.

```

Example:

```console
$ # running dependenpy on itself
$ dependenpy dependenpy -z=

                Module │ Id │0│1│2│3│4│5│6│7│8│
 ──────────────────────┼────┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
   dependenpy.__init__ │  0 │ │ │ │4│ │ │ │ │2│
   dependenpy.__main__ │  1 │ │ │1│ │ │ │ │ │ │
        dependenpy.cli │  2 │1│ │ │1│ │4│ │ │ │
        dependenpy.dsm │  3 │ │ │ │ │2│1│3│ │ │
     dependenpy.finder │  4 │ │ │ │ │ │ │ │ │ │
    dependenpy.helpers │  5 │ │ │ │ │ │ │ │ │ │
       dependenpy.node │  6 │ │ │ │ │ │ │ │ │3│
    dependenpy.plugins │  7 │ │ │ │1│ │1│ │ │ │
 dependenpy.structures │  8 │ │ │ │ │ │1│ │ │ │

```
