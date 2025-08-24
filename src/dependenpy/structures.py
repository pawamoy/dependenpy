"""Deprecated. Import from `dependenpy` directly."""

# YORE: Bump 4: Remove file.

import warnings
from typing import Any

from dependenpy._internal import structures


def __getattr__(name: str) -> Any:
    warnings.warn(
        "Importing from `dependenpy.structures` is deprecated. Import from `dependenpy` directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    return getattr(structures, name)
