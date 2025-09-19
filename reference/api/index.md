# dependenpy

Dependenpy package.

Show the inter-dependencies between modules of Python packages.

With dependenpy you will be able to analyze the internal dependencies in your Python code, i.e. which module needs which other module. You will then be able to build a dependency matrix and use it for other purposes.

If you read this message, you probably want to learn about the library and not the command-line tool: please refer to the README.md included in this package to get the link to the official documentation.

Modules:

- **`cli`** – Deprecated. Import from dependenpy directly.
- **`debug`** – Deprecated. Import from dependenpy directly.
- **`dsm`** – Deprecated. Import from dependenpy directly.
- **`finder`** – Deprecated. Import from dependenpy directly.
- **`helpers`** – Deprecated. Import from dependenpy directly.
- **`node`** – Deprecated. Import from dependenpy directly.
- **`plugins`** – Deprecated. Import from dependenpy directly.
- **`structures`** – Deprecated. Import from dependenpy directly.

Classes:

- **`DSM`** – DSM-capable class.
- **`Dependency`** – Dependency class.
- **`Edge`** – Edge class. Used in Graph class.
- **`Finder`** – Main package finder class.
- **`Graph`** – Graph class.
- **`InstalledPackageFinder`** – Finder to find installed Python packages using importlib.
- **`InternalDependencies`** – Dependenpy provider for Archan.
- **`LeafNode`** – Shared code between Package and Module.
- **`LocalPackageFinder`** – Finder to find local packages (directories on the disk).
- **`Matrix`** – Matrix class.
- **`Module`** – Module class.
- **`NodeMixin`** – Shared code between DSM, Package and Module.
- **`Package`** – Package class.
- **`PackageFinder`** – Abstract package finder class.
- **`PackageSpec`** – Holder for a package specification (given as argument to DSM).
- **`PrintMixin`** – Print mixin class.
- **`RootNode`** – Shared code between DSM and Package.
- **`TreeMap`** – TreeMap class.
- **`Vertex`** – Vertex class. Used in Graph class.

Functions:

- **`get_parser`** – Return the CLI argument parser.
- **`guess_depth`** – Guess the optimal depth to use for the given list of arguments.
- **`main`** – Run the main program.

Attributes:

- **`CSV`** – CSV format.
- **`FORMAT`** – Supported output formats.
- **`JSON`** – JSON format.
- **`TEXT`** – Plain text format.

## CSV

```
CSV = 'csv'
```

CSV format.

## FORMAT

```
FORMAT = (CSV, JSON, TEXT)
```

Supported output formats.

## JSON

```
JSON = 'json'
```

JSON format.

## TEXT

```
TEXT = 'text'
```

Plain text format.

## DSM

```
DSM(
    *packages: str,
    build_tree: bool = True,
    build_dependencies: bool = True,
    enforce_init: bool = True,
)
```

Bases: `RootNode`, `NodeMixin`, `PrintMixin`

DSM-capable class.

Technically speaking, a DSM instance is not a real DSM but more a tree representing the Python packages structure. However, it has the necessary methods to build a real DSM in the form of a square matrix, a dictionary or a tree-map.

Parameters:

- **`*packages`** (`str`, default: `()` ) – List of packages to search for.
- **`build_tree`** (`bool`, default: `True` ) – Auto-build the tree or not.
- **`build_dependencies`** (`bool`, default: `True` ) – Auto-build the dependencies or not.
- **`enforce_init`** (`bool`, default: `True` ) – If True, only treat directories if they contain an __init__.py file.

Methods:

- **`__bool__`** – Node as Boolean.
- **`__contains__`** – Get result of \_contains, cache it and return it.
- **`__getitem__`** – Return the corresponding Package or Module object.
- **`as_dict`** – Return the dependencies as a dictionary.
- **`as_graph`** – Create a graph with self as node, cache it, return it.
- **`as_matrix`** – Create a matrix with self as node, cache it, return it.
- **`as_treemap`** – Return the dependencies as a TreeMap.
- **`build_dependencies`** – Recursively build the dependencies for sub-modules and sub-packages.
- **`build_tree`** – Build the Python packages tree.
- **`get`** – Get item through __getitem__ and cache the result.
- **`get_target`** – Get the result of \_get_target, cache it and return it.
- **`print`** – Print the object in a file or on standard output by default.
- **`print_graph`** – Print the graph for self's nodes.
- **`print_matrix`** – Print the matrix for self's nodes.
- **`print_treemap`** – Print the matrix for self's nodes.

Attributes:

- **`base_packages`** (`tuple[str, ...]`) – Packages initially specified.
- **`empty`** (`bool`) – Whether the node has neither modules nor packages.
- **`enforce_init`** (`bool`) – Whether to enforce the presence of __init__.py files.
- **`finder`** (`Finder`) – Finder instance for locating packages and modules.
- **`isdsm`** (`bool`) – Inherited from NodeMixin. Always True.
- **`ismodule`** (`bool`) – Property to check if object is instance of Module.
- **`ispackage`** (`bool`) – Property to check if object is instance of Package.
- **`modules`** (`list[Module]`) – List of modules contained in the node.
- **`not_found`** (`list[str]`) – List of packages that were not found.
- **`packages`** (`list[Package]`) – List of packages contained in the node.
- **`specs`** (`list[PackageSpec]`) – List of package specifications found.
- **`submodules`** (`list[Module]`) – Property to return all sub-modules of the node, recursively.

Source code in `src/dependenpy/_internal/dsm.py`

```
def __init__(
    self,
    *packages: str,
    build_tree: bool = True,
    build_dependencies: bool = True,
    enforce_init: bool = True,
):
    """Initialization method.

    Parameters:
        *packages: List of packages to search for.
        build_tree: Auto-build the tree or not.
        build_dependencies: Auto-build the dependencies or not.
        enforce_init: If True, only treat directories if they contain an `__init__.py` file.
    """
    self.base_packages: tuple[str, ...] = packages
    """Packages initially specified."""
    self.finder: Finder = Finder()
    """Finder instance for locating packages and modules."""
    self.specs: list[PackageSpec] = []
    """List of package specifications found."""
    self.not_found: list[str] = []
    """List of packages that were not found."""
    self.enforce_init: bool = enforce_init
    """Whether to enforce the presence of `__init__.py` files."""

    specs = []
    for package in packages:
        spec = self.finder.find(package, enforce_init=enforce_init)
        if spec:
            specs.append(spec)
        else:
            self.not_found.append(package)

    if not specs:
        print("** dependenpy: DSM empty.", file=sys.stderr)  # noqa: T201

    self.specs = PackageSpec.combine(specs)

    for module in self.not_found:
        print(f"** dependenpy: Not found: {module}.", file=sys.stderr)  # noqa: T201

    super().__init__(build_tree)

    if build_tree and build_dependencies:
        self.build_dependencies()
```

### base_packages

```
base_packages: tuple[str, ...] = packages
```

Packages initially specified.

### empty

```
empty: bool
```

Whether the node has neither modules nor packages.

Returns:

- `bool` – True if empty, False otherwise.

### enforce_init

```
enforce_init: bool = enforce_init
```

Whether to enforce the presence of `__init__.py` files.

### finder

```
finder: Finder = Finder()
```

Finder instance for locating packages and modules.

### isdsm

```
isdsm: bool
```

Inherited from NodeMixin. Always True.

Returns:

- `bool` – Whether this object is a DSM.

### ismodule

```
ismodule: bool
```

Property to check if object is instance of Module.

Returns:

- `bool` – Whether this object is a module.

### ispackage

```
ispackage: bool
```

Property to check if object is instance of Package.

Returns:

- `bool` – Whether this object is a package.

### modules

```
modules: list[Module] = []
```

List of modules contained in the node.

### not_found

```
not_found: list[str] = []
```

List of packages that were not found.

### packages

```
packages: list[Package] = []
```

List of packages contained in the node.

### specs

```
specs: list[PackageSpec] = combine(specs)
```

List of package specifications found.

### submodules

```
submodules: list[Module]
```

Property to return all sub-modules of the node, recursively.

Returns:

- `list[Module]` – The sub-modules.

### __bool__

```
__bool__() -> bool
```

Node as Boolean.

Returns:

- `bool` – Result of node.empty.

Source code in `src/dependenpy/_internal/node.py`

```
def __bool__(self) -> bool:
    """Node as Boolean.

    Returns:
        Result of node.empty.
    """
    return bool(self.modules or self.packages)
```

### __contains__

```
__contains__(item: Package | Module) -> bool
```

Get result of \_contains, cache it and return it.

Parameters:

- **`item`** (`Package | Module`) – A package or module.

Returns:

- `bool` – True if self contains item, False otherwise.

Source code in `src/dependenpy/_internal/node.py`

```
def __contains__(self, item: Package | Module) -> bool:
    """Get result of _contains, cache it and return it.

    Parameters:
        item: A package or module.

    Returns:
        True if self contains item, False otherwise.
    """
    if item not in self._contains_cache:
        self._contains_cache[item] = self._contains(item)
    return self._contains_cache[item]
```

### __getitem__

```
__getitem__(item: str) -> Package | Module
```

Return the corresponding Package or Module object.

Parameters:

- **`item`** (`str`) – Name of the package/module, dot-separated.

Raises:

- `KeyError` – When the package or module cannot be found.

Returns:

- `Package | Module` – The corresponding object.

Source code in `src/dependenpy/_internal/node.py`

```
def __getitem__(self, item: str) -> Package | Module:
    """Return the corresponding Package or Module object.

    Parameters:
        item: Name of the package/module, dot-separated.

    Raises:
        KeyError: When the package or module cannot be found.

    Returns:
        The corresponding object.
    """
    depth = item.count(".") + 1
    parts = item.split(".", 1)
    for module in self.modules:
        if parts[0] == module.name and depth == 1:
            return module
    for package in self.packages:
        if parts[0] == package.name:
            if depth == 1:
                return package
            obj = package.get(parts[1])
            if obj:
                return obj
    raise KeyError(item)
```

### as_dict

```
as_dict() -> dict
```

Return the dependencies as a dictionary.

Returns:

- `dict` – Dictionary of dependencies.

Source code in `src/dependenpy/_internal/node.py`

```
def as_dict(self) -> dict:
    """Return the dependencies as a dictionary.

    Returns:
        Dictionary of dependencies.
    """
    return {
        "name": str(self),
        "modules": [module.as_dict() for module in self.modules],
        "packages": [package.as_dict() for package in self.packages],
    }
```

### as_graph

```
as_graph(depth: int = 0) -> Graph
```

Create a graph with self as node, cache it, return it.

Parameters:

- **`depth`** (`int`, default: `0` ) – Depth of the graph.

Returns:

- `Graph` – An instance of Graph.

Source code in `src/dependenpy/_internal/node.py`

```
def as_graph(self, depth: int = 0) -> Graph:
    """Create a graph with self as node, cache it, return it.

    Parameters:
        depth: Depth of the graph.

    Returns:
        An instance of Graph.
    """
    if depth not in self._graph_cache:
        self._graph_cache[depth] = Graph(self, depth=depth)  # type: ignore[arg-type]
    return self._graph_cache[depth]
```

### as_matrix

```
as_matrix(depth: int = 0) -> Matrix
```

Create a matrix with self as node, cache it, return it.

Parameters:

- **`depth`** (`int`, default: `0` ) – Depth of the matrix.

Returns:

- `Matrix` – An instance of Matrix.

Source code in `src/dependenpy/_internal/node.py`

```
def as_matrix(self, depth: int = 0) -> Matrix:
    """Create a matrix with self as node, cache it, return it.

    Parameters:
        depth: Depth of the matrix.

    Returns:
        An instance of Matrix.
    """
    if depth not in self._matrix_cache:
        self._matrix_cache[depth] = Matrix(self, depth=depth)  # type: ignore[arg-type]
    return self._matrix_cache[depth]
```

### as_treemap

```
as_treemap() -> TreeMap
```

Return the dependencies as a TreeMap.

Returns:

- `TreeMap` – An instance of TreeMap.

Source code in `src/dependenpy/_internal/node.py`

```
def as_treemap(self) -> TreeMap:
    """Return the dependencies as a TreeMap.

    Returns:
        An instance of TreeMap.
    """
    if not self._treemap_cache:
        self._treemap_cache = TreeMap(self)
    return self._treemap_cache
```

### build_dependencies

```
build_dependencies() -> None
```

Recursively build the dependencies for sub-modules and sub-packages.

Iterate on node's modules then packages and call their build_dependencies methods.

Source code in `src/dependenpy/_internal/node.py`

```
def build_dependencies(self) -> None:
    """Recursively build the dependencies for sub-modules and sub-packages.

    Iterate on node's modules then packages and call their
    build_dependencies methods.
    """
    for module in self.modules:
        module.build_dependencies()
    for package in self.packages:
        package.build_dependencies()
```

### build_tree

```
build_tree() -> None
```

Build the Python packages tree.

Source code in `src/dependenpy/_internal/dsm.py`

```
def build_tree(self) -> None:
    """Build the Python packages tree."""
    for spec in self.specs:
        if spec.ismodule:
            self.modules.append(Module(spec.name, spec.path, dsm=self))
        else:
            self.packages.append(
                Package(
                    spec.name,
                    spec.path,
                    dsm=self,
                    limit_to=spec.limit_to,
                    build_tree=True,
                    build_dependencies=False,
                    enforce_init=self.enforce_init,
                ),
            )
```

### get

```
get(item: str) -> Package | Module
```

Get item through `__getitem__` and cache the result.

Parameters:

- **`item`** (`str`) – Name of package or module.

Returns:

- `Package | Module` – The corresponding object.

Source code in `src/dependenpy/_internal/node.py`

```
def get(self, item: str) -> Package | Module:
    """Get item through `__getitem__` and cache the result.

    Parameters:
        item: Name of package or module.

    Returns:
        The corresponding object.
    """
    if item not in self._item_cache:
        try:
            obj = self.__getitem__(item)
        except KeyError:
            obj = None
        self._item_cache[item] = obj
    return self._item_cache[item]
```

### get_target

```
get_target(target: str) -> Package | Module
```

Get the result of \_get_target, cache it and return it.

Parameters:

- **`target`** (`str`) – Target to find.

Returns:

- `Package | Module` – Package containing target or corresponding module.

Source code in `src/dependenpy/_internal/node.py`

```
def get_target(self, target: str) -> Package | Module:
    """Get the result of _get_target, cache it and return it.

    Parameters:
        target: Target to find.

    Returns:
        Package containing target or corresponding module.
    """
    if target not in self._target_cache:
        self._target_cache[target] = self._get_target(target)
    return self._target_cache[target]
```

### print

```
print(
    format: str | None = TEXT,
    output: IO = stdout,
    **kwargs: Any,
) -> None
```

Print the object in a file or on standard output by default.

Parameters:

- **`format`** (`str | None`, default: `TEXT` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – Descriptor to an opened file (default to standard output).
- **`**kwargs`** (`Any`, default: `{}` ) – Additional arguments.

Source code in `src/dependenpy/_internal/helpers.py`

```
def print(self, format: str | None = TEXT, output: IO = sys.stdout, **kwargs: Any) -> None:  # noqa: A002
    """Print the object in a file or on standard output by default.

    Parameters:
        format: Output format (csv, json or text).
        output: Descriptor to an opened file (default to standard output).
        **kwargs: Additional arguments.
    """
    if format is None:
        format = TEXT

    if format != TEXT:
        kwargs.pop("zero", "")

    if format == TEXT:
        print(self._to_text(**kwargs), file=output)
    elif format == CSV:
        print(self._to_csv(**kwargs), file=output)
    elif format == JSON:
        print(self._to_json(**kwargs), file=output)
```

### print_graph

```
print_graph(
    format: str | None = None,
    output: IO = stdout,
    depth: int = 0,
    **kwargs: Any,
) -> None
```

Print the graph for self's nodes.

Parameters:

- **`format`** (`str | None`, default: `None` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – File descriptor on which to write.
- **`depth`** (`int`, default: `0` ) – Depth of the graph.
- **`**kwargs`** (`Any`, default: `{}` ) – Additional keyword arguments passed to graph.print.

Source code in `src/dependenpy/_internal/node.py`

```
def print_graph(
    self,
    format: str | None = None,  # noqa: A002
    output: IO = sys.stdout,
    depth: int = 0,
    **kwargs: Any,
) -> None:
    """Print the graph for self's nodes.

    Parameters:
        format: Output format (csv, json or text).
        output: File descriptor on which to write.
        depth: Depth of the graph.
        **kwargs: Additional keyword arguments passed to `graph.print`.
    """
    graph = self.as_graph(depth=depth)
    graph.print(format=format, output=output, **kwargs)
```

### print_matrix

```
print_matrix(
    format: str | None = None,
    output: IO = stdout,
    depth: int = 0,
    **kwargs: Any,
) -> None
```

Print the matrix for self's nodes.

Parameters:

- **`format`** (`str | None`, default: `None` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – File descriptor on which to write.
- **`depth`** (`int`, default: `0` ) – Depth of the matrix.
- **`**kwargs`** (`Any`, default: `{}` ) – Additional keyword arguments passed to matrix.print.

Source code in `src/dependenpy/_internal/node.py`

```
def print_matrix(
    self,
    format: str | None = None,  # noqa: A002
    output: IO = sys.stdout,
    depth: int = 0,
    **kwargs: Any,
) -> None:
    """Print the matrix for self's nodes.

    Parameters:
        format: Output format (csv, json or text).
        output: File descriptor on which to write.
        depth: Depth of the matrix.
        **kwargs: Additional keyword arguments passed to `matrix.print`.
    """
    matrix = self.as_matrix(depth=depth)
    matrix.print(format=format, output=output, **kwargs)
```

### print_treemap

```
print_treemap(
    format: str | None = None,
    output: IO = stdout,
    **kwargs: Any,
) -> None
```

Print the matrix for self's nodes.

Parameters:

- **`format`** (`str | None`, default: `None` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – File descriptor on which to write.
- **`**kwargs`** (`Any`, default: `{}` ) – Additional keyword arguments passed to treemap.print.

Source code in `src/dependenpy/_internal/node.py`

```
def print_treemap(self, format: str | None = None, output: IO = sys.stdout, **kwargs: Any) -> None:  # noqa: A002
    """Print the matrix for self's nodes.

    Parameters:
        format: Output format (csv, json or text).
        output: File descriptor on which to write.
        **kwargs: Additional keyword arguments passed to `treemap.print`.
    """
    treemap = self.as_treemap()
    treemap.print(format=format, output=output, **kwargs)
```

## Dependency

```
Dependency(
    source: Module,
    lineno: int,
    target: str | Module | Package,
    what: str | None = None,
)
```

Dependency class.

Represent a dependency from a module to another.

Parameters:

- **`source`** (`Module`) – Source Module.
- **`lineno`** (`int`) – Number of line at which import statement occurs.
- **`target`** (`str | Module | Package`) – The target node.
- **`what`** (`str | None`, default: `None` ) – What is imported (optional).

Attributes:

- **`external`** (`bool`) – Property to tell if the dependency's target is a valid node.
- **`lineno`** – Line number of the import statement.
- **`source`** – Source module.
- **`target`** – Target module or package.
- **`what`** – What is imported (optional).

Source code in `src/dependenpy/_internal/dsm.py`

```
def __init__(self, source: Module, lineno: int, target: str | Module | Package, what: str | None = None) -> None:
    """Initialization method.

    Parameters:
        source: Source Module.
        lineno: Number of line at which import statement occurs.
        target: The target node.
        what: What is imported (optional).
    """
    self.source = source
    """Source module."""
    self.lineno = lineno
    """Line number of the import statement."""
    self.target = target
    """Target module or package."""
    self.what = what
    """What is imported (optional)."""
```

### external

```
external: bool
```

Property to tell if the dependency's target is a valid node.

Returns:

- `bool` – Whether the dependency's target is a valid node.

### lineno

```
lineno = lineno
```

Line number of the import statement.

### source

```
source = source
```

Source module.

### target

```
target = target
```

Target module or package.

### what

```
what = what
```

What is imported (optional).

## Edge

```
Edge(
    vertex_out: Vertex, vertex_in: Vertex, weight: int = 1
)
```

Edge class. Used in Graph class.

Parameters:

- **`vertex_out`** (`Vertex`) – source vertex (edge going out).
- **`vertex_in`** (`Vertex`) – target vertex (edge going in).
- **`weight`** (`int`, default: `1` ) – weight of the edge.

Methods:

- **`go_from`** – Tell the edge to go out from this vertex.
- **`go_in`** – Tell the edge to go into this vertex.

Attributes:

- **`vertex_in`** (`Vertex | None`) – Incoming vertex.
- **`vertex_out`** (`Vertex | None`) – Outgoing vertex.
- **`weight`** – Weight of the edge.

Source code in `src/dependenpy/_internal/structures.py`

```
def __init__(self, vertex_out: Vertex, vertex_in: Vertex, weight: int = 1) -> None:
    """Initialization method.

    Parameters:
        vertex_out (Vertex): source vertex (edge going out).
        vertex_in (Vertex): target vertex (edge going in).
        weight (int): weight of the edge.
    """
    self.vertex_out: Vertex | None = None
    """Outgoing vertex."""
    self.vertex_in: Vertex | None = None
    """Incoming vertex."""
    self.weight = weight
    """Weight of the edge."""
    self.go_from(vertex_out)
    self.go_in(vertex_in)
```

### vertex_in

```
vertex_in: Vertex | None = None
```

Incoming vertex.

### vertex_out

```
vertex_out: Vertex | None = None
```

Outgoing vertex.

### weight

```
weight = weight
```

Weight of the edge.

### go_from

```
go_from(vertex: Vertex) -> None
```

Tell the edge to go out from this vertex.

Parameters:

- **`vertex`** (`Vertex`) – vertex to go from.

Source code in `src/dependenpy/_internal/structures.py`

```
def go_from(self, vertex: Vertex) -> None:
    """Tell the edge to go out from this vertex.

    Parameters:
        vertex (Vertex): vertex to go from.
    """
    if self.vertex_out:
        self.vertex_out.edges_out.remove(self)
    self.vertex_out = vertex
    vertex.edges_out.add(self)
```

### go_in

```
go_in(vertex: Vertex) -> None
```

Tell the edge to go into this vertex.

Parameters:

- **`vertex`** (`Vertex`) – vertex to go into.

Source code in `src/dependenpy/_internal/structures.py`

```
def go_in(self, vertex: Vertex) -> None:
    """Tell the edge to go into this vertex.

    Parameters:
        vertex (Vertex): vertex to go into.
    """
    if self.vertex_in:
        self.vertex_in.edges_in.remove(self)
    self.vertex_in = vertex
    vertex.edges_in.add(self)
```

## Finder

```
Finder(finders: list[type] | None = None)
```

Main package finder class.

Initialize it with a list of package finder classes (not instances).

Parameters:

- **`finders`** (`list[type] | None`, default: `None` ) – list of package finder classes (not instances) in a specific order. Default: [LocalPackageFinder, InstalledPackageFinder].

Methods:

- **`find`** – Find a package using package finders.

Attributes:

- **`finders`** (`list[PackageFinder]`) – Selected finders.

Source code in `src/dependenpy/_internal/finder.py`

```
def __init__(self, finders: list[type] | None = None):
    """Initialization method.

    Parameters:
        finders: list of package finder classes (not instances) in a specific
            order. Default: [LocalPackageFinder, InstalledPackageFinder].
    """
    self.finders: list[PackageFinder]
    """Selected finders."""
    if finders is None:
        finder_instances = [LocalPackageFinder(), InstalledPackageFinder()]
    else:
        finder_instances = [finder() for finder in finders]
    self.finders = finder_instances
```

### finders

```
finders: list[PackageFinder] = finder_instances
```

Selected finders.

### find

```
find(package: str, **kwargs: Any) -> PackageSpec | None
```

Find a package using package finders.

Return the first package found.

Parameters:

- **`package`** (`str`) – package to find.
- **`**kwargs`** (`Any`, default: `{}` ) – additional keyword arguments used by finders.

Returns:

- `PackageSpec | None` – Package spec or None.

Source code in `src/dependenpy/_internal/finder.py`

```
def find(self, package: str, **kwargs: Any) -> PackageSpec | None:
    """Find a package using package finders.

    Return the first package found.

    Parameters:
        package: package to find.
        **kwargs: additional keyword arguments used by finders.

    Returns:
        Package spec or None.
    """
    for finder in self.finders:
        package_spec = finder.find(package, **kwargs)
        if package_spec:
            return package_spec
    return None
```

## Graph

```
Graph(*nodes: DSM | Package | Module, depth: int = 0)
```

Bases: `PrintMixin`

Graph class.

A class to build a graph given a list of nodes. After instantiation, it has two attributes: vertices, the set of nodes, and edges, the set of edges.

An intermediary matrix is built to ease the creation of the graph.

Parameters:

- **`*nodes`** (`list of DSM/Package/Module`, default: `()` ) – the nodes on which to build the graph.
- **`depth`** (`int`, default: `0` ) – the depth of the intermediary matrix. See the documentation for Matrix class.

Methods:

- **`print`** – Print the object in a file or on standard output by default.

Attributes:

- **`edges`** – Set of edges in the graph.
- **`vertices`** – Set of vertices in the graph.

Source code in `src/dependenpy/_internal/structures.py`

```
def __init__(self, *nodes: DSM | Package | Module, depth: int = 0) -> None:
    """Initialization method.

    An intermediary matrix is built to ease the creation of the graph.

    Parameters:
        *nodes (list of DSM/Package/Module):
            the nodes on which to build the graph.
        depth (int): the depth of the intermediary matrix. See
            the documentation for Matrix class.
    """
    self.edges = set()
    """Set of edges in the graph."""
    vertices = []
    matrix = Matrix(*nodes, depth=depth)
    for key in matrix.keys:
        vertices.append(Vertex(key))
    for line_index, line in enumerate(matrix.data):
        for col_index, cell in enumerate(line):
            if cell > 0:
                self.edges.add(Edge(vertices[line_index], vertices[col_index], weight=cell))
    self.vertices = set(vertices)
    """Set of vertices in the graph."""
```

### edges

```
edges = set()
```

Set of edges in the graph.

### vertices

```
vertices = set(vertices)
```

Set of vertices in the graph.

### print

```
print(
    format: str | None = TEXT,
    output: IO = stdout,
    **kwargs: Any,
) -> None
```

Print the object in a file or on standard output by default.

Parameters:

- **`format`** (`str | None`, default: `TEXT` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – Descriptor to an opened file (default to standard output).
- **`**kwargs`** (`Any`, default: `{}` ) – Additional arguments.

Source code in `src/dependenpy/_internal/helpers.py`

```
def print(self, format: str | None = TEXT, output: IO = sys.stdout, **kwargs: Any) -> None:  # noqa: A002
    """Print the object in a file or on standard output by default.

    Parameters:
        format: Output format (csv, json or text).
        output: Descriptor to an opened file (default to standard output).
        **kwargs: Additional arguments.
    """
    if format is None:
        format = TEXT

    if format != TEXT:
        kwargs.pop("zero", "")

    if format == TEXT:
        print(self._to_text(**kwargs), file=output)
    elif format == CSV:
        print(self._to_csv(**kwargs), file=output)
    elif format == JSON:
        print(self._to_json(**kwargs), file=output)
```

## InstalledPackageFinder

Bases: `PackageFinder`

Finder to find installed Python packages using importlib.

Methods:

- **`find`** – Find method.

### find

```
find(package: str, **kwargs: Any) -> PackageSpec | None
```

Find method.

Parameters:

- **`package`** (`str`) – package to find.
- **`**kwargs`** (`Any`, default: `{}` ) – additional keyword arguments.

Returns:

- `PackageSpec | None` – Package spec or None.

Source code in `src/dependenpy/_internal/finder.py`

```
def find(self, package: str, **kwargs: Any) -> PackageSpec | None:  # noqa: ARG002
    """Find method.

    Parameters:
        package: package to find.
        **kwargs: additional keyword arguments.

    Returns:
        Package spec or None.
    """
    spec = find_spec(package)
    if spec is None:
        return None
    if "." in package:
        package, rest = package.split(".", 1)
        limit = [rest]
        spec = find_spec(package)
    else:
        limit = []
    if spec is not None:
        if spec.submodule_search_locations:
            path = spec.submodule_search_locations[0]
        elif spec.origin and spec.origin != "built-in":
            path = spec.origin
        else:
            return None
        return PackageSpec(spec.name, path, limit)
    return None
```

## InternalDependencies

Bases: `Provider`

Dependenpy provider for Archan.

Methods:

- **`get_data`** – Provide matrix data for internal dependencies in a set of packages.

Attributes:

- **`argument_list`** – List of arguments for the provider.
- **`description`** – Description of the provider.
- **`identifier`** – Identifier of the provider.
- **`name`** – Name of the provider.

### argument_list

```
argument_list = (
    Argument(
        "packages",
        list,
        "The list of packages to check for.",
    ),
    Argument(
        "enforce_init",
        bool,
        default=True,
        description="Whether to assert presence of __init__.py files in directories.",
    ),
    Argument(
        "depth", int, "The depth of the matrix to generate."
    ),
)
```

List of arguments for the provider.

### description

```
description = "Provide matrix data about internal dependencies in a set of packages."
```

Description of the provider.

### identifier

```
identifier = 'dependenpy.InternalDependencies'
```

Identifier of the provider.

### name

```
name = 'Internal Dependencies'
```

Name of the provider.

### get_data

```
get_data(
    packages: list[str],
    enforce_init: bool = True,
    depth: int | None = None,
) -> DSM
```

Provide matrix data for internal dependencies in a set of packages.

Parameters:

- **`packages`** (`list[str]`) – The list of packages to check for.
- **`enforce_init`** (`bool`, default: `True` ) – Whether to assert presence of init.py files in directories.
- **`depth`** (`int | None`, default: `None` ) – The depth of the matrix to generate.

Returns:

- `DSM` – Instance of archan DSM.

Source code in `src/dependenpy/_internal/plugins.py`

```
def get_data(
    self,
    packages: list[str],
    enforce_init: bool = True,  # noqa: FBT001,FBT002
    depth: int | None = None,
) -> archan.DSM:
    """Provide matrix data for internal dependencies in a set of packages.

    Parameters:
        packages: The list of packages to check for.
        enforce_init: Whether to assert presence of __init__.py files in directories.
        depth: The depth of the matrix to generate.

    Returns:
        Instance of archan DSM.
    """
    dsm = DependenpyDSM(*packages, enforce_init=enforce_init)
    if depth is None:
        depth = guess_depth(packages)
    matrix = dsm.as_matrix(depth=depth)
    return archan.DesignStructureMatrix(data=matrix.data, entities=matrix.keys)
```

## LeafNode

```
LeafNode()
```

Shared code between Package and Module.

Methods:

- **`absolute_name`** – Return the absolute name of the node.

Attributes:

- **`depth`** (`int`) – Property to tell the depth of the node in the tree.
- **`root`** (`Package`) – Property to return the root of this node.

Source code in `src/dependenpy/_internal/node.py`

```
def __init__(self):
    """Initialization method."""
    self._depth_cache = None
```

### depth

```
depth: int
```

Property to tell the depth of the node in the tree.

Returns:

- `int` – The node's depth in the tree.

### root

```
root: Package
```

Property to return the root of this node.

Returns:

- **`Package`** ( `Package` ) – this node's root package.

### absolute_name

```
absolute_name(depth: int = 0) -> str
```

Return the absolute name of the node.

Concatenate names from root to self within depth.

Parameters:

- **`depth`** (`int`, default: `0` ) – Maximum depth to go to.

Returns:

- `str` – Absolute name of the node (until given depth is reached).

Source code in `src/dependenpy/_internal/node.py`

```
def absolute_name(self, depth: int = 0) -> str:
    """Return the absolute name of the node.

    Concatenate names from root to self within depth.

    Parameters:
        depth: Maximum depth to go to.

    Returns:
        Absolute name of the node (until given depth is reached).
    """
    node: Package
    node, node_depth = self, self.depth  # type: ignore[assignment]
    if depth < 1:
        depth = node_depth
    while node_depth > depth and node.package is not None:
        node = node.package
        node_depth -= 1
    names = []
    while node is not None:
        names.append(node.name)
        node = node.package  # type: ignore[assignment]
    return ".".join(reversed(names))
```

## LocalPackageFinder

Bases: `PackageFinder`

Finder to find local packages (directories on the disk).

Methods:

- **`find`** – Find method.

### find

```
find(package: str, **kwargs: Any) -> PackageSpec | None
```

Find method.

Parameters:

- **`package`** (`str`) – Package to find.
- **`**kwargs`** (`Any`, default: `{}` ) – Additional keyword arguments.

Returns:

- `PackageSpec | None` – Package spec or None.

Source code in `src/dependenpy/_internal/finder.py`

```
def find(self, package: str, **kwargs: Any) -> PackageSpec | None:
    """Find method.

    Parameters:
        package: Package to find.
        **kwargs: Additional keyword arguments.

    Returns:
        Package spec or None.
    """
    if not exists(package):
        return None
    name, path = None, None
    enforce_init = kwargs.pop("enforce_init", True)
    if isdir(package):
        if isfile(join(package, "__init__.py")) or not enforce_init:
            name, path = basename(package), package
    elif isfile(package) and package.endswith(".py"):
        name, path = splitext(basename(package))[0], package
    if name and path:
        return PackageSpec(name, path)
    return None
```

## Matrix

```
Matrix(*nodes: DSM | Package | Module, depth: int = 0)
```

Bases: `PrintMixin`

Matrix class.

A class to build a matrix given a list of nodes. After instantiation, it has two attributes: data, a 2-dimensions array, and keys, the names of the entities in the corresponding order.

Parameters:

- **`*nodes`** (`DSM | Package | Module`, default: `()` ) – The nodes on which to build the matrix.
- **`depth`** (`int`, default: `0` ) – The depth of the matrix. This depth is always absolute, meaning that building a matrix with a sub-package "A.B.C" and a depth of 1 will return a matrix of size 1, containing A only. To see the matrix for the sub-modules and sub-packages in C, you will have to give depth=4.

Methods:

- **`cast`** – Cast a set of keys and an array to a Matrix object.
- **`print`** – Print the object in a file or on standard output by default.

Attributes:

- **`data`** – The data of the matrix.
- **`keys`** – The keys of the matrix.
- **`size`** – The size of the matrix.
- **`total`** (`int`) – Return the total number of dependencies within this matrix.

Source code in `src/dependenpy/_internal/structures.py`

```
def __init__(self, *nodes: DSM | Package | Module, depth: int = 0):
    """Initialization method.

    Parameters:
        *nodes: The nodes on which to build the matrix.
        depth: The depth of the matrix. This depth is always
            absolute, meaning that building a matrix with a sub-package
            "A.B.C" and a depth of 1 will return a matrix of size 1,
            containing A only. To see the matrix for the sub-modules and
            sub-packages in C, you will have to give depth=4.
    """
    modules: list[Module] = []
    for node in nodes:
        if node.ismodule:
            modules.append(node)  # type: ignore[arg-type]
        elif node.ispackage or node.isdsm:
            modules.extend(node.submodules)  # type: ignore[union-attr]

    if depth < 1:
        keys = modules
    else:
        keys = []
        for module in modules:
            if module.depth <= depth:
                keys.append(module)
                continue
            package = module.package
            while package.depth > depth and package.package and package not in nodes:  # type: ignore[union-attr]
                package = package.package  # type: ignore[union-attr]
            if package not in keys:
                keys.append(package)  # type: ignore[arg-type]

    size = len(keys)
    data = [[0] * size for _ in range(size)]
    keys = sorted(keys, key=lambda key: key.absolute_name())

    if depth < 1:
        for index, key in enumerate(keys):
            key.index = index  # type: ignore[attr-defined]
        for index, key in enumerate(keys):
            for dep in key.dependencies:
                if dep.external:
                    continue
                if dep.target.ismodule and dep.target in keys:  # type: ignore[union-attr]
                    data[index][dep.target.index] += 1  # type: ignore[index,union-attr]
                elif dep.target.ispackage:  # type: ignore[union-attr]
                    init = dep.target.get("__init__")  # type: ignore[union-attr]
                    if init is not None and init in keys:
                        data[index][init.index] += 1  # type: ignore[union-attr]
    else:
        for row, row_key in enumerate(keys):
            for col, col_key in enumerate(keys):
                data[row][col] = row_key.cardinal(to=col_key)

    self.size = size
    """The size of the matrix."""
    self.keys = [key.absolute_name() for key in keys]
    """The keys of the matrix."""
    self.data = data
    """The data of the matrix."""
```

### data

```
data = data
```

The data of the matrix.

### keys

```
keys = [(absolute_name()) for key in keys]
```

The keys of the matrix.

### size

```
size = size
```

The size of the matrix.

### total

```
total: int
```

Return the total number of dependencies within this matrix.

Returns:

- `int` – The total number of dependencies.

### cast

```
cast(keys: list[str], data: list[list[int]]) -> Matrix
```

Cast a set of keys and an array to a Matrix object.

Parameters:

- **`keys`** (`list[str]`) – The matrix keys.
- **`data`** (`list[list[int]]`) – The matrix data.

Returns:

- `Matrix` – A new matrix.

Source code in `src/dependenpy/_internal/structures.py`

```
@staticmethod
def cast(keys: list[str], data: list[list[int]]) -> Matrix:
    """Cast a set of keys and an array to a Matrix object.

    Arguments:
        keys: The matrix keys.
        data: The matrix data.

    Returns:
        A new matrix.
    """
    matrix = Matrix()
    matrix.keys = copy.deepcopy(keys)
    matrix.data = copy.deepcopy(data)
    return matrix
```

### print

```
print(
    format: str | None = TEXT,
    output: IO = stdout,
    **kwargs: Any,
) -> None
```

Print the object in a file or on standard output by default.

Parameters:

- **`format`** (`str | None`, default: `TEXT` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – Descriptor to an opened file (default to standard output).
- **`**kwargs`** (`Any`, default: `{}` ) – Additional arguments.

Source code in `src/dependenpy/_internal/helpers.py`

```
def print(self, format: str | None = TEXT, output: IO = sys.stdout, **kwargs: Any) -> None:  # noqa: A002
    """Print the object in a file or on standard output by default.

    Parameters:
        format: Output format (csv, json or text).
        output: Descriptor to an opened file (default to standard output).
        **kwargs: Additional arguments.
    """
    if format is None:
        format = TEXT

    if format != TEXT:
        kwargs.pop("zero", "")

    if format == TEXT:
        print(self._to_text(**kwargs), file=output)
    elif format == CSV:
        print(self._to_csv(**kwargs), file=output)
    elif format == JSON:
        print(self._to_json(**kwargs), file=output)
```

## Module

```
Module(
    name: str,
    path: str,
    dsm: DSM | None = None,
    package: Package | None = None,
)
```

Bases: `LeafNode`, `NodeMixin`, `PrintMixin`

Module class.

This class represents a Python module (a Python file).

Parameters:

- **`name`** (`str`) – Name of the module.
- **`path`** (`str`) – Path to the module.
- **`dsm`** (`DSM | None`, default: `None` ) – Parent DSM.
- **`package`** (`Package | None`, default: `None` ) – Parent Package.

Methods:

- **`__contains__`** – Whether given item is contained inside this module.
- **`absolute_name`** – Return the absolute name of the node.
- **`as_dict`** – Return the dependencies as a dictionary.
- **`build_dependencies`** – Build the dependencies for this module.
- **`cardinal`** – Return the number of dependencies of this module to the given node.
- **`get_imports`** – Return all the import statements given an AST body (AST nodes).
- **`parse_code`** – Read the source code and return all the import statements.
- **`print`** – Print the object in a file or on standard output by default.

Attributes:

- **`RECURSIVE_NODES`** – Nodes that can be recursive.
- **`dependencies`** (`list[Dependency]`) – List of dependencies.
- **`depth`** (`int`) – Property to tell the depth of the node in the tree.
- **`dsm`** – Parent DSM.
- **`isdsm`** (`bool`) – Property to check if object is instance of DSM.
- **`ismodule`** (`bool`) – Inherited from NodeMixin. Always True.
- **`ispackage`** (`bool`) – Property to check if object is instance of Package.
- **`name`** – Name of the module.
- **`package`** – Package to which the module belongs.
- **`path`** – Path to the module.
- **`root`** (`Package`) – Property to return the root of this node.

Source code in `src/dependenpy/_internal/dsm.py`

```
def __init__(self, name: str, path: str, dsm: DSM | None = None, package: Package | None = None) -> None:
    """Initialization method.

    Parameters:
        name: Name of the module.
        path: Path to the module.
        dsm: Parent DSM.
        package: Parent Package.
    """
    super().__init__()
    self.name = name
    """Name of the module."""
    self.path = path
    """Path to the module."""
    self.package = package
    """Package to which the module belongs."""
    self.dsm = dsm
    """Parent DSM."""
    self.dependencies: list[Dependency] = []
    """List of dependencies."""
```

### RECURSIVE_NODES

```
RECURSIVE_NODES = (
    ClassDef,
    FunctionDef,
    If,
    IfExp,
    Try,
    With,
    ExceptHandler,
)
```

Nodes that can be recursive.

### dependencies

```
dependencies: list[Dependency] = []
```

List of dependencies.

### depth

```
depth: int
```

Property to tell the depth of the node in the tree.

Returns:

- `int` – The node's depth in the tree.

### dsm

```
dsm = dsm
```

Parent DSM.

### isdsm

```
isdsm: bool
```

Property to check if object is instance of DSM.

Returns:

- `bool` – Whether this object is a DSM.

### ismodule

```
ismodule: bool
```

Inherited from NodeMixin. Always True.

Returns:

- `bool` – Whether this object is a module.

### ispackage

```
ispackage: bool
```

Property to check if object is instance of Package.

Returns:

- `bool` – Whether this object is a package.

### name

```
name = name
```

Name of the module.

### package

```
package = package
```

Package to which the module belongs.

### path

```
path = path
```

Path to the module.

### root

```
root: Package
```

Property to return the root of this node.

Returns:

- **`Package`** ( `Package` ) – this node's root package.

### __contains__

```
__contains__(item: Package | Module) -> bool
```

Whether given item is contained inside this module.

Parameters:

- **`item`** (`Package / Module`) – a package or module.

Returns:

- `bool` – True if self is item or item is self's package and self if an __init__ module.

Source code in `src/dependenpy/_internal/dsm.py`

```
def __contains__(self, item: Package | Module) -> bool:
    """Whether given item is contained inside this module.

    Parameters:
        item (Package/Module): a package or module.

    Returns:
        True if self is item or item is self's package and
            self if an `__init__` module.
    """
    if self is item:
        return True
    return self.package is item and self.name == "__init__"
```

### absolute_name

```
absolute_name(depth: int = 0) -> str
```

Return the absolute name of the node.

Concatenate names from root to self within depth.

Parameters:

- **`depth`** (`int`, default: `0` ) – Maximum depth to go to.

Returns:

- `str` – Absolute name of the node (until given depth is reached).

Source code in `src/dependenpy/_internal/node.py`

```
def absolute_name(self, depth: int = 0) -> str:
    """Return the absolute name of the node.

    Concatenate names from root to self within depth.

    Parameters:
        depth: Maximum depth to go to.

    Returns:
        Absolute name of the node (until given depth is reached).
    """
    node: Package
    node, node_depth = self, self.depth  # type: ignore[assignment]
    if depth < 1:
        depth = node_depth
    while node_depth > depth and node.package is not None:
        node = node.package
        node_depth -= 1
    names = []
    while node is not None:
        names.append(node.name)
        node = node.package  # type: ignore[assignment]
    return ".".join(reversed(names))
```

### as_dict

```
as_dict(absolute: bool = False) -> dict
```

Return the dependencies as a dictionary.

Parameters:

- **`absolute`** (`bool`, default: `False` ) – Whether to use the absolute name.

Returns:

- `dict` – Dictionary of dependencies.

Source code in `src/dependenpy/_internal/dsm.py`

```
def as_dict(self, absolute: bool = False) -> dict:  # noqa: FBT001,FBT002
    """Return the dependencies as a dictionary.

    Arguments:
        absolute: Whether to use the absolute name.

    Returns:
        Dictionary of dependencies.
    """
    return {
        "name": self.absolute_name() if absolute else self.name,
        "path": self.path,
        "dependencies": [
            {
                # 'source': d.source.absolute_name(),  # redundant
                "target": dep.target if dep.external else dep.target.absolute_name(),  # type: ignore[union-attr]
                "lineno": dep.lineno,
                "what": dep.what,
                "external": dep.external,
            }
            for dep in self.dependencies
        ],
    }
```

### build_dependencies

```
build_dependencies() -> None
```

Build the dependencies for this module.

Parse the code with ast, find all the import statements, convert them into Dependency objects.

Source code in `src/dependenpy/_internal/dsm.py`

```
def build_dependencies(self) -> None:
    """Build the dependencies for this module.

    Parse the code with ast, find all the import statements, convert
    them into Dependency objects.
    """
    highest = self.dsm or self.root
    for import_ in self.parse_code():
        target = highest.get_target(import_["target"])
        if target:
            what = import_["target"].split(".")[-1]
            if what != target.name:
                import_["what"] = what
            import_["target"] = target
        self.dependencies.append(Dependency(source=self, **import_))
```

### cardinal

```
cardinal(to: Package | Module) -> int
```

Return the number of dependencies of this module to the given node.

Parameters:

- **`to`** (`Package | Module`) – The target node.

Returns:

- `int` – Number of dependencies.

Source code in `src/dependenpy/_internal/dsm.py`

```
def cardinal(self, to: Package | Module) -> int:
    """Return the number of dependencies of this module to the given node.

    Parameters:
        to: The target node.

    Returns:
        Number of dependencies.
    """
    return len([dep for dep in self.dependencies if not dep.external and dep.target in to])  # type: ignore[operator]
```

### get_imports

```
get_imports(ast_body: Sequence[AST]) -> list[dict]
```

Return all the import statements given an AST body (AST nodes).

Returns:

- `list[dict]` – The import statements.

Source code in `src/dependenpy/_internal/dsm.py`

```
def get_imports(self, ast_body: Sequence[ast.AST]) -> list[dict]:
    """Return all the import statements given an AST body (AST nodes).

    Parameters:
        The body to filter.

    Returns:
        The import statements.
    """
    imports: list[dict] = []
    for node in ast_body:
        if isinstance(node, ast.Import):
            imports.extend({"target": name.name, "lineno": node.lineno} for name in node.names)
        elif isinstance(node, ast.ImportFrom):
            for name in node.names:
                abs_name = self.absolute_name(self.depth - node.level) + "." if node.level > 0 else ""
                node_module = node.module + "." if node.module else ""
                name = abs_name + node_module + name.name  # type: ignore[assignment]  # noqa: PLW2901
                imports.append({"target": name, "lineno": node.lineno})
        elif isinstance(node, Module.RECURSIVE_NODES):
            imports.extend(self.get_imports(node.body))  # type: ignore[arg-type]
            if isinstance(node, ast.Try):
                imports.extend(self.get_imports(node.finalbody))
    return imports
```

### parse_code

```
parse_code() -> list[dict]
```

Read the source code and return all the import statements.

Returns:

- `list[dict]` – The import statements.

Source code in `src/dependenpy/_internal/dsm.py`

```
def parse_code(self) -> list[dict]:
    """Read the source code and return all the import statements.

    Returns:
        The import statements.
    """
    code = Path(self.path).read_text(encoding="utf-8")
    try:
        body = ast.parse(code).body
    except SyntaxError:
        code = code.encode("utf-8")  # type: ignore[assignment]
        try:
            body = ast.parse(code).body
        except SyntaxError:
            return []
    return self.get_imports(body)
```

### print

```
print(
    format: str | None = TEXT,
    output: IO = stdout,
    **kwargs: Any,
) -> None
```

Print the object in a file or on standard output by default.

Parameters:

- **`format`** (`str | None`, default: `TEXT` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – Descriptor to an opened file (default to standard output).
- **`**kwargs`** (`Any`, default: `{}` ) – Additional arguments.

Source code in `src/dependenpy/_internal/helpers.py`

```
def print(self, format: str | None = TEXT, output: IO = sys.stdout, **kwargs: Any) -> None:  # noqa: A002
    """Print the object in a file or on standard output by default.

    Parameters:
        format: Output format (csv, json or text).
        output: Descriptor to an opened file (default to standard output).
        **kwargs: Additional arguments.
    """
    if format is None:
        format = TEXT

    if format != TEXT:
        kwargs.pop("zero", "")

    if format == TEXT:
        print(self._to_text(**kwargs), file=output)
    elif format == CSV:
        print(self._to_csv(**kwargs), file=output)
    elif format == JSON:
        print(self._to_json(**kwargs), file=output)
```

## NodeMixin

Shared code between DSM, Package and Module.

Attributes:

- **`isdsm`** (`bool`) – Property to check if object is instance of DSM.
- **`ismodule`** (`bool`) – Property to check if object is instance of Module.
- **`ispackage`** (`bool`) – Property to check if object is instance of Package.

### isdsm

```
isdsm: bool
```

Property to check if object is instance of DSM.

Returns:

- `bool` – Whether this object is a DSM.

### ismodule

```
ismodule: bool
```

Property to check if object is instance of Module.

Returns:

- `bool` – Whether this object is a module.

### ispackage

```
ispackage: bool
```

Property to check if object is instance of Package.

Returns:

- `bool` – Whether this object is a package.

## Package

```
Package(
    name: str,
    path: str,
    dsm: DSM | None = None,
    package: Package | None = None,
    limit_to: list[str] | None = None,
    build_tree: bool = True,
    build_dependencies: bool = True,
    enforce_init: bool = True,
)
```

Bases: `RootNode`, `LeafNode`, `NodeMixin`, `PrintMixin`

Package class.

This class represent Python packages as nodes in a tree.

Parameters:

- **`name`** (`str`) – Name of the package.
- **`path`** (`str`) – Path to the package.
- **`dsm`** (`DSM | None`, default: `None` ) – Parent DSM.
- **`package`** (`Package | None`, default: `None` ) – Parent package.
- **`limit_to`** (`list[str] | None`, default: `None` ) – List of string to limit the recursive tree-building to what is specified.
- **`build_tree`** (`bool`, default: `True` ) – Auto-build the tree or not.
- **`build_dependencies`** (`bool`, default: `True` ) – Auto-build the dependencies or not.
- **`enforce_init`** (`bool`, default: `True` ) – If True, only treat directories if they contain an __init__.py file.

Methods:

- **`__bool__`** – Node as Boolean.
- **`__contains__`** – Get result of \_contains, cache it and return it.
- **`__getitem__`** – Return the corresponding Package or Module object.
- **`absolute_name`** – Return the absolute name of the node.
- **`as_dict`** – Return the dependencies as a dictionary.
- **`as_graph`** – Create a graph with self as node, cache it, return it.
- **`as_matrix`** – Create a matrix with self as node, cache it, return it.
- **`as_treemap`** – Return the dependencies as a TreeMap.
- **`build_dependencies`** – Recursively build the dependencies for sub-modules and sub-packages.
- **`build_tree`** – Build the tree for this package.
- **`cardinal`** – Return the number of dependencies of this package to the given node.
- **`get`** – Get item through __getitem__ and cache the result.
- **`get_target`** – Get the result of \_get_target, cache it and return it.
- **`print`** – Print the object in a file or on standard output by default.
- **`print_graph`** – Print the graph for self's nodes.
- **`print_matrix`** – Print the matrix for self's nodes.
- **`print_treemap`** – Print the matrix for self's nodes.
- **`split_limits_heads`** – Return first parts of dot-separated strings, and rest of strings.

Attributes:

- **`depth`** (`int`) – Property to tell the depth of the node in the tree.
- **`dsm`** – Parent DSM.
- **`empty`** (`bool`) – Whether the node has neither modules nor packages.
- **`enforce_init`** – Whether to enforce the presence of __init__.py files.
- **`isdsm`** (`bool`) – Property to check if object is instance of DSM.
- **`ismodule`** (`bool`) – Property to check if object is instance of Module.
- **`ispackage`** (`bool`) – Inherited from NodeMixin. Always True.
- **`isroot`** (`bool`) – Property to tell if this node is a root node.
- **`issubpackage`** (`bool`) – Property to tell if this node is a sub-package.
- **`limit_to`** – List of strings to limit the recursive tree-building.
- **`modules`** (`list[Module]`) – List of modules contained in the node.
- **`name`** – Name of the package.
- **`package`** – Parent package.
- **`packages`** (`list[Package]`) – List of packages contained in the node.
- **`path`** – Path to the package.
- **`root`** (`Package`) – Property to return the root of this node.
- **`submodules`** (`list[Module]`) – Property to return all sub-modules of the node, recursively.

Source code in `src/dependenpy/_internal/dsm.py`

```
def __init__(
    self,
    name: str,
    path: str,
    dsm: DSM | None = None,
    package: Package | None = None,
    limit_to: list[str] | None = None,
    build_tree: bool = True,  # noqa: FBT001,FBT002
    build_dependencies: bool = True,  # noqa: FBT001,FBT002
    enforce_init: bool = True,  # noqa: FBT001,FBT002
):
    """Initialization method.

    Parameters:
        name: Name of the package.
        path: Path to the package.
        dsm: Parent DSM.
        package: Parent package.
        limit_to: List of string to limit the recursive tree-building to what is specified.
        build_tree: Auto-build the tree or not.
        build_dependencies: Auto-build the dependencies or not.
        enforce_init: If True, only treat directories if they contain an `__init__.py` file.
    """
    self.name = name
    """Name of the package."""
    self.path = path
    """Path to the package."""
    self.package = package
    """Parent package."""
    self.dsm = dsm
    """Parent DSM."""
    self.limit_to = limit_to or []
    """List of strings to limit the recursive tree-building."""
    self.enforce_init = enforce_init
    """Whether to enforce the presence of `__init__.py` files."""

    RootNode.__init__(self, build_tree)
    LeafNode.__init__(self)

    if build_tree and build_dependencies:
        self.build_dependencies()
```

### depth

```
depth: int
```

Property to tell the depth of the node in the tree.

Returns:

- `int` – The node's depth in the tree.

### dsm

```
dsm = dsm
```

Parent DSM.

### empty

```
empty: bool
```

Whether the node has neither modules nor packages.

Returns:

- `bool` – True if empty, False otherwise.

### enforce_init

```
enforce_init = enforce_init
```

Whether to enforce the presence of `__init__.py` files.

### isdsm

```
isdsm: bool
```

Property to check if object is instance of DSM.

Returns:

- `bool` – Whether this object is a DSM.

### ismodule

```
ismodule: bool
```

Property to check if object is instance of Module.

Returns:

- `bool` – Whether this object is a module.

### ispackage

```
ispackage: bool
```

Inherited from NodeMixin. Always True.

Returns:

- `bool` – Whether this object is a package.

### isroot

```
isroot: bool
```

Property to tell if this node is a root node.

Returns:

- `bool` – This package has no parent.

### issubpackage

```
issubpackage: bool
```

Property to tell if this node is a sub-package.

Returns:

- `bool` – This package has a parent.

### limit_to

```
limit_to = limit_to or []
```

List of strings to limit the recursive tree-building.

### modules

```
modules: list[Module] = []
```

List of modules contained in the node.

### name

```
name = name
```

Name of the package.

### package

```
package = package
```

Parent package.

### packages

```
packages: list[Package] = []
```

List of packages contained in the node.

### path

```
path = path
```

Path to the package.

### root

```
root: Package
```

Property to return the root of this node.

Returns:

- **`Package`** ( `Package` ) – this node's root package.

### submodules

```
submodules: list[Module]
```

Property to return all sub-modules of the node, recursively.

Returns:

- `list[Module]` – The sub-modules.

### __bool__

```
__bool__() -> bool
```

Node as Boolean.

Returns:

- `bool` – Result of node.empty.

Source code in `src/dependenpy/_internal/node.py`

```
def __bool__(self) -> bool:
    """Node as Boolean.

    Returns:
        Result of node.empty.
    """
    return bool(self.modules or self.packages)
```

### __contains__

```
__contains__(item: Package | Module) -> bool
```

Get result of \_contains, cache it and return it.

Parameters:

- **`item`** (`Package | Module`) – A package or module.

Returns:

- `bool` – True if self contains item, False otherwise.

Source code in `src/dependenpy/_internal/node.py`

```
def __contains__(self, item: Package | Module) -> bool:
    """Get result of _contains, cache it and return it.

    Parameters:
        item: A package or module.

    Returns:
        True if self contains item, False otherwise.
    """
    if item not in self._contains_cache:
        self._contains_cache[item] = self._contains(item)
    return self._contains_cache[item]
```

### __getitem__

```
__getitem__(item: str) -> Package | Module
```

Return the corresponding Package or Module object.

Parameters:

- **`item`** (`str`) – Name of the package/module, dot-separated.

Raises:

- `KeyError` – When the package or module cannot be found.

Returns:

- `Package | Module` – The corresponding object.

Source code in `src/dependenpy/_internal/node.py`

```
def __getitem__(self, item: str) -> Package | Module:
    """Return the corresponding Package or Module object.

    Parameters:
        item: Name of the package/module, dot-separated.

    Raises:
        KeyError: When the package or module cannot be found.

    Returns:
        The corresponding object.
    """
    depth = item.count(".") + 1
    parts = item.split(".", 1)
    for module in self.modules:
        if parts[0] == module.name and depth == 1:
            return module
    for package in self.packages:
        if parts[0] == package.name:
            if depth == 1:
                return package
            obj = package.get(parts[1])
            if obj:
                return obj
    raise KeyError(item)
```

### absolute_name

```
absolute_name(depth: int = 0) -> str
```

Return the absolute name of the node.

Concatenate names from root to self within depth.

Parameters:

- **`depth`** (`int`, default: `0` ) – Maximum depth to go to.

Returns:

- `str` – Absolute name of the node (until given depth is reached).

Source code in `src/dependenpy/_internal/node.py`

```
def absolute_name(self, depth: int = 0) -> str:
    """Return the absolute name of the node.

    Concatenate names from root to self within depth.

    Parameters:
        depth: Maximum depth to go to.

    Returns:
        Absolute name of the node (until given depth is reached).
    """
    node: Package
    node, node_depth = self, self.depth  # type: ignore[assignment]
    if depth < 1:
        depth = node_depth
    while node_depth > depth and node.package is not None:
        node = node.package
        node_depth -= 1
    names = []
    while node is not None:
        names.append(node.name)
        node = node.package  # type: ignore[assignment]
    return ".".join(reversed(names))
```

### as_dict

```
as_dict() -> dict
```

Return the dependencies as a dictionary.

Returns:

- `dict` – Dictionary of dependencies.

Source code in `src/dependenpy/_internal/node.py`

```
def as_dict(self) -> dict:
    """Return the dependencies as a dictionary.

    Returns:
        Dictionary of dependencies.
    """
    return {
        "name": str(self),
        "modules": [module.as_dict() for module in self.modules],
        "packages": [package.as_dict() for package in self.packages],
    }
```

### as_graph

```
as_graph(depth: int = 0) -> Graph
```

Create a graph with self as node, cache it, return it.

Parameters:

- **`depth`** (`int`, default: `0` ) – Depth of the graph.

Returns:

- `Graph` – An instance of Graph.

Source code in `src/dependenpy/_internal/node.py`

```
def as_graph(self, depth: int = 0) -> Graph:
    """Create a graph with self as node, cache it, return it.

    Parameters:
        depth: Depth of the graph.

    Returns:
        An instance of Graph.
    """
    if depth not in self._graph_cache:
        self._graph_cache[depth] = Graph(self, depth=depth)  # type: ignore[arg-type]
    return self._graph_cache[depth]
```

### as_matrix

```
as_matrix(depth: int = 0) -> Matrix
```

Create a matrix with self as node, cache it, return it.

Parameters:

- **`depth`** (`int`, default: `0` ) – Depth of the matrix.

Returns:

- `Matrix` – An instance of Matrix.

Source code in `src/dependenpy/_internal/node.py`

```
def as_matrix(self, depth: int = 0) -> Matrix:
    """Create a matrix with self as node, cache it, return it.

    Parameters:
        depth: Depth of the matrix.

    Returns:
        An instance of Matrix.
    """
    if depth not in self._matrix_cache:
        self._matrix_cache[depth] = Matrix(self, depth=depth)  # type: ignore[arg-type]
    return self._matrix_cache[depth]
```

### as_treemap

```
as_treemap() -> TreeMap
```

Return the dependencies as a TreeMap.

Returns:

- `TreeMap` – An instance of TreeMap.

Source code in `src/dependenpy/_internal/node.py`

```
def as_treemap(self) -> TreeMap:
    """Return the dependencies as a TreeMap.

    Returns:
        An instance of TreeMap.
    """
    if not self._treemap_cache:
        self._treemap_cache = TreeMap(self)
    return self._treemap_cache
```

### build_dependencies

```
build_dependencies() -> None
```

Recursively build the dependencies for sub-modules and sub-packages.

Iterate on node's modules then packages and call their build_dependencies methods.

Source code in `src/dependenpy/_internal/node.py`

```
def build_dependencies(self) -> None:
    """Recursively build the dependencies for sub-modules and sub-packages.

    Iterate on node's modules then packages and call their
    build_dependencies methods.
    """
    for module in self.modules:
        module.build_dependencies()
    for package in self.packages:
        package.build_dependencies()
```

### build_tree

```
build_tree() -> None
```

Build the tree for this package.

Source code in `src/dependenpy/_internal/dsm.py`

```
def build_tree(self) -> None:
    """Build the tree for this package."""
    for module in listdir(self.path):
        abs_m = join(self.path, module)
        if isfile(abs_m) and module.endswith(".py"):
            name = splitext(module)[0]
            if not self.limit_to or name in self.limit_to:
                self.modules.append(Module(name, abs_m, self.dsm, self))
        elif isdir(abs_m) and (isfile(join(abs_m, "__init__.py")) or not self.enforce_init):
            heads, new_limit_to = self.split_limits_heads()
            if not heads or module in heads:
                self.packages.append(
                    Package(
                        module,
                        abs_m,
                        self.dsm,
                        self,
                        new_limit_to,
                        build_tree=True,
                        build_dependencies=False,
                        enforce_init=self.enforce_init,
                    ),
                )
```

### cardinal

```
cardinal(to: Package | Module) -> int
```

Return the number of dependencies of this package to the given node.

Parameters:

- **`to`** (`Package | Module`) – Target node.

Returns:

- `int` – Number of dependencies.

Source code in `src/dependenpy/_internal/dsm.py`

```
def cardinal(self, to: Package | Module) -> int:
    """Return the number of dependencies of this package to the given node.

    Parameters:
        to: Target node.

    Returns:
        Number of dependencies.
    """
    return sum(module.cardinal(to) for module in self.submodules)
```

### get

```
get(item: str) -> Package | Module
```

Get item through `__getitem__` and cache the result.

Parameters:

- **`item`** (`str`) – Name of package or module.

Returns:

- `Package | Module` – The corresponding object.

Source code in `src/dependenpy/_internal/node.py`

```
def get(self, item: str) -> Package | Module:
    """Get item through `__getitem__` and cache the result.

    Parameters:
        item: Name of package or module.

    Returns:
        The corresponding object.
    """
    if item not in self._item_cache:
        try:
            obj = self.__getitem__(item)
        except KeyError:
            obj = None
        self._item_cache[item] = obj
    return self._item_cache[item]
```

### get_target

```
get_target(target: str) -> Package | Module
```

Get the result of \_get_target, cache it and return it.

Parameters:

- **`target`** (`str`) – Target to find.

Returns:

- `Package | Module` – Package containing target or corresponding module.

Source code in `src/dependenpy/_internal/node.py`

```
def get_target(self, target: str) -> Package | Module:
    """Get the result of _get_target, cache it and return it.

    Parameters:
        target: Target to find.

    Returns:
        Package containing target or corresponding module.
    """
    if target not in self._target_cache:
        self._target_cache[target] = self._get_target(target)
    return self._target_cache[target]
```

### print

```
print(
    format: str | None = TEXT,
    output: IO = stdout,
    **kwargs: Any,
) -> None
```

Print the object in a file or on standard output by default.

Parameters:

- **`format`** (`str | None`, default: `TEXT` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – Descriptor to an opened file (default to standard output).
- **`**kwargs`** (`Any`, default: `{}` ) – Additional arguments.

Source code in `src/dependenpy/_internal/helpers.py`

```
def print(self, format: str | None = TEXT, output: IO = sys.stdout, **kwargs: Any) -> None:  # noqa: A002
    """Print the object in a file or on standard output by default.

    Parameters:
        format: Output format (csv, json or text).
        output: Descriptor to an opened file (default to standard output).
        **kwargs: Additional arguments.
    """
    if format is None:
        format = TEXT

    if format != TEXT:
        kwargs.pop("zero", "")

    if format == TEXT:
        print(self._to_text(**kwargs), file=output)
    elif format == CSV:
        print(self._to_csv(**kwargs), file=output)
    elif format == JSON:
        print(self._to_json(**kwargs), file=output)
```

### print_graph

```
print_graph(
    format: str | None = None,
    output: IO = stdout,
    depth: int = 0,
    **kwargs: Any,
) -> None
```

Print the graph for self's nodes.

Parameters:

- **`format`** (`str | None`, default: `None` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – File descriptor on which to write.
- **`depth`** (`int`, default: `0` ) – Depth of the graph.
- **`**kwargs`** (`Any`, default: `{}` ) – Additional keyword arguments passed to graph.print.

Source code in `src/dependenpy/_internal/node.py`

```
def print_graph(
    self,
    format: str | None = None,  # noqa: A002
    output: IO = sys.stdout,
    depth: int = 0,
    **kwargs: Any,
) -> None:
    """Print the graph for self's nodes.

    Parameters:
        format: Output format (csv, json or text).
        output: File descriptor on which to write.
        depth: Depth of the graph.
        **kwargs: Additional keyword arguments passed to `graph.print`.
    """
    graph = self.as_graph(depth=depth)
    graph.print(format=format, output=output, **kwargs)
```

### print_matrix

```
print_matrix(
    format: str | None = None,
    output: IO = stdout,
    depth: int = 0,
    **kwargs: Any,
) -> None
```

Print the matrix for self's nodes.

Parameters:

- **`format`** (`str | None`, default: `None` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – File descriptor on which to write.
- **`depth`** (`int`, default: `0` ) – Depth of the matrix.
- **`**kwargs`** (`Any`, default: `{}` ) – Additional keyword arguments passed to matrix.print.

Source code in `src/dependenpy/_internal/node.py`

```
def print_matrix(
    self,
    format: str | None = None,  # noqa: A002
    output: IO = sys.stdout,
    depth: int = 0,
    **kwargs: Any,
) -> None:
    """Print the matrix for self's nodes.

    Parameters:
        format: Output format (csv, json or text).
        output: File descriptor on which to write.
        depth: Depth of the matrix.
        **kwargs: Additional keyword arguments passed to `matrix.print`.
    """
    matrix = self.as_matrix(depth=depth)
    matrix.print(format=format, output=output, **kwargs)
```

### print_treemap

```
print_treemap(
    format: str | None = None,
    output: IO = stdout,
    **kwargs: Any,
) -> None
```

Print the matrix for self's nodes.

Parameters:

- **`format`** (`str | None`, default: `None` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – File descriptor on which to write.
- **`**kwargs`** (`Any`, default: `{}` ) – Additional keyword arguments passed to treemap.print.

Source code in `src/dependenpy/_internal/node.py`

```
def print_treemap(self, format: str | None = None, output: IO = sys.stdout, **kwargs: Any) -> None:  # noqa: A002
    """Print the matrix for self's nodes.

    Parameters:
        format: Output format (csv, json or text).
        output: File descriptor on which to write.
        **kwargs: Additional keyword arguments passed to `treemap.print`.
    """
    treemap = self.as_treemap()
    treemap.print(format=format, output=output, **kwargs)
```

### split_limits_heads

```
split_limits_heads() -> tuple[list[str], list[str]]
```

Return first parts of dot-separated strings, and rest of strings.

Returns:

- `tuple[list[str], list[str]]` – The heads and rest of the strings.

Source code in `src/dependenpy/_internal/dsm.py`

```
def split_limits_heads(self) -> tuple[list[str], list[str]]:
    """Return first parts of dot-separated strings, and rest of strings.

    Returns:
        The heads and rest of the strings.
    """
    heads = []
    new_limit_to = []
    for limit in self.limit_to:
        if "." in limit:
            name, limit = limit.split(".", 1)  # noqa: PLW2901
            heads.append(name)
            new_limit_to.append(limit)
        else:
            heads.append(limit)
    return heads, new_limit_to
```

## PackageFinder

Abstract package finder class.

Methods:

- **`find`** – Find method.

### find

```
find(package: str, **kwargs: Any) -> PackageSpec | None
```

Find method.

Parameters:

- **`package`** (`str`) – Package to find.
- **`**kwargs`** (`Any`, default: `{}` ) – Additional keyword arguments.

Returns:

- `PackageSpec | None` – Package spec or None.

Source code in `src/dependenpy/_internal/finder.py`

```
def find(self, package: str, **kwargs: Any) -> PackageSpec | None:
    """Find method.

    Parameters:
        package: Package to find.
        **kwargs: Additional keyword arguments.

    Returns:
        Package spec or None.
    """
    raise NotImplementedError
```

## PackageSpec

```
PackageSpec(
    name: str, path: str, limit_to: list[str] | None = None
)
```

Holder for a package specification (given as argument to DSM).

Parameters:

- **`name`** (`str`) – Name of the package.
- **`path`** (`str`) – Path to the package.
- **`limit_to`** (`list[str] | None`, default: `None` ) – Limitations.

Methods:

- **`__hash__`** – Hash method.
- **`add`** – Add limitations of given spec to self's.
- **`combine`** – Combine package specifications' limitations.

Attributes:

- **`ismodule`** (`bool`) – Property to tell if the package is in fact a module (a file).
- **`limit_to`** – List of limitations.
- **`name`** – Name of the package.
- **`path`** – Path to the package.

Source code in `src/dependenpy/_internal/finder.py`

```
def __init__(self, name: str, path: str, limit_to: list[str] | None = None) -> None:
    """Initialization method.

    Parameters:
        name: Name of the package.
        path: Path to the package.
        limit_to: Limitations.
    """
    self.name = name
    """Name of the package."""
    self.path = path
    """Path to the package."""
    self.limit_to = limit_to or []
    """List of limitations."""
```

### ismodule

```
ismodule: bool
```

Property to tell if the package is in fact a module (a file).

Returns:

- `bool` – Whether this package is in fact a module.

### limit_to

```
limit_to = limit_to or []
```

List of limitations.

### name

```
name = name
```

Name of the package.

### path

```
path = path
```

Path to the package.

### __hash__

```
__hash__()
```

Hash method.

The hash is computed based on the package name and path.

Source code in `src/dependenpy/_internal/finder.py`

```
def __hash__(self):
    """Hash method.

    The hash is computed based on the package name and path.
    """
    return hash((self.name, self.path))
```

### add

```
add(spec: PackageSpec) -> None
```

Add limitations of given spec to self's.

Parameters:

- **`spec`** (`PackageSpec`) – Another spec.

Source code in `src/dependenpy/_internal/finder.py`

```
def add(self, spec: PackageSpec) -> None:
    """Add limitations of given spec to self's.

    Parameters:
        spec: Another spec.
    """
    for limit in spec.limit_to:
        if limit not in self.limit_to:
            self.limit_to.append(limit)
```

### combine

```
combine(specs: list[PackageSpec]) -> list[PackageSpec]
```

Combine package specifications' limitations.

Parameters:

- **`specs`** (`list[PackageSpec]`) – The package specifications.

Returns:

- `list[PackageSpec]` – The new, merged list of PackageSpec.

Source code in `src/dependenpy/_internal/finder.py`

```
@staticmethod
def combine(specs: list[PackageSpec]) -> list[PackageSpec]:
    """Combine package specifications' limitations.

    Parameters:
        specs: The package specifications.

    Returns:
        The new, merged list of PackageSpec.
    """
    new_specs: dict[PackageSpec, PackageSpec] = {}
    for spec in specs:
        if new_specs.get(spec) is None:
            new_specs[spec] = spec
        else:
            new_specs[spec].add(spec)
    return list(new_specs.values())
```

## PrintMixin

Print mixin class.

Methods:

- **`print`** – Print the object in a file or on standard output by default.

### print

```
print(
    format: str | None = TEXT,
    output: IO = stdout,
    **kwargs: Any,
) -> None
```

Print the object in a file or on standard output by default.

Parameters:

- **`format`** (`str | None`, default: `TEXT` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – Descriptor to an opened file (default to standard output).
- **`**kwargs`** (`Any`, default: `{}` ) – Additional arguments.

Source code in `src/dependenpy/_internal/helpers.py`

```
def print(self, format: str | None = TEXT, output: IO = sys.stdout, **kwargs: Any) -> None:  # noqa: A002
    """Print the object in a file or on standard output by default.

    Parameters:
        format: Output format (csv, json or text).
        output: Descriptor to an opened file (default to standard output).
        **kwargs: Additional arguments.
    """
    if format is None:
        format = TEXT

    if format != TEXT:
        kwargs.pop("zero", "")

    if format == TEXT:
        print(self._to_text(**kwargs), file=output)
    elif format == CSV:
        print(self._to_csv(**kwargs), file=output)
    elif format == JSON:
        print(self._to_json(**kwargs), file=output)
```

## RootNode

```
RootNode(build_tree: bool = True)
```

Shared code between DSM and Package.

Parameters:

- **`build_tree`** (`bool`, default: `True` ) – Whether to immediately build the tree or not.

Methods:

- **`__bool__`** – Node as Boolean.
- **`__contains__`** – Get result of \_contains, cache it and return it.
- **`__getitem__`** – Return the corresponding Package or Module object.
- **`as_dict`** – Return the dependencies as a dictionary.
- **`as_graph`** – Create a graph with self as node, cache it, return it.
- **`as_matrix`** – Create a matrix with self as node, cache it, return it.
- **`as_treemap`** – Return the dependencies as a TreeMap.
- **`build_dependencies`** – Recursively build the dependencies for sub-modules and sub-packages.
- **`build_tree`** – To be overridden.
- **`get`** – Get item through __getitem__ and cache the result.
- **`get_target`** – Get the result of \_get_target, cache it and return it.
- **`print_graph`** – Print the graph for self's nodes.
- **`print_matrix`** – Print the matrix for self's nodes.
- **`print_treemap`** – Print the matrix for self's nodes.

Attributes:

- **`empty`** (`bool`) – Whether the node has neither modules nor packages.
- **`modules`** (`list[Module]`) – List of modules contained in the node.
- **`packages`** (`list[Package]`) – List of packages contained in the node.
- **`submodules`** (`list[Module]`) – Property to return all sub-modules of the node, recursively.

Source code in `src/dependenpy/_internal/node.py`

```
def __init__(self, build_tree: bool = True):  # noqa: FBT001,FBT002
    """Initialization method.

    Parameters:
        build_tree: Whether to immediately build the tree or not.
    """
    self._target_cache: dict[str, Any] = {}
    self._item_cache: dict[str, Any] = {}
    self._contains_cache: dict[Package | Module, bool] = {}
    self._matrix_cache: dict[int, Matrix] = {}
    self._graph_cache: dict[int, Graph] = {}
    self._treemap_cache = TreeMap()
    self.modules: list[Module] = []
    """List of modules contained in the node."""
    self.packages: list[Package] = []
    """List of packages contained in the node."""

    if build_tree:
        self.build_tree()
```

### empty

```
empty: bool
```

Whether the node has neither modules nor packages.

Returns:

- `bool` – True if empty, False otherwise.

### modules

```
modules: list[Module] = []
```

List of modules contained in the node.

### packages

```
packages: list[Package] = []
```

List of packages contained in the node.

### submodules

```
submodules: list[Module]
```

Property to return all sub-modules of the node, recursively.

Returns:

- `list[Module]` – The sub-modules.

### __bool__

```
__bool__() -> bool
```

Node as Boolean.

Returns:

- `bool` – Result of node.empty.

Source code in `src/dependenpy/_internal/node.py`

```
def __bool__(self) -> bool:
    """Node as Boolean.

    Returns:
        Result of node.empty.
    """
    return bool(self.modules or self.packages)
```

### __contains__

```
__contains__(item: Package | Module) -> bool
```

Get result of \_contains, cache it and return it.

Parameters:

- **`item`** (`Package | Module`) – A package or module.

Returns:

- `bool` – True if self contains item, False otherwise.

Source code in `src/dependenpy/_internal/node.py`

```
def __contains__(self, item: Package | Module) -> bool:
    """Get result of _contains, cache it and return it.

    Parameters:
        item: A package or module.

    Returns:
        True if self contains item, False otherwise.
    """
    if item not in self._contains_cache:
        self._contains_cache[item] = self._contains(item)
    return self._contains_cache[item]
```

### __getitem__

```
__getitem__(item: str) -> Package | Module
```

Return the corresponding Package or Module object.

Parameters:

- **`item`** (`str`) – Name of the package/module, dot-separated.

Raises:

- `KeyError` – When the package or module cannot be found.

Returns:

- `Package | Module` – The corresponding object.

Source code in `src/dependenpy/_internal/node.py`

```
def __getitem__(self, item: str) -> Package | Module:
    """Return the corresponding Package or Module object.

    Parameters:
        item: Name of the package/module, dot-separated.

    Raises:
        KeyError: When the package or module cannot be found.

    Returns:
        The corresponding object.
    """
    depth = item.count(".") + 1
    parts = item.split(".", 1)
    for module in self.modules:
        if parts[0] == module.name and depth == 1:
            return module
    for package in self.packages:
        if parts[0] == package.name:
            if depth == 1:
                return package
            obj = package.get(parts[1])
            if obj:
                return obj
    raise KeyError(item)
```

### as_dict

```
as_dict() -> dict
```

Return the dependencies as a dictionary.

Returns:

- `dict` – Dictionary of dependencies.

Source code in `src/dependenpy/_internal/node.py`

```
def as_dict(self) -> dict:
    """Return the dependencies as a dictionary.

    Returns:
        Dictionary of dependencies.
    """
    return {
        "name": str(self),
        "modules": [module.as_dict() for module in self.modules],
        "packages": [package.as_dict() for package in self.packages],
    }
```

### as_graph

```
as_graph(depth: int = 0) -> Graph
```

Create a graph with self as node, cache it, return it.

Parameters:

- **`depth`** (`int`, default: `0` ) – Depth of the graph.

Returns:

- `Graph` – An instance of Graph.

Source code in `src/dependenpy/_internal/node.py`

```
def as_graph(self, depth: int = 0) -> Graph:
    """Create a graph with self as node, cache it, return it.

    Parameters:
        depth: Depth of the graph.

    Returns:
        An instance of Graph.
    """
    if depth not in self._graph_cache:
        self._graph_cache[depth] = Graph(self, depth=depth)  # type: ignore[arg-type]
    return self._graph_cache[depth]
```

### as_matrix

```
as_matrix(depth: int = 0) -> Matrix
```

Create a matrix with self as node, cache it, return it.

Parameters:

- **`depth`** (`int`, default: `0` ) – Depth of the matrix.

Returns:

- `Matrix` – An instance of Matrix.

Source code in `src/dependenpy/_internal/node.py`

```
def as_matrix(self, depth: int = 0) -> Matrix:
    """Create a matrix with self as node, cache it, return it.

    Parameters:
        depth: Depth of the matrix.

    Returns:
        An instance of Matrix.
    """
    if depth not in self._matrix_cache:
        self._matrix_cache[depth] = Matrix(self, depth=depth)  # type: ignore[arg-type]
    return self._matrix_cache[depth]
```

### as_treemap

```
as_treemap() -> TreeMap
```

Return the dependencies as a TreeMap.

Returns:

- `TreeMap` – An instance of TreeMap.

Source code in `src/dependenpy/_internal/node.py`

```
def as_treemap(self) -> TreeMap:
    """Return the dependencies as a TreeMap.

    Returns:
        An instance of TreeMap.
    """
    if not self._treemap_cache:
        self._treemap_cache = TreeMap(self)
    return self._treemap_cache
```

### build_dependencies

```
build_dependencies() -> None
```

Recursively build the dependencies for sub-modules and sub-packages.

Iterate on node's modules then packages and call their build_dependencies methods.

Source code in `src/dependenpy/_internal/node.py`

```
def build_dependencies(self) -> None:
    """Recursively build the dependencies for sub-modules and sub-packages.

    Iterate on node's modules then packages and call their
    build_dependencies methods.
    """
    for module in self.modules:
        module.build_dependencies()
    for package in self.packages:
        package.build_dependencies()
```

### build_tree

```
build_tree() -> None
```

To be overridden.

Source code in `src/dependenpy/_internal/node.py`

```
def build_tree(self) -> None:
    """To be overridden."""
    raise NotImplementedError
```

### get

```
get(item: str) -> Package | Module
```

Get item through `__getitem__` and cache the result.

Parameters:

- **`item`** (`str`) – Name of package or module.

Returns:

- `Package | Module` – The corresponding object.

Source code in `src/dependenpy/_internal/node.py`

```
def get(self, item: str) -> Package | Module:
    """Get item through `__getitem__` and cache the result.

    Parameters:
        item: Name of package or module.

    Returns:
        The corresponding object.
    """
    if item not in self._item_cache:
        try:
            obj = self.__getitem__(item)
        except KeyError:
            obj = None
        self._item_cache[item] = obj
    return self._item_cache[item]
```

### get_target

```
get_target(target: str) -> Package | Module
```

Get the result of \_get_target, cache it and return it.

Parameters:

- **`target`** (`str`) – Target to find.

Returns:

- `Package | Module` – Package containing target or corresponding module.

Source code in `src/dependenpy/_internal/node.py`

```
def get_target(self, target: str) -> Package | Module:
    """Get the result of _get_target, cache it and return it.

    Parameters:
        target: Target to find.

    Returns:
        Package containing target or corresponding module.
    """
    if target not in self._target_cache:
        self._target_cache[target] = self._get_target(target)
    return self._target_cache[target]
```

### print_graph

```
print_graph(
    format: str | None = None,
    output: IO = stdout,
    depth: int = 0,
    **kwargs: Any,
) -> None
```

Print the graph for self's nodes.

Parameters:

- **`format`** (`str | None`, default: `None` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – File descriptor on which to write.
- **`depth`** (`int`, default: `0` ) – Depth of the graph.
- **`**kwargs`** (`Any`, default: `{}` ) – Additional keyword arguments passed to graph.print.

Source code in `src/dependenpy/_internal/node.py`

```
def print_graph(
    self,
    format: str | None = None,  # noqa: A002
    output: IO = sys.stdout,
    depth: int = 0,
    **kwargs: Any,
) -> None:
    """Print the graph for self's nodes.

    Parameters:
        format: Output format (csv, json or text).
        output: File descriptor on which to write.
        depth: Depth of the graph.
        **kwargs: Additional keyword arguments passed to `graph.print`.
    """
    graph = self.as_graph(depth=depth)
    graph.print(format=format, output=output, **kwargs)
```

### print_matrix

```
print_matrix(
    format: str | None = None,
    output: IO = stdout,
    depth: int = 0,
    **kwargs: Any,
) -> None
```

Print the matrix for self's nodes.

Parameters:

- **`format`** (`str | None`, default: `None` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – File descriptor on which to write.
- **`depth`** (`int`, default: `0` ) – Depth of the matrix.
- **`**kwargs`** (`Any`, default: `{}` ) – Additional keyword arguments passed to matrix.print.

Source code in `src/dependenpy/_internal/node.py`

```
def print_matrix(
    self,
    format: str | None = None,  # noqa: A002
    output: IO = sys.stdout,
    depth: int = 0,
    **kwargs: Any,
) -> None:
    """Print the matrix for self's nodes.

    Parameters:
        format: Output format (csv, json or text).
        output: File descriptor on which to write.
        depth: Depth of the matrix.
        **kwargs: Additional keyword arguments passed to `matrix.print`.
    """
    matrix = self.as_matrix(depth=depth)
    matrix.print(format=format, output=output, **kwargs)
```

### print_treemap

```
print_treemap(
    format: str | None = None,
    output: IO = stdout,
    **kwargs: Any,
) -> None
```

Print the matrix for self's nodes.

Parameters:

- **`format`** (`str | None`, default: `None` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – File descriptor on which to write.
- **`**kwargs`** (`Any`, default: `{}` ) – Additional keyword arguments passed to treemap.print.

Source code in `src/dependenpy/_internal/node.py`

```
def print_treemap(self, format: str | None = None, output: IO = sys.stdout, **kwargs: Any) -> None:  # noqa: A002
    """Print the matrix for self's nodes.

    Parameters:
        format: Output format (csv, json or text).
        output: File descriptor on which to write.
        **kwargs: Additional keyword arguments passed to `treemap.print`.
    """
    treemap = self.as_treemap()
    treemap.print(format=format, output=output, **kwargs)
```

## TreeMap

```
TreeMap(*nodes: Any, value: int = -1)
```

Bases: `PrintMixin`

TreeMap class.

Parameters:

- **`*nodes`** (`Any`, default: `()` ) – the nodes from which to build the treemap.
- **`value`** (`int`, default: `-1` ) – the value of the current area.

Methods:

- **`print`** – Print the object in a file or on standard output by default.

Attributes:

- **`value`** – The value of the current area.

Source code in `src/dependenpy/_internal/structures.py`

```
def __init__(self, *nodes: Any, value: int = -1):  # noqa: ARG002
    """Initialization method.

    Arguments:
        *nodes: the nodes from which to build the treemap.
        value: the value of the current area.
    """
    # if nodes:
    #     matrix_lower_level = Matrix(*nodes, depth=2)
    #     matrix_current_level = Matrix(*nodes, depth=1)
    #     if value == -1:
    #         value = sum(c for row in matrix_current_level.data for c in row)
    #     splits = [0]
    #     key_comp = matrix_lower_level.keys[0].split('.')[0]
    #     i = 1
    #     for key in matrix_lower_level.keys[1:]:
    #         key = key.split('.')[0]
    #         if key != key_comp:
    #             splits.append(i)
    #             key_comp = key
    #         i += 1
    #     splits.append(i)
    #
    #     self.data = []
    #     for i in range(len(splits) - 1):
    #         self.data.append([])
    #         rows = matrix_lower_level.data[splits[i]:splits[i+1]]
    #         for j in range(len(splits) - 1):
    #             self.data[i].append([row[splits[j]:splits[j+1]] for row in rows])

    self.value = value
    """The value of the current area."""
```

### value

```
value = value
```

The value of the current area.

### print

```
print(
    format: str | None = TEXT,
    output: IO = stdout,
    **kwargs: Any,
) -> None
```

Print the object in a file or on standard output by default.

Parameters:

- **`format`** (`str | None`, default: `TEXT` ) – Output format (csv, json or text).
- **`output`** (`IO`, default: `stdout` ) – Descriptor to an opened file (default to standard output).
- **`**kwargs`** (`Any`, default: `{}` ) – Additional arguments.

Source code in `src/dependenpy/_internal/helpers.py`

```
def print(self, format: str | None = TEXT, output: IO = sys.stdout, **kwargs: Any) -> None:  # noqa: A002
    """Print the object in a file or on standard output by default.

    Parameters:
        format: Output format (csv, json or text).
        output: Descriptor to an opened file (default to standard output).
        **kwargs: Additional arguments.
    """
    if format is None:
        format = TEXT

    if format != TEXT:
        kwargs.pop("zero", "")

    if format == TEXT:
        print(self._to_text(**kwargs), file=output)
    elif format == CSV:
        print(self._to_csv(**kwargs), file=output)
    elif format == JSON:
        print(self._to_json(**kwargs), file=output)
```

## Vertex

```
Vertex(name: str)
```

Vertex class. Used in Graph class.

Parameters:

- **`name`** (`str`) – name of the vertex.

Methods:

- **`connect_from`** – Connect another vertex to this one.
- **`connect_to`** – Connect this vertex to another one.

Attributes:

- **`edges_in`** (`set[Edge]`) – Incoming edges.
- **`edges_out`** (`set[Edge]`) – Outgoing edges.
- **`name`** – Name of the vertex.

Source code in `src/dependenpy/_internal/structures.py`

```
def __init__(self, name: str) -> None:
    """Initialization method.

    Parameters:
        name (str): name of the vertex.
    """
    self.name = name
    """Name of the vertex."""
    self.edges_in: set[Edge] = set()
    """Incoming edges."""
    self.edges_out: set[Edge] = set()
    """Outgoing edges."""
```

### edges_in

```
edges_in: set[Edge] = set()
```

Incoming edges.

### edges_out

```
edges_out: set[Edge] = set()
```

Outgoing edges.

### name

```
name = name
```

Name of the vertex.

### connect_from

```
connect_from(vertex: Vertex, weight: int = 1) -> Edge
```

Connect another vertex to this one.

Parameters:

- **`vertex`** (`Vertex`) – Vertex to connect from.
- **`weight`** (`int`, default: `1` ) – Weight of the edge.

Returns:

- `Edge` – The newly created edge.

Source code in `src/dependenpy/_internal/structures.py`

```
def connect_from(self, vertex: Vertex, weight: int = 1) -> Edge:
    """Connect another vertex to this one.

    Parameters:
        vertex: Vertex to connect from.
        weight: Weight of the edge.

    Returns:
        The newly created edge.
    """
    for edge in self.edges_in:
        if vertex == edge.vertex_out:
            return edge
    return Edge(vertex, self, weight)
```

### connect_to

```
connect_to(vertex: Vertex, weight: int = 1) -> Edge
```

Connect this vertex to another one.

Parameters:

- **`vertex`** (`Vertex`) – Vertex to connect to.
- **`weight`** (`int`, default: `1` ) – Weight of the edge.

Returns:

- `Edge` – The newly created edge.

Source code in `src/dependenpy/_internal/structures.py`

```
def connect_to(self, vertex: Vertex, weight: int = 1) -> Edge:
    """Connect this vertex to another one.

    Parameters:
        vertex: Vertex to connect to.
        weight: Weight of the edge.

    Returns:
        The newly created edge.
    """
    for edge in self.edges_out:
        if vertex == edge.vertex_in:
            return edge
    return Edge(self, vertex, weight)
```

## get_parser

```
get_parser() -> ArgumentParser
```

Return the CLI argument parser.

Returns:

- `ArgumentParser` – An argparse parser.

Source code in `src/dependenpy/_internal/cli.py`

```
def get_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    parser = argparse.ArgumentParser(
        prog="dependenpy",
        add_help=False,
        description="Command line tool for dependenpy Python package.",
    )
    mxg = parser.add_mutually_exclusive_group(required=False)

    parser.add_argument(
        "packages",
        metavar="PACKAGES",
        nargs=argparse.ONE_OR_MORE,
        help="The package list. Can be a comma-separated list. Each package "
        "must be either a valid path or a package in PYTHONPATH.",
    )
    parser.add_argument(
        "-d",
        "--depth",
        default=None,
        type=int,
        dest="depth",
        help="Specify matrix or graph depth. Default: best guess.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=FORMAT,
        default="text",
        dest="format",
        help="Output format. Default: text.",
    )
    mxg.add_argument(
        "-g",
        "--show-graph",
        action="store_true",
        dest="graph",
        default=False,
        help="Show the graph (no text format). Default: false.",
    )
    parser.add_argument(
        "-G",
        "--greedy",
        action="store_true",
        dest="greedy",
        default=False,
        help="Explore subdirectories even if they do not contain an "
        "__init__.py file. Can make execution slower. Default: false.",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )
    parser.add_argument(
        "-i",
        "--indent",
        default=None,
        type=int,
        dest="indent",
        help="Specify output indentation. CSV will never be indented. "
        "Text will always have new-lines. JSON can be minified with "
        "a negative value. Default: best guess.",
    )
    mxg.add_argument(
        "-l",
        "--show-dependencies-list",
        action="store_true",
        dest="dependencies",
        default=False,
        help="Show the dependencies list. Default: false.",
    )
    mxg.add_argument(
        "-m",
        "--show-matrix",
        action="store_true",
        dest="matrix",
        default=False,
        help="Show the matrix. Default: true unless -g, -l or -t.",
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        dest="output",
        default=sys.stdout,
        help="Output to given file. Default: stdout.",
    )
    mxg.add_argument(
        "-t",
        "--show-treemap",
        action="store_true",
        dest="treemap",
        default=False,
        help="Show the treemap (work in progress). Default: false.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"dependenpy {debug._get_version()}",
        help="Show the current version of the program and exit.",
    )
    parser.add_argument(
        "-z",
        "--zero",
        dest="zero",
        default="0",
        help="Character to use for cells with value=0 (text matrix display only).",
    )

    parser.add_argument("--debug-info", action=_DebugInfo, help="Print debug information.")
    return parser
```

## guess_depth

```
guess_depth(packages: Sequence[str]) -> int
```

Guess the optimal depth to use for the given list of arguments.

Parameters:

- **`packages`** (`Sequence[str]`) – List of packages.

Returns:

- `int` – Guessed depth to use.

Source code in `src/dependenpy/_internal/helpers.py`

```
def guess_depth(packages: Sequence[str]) -> int:
    """Guess the optimal depth to use for the given list of arguments.

    Parameters:
        packages: List of packages.

    Returns:
        Guessed depth to use.
    """
    if len(packages) == 1:
        return packages[0].count(".") + 2
    return min(package.count(".") for package in packages) + 1
```

## main

```
main(args: list[str] | None = None) -> int
```

Run the main program.

This function is executed when you type `dependenpy` or `python -m dependenpy`.

Parameters:

- **`args`** (`list[str] | None`, default: `None` ) – Arguments passed from the command line.

Returns:

- `int` – An exit code. 0 (OK), 1 (dsm empty) or 2 (error).

Source code in `src/dependenpy/_internal/cli.py`

```
def main(args: list[str] | None = None) -> int:
    """Run the main program.

    This function is executed when you type `dependenpy` or `python -m dependenpy`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code. 0 (OK), 1 (dsm empty) or 2 (error).
    """
    parser = get_parser()
    opts = parser.parse_args(args=args)
    if not (opts.matrix or opts.dependencies or opts.treemap or opts.graph):
        opts.matrix = True

    dsm = DSM(*_get_packages(opts), build_tree=True, build_dependencies=True, enforce_init=not opts.greedy)
    if dsm.empty:
        return 1

    # init colorama
    init()

    try:
        _run(opts, dsm)
    except BrokenPipeError:
        # avoid traceback
        return 2

    return 0
```
