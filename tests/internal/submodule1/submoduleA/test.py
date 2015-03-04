# builtin import, ignored
import builtin

# relative import, should be transformed into internal.test
from ...test import someclass
