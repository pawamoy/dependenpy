# OK: relative import, should be transformed into internal.submodule1.submoduleA
from .submoduleA import test
from .submoduleA.test import Test1

# OK: absolute import
from internal.submodule1.submoduleA import othertest

# OK: relative import, should be transformed into internal.test
from .. import test

# OK: "as" clause should be recognized
from ..submodule2 import test as test2

# TODO: we need to handle import statements as well
# OK !BUT NOT HANDLED YET!: internal import statements should be handled
import internal.submodule1 as sub1

# total: 4
