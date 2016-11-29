# IGNORED: builtin import
import builtin

# OK: package import, should be transformed to internal.__init__
from internal import submodule2

# OK: package import, should be transformed to internal.submodule1.__init__
from internal.submodule1 import submoduleA

# OK: idem, submoduleA exists
from internal.submodule1.submoduleA import test

# IGNORED: local import, ignored (not interesting)
from . import test

# OK: internal, does not exists, but is added
# because we only check 'from' parts
from internal.submodule2 import doesnotexists

# IGNORED: exists but external
from external.exists import something

# total: 4
