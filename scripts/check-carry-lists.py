#!/usr/bin/env python3
"""Kit check: every decision record names a home for each thing it rules, and every accepted
record has the receipt of its carry audit.

A ruling that is recorded and approved but never written into a current-state document is
lost the day its record stops being read. Whether a sentence really states a rule is judgment,
and a reader decides it — the carry audit. This check holds the two parts of that audit a
script can hold:

  the list     the record's last section is "Carry list"; every ruling item carries a handle,
               **R1.**, **R2.**, …; the list pairs each handle, once, with links, with "history
               only", or with "pending" and a link. A link leads where a rule can live — an active
               document of type current-state, CLAUDE.md, a skill of the kit, a module's or the
               template's own file, a file that is not markdown — a file, never a folder. The rollout
               plan, a research comparison, another record and a README cannot — the root's, where
               rulings were found hiding, and a module's, a page written for a reader, which binds
               nothing and counts as no task-record, whatever envelope it is given.
               "pending" is for intent that is not yet real, and its link leads to the task-record
               that holds the work to come — a plan, never a decision record — where the kernel says
               such intent rides. The entry is never rewritten: once that task-record closes, the
               check says so in a note.
  the receipt  the commit that accepts a record — trailer "Accepted: <record id>" — also carries
               "Carry-Audit: at <commit>; <n> records; <f> findings, <x> fixed, <j> justified";
               the commit named is an ancestor at which the record already existed — a file of
               its id, `<id>.md`, in any folder of that commit's tree, so that a folder moved
               since leaves the old receipts true — n is above zero, x + j = f. The newest
               acceptance of a record is the one that counts, so a wrong receipt is mended by
               accepting again, in the merge commit of a new pull request. A record no commit
               accepts yet awaits its yes: a note, never a finding —
               a gate is not red for waiting on a person. An "Accepted:" id that names no record
               is a note too: deleted since, renumbered or misspelt. A renumbered record is accepted
               again under its new id, in the merge commit of the change that renumbers it.

What it cannot see, and leaves to the reader of the audit: a ruling item the author never gave a
handle; whether the linked text states the rule; whether the audit the receipt names was run.

Records numbered below the threshold were written before the rule and are not examined. The records'
folder and the width of their numbers are read from the `dec` entry of `const-catalogs.catalogs` in
constitution.yaml at the kit root: its territory must be exactly one pattern `<folder>/**`, its width
(absent is 4) a whole number from 1 to 9 that can number the threshold, and the entry stands once. A
dials file, an entry or a folder that cannot be read, a width or a territory that is off, and a file
of `*.md` in that folder that does not have the form `dec-<width digits>-<slug>` — never skipped —
are each a failure to run, with the fix.

Modes:  no arguments            check the lists and the receipts;
        --scope BASE [MODULE]   print the records a closing audit must read for the change since
                                BASE: in full — those the change adds or edits and those the module's
                                decisions section, found by its anchor `t4`, cites; for regression —
                                those that cite a file the change touched;
        --self-test             prove each finding red and the right record green, on throwaway trees:
                                the catalog's folder and width over their whole sets, a stray file,
                                a receipt whose record stood in another folder, the scope in each
                                layout and a decisions section that ends at the next anchor, with
                                that anchor gone a failure to run.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from kit_module_doc import DocumentError, section

try:
    import yaml
except ImportError:
    print("BROKEN: PyYAML is not installed — fix: python3 -m pip install pyyaml")
    print("BROKEN: the check could not run — 0 records examined")
    sys.exit(1)

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2

DIALS = "constitution.yaml"
NAMESPACE = "const-catalogs"  # the dials namespace of the module that numbers the records
PREFIX = "dec"  # the catalog whose items are the decision records (rule 3 of plc-0004)
DEFAULT_WIDTH, MAX_WIDTH = 4, 9  # the catalog module's own: a width is a whole number from 1 to 9
THRESHOLD = 30  # the record that landed this check; earlier records predate the rule
LAST_SECTION = "Carry list"
UNKNOWN_PLACEHOLDER = "%(trailers"  # what a git that does not know a trailer option prints instead
UNGOVERNED_HOMES = (
    "CLAUDE.md",
    ".claude/skills/",
    "modules/",
    "module-template/",
)  # markdown with no `type` that may hold a rule

HEADING = re.compile(r"^## +(.+?)\s*$", re.MULTILINE)
HANDLE = re.compile(r"\*\*R(\d+)\.\*\*")
ENTRY_START = re.compile(r"^\s*(?:\d+\.|-)\s+(.*)$")
ENTRY = re.compile(r"^((?:R\d+)(?:,\s*R\d+)*)\s+—\s+(.*)$", re.DOTALL)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
RECEIPT = re.compile(r"^at ([0-9a-f]{7,40}); (\d+) records?; (\d+) findings?, (\d+) fixed, (\d+) justified$")

WHY_LIST = (
    "a ruling with no declared home in a current-state document is lost when its record stops being read"
)
WHY_RECEIPT = (
    "the carry audit is mandatory before a yes, and a yes that does not name its audit cannot be told "
    "from one without"
)


@dataclass(frozen=True)
class Finding:
    headline: str
    why: str
    fix: str

    def render(self) -> str:
        return f"RED: {self.headline}\n  why: {self.why}\n  fix: {self.fix}"


class CouldNotRun(Exception):
    """The check cannot give a verdict: no git, a shallow clone, no records folder, no readable catalog."""


@dataclass(frozen=True)
class Catalog:
    """Where the records are and how their names are numbered, as the dials file declares."""

    folder: str  # relative to the kit, no slash at either end
    width: int
    # dec-<width digits>-<slug>, the number its one group; ASCII digits only, as the catalog module's own
    # pattern (modules/const-catalogs/scripts/catalogs_gate/model.py, line 79) reads them
    stem: re.Pattern[str]


FOLDER_PATTERN = re.compile(r"/?([^*?\[\]!\\\s]+)/\*\*")  # a territory of one folder, whole


def folder_of(territory: object) -> str | None:
    """The folder of a territory that is exactly one pattern `<folder>/**`; None for any other."""
    if not isinstance(territory, list) or len(territory) != 1 or not isinstance(territory[0], str):
        return None
    found = FOLDER_PATTERN.fullmatch(territory[0])
    if found is None or territory[0].startswith("#"):
        return None
    folder = found.group(1)
    return None if any(part in ("", ".", "..") for part in folder.split("/")) else folder


def width_of(entry: dict[object, object]) -> int | None:
    """The width of a catalog entry, as the catalog module accepts it: absent is the default, else a
    whole number from 1 to the maximum — YAML's true is an int to Python, and no width."""
    value = entry.get("width", DEFAULT_WIDTH)
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if 1 <= value <= MAX_WIDTH else None


def load_catalog(kit: Path) -> Catalog:
    """The `dec` entry of the dials file, and the guard that every markdown file in its folder is numbered."""
    try:
        dials = yaml.safe_load((kit / DIALS).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise CouldNotRun(
            f"{DIALS} cannot be read ({exc}) — fix: restore the dials file at the kit root, "
            "which declares where the records are and how they are numbered"
        ) from exc
    namespace = dials.get(NAMESPACE) if isinstance(dials, dict) else None
    entries = namespace.get("catalogs") if isinstance(namespace, dict) else None
    if not isinstance(entries, list):
        raise CouldNotRun(
            f"{DIALS} has no {NAMESPACE}.catalogs list, so the records' folder and number width cannot "
            f"be read — fix: declare the {PREFIX} catalog under {NAMESPACE}.catalogs"
        )
    if not all(isinstance(entry, dict) for entry in entries):
        raise CouldNotRun(
            f"{NAMESPACE}.catalogs in {DIALS} holds an entry that is no mapping, and the catalog module "
            "refuses the file for it — fix: write each entry as prefix, width and territory"
        )
    mine = [entry for entry in entries if entry.get("prefix") == PREFIX]
    if not mine:
        raise CouldNotRun(
            f"{DIALS} declares no catalog with prefix {PREFIX}, so the records cannot be found — "
            f"fix: add the entry to {NAMESPACE}.catalogs, its territory the records' folder as '<folder>/**'"
        )
    if len(mine) > 1:
        raise CouldNotRun(
            f"{DIALS} declares prefix {PREFIX} twice, and the catalog module refuses it, so which one holds "
            f"the records is not told — fix: keep one {PREFIX} entry in {NAMESPACE}.catalogs"
        )
    width = width_of(mine[0])
    if width is None:
        raise CouldNotRun(
            f"the {PREFIX} catalog in {DIALS} has a width that is not a whole number from 1 to {MAX_WIDTH}, "
            "so this check cannot number the records — "
            f"fix: set width to the digits of the records' names, or leave it out for {DEFAULT_WIDTH}"
        )
    if 10**width - 1 < THRESHOLD:
        raise CouldNotRun(
            f"the {PREFIX} catalog in {DIALS} has width {width}, which cannot number a record at "
            f"{THRESHOLD}, the first this check examines, so it would examine nothing — "
            f"fix: set width to at least {len(str(THRESHOLD))}, the digits of the records' names"
        )
    folder = folder_of(mine[0].get("territory"))
    if folder is None:
        raise CouldNotRun(
            f"the {PREFIX} catalog in {DIALS} has no single territory '<folder>/**', so this check cannot "
            "tell where the records are — "
            "fix: give it one territory pattern of that form, a folder with no glob character in it"
        )
    catalog = Catalog(folder, width, re.compile(rf"^{PREFIX}-([0-9]{{{width}}})-[a-z0-9-]+$"))
    if not (kit / folder).is_dir():
        raise CouldNotRun(
            f"{kit} has no {folder}/ directory, the folder the {PREFIX} catalog of {DIALS} declares — "
            f"fix: correct the {PREFIX} catalog's territory in {DIALS}, or restore the folder"
        )
    strays = sorted(path.name for path in (kit / folder).glob("*.md") if not catalog.stem.match(path.stem))
    if strays:
        raise CouldNotRun(
            f"{folder}/{strays[0]} does not have the form {PREFIX}-<{width} digits>-<slug> the {PREFIX} "
            "catalog declares, and a file this check cannot number it cannot examine — "
            f"fix: make the catalog's width in {DIALS} and the records' names agree"
        )
    return catalog


def gated_records(kit: Path, catalog: Catalog) -> list[Path]:
    records = []
    for path in sorted((kit / catalog.folder).glob("*.md")):
        match = catalog.stem.match(path.stem)
        if match and int(match.group(1)) >= THRESHOLD:
            records.append(path)
    return records


def split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    try:
        loaded = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return {}, text[end + 5 :]
    return (loaded if isinstance(loaded, dict) else {}), text[end + 5 :]


# ---------------------------------------------------------------------------------------------
# the list
# ---------------------------------------------------------------------------------------------


CARRY_IT = (
    "write the rule into a current-state document and link that; a plan, a comparison, another record and "
    'a README state no rule — intent that is not yet real is "pending" with a link to its task-record'
)
PEND_IT = "link the step of the task-record that holds the intent — the plan, never a decision record"


def home_problem(
    kit: Path, catalog: Catalog, record: Path, target: str, pending: bool = False
) -> tuple[str, str] | None:
    """Why this link may not be the home of a rule — of pending intent — and the fix; None when it may."""
    general = PEND_IT if pending else CARRY_IT
    if re.match(r"^[a-z][a-z0-9+.-]*:", target):
        return f"{target} is outside the repository", general
    path = (record.parent / target.split("#", 1)[0]).resolve()
    try:
        shown = path.relative_to(kit).as_posix()
    except ValueError:
        return f"{target} leads outside the repository", general
    if not path.exists():
        mend = (
            "correct the path to the task-record"
            if pending
            else "correct the path, or link the file that states it now"
        )
        return f"{shown} does not exist", mend
    if not path.is_file():
        return (
            f"{shown} is a directory, and a rule is stated in a file",
            PEND_IT if pending else "link the file in it that states the item",
        )
    if re.fullmatch(r"modules/[^/]+/README\.md", shown):
        if pending:
            return (
                f"{shown} is a module's README, a page written for a reader, which counts as no"
                " task-record, whatever its envelope",
                general,
            )
        return f"{shown} is a module's README, a page written for a reader, and it binds nothing", general
    envelope, _ = split_frontmatter(path.read_text(encoding="utf-8")) if path.suffix == ".md" else ({}, "")
    kind = envelope.get("type")
    if pending:
        if kind == "task-record" and not shown.startswith(catalog.folder + "/"):
            return None
        return (
            f"{shown} is no task-record outside the records' folder, and pending intent rides only in one",
            general,
        )
    if path.suffix != ".md":
        return None
    if kind is None:
        if shown == UNGOVERNED_HOMES[0] or shown.startswith(UNGOVERNED_HOMES[1:]):
            return None
        return f"{shown} is not a governed document and holds no rules", general
    if kind != "current-state":
        return f"{shown} is `{kind}`, and only a `current-state` document states a rule that binds", general
    if envelope.get("status") != "active":
        return (
            f"{shown} is not `active`, and a document that is not in force binds nothing",
            "link the document now in force that states the item",
        )
    return None


def closed_task(kit: Path, record: Path, target: str) -> str | None:
    """The task-record a pending link leads to, when it has closed since."""
    path = (record.parent / target.split("#", 1)[0]).resolve()
    envelope, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    return None if envelope.get("status") == "active" else path.relative_to(kit).as_posix()


def carry_entries(body: str) -> list[str]:
    entries: list[str] = []
    for line in body.splitlines():
        start = ENTRY_START.match(line)
        if start:
            entries.append(start.group(1).strip())
        elif entries and line.strip():
            entries[-1] += " " + line.strip()
    return entries


def check_list(kit: Path, catalog: Catalog, record: Path) -> tuple[list[Finding], list[str]]:
    shown = record.relative_to(kit).as_posix()
    _, text = split_frontmatter(record.read_text(encoding="utf-8"))
    headings = list(HEADING.finditer(text))
    if not headings or headings[-1].group(1) != LAST_SECTION:
        return [
            Finding(
                f'{shown}: the last section is not "{LAST_SECTION}"',
                WHY_LIST,
                f'close the record with "## {LAST_SECTION}": one entry per ruling item, '
                '"R1 — [document](path#anchor), rule 2" or "R3 — history only: a one-time act"',
            )
        ], []
    ruled, listed = text[: headings[-1].start()], text[headings[-1].end() :]
    handles = [f"R{n}" for n in HANDLE.findall(ruled)]
    findings: list[Finding] = []
    notes: list[str] = []
    if not handles:
        findings.append(
            Finding(
                f"{shown}: no ruling item carries a handle",
                WHY_LIST,
                "open every ruling item with a bold handle — **R1.**, **R2.** — a deferred trigger, "
                "a fallback and an exception are items too",
            )
        )
    for handle in sorted({h for h in handles if handles.count(h) > 1}):
        findings.append(
            Finding(f"{shown}: handle {handle} opens two ruling items", WHY_LIST, "renumber one of them")
        )
    seen: dict[str, int] = {}
    for entry in carry_entries(listed):
        parsed = ENTRY.match(entry)
        if not parsed:
            findings.append(
                Finding(
                    f'{shown}: the carry-list entry "{entry[:60]}" does not open with its handles',
                    WHY_LIST,
                    'write it as "R1 — …" or "R1, R2 — …", with an em dash',
                )
            )
            continue
        for handle in re.findall(r"R\d+", parsed.group(1)):
            seen[handle] = seen.get(handle, 0) + 1
            if handle not in handles:
                findings.append(
                    Finding(
                        f"{shown}: the carry list names {handle}, which opens no ruling item",
                        WHY_LIST,
                        f"remove {handle} from the list, or give the item it means its handle",
                    )
                )
        home = parsed.group(2).strip()
        if home.lower().startswith("history only"):
            continue
        pending = home.lower().startswith("pending")
        targets = LINK.findall(home)
        if not targets:
            findings.append(
                Finding(
                    f"{shown}: {parsed.group(1)} names no home",
                    WHY_LIST,
                    PEND_IT
                    if pending
                    else 'link the current-state text that states it, or write "history only" when the item '
                    "binds nothing",
                )
            )
        for target in targets:
            problem = home_problem(kit, catalog, record, target, pending)
            if problem:
                where = "is pending nowhere" if pending else "is carried nowhere that binds"
                findings.append(
                    Finding(f"{shown}: {parsed.group(1)} {where} — {problem[0]}", WHY_LIST, problem[1])
                )
            elif pending and (closed := closed_task(kit, record, target)):
                notes.append(
                    f"NOTE: {record.stem}: {parsed.group(1)} was pending in {closed}, no longer active — "
                    "its close should have carried the intent into the current-state documents, and an "
                    "audit in full checks that"
                )
    for handle in dict.fromkeys(handles):
        if seen.get(handle, 0) == 0:
            findings.append(
                Finding(
                    f"{shown}: {handle} is missing from the carry list",
                    WHY_LIST,
                    f'add "{handle} — …" with the text that now states it, or "history only"',
                )
            )
        elif seen[handle] > 1:
            findings.append(
                Finding(
                    f"{shown}: {handle} is listed {seen[handle]} times", WHY_LIST, "keep one entry for it"
                )
            )
    return findings, notes


# ---------------------------------------------------------------------------------------------
# the receipt
# ---------------------------------------------------------------------------------------------


def git(kit: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(["git", "-C", str(kit), *args], capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise CouldNotRun("git is not installed — fix: install git and rerun") from exc


@dataclass(frozen=True)
class Acceptance:
    commit: str
    accepted: list[str]
    receipts: list[str]


def acceptances(kit: Path) -> list[Acceptance]:
    if git(kit, "rev-parse", "--git-dir").returncode != 0:
        raise CouldNotRun(f"{kit} is not a git repository — fix: run the script from a checkout of the kit")
    if git(kit, "rev-parse", "--is-shallow-repository").stdout.strip() == "true":
        raise CouldNotRun(
            "the clone is shallow, so acceptance commits may be out of reach — fix: git fetch --unshallow"
        )
    if git(kit, "rev-parse", "--verify", "-q", "HEAD").returncode != 0:
        return []
    form = (
        "%H%x00%(trailers:key=Accepted,valueonly,separator=%x1f)"
        "%x00%(trailers:key=Carry-Audit,valueonly,separator=%x1f)%x01"
    )
    # no signature lines: with log.showSignature=true git prints the check before the formatted line,
    # and the first field, the commit, would hold it
    log = git(kit, "-c", "log.showSignature=false", "log", "--topo-order", f"--format={form}")
    if log.returncode != 0:
        raise CouldNotRun(
            f"git log failed: {log.stderr.strip()} — fix: run the script from a checkout of the kit"
        )
    found = []
    for chunk in log.stdout.split("\x01"):
        parts = chunk.strip("\n").split("\x00")
        if len(parts) == 3 and any(field.startswith(UNKNOWN_PLACEHOLDER) for field in parts[1:]):
            # a git too old for the trailer options prints each placeholder as text, at the start
            # of the second and third fields; a trailer value that merely quotes it does not begin so
            version = git(kit, "version")
            lines = (version.stdout if version.returncode == 0 else version.stderr).strip().splitlines()
            said = lines[0] if lines else ""
            raise CouldNotRun(
                "git does not know the trailer options this check reads (key, valueonly, separator): "
                + (said if version.returncode == 0 else f"git version failed: {said}")
                + " — fix: install a newer git (https://git-scm.com/downloads)"
            )
        if len(parts) != 3 or not parts[1].strip():
            continue
        ids = [i.strip() for value in parts[1].split("\x1f") for i in value.split(",") if i.strip()]
        receipts = [r.strip() for r in parts[2].split("\x1f") if r.strip()]
        found.append(Acceptance(parts[0], ids, receipts))
    return found


RECEIPT_FORM = "Carry-Audit: at <commit>; <n> records; <f> findings, <x> fixed, <j> justified"
AGAIN = (
    " — then accept again in the merge commit of a new pull request, never by rewriting history: "
    "the newest acceptance counts"
)


def files_at(kit: Path, listings: dict[str, set[str]], commit: str) -> set[str]:
    """The file names of every folder of a commit's tree, read once per commit."""
    if commit not in listings:
        listed = git(kit, "ls-tree", "-r", "--name-only", f"{commit}^{{commit}}")
        names = listed.stdout.splitlines() if listed.returncode == 0 else []
        listings[commit] = {Path(name).name for name in names}
    return listings[commit]


def check_receipt(
    kit: Path, listings: dict[str, set[str]], record_id: str, acceptance: Acceptance
) -> list[Finding]:
    where = f"commit {acceptance.commit[:7]} accepts {record_id}"
    if not acceptance.receipts:
        return [
            Finding(
                f"{where} and names no carry audit",
                WHY_RECEIPT,
                "run the audit, then accept again in the merge commit of a new pull request, "
                "carrying both trailers — "
                f'"Accepted: {record_id}" and "{RECEIPT_FORM}" — never by rewriting history: the newest '
                "acceptance counts",
            )
        ]
    findings = []
    for receipt in acceptance.receipts:
        parsed = RECEIPT.match(receipt)
        if not parsed:
            findings.append(
                Finding(
                    f'{where} with a receipt that cannot be read: "{receipt}"',
                    WHY_RECEIPT,
                    f'write it as "{RECEIPT_FORM}"' + AGAIN,
                )
            )
            continue
        at, records, found, fixed, justified = parsed.group(1), *map(int, parsed.groups()[1:])
        if records == 0:
            findings.append(
                Finding(
                    f"{where} on an audit that read 0 records",
                    WHY_RECEIPT,
                    "an audit reads at least the record it accepts; run it" + AGAIN,
                )
            )
        if fixed + justified != found:
            findings.append(
                Finding(
                    f"{where}: {found} findings, of which {fixed} fixed and {justified} justified — "
                    f"{found - fixed - justified} unaccounted for",
                    WHY_RECEIPT,
                    "every finding is fixed or justified before the yes; account for each" + AGAIN,
                )
            )
        if git(kit, "merge-base", "--is-ancestor", f"{at}^{{commit}}", acceptance.commit).returncode != 0:
            findings.append(
                Finding(
                    f"{where} on an audit at {at}, which is not a commit before it",
                    WHY_RECEIPT,
                    "name the commit the readers were pinned to; it is in the history the acceptance "
                    "stands on" + AGAIN,
                )
            )
        elif f"{record_id}.md" not in files_at(kit, listings, at):
            findings.append(
                Finding(
                    f"{where} on an audit at {at}, where the record did not exist yet",
                    WHY_RECEIPT,
                    "an audit reads the record it accepts: commit the record, pin the readers to that commit "
                    "or a later one, and name it" + AGAIN,
                )
            )
    return findings


# ---------------------------------------------------------------------------------------------
# verdict
# ---------------------------------------------------------------------------------------------


def check_kit(kit: Path) -> tuple[list[Finding], list[str], int]:
    catalog = load_catalog(kit)
    records = gated_records(kit, catalog)
    findings: list[Finding] = []
    notes: list[str] = []
    for record in records:
        found, noted = check_list(kit, catalog, record)
        findings.extend(found)
        notes.extend(noted)
    accepted = acceptances(kit) if records else []
    listings: dict[str, set[str]] = {}  # the files of each audit commit, read once, whatever the folder then
    for record in records:
        mine = [
            a for a in accepted if record.stem in a.accepted
        ]  # --topo-order: a commit comes before its ancestors
        if not mine:
            notes.append(f'NOTE: {record.stem} awaits its yes — no commit carries "Accepted: {record.stem}"')
        else:
            findings.extend(check_receipt(kit, listings, record.stem, mine[0]))
    present = {path.stem for path in (kit / catalog.folder).glob("*.md")}
    for acceptance in accepted:
        for stem in acceptance.accepted:
            if stem not in present:
                notes.append(
                    f"NOTE: commit {acceptance.commit[:7]} accepts {stem}, which is no record here — "
                    "deleted since, renumbered or misspelt; when renumbered, accept it again under its "
                    "new id in the merge commit of the change that renumbers it; when misspelt, accept "
                    "again in the merge commit of a new pull request, the id spelt right"
                )
    return findings, notes, len(records)


def report(findings: list[Finding], notes: list[str], records: int) -> int:
    counts = f"{records} record(s) numbered {THRESHOLD:04d} or above examined"
    for note in notes:
        print(note)
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(f"GREEN: every ruling item names its home, every acceptance names its audit — {counts}")
    return EXIT_GREEN


# ---------------------------------------------------------------------------------------------
# scope of a closing audit
# ---------------------------------------------------------------------------------------------


def cited_files(kit: Path, document: Path, text: str) -> set[str]:
    cited = set()
    for target in LINK.findall(text):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target):
            continue
        path = (document.parent / target.split("#", 1)[0]).resolve()
        if path.is_relative_to(kit):
            cited.add(path.relative_to(kit).as_posix())
    return cited


def compute_scope(kit: Path, base: str, module: str | None) -> tuple[dict[str, str], dict[str, list[str]]]:
    """The records a closing audit reads in full, each with the reason, and those it reads for regression;
    a module's decisions section is the one under its anchor `t4`, and a document without it, with it
    twice, or without its end anchor `t5` while a later one stands, is a failure to run."""
    catalog = load_catalog(kit)
    if git(kit, "rev-parse", "--verify", "-q", f"{base}^{{commit}}").returncode != 0:
        raise CouldNotRun(f"{base} names no commit — fix: pass the commit the change started from")

    def names(*args: str) -> set[str]:
        return set(git(kit, *args).stdout.split())

    in_records = ("--", catalog.folder)
    added = names("diff", "--name-only", "--diff-filter=A", "--no-renames", base, *in_records)
    added |= names("ls-files", "--others", "--exclude-standard", *in_records)
    edited = names("diff", "--name-only", "--diff-filter=M", "--no-renames", base, *in_records)
    touched = names("diff", "--name-only", "--no-renames", base) | names(
        "ls-files", "--others", "--exclude-standard"
    )
    touched = {t for t in touched if not t.startswith(catalog.folder + "/")}
    full = {Path(p).stem: "edited" for p in edited if catalog.stem.match(Path(p).stem)}
    full |= {Path(p).stem: "added" for p in added if catalog.stem.match(Path(p).stem)}
    if module:
        document = kit / "modules" / module / "MODULE.md"
        if not document.is_file():
            raise CouldNotRun(
                f"modules/{module}/MODULE.md does not exist, so the records it cites cannot be read — "
                "fix: name a module under modules/"
            )
        try:
            decisions = section(document.read_text(encoding="utf-8"), "t4", f"modules/{module}/MODULE.md")
        except DocumentError as bad:
            raise CouldNotRun(str(bad)) from bad
        for cited in cited_files(kit, document, "\n".join(line for _, line in decisions)):
            if cited.startswith(catalog.folder + "/"):
                full.setdefault(Path(cited).stem, "cited")
    regression: dict[str, list[str]] = {}
    for record in sorted((kit / catalog.folder).glob("*.md")):
        if record.stem in full or not catalog.stem.match(record.stem):
            continue
        hits = sorted(cited_files(kit, record, record.read_text(encoding="utf-8")) & touched)
        if hits:
            regression[record.stem] = hits
    return full, regression


def scope(kit: Path, base: str, module: str | None) -> int:
    full, regression = compute_scope(kit, base, module)
    for stem in sorted(full):
        print(f"full        {stem}  — {full[stem]}")
    for stem, hits in regression.items():
        print(f"regression  {stem}  — cites {', '.join(hits)}")
    print(f"SCOPE: {len(full)} record(s) in full, {len(regression)} for regression, since {base}")
    return EXIT_GREEN


# ---------------------------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Layout:
    """Where a sample kit keeps its records and how it numbers them, as its dials file says."""

    folder: str = "docs/decisions"
    width: int = 4

    @property
    def sample(self) -> str:
        # built, so that no file names a record that does not exist
        return f"dec-{THRESHOLD + 1:0{self.width}d}-sample"

    def dials(self) -> str:
        return dials_file(f"{self.width}", f'["{self.folder}/**"]')


def dials_file(width: str | None, territory: str, *, entries: int = 1) -> str:
    """A dials file with `entries` catalog entries of prefix dec; width and territory are YAML as written,
    and a width of None is left out."""
    entry = "    - prefix: dec\n" + ("" if width is None else f"      width: {width}\n")
    return "const-catalogs:\n  catalogs:\n" + (entry + f"      territory: {territory}\n") * entries


DEFAULT_LAYOUT = Layout()
SAMPLE = DEFAULT_LAYOUT.sample
GOOD_RECORD = f"""---
id: {SAMPLE}
type: task-record
title: A sample
status: inactive
stakes: process
decider: someone
---

# A sample

## Ruling

1. **R1.** A rule that binds.
2. **R2.** A one-time act.
3. **R3.** Something to be done in a later phase.

## Carry list

1. R1 — [policy](../policies/p.md), rule 1.
2. R2 — history only: done on the day.
3. R3 — pending: [the plan](../plan.md), step 4.
"""


def sample_kit(root: Path, record: str = GOOD_RECORD, layout: Layout = DEFAULT_LAYOUT) -> Path:
    for folder in (
        layout.folder,
        "docs/policies",
        "docs/research",
        ".claude/skills/s",
        "modules/m",
        "modules/n",
        "modules/p",
        "scripts",
    ):
        (root / folder).mkdir(parents=True, exist_ok=True)
    envelopes = {
        "docs/policies/p.md": "id: p\ntype: current-state\nstatus: active",
        "docs/policies/old.md": "id: old\ntype: current-state\nstatus: inactive",
        "docs/plan.md": "id: plan\ntype: task-record\nstatus: active",
        "docs/done.md": "id: done\ntype: task-record\nstatus: inactive",
        "docs/research/r.md": "id: r\ntype: non-authoritative\nstatus: active",
        ".claude/skills/s/SKILL.md": "name: s\ndescription: a skill of the kit",
        "modules/n/README.md": "id: n\ntype: current-state\nstatus: active",
        "modules/p/README.md": "id: p-page\ntype: task-record\nstatus: active",
    }
    for name, envelope in envelopes.items():
        (root / name).write_text(f"---\n{envelope}\n---\n", encoding="utf-8")
    for name in ("README.md", "CLAUDE.md", "modules/m/INSTALL.md", "modules/m/README.md", "scripts/x.py"):
        (root / name).write_text("text\n", encoding="utf-8")
    (root / DIALS).write_text(layout.dials(), encoding="utf-8")
    path = root / layout.folder / f"{layout.sample}.md"
    path.write_text(record, encoding="utf-8")
    return path


def commit(root: Path, message: str) -> str:
    who = (
        "-c",
        "user.name=self-test",
        "-c",
        "user.email=self-test@example.invalid",
        "-c",
        "commit.gpgsign=false",
    )
    git(root, "add", "-A")
    done = git(root, *who, "commit", "-q", "--allow-empty", "-m", message)
    if done.returncode != 0:
        raise CouldNotRun(
            f"git commit failed in the self-test: {done.stderr.strip()} — fix: check the git installation"
        )
    return git(root, "rev-parse", "HEAD").stdout.strip()


def fake_signer(root: Path, tools: Path) -> Path:
    """Signs later `git merge -S` of the repository through a fake `gpg.program` and turns
    `log.showSignature` on; the fake logs each call to the returned file and, to verify, says its human
    text on stderr as gpg does, which git log prints before the formatted line."""
    log = tools / "gpg.log"
    program = tools / "gpg"
    program.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$*\" >> {shlex.quote(str(log))}\n"
        "cat > /dev/null\n"
        'case "$*" in\n'
        "  *--verify*)\n"
        "    printf 'gpg: Good signature from \"fake signer\"\\n' >&2\n"
        "    printf '[GNUPG:] GOODSIG 0123456789ABCDEF fake signer\\n'\n"
        "    printf '[GNUPG:] VALIDSIG 0123456789ABCDEF 2026-10-06 1 0 4 0 1 8 00 0123456789ABCDEF\\n';;\n"
        "  *)\n"
        "    printf '[GNUPG:] SIG_CREATED D 1 8 00 1 0123456789ABCDEF 1\\n' >&2\n"
        "    printf -- '-----BEGIN PGP SIGNATURE-----\\n\\nZmFrZQ==\\n-----END PGP SIGNATURE-----\\n';;\n"
        "esac\n",
        encoding="utf-8",
    )
    program.chmod(0o755)
    for key, value in (
        ("gpg.format", "openpgp"),
        ("gpg.program", str(program)),
        ("user.signingkey", "FIXTURE"),
        ("log.showSignature", "true"),
    ):
        if git(root, "config", key, value).returncode != 0:
            raise CouldNotRun(f"git config {key} failed in the self-test — fix: check the git installation")
    return log


def signed_merge(root: Path, message: str) -> None:
    """A merge commit signed through the fake, as the forge signs the merge of a pull request."""
    who = ("-c", "user.name=self-test", "-c", "user.email=self-test@example.invalid")
    git(root, "checkout", "-q", "-b", "side")
    commit(root, "the side of the merge")
    git(root, "checkout", "-q", "-")
    done = git(root, *who, "merge", "--no-ff", "-S", "-m", message, "side")
    if done.returncode != 0:
        raise CouldNotRun(
            f"git merge -S failed in the self-test: {done.stderr.strip()} — fix: check the git installation"
        )


def fake_old_git(tools: Path, real: str) -> Path:
    """A git first on PATH that logs each call's arguments, as it hands them on, to the returned file and
    gives every `%(trailers:` an option no git knows, as a git of before the options does not know its own:
    the real git then prints the placeholder as text, with exit 0."""
    log = tools / "git.log"
    script = tools / "git"
    script.write_text(
        "#!/bin/sh\n"
        'for a in "$@"; do\n'
        "  shift\n"
        '  case "$a" in\n'
        "    *'%(trailers:'*) a=$(printf '%s' \"$a\" | sed 's/%(trailers:/%(trailers:nosuchopt,/g');;\n"
        "  esac\n"
        '  set -- "$@" "$a"\n'
        "done\n"
        f"printf '%s\\n' \"$*\" >> {shlex.quote(str(log))}\n"
        f'exec {shlex.quote(real)} "$@"\n',
        encoding="utf-8",
    )
    script.chmod(0o755)
    return log


def fake_logging_git(tools: Path, real: str) -> Path:
    """A git first on PATH that logs each call's arguments, as it hands them on, to the returned file and
    runs the real git unchanged."""
    log = tools / "git.log"
    script = tools / "git"
    script.write_text(
        f'#!/bin/sh\nprintf \'%s\\n\' "$*" >> {shlex.quote(str(log))}\nexec {shlex.quote(real)} "$@"\n',
        encoding="utf-8",
    )
    script.chmod(0o755)
    return log


@contextlib.contextmanager
def listed_in_reverse() -> Iterator[None]:
    """For the cases inside, `Path.glob` yields what it finds sorted by name and reversed, whatever the
    filesystem lists: a case that holds an order is then red on every filesystem for a check that does not
    sort, never by the chance of a listing that happens to be unsorted. Restored on leaving."""
    real = Path.glob

    def reversed_glob(self: Path, pattern: str) -> Iterator[Path]:
        return iter(sorted(real(self, pattern), key=lambda path: path.name, reverse=True))

    Path.glob = reversed_glob  # type: ignore[method-assign,assignment]
    try:
        yield
    finally:
        Path.glob = real  # type: ignore[method-assign]


def lists(root: Path, record: Path) -> tuple[list[Finding], list[str]]:
    return check_list(root, load_catalog(root), record)


def self_test() -> int:
    folder = DEFAULT_LAYOUT.folder
    home = "../policies/p.md"
    wrong_lists: dict[str, Callable[[str], str]] = {
        "no carry list": lambda t: t[: t.index("## Carry list")],
        "a carry list that is not the last section": lambda t: t + "\n## After\n\ntext\n",
        "no handles": lambda t: re.sub(r"\*\*R\d\.\*\* |(?<=\d\. )R\d — ", "", t),
        "a handle missing from the list": lambda t: t.replace("2. R2 — history only: done on the day.\n", ""),
        "a handle listed twice": lambda t: t + "4. R1 — history only.\n",
        "an unknown handle in the list": lambda t: t + "4. R9 — history only.\n",
        "a handle opening two items": lambda t: t.replace("**R2.**", "**R1.**").replace(
            "2. R2 — history only: done on the day.\n", ""
        ),
        "an entry with no home": lambda t: t.replace(f"[policy]({home}), rule 1.", "the policy, rule 1."),
        "a home in a research comparison": lambda t: t.replace(home, "../research/r.md"),
        "a home in another record": lambda t: t.replace(home, f"{SAMPLE}.md"),
        "a home in the README": lambda t: t.replace(home, "../../README.md"),
        "a home in a module's README": lambda t: t.replace(home, "../../modules/m/README.md"),
        "a home in a module's README given an envelope": lambda t: t.replace(
            home, "../../modules/n/README.md"
        ),
        "pending intent in a module's README given a task-record envelope": lambda t: t.replace(
            "(../plan.md)", "(../../modules/p/README.md)"
        ),
        "a home in a document that is not in force": lambda t: t.replace(home, "../policies/old.md"),
        "a folder as a home": lambda t: t.replace(home, "../../scripts"),
        "a home that does not exist": lambda t: t.replace(home, "../policies/none.md"),
        "a home outside the repository": lambda t: t.replace(home, "https://example.invalid/p"),
        "pending intent in another record": lambda t: t.replace("(../plan.md)", f"({SAMPLE}.md)"),
        "pending intent in a current-state document": lambda t: t.replace("(../plan.md)", f"({home})"),
        "a rule carried into the active plan": lambda t: t.replace(home, "../plan.md"),
    }
    right_homes = {
        "CLAUDE.md": "../../CLAUDE.md",
        "a skill of the kit": "../../.claude/skills/s/SKILL.md",
        "a module's own file": "../../modules/m/INSTALL.md",
        "a file that is not markdown": "../../scripts/x.py",
    }
    failed = 0
    for name, damage in wrong_lists.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            record = sample_kit(root)
            green_before = not lists(root, record)[0]
            record.write_text(damage(GOOD_RECORD), encoding="utf-8")
            red_after = bool(lists(root, record)[0])
        ok = green_before and red_after
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the right list is green, {name} is red")
    readme_texts = {  # case: the damage, the headline's end and the fix, typed by hand
        "a module's README refused as a home teaches CARRY_IT": (
            wrong_lists["a home in a module's README given an envelope"],
            "modules/n/README.md is a module's README, a page written for a reader, and it binds nothing",
            CARRY_IT,
        ),
        "a module's README refused as a pending link teaches PEND_IT": (
            wrong_lists["pending intent in a module's README given a task-record envelope"],
            "modules/p/README.md is a module's README, a page written for a reader, which counts as no"
            " task-record, whatever its envelope",
            PEND_IT,
        ),
    }
    for name, (damage, ending, fix) in readme_texts.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            found = lists(root, sample_kit(root, damage(GOOD_RECORD)))[0]
        ok = len(found) == 1 and found[0].headline.endswith(ending) and found[0].fix == fix
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        found, noted = lists(root, sample_kit(root, GOOD_RECORD.replace("(../plan.md)", "(../done.md)")))
    ok = not found and len(noted) == 1
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] pending intent in a task-record that has closed is green, with a note")
    for name, target in right_homes.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            ok = not lists(root, sample_kit(root, GOOD_RECORD.replace(home, target)))[0]
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] a home in {name} is green")

    accept = f"Accepted: {SAMPLE}"
    stranger = f"dec-{THRESHOLD + 69:04d}-no-such-record"
    right = "yes\n\n" + accept + "\nCarry-Audit: at {at}; 3 records; 2 findings, 1 fixed, 1 justified\n"
    bare = f"yes\n\n{accept}\n"
    # name -> (the commit messages after the record lands, red wanted, notes wanted)
    receipts: dict[str, tuple[list[str], bool, int]] = {
        "the right receipt is green": ([right], False, 0),
        "an acceptance with no receipt is red": ([bare], True, 0),
        "a receipt that cannot be read is red": ([bare + "Carry-Audit: done, all fine\n"], True, 0),
        "an audit of 0 records is red": (
            [bare + "Carry-Audit: at {at}; 0 records; 0 findings, 0 fixed, 0 justified\n"],
            True,
            0,
        ),
        "findings unaccounted for are red": (
            [bare + "Carry-Audit: at {at}; 3 records; 5 findings, 2 fixed, 1 justified\n"],
            True,
            0,
        ),
        "an audit at no commit is red": (
            [bare + "Carry-Audit: at " + "0" * 40 + "; 3 records; 0 findings, 0 fixed, 0 justified\n"],
            True,
            0,
        ),
        "an audit pinned before the record existed is red": (
            [bare + "Carry-Audit: at {before}; 3 records; 0 findings, 0 fixed, 0 justified\n"],
            True,
            0,
        ),
        "a wrong receipt mended by accepting again is green": ([bare, right], False, 0),
        "an acceptance of a record that is not there is a note": (
            [right, f"yes\n\nAccepted: {stranger}\n"],
            False,
            1,
        ),
    }
    # the note of an id that names no record, typed by hand, the commit being the case's last
    stranger_note = (
        "NOTE: commit {last} accepts " + stranger + ", which is no record here — deleted since, renumbered"
        " or misspelt; when renumbered, accept it again under its new id in the merge commit of the change"
        " that renumbers it; when misspelt, accept again in the merge commit of a new pull request, the id"
        " spelt right"
    )
    for name, (messages, red_wanted, notes_wanted) in receipts.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            git(root, "init", "-q")
            before = commit(root, "before the record")
            sample_kit(root)
            pinned = commit(root, "the record lands")
            awaiting = check_kit(root)
            last = pinned
            for message in messages:
                last = commit(root, message.format(at=pinned[:12], before=before[:12]))
            findings, notes, _ = check_kit(root)
        ok = (not awaiting[0] and len(awaiting[1]) == 1) and bool(findings) == red_wanted
        ok = ok and len(notes) == notes_wanted
        if name == "an acceptance of a record that is not there is a note":
            ok = ok and notes == [stranger_note.format(last=last[:7])]
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] a record awaiting its yes is a note; {name}")

    # the acceptance read asks git log without signature lines: a signed merge, with log.showSignature
    # on, is read as the unsigned right receipt is — green — and git was asked to verify it
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as tools:
        root = Path(tmp).resolve()
        git(root, "init", "-q")
        commit(root, "before the record")
        sample_kit(root)
        pinned = commit(root, "the record lands")
        signing = fake_signer(root, Path(tools).resolve())
        signed_merge(root, right.format(at=pinned[:12]))
        shown = git(root, "log", "-1", "--format=%h")
        calls = signing.read_text(encoding="utf-8") if signing.exists() else ""
        findings, notes, _ = check_kit(root)
    asked = "--verify" in calls and "fake signer" in shown.stdout + shown.stderr
    ok = asked and not findings and not notes
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] a signed acceptance merge under showSignature is read as an unsigned one"
    )

    # a git too old for the trailer options prints the placeholders as text: the check cannot run, and
    # says which git; a receipt that merely quotes the placeholder is read as ever
    real = shutil.which("git")
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as tools:
        root = Path(tmp).resolve()
        git(root, "init", "-q")
        commit(root, "before the record")
        sample_kit(root)
        pinned = commit(root, "the record lands")
        commit(root, right.format(at=pinned[:12]))
        for script in ("check-carry-lists.py", "kit_module_doc.py"):  # the check and the reader it imports
            (root / "scripts" / script).write_text(
                (Path(__file__).parent / script).read_text(encoding="utf-8"), encoding="utf-8"
            )
        old_log = fake_old_git(Path(tools).resolve(), real or "git")
        env = {**os.environ, "PATH": f"{Path(tools).resolve()}{os.pathsep}{os.environ['PATH']}"}
        ran = subprocess.run(
            [sys.executable, str(root / "scripts" / "check-carry-lists.py")],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        version = subprocess.run([real or "git", "version"], capture_output=True, text=True, check=False)
        asked_for_options = old_log.exists() and "nosuchopt" in old_log.read_text(encoding="utf-8")
        wanted = [
            "BROKEN: git does not know the trailer options this check reads (key, valueonly, separator): "
            f"{version.stdout.splitlines()[0]} — fix: install a newer git (https://git-scm.com/downloads)",
            "BROKEN: the check could not run — 0 records examined",
        ]
    ok = asked_for_options and ran.returncode == EXIT_BROKEN and ran.stdout.splitlines() == wanted
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a git that prints the trailer placeholders as text is named, exit 1")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        git(root, "init", "-q")
        commit(root, "before the record")
        sample_kit(root)
        pinned = commit(root, "the record lands")
        commit(root, right.format(at=pinned[:12]) + "Carry-Audit: the %(trailers placeholder, quoted\n")
        try:
            findings, _, _ = check_kit(root)
            ok = any("cannot be read" in finding.headline for finding in findings)
        except CouldNotRun:
            ok = False
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a receipt that quotes the placeholder is read, not a git too old")

    newer = f"dec-{THRESHOLD + 2:04d}-newer"
    moved = f"dec-{THRESHOLD + 3:04d}-moved"
    policy = "---\nid: p\ntype: current-state\nstatus: active\n---\nmore\n"
    cites = f"1. [x](../../{folder}/{SAMPLE}.md)\n"
    module_doc = f'<a id="t4"></a>\n## 4. Decisions\n\n{cites}'
    renumbered_doc = f'<a id="t3"></a>\n## 4. Rows\n\n<a id="t4"></a>\n## 5. Decisions\n\n{cites}'
    stray_doc = (
        f'<a id="t3"></a>\n## 3. Rows\n\n## 4. Notes\n\nnothing is cited here\n\n<a id="t4"></a>\n'
        f"## 5. Decisions\n\n{cites}"
    )
    other = f"dec-{THRESHOLD + 4:04d}-other"
    cites_other = f"1. [y](../../{folder}/{other}.md)\n"
    ends_doc = f'<a id="t4"></a>\n## 4. Decisions\n\n{cites}\n<a id="t5"></a>\n## 5. Next\n\n{cites_other}'
    sub_heading_doc = (  # the section ends at the next anchor, not at the next "## " heading
        f'<a id="t4"></a>\n## 4. Decisions\n\nthe records:\n\n## Some sub-heading\n\n{cites}\n'
        f'<a id="t5"></a>\n## 5. Next\n\n{cites_other}'
    )

    def add_record(root: Path) -> None:
        (root / folder / f"{newer}.md").write_text(GOOD_RECORD.replace(SAMPLE, newer), encoding="utf-8")
        (root / "docs/policies/p.md").write_text(policy, encoding="utf-8")

    def edit_record(root: Path) -> None:
        (root / folder / f"{SAMPLE}.md").write_text(GOOD_RECORD + "\n", encoding="utf-8")

    def rename_record(root: Path) -> None:
        (root / folder / f"{SAMPLE}.md").rename(root / folder / f"{moved}.md")
        git(root, "add", "-A")  # staged, so that git sees a rename: without --no-renames the case is red

    def cite_in(text: str) -> Callable[[Path], None]:
        def write(root: Path) -> None:
            (root / "modules/m/MODULE.md").write_text(text, encoding="utf-8")

        return write

    # name -> (the change, the module, full wanted, regression wanted)
    scopes: dict[str, tuple[Callable[[Path], None], str | None, dict[str, str], dict[str, list[str]]]] = {
        "an added record in full, a record citing a touched file for regression": (
            add_record,
            None,
            {newer: "added"},
            {SAMPLE: ["docs/policies/p.md"]},
        ),
        "an edited record in full": (edit_record, None, {SAMPLE: "edited"}, {}),
        "a renamed record in full, under its new name": (rename_record, None, {moved: "added"}, {}),
        "a record the module cites in full": (cite_in(module_doc), "m", {SAMPLE: "cited"}, {}),
        "a record cited under anchor t4 in full, its section numbered 5 and the rows 4": (
            cite_in(renumbered_doc),
            "m",
            {SAMPLE: "cited"},
            {},
        ),
        "a record cited under anchor t4 in full, a stray section 4 above it": (
            cite_in(stray_doc),
            "m",
            {SAMPLE: "cited"},
            {},
        ),
        "a record cited in the section after the decisions, under anchor t5, is not in full": (
            cite_in(ends_doc),
            "m",
            {SAMPLE: "cited"},
            {},
        ),
        'a record cited below a "## " sub-heading of the decisions section is in full': (
            cite_in(sub_heading_doc),
            "m",
            {SAMPLE: "cited"},
            {},
        ),
    }
    for name, (change, module, full_wanted, regression_wanted) in scopes.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            git(root, "init", "-q")
            sample_kit(root)
            base = commit(root, "the base: one record, which cites the policy")
            change(root)
            ok = compute_scope(root, base, module) == (full_wanted, regression_wanted)
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the scope: {name}")
    unscopable = {  # the module document, and what its scope cannot be read from
        "with no decisions section": ('<a id="t3"></a>\n## 3. Rows\n', "has no anchor"),
        "whose decisions anchor has text on its line": (
            f'<a id="t3"></a>\n## 3. Rows\n\n## 4. Decisions <a id="t4"></a>\n\n{cites}',
            "has no anchor",
        ),
        "whose decisions anchor stands twice": (
            f'<a id="t4"></a>\n## 4. Decisions\n\n{cites}\n<a id="t4"></a>\n',
            "holds the anchor",
        ),
        "whose rows anchor stands twice, above the decisions": (
            f'<a id="t3"></a>\n## 3. Rows\n\n<a id="t3"></a>\n\n<a id="t4"></a>\n## 4. Decisions\n\n{cites}',
            "holds the anchor",
        ),
        "whose decisions section's end anchor is gone, a later one standing": (
            f'<a id="t4"></a>\n## 4. Decisions\n\n{cites}\n<a id="t6"></a>\n## 6\n',
            'has no anchor <a id="t5"></a> after <a id="t4"></a>',
        ),
        "whose acceptance anchor stands twice, below the decisions": (
            f'<a id="t4"></a>\n## 4. Decisions\n\n{cites}\n<a id="t9"></a>\n\n<a id="t9"></a>\n',
            "holds the anchor",
        ),
    }
    for name, (text, said) in unscopable.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            git(root, "init", "-q")
            sample_kit(root)
            base = commit(root, "the base")
            (root / "modules/m/MODULE.md").write_text(text, encoding="utf-8")
            try:
                compute_scope(root, base, "m")
                ok = False
            except CouldNotRun as bad:
                ok = said in str(bad) and "modules/m/MODULE.md" in str(bad) and "— fix:" in str(bad)
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the scope: a module document {name} cannot be scoped")

    # the records' folder and number width are the dials file's, read and never assumed
    extra = 0

    def judge(ok: bool, text: str) -> None:
        nonlocal failed, extra
        extra += 1
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {text}")

    def run_on_dials(dials: str | None) -> tuple[str, int]:
        """What the check says when the sample kit's dials file is this text (None: no file), empty when it
        runs, and how many records it examined."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            git(root, "init", "-q")
            sample_kit(root)
            if dials is None:
                (root / DIALS).unlink()
            else:
                (root / DIALS).write_text(dials, encoding="utf-8")
            try:
                return "", check_kit(root)[2]
            except CouldNotRun as bad:
                return str(bad), 0

    def examined(layout: Layout, damage: Callable[[str], str] = lambda text: text) -> tuple[int, int]:
        """The findings and the records of the check over a sample kit of this layout, its record damaged."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            git(root, "init", "-q")
            sample_kit(root, damage(GOOD_RECORD.replace(SAMPLE, layout.sample)), layout)
            findings, _, records = check_kit(root)
        return len(findings), records

    in_folder = f'["{folder}/**"]'
    refused: dict[str, tuple[str | None, tuple[str, ...]]] = {
        "no dials file": (None, (f"{DIALS} cannot be read", "restore the dials file")),
        "a dials file that is no YAML": ("const-catalogs: [\n", ("cannot be read",)),
        "a dials file that is no mapping": ("just text\n", (f"no {NAMESPACE}.catalogs list",)),
        "no const-catalogs namespace": ("other:\n  catalogs: []\n", (f"no {NAMESPACE}.catalogs list",)),
        "catalogs that is no list": (f"{NAMESPACE}:\n  catalogs: dec\n", (f"no {NAMESPACE}.catalogs list",)),
        "an empty catalogs list": (
            f"{NAMESPACE}:\n  catalogs: []\n",
            ("declares no catalog with prefix dec",),
        ),
        "an entry that is no mapping": (f"{NAMESPACE}:\n  catalogs:\n    - dec\n", ("no mapping",)),
        "an rfc catalog and no dec one": (
            dials_file("4", in_folder).replace("prefix: dec", "prefix: rfc"),
            ("declares no catalog with prefix dec", "add the entry"),
        ),
        "two dec catalogs": (
            dials_file("4", in_folder, entries=2),
            ("prefix dec twice", "keep one dec entry"),
        ),
        "a catalog width of 5 where the records have four digits": (
            Layout(width=5).dials(),
            (
                f"{folder}/{SAMPLE}.md",
                "make the catalog's width in constitution.yaml and the records' names agree",
            ),
        ),
        "a catalog folder that is not where the records are": (
            Layout("docs/records").dials(),
            (
                "no docs/records/ directory",
                "correct the dec catalog's territory in constitution.yaml, or restore the folder",
            ),
        ),
    }
    for written in ("true", "false", "0", "10", "-1", '"4"', "4.0", "null", "[4]"):
        refused[f"a catalog width of {written}"] = (
            dials_file(written, in_folder),
            (f"a whole number from 1 to {MAX_WIDTH}", "digits of the records' names"),
        )
    for territory in (
        '["docs/decisions/**", "docs/records/**"]',
        '["docs/decisions/*.md"]',
        '"docs/decisions/**"',
        '["docs/**/decisions/**"]',
        '["**"]',
        '["docs/../x/**"]',
        '["docs//decisions/**"]',
        '["./docs/decisions/**"]',
        '["docs/decisions//**"]',
        "[3]",
        '["docs/decisions/"]',
        '["#docs/**"]',
        "[]",
        "null",
    ):
        refused[f"a catalog territory of {territory}"] = (
            dials_file("4", territory),
            ("no single territory '<folder>/**'", "one territory pattern of that form"),
        )
    refused["a catalog width of 1, too narrow for a record at the threshold"] = (
        dials_file("1", in_folder),
        ("width 1", f"a record at {THRESHOLD}", "set width to at least 2"),
    )
    for name, (dials, fragments) in refused.items():
        said = run_on_dials(dials)[0]
        ok = bool(said) and all(fragment in said for fragment in fragments) and "— fix:" in said
        judge(ok, f"{name} cannot be checked, never a silent green")

    with tempfile.TemporaryDirectory() as tmp:  # a dials file that is no UTF-8 text: a teaching line
        root = Path(tmp).resolve()
        git(root, "init", "-q")
        sample_kit(root)
        (root / DIALS).write_bytes(b"const-catalogs:\n  # \xff\xfe\n")
        try:
            check_kit(root)
            said = ""
        except CouldNotRun as bad:
            said = str(bad)
    judge(
        f"{DIALS} cannot be read" in said and "utf-8" in said and "— fix:" in said,
        "a dials file that is not UTF-8 text cannot be checked, never a traceback",
    )
    widths_ok = True
    for width in range(len(str(THRESHOLD)), MAX_WIDTH + 1):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / folder).mkdir(parents=True)
            (root / DIALS).write_text(dials_file(str(width), in_folder), encoding="utf-8")
            try:
                stem = load_catalog(root).stem
            except CouldNotRun:
                widths_ok = False
                continue
        digits = "1" * width
        widths_ok = widths_ok and bool(stem.match(f"dec-{digits}-x")) and not stem.match(f"dec-{digits}1-x")
    judge(
        widths_ok,
        f"every catalog width from {len(str(THRESHOLD))} to {MAX_WIDTH} is accepted, "
        "and numbers by exactly that many digits",
    )
    alias = (
        'anchors:\n  territory: &decisions\n    - "/docs/decisions/**"\n'
        f"{NAMESPACE}:\n  catalogs:\n    - prefix: dec\n      territory: *decisions\n"
    )
    judge(
        run_on_dials(dials_file(None, in_folder)) == ("", 1),
        "a catalog with no width numbers by four digits: the record is found",
    )
    judge(
        run_on_dials(alias) == ("", 1),
        "a territory by alias, with a leading slash, is read: the record is found",
    )

    width5, moved_to, both = Layout(width=5), Layout("docs/records"), Layout("docs/records", 5)

    def cut(text: str) -> str:
        return text[: text.index("## Carry list")]

    for name, layout in (
        ("a catalog of width 5", width5),
        ("a catalog in docs/records", moved_to),
    ):
        judge(
            examined(layout) == (0, 1) and examined(layout, cut) == (1, 1),
            f"{name} is read: its record is found, green whole and red with its carry list cut",
        )

    def stray_said(strays: tuple[str, ...], scoped: bool) -> str:
        """What the check or the scope says when these files stand in the sample kit's records' folder."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            git(root, "init", "-q")
            sample_kit(root)
            base = commit(root, "the base")
            for stray in strays:
                (root / folder / stray).write_text("text\n", encoding="utf-8")
            try:
                if scoped:
                    compute_scope(root, base, None)
                else:
                    check_kit(root)
            except CouldNotRun as bad:
                return str(bad)
        return ""

    arabic = "dec-٠٠٣١-sample.md"  # 0031 in Arabic-Indic digits
    # the strays, and the first of them in sorted order, the one the failure names; the folder is listed
    # in reverse order for these cases (listed_in_reverse), so that the sorted first is listed last, on
    # every filesystem: a failure naming the first it lists is red, and the order of the filesystem,
    # which is no promise, holds nothing here
    stray_cases: dict[str, tuple[tuple[str, ...], str]] = {
        "a file in the records' folder the width cannot number cannot be {}": (("README.md",), "README.md"),
        "a record named with non-ASCII digits is a stray, never a gated record: it cannot be {}": (
            (arabic,),
            arabic,
        ),
        "of several files the width cannot number, the first in sorted order is named: they cannot be {}": (
            ("Zed.md", "README.md", arabic, "TODO.md", "NOTES.md", "dec-31-short.md"),
            "NOTES.md",
        ),
    }
    for name, (strays, first) in stray_cases.items():
        for scoped, verb in ((False, "checked"), (True, "scoped")):
            with listed_in_reverse():
                said = stray_said(strays, scoped)
            others = [stray for stray in strays if stray != first]
            judge(
                f"{folder}/{first} " in said and not any(f"{folder}/{other} " in said for other in others),
                ("the scope: " if scoped else "") + name.format(verb),
            )

    newest = f"dec-{THRESHOLD + 2:05d}-newer"
    rows = f'<a id="t4"></a>\n## 4. Decisions\n\n1. [x](../../{both.folder}/{both.sample}.md)\n'
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        git(root, "init", "-q")
        sample_kit(root, GOOD_RECORD.replace(SAMPLE, both.sample), both)
        base = commit(root, "the base")
        (root / both.folder / f"{newest}.md").write_text(
            GOOD_RECORD.replace(SAMPLE, newest), encoding="utf-8"
        )
        (root / "docs/policies/p.md").write_text(policy, encoding="utf-8")
        added = compute_scope(root, base, None)
        (root / "modules/m/MODULE.md").write_text(rows, encoding="utf-8")
        cited = compute_scope(root, base, "m")
    judge(
        added == ({newest: "added"}, {both.sample: ["docs/policies/p.md"]})
        and cited == ({newest: "added", both.sample: "cited"}, {}),
        "the scope of a catalog in docs/records of width 5: a record added and a record cited, found there",
    )
    # a record the change edits is read in full; that another record, unedited, links to its file is no
    # reason to read that one for regression: the records' own folder is not among the files that count
    for layout in (DEFAULT_LAYOUT, moved_to):
        other_record = f"dec-{THRESHOLD + 5:04d}-links"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            git(root, "init", "-q")
            path = sample_kit(root, layout=layout)
            (root / layout.folder / f"{other_record}.md").write_text(
                GOOD_RECORD.replace(SAMPLE, other_record) + f"\nSee [the sample]({path.name}).\n",
                encoding="utf-8",
            )
            base = commit(root, "the base: two records, the second linking the first")
            path.write_text(GOOD_RECORD.replace(SAMPLE, layout.sample) + "\n", encoding="utf-8")
            edited_scope = compute_scope(root, base, None)
        judge(
            edited_scope == ({layout.sample: "edited"}, {}),
            f"the scope in {layout.folder}: an edited record is in full, and a record linking its file "
            "is not read for regression",
        )
    accept = f"yes\n\nAccepted: {both.sample}\n"
    for name, at, red in (
        ("an audit at the record's commit", "{pinned}", False),
        ("an audit pinned before the record existed", "{before}", True),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            git(root, "init", "-q")
            before = commit(root, "before the record")
            sample_kit(root, GOOD_RECORD.replace(SAMPLE, both.sample), both)
            pinned = commit(root, "the record lands")
            at = at.format(pinned=pinned[:12], before=before[:12])
            commit(root, accept + f"Carry-Audit: at {at}; 3 records; 0 findings, 0 fixed, 0 justified\n")
            findings, notes, _ = check_kit(root)
        judge(
            bool(findings) == red and not notes,
            f"in a catalog of docs/records, width 5: {name} is {'red' if red else 'green'}",
        )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        pending = GOOD_RECORD.replace(SAMPLE, both.sample).replace("(../plan.md)", f"({both.sample}.md)")
        found, _ = lists(root, sample_kit(root, pending, both))
    judge(
        len(found) == 1 and "pending nowhere" in found[0].headline,
        "in a catalog of docs/records, pending intent in another record is red: the folder is the dials'",
    )

    right_receipt = (
        "yes\n\nAccepted: {id}\nCarry-Audit: at {at}; 3 records; 0 findings, 0 fixed, 0 justified\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        git(root, "init", "-q")
        sample_kit(root)
        pinned = commit(root, "the record lands")
        commit(root, right_receipt.format(id=SAMPLE, at=pinned[:12]))
        (root / folder).rename(root / "docs/records")
        (root / DIALS).write_text(Layout("docs/records").dials(), encoding="utf-8")
        commit(root, "the records move")
        moved_after = check_kit(root)
        listings: dict[str, set[str]] = {}
        files_at(root, listings, pinned)
        listings[pinned] = {"cached.md"}
        cached = files_at(root, listings, pinned) == {"cached.md"}
    judge(
        moved_after[0] == [] and moved_after[1] == [] and moved_after[2] == 1,
        "the folder moved since the audit: the record is found at the audit commit wherever it stood, green",
    )
    judge(cached, "the files of an audit commit are read once per commit")
    # two records whose receipts name the same audit commit: its listing is asked of git once
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as tools:
        root = Path(tmp).resolve()
        git(root, "init", "-q")
        sample_kit(root)
        (root / folder / f"{newer}.md").write_text(GOOD_RECORD.replace(SAMPLE, newer), encoding="utf-8")
        pinned = commit(root, "the records land")
        for accepted_id in (SAMPLE, newer):
            commit(root, right_receipt.format(id=accepted_id, at=pinned[:12]))
        git_calls = fake_logging_git(Path(tools).resolve(), real or "git")
        search = os.environ["PATH"]
        os.environ["PATH"] = f"{Path(tools).resolve()}{os.pathsep}{search}"
        try:
            shared = check_kit(root)
        finally:
            os.environ["PATH"] = search
        listings_read = [
            line for line in git_calls.read_text(encoding="utf-8").splitlines() if " ls-tree " in line
        ]
    judge(
        shared[0] == [] and shared[1] == [] and shared[2] == 2 and len(listings_read) == 1,
        "two records with receipts at the same audit commit: the listing of that commit is read once",
    )
    renamed = f"dec-{THRESHOLD + 4:04d}-renamed"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        git(root, "init", "-q")
        sample_kit(root)
        pinned = commit(root, "the record lands")
        (root / folder / f"{SAMPLE}.md").rename(root / folder / f"{renamed}.md")
        commit(root, right_receipt.format(id=renamed, at=pinned[:12]))
        findings, _, _ = check_kit(root)
    judge(
        len(findings) == 1 and "did not exist yet" in findings[0].headline,
        "a record that stood under another id at the audit commit did not exist yet there: red",
    )

    total = (
        len(wrong_lists)
        + len(readme_texts)
        + 1
        + len(right_homes)
        + len(receipts)
        + len(scopes)
        + len(unscopable)
        + 3
        + extra
    )
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-carry-lists", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--scope", nargs="+", metavar=("BASE", "MODULE"))
    try:
        args = parser.parse_args(argv)
        if args.scope and len(args.scope) > 2:
            raise SystemExit(2)
    except SystemExit:
        print(
            "BROKEN: misinvocation — fix: run with no arguments, with --scope BASE [MODULE], "
            "or with --self-test"
        )
        print("BROKEN: the check could not run — 0 records examined")
        return EXIT_BROKEN
    try:
        if args.self_test:
            return self_test()
        if args.scope:
            return scope(KIT, args.scope[0], args.scope[1] if len(args.scope) == 2 else None)
        return report(*check_kit(KIT))
    except CouldNotRun as failure:
        print(f"BROKEN: {failure}")
        print("BROKEN: the check could not run — 0 records examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
