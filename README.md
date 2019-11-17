<!--
IMPORTANT:
  This file is generated from the template at 'scripts/templates/README.md'.
  Please update the template instead of this file.
-->

# dependenpy
[![pipeline status](https://gitlab.com/pawamoy/dependenpy/badges/master/pipeline.svg)](https://gitlab.com/pawamoy/dependenpy/pipelines)
[![coverage report](https://gitlab.com/pawamoy/dependenpy/badges/master/coverage.svg)](https://gitlab.com/pawamoy/dependenpy/commits/master)
[![documentation](https://img.shields.io/readthedocs/dependenpy.svg?style=flat)](https://dependenpy.readthedocs.io/en/latest/index.html)
[![pypi version](https://img.shields.io/pypi/v/dependenpy.svg)](https://pypi.org/project/dependenpy/)

Build a dependency matrix for a set of Python packages.

`dependenpy` allows you to build a dependency matrix for a set of Python packages.
To do this, it reads and searches the source code for import statements.

.. image:: demo.svg
    :alt: Demo

## Requirements
dependenpy requires Python 3.6 or above.

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

With [`pipx`](https://github.com/cs01/pipx):
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
$ dependenpy dependenpy

                Module | Id ||0|1|2|3|4|5|6|7|8|
 ----------------------+----++-+-+-+-+-+-+-+-+-+
   dependenpy.__init__ |  0 ||0|0|0|4|0|0|0|0|2|
   dependenpy.__main__ |  1 ||0|0|1|0|0|0|0|0|0|
        dependenpy.cli |  2 ||1|0|0|1|0|4|0|0|0|
        dependenpy.dsm |  3 ||0|0|0|0|2|1|3|0|0|
     dependenpy.finder |  4 ||0|0|0|0|0|0|0|0|0|
    dependenpy.helpers |  5 ||0|0|0|0|0|0|0|0|0|
       dependenpy.node |  6 ||0|0|0|0|0|0|0|0|3|
    dependenpy.plugins |  7 ||0|0|0|1|0|1|0|0|0|
 dependenpy.structures |  8 ||0|0|0|0|0|1|0|0|0|
```



