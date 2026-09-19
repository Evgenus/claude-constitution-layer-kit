"""Which gate this process is.

The shared code serves several plugins, and each hook process runs exactly one of them.
The plugin's entry point declares itself once, before anything is printed; from then on
every message, the log and the dials reader ask here for the name. It is the package's one
global of its own; the output module also switches off a process-wide flag of `logging`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Identity:
    namespace: str  # the plugin's name: its dials namespace, its name in every message, its log
    gate: str  # the entry point's name, as the log and the usage line show it
    plugin_root: Path  # where the plugin's requirements file lies
    libraries: Mapping[str, str] = field(
        default_factory=dict
    )  # distribution -> module, beyond the shared ones


_declared: Identity | None = None


def declare(identity: Identity) -> None:
    global _declared
    if _declared is not None and _declared != identity:
        raise RuntimeError("a process is one gate: a second, different declaration is a defect")
    _declared = identity


def current() -> Identity:
    if _declared is None:  # a defect of the entry point, never of the repository
        raise RuntimeError("the entry point did not declare which gate it is")
    return _declared
