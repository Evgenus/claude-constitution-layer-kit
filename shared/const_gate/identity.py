"""Which gate this process is.

The shared code serves several plugins, and each hook process runs exactly one of them.
The plugin's entry point declares itself once, before anything is printed; from then on
every message, the log and the dials reader ask here for the name. Nothing else in the
package is global.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Identity:
    namespace: str  # the plugin's name: its dials namespace, its name in every message, its log
    gate: str  # the entry point's name, as the log and the usage line show it
    plugin_root: Path  # where the plugin's requirements file lies


_declared: Identity | None = None


def declare(identity: Identity) -> None:
    global _declared
    _declared = identity


def current() -> Identity:
    if _declared is None:  # a defect of the entry point, never of the repository
        raise RuntimeError("the entry point did not declare which gate it is")
    return _declared
