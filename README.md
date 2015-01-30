dependenpy
=======

This Python module can build two dimensions arrays (lists of lists or matrices)
representing the dependencies between other Python modules.
For now, its purpose is purely informational.

Usage
-----

```python
from dependenpy.utils import DependencyMatrix

myapps = (
    ‘module1’,
    ‘module2’,
    ‘...’,
    ‘moduleN’
)

dm = DependencyMatrix(myapps)

# Print max depth of submodules and the big dictionary of imports
print dm.max_depth
print dm.imports

# Actually build the matrices, one for each depth
dm.compute_matrix()

m1 = dm.get_matrix(1)

# Equivalent to m_max = dm.get_matrix(dm.max_depth)
m_max = dm.get_matrix(0)

# Print size of the square matrix
print len(m_max)

# Output matrix on stdout
m_max.print_data()
```

A Bash script and Python script are provided to improve the display of the matrices.
To use them, just update the module list in `depmat.py` and run `./pretty_matrix.sh [DEPTH]`.

This module was originally design to work in a Django project.
A Django package might be built using this tool to let admins
see dependency matrices of the project and keep a history of them.
