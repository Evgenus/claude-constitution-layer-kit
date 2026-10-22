"""The command line, the single guard, and the check of the installed release.

Parameters are parsed with argparse, whose own default is to exit 2 on bad usage; 2 is
reserved for findings, so a misinvoked hook must not read as "blocked, here is the
feedback" having produced no verdict. The parser here raises a configuration failure
instead, and carries no built-in help action: argparse's help prints and exits on its
own, past the guard and the log. The usage is one line, in the misinvocation message.
The guard turns every configuration failure, and every unexpected exception, into
exit 1 — never 0 — and flushes the log however the run ended.

`version_failure` is the check every module's entry file calls right after it imports this module:
whether the installed release serves the module, else the one line to print before it exits 1.
"""

from __future__ import annotations

import argparse
import re
import sys
import traceback
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, TextIO

from . import __version__ as __version__  # re-exported: the installed version `version_failure` compares
from . import identity, messages, preflight
from .errors import ConfigurationFailure
from .identity import Identity
from .model import EXIT_BROKEN, Mode
from .output import Output

SCAN_FLAG = "--scan"

# A version is major.minor.patch, three decimal integers written without a leading zero, and nothing else:
# no prefix, no suffix, no space, no digit of another script (`[0-9]`, where `\d` takes them all).
_VERSION_SHAPE = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")


def _version(text: str, whose: str) -> tuple[int, int, int]:
    found = _VERSION_SHAPE.fullmatch(text)
    if found is None:
        raise ValueError(
            f"{whose} {text!r} is not major.minor.patch: three decimal integers without a leading zero,"
            " and nothing else"
        )
    return int(found[1]), int(found[2]), int(found[3])


def version_failure(namespace: str, required: str, guide: str, until: str) -> str | None:
    """Whether the installed constitution-layer-kit serves a module that requires `required`. None when it
    does: the installed `__version__` is at or above `required` and of the same major. Otherwise the one
    rendered BROKEN line the module's entry file prints, with its closing line, before it exits 1: `C16`
    when the installed version is below `required` — the shared code is too old, a required major above the
    installed one included — and `C17` when the required major is below the installed major — the module is
    too old for that major. `guide` is the path of the module's install note and `until` its closing clause,
    empty for a generator's, which closes with none.

    Both versions are strict major.minor.patch. A malformed `required` raises ValueError: a defect of the
    module, which its fixtures catch. This reads no identity, since none is declared when it runs.

    The signature of this function never changes from the first release on, and no parameter changes its
    meaning. Every module's entry file calls it right after it imports `cli`, before it builds anything,
    on whatever release is installed, one older or newer than the module was written for. A changed
    signature would end that call in an error of its own, and the module would print neither line."""
    needed = _version(required, "the required version")
    installed = _version(__version__, "the installed version")
    if installed < needed:  # a required major above the installed one is below it too
        return messages.c16_shared_too_old(namespace, required, __version__, guide, until).render()
    if needed[0] < installed[0]:
        return messages.c17_module_too_old(namespace, required, __version__, guide, until).render()
    return None


@dataclass(frozen=True, slots=True)
class Argument:
    """A module's own flag on the one parser, scan mode only, one value each: `--since <ref>`."""

    flag: str
    metavar: str


Values = Mapping[str, str | None]  # a module's flags by flag, None where not given


@dataclass(frozen=True, slots=True)
class Modes:
    """The module's two modes. Each returns an exit code. A module with flags of its own gives
    `scan_with`, which receives their values, and `scan` is then not called."""

    hook: Callable[[Output, TextIO], int]
    scan: Callable[[Output, Path], int]
    scan_with: Callable[[Output, Path, Values], int] | None = None


class Parser(argparse.ArgumentParser):
    def __init__(self, usage: str, prog: str) -> None:
        super().__init__(prog=prog, add_help=False, allow_abbrev=False)  # --sc is not --scan
        self.usage_line = usage

    def error(self, message: str) -> NoReturn:
        raise ConfigurationFailure(messages.c12_invocation(message, self.usage_line))


def usage(arguments: Sequence[Argument]) -> str:
    return messages.USAGE + "".join(f" [{a.flag} <{a.metavar}>]" for a in arguments)


def make_parser(arguments: Sequence[Argument] = ()) -> Parser:
    parser = Parser(usage(arguments), identity.current().gate)
    parser.add_argument(SCAN_FLAG, nargs="?", const=".", default=None, metavar="DIR")
    for argument in arguments:
        parser.add_argument(argument.flag, dest=argument.flag, default=None, metavar=argument.metavar)
    return parser


def main(
    argv: Sequence[str],
    output: Output,
    load_modes: Callable[[], Modes],
    arguments: Sequence[Argument] = (),
) -> int:
    parser = make_parser(arguments)
    args = parser.parse_args(list(argv))
    values: dict[str, str | None] = {a.flag: getattr(args, a.flag) for a in arguments}
    if args.scan is None:
        given = [flag for flag, value in values.items() if value is not None]
        if given:
            raise ConfigurationFailure(
                messages.c12_invocation(f"{given[0]} applies to --scan", parser.usage_line)
            )
    preflight.check()
    modes = load_modes()  # the module's code is imported after the preflight: it needs the libraries
    if args.scan is not None:
        if modes.scan_with is not None:
            return modes.scan_with(output, Path(args.scan), values)
        return modes.scan(output, Path(args.scan))
    return modes.hook(output, sys.stdin)


def run(
    argv: Sequence[str],
    gate: Identity,
    load_modes: Callable[[], Modes],
    arguments: Sequence[Argument] = (),
) -> int:
    """A gate's entry: the entry point says which gate this is, how to load its two modes, and
    which flags of its own the scan takes — none for a gate that takes only --scan."""
    mode = Mode.SCAN if any(a.startswith(SCAN_FLAG) for a in argv) else Mode.HOOK
    return guarded(gate, mode, lambda output: main(argv, output, load_modes, arguments))


def guarded(
    gate: Identity,
    mode: Mode,
    body: Callable[[Output], int],
    could_not_run: Callable[[], str] = messages.c11_broken_count,
) -> int:
    """The guard: the one place exit codes are decided for failures. A gate reaches it through
    `run`; a second entry point — a generator with a command line of its own — calls it with its
    own body, which parses its arguments with `Parser`'s kind, runs `preflight.check`, and only
    then imports what needs the declared libraries; a session-start printer does the same, in hook
    mode, with no arguments to parse and a closing line saying the gate's state is not said.
    `could_not_run` is the line that closes a
    failure: a gate's says that nothing was examined, a generator's that nothing was changed. The
    mode is declared with the gate: a hook starts the run's one deadline, `gate.hook_seconds` from this
    declaration, and every wait of the run takes what is left of it, each git call also within its own
    `GIT_SECONDS`; a scan and an act have no deadline and no budget."""
    identity.declare(gate, mode)  # first: every text, the log, the git calls and the deadline ask who and how
    output = Output(mode)
    try:
        return body(output)
    except ConfigurationFailure as failure:
        output.err(failure.broken.render())
        output.err(could_not_run())
    except Exception as exc:  # not fail-open: an unexpected failure exits 1, never 0
        # the BROKEN line first: in hook mode only the first stderr line reaches the user
        output.err(messages.c12_unexpected(f"{type(exc).__name__}: {exc}").render())
        output.err(could_not_run())
        output.err(traceback.format_exc().rstrip())
    finally:
        output.flush()
    return EXIT_BROKEN
