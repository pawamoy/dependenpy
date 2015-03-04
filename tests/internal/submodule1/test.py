# relative import, should be transformed into internal.submodule1.submoduleA
from .submoduleA import test
from .submoduleA.test import Test

# absolute import, should be OK
from internal.submodule1.submoduleA import Test

# relative import, should be transformed into internal.test
from .. import test
