#!/usr/bin/env python3
"""Kit report, never a gate: what each module's fixtures reach of its code, from coverage.py's files.

Advisory in the sense of law 5 of CLAUDE.md: it judges nothing and blocks nothing. Its numbers are read
by a person, who decides what they mean; no number here is a threshold, and none is held anywhere.
The numbers come from the fixtures entry itself: `scripts/check-aspects.py --run` runs a module's runner
under coverage.py when CONSTITUTION_KIT_COVERAGE names a folder, and writes `<folder>/<module>.json`
(scripts/kit_coverage.py says how, and what the file holds). The kit's CI sets it in each module's job
on every pull request and on main, and the job `gates`, after its verdict, runs this report over the
files of every module job (decision dec-0089-module-coverage-report). Mutation score is no metric of
this report: it stays a work item of its own, pending at step 9 of the rollout plan.

The measured code is the module's own Python under modules/<module>/scripts (`own`) and the shared
const_gate it links, read at shared/const_gate (`shared`). Per module, the JSON keys as written:
  own_lines, own_lines_covered        the statements of the module's own Python, and those run;
  own_branches, own_branches_covered  its branch destinations, and those taken;
  own_line_percent,                   the two ratios as percentages, rounded to one decimal,
  own_branch_percent                  null when there is nothing to count;
  shared_lines, …, shared_branch_percent
                                      the same six for shared/const_gate, as this module's fixtures
                                      reach it;
  runner_exit                         the runner's exit: 0 when every item was green;
  seconds                             the run's wall-clock time under coverage.py, whole seconds.
The JSON object holds `advisory`, the line that it judges nothing; `commit`, the HEAD it was run at;
`modules`, these keys per module; `totals`, the same keys for the totals row; and `notes`, the notes.
The totals row joins the modules: its own keys count every module's own code, its shared keys the
union of every module's runs over shared/const_gate, never a sum; its seconds are the sum, and its
runner_exit the largest.

Modes:  --from <folder>   read the files in <folder>, one per module, and print one table;
        no --from         make the files first, in a folder of its own: run
                          `python3 scripts/check-aspects.py --run --module <module>` for every module,
                          with this interpreter and the variable set — minutes in all;
        --module <name>   with no --from, that module alone, the option repeatable;
        --json <path>     the table on stdout and the same numbers as one JSON object in <path>;
        --json -          the JSON object on stdout, and no table.
Notes on stderr: a runner that exited other than 0 (its numbers still count what ran); a module whose
file measured nothing, as when its run left no coverage data, shown with nothing to count; with
--from, a module folder with no file, which the table leaves out; each module run, as it starts.
Exit:   0 whenever the files could be read or made, whatever they measure; 1, with a BROKEN line that
        says what failed, why and the fix, when they cannot: the folder that is missing or cannot be
        read, a file that does not parse or lacks a key, a fixtures entry that wrote no file, the
        module folders that cannot be listed, a module named that is no module folder, the arguments
        misused, or the JSON file that cannot be written.
No --self-test: no list runs it, so a self-test would be a test that nothing runs. The job `gates`
runs the script itself on every change, where only its output shows; the self-test of check-aspects
holds the files it reads; and the kit's `lint` and `types` entries of scripts/gate-list.sh hold its
code, as they hold every script at the top of scripts/.
Its name is module-coverage, never check-: the kit's check-gate-lists holds every scripts/check-*.py to
the gate group, and this script is no check. Nor is it coverage.py: a script of that name would shadow
the package it runs.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import kit_coverage
from kit_module_doc import DocumentError, module_folders

KIT = Path(__file__).resolve().parent.parent
SHARED = "shared/const_gate/"
OK, BROKEN = 0, 1


class Broken(Exception):
    """An input the report needs cannot be read or made: the message is its BROKEN line."""


@dataclass
class Lines:
    """The lines and branches of a set of files, each kept as a set so that runs can be joined."""

    lines: set[tuple[str, int]] = field(default_factory=set)
    run: set[tuple[str, int]] = field(default_factory=set)
    branches: set[tuple[str, int, int]] = field(default_factory=set)
    taken: set[tuple[str, int, int]] = field(default_factory=set)

    def add(self, path: str, one: dict[str, list[object]]) -> None:
        executed = {(path, number(n)) for n in one["executed_lines"]}
        self.run |= executed
        self.lines |= executed | {(path, number(n)) for n in one["missing_lines"]}
        taken = {(path, *pair(b)) for b in one["executed_branches"]}
        self.taken |= taken
        self.branches |= taken | {(path, *pair(b)) for b in one["missing_branches"]}

    def join(self, other: Lines) -> None:
        self.lines |= other.lines
        self.run |= other.run
        self.branches |= other.branches
        self.taken |= other.taken

    def keys(self, side: str) -> dict[str, object]:
        """The six keys of the docstring for `side`, own or shared."""
        return {
            f"{side}_lines": len(self.lines),
            f"{side}_lines_covered": len(self.run),
            f"{side}_branches": len(self.branches),
            f"{side}_branches_covered": len(self.taken),
            f"{side}_line_percent": percent(len(self.run), len(self.lines)),
            f"{side}_branch_percent": percent(len(self.taken), len(self.branches)),
        }


@dataclass
class Module:
    own: Lines = field(default_factory=Lines)
    shared: Lines = field(default_factory=Lines)
    runner_exit: int = 0
    seconds: int = 0


def number(value: object) -> int:
    if not isinstance(value, int):
        raise ValueError(f"a line number that is no whole number: {value!r}")
    return value


def pair(branch: object) -> tuple[int, int]:
    if not isinstance(branch, list) or len(branch) != 2:
        raise ValueError(f"a branch that is no pair of line numbers: {branch!r}")
    return number(branch[0]), number(branch[1])


def percent(part: int, whole: int) -> float | None:
    return round(100 * part / whole, 1) if whole else None


def read(path: Path) -> tuple[str, Module]:
    """One module's file: its name and its numbers, or Broken."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        name = str(data["module"])
        module = Module(runner_exit=int(data["runner_exit"]), seconds=int(data["seconds"]))
        own = f"modules/{name}/scripts/"
        for file, one in data["files"].items():
            if file.startswith(own):
                module.own.add(file, one)
            elif file.startswith(SHARED):
                module.shared.add(file, one)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as bad:
        raise Broken(
            f"{path} cannot be read ({bad})\n  why: the report reads each module's coverage file whole\n"
            f"  fix: make the files again — run the fixtures entry with {kit_coverage.ENV} set, or this"
            " report without --from"
        ) from bad
    return name, module


def listed() -> list[str]:
    try:
        return [folder.name for folder in module_folders(KIT)]
    except DocumentError as bad:
        raise Broken(f"{bad}\n  why: the report measures each module folder") from bad


def gather(folder: Path, expected: list[str], notes: list[str]) -> dict[str, Module]:
    why = "\n  why: the report reads the coverage files in that folder, one per module"
    if not folder.is_dir():
        raise Broken(f"{folder} is no folder{why}\n  fix: name the folder the coverage files were written to")
    try:
        files = sorted(folder / name for name in os.listdir(folder) if name.endswith(".json"))
    except OSError as bad:
        raise Broken(
            f"{folder} cannot be read ({bad.strerror}){why}\n  fix: name a folder that can be read"
        ) from bad
    measured = dict(read(file) for file in files)
    for name in expected:
        if name not in measured:
            notes.append(f"{name}: no coverage file in {folder}; the table leaves it out")
    for name, module in measured.items():
        if not module.own.lines and not module.shared.lines:
            notes.append(
                f"{name}: its coverage file measured nothing; its run may have left no coverage data"
            )
        if module.runner_exit != 0:
            notes.append(
                f"{name}: the runner exited {module.runner_exit}; its numbers count what ran — run"
                f" python3 scripts/check-aspects.py --run --module {name} for its red items"
            )
    return measured


def make(names: list[str] | None, folder: Path) -> list[str]:
    """Run the fixtures entry of each module chosen, with the variable set to `folder`; the modules run."""
    known = listed()
    for name in names or []:
        if name not in known:
            raise Broken(
                f"--module {name} names no module folder\n  why: the report runs a module's own runner\n"
                f"  fix: name one of {', '.join(known)}"
            )
    env = dict(os.environ)
    env[kit_coverage.ENV] = str(folder)
    for name in dict.fromkeys(names or known):
        print(f"running the fixtures of {name} under coverage.py", file=sys.stderr)
        done = subprocess.run(
            [sys.executable, str(KIT / "scripts" / "check-aspects.py"), "--run", "--module", name],
            cwd=KIT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        if not (folder / f"{name}.json").is_file():
            said = [line for line in done.stdout.splitlines() if line.startswith("BROKEN:")]
            raise Broken(
                f"the fixtures entry of {name} wrote no coverage file ("
                + (said[0] if said else f"exit {done.returncode}")
                + ")\n  why: the report reads the file the entry writes\n"
                f"  fix: run {kit_coverage.ENV}=<folder> python3 scripts/check-aspects.py --run --module"
                f" {name} and repair what it reports"
            )
    return list(dict.fromkeys(names or known))


COLUMNS = (
    ("own lines", "own", "lines"),
    ("own branches", "own", "branches"),
    ("shared lines", "shared", "lines"),
    ("shared branches", "shared", "branches"),
)


def cell(numbers: Lines, kind: str) -> str:
    if kind == "lines":
        part, whole = len(numbers.run), len(numbers.lines)
    else:
        part, whole = len(numbers.taken), len(numbers.branches)
    ratio = percent(part, whole)
    return f"{'-' if ratio is None else f'{ratio:.1f}%'} {part}/{whole}"


def table(measured: dict[str, Module], total: Module) -> str:
    """One plain-text table: a module column, the four ratios with their counts, the exit and the time."""
    rows = [*measured.items(), ("totals", total)]
    head = ["module", *(title for title, _, _ in COLUMNS), "exit", "seconds"]
    body = [
        [
            name,
            *(cell(getattr(m, side), kind) for _, side, kind in COLUMNS),
            str(m.runner_exit),
            str(m.seconds),
        ]
        for name, m in rows
    ]
    widths = [max(len(row[i]) for row in [head, *body]) for i in range(len(head))]

    def line(row: list[str]) -> str:
        return "  ".join(
            v.ljust(w) if i == 0 else v.rjust(w) for i, (v, w) in enumerate(zip(row, widths, strict=True))
        )

    rule = "-" * len(line(head))
    title = (
        "Fixture coverage per module (coverage.py, Python only; shared: shared/const_gate as the module's"
        " fixtures reach it, totals: the union), advisory: a report, never a verdict"
    )
    return "\n".join([title, line(head), rule, *map(line, body[:-1]), rule, line(body[-1])])


def totals(measured: dict[str, Module]) -> Module:
    total = Module()
    for one in measured.values():
        total.own.join(one.own)
        total.shared.join(one.shared)
        total.runner_exit = max(total.runner_exit, one.runner_exit)
        total.seconds += one.seconds
    return total


def flat(module: Module) -> dict[str, object]:
    return {
        **module.own.keys("own"),
        **module.shared.keys("shared"),
        "runner_exit": module.runner_exit,
        "seconds": module.seconds,
    }


def write(path: str | None, text: str) -> None:
    """The JSON into the file `path` names, or Broken."""
    if path is None:
        return
    try:
        Path(path).write_text(text + "\n", encoding="utf-8")
    except OSError as bad:
        raise Broken(
            f"{path} cannot be written ({bad.strerror})\n  why: the JSON is the report's copy for CI's"
            " artifact\n  fix: name a path in a folder that exists and can be written to"
        ) from bad


def commit() -> str:
    done = subprocess.run(["git", "rev-parse", "HEAD"], cwd=KIT, capture_output=True, text=True, check=False)
    return done.stdout.strip() if done.returncode == 0 else "unknown"


def report(source: Path, expected: list[str], json_path: str | None, notes: list[str]) -> None:
    measured = gather(source, expected, notes)
    total = totals(measured)
    written = json.dumps(
        {
            "advisory": "a report of law 5 of CLAUDE.md: it judges nothing",
            "commit": commit(),
            "modules": {name: flat(one) for name, one in measured.items()},
            "totals": flat(total),
            "notes": notes,
        },
        indent=2,
        ensure_ascii=False,
    )
    if json_path == "-":
        print(written)
    else:
        write(json_path, written)
        print(table(measured, total))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="module-coverage", add_help=False, allow_abbrev=False)
    parser.add_argument("--from", dest="source")
    parser.add_argument("--json")
    parser.add_argument("--module", action="append")
    try:
        args = parser.parse_args(argv)
        if args.source is not None and args.module:
            raise SystemExit(2)
    except SystemExit:
        print(
            "BROKEN: misinvocation\n  why: an option or value the report does not know would measure"
            " something other than what was asked\n"
            "  fix: run with --from <folder>, or with no --from and any --module <name>, each with or"
            " without --json <path> or --json -"
        )
        return BROKEN
    notes: list[str] = []
    try:
        if args.source is not None:
            report(Path(args.source), listed(), args.json, notes)
        else:
            with tempfile.TemporaryDirectory(prefix="module-coverage-") as scratch:
                ran = make(args.module, Path(scratch))
                report(Path(scratch), ran, args.json, notes)
    except Broken as broken:
        print(f"BROKEN: {broken}")
        return BROKEN
    for note in notes:
        print(f"note: {note}", file=sys.stderr)
    return OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
