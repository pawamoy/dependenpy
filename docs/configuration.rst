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
To do so, instead of passing a `list` to the `MatrixBuilder` constructor,
you can pass an `OrderedDict`, imported from `collections`. Example:

.. code:: python

    from collections import OrderedDict
    from dependenpy.utils import MatrixBuilder

    my_packages = OrderedDict()

    my_packages['Framework'] = ['django']
    my_packages['Libraries'] = ['dependenpy', 'django-dpdpy']
    my_packages['Core features'] = ['members', 'surveys', 'news']
    my_packages['Security layer'] = ['broker']

    my_dm = MatrixBuilder(my_packages)


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

    from dependenpy.utils import MatrixBuilder

    my_packages = ...

    def get_django_module_path(module):
        module_path = sys.modules.get(module)
        if module_path:
            return 'py'.join(module_path.__file__.rsplit('pyc'))
        return None

    my_dm = MatrixBuilder(my_packages, get_django_module_path)

.. warning::

    In a Django project, to include packages in your dependency matrix that
    are not listed in your `settings.INSTALLED_APPS`, you have to use the
    default path resolver (it is currently not possible to specify several
    path resolver methods).

