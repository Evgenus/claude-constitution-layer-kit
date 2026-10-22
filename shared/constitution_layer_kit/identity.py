"""Which gate this process is, how long its hook may run, and the name of the dials file it reads.

The shared code serves several plugins, and each hook process runs exactly one of them.
The plugin's entry point declares itself once, before anything is printed; from then on
every message, the log and the dials reader ask here for the name. The guard declares the
mode of the run beside it, in the same declaration, for the code that behaves differently in
a hook than in a scan or an act: the git calls' budget and the hook's one deadline.

A hook run has one deadline, `hook_seconds` of the identity from the moment of the declaration,
and every wait of the run takes the smaller of its own cap and what is left of it (`remaining`, and
`left_of` for a wait no verdict depends on); a scan, an act and a process declared with no mode
have no deadline. The handler's timeout in the plugin's hooks file stays `hook_seconds` and
`LEFT_FOR_THE_REST` above it, so that a spent deadline ends with the gate's own line before the
platform cuts the hook.

The identity is the package's one global of its own; the output module also switches off a process-wide
flag of `logging`.

The name of the dials file the gate reads is the second piece of process state beside the identity,
and it is no global: a context variable of this package with no default. The entry point declares it
once, through `declare_dials_file`, before its run; the dials reader opens that file and every shared
message that names it asks `dials_file` at the moment it is built. As for the identity, a read before
the declaration and a second declaration with another name are defects of the entry point, a
`RuntimeError` and never a repository's failure, and so is an empty name; the same name twice is
harmless. No module-level name holds the file's name and nothing patches one, so a gate of another kit
declares its own file and the package reads nothing else.
"""

from __future__ import annotations

import contextvars
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from . import messages
from .errors import ConfigurationFailure
from .model import Broken, Mode

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
# The name of the dials file, declared once per process. No default: a read before the declaration is a
# defect of the entry point, never a silent read of some file that a kit happened to name first.
_dials_file: contextvars.ContextVar[str] = contextvars.ContextVar("dials_file")


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


def declare_dials_file(name: str) -> None:
    """Declares the name of the dials file the gate reads, once. The same name again is harmless; another
    is a defect, as a second, different identity is, and so is an empty name, or one that is empty once
    stripped of whitespace, which names no file: a defect of the entry point, declared first or second,
    that leaves the process as it was."""
    if not name.strip():
        raise RuntimeError(
            "a process reads one dials file: an empty name is no file, a defect of the entry point"
        )
    try:
        declared = _dials_file.get()
    except LookupError:
        _dials_file.set(name)
        return
    if declared != name:
        raise RuntimeError("a process reads one dials file: a second, different declaration is a defect")


def dials_file() -> str:
    """The name of the dials file the entry point declared, relative to the repository's top."""
    try:
        return _dials_file.get()
    except LookupError:  # a defect of the entry point, never of the repository
        raise RuntimeError("the entry point did not declare which dials file it reads") from None


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


def left_of(cap: float) -> float:
    """The seconds a wait of a hook run may take where no verdict depends on it: the smaller of its own
    `cap` and what is left of the run's deadline, zero where nothing is left, the cap itself where the
    run has no deadline. It never raises: a wait for advice that the deadline cuts ends the advice, and
    the verdict stands. `remaining` serves a wait that a verdict does wait for."""
    if _declared is None or _declared.deadline is None:
        return cap
    return max(min(cap, _declared.deadline - time.monotonic()), 0.0)


def ran_out(given: float, cap: float, before: str, own: Broken) -> ConfigurationFailure:
    """The failure for a wait that ran out of the `given` seconds `remaining` gave it, of its own `cap`. Given
    the whole cap, the wait was slow by itself and `own` is its line. Given less, the run's deadline cut it,
    and the line is the shared C12.14 naming the wait (`before`, as `remaining` was asked): the line `own`
    would print the shortened number as the most the check waits. A scan and an act give the cap."""
    if given < cap and _declared is not None:
        return ConfigurationFailure(messages.c12_hook_budget(_declared.identity.hook_seconds, before))
    return ConfigurationFailure(own)
