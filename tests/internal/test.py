# builtin import, ignored
import builtin

# package import, should be transformed to submodule2.__init__
from internal import submodule2

# idem
from internal.submodule1 import submoduleA

# test module exists, should be OK
from internal.submodule1.submoduleA import test

# relative import, should be transformed to internal.test
from . import test

# internal but does not exists, ignored
from internal.submodule2 import doesnotexists

# exists but external, ignored
from external import exists
