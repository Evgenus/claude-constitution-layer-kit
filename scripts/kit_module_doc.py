"""Kit tooling, never shipped in a module: how a kit check reads a section of a module document, and
the scans and the table form of its enforcement section.

A module document (template `MODULE.md`) puts the anchor `<a id="tN"></a>` alone on the line above
the heading of its section N. `section` reads one section by that anchor, so that a heading's number,
its wording or its place never decides what is read, and it fails loud where a read would otherwise
go quietly wrong: an anchor gone, an anchor twice, the next section's anchor gone, or another anchor
standing after it, `DocumentError` with the fix.

Only a line whose stripped form is exactly the anchor counts; the same anchor written inside other
text, as in prose that shows it or on the heading's own line, is plain text and no anchor, so a
document that has it nowhere else lacks the anchor. The section ends at the next such anchor, or at
the end of the file. When the document holds any anchor numbered above the section's, the next one
must be the next number: a section whose end anchor is gone, or out of order, is no section the
check can read, and never runs on into the one after it. The message tells the two apart: the next
number gone from the document, whose fix is to restore it, and the next number standing elsewhere,
with another anchor, or none, after this one, whose fix is to put the sections in the template's
order. A section whose anchor is the highest of the document reads to the end of the file.
`enforcement` reads the section of anchor `t9` for the scans it declares and the problems with its
form, which check-gate-lists reports; check-bare-install uses the scans alone. There is no runner of
its own: each check that reads through it proves it in its own `--self-test`.

`module_folders` is the kit's one listing of its module folders, which every kit check that walks
them reads: the folders directly under `<root>/modules/` whose name opens with neither `.` nor `_`,
sorted by name, a plain file standing there none and a name without `const-` no exception, each
holding its `MODULE.md`. No `modules/` directory, and a folder without its document, are a
`DocumentError` with the fix, never a shorter list: a check that walks the modules would otherwise
pass over the very folder it owes a verdict on. check-gate-lists proves it directly in its own
`--self-test`, every other check through the cases of its own.

`marketplace_name` is the kit's one reader of its marketplace's name, which check-bare-install (the
kit it lives in) and check-install-guide (the guide's clone of the kit) read and type nowhere: the
top-level "name" of `.claude-plugin/marketplace.json`, a non-empty string; the file missing or
unreadable, not JSON, not an object, with no "name", a "name" that is no string, and an empty one are
each a `DocumentError` with the fix. check-install-guide proves it in its `--self-test`, over the
whole set. check-gate-lists reads the file in its own way, for the entries and their lines, and not
through it.

`pinned_claude` and `claude_note` are the kit's one reading of the Claude Code version its two install
checks run on. `pinned_claude` reads `scripts/claude-code.version` of the kit, which the CI workflow
installs from too: one line, a version of three numbers, with at most one final line break; the file
missing or unreadable, empty, or anything else (a carriage return, a byte-order mark, a second line, a
word, a blank line after the version) is a `DocumentError` with the fix. `claude_note` runs
`claude --version` before any other `claude` command of the check, in an empty configuration folder of
its own, and reads the first word of the first line of the output, when the command exits 0:
  the pinned version        the run goes on, the note is empty;
  another readable version  `DocumentError` with the fix, unless the environment's
                            CONSTITUTION_KIT_ANY_CLAUDE is exactly `1` (any other value, an empty one
                            included, is strict): then the run goes on, and the note names both
                            versions, for the check to end every headline line of its report with;
  no readable version       `DocumentError` with the fix, the opt-out notwithstanding: a command that
                            fails, prints nothing, or opens with a word that is no version.
check-install-guide proves `pinned_claude` in its `--self-test`, over the whole set; it and
check-bare-install prove `claude_note` in theirs, over the whole set of answers of `claude --version`.
`claude_note` returns a `Note`: the note as a string, and with it the pinned version and the one found.
`platform_fix` is the kit's one wording of the fix for a platform reply, record or settings file that the
kit's reader does not read, which both checks end such a BROKEN line with; it reads the `Note`, so that the
fix can be followed in either state. On the pinned version (the note empty) it says that version wrote what
the reader does not read, names the script and its function, and tells to update that reader to what the
pinned version writes. Off the pin (the opt-out set) it says the run is on the version found, not the
pinned one, and tells to run it again on the pinned version, put first on PATH as `claude_note`'s own fix
words it. Both checks prove it in theirs, in each state, as literal lines.

`own_packages` is the kit's one derivation of a module's own packages, which the fixture runner
imports through links in `tests/`: each folder at the top of the module's `scripts/`, itself no link,
that holds an `__init__.py`, whose name starts with neither `.` nor `_`, save the shared `const_gate`.
check-shared-links, check-bare-install, check-resolved-paths and list-message-literals read it; the
gate list's `types-<module>` entry derives the same set in shell. check-shared-links proves it in its
`--self-test`.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

ANCHOR = re.compile(r'^<a id="(t\d+)"></a>$')
CLAUDE_PIN = "scripts/claude-code.version"  # the kit's pin of the Claude Code version, from the kit's root
ANY_CLAUDE = "CONSTITUTION_KIT_ANY_CLAUDE"  # the variable that, exactly `1`, lets a check run off the pin
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")  # ASCII digits only: `\d` would take other scripts' digits
PIN_FIX = "write the one version Claude Code's npm package carries, e.g. 2.1.282, as the file's only line"


class Note(str):
    """The note a check ends every headline line of its report with: "" on the pinned version, else
    ` [claude <found>, not the pinned <pinned>: CONSTITUTION_KIT_ANY_CLAUDE=1]`. It is a string, and it
    carries the pinned version and the one found ("" on the pin), which `platform_fix` words a fix from."""

    pinned: str
    found: str

    def __new__(cls, pinned: str, found: str = "") -> Note:
        text = f" [claude {found}, not the pinned {pinned}: {ANY_CLAUDE}=1]" if found else ""
        note = super().__new__(cls, text)
        note.pinned, note.found = pinned, found
        return note


class DocumentError(Exception):
    """A module document, or the folder that holds it, cannot be read; the message says why and how to
    fix it."""


def module_folders(root: Path) -> list[Path]:
    """The module folders of the kit at `root`, sorted by name: each directory directly under
    `modules/` whose name opens with neither `.` nor `_`, and each holds a `MODULE.md` file, else
    `DocumentError` naming the first folder, in sorted order, that lacks it. A caller that needs a
    narrower set filters the list, never lists again."""
    base = root / "modules"
    if not base.is_dir():
        raise DocumentError(
            f"{root} has no modules/ directory — fix: run the check from a checkout of the kit"
        )
    folders = sorted(d for d in base.iterdir() if d.is_dir() and not d.name.startswith((".", "_")))
    for folder in folders:
        if not (folder / "MODULE.md").is_file():
            raise DocumentError(f"modules/{folder.name} has no MODULE.md — fix: restore the module document")
    return folders


def marketplace_name(root: Path) -> str:
    """The name of the marketplace the kit at `root` declares: the top-level "name" of
    `<root>/.claude-plugin/marketplace.json`, which must be a non-empty string, else `DocumentError`
    with the fix. The kit's install checks read the name here and type it nowhere. A caller that
    needs the name of its own kit or of a clone passes that root."""
    path = root / ".claude-plugin" / "marketplace.json"
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError as bad:
        raise DocumentError(
            f"{path} cannot be read ({bad.strerror}) — fix: run the check from a checkout of the kit,"
            " which holds the file"
        ) from bad
    except ValueError as bad:
        raise DocumentError(f"{path} is not JSON ({bad}) — fix: restore the file as a JSON object") from bad
    if not isinstance(document, dict):
        raise DocumentError(
            f'{path} is not a JSON object — fix: restore the file as an object with the marketplace\'s "name"'
        )
    if "name" not in document:
        raise DocumentError(
            f'{path} has no "name" — fix: give the marketplace its name, at the top of the object'
        )
    name = document["name"]
    if not isinstance(name, str):
        raise DocumentError(
            f'{path} gives a "name" that is not a string — fix: write the name as a JSON string'
        )
    if not name:
        raise DocumentError(f'{path} gives an empty "name" — fix: write the marketplace\'s name in it')
    return name


def pinned_claude(root: Path) -> str:
    """The Claude Code version the kit at `root` pins: the text of `<root>/scripts/claude-code.version`,
    with at most one final line break removed, must be exactly one version of three numbers, else
    `DocumentError` with the fix. The file is read as bytes, so that a carriage return or a byte-order
    mark is seen and not translated away."""
    path = root / CLAUDE_PIN
    try:
        text = path.read_bytes().decode("utf-8", errors="replace")
    except OSError as bad:
        raise DocumentError(f"{path} cannot be read ({bad.strerror}) — fix: {PIN_FIX}") from bad
    if not text:
        raise DocumentError(f"{path} is empty — fix: {PIN_FIX}")
    version = text.removesuffix("\n")
    if not VERSION.fullmatch(version):
        raise DocumentError(f"{path} is not one version ({text!r}) — fix: {PIN_FIX}")
    return version


def claude_note(root: Path, env: Mapping[str, str], timeout: float = 60) -> Note:
    """Ask the `claude` on PATH its version, before any other command of the check, and compare it with
    the pin of the kit at `root`. Returns the empty `Note` when it is the pinned version, and the note a
    check ends every headline line of its report with, `[claude <found>, not the pinned <pinned>:
    <variable>=1]`, when it is another readable version and `env` sets CONSTITUTION_KIT_ANY_CLAUDE to
    exactly `1`;
    else `DocumentError` with the fix: the pin unreadable, `claude` missing, another version with the
    variable unset or of another value, or no readable version at all, the variable notwithstanding.
    The version is the first whitespace-separated word of the first line of the output, read when the
    command exits 0 and the word is three numbers; a line break of either kind is white space, and the
    lines after the first are not read. The command runs in `env`, in an empty configuration folder of
    its own and with the auto-updater off, and one that has not answered in `timeout` seconds is no
    version."""
    pinned = pinned_claude(root)
    with tempfile.TemporaryDirectory(prefix="claude-version-") as config:
        asked = dict(env) | {"CLAUDE_CONFIG_DIR": config, "DISABLE_AUTOUPDATER": "1"}
        try:
            done = subprocess.run(
                ["claude", "--version"],
                cwd=root,
                env=asked,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
            )
            code, out, err = done.returncode, done.stdout.strip(), done.stderr.strip()
        except FileNotFoundError as bad:
            raise DocumentError(
                f"claude is not installed ({bad.strerror}) — fix: install it and put it on PATH"
            ) from bad
        except subprocess.TimeoutExpired:
            code, out, err = 124, "", f"timed out after {timeout:g} s"
    words = out.splitlines()[0].split() if out else []
    found = words[0] if code == 0 and words and VERSION.fullmatch(words[0]) else ""
    if not found:
        said = out or err
        last = said.splitlines()[-1] if said else "no output"
        what = f"exited {code}" if code != 0 else "printed no version"
        raise DocumentError(
            f"`claude --version` {what} ({last}) — fix: check that `claude` on PATH is Claude Code"
            " (`command -v claude`), and reinstall it"
        )
    if found == pinned:
        return Note(pinned)
    if env.get(ANY_CLAUDE) == "1":
        return Note(pinned, found)
    raise DocumentError(
        f"claude is {found}, and the kit's install checks read the platform as {pinned} writes it"
        f" ({CLAUDE_PIN}) — fix: {put_first(pinned)}, or set {ANY_CLAUDE}=1 to run on {found} with a note on"
        " every line"
    )


def put_first(pinned: str) -> str:
    """How to run on the pinned version beside one's own `claude`, which stays as it is."""
    return (
        f"put Claude Code {pinned} first on PATH for this run, installed beside your own"
        f" (npm install --prefix <folder> @anthropic-ai/claude-code@{pinned}, then"
        " PATH=<folder>/node_modules/.bin:$PATH)"
    )


def platform_fix(note: Note, script: str, reader: str, wrote: str) -> str:
    """The fix a check ends a BROKEN line with when `reader`, a function of `script`, cannot read what the
    platform wrote (`wrote` says what: "a reply", "a record", "a settings file"), by the state `note`
    records. On the pinned version: that version wrote what the reader does not read, so update the reader
    to what it writes. Off the pin: the run is on the version found, so run it again on the pinned one."""
    if note.found:
        return (
            f" — fix: this run is on {note.found}, not the pinned {note.pinned}: run it again on the pinned"
            f" version, {put_first(note.pinned)}"
        )
    return (
        f" — fix: Claude Code {note.pinned} wrote {wrote} that the kit's reader, `{reader}` in {script},"
        f" does not read: update that reader to what {note.pinned} writes"
    )


def own_packages(module: Path) -> list[Path]:
    """The module's own packages, sorted by name: each folder at the top of `<module>/scripts/`, itself no
    link, that holds an `__init__.py`, whose name starts with neither `.` nor `_`, save `const_gate`. A
    module with no `scripts/` has none."""
    scripts = module / "scripts"
    if not scripts.is_dir():
        return []
    return sorted(
        path
        for path in scripts.iterdir()
        if not path.is_symlink()
        and path.name != "const_gate"
        and not path.name.startswith((".", "_"))
        and (path / "__init__.py").is_file()
    )


def section(text: str, anchor: str, path: str) -> list[tuple[int, str]]:
    """The lines (1-based number, text) after the line of `anchor` up to, not including, the next
    section anchor, or to the end of the text; `path` names the document in a message. When the document
    holds an anchor numbered above this one, the next anchor must be the next number, else
    `DocumentError`: a section never runs on into the next but one."""
    lines = text.splitlines()
    stands: dict[str, list[int]] = {}
    for number, line in enumerate(lines, start=1):
        if (found := ANCHOR.match(line.strip())) is not None:
            stands.setdefault(found[1], []).append(number)
    if anchor not in stands:
        raise DocumentError(
            f'{path} has no anchor <a id="{anchor}"></a> on a line of its own'
            " — fix: restore the template's anchor, alone on its line"
        )
    for name, numbers in stands.items():
        if len(numbers) > 1:
            raise DocumentError(
                f'{path} holds the anchor <a id="{name}"></a> twice, lines {numbers[0]} and {numbers[1]}'
                " — fix: keep the one before its section's heading"
            )
    start = stands[anchor][0]
    later = sorted((number, name) for name, numbers in stands.items() for number in numbers if number > start)
    mine = int(anchor.removeprefix("t"))
    after = f"t{mine + 1}"
    if any(int(name.removeprefix("t")) > mine for name in stands) and (not later or later[0][1] != after):
        if after not in stands:
            raise DocumentError(
                f'{path} has no anchor <a id="{after}"></a> after <a id="{anchor}"></a>'
                " — fix: restore it, alone on its line"
            )
        what = (
            f'the anchor after <a id="{anchor}"></a> is <a id="{later[0][1]}"></a>, not <a id="{after}"></a>'
            if later
            else f'no anchor follows <a id="{anchor}"></a>, and <a id="{after}"></a> stands before it'
        )
        raise DocumentError(
            f"{path}: {what} — fix: put the sections in the template's order, t1 to t12, each anchor"
            " alone on the line above its section's heading"
        )
    end = later[0][0] if later else len(lines) + 1
    return [(number, lines[number - 1]) for number in range(start + 1, end)]


class Fault(StrEnum):
    """What is wrong with a line of the enforcement section."""

    FIRST_CELL = "first cell"  # a table row that opens with anything but `E<n>` or `**E<n>**`
    SPAN = "span"  # a table row's code span that holds `--scan` in a form the check cannot read
    UNMARKED = "unmarked"  # a flag after `--scan` in a cell, the one that holds the span, that lacks the mark
    PROSE = "prose"  # a span in the declared form outside the table


@dataclass(frozen=True)
class Problem:
    line: int  # the line in the document
    fault: Fault
    text: str  # the first cell, or the span


ENTRY = r"[a-z][a-z0-9-]*(?:\.py)?"
DECLARED = re.compile(rf"({ENTRY}) --scan")  # `<entry> --scan` or `<entry>.py --scan`, nothing after
EXPLAIN = re.compile(rf"({ENTRY}) --scan(?: --[a-z][a-z0-9-]*(?: [^\s-]\S*)?)+")  # a flag or more after
HANDLE = re.compile(r"E\d+|\*\*E\d+\*\*")
SPAN = re.compile(r"`([^`]*)`")
SEPARATOR = re.compile(r"\|(?:\s*:?-+:?\s*\|)+")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
MARK = re.compile(r"\bnot a tree scan\b")  # the words that make a flag after `--scan` another mode


def cells(line: str) -> list[str]:
    """The cells of a table line, the bar that opens it and the one that closes it dropped, each cell
    stripped; the last cell is read whether or not the line closes with a bar."""
    parts = CELL_SPLIT.split(line.strip())[1:]
    if parts and not parts[-1]:  # the line closed with a bar: nothing follows it
        parts.pop()
    return [part.strip() for part in parts]


def enforcement(text: str, path: str) -> tuple[list[str], list[Problem]]:
    """The scans a module document declares, sorted, and what is wrong with its enforcement section
    (anchor `t9`): a table line is a line whose stripped form starts with `|`, the separator and the
    header line above it skipped; a row opens with `E<n>` or `**E<n>**`, any other first cell is a problem
    and the row's spans are read all the same; a code span in a row that holds
    `--scan` reads `<entry> --scan`, which declares the scan, or `<entry> --scan --<flag> …` in a row
    where the cell that holds the span, whatever its column, also holds the words `not a tree scan`
    outside any code span, which declares none; any other such span is a problem; a span in the declared form
    stays declared when the mark stands beside it, since the mark only licenses the form with a flag;
    outside the table, a span in the declared form is a problem and any other is ignored."""
    body = section(text, "t9", path)
    headers = {
        number
        for (number, _), (_, below) in zip(body, body[1:], strict=False)
        if SEPARATOR.fullmatch(below.strip())
    }
    scans: set[str] = set()
    problems: list[Problem] = []
    for number, raw in body:
        line = raw.strip()
        if not line.startswith("|"):
            problems += [
                Problem(number, Fault.PROSE, span)
                for span in SPAN.findall(line)
                if DECLARED.fullmatch(span) is not None
            ]
            continue
        if number in headers or SEPARATOR.fullmatch(line):
            continue
        row = cells(line)
        if not row or HANDLE.fullmatch(row[0]) is None:
            problems.append(Problem(number, Fault.FIRST_CELL, row[0] if row else ""))
        for cell in row:
            for span in SPAN.findall(cell):
                if "--scan" not in span:
                    continue
                if (found := DECLARED.fullmatch(span)) is not None:
                    scans.add(found[1])
                elif EXPLAIN.fullmatch(span) is None:
                    problems.append(Problem(number, Fault.SPAN, span))
                elif MARK.search(SPAN.sub("", cell)) is None:
                    problems.append(Problem(number, Fault.UNMARKED, span))
    return sorted(scans), problems
