"""Which gate this process is.

The shared code serves several plugins, and each hook process runs exactly one of them.
The plugin's entry point declares itself once, before anything is printed; from then on
every message, the log and the dials reader ask here for the name. The guard declares the
mode of the run beside it, in the same declaration, for the code that behaves differently in
a hook than in a scan or an act: the git calls' budget. It is the package's one global of its
own; the output module also switches off a process-wide flag of `logging`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from .model import Mode


@dataclass(frozen=True, slots=True)
class Identity:
    namespace: str  # the plugin's name: its dials namespace, its name in every message, its log
    gate: str  # the entry point's name, as the log and the usage line show it
    plugin_root: Path  # where the plugin's requirements file lies
    libraries: Mapping[str, str] = field(
        default_factory=dict
    )  # distribution -> module, beyond the shared ones
    # The clause that closes the two shared failures whose consequence is the entry point's own — a
    # library missing (C2), an unexpected exception (C12.11). A gate's, by default: writes pass; a
    # generator says what it leaves undone.
    until_installed: str = "until then Markdown writes pass unchecked"
    until_fixed: str = "until it is fixed this check does not run"
    # The skill of the plugin that teaches a mode's rule and its fix, by mode, named in the line that
    # follows a red verdict of that mode (F10); a mode without one, no line.
    skills: Mapping[Mode, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class _Declaration:
    identity: Identity
    mode: Mode | None  # None: declared without a mode, as a test runner does — no mode-bound behaviour


_declared: _Declaration | None = None


def declare(identity: Identity, mode: Mode | None = None) -> None:
    global _declared
    now = _Declaration(identity, mode)
    if _declared is not None and _declared != now:
        raise RuntimeError("a process is one gate: a second, different declaration is a defect")
    _declared = now


def current() -> Identity:
    if _declared is None:  # a defect of the entry point, never of the repository
        raise RuntimeError("the entry point did not declare which gate it is")
    return _declared.identity


def declared_mode() -> Mode | None:
    """The mode the run was declared in, or None where none was declared — never a failure: a
    caller that asks for it behaves as it did before there was one."""
    return None if _declared is None else _declared.mode
