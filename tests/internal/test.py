import builtin
import internal.submodule1
from internal import submodule2
from internal.submodule1 import submoduleA
from internal.submodule1 import submoduleA, test
from internal.submodule1.submoduleA import test
from . import test
from internal.submodule2 import doesnotexists
from external.exists import something
