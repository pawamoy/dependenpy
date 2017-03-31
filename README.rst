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

A Python module that build dependency matrices between other modules.

This Python module can build the dependency matrices of a project's packages,
based on ``from ... import ...`` commands in their modules.
For now, its purpose is purely informational.

The module is composed of two classes: MatrixBuilder,
which is initialized with a list of packages available is ``sys.path``, and Matrix,
which is an autonomous class containing matrix data.
This list of packages can be a string (one package), a list of string (several)
or another type of list, used to define groups of packages with a legend.

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

Thanks
======

Thanks to `dmishin`_ for the TSP solver, needed to compute the similarity order.

.. _dmishin: https://github.com/dmishin
