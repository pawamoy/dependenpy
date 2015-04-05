dependenpy
==========

.. image:: https://pypip.in/version/dependenpy/badge.svg
    :target: https://pypi.python.org/pypi/dependenpy/
    :alt: Latest Version

.. image:: https://pypip.in/status/dependenpy/badge.svg
    :target: https://pypi.python.org/pypi/dependenpy/
    :alt: Development Status

.. image:: https://pypip.in/format/dependenpy/badge.svg
    :target: https://pypi.python.org/pypi/dependenpy/
    :alt: Download format

.. image:: https://travis-ci.org/Pawamoy/dependenpy.svg?branch=master
    :target: https://travis-ci.org/Pawamoy/dependenpy
    :alt: Build Status

.. image:: https://readthedocs.org/projects/dependenpy/badge/?version=latest
    :target: https://readthedocs.org/projects/dependenpy/?badge=latest
    :alt: Documentation Status

.. image:: https://coveralls.io/repos/Pawamoy/dependenpy/badge.svg?branch=master
    :target: https://coveralls.io/r/Pawamoy/dependenpy?branch=master
    :alt: Coverage Status

.. image:: https://landscape.io/github/Pawamoy/dependenpy/master/landscape.svg?style=flat
   :target: https://landscape.io/github/Pawamoy/dependenpy/master
   :alt: Code Health

.. image:: https://pypip.in/py_versions/dependenpy/badge.svg
    :target: https://pypi.python.org/pypi/dependenpy/
    :alt: Supported Python versions

.. image:: https://pypip.in/license/dependenpy/badge.svg
    :target: https://pypi.python.org/pypi/dependenpy/
    :alt: License

This Python module can build the dependency matrices of a project's packages,
based on ``from ... import ...`` commands in their modules.
For now, its purpose is purely informational.

The module is composed of two classes: MatrixBuilder,
which is initialized with a list of packages foundable is sys.path, and Matrix,
which is an autonomous class containing matrix data.
This list of packages can be a string (one package), a list of string (several)
or another type of list, used to define groups of packages with a legend.

Usage
-----

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


Here is an example of colorized CSV output:

.. image:: http://imageshack.com/a/img537/3731/myhqOU.png
    :alt: CSV array



This module was originally design to work in a Django project.
The Django package `django-archan`_ has been built on it to display the matrices with D3JS.

.. _django-archan: https://github.com/Pawamoy/archan

Documentation
-------------

On `ReadTheDocs`_

.. _ReadTheDocs: http://dependenpy.readthedocs.org/en/latest/


License
-------

Copyright (c) 2015 Timothée Mazzucotelli

This Source Code is subject to the terms of the Mozilla Public
License, v. 2.0. See the LICENSE.txt file for more details.

Thanks
------

Thanks to `dmishin`_ for the TSP solver, needed to compute the similarity order.

.. _dmishin: https://github.com/dmishin