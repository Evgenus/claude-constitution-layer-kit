"""Which gate this run is, the name of the dials file it reads, and how long its hook may run.

The shared code serves several plugins, and each hook process runs exactly one of them. The gate
declares itself for the length of one guarded run, through the context manager `declared`: inside its
scope every message, the log and the dials reader ask here for the gate's name and for the name of the
dials file, and outside every scope they ask in vain. The guard opens the scope around everything it does,
with the mode of the run beside the identity, in the same declaration, for the code that behaves
differently in a hook than in a scan or an act: the git calls' budget and the hook's one deadline.

The declaration is held in one context variable of this package, with no default. The variable is the one
module-level name involved, and it holds no declaration of its own: only a scope sets it, and no code
assigns or patches the declaration otherwise. A read of the identity or of the dials file's name outside
every scope is a defect of the caller, a `RuntimeError` and never a repository's failure; there the mode
reads as none and no wait has a deadline. An identity whose dials file is empty, or empty once stripped of
whitespace, names no file: opening a scope with it is the same defect, and the name is otherwise read as
written. A scope
opened inside another shadows the outer declaration until it closes, and the outer one holds again after it:
a second declaration is no defect, whether it differs or not. A gate of another kit names its own dials
file in its identity, and the package reads nothing else.

A hook run has one deadline, `hook_seconds` of the identity from the moment its scope opens, and every wait
of the run takes the smaller of its own cap and what is left of it (`remaining`, and `left_of` for a wait no
verdict depends on); a scan, an act and a scope opened with no mode have no deadline. The handler's timeout
in the plugin's hooks file stays `hook_seconds` and `LEFT_FOR_THE_REST` above it, so that a spent deadline
ends with the gate's own line before the platform cuts the hook.

No state of a gate lives in a module-level name of this package; the output module still switches off a
process-wide flag of `logging`.
"""

from __future__ import annotations

import contextvars
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from . import messages
from .errors import ConfigurationFailure
from .model import Broken, Mode

# The seconds one hook run may take in all, from the opening of its scope: the default of
# `Identity.hook_seconds`, and the handlers' 30 s less `LEFT_FOR_THE_REST`.
HOOK_SECONDS: float = 25
# The seconds a handler's timeout keeps over a hook's budget, for the interpreter's start, which the
# deadline does not count, and for the reads and writes after the last wait.
LEFT_FOR_THE_REST: float = 5


@dataclass(frozen=True, slots=True)
class Identity:
    namespace: str  # the plugin's name: its dials namespace, its name in every message, its log
    gate: str  # the entry point's name, as the log and the usage line show it
    plugin_root: Path  # where the plugin's requirements file lies
    # The name of the dials file the gate reads, relative to the repository's top. No default: a gate that
    # names no file reads none, never some file that a kit happened to name first.
    dials_file: str
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
    # The seconds one hook run of this gate may take in all, from the opening of its scope: every wait of
    # the run takes what is left of them (`remaining`).
    hook_seconds: float = HOOK_SECONDS


@dataclass(frozen=True, slots=True)
class _Declaration:
    identity: Identity
    mode: Mode | None  # None: declared without a mode, as a test runner does — no mode-bound behaviour
    # On the monotonic clock: set in hook mode alone, the moment the scope opened plus `hook_seconds`.
    deadline: float | None = None


# The declaration of the run in progress, in one context variable. No default: a read outside every scope is
# a defect of the caller, never a silent read of some gate that a kit happened to name first.
_declaration: contextvars.ContextVar[_Declaration] = contextvars.ContextVar("declaration")


@contextmanager
def declared(identity: Identity, mode: Mode | None = None) -> Iterator[None]:
    """Declares the gate and the mode of the run for the length of the scope. In hook mode the opening
    also starts the run's one deadline, `identity.hook_seconds` from now; a scan, an act and a scope with no
    mode have none. Closing the scope, normally or by an exception, resets the variable to what it was: a
    scope opened inside another shadows the outer declaration until it closes, and the outer one holds
    again after. An identity whose dials file is empty, or empty once stripped of whitespace, names no file:
    a defect of the entry point, raised as the scope opens, that declares nothing."""
    if not identity.dials_file.strip():
        raise RuntimeError(
            "a process reads one dials file: an empty name is no file, a defect of the entry point"
        )
    deadline = time.monotonic() + identity.hook_seconds if mode is Mode.HOOK else None
    token = _declaration.set(_Declaration(identity, mode, deadline))
    try:
        yield
    finally:
        _declaration.reset(token)


def current() -> Identity:
    """The identity declared by the scope in progress."""
    try:
        return _declaration.get().identity
    except LookupError:  # a defect of the caller, never of the repository
        raise RuntimeError("the entry point did not declare which gate it is") from None


def dials_file() -> str:
    """The name of the dials file the declared identity reads, relative to the repository's top."""
    return current().dials_file


def declared_mode() -> Mode | None:
    """The mode the run was declared in, or None where none was declared, or no scope is open — never a
    failure: a caller that asks for it behaves as it did before there was one."""
    declaration = _declaration.get(None)
    return None if declaration is None else declaration.mode


def remaining(cap: float, before: str) -> float:
    """The seconds a wait of a hook run may take: the smaller of its own `cap` and what is left of the
    run's deadline. Where the run has no deadline — a scan, an act, a scope opened with no mode, or no scope —
    the cap, unchanged. Where nothing is left, a configuration failure that names the wait it ended
    before (`before`, e.g. "git ls-files answered"): the hook's budget is spent, and the gate says so
    ahead of the platform's cut, which says nothing. The caller asks at the moment it begins to wait."""
    declaration = _declaration.get(None)
    if declaration is None or declaration.deadline is None:
        return cap
    left = declaration.deadline - time.monotonic()
    if left <= 0:
        raise ConfigurationFailure(messages.c12_hook_budget(declaration.identity.hook_seconds, before))
    return min(cap, left)


def left_of(cap: float) -> float:
    """The seconds a wait of a hook run may take where no verdict depends on it: the smaller of its own
    `cap` and what is left of the run's deadline, zero where nothing is left, the cap itself where the
    run has no deadline. It never raises: a wait for advice that the deadline cuts ends the advice, and
    the verdict stands. `remaining` serves a wait that a verdict does wait for."""
    declaration = _declaration.get(None)
    if declaration is None or declaration.deadline is None:
        return cap
    return max(min(cap, declaration.deadline - time.monotonic()), 0.0)


def ran_out(given: float, cap: float, before: str, own: Broken) -> ConfigurationFailure:
    """The failure for a wait that ran out of the `given` seconds `remaining` gave it, of its own `cap`. Given
    the whole cap, the wait was slow by itself and `own` is its line. Given less, the run's deadline cut it,
    and the line is the shared C12.14 naming the wait (`before`, as `remaining` was asked): the line `own`
    would print the shortened number as the most the check waits. A scan and an act give the cap."""
    declaration = _declaration.get(None)
    if given < cap and declaration is not None:
        return ConfigurationFailure(messages.c12_hook_budget(declaration.identity.hook_seconds, before))
    return ConfigurationFailure(own)
