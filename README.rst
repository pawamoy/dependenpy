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

Version 3
---------

Version 3 introduces a command-line tool:

Example:

.. code:: bash

    dependenpy -h

Result:

.. code:: bash

    usage: dependenpy [-d DEPTH] [-l] [-m] [-o OUTPUT] [-v] [-h] PACKAGES [PACKAGES ...]

    Command line tool for dependenpy Python package.

    positional arguments:
      PACKAGES              The package list. Can be a comma-separated list. Each package must be either a valid path or a package in PYTHONPATH.

    optional arguments:
      -d DEPTH, --depth DEPTH
                            Matrix depth. Default: 2 if one package, otherwise 1.
      -i, --enforce-init    Enforce presence of __init__.py when listing
                            directories. Default: false.
      -l, --show-dependencies-list
                            Show the dependencies list. Default: false.
      -m, --show-matrix     Show the matrix. Default: false.
      -o OUTPUT, --output OUTPUT
                            File to write to. Default: stdout.
      -v, --version         Show program's version number and exit.
      -h, --help            Show this help message and exit.

Example:

.. code:: bash

    dependenpy dependenpy
    dependenpy dependenpy --depth=2

Result:

.. code:: bash

                  Module | Id ||0|1|2|3|
     --------------------+----++-+-+-+-+
     dependenpy.__init__ |  0 ||0|0|0|4|
     dependenpy.__main__ |  1 ||0|0|1|0|
          dependenpy.cli |  2 ||0|0|0|1|
          dependenpy.dsm |  3 ||0|0|0|0|

Example:

.. code:: bash

    dependenpy -l dependenpy

Result:

.. code:: bash

    Dependency DSM for packages: [dependenpy]
      dependenpy
        __main__
          ! __main__ imports sys (line 13)
          __main__ imports main from dependenpy.cli (line 15)
        dsm
          ! dsm imports ast (line 5)
          ! dsm imports os (line 6)
          ! dsm imports sys (line 7)
          ! dsm imports copy.deepcopy (line 8)
          ! dsm imports importlib.util.find_spec (line 9)
          ! dsm imports os.path.basename (line 10)
          ! dsm imports os.path.dirname (line 10)
          ! dsm imports os.path.exists (line 10)
          ! dsm imports os.path.isdir (line 10)
          ! dsm imports os.path.isfile (line 10)
          ! dsm imports os.path.join (line 10)
          ! dsm imports os.path.splitext (line 10)
        cli
          ! cli imports argparse (line 20)
          ! cli imports sys (line 21)
          cli imports DSM from dependenpy.dsm (line 23)
        __init__
          __init__ imports DSM from dependenpy.dsm (line 11)
          __init__ imports Dependency from dependenpy.dsm (line 11)
          __init__ imports Module from dependenpy.dsm (line 11)
          __init__ imports Package from dependenpy.dsm (line 11)

Example:

.. code:: bash

    dependenpy json,setuptools
    dependenpy json setuptools

Result:

.. code:: bash

         Module | Id ||0 |1 |
     -----------+----++--+--+
           json |  0 || 5| 0|
     setuptools |  1 || 0|75|

You can also use dependenpy programmatically:

.. code:: python

    from dependenpy import DSM

    # create DSM
    dsm = DSM('django')

    # transform as matrix, dict of deps or treemap
    matrix = dsm.as_matrix(depth=2)
    deps = dsm.as_dict()
    treemap = dsm.as_treemap()  # soon

    # initialize with many packages
    dsm = DSM('django', 'meerkat', 'appsettings', 'dependenpy', 'archan')
    with open('output', 'w') as output:
        dsm.print(matrix=True, depth=1, dependencies=True, output=output)

    # access packages and modules
    meerkat = dsm['meerkat']  # or dsm.get('meerkat')
    finder = dsm['dependenpy.finder']  # or even dsm['dependenpy']['finder']

    # instances of DSM and Package all have print, as_matrix, etc. methods
    meerkat.print_matrix(depth=2)

Version 2
---------

.. code:: python

    from dependenpy.utils import MatrixBuilder

    myapps = (
        ‘module1’,
        ‘module2’,
        ‘...’,
        ‘moduleN’
    )

    # Create an empty instance
    dm = MatrixBuilder(myapps)

    # Init its data with build methods
    dm.build()

    # You can also use separately dm.build_modules(),
    # dm.build_imports() and dm.build_matrices().
    # You can even chain them: dm.build_modules().build_imports().build_matrices().
    # The order is important, since matrices need imports, and imports need modules.
    # The build() method is just a shortcut of the above chained command.

    # Print max depth of submodules and the big dictionary of imports
    print dm.max_depth
    print dm.imports

    # Output matrix of depth 1 in CSV
    dm.get_matrix(1).to_csv()

    # Output matrix of maximum depth in JSON
    dm.get_matrix(0).to_json()


The "other type" of list you can give to a MatrixBuilder looks like this:

.. code:: python

    my_packages = [
        'Framework', ['django'],
        'Libraries', ['dependenpy', 'django-archan'],
        'Core features', ['members', 'surveys', 'news']
        'Security layer', ['broker']
    ]

This way you can specify groups of packages.

This module was originally design to work in a Django project.
The Django package `django-meerkat`_ uses it to display the matrices with Highcharts.

.. _django-meerkat: https://github.com/Pawamoy/django-meerkat


Documentation
=============

`On ReadTheDocs`_

.. _`On ReadTheDocs`: http://dependenpy.readthedocs.io/

Development
===========

To run all the tests: ``tox``
