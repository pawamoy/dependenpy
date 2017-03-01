#!/usr/bin/env python

import sys
import pprint
from dependenpy.utils import Module

# pprint.pprint(sys.path)

m1 = Module('django')
m2 = Module('dependenpy')
m3 = Module('dependenpy.utils')
m4 = Module('tests/internal')


# pprint.pprint(m1.__dict__)
# pprint.pprint(m2.__dict__)
# pprint.pprint(m3.__dict__)

pprint.pprint([(i.by.name, i.name) for i in m4.imports()])
