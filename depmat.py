import sys
from dependenpy.utils import DependencyMatrix

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
)

dm = DependencyMatrix(INSTALLED_APPS)
dm.compute_matrix()

if len(sys.argv) > 1:
    depth = int(sys.argv[1])
else:
    depth = 0

matrix = dm.get_matrix(depth)
matrix.print_keys()
print
matrix.print_data()
