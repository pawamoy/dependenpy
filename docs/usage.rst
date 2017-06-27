Usage
=====

- :ref:`Importing`
- :ref:`ObjectsCreation`

  - :ref:`CreateDSM`
  - :ref:`CreatePackage`
  - :ref:`CreateModule`
  - :ref:`CreateDependency`
  - :ref:`CreateMatrix`
  - :ref:`CreateTreeMap`
  - :ref:`CreateGraph`

- :ref:`AccessingElements`
- :ref:`PrintContents`

.. _Importing:

Importing classes
-----------------

You can directly import the following classes from ``dependenpy``:
``DSM``, ``Package``, ``Module``, ``Dependency``, ``Matrix`` and ``TreeMap``.

If you need to import other classes, please take a look at the structure
of the code.

Example:

.. code:: python

    from dependenpy import DSM, Matrix

.. _ObjectsCreation:

Creation of objects
-------------------

For basic usage, you only have to instantiate a ``DSM`` object, and
sometimes ``Matrix`` and ``TreeMap``. But if you need to do more complicated
stuff, you might also want to build instances of ``Package``, ``Module``
or ``Dependency``.

.. _CreateDSM:

Create a DSM
''''''''''''

To create a ``DSM`` object, just pass it a list of packages that can be either
found on the disk (absolute or relative paths), or in the Python path (like
in ``sys.path``).

.. code:: python

    from dependenpy import DSM
    django = DSM('django')
    flask = DSM('flask')
    both = DSM('django', 'flask')

Three keyword arguments can be given to ``DSM``:

- ``build_tree``: Boolean
- ``build_dependencies``: Boolean
- ``enforce_init``: Boolean

The three of them defaults to true.

Turning ``build_tree`` to false will delay the build of the Python package
tree (the exploration of files on the file system).
You can later call ``dsm.build_tree()`` to build the tree.

Turning ``build_dependencies`` to false will delay the build of the
dependencies (the parsing of the source code to determine the
inter-dependencies).
You can later call ``dsm.build_dependencies()`` to build the dependencies.
Note that you won't be able to build the dependencies before the tree has
been built.

Using true for both ``build_tree`` and ``build_dependencies`` is recommended
since it is done pretty quickly, even for big projects like Django.

Turning ``enforce_init`` to false will make the exploration of sub-directories
complete: by default, a sub-directory is not explored if it does not contain
an ``__init__.py`` file. It makes the building of the tree faster. But in some
cases, you might want to still explore the sub-directory even without
``__init__.py``. In that case, use ``enforce_init=False``. Note that
depending on the tree, the build might take longer.

.. _CreatePackage:

Create a Package
''''''''''''''''

To create a ``Package`` object, initialize it with a name and a path.
These two arguments are the only one required. Name should be the name of
the Python package (the name of the directory), and path should be
the path to the directory on the file system.

Example:

.. code:: python

    from dependenpy import Package
    absolute_package = Package('django', '/my/virtualenv/lib/python3.5/site-packages/django')
    relative_package = Package('program', 'src/program')

Additionally, you can pass 6 more keyword arguments: the same three from
``DSM`` (``build_tree``, ``build_dependencies`` and ``enforce_init``), and
the three following:

- ``dsm``: parent DSM (instance of DSM).
- ``package``: parent package (instance of Package).
- ``limit_to``: list of strings to limit the exploration to a subset of
  directories.

These three arguments default to ``None``. Both ``dsm`` and ``package``
arguments are useful to build a tree.

Argument ``limit_to`` can be used this way:

.. code:: python

    from dependenpy import Package
    django_auth = Package('django', 'path/to/django',
                          limit_to=['contrib.auth'])

Of course, you could also have build a the ``django_auth`` Package by directly
specify the name and path of the sub-directory, but using limit_to allows you
to build the full tree, starting at the root (Django's directory).

.. code:: python

    from dependenpy import Package
    django_auth = Package('auth', 'path/to/django/contrib/auth')

.. _CreateModule:

Create a Module
'''''''''''''''

To create a ``Module`` object, initialize it with a name and a path.
These two arguments are the only one required. Name should be the name of
the Python module (the file without the ``.py`` extension), and path should be
the path to the file on the file system.

As for ``Package``, ``dsm`` and ``package`` arguments can be passed when
creating a module.

Example:

.. code:: python

    from dependenpy import Module
    dsm_module = Module('dsm', 'path/to/dependenpy/dsm.py')

.. _CreateDependency:

Create a Dependency
'''''''''''''''''''

A dependency is a simple object that require:

- ``source``: the ``Module`` instance importing the item,
- ``lineno``: the line number at which the import occurred,
- ``target``: the ``Package`` or ``Module`` instance from which the item is imported
- and an optional ``what`` argument which defaults to None: the name of the
  imported item.

.. _CreateMatrix:

Create a Matrix
'''''''''''''''

From an instance of ``DSM`` or ``Package`` called ``node``:

.. code:: python

    matrix = node.as_matrix(depth=2)

From a list of nodes (DSMs, packages or modules):

.. code:: python

    matrix = Matrix(*node_list, depth=2)

An instance of ``Matrix`` has a ``data`` attribute, which is a two-dimensions
array of integers, and a ``keys`` attribute which is the list of names,
in the same order as rows in data.

.. _CreateTreeMap:

Create a TreeMap
''''''''''''''''

From an instance of ``DSM`` or ``Package`` called ``node``:

.. code:: python

    treemap = node.as_treemap(depth=2)

From a list of nodes (DSMs, packages or modules):

.. code:: python

    matrix = TreeMap(*node_list, depth=2)

An instance of ``TreeMap`` has a ``data`` attribute, which is a two-dimensions
array of integers or treemaps, a ``keys`` attribute which is the list of names
in the same order as rows in data, and a ``value`` attribute which is the
total number of dependencies in the treemap.

.. _CreateGraph:

Create a Graph
''''''''''''''

From an instance of ``DSM`` or ``Package`` called ``node``:

.. code:: python

    graph = node.as_graph(depth=2)

From a list of nodes (DSMs, packages or modules):

.. code:: python

    graph = Graph(*node_list, depth=2)

An instance of ``Graph`` has a ``vertices`` attribute, which is a list of
``Vertex`` instances, and a ``edges`` attribute which is list of ``Edge``
instances. See the documentation of ``Vertex`` and ``Edge`` for more
information.

.. _AccessingElements:

Accessing elements
------------------

Accessing elements in a DSM or a Package is very easy. Just like for a
dictionary, you can use the ``[]`` notation to search for a sub-package or
a sub-module. You can also use the ``get`` method, which is equivalent to
the brackets accessor, but will return ``None`` if the element is not found
whereas brackets accessor will raise a ``KeyError``.

Example:

.. code:: python

    from dependenpy import DSM

    dsm = DSM('django')  # full DSM object, containing Django
    django = dsm['django']  # Django Package object

You can use dots in the element name to go further in just one instruction:

.. code:: python

    django_auth = django['contrib.auth']
    django_forms_models = dsm.get('django.forms.models')

Of course, accesses can be chained:

.. code:: python

    django_db_models_utils = dsm['django'].get('db')['models']['utils']

.. _PrintContents:

Print contents
--------------

Contents of DSMs, packages, modules, matrices, treemaps and graphs can be printed
with their ``print`` method. The contents printed are the dependencies.
With some exception, each one of them can output contents in three different formats:

- text (by default)
- CSV
- JSON

(Currently, treemaps are not implemented, and graphs can only be printed in
JSON or CSV.)

To choose one of these format, just pass the ``format`` argument, which accepts
values ``'text'``, ``'csv'`` and ``'json'``. Please note that these values
can be replaced by constants imported from ``dependenpy.helpers``
module:

.. code:: python

    from dependenpy import DSM
    from dependenpy.helpers import TEXT, CSV, JSON

    dsm = DSM('django')
    dsm.print(format=JSON)

Depending on the chosen format, additional keyword arguments can be passed
to the print method:

- text format: ``indent``, indentation value (integer)
- CSV format: ``header``, True or False, to display the headers (columns names)
- JSON format: every arguments accepted by ``json.dumps``, and in the case
  of a ``Module`` instance, ``absolute`` Boolean to switch between output
  of absolute and relative paths.

For ``DSM`` and ``Package`` instances, shortcuts to print a matrix, a treemap
or a graph are available with ``print_matrix``, ``print_treemap`` and
``print_graph`` methods.
These methods will first create the related object and then call
the object's own ``print`` method.
