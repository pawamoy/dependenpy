import os, sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('tests'))
from dependenpy.utils import MatrixBuilder as MB
dm = MB('internal')
dm.build()
