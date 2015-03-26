.. Dependenpy documentation master file, created by
   sphinx-quickstart on Sat Feb 21 19:10:20 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Dependenpy's documentation!
======================================

*dependenpy* is a Python package that helps you build a dependency matrix
of your project. You just give the list of packages that have to be scanned
and *dependenpy* automatically parses all the code to build dependencies
between modules, based on `from ... import ...` instructions.
You can then output and use content as JSON or CSV.

.. note::

   *dependenpy* **can not do** matrix computations. If this is what you need,
   consider using libraries that are optimized for this. However, *dependenpy*
   has built-ins methods that allow you to sort the matrix according to different
   criteria.


Why would you do that ?
-----------------------

Some projects need increased security for various reasons,
and visualizing the dependencies between the different modules of your project
can really help you refactor your code to reduce the sources of bugs and/or
security flaws.


Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   usage
   configuration


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

