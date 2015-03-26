import os, sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('tests'))
from dependenpy.utils import DependencyMatrix as DM
dm = DM('internal')
dm.build()
dm.get_matrix(3).sort('import')