#!/usr/bin/env python3
"""Kit check: every decision record names a home for each thing it rules, and every accepted
record has the receipt of its carry audit.

A ruling that is recorded and approved but never written into a current-state document is
lost the day its record stops being read. Whether a sentence really states a rule is judgment,
and a reader decides it — the carry audit. This check holds the two parts of that audit a
script can hold:

  the list     the record's last section is "Carry list"; every ruling item carries a handle,
               **R1.**, **R2.**, …; the list pairs each handle, once, with links, with "history
               only", or with "pending" and links. A link leads where a rule can live — a governed
               document of type current-state, CLAUDE.md, a skill of the kit, a module's or the
               template's own file, a file that is not markdown. The rollout plan, a research
               comparison, another record and the README cannot: those are where rulings were
               found hiding. "pending" is for intent that is not yet real, and its links lead to
               an active task-record, where the kernel says such intent rides.
  the receipt  the commit that accepts a record — trailer "Accepted: <record id>" — also carries
               "Carry-Audit: at <commit>; <n> records; <f> findings, <x> fixed, <j> justified";
               the commit named is an ancestor, n is above zero, x + j = f. A record no commit
               accepts yet awaits its yes: a note, never a finding.

What it cannot see, and leaves to the reader of the audit: a ruling item the author never gave a
handle; whether the linked text states the rule; whether the audit the receipt names was run.

Records numbered below the threshold were written before the rule and are not examined.

Modes:  no arguments            check the lists and the receipts;
        --scope BASE [MODULE]   print the records a closing audit must read for the change since
                                BASE: in full — those the change lands and those the module's
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


def home_problem(kit: Path, record: Path, target: str, pending: bool = False) -> str | None:
    """Why this link may not be the home of a rule — of pending intent — or None when it may."""
    if re.match(r"^[a-z][a-z0-9+.-]*:", target):
        return f"{target} is outside the repository"
    path = (record.parent / target.split("#", 1)[0]).resolve()
    try:
        shown = path.relative_to(kit).as_posix()
    except ValueError:
        return f"{target} leads outside the repository"
    if not path.exists():
        return f"{shown} does not exist"
    if path.suffix != ".md":
        return "pending intent rides in an active task-record, and this is none" if pending else None
    envelope, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    kind = envelope.get("type")
    if pending:
        if kind == "task-record" and envelope.get("status") == "active":
            return None
        return f"{shown} is not an active task-record, and intent that is not yet real rides only there"
    if kind is None:
        if shown == UNGOVERNED_HOMES[0] or shown.startswith(UNGOVERNED_HOMES[1:]):
            return None
        return f"{shown} is not a governed document and holds no rules"
    if kind != "current-state":
        return f"{shown} is `{kind}`, and only a `current-state` document states a rule that binds"
    return None


def carry_entries(body: str) -> list[str]:
    entries: list[str] = []
    for line in body.splitlines():
        start = ENTRY_START.match(line)
        if start:
            entries.append(start.group(1).strip())
        elif entries and line.strip():
            entries[-1] += " " + line.strip()
    return entries


def check_list(kit: Path, record: Path) -> list[Finding]:
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
        ]
    ruled, listed = text[: headings[-1].start()], text[headings[-1].end() :]
    handles = [f"R{n}" for n in HANDLE.findall(ruled)]
    findings: list[Finding] = []
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
                    'link the current-state text that states it, or write "history only" when the item '
                    "binds nothing",
                )
            )
        for target in targets:
            problem = home_problem(kit, record, target, pending)
            if problem and pending:
                findings.append(
                    Finding(
                        f"{shown}: {parsed.group(1)} is pending nowhere — {problem}",
                        WHY_LIST,
                        "link the step of the active task-record that holds the intent; once it is real, "
                        "carry it and drop the word pending",
                    )
                )
            elif problem:
                findings.append(
                    Finding(
                        f"{shown}: {parsed.group(1)} is carried nowhere that binds — {problem}",
                        WHY_LIST,
                        "write the rule into a current-state document and link that; a plan, a comparison, "
                        "another record and the README state no rule — intent that is not yet real is "
                        '"pending" with a link to the active task-record',
                    )
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
    return findings


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
    log = git(kit, "log", f"--format={form}")
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


def check_receipt(kit: Path, record_id: str, acceptance: Acceptance) -> list[Finding]:
    where = f"commit {acceptance.commit[:7]} accepts {record_id}"
    if not acceptance.receipts:
        return [
            Finding(
                f"{where} and names no carry audit",
                WHY_RECEIPT,
                "run the audit, then accept again in a commit with both trailers — "
                f'"Accepted: {record_id}" and '
                f'"{RECEIPT_FORM}"',
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
                    f'write it as "{RECEIPT_FORM}"',
                )
            )
            continue
        at, records, found, fixed, justified = parsed.group(1), *map(int, parsed.groups()[1:])
        if records == 0:
            findings.append(
                Finding(
                    f"{where} on an audit that read 0 records",
                    WHY_RECEIPT,
                    "an audit reads at least the record it accepts; run it",
                )
            )
        if fixed + justified != found:
            findings.append(
                Finding(
                    f"{where}: {found} findings, of which {fixed} fixed and {justified} justified — "
                    f"{found - fixed - justified} unaccounted for",
                    WHY_RECEIPT,
                    "every finding is fixed or justified before the yes; account for each and accept again",
                )
            )
        if git(kit, "merge-base", "--is-ancestor", f"{at}^{{commit}}", acceptance.commit).returncode != 0:
            findings.append(
                Finding(
                    f"{where} on an audit at {at}, which is not a commit before it",
                    WHY_RECEIPT,
                    "name the commit the readers were pinned to; it is in the history the acceptance "
                    "stands on",
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
    findings = [finding for record in records for finding in check_list(kit, record)]
    notes = []
    accepted = acceptances(kit) if records else []
    for record in records:
        mine = [a for a in accepted if record.stem in a.accepted]
        if not mine:
            notes.append(f'NOTE: {record.stem} awaits its yes — no commit carries "Accepted: {record.stem}"')
        for acceptance in mine:
            findings.extend(check_receipt(kit, record.stem, acceptance))
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


def scope(kit: Path, base: str, module: str | None) -> int:
    if git(kit, "rev-parse", "--verify", "-q", f"{base}^{{commit}}").returncode != 0:
        raise CouldNotRun(f"{base} names no commit — fix: pass the commit the change started from")
    landed = set(git(kit, "diff", "--name-only", "--diff-filter=A", base, "--", DECISIONS).stdout.split())
    landed |= set(git(kit, "ls-files", "--others", "--exclude-standard", "--", DECISIONS).stdout.split())
    touched = set(git(kit, "diff", "--name-only", base).stdout.split())
    touched |= set(git(kit, "ls-files", "--others", "--exclude-standard").stdout.split())
    touched = {t for t in touched if not t.startswith(DECISIONS + "/")}
    full = {Path(p).stem for p in landed if STEM.match(Path(p).stem)}
    if module:
        document = kit / "modules" / module / "MODULE.md"
        if not document.is_file():
            raise CouldNotRun(
                f"modules/{module}/MODULE.md does not exist — fix: name a module under modules/"
            )
        section = re.search(
            r"^## 4\. .*?(?=^## )", document.read_text(encoding="utf-8"), re.MULTILINE | re.DOTALL
        )
        for cited in cited_files(kit, document, section.group(0) if section else ""):
            if cited.startswith(DECISIONS + "/"):
                full.add(Path(cited).stem)
    regression: dict[str, list[str]] = {}
    for record in sorted((kit / DECISIONS).glob("*.md")):
        if record.stem in full or not STEM.match(record.stem):
            continue
        hits = sorted(cited_files(kit, record, record.read_text(encoding="utf-8")) & touched)
        if hits:
            regression[record.stem] = hits
    for stem in sorted(full):
        print(f"full        {stem}")
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
    for folder in (DECISIONS, "docs/policies", "docs/research"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    (root / "docs/policies/p.md").write_text("---\nid: p\ntype: current-state\n---\n", encoding="utf-8")
    (root / "docs/plan.md").write_text(
        "---\nid: plan\ntype: task-record\nstatus: active\n---\n", encoding="utf-8"
    )
    (root / "docs/done.md").write_text(
        "---\nid: done\ntype: task-record\nstatus: inactive\n---\n", encoding="utf-8"
    )
    (root / "docs/research/r.md").write_text("---\nid: r\ntype: non-authoritative\n---\n", encoding="utf-8")
    (root / "README.md").write_text("# readme\n", encoding="utf-8")
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
        "an entry with no home": lambda t: t.replace(
            "[policy](../policies/p.md), rule 1.", "the policy, rule 1."
        ),
        "a home in a research comparison": lambda t: t.replace("../policies/p.md", "../research/r.md"),
        "a home in another record": lambda t: t.replace("../policies/p.md", f"{SAMPLE}.md"),
        "a home in the README": lambda t: t.replace("../policies/p.md", "../../README.md"),
        "a home that does not exist": lambda t: t.replace("../policies/p.md", "../policies/none.md"),
        "a home outside the repository": lambda t: t.replace("../policies/p.md", "https://example.invalid/p"),
        "pending intent in a closed task-record": lambda t: t.replace("(../plan.md)", "(../done.md)"),
        "pending intent in a current-state document": lambda t: t.replace(
            "(../plan.md)", "(../policies/p.md)"
        ),
        "a rule carried into the active plan": lambda t: t.replace("../policies/p.md", "../plan.md"),
    }
    failed = 0
    for name, damage in wrong_lists.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            record = sample_kit(root)
            green_before = not check_list(root, record)
            record.write_text(damage(GOOD_RECORD), encoding="utf-8")
            red_after = bool(check_list(root, record))
        ok = green_before and red_after
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the right list is green, {name} is red")

    accept = f"Accepted: {SAMPLE}"
    wrong_receipts: dict[str, Callable[[str], str]] = {
        "an acceptance with no receipt": lambda at: f"yes\n\n{accept}\n",
        "a receipt that cannot be read": lambda at: f"yes\n\n{accept}\nCarry-Audit: done, all fine\n",
        "an audit of 0 records": lambda at: (
            f"yes\n\n{accept}\nCarry-Audit: at {at}; 0 records; 0 findings, 0 fixed, 0 justified\n"
        ),
        "findings unaccounted for": lambda at: (
            f"yes\n\n{accept}\nCarry-Audit: at {at}; 3 records; 5 findings, 2 fixed, 1 justified\n"
        ),
        "an audit at no commit": lambda at: (
            f"yes\n\n{accept}\nCarry-Audit: at {'0' * 40}; 3 records; 0 findings, 0 fixed, 0 justified\n"
        ),
    }
    right = "yes\n\n" + accept + "\nCarry-Audit: at {at}; 3 records; 2 findings, 1 fixed, 1 justified\n"
    cases: dict[str, tuple[Callable[[str], str], bool]] = {
        "the right receipt": (lambda at: right.format(at=at), False),
        **{n: (m, True) for n, m in wrong_receipts.items()},
    }
    for name, (message, red_wanted) in cases.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            sample_kit(root)
            git(root, "init", "-q")
            pinned = commit(root, "the record lands")
            awaiting = check_kit(root)
            commit(root, message(pinned[:12]))
            findings, notes, _ = check_kit(root)
        ok = (not awaiting[0] and len(awaiting[1]) == 1) and (bool(findings) == red_wanted) and not notes
        failed += 0 if ok else 1
        print(
            f"[{'ok' if ok else 'FAIL'}] a record awaiting its yes is a note; "
            f"{name} is {'red' if red_wanted else 'green'}"
        )
    total = len(wrong_lists) + len(cases)
    print(f"{total - failed}/{total} red→green cases green")
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
