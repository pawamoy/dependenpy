from dependenpy import DSM, Module


def _cycles(dsm):
    cycles = set()
    for pkg in dsm.packages:
        for mod in pkg.modules:
            try:
                _cycle(mod, set())
            except CycleError as cycle:
                cycles.add(tuple(cycle.path))
    if cycles:
        print("Cycles detected:")
        for cycle in cycles:
            indent = "  "
            for mod in cycle:
                print(f"{indent}{mod}")
                indent += "  "


def _cycle(mod, seen):
    if mod in seen:
        raise CycleError([mod])
    seen.add(mod)
    for dep in mod.dependencies:
        if isinstance(dep.target, Module):
            try:
                _cycle(dep.target, seen)
            except CycleError as cycle:
                if cycle.complete:
                    raise cycle
                complete = mod in cycle.path
                raise CycleError([mod] + cycle.path, complete=complete)


class CycleError(Exception):
    def __init__(self, path, complete=False) -> None:
        super().__init__("cycle detected")
        self.path = path
        self.complete = complete


dsm = DSM("griffe")
_cycles(dsm)
