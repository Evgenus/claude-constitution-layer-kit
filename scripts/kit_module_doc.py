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
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

ANCHOR = re.compile(r'^<a id="(t\d+)"></a>$')


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
