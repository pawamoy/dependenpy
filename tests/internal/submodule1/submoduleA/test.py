# IGNORED: builtin import
import builtin

# OK: relative import, should be transformed into internal.test
from ...test import someclass

# OK: relative import, multiple
from ...test import classA, classB
from ...test import (classC, classD)
from ...test import (
    classE, classF)
from ...test import classG, \
    classH

# total: 1
