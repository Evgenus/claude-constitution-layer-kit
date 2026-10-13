#!/usr/bin/env python3
"""Kit report, never a gate: run each module's fixtures under coverage.py, and print what they reach.

Advisory in the sense of law 5 of CLAUDE.md: it judges nothing and blocks nothing. Its numbers are read
by a person, who decides what they mean; no number here is a threshold, and none is held anywhere. The
kit's scheduled workflow .github/workflows/coverage.yml runs it on main, never on a pull request and
never as a required check (decision dec-0089-module-coverage-report). Mutation score is no metric of
this report: it stays pending, at step 9 of the rollout plan.

Per module folder (the kit's one listing, `module_folders` of scripts/kit_module_doc.py), the report
runs the module's runner, modules/<module>/tests/run.py, once, from the kit root, under
`python3 -m coverage run` with branch coverage and `patch = subprocess`: the fixtures run the gates as
child processes, `sh` entry points that call `python3`, and each such child is measured too. So that
`python3` is the interpreter that runs this report, the one coverage.py is installed in, a folder
holding a `python3` that calls it goes first on the runner's PATH. A child started with an environment
of its own, without coverage's variable, is not measured, and its lines count as missed. coverage.py
measures Python alone: a module's `.sh` files are not in these numbers.

The measured code is the module's own Python under modules/<module>/scripts (`own`) and the shared
const_gate it links, read at shared/const_gate (`shared`); a file under either that no run imports
counts with all its lines missed. The runner and the shared test files are not measured. Per module,
the JSON keys as written:
  own_lines, own_lines_covered        the statements of the module's own Python, and those run;
  own_branches, own_branches_covered  its branch destinations, and those taken;
  own_line_percent,                   the two ratios as percentages, rounded to one decimal,
  own_branch_percent                  null when there is nothing to count;
  shared_lines, …, shared_branch_percent
                                      the same six for shared/const_gate, as this module's fixtures
                                      reach it;
  files                               per measured file, its path from the kit root and its
                                      `lines`, `lines_covered`, `branches`, `branches_covered`;
  runner_exit                         the runner's exit: 0 when every item was green;
  seconds                             the run's wall-clock time, whole seconds.
The totals row sums the own keys and the seconds; its shared keys are the union of every module's runs
over shared/const_gate, never a sum, and its runner_exit is the largest.

Modes:  no arguments      every module, one table on stdout;
        --module <name>   that module alone, the option repeatable;
        --json <path>     the table on stdout and the same numbers as one JSON object in <path>;
        --json -          the JSON object on stdout, and no table.
Notes on stderr: a runner that exits other than 0 (its numbers still count what ran), and a run that
leaves no coverage data, whose module is reported with zero lines covered.
Exit:   0 whenever the runs could be made, whatever they measure; 1, with a BROKEN line that says what
        failed, why and the fix, when they cannot: coverage.py not installed, the module folders that
        cannot be listed, a module named that is no module folder, a module with no runner, a
        coverage.py command that fails, its JSON that does not parse, the arguments misused, or the
        JSON file that cannot be written.
No --self-test: no list runs it, so a self-test would be a test that nothing runs. The scheduled
workflow runs the script itself, where only its output shows, and the kit's `lint` and `types`
entries of scripts/gate-list.sh hold its code, as they hold every script at the top of scripts/.
Its name is module-coverage, never check-: the kit's check-gate-lists holds every scripts/check-*.py to
the gate group, and this script is no check. Nor is it coverage.py: a script of that name would shadow
the package it runs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from kit_module_doc import DocumentError, module_folders

KIT = Path(__file__).resolve().parent.parent
SHARED = KIT / "shared" / "const_gate"
OK, BROKEN = 0, 1
FIX_INSTALL = 'python3 -m pip install "coverage==7.16.2"'


class Broken(Exception):
    """A run the report needs cannot be made: the message is its BROKEN line, what failed and the fix."""


@dataclass
class Counts:
    lines: int = 0
    lines_covered: int = 0
    branches: int = 0
    branches_covered: int = 0

    def add(self, other: Counts) -> None:
        self.lines += other.lines
        self.lines_covered += other.lines_covered
        self.branches += other.branches
        self.branches_covered += other.branches_covered


@dataclass
class Coverage:
    own: Counts = field(default_factory=Counts)
    shared: Counts = field(default_factory=Counts)
    files: dict[str, Counts] = field(default_factory=dict)
    runner_exit: int = 0
    seconds: int = 0


def percent(part: int, whole: int) -> float | None:
    return round(100 * part / whole, 1) if whole else None


def flat(measured: Coverage) -> dict[str, object]:
    """One module's JSON object, the keys of the docstring."""
    row: dict[str, object] = {}
    for side in ("own", "shared"):
        counts: Counts = getattr(measured, side)
        row[f"{side}_lines"] = counts.lines
        row[f"{side}_lines_covered"] = counts.lines_covered
        row[f"{side}_branches"] = counts.branches
        row[f"{side}_branches_covered"] = counts.branches_covered
        row[f"{side}_line_percent"] = percent(counts.lines_covered, counts.lines)
        row[f"{side}_branch_percent"] = percent(counts.branches_covered, counts.branches)
    row["files"] = {path: asdict(counts) for path, counts in sorted(measured.files.items())}
    row["runner_exit"] = measured.runner_exit
    row["seconds"] = measured.seconds
    return row


# --- the runs -------------------------------------------------------------------------------------


def coverage_cli(*args: str, cwd: Path) -> None:
    """One `python3 -m coverage` command, or Broken with its own output."""
    done = subprocess.run(
        [sys.executable, "-m", "coverage", *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    if done.returncode != 0:
        said = (done.stderr or done.stdout).strip().splitlines()
        raise Broken(
            f"`coverage {' '.join(args)}` exited {done.returncode}: {said[-1] if said else 'no output'}\n"
            "  why: a number from a run coverage.py could not finish would be a guess\n"
            f"  fix: run the same command in {cwd} and repair what it reports"
        )


def config(work: Path, sources: list[Path]) -> Path:
    """The rc file of one run: branch coverage, the children measured, the data kept in `work`."""
    rc = work / "coveragerc"
    rc.write_text(
        "[run]\n"
        "branch = true\n"
        "parallel = true\n"
        "patch = subprocess\n"
        f"data_file = {work / 'data'}\n"
        "source =\n" + "".join(f"    {source}\n" for source in sources),
        encoding="utf-8",
    )
    return rc


def shim(work: Path) -> Path:
    """A folder whose `python3` runs this interpreter, so that a gate's `python3` is the measured one."""
    folder = work / "bin"
    folder.mkdir()
    python3 = folder / "python3"
    python3.write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n', encoding="utf-8")
    python3.chmod(0o755)
    return folder


def read_json(work: Path, rc: Path) -> dict[str, Counts]:
    """The measured files of the combined data in `work`, by path from the kit root."""
    out = work / "coverage.json"
    coverage_cli("json", "--rcfile", str(rc), "-q", "-o", str(out), cwd=work)
    try:
        files = json.loads(out.read_text(encoding="utf-8"))["files"]
        return {
            Path(name).resolve().relative_to(KIT).as_posix(): Counts(
                one["summary"]["num_statements"],
                one["summary"]["covered_lines"],
                one["summary"].get("num_branches", 0),
                one["summary"].get("covered_branches", 0),
            )
            for name, one in files.items()
        }
    except (OSError, ValueError, KeyError, TypeError) as bad:
        raise Broken(
            f"coverage.py's JSON in {out} cannot be read ({bad})\n"
            "  why: the report reads each file's summary from it\n"
            f"  fix: install the version the workflow pins, {FIX_INSTALL}"
        ) from bad


def has_data(work: Path) -> bool:
    return any(work.glob("data.*"))


def measure(module: Path, scratch: Path, notes: list[str]) -> tuple[Coverage, Path | None]:
    """Run one module's fixtures under coverage.py; its numbers, and its combined data file, if any."""
    runner = module / "tests" / "run.py"
    if not runner.is_file():
        raise Broken(
            f"modules/{module.name}/tests/run.py does not exist\n"
            "  why: the report measures what a module's fixtures reach\n"
            "  fix: restore the module's runner"
        )
    work = scratch / module.name
    work.mkdir()
    rc = config(work, [module / "scripts", SHARED])
    env = dict(os.environ)
    env["PATH"] = f"{shim(work)}{os.pathsep}{env.get('PATH', '')}"
    started = time.monotonic()
    done = subprocess.run(
        [sys.executable, "-m", "coverage", "run", "--rcfile", str(rc), str(runner)],
        cwd=KIT,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    measured = Coverage(runner_exit=done.returncode, seconds=round(time.monotonic() - started))
    if done.returncode != 0:
        notes.append(
            f"{module.name}: the runner exited {done.returncode}; its numbers count what ran — run"
            f" python3 scripts/check-aspects.py --run --module {module.name} for its red items"
        )
    if not has_data(work):
        notes.append(f"{module.name}: the run left no coverage data; its lines count as missed")
        return measured, None
    coverage_cli("combine", "--rcfile", str(rc), "-q", cwd=work)
    own = (module / "scripts").relative_to(KIT).as_posix() + "/"
    for path, counts in read_json(work, rc).items():
        if path.startswith(own):
            measured.own.add(counts)
        elif path.startswith(SHARED.relative_to(KIT).as_posix() + "/"):
            measured.shared.add(counts)
        else:
            continue
        measured.files[path] = counts
    return measured, work / "data"


def union(data: list[Path], scratch: Path) -> Counts:
    """shared/const_gate as every module's runs together reach it."""
    work = scratch / "union"
    work.mkdir()
    rc = config(work, [SHARED])
    total = Counts()
    if not data:
        return total
    coverage_cli("combine", "--rcfile", str(rc), "--keep", "-q", *map(str, data), cwd=work)
    for path, counts in read_json(work, rc).items():
        if path.startswith(SHARED.relative_to(KIT).as_posix() + "/"):
            total.add(counts)
    return total


# --- reporting -----------------------------------------------------------------------------------


COLUMNS = (
    ("own lines", "own", "lines"),
    ("own branches", "own", "branches"),
    ("shared lines", "shared", "lines"),
    ("shared branches", "shared", "branches"),
)


def cell(counts: Counts, kind: str) -> str:
    part, whole = getattr(counts, f"{kind}_covered"), getattr(counts, kind)
    ratio = percent(part, whole)
    return f"{'-' if ratio is None else f'{ratio:.1f}%'} {part}/{whole}"


def table(measured: dict[str, Coverage], total: Coverage) -> str:
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


def chosen(names: list[str] | None) -> list[Path]:
    """The module folders the report runs, all of them unless `--module` names some."""
    try:
        folders = module_folders(KIT)
    except DocumentError as bad:
        raise Broken(f"{bad}\n  why: the report measures each module folder") from bad
    if not names:
        return folders
    known = {folder.name: folder for folder in folders}
    for name in names:
        if name not in known:
            raise Broken(
                f"--module {name} names no module folder\n  why: the report runs a module's own runner\n"
                f"  fix: name one of {', '.join(sorted(known))}"
            )
    return [known[name] for name in dict.fromkeys(names)]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="module-coverage", add_help=False, allow_abbrev=False)
    parser.add_argument("--json")
    parser.add_argument("--module", action="append")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print(
            "BROKEN: misinvocation\n  why: an option or value the report does not know would measure"
            " something other than what was asked\n"
            "  fix: run with no arguments, with --module <name> (repeatable), with --json <path> or with"
            " --json -, alone or together"
        )
        return BROKEN
    notes: list[str] = []
    try:
        if importlib.util.find_spec("coverage") is None:
            raise Broken(
                f"coverage.py is not installed for {sys.executable}\n"
                "  why: the report runs each module's fixtures under it\n"
                f"  fix: {FIX_INSTALL}, then run the report with that same python3"
            )
        folders = chosen(args.module)
        measured: dict[str, Coverage] = {}
        data: list[Path] = []
        with tempfile.TemporaryDirectory(prefix="module-coverage-") as scratch:
            for module in folders:
                one, kept = measure(module, Path(scratch), notes)
                measured[module.name] = one
                if kept is not None:
                    data.append(kept)
            total = Coverage(shared=union(data, Path(scratch)))
        for one in measured.values():
            total.own.add(one.own)
            total.runner_exit = max(total.runner_exit, one.runner_exit)
            total.seconds += one.seconds
        totals = flat(total)
        del totals["files"]
        written = json.dumps(
            {
                "advisory": "a report of law 5 of CLAUDE.md: it judges nothing",
                "commit": commit(),
                "modules": {name: flat(one) for name, one in measured.items()},
                "totals": totals,
                "notes": notes,
            },
            indent=2,
            ensure_ascii=False,
        )
        if args.json == "-":
            print(written)
        else:
            write(args.json, written)
            print(table(measured, total))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        return BROKEN
    for note in notes:
        print(f"note: {note}", file=sys.stderr)
    return OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
