import distutils.sysconfig as sysconfig
import os
from pathlib import Path

std = []
std_lib = Path(sysconfig.get_python_lib(standard_lib=True))
for path in std_lib.iterdir():
    if not path.name.startswith("_") and (path.is_dir() or path.suffix == ".py"):
        std.append(path.stem)

print("\n".join(sorted(std)))
