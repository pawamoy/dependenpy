dependenpy
==========

.. image:: https://travis-ci.org/Pawamoy/dependenpy.svg?branch=master
    :target: https://travis-ci.org/Pawamoy/dependenpy
    :alt: Build Status

.. image:: https://readthedocs.org/projects/dependenpy/badge/?version=latest
    :target: https://readthedocs.org/projects/dependenpy/?badge=latest
    :alt: Documentation Status

.. image:: https://coveralls.io/repos/Pawamoy/dependenpy/badge.svg?branch=master
    :target: https://coveralls.io/r/Pawamoy/dependenpy?branch=master
    :alt: Coverage Status

This Python module can build the dependency matrices of a project's packages, based on `from ... import ...` commands in their modules. For now, its purpose is purely informational.

The module is composed of only one class: DependencyMatrix, which is initialized with a list of packages foundable is sys.path. This list of packages can be a string (one package), a list (several) or an ordered dictionary, used to define groups of packages with a legend. We use an ordered dictionary because it is important to keep the same order as the one given by the user. On the other hand it is not always handy to pass an OrderedDict instance, so in the future we could maybe pass a list of dict.

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