import re
from dependenpy import DSM
import tomllib
from importlib.metadata import packages_distributions

_dists = packages_distributions()


def _undeclared(package, declared, undeclared):
    for pkg in package.packages:
        _undeclared(pkg, declared, undeclared)
    for mod in package.modules:
        for dep in mod.dependencies:
            if isinstance(dep.target, str):
                top = dep.target.split(".", 1)[0]
                if top in _dists:
                    for _dist in _dists[top]:
                        dist = _dist.replace("_", "-").lower()
                        if dist not in declared:
                            if dist not in undeclared:
                                undeclared.add(dist)
                                print(f"Undeclared dependency: {dist}")
                                break


dsm = DSM("griffe")
with open("pyproject.toml", "rb") as file:
    pyproject = tomllib.load(file)
declared = {
    re.search(r"^([a-z0-9._-]+)", dep).group(1).replace("_", "-").lower()
    for dep in pyproject["project"]["dependencies"]
}
undeclared = set()
_undeclared(dsm, declared, undeclared)
