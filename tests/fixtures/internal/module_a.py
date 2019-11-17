import os

import external
from external import module_a
from external.module_a import ClassA

from . import subpackage_1 as indirect_subpackage_1
from . import subpackage_a
from .subpackage_a import subpackage_1


class ClassA(object):
    pass
