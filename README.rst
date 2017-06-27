==========
Dependenpy
==========

.. start-badges


|travis|
|codacygrade|
|codacycoverage|
|version|
|wheel|
|pyup|
|gitter|


.. |travis| image:: https://travis-ci.org/Pawamoy/dependenpy.svg?branch=master
    :target: https://travis-ci.org/Pawamoy/dependenpy/
    :alt: Travis-CI Build Status

.. |codacygrade| image:: https://api.codacy.com/project/badge/Grade/6cac1ad3e1a34d349ef4dd73cf3e5276
    :target: https://www.codacy.com/app/Pawamoy/dependenpy/dashboard
    :alt: Codacy Code Quality Status

.. |codacycoverage| image:: https://api.codacy.com/project/badge/Coverage/6cac1ad3e1a34d349ef4dd73cf3e5276
    :target: https://www.codacy.com/app/Pawamoy/dependenpy/dashboard
    :alt: Codacy Code Coverage

.. |pyup| image:: https://pyup.io/repos/github/Pawamoy/dependenpy/shield.svg
    :target: https://pyup.io/repos/github/Pawamoy/dependenpy/
    :alt: Updates

.. |version| image:: https://img.shields.io/pypi/v/dependenpy.svg?style=flat
    :target: https://pypi.python.org/pypi/dependenpy/
    :alt: PyPI Package latest release

.. |wheel| image:: https://img.shields.io/pypi/wheel/dependenpy.svg?style=flat
    :target: https://pypi.python.org/pypi/dependenpy/
    :alt: PyPI Wheel

.. |gitter| image:: https://badges.gitter.im/Pawamoy/dependenpy.svg
    :target: https://gitter.im/Pawamoy/dependenpy
    :alt: Join the chat at https://gitter.im/Pawamoy/dependenpy



.. end-badges

Dependenpy allows you to build a dependency matrix for a set of Python packages.
To do this, it reads and searches the source code for import statements.

License
=======

Software licensed under `ISC`_ license.

.. _ISC: https://www.isc.org/downloads/software-support-policy/isc-license/

Installation
============

::

    pip install dependenpy


Usage
=====

Version 3 introduces a command-line tool:

Example:

.. code:: bash

    dependenpy -h

Result:

.. code:: bash

    usage: dependenpy [-d DEPTH] [-f {csv,json,text}] [-g] [-G] [-h] [-i INDENT] [-l] [-m]
                  [-o OUTPUT] [-t] [-v]
                  PACKAGES [PACKAGES ...]

    Command line tool for dependenpy Python package.

    positional arguments:
      PACKAGES              The package list. Can be a comma-separated list. Each package
                            must be either a valid path or a package in PYTHONPATH.

    optional arguments:
      -d DEPTH, --depth DEPTH
                            Specify matrix or graph depth. Default: best guess.
      -f {csv,json,text}, --format {csv,json,text}
                            Output format. Default: text.
      -g, --show-graph      Show the graph (no text format). Default: false.
      -G, --greedy          Explore subdirectories even if they do not contain an
                            __init__.py file. Can make execution slower. Default: false.
      -h, --help            Show this help message and exit.
      -i INDENT, --indent INDENT
                            Specify output indentation. CSV will never be indented. Text
                            will always have new-lines. JSON can be minified with a
                            negative value. Default: best guess.
      -l, --show-dependencies-list
                            Show the dependencies list. Default: false.
      -m, --show-matrix     Show the matrix. Default: true unless -g, -l or -t.
      -o OUTPUT, --output OUTPUT
                            Output to given file. Default: stdout.
      -t, --show-treemap    Show the treemap (work in progress). Default: false.
      -v, --version         Show the current version of the program and exit.

Example:

.. code:: bash

    dependenpy dependenpy
    dependenpy dependenpy --depth=2

Result:

.. code:: bash

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

You can also use dependenpy programmatically:

.. code:: python

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

This package was originally design to work in a Django project.
The Django package `django-meerkat`_ uses it to display the matrices with Highcharts.

.. _django-meerkat: https://github.com/Pawamoy/django-meerkat


Documentation
=============

`On ReadTheDocs`_

.. _`On ReadTheDocs`: http://dependenpy.readthedocs.io/

Development
===========

To run all the tests: ``tox``
