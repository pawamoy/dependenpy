Configuration
=============

Using groups
------------

In your project, you can have different types of packages:

* libraries
* main features
* security apps
* frameworks
* ...

It would be great to organize your packages by groups.
To do so, instead of passing a `list` to the `DependencyMatrix` constructor,
you can pass an `OrderedDict`, imported from `collections`. Example:

.. code:: python

    from collections import OrderedDict
    from dependenpy.utils import DependencyMatrix

    my_packages = OrderedDict()

    my_packages['Framework'] = ['django']
    my_packages['Libraries'] = ['dependenpy', 'django-dpdpy']
    my_packages['Core features'] = ['members', 'surveys', 'news']
    my_packages['Security layer'] = ['broker']

    my_dm = DependencyMatrix(my_packages)


Finding modules' paths
----------------------

By default, *dependenpy* uses its own function to get the absolute path
of a module on your system: `resolve_path`.

.. autofunction:: dependenpy.utils.resolve_path

As you can see, this function loops over all directories in sys.path to find
the specified module.

But you can specify your own function that DependencyMatrix will use.
Your function must return the absolute path to the module, with \__init__.py
appended if it is a (sub)package, and return None if the module was not found.

For example, in a Django project, there is a quicker way of finding the path
of a module than looping over sys.path: using `sys.modules.get(module_name)`.

.. code:: python

    from dependenpy.utils import DependencyMatrix

    my_packages = ...

    def get_django_module_path(module):
        module_path = sys.modules.get(module)
        if module_path:
            return 'py'.join(module_path.__file__.rsplit('pyc'))
        return None

    my_dm = DependencyMatrix(my_packages, get_django_module_path)

.. warning::

    In a Django project, to include packages in your dependency matrix that
    are not listed in your `settings.INSTALLED_APPS`, you have to use the
    default path resolver (it is currently not possible to specify several
    path resolver methods).


Filtering JSON output
---------------------

By default, the `matrix_to_json` method outputs all available data, using
the following filter options.

.. autodata:: dependenpy.utils.DEFAULT_OPTIONS

    * `group_name` is the name of the module's group
    * `group_index` is the position of the module's group in the list of groups
    * `source_name` is the name of the **importing** module
    * `source_index` is the position of the **importing** module in the list of modules
    * `target_name` is the name of the **imported** module
    * `target_index` is the position of the **imported** module in the list of modules
    * `imports` is the list of imports (dict containing 'by', 'from' and 'import') done by the source
    * `cardinal` is the number of imports done by the source

If you create a DependencyMatrix object in an huge project, the lists of
imports (`imports` option) for each dependency might also be enormous.
It would be a waste of time and space to output or store it
if you don't need it. The other options involve just one value for each dependency.

Use options like this:

.. code:: python

    my_options = {
        'group_name': False,
        'group_index': True,
        'source_name': False,
        'source_index': True,
        'target_name': False,
        'target_index': True,
        'imports': False,
        'cardinal': True,
    }

    my_dm.matrix_to_json(2, my_options)
