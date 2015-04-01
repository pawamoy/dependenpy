import os, sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('tests'))
from dependenpy.utils import MatrixBuilder as MB
dm = MB('internal')
dm.build()
m = dm.get_matrix(2)
m.compute_order('similarity')

print m.matrix
m.sort('similarity')
print m.matrix

m = dm.get_matrix(0)
m.compute_order('similarity')

print
print m.matrix
m.sort('similarity')
print m.matrix