"""The cheap check that runs on every invocation, before anything is imported that could
fail halfway: every library declared in the plugin's requirements file must import.
(The interpreter floor is checked earlier still, by the entry file, in syntax any
Python 3 can parse.)"""

from __future__ import annotations

import importlib
from pathlib import Path

from . import identity, messages
from .errors import ConfigurationFailure

# distribution name in requirements.txt -> the module it provides
DECLARED: dict[str, str] = {"PyYAML": "yaml"}


def requirements_file() -> Path:
    return identity.current().plugin_root / "requirements.txt"


def check() -> None:
    for distribution, module in DECLARED.items():
        try:
            importlib.import_module(module)
        except ImportError as exc:
            raise ConfigurationFailure(
                messages.c2_library_missing(distribution, str(requirements_file()))
            ) from exc
