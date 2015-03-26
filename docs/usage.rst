Usage
=====

Project structure
-----------------

In your project, you have packages, each of them containing modules,
and potentially sub-modules. Example::

    core
        __init__.py
        utils.py
        models.py
    feature1
        __init__.py
        subfeatureA
            __init__.py
            main.py
    feature2
        __init__.py
        main.py
    security
        __init.py
        utils.py

In this case we have modules of depth 1 (packages), modules of depth 2 (like
`core.__init__` or `core.models`), and modules of depth 3:
`feature1.subfeatureA.__init__` and `feature1.subfeatureA.main`.

Therefore, we consider the maximum depth of this project modules equal to 3.
The DependencyMatrix class of *dependenpy* builds one matrix for each depth,
starting from the maximum depth (here: 3), to the top (depth 1), by summing
the imports while ascending.


Methods
-------

You can then access each one of the built matrices with the `get_matrix(depth)`
method, knowing that depth **0** is equivalent to the **maximum depth**.

.. autoclass:: dependenpy.utils.MatrixBuilder
    :members:


Example
-------

To instantiate, build and use/output your dependency matrix, a few steps:

* import the DependencyMatrix class
* set your list of packages
* instantiate a matrix with this list
* run its build methods
* use its attributes/methods to get content

.. code:: python

    from dependenpy.utils import MatrixBuilder


    # set the list of packages
    my_packages = [
        'core',
        'feature1',
        'feature2',
        'security',
    ]


    # create an object
    my_dm = MatrixBuilder(my_packages)


    # build the content progressively...
    # (the order is important)
    my_dm.build_modules()
    print my_dm.modules

    my_dm.build_imports()
    print my_dm.imports

    my_dm.build_matrices()
    print my_dm.matrices
    print dm.get_matrix(2)


    # ... or all at once
    my_dm.build()


    # then output the content as JSON...
    print dm.to_json()
    print dm.get_matrix(0).to_json()

    # ... or as CSV
    print dm.get_matrix(1).to_csv()

    # you can also directly write the CSV data into a file object
    with open("matrix.csv", "w") as my_csv:
        dm.matrix_to_csv(1, my_csv)


    # You can skip the assignation of the data builder object
    # to keep only one autonomous Matrix instance:
    my_matrix = MatrixBuilder(my_packages).build().get_matrix(2)
