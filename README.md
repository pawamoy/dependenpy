dependenpy
=======

This Python module can build the dependency matrices of a project's packages, based on `import` and `from ... import ...` commands in their modules.
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

# Output matrix as JSON
print m_max.to_json()
```

This module was originally design to work in a Django project.
The Django package django-dpdpy has been built with it to display the matrices with D3JS.

