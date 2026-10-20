"""The cheap check that runs on every invocation, before anything is imported that could
fail halfway: every library declared in the plugin's requirements file must import.
(The interpreter floor is checked earlier still, by each entry file against its own
literal, in syntax any Python 3 can parse; `FLOOR` below is the one source of that value.)"""

from __future__ import annotations

import importlib
from pathlib import Path

from . import identity, messages
from .errors import ConfigurationFailure

# The floor's one source, read by no gate at run time: each entry file keeps its own literal, since it must
# parse on any Python 3; every copy is held to this one.
FLOOR = (3, 12)

# distribution name in requirements.txt -> the module it provides; what the shared code itself needs
SHARED: dict[str, str] = {"PyYAML": "yaml"}


def declared() -> dict[str, str]:
    """The shared libraries and the ones the module declared with its identity."""
    return {**SHARED, **identity.current().libraries}


def requirements_file() -> Path:
    return identity.current().plugin_root / "requirements.txt"


def check() -> None:
    for distribution, module in declared().items():
        try:
            importlib.import_module(module)
        except ImportError as exc:
            raise ConfigurationFailure(
                messages.c2_library_missing(distribution, str(requirements_file()))
            ) from exc
