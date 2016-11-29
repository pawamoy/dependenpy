# OK: relative import, should be transformed into internal.submodule2.test2
from .test2 import someclass

# OK: absolute import, here to test similarity
from internal.submodule1.submoduleA import othertest

# total: 1
