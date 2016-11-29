# OK: relative import, should be transformed into internal.submodule1.submoduleA
from .submoduleA import test
from .submoduleA.test import Test1

# OK: absolute import
from internal.submodule1.submoduleA import othertest

# OK: relative import, should be transformed into internal.test
from .. import test

# total: 3
