"""Which gate this process is, and how long its hook may run.

The shared code serves several plugins, and each hook process runs exactly one of them.
The plugin's entry point declares itself once, before anything is printed; from then on
every message, the log and the dials reader ask here for the name. The guard declares the
mode of the run beside it, in the same declaration, for the code that behaves differently in
a hook than in a scan or an act: the git calls' budget and the hook's one deadline.

A hook run has one deadline, `hook_seconds` of the identity from the moment of the declaration,
and every wait of the run takes the smaller of its own cap and what is left of it (`remaining`);
a scan, an act and a process declared with no mode have no deadline. The handler's timeout in the
plugin's hooks file stays `hook_seconds` and `LEFT_FOR_THE_REST` above it, so that a spent
deadline ends with the gate's own line before the platform cuts the hook.

It is the package's one global of its own; the output module also switches off a process-wide flag
of `logging`.
"""

from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from . import messages
from .errors import ConfigurationFailure
from .model import Mode

# The seconds one hook run may take in all, from its declaration: the default of `Identity.hook_seconds`,
# and the handlers' 30 s less `LEFT_FOR_THE_REST`.
HOOK_SECONDS: float = 25
# The seconds a handler's timeout keeps over a hook's budget, for the interpreter's start, which the
# deadline does not count, and for the reads and writes after the last wait.
LEFT_FOR_THE_REST: float = 5


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
    # The seconds one hook run of this gate may take in all, from its declaration: every wait of the run
    # takes what is left of them (`remaining`). Part of the identity, so a second declaration with
    # another number is a defect like any other difference.
    hook_seconds: float = HOOK_SECONDS


@dataclass(frozen=True, slots=True)
class _Declaration:
    identity: Identity
    mode: Mode | None  # None: declared without a mode, as a test runner does — no mode-bound behaviour
    # On the monotonic clock: set in hook mode alone, the moment of the declaration plus `hook_seconds`;
    # no part of the comparison of two declarations, since the clock moves between them.
    deadline: float | None = field(default=None, compare=False)


_declared: _Declaration | None = None


def declare(identity: Identity, mode: Mode | None = None) -> None:
    """Declares the gate and the mode of the run, once. In hook mode it also starts the run's one
    deadline, `identity.hook_seconds` from now; a scan, an act and a declaration with no mode have none.
    A second declaration that is the same keeps the first's deadline; one that differs is a defect."""
    global _declared
    deadline = time.monotonic() + identity.hook_seconds if mode is Mode.HOOK else None
    now = _Declaration(identity, mode, deadline)
    if _declared is not None and _declared != now:
        raise RuntimeError("a process is one gate: a second, different declaration is a defect")
    if _declared is None:
        _declared = now


def current() -> Identity:
    if _declared is None:  # a defect of the entry point, never of the repository
        raise RuntimeError("the entry point did not declare which gate it is")
    return _declared.identity


def declared_mode() -> Mode | None:
    """The mode the run was declared in, or None where none was declared — never a failure: a
    caller that asks for it behaves as it did before there was one."""
    return None if _declared is None else _declared.mode


def remaining(cap: float, before: str) -> float:
    """The seconds a wait of a hook run may take: the smaller of its own `cap` and what is left of the
    run's deadline. Where the run has no deadline — a scan, an act, a process declared with no mode —
    the cap, unchanged. Where nothing is left, a configuration failure that names the wait it ended
    before (`before`, e.g. "git ls-files answered"): the hook's budget is spent, and the gate says so
    ahead of the platform's cut, which says nothing. The caller asks at the moment it begins to wait."""
    if _declared is None or _declared.deadline is None:
        return cap
    left = _declared.deadline - time.monotonic()
    if left <= 0:
        raise ConfigurationFailure(messages.c12_hook_budget(_declared.identity.hook_seconds, before))
    return min(cap, left)
