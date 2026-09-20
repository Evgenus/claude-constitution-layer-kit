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
               plan, a research comparison, another record and the README cannot: those are where
               rulings were found hiding. "pending" is for intent that is not yet real, and its
               link leads to the task-record that holds the work to come — a plan, never a
               decision record — where the kernel says such intent rides. The entry is never
               rewritten: once that task-record closes, the check says so in a note.
  the receipt  the commit that accepts a record — trailer "Accepted: <record id>" — also carries
               "Carry-Audit: at <commit>; <n> records; <f> findings, <x> fixed, <j> justified";
               the commit named is an ancestor at which the record already existed, n is above
               zero, x + j = f. The newest acceptance of a record is the one that counts, so a
               wrong receipt is mended by accepting again. A record no commit accepts yet awaits
               its yes: a note, never a finding — a gate is not red for waiting on a person. An
               "Accepted:" id that names no record is a note too: deleted since, or misspelt.

What it cannot see, and leaves to the reader of the audit: a ruling item the author never gave a
handle; whether the linked text states the rule; whether the audit the receipt names was run.

Records numbered below the threshold were written before the rule and are not examined.

Modes:  no arguments            check the lists and the receipts;
        --scope BASE [MODULE]   print the records a closing audit must read for the change since
                                BASE: in full — those the change adds or edits and those the module's
                                decisions section cites; for regression — those that cite a file
                                the change touched;
        --self-test             prove each finding red and the right record green, on throwaway trees.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:
    print("BROKEN: PyYAML is not installed — fix: python3 -m pip install pyyaml")
    print("BROKEN: the check could not run — 0 records examined")
    sys.exit(1)

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2

DECISIONS = "docs/decisions"
THRESHOLD = 30  # the record that landed this check; earlier records predate the rule
STEM = re.compile(r"^dec-(\d{4})-[a-z0-9-]+$")
LAST_SECTION = "Carry list"
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
    """The check cannot give a verdict: no git, a shallow clone, no records directory."""


def gated_records(kit: Path) -> list[Path]:
    records = []
    for path in sorted((kit / DECISIONS).glob("*.md")):
        match = STEM.match(path.stem)
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
    'the README state no rule — intent that is not yet real is "pending" with a link to its task-record'
)
PEND_IT = "link the step of the task-record that holds the intent — the plan, never a decision record"


def home_problem(kit: Path, record: Path, target: str, pending: bool = False) -> tuple[str, str] | None:
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
    envelope, _ = split_frontmatter(path.read_text(encoding="utf-8")) if path.suffix == ".md" else ({}, "")
    kind = envelope.get("type")
    if pending:
        if kind == "task-record" and not shown.startswith(DECISIONS + "/"):
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


def check_list(kit: Path, record: Path) -> tuple[list[Finding], list[str]]:
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
            problem = home_problem(kit, record, target, pending)
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
    log = git(kit, "log", "--topo-order", f"--format={form}")
    if log.returncode != 0:
        raise CouldNotRun(
            f"git log failed: {log.stderr.strip()} — fix: run the script from a checkout of the kit"
        )
    found = []
    for chunk in log.stdout.split("\x01"):
        parts = chunk.strip("\n").split("\x00")
        if len(parts) != 3 or not parts[1].strip():
            continue
        ids = [i.strip() for value in parts[1].split("\x1f") for i in value.split(",") if i.strip()]
        receipts = [r.strip() for r in parts[2].split("\x1f") if r.strip()]
        found.append(Acceptance(parts[0], ids, receipts))
    return found


RECEIPT_FORM = "Carry-Audit: at <commit>; <n> records; <f> findings, <x> fixed, <j> justified"
AGAIN = " — then accept again in a new commit, never by rewriting history: the newest acceptance counts"


def check_receipt(kit: Path, record_id: str, acceptance: Acceptance) -> list[Finding]:
    where = f"commit {acceptance.commit[:7]} accepts {record_id}"
    if not acceptance.receipts:
        return [
            Finding(
                f"{where} and names no carry audit",
                WHY_RECEIPT,
                "run the audit, then accept again in a new commit that carries both trailers — "
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
        elif git(kit, "cat-file", "-e", f"{at}:{DECISIONS}/{record_id}.md").returncode != 0:
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
    if not (kit / DECISIONS).is_dir():
        raise CouldNotRun(
            f"{kit} has no {DECISIONS}/ directory — fix: run the script from a checkout of the kit"
        )
    records = gated_records(kit)
    findings: list[Finding] = []
    notes: list[str] = []
    for record in records:
        found, noted = check_list(kit, record)
        findings.extend(found)
        notes.extend(noted)
    accepted = acceptances(kit) if records else []
    for record in records:
        mine = [
            a for a in accepted if record.stem in a.accepted
        ]  # --topo-order: a commit comes before its ancestors
        if not mine:
            notes.append(f'NOTE: {record.stem} awaits its yes — no commit carries "Accepted: {record.stem}"')
        else:
            findings.extend(check_receipt(kit, record.stem, mine[0]))
    present = {path.stem for path in (kit / DECISIONS).glob("*.md")}
    for acceptance in accepted:
        for stem in acceptance.accepted:
            if stem not in present:
                notes.append(
                    f"NOTE: commit {acceptance.commit[:7]} accepts {stem}, which is no record here — "
                    "deleted since, or misspelt; when misspelt, accept again in a new commit, the id "
                    "spelt right"
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
    """The records a closing audit reads in full, each with the reason, and those it reads for regression."""
    if git(kit, "rev-parse", "--verify", "-q", f"{base}^{{commit}}").returncode != 0:
        raise CouldNotRun(f"{base} names no commit — fix: pass the commit the change started from")

    def names(*args: str) -> set[str]:
        return set(git(kit, *args).stdout.split())

    in_records = ("--", DECISIONS)
    added = names("diff", "--name-only", "--diff-filter=A", "--no-renames", base, *in_records)
    added |= names("ls-files", "--others", "--exclude-standard", *in_records)
    edited = names("diff", "--name-only", "--diff-filter=M", "--no-renames", base, *in_records)
    touched = names("diff", "--name-only", "--no-renames", base) | names(
        "ls-files", "--others", "--exclude-standard"
    )
    touched = {t for t in touched if not t.startswith(DECISIONS + "/")}
    full = {Path(p).stem: "edited" for p in edited if STEM.match(Path(p).stem)}
    full |= {Path(p).stem: "added" for p in added if STEM.match(Path(p).stem)}
    if module:
        document = kit / "modules" / module / "MODULE.md"
        if not document.is_file():
            raise CouldNotRun(
                f"modules/{module}/MODULE.md does not exist, so the records it cites cannot be read — "
                "fix: name a module under modules/"
            )
        section = re.search(
            r"^## 4\. .*?(?=^## |\Z)", document.read_text(encoding="utf-8"), re.MULTILINE | re.DOTALL
        )
        if section is None:
            raise CouldNotRun(
                f"modules/{module}/MODULE.md has no section 4, and a scope that silently leaves out the "
                "records a module cites is too narrow — fix: fill the template's decisions section"
            )
        for cited in cited_files(kit, document, section.group(0)):
            if cited.startswith(DECISIONS + "/"):
                full.setdefault(Path(cited).stem, "cited")
    regression: dict[str, list[str]] = {}
    for record in sorted((kit / DECISIONS).glob("*.md")):
        if record.stem in full or not STEM.match(record.stem):
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

SAMPLE = f"dec-{THRESHOLD + 1:04d}-sample"  # built, so that no file names a record that does not exist
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


def sample_kit(root: Path, record: str = GOOD_RECORD) -> Path:
    for folder in (DECISIONS, "docs/policies", "docs/research", ".claude/skills/s", "modules/m", "scripts"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    envelopes = {
        "docs/policies/p.md": "id: p\ntype: current-state\nstatus: active",
        "docs/policies/old.md": "id: old\ntype: current-state\nstatus: inactive",
        "docs/plan.md": "id: plan\ntype: task-record\nstatus: active",
        "docs/done.md": "id: done\ntype: task-record\nstatus: inactive",
        "docs/research/r.md": "id: r\ntype: non-authoritative\nstatus: active",
        ".claude/skills/s/SKILL.md": "name: s\ndescription: a skill of the kit",
    }
    for name, envelope in envelopes.items():
        (root / name).write_text(f"---\n{envelope}\n---\n", encoding="utf-8")
    for name in ("README.md", "CLAUDE.md", "modules/m/INSTALL.md", "scripts/x.py"):
        (root / name).write_text("text\n", encoding="utf-8")
    path = root / DECISIONS / f"{SAMPLE}.md"
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


def self_test() -> int:
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
            green_before = not check_list(root, record)[0]
            record.write_text(damage(GOOD_RECORD), encoding="utf-8")
            red_after = bool(check_list(root, record)[0])
        ok = green_before and red_after
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the right list is green, {name} is red")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        found, noted = check_list(root, sample_kit(root, GOOD_RECORD.replace("(../plan.md)", "(../done.md)")))
    ok = not found and len(noted) == 1
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] pending intent in a task-record that has closed is green, with a note")
    for name, target in right_homes.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            ok = not check_list(root, sample_kit(root, GOOD_RECORD.replace(home, target)))[0]
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
    for name, (messages, red_wanted, notes_wanted) in receipts.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            git(root, "init", "-q")
            before = commit(root, "before the record")
            sample_kit(root)
            pinned = commit(root, "the record lands")
            awaiting = check_kit(root)
            for message in messages:
                commit(root, message.format(at=pinned[:12], before=before[:12]))
            findings, notes, _ = check_kit(root)
        ok = (not awaiting[0] and len(awaiting[1]) == 1) and bool(findings) == red_wanted
        ok = ok and len(notes) == notes_wanted
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] a record awaiting its yes is a note; {name}")

    newer = f"dec-{THRESHOLD + 2:04d}-newer"
    moved = f"dec-{THRESHOLD + 3:04d}-moved"
    policy = "---\nid: p\ntype: current-state\nstatus: active\n---\nmore\n"
    module_doc = f"## 4. Decisions\n\n1. [x](../../{DECISIONS}/{SAMPLE}.md)\n"

    def add_record(root: Path) -> None:
        (root / DECISIONS / f"{newer}.md").write_text(GOOD_RECORD.replace(SAMPLE, newer), encoding="utf-8")
        (root / "docs/policies/p.md").write_text(policy, encoding="utf-8")

    def edit_record(root: Path) -> None:
        (root / DECISIONS / f"{SAMPLE}.md").write_text(GOOD_RECORD + "\n", encoding="utf-8")

    def rename_record(root: Path) -> None:
        (root / DECISIONS / f"{SAMPLE}.md").rename(root / DECISIONS / f"{moved}.md")
        git(root, "add", "-A")  # staged, so that git sees a rename: without --no-renames the case is red

    def cite_record(root: Path) -> None:
        (root / "modules/m/MODULE.md").write_text(module_doc, encoding="utf-8")

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
        "a record the module cites in full": (cite_record, "m", {SAMPLE: "cited"}, {}),
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
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        git(root, "init", "-q")
        sample_kit(root)
        base = commit(root, "the base")
        (root / "modules/m/MODULE.md").write_text("## 3. Rows\n", encoding="utf-8")
        try:
            compute_scope(root, base, "m")
            ok = False
        except CouldNotRun:
            ok = True
    failed += 0 if ok else 1
    print(
        f"[{'ok' if ok else 'FAIL'}] the scope: a module document with no decisions section cannot be scoped"
    )

    total = len(wrong_lists) + 1 + len(right_homes) + len(receipts) + len(scopes) + 1
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
