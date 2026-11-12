#!/usr/bin/env python3
"""Kit report, never a gate: the mutation score of each module — the share of small changes to its code
that its tests notice.

Kit tooling, never shipped in a module, and advisory in the sense of law 5 of CLAUDE.md: it judges
nothing and blocks nothing. Its numbers are read
by a person, who decides what they mean; no number here is a threshold, and none is held anywhere
(decision dec-0122-module-mutation-report). A mutant is the module's code with one small change;
`scripts/kit_mutation.py` says how the mutants are made, which tests run for each, and what each outcome
means, and its docstring defines the file of one module that this report reads. The kit's CI runs the
report on every pull request and on main, on a sample, in one job per module that starts once the check
jobs have ended and that the job `gates` does not wait for:
`--budget` stops the run after a fixed time, `--seed` is the commit the run checked out, on a pull
request its merge with the base, so that each change draws mutants of its own. The job `mutation`
then reads every module's file with `--from` and prints one table on the run's summary page, where the
fixture coverage stands too. A failure of the report changes no verdict and turns no job red.

What the score is not. Some mutants change no behaviour, and no test can kill them; the tests build some
expected texts with the gate's own functions, so a mutant there changes both sides alike; the operators
are the kit's own, and another list would give another score. With a budget the score is an estimate
from a sample, and moves from run to run with no change in the code: the table gives one standard error
beside it. So the list of survivors is the part a person can act on, each a place where the tests may
hold nothing, and the score is read as a rough level and never compared across two runs as a change.

Per module, the JSON keys as written:
  mutants         the mutants made, run or not;
  run             the mutants that got an outcome;
  killed          those a test failed with, or whose tests could not be collected;
  timeout         those whose run passed its limit; counted with the killed in the score;
  survived        those every chosen test passed with;
  not_covered     those no test reaches, counted without a run;
  unsure, error   those left out of the score: a kill whose test also failed without the mutant, and a
                  run of pytest that ended in neither a pass nor a failure;
  not_run         mutants less run: what the budget left;
  score_percent   killed and timeout as a percentage of killed, timeout, survived and not_covered, one
                  decimal; null when none of them was counted;
  standard_error_points
                  one standard error of that percentage, in points, for a sample drawn without
                  replacement from the module's mutants: 0.0 for a whole run, null with the score;
  tests           the tests that passed in the line map's run;
  seconds         the line map's run and the mutants' runs, whole seconds;
  seed, budget, copies
                  the run's settings, the budget null for a whole run;
  survivors       per survivor, its `id`, `<file>:<line>:<column>:<operator>`, the source replaced, `old`,
                  and what replaced it, `new`.
The JSON object holds `advisory`, the line that it judges nothing; `commit`, the HEAD it was run at;
`modules`, these keys per module; `totals`, the counts added, the score each module's own weighted by
its mutants, and its standard error from the modules'; and `notes`, the notes.

Modes:  --from <folder>   read the files in <folder>, one per module, and print the table and the survivors;
        no --from         make the files first: copy the kit into a scratch folder outside the tree,
                          build each module's line map and run its mutants there — a whole run takes
                          from minutes to hours per module;
        --module <name>   with no --from, that module alone, the option repeatable;
        --budget <seconds>
                          with no --from, per module: no new mutant starts once that many seconds of
                          wall-clock time have passed since the copies started on its mutants; absent,
                          every mutant runs;
        --seed <text>     with no --from, the seed of the mutants' order, `0` when absent;
        --copies <n>      with no --from, that many copies of the kit run mutants side by side, 1 when
                          absent; with more than one, a kill by a failed test is confirmed on the
                          unmutated file;
        --out <folder>    with no --from, keep each module's file there, as `<module>.json`; the table
                          then reads every module's file that folder holds;
        --json <path>     the table on stdout and the same numbers as one JSON object in <path>;
        --json -          the JSON object on stdout, and no table;
        --self-test       prove the report on a small kit of its own: the mutants of each operator, the
                          line map through a child process, each outcome, the files taken back, the
                          budget, the copies, and the table.
Notes on stderr: with --from, a module folder with no file, which the table leaves out; each module's
measure, as it starts.
Exit:   0 whenever the files could be read or made, whatever they measure; 1, with a BROKEN line on
        stdout that says what failed, why and the fix, when they cannot: a module whose unmutated tests
        are not green, coverage.py or pytest not installed, the folder that is missing or cannot be read,
        a file that does not parse or lacks a key, the module folders that cannot be listed, a module
        named that is no module folder, the arguments misused, or the JSON file that cannot be written. The
        self-test exits 0 when every case is green, 2 when one is not, and 1 with a BROKEN line where
        coverage.py or pytest is not installed.
Its name is module-mutation, never check-: the kit's check-gate-lists holds every scripts/check-*.py to
the gate group as a check, and this script is none. Its self-test is the entry `module-mutation` of the
gate group, which holds the report's code and judges no module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import kit_mutation
from kit_module_doc import DocumentError, module_folders

KIT = Path(__file__).resolve().parent.parent
OK, BROKEN, RED = 0, 1, 2
ADVISORY = "a report of law 5 of CLAUDE.md: it judges nothing"
TITLE = (
    "Mutation score per module (the kit's own operators; score: killed and timeout of the mutants judged;"
    " ±: one standard error in points, where a budget made the run a sample), advisory: a report, never a"
    " verdict"
)
SURVIVORS = (
    "Survivors, the mutants every chosen test passed with — each a place where the tests may hold nothing,"
    " or a change that alters no behaviour:"
)


class Broken(Exception):
    """An input the report needs cannot be read or made: the message is its BROKEN line."""


@dataclass
class Module:
    mutants: int = 0
    counts: dict[str, int] = field(default_factory=lambda: dict.fromkeys(kit_mutation.STATUSES, 0))
    tests: int = 0
    seconds: int = 0
    seed: str = ""
    budget: float | None = None
    copies: int = 1
    survivors: list[dict[str, str]] = field(default_factory=list)
    score: float | None = None  # a share, 0 to 1
    error: float | None = None  # its standard error, a share

    @property
    def run(self) -> int:
        return sum(self.counts.values())

    @property
    def judged(self) -> int:
        return sum(self.counts[status] for status in kit_mutation.JUDGED)

    def settle(self) -> None:
        """The score and its standard error from the counts: a sample of `judged` mutants drawn without
        replacement from `mutants`, less those left out of the score."""
        judged = self.judged
        if judged == 0:
            return
        detected = sum(self.counts[status] for status in kit_mutation.DETECTED)
        self.score = detected / judged
        whole = self.mutants - (self.run - judged)
        left = (whole - judged) / (whole - 1) if whole > 1 else 0.0
        self.error = math.sqrt(self.score * (1 - self.score) / judged * max(left, 0.0))


def points(share: float | None) -> float | None:
    return None if share is None else round(100 * share, 1)


def read(path: Path) -> tuple[str, Module]:
    """One module's file: its name and its numbers, or Broken."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        name = str(data["module"])
        module = Module(
            mutants=int(data["mutants"]),
            tests=int(data["tests"]),
            seconds=round(float(data["map_seconds"]) + float(data["seconds"])),
            seed=str(data["seed"]),
            budget=None if data["budget"] is None else float(data["budget"]),
            copies=int(data["copies"]),
        )
        for one in data["results"]:
            status = str(one["status"])
            if status not in module.counts:
                raise ValueError(f"an outcome the report does not know: {status!r}")
            module.counts[status] += 1
            if status == "survived":
                module.survivors.append(
                    {"id": str(one["id"]), "old": str(one["old"]), "new": str(one["new"])}
                )
        if module.run > module.mutants:
            raise ValueError(f"{module.run} results for {module.mutants} mutants")
        module.survivors.sort(key=place)
        module.settle()
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as bad:
        raise Broken(
            f"{path} cannot be read ({bad})\n  why: the report reads each module's mutation file whole\n"
            "  fix: make the files again — run this report without --from, with --out <folder>"
        ) from bad
    return name, module


def place(survivor: dict[str, str]) -> tuple[str, int, int, str]:
    """A survivor's id as its file, line, column and the rest, so that the list reads in source order."""
    file, line, column, rest = survivor["id"].split(":", 3)
    return file, int(line), int(column), rest


def listed() -> list[str]:
    try:
        return [folder.name for folder in module_folders(KIT)]
    except DocumentError as bad:
        raise Broken(f"{bad}\n  why: the report measures each module folder") from bad


def gather(folder: Path, expected: list[str], notes: list[str]) -> dict[str, Module]:
    why = "\n  why: the report reads the mutation files in that folder, one per module"
    try:
        if not folder.is_dir():
            raise Broken(
                f"{folder} is no folder{why}\n  fix: name the folder the mutation files were written to"
            )
        files = sorted(folder / name for name in os.listdir(folder) if name.endswith(".json"))
    except OSError as bad:
        raise Broken(
            f"{folder} cannot be read ({bad.strerror}){why}\n  fix: name a folder that can be read"
        ) from bad
    measured = dict(read(file) for file in files)
    for name in expected:
        if name not in measured:
            notes.append(f"{name}: no mutation file in {folder}; the table leaves it out")
    return measured


def make(names: list[str] | None, folder: Path, seed: str, budget: float | None, copies: int) -> list[str]:
    """Measure each module chosen and write its file into `folder`; the modules measured."""
    known = listed()
    for name in names or []:
        if name not in known:
            raise Broken(
                f"--module {name} names no module folder\n  why: the report measures a module's own code"
                f" with its own tests\n  fix: name one of {', '.join(known)}"
            )
    chosen = list(dict.fromkeys(names or known))
    for name in chosen:
        print(f"measuring the mutants of {name}", file=sys.stderr)
        with tempfile.TemporaryDirectory(prefix=f"module-mutation-{name}-") as scratch:
            try:
                one = kit_mutation.measure(KIT, name, Path(scratch), seed=seed, budget=budget, copies=copies)
            except kit_mutation.MutationError as bad:
                raise Broken(str(bad)) from bad
        write(str(folder / f"{name}.json"), json.dumps(one, indent=1, ensure_ascii=False))
    return chosen


def totals(measured: dict[str, Module]) -> Module:
    """The totals row: the counts added; the score each module's own weighted by its mutants, over the
    modules that have one, and its standard error from theirs."""
    total = Module()
    for one in measured.values():
        total.mutants += one.mutants
        total.tests += one.tests
        total.seconds += one.seconds
        for status, count in one.counts.items():
            total.counts[status] += count
    scored = [one for one in measured.values() if one.score is not None and one.error is not None]
    weight = sum(one.mutants for one in scored)
    if weight:
        total.score = sum(one.mutants * (one.score or 0.0) for one in scored) / weight
        total.error = math.sqrt(sum((one.mutants / weight * (one.error or 0.0)) ** 2 for one in scored))
    return total


def flat(module: Module, *, row: bool) -> dict[str, object]:
    keys: dict[str, object] = {
        "mutants": module.mutants,
        "run": module.run,
        "killed": module.counts["killed"],
        "timeout": module.counts["timeout"],
        "survived": module.counts["survived"],
        "not_covered": module.counts["not covered"],
        "unsure": module.counts["unsure"],
        "error": module.counts["error"],
        "not_run": module.mutants - module.run,
        "score_percent": points(module.score),
        "standard_error_points": points(module.error),
        "tests": module.tests,
        "seconds": module.seconds,
    }
    if row:
        keys |= {
            "seed": module.seed,
            "budget": module.budget,
            "copies": module.copies,
            "survivors": module.survivors,
        }
    return keys


def cells(name: str, module: Module) -> list[str]:
    score, error = points(module.score), points(module.error)
    return [
        name,
        str(module.mutants),
        str(module.run),
        str(module.counts["killed"]),
        str(module.counts["timeout"]),
        str(module.counts["survived"]),
        str(module.counts["not covered"]),
        str(module.counts["unsure"] + module.counts["error"]),
        "-" if score is None else f"{score:.1f}%",
        "-" if error is None else f"±{error:.1f}",
        str(module.seconds),
    ]


def table(measured: dict[str, Module], total: Module) -> str:
    """One plain-text table: a module column, the counts, the score with its standard error, the time."""
    head = [
        "module",
        "mutants",
        "run",
        "killed",
        "timeout",
        "survived",
        "not covered",
        "other",
        "score",
        "±",
        "seconds",
    ]
    body = [cells(name, module) for name, module in [*measured.items(), ("totals", total)]]
    widths = [max(len(row[i]) for row in [head, *body]) for i in range(len(head))]

    def line(row: list[str]) -> str:
        return "  ".join(
            v.ljust(w) if i == 0 else v.rjust(w) for i, (v, w) in enumerate(zip(row, widths, strict=True))
        )

    rule = "-" * len(line(head))
    return "\n".join([TITLE, line(head), rule, *map(line, body[:-1]), rule, line(body[-1])])


def shown(text: str) -> str:
    """A piece of source on one line: every run of white space one space."""
    return " ".join(text.split())


def survivors(measured: dict[str, Module]) -> str:
    lines = [
        f"  {one['id']}: {shown(one['old'])} -> {shown(one['new'])}"
        for module in measured.values()
        for one in module.survivors
    ]
    return "\n".join([SURVIVORS, *(lines or ["  none among the mutants run"])])


def write(path: str | None, text: str) -> None:
    """The JSON into the file `path` names, or Broken."""
    if path is None:
        return
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text + "\n", encoding="utf-8")
    except OSError as bad:
        raise Broken(
            f"{path} cannot be written ({bad.strerror})\n  why: the JSON is the report's copy for CI's"
            " artifact\n  fix: name a path in a folder that can be written to"
        ) from bad


def commit() -> str:
    done = subprocess.run(["git", "rev-parse", "HEAD"], cwd=KIT, capture_output=True, text=True, check=False)
    return done.stdout.strip() if done.returncode == 0 else "unknown"


def report(source: Path, expected: list[str], json_path: str | None, notes: list[str]) -> None:
    measured = gather(source, expected, notes)
    total = totals(measured)
    written = json.dumps(
        {
            "advisory": ADVISORY,
            "commit": commit(),
            "modules": {name: flat(one, row=True) for name, one in measured.items()},
            "totals": flat(total, row=False),
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
        print()
        print(survivors(measured))


# ---------------------------------------------------------------- self-test

OPERATORS = '''"""A docstring is never mutated."""


def every(a: int, b: list[int], name: str = "x") -> int:
    """Nor is this one, nor the annotations."""
    if a == 1 and not b:
        return a - 2
    for n in b:
        if n < a:
            continue
        a += n
        break
    print(f"{name}: {a:>3}")
    return a if b else 0
'''
OPERATORS_MUTANTS = [
    (4, "str", '"x"', "'XX' + \"x\""),  # a default value is code, where its annotation is not
    (6, "bool-swap", "a == 1 and not b", "a == 1 or not b"),
    (6, "cmp-negate", "a == 1", "a != 1"),
    (6, "cond-negate", "a == 1 and not b", "not (a == 1 and not b)"),
    (6, "num", "1", "2"),
    (6, "not-drop", "not b", "b"),
    (7, "arith", "a - 2", "a + 2"),
    (7, "return", "a - 2", "None"),
    (7, "num", "2", "3"),
    (8, "for-zero", "b", "()"),
    (9, "cmp-boundary", "n < a", "n <= a"),
    (9, "cmp-negate", "n < a", "n >= a"),
    (10, "loop-jump", "continue", "break"),
    (11, "aug", "a += n", "-="),
    (12, "loop-jump", "break", "continue"),
    (13, "call-del", 'print(f"{name}: {a:>3}")', "None"),
    (13, "str", 'f"{name}: {a:>3}"', "'XX' + f\"{name}: {a:>3}\""),
    (14, "return", "a if b else 0", "None"),
    (14, "cond-negate", "b", "not (b)"),
    (14, "num", "0", "1"),
]

CALC = '''"""The fixture's gate package: a docstring, never mutated."""

LIMIT = 3


def over(n: int) -> bool:
    return n > LIMIT


def label(n: int) -> str:
    return "big" if over(n) else "small"


def count(n: int) -> int:
    total = 0
    while n > 0:
        total += 1
        n -= 1
    return total


def unused(n: int) -> int:
    return n + 1
'''
ENTRY = """import sys

from x_gate import calc


def main() -> int:
    n = int(sys.argv[1])
    print(calc.label(n))
    return 0 if n < 10 else 2


if __name__ == "__main__":
    sys.exit(main())
"""
COPIED = 'print("copied")\n'
BARE = 'import sys\n\nsys.stdout.write("bare\\n")\n'
SIZED = 'print("sized")\n'
NAMES = 'NAMES = (\n    "a",\n    "b",\n)\n'
TESTS = """import resource
import shutil
import subprocess
import sys
from pathlib import Path

from x_gate import calc

ENTRY = Path(__file__).resolve().parent.parent / "plugin" / "scripts" / "entry.py"


def test_over():
    assert calc.over(4) and not calc.over(1)


def test_count():
    assert calc.count(2) == 2


def test_child():
    done = subprocess.run(["python3", str(ENTRY), "5"], capture_output=True, text=True, check=False)
    assert done.stdout == "big\\n"


def test_copy(tmp_path):
    shutil.copytree(ENTRY.parent, tmp_path / "plugin" / "scripts")
    copied = tmp_path / "plugin" / "scripts" / "copied.py"
    done = subprocess.run(["python3", str(copied)], capture_output=True, text=True, check=False)
    assert done.stdout == "copied\\n"


def test_bare():
    bare = ENTRY.parent / "bare.py"
    done = subprocess.run([sys.executable, "-S", str(bare)], capture_output=True, text=True, check=False)
    assert done.stdout == "bare\\n"


def test_names():
    from x_gate import names

    assert names.NAMES == ("a", "b")


def limited():
    resource.setrlimit(resource.RLIMIT_FSIZE, (4096, 4096))


def test_sized():
    sized = ENTRY.parent / "sized.py"
    done = subprocess.run(
        ["python3", str(sized)], capture_output=True, text=True, check=False, preexec_fn=limited
    )
    assert done.stdout == "sized\\n"
"""
SCRIPTS = "modules/const-x/plugin/scripts"
# what the fixture's tests do to each of its mutants, by the mutant's id less the folder
OUTCOMES = {
    # the entry file, which only the child process of test_child runs
    "entry.py:7:21:num": "killed",  # argv[2] does not exist
    "entry.py:8:4:call-del": "killed",  # nothing printed
    "entry.py:9:11:num": "survived",  # the exit code, which no test reads
    "entry.py:9:16:cmp-boundary": "survived",
    "entry.py:9:16:cmp-negate": "survived",
    "entry.py:9:20:num": "survived",
    "entry.py:9:28:num": "survived",
    "entry.py:9:11:return": "survived",
    "entry.py:12:3:cmp-negate": "killed",  # main never runs
    "entry.py:12:15:str": "killed",
    "entry.py:13:4:call-del": "killed",
    # the package: over and count run in the pytest process, label in the child alone
    # a module-level line, run at import and in the child: test_over, which the line's coverage does not
    # name, kills it
    "x_gate/calc.py:3:8:num": "killed",
    "x_gate/calc.py:7:11:cmp-boundary": "survived",
    "x_gate/calc.py:7:11:cmp-negate": "killed",
    "x_gate/calc.py:7:11:return": "killed",
    "x_gate/calc.py:11:11:return": "killed",  # by the child's output alone
    "x_gate/calc.py:11:11:str": "killed",
    "x_gate/calc.py:11:20:cond-negate": "killed",
    "x_gate/calc.py:11:33:str": "survived",  # `small` is never printed
    "x_gate/calc.py:15:12:num": "killed",
    "x_gate/calc.py:16:10:cmp-boundary": "killed",
    "x_gate/calc.py:16:10:cmp-negate": "killed",
    "x_gate/calc.py:16:14:num": "killed",
    "x_gate/calc.py:17:8:aug": "killed",
    "x_gate/calc.py:17:17:num": "killed",
    "x_gate/calc.py:18:8:aug": "timeout",  # n grows, and the loop never ends
    "x_gate/calc.py:18:13:num": "killed",
    "x_gate/calc.py:19:11:return": "killed",
    "x_gate/calc.py:23:11:arith": "not covered",  # no test calls unused
    "x_gate/calc.py:23:11:return": "not covered",
    "x_gate/calc.py:23:15:num": "not covered",
}
# what the line map once did not see, each run by one test alone: a copy of the plugin's scripts that the
# test makes and runs; a child under `python3 -S`; the continuation lines of a folded constant; a child
# under a limit on the size of the files it writes, of 4096 bytes, too few for coverage.py's data file
BLIND = {
    "copy": {"copied.py:1:0:call-del": "killed", "copied.py:1:6:str": "killed"},
    "-S": {"bare.py:3:0:call-del": "killed", "bare.py:3:17:str": "killed"},
    "folded": {"x_gate/names.py:2:4:str": "killed", "x_gate/names.py:3:4:str": "killed"},
    "size": {"sized.py:1:0:call-del": "killed", "sized.py:1:6:str": "killed"},
}
OUTCOMES.update({key: status for one in BLIND.values() for key, status in one.items()})
TESTS_COUNT = 7
TABLE = """\
module   mutants  run  killed  timeout  survived  not covered  other  score      ±  seconds
-------------------------------------------------------------------------------------------
const-a       10   10       6        1         2            1      0  70.0%   ±0.0       12
const-b      100    8       4        0         2            1      1  57.1%  ±18.1        9
-------------------------------------------------------------------------------------------
totals       110   18      10        1         4            2      1  58.3%  ±16.5       21"""


def fixture_kit(root: Path) -> None:
    """A kit of one module, `const-x`: a package the tests import through a link, and an entry file
    that only a child process runs."""
    scripts = root / SCRIPTS
    (scripts / "x_gate").mkdir(parents=True)
    (scripts / "x_gate" / "__init__.py").write_text("", encoding="utf-8")
    (scripts / "x_gate" / "calc.py").write_text(CALC, encoding="utf-8")
    (scripts / "entry.py").write_text(ENTRY, encoding="utf-8")
    (scripts / "copied.py").write_text(COPIED, encoding="utf-8")
    (scripts / "bare.py").write_text(BARE, encoding="utf-8")
    (scripts / "sized.py").write_text(SIZED, encoding="utf-8")
    (scripts / "x_gate" / "names.py").write_text(NAMES, encoding="utf-8")
    tests = root / "modules" / "const-x" / "tests"
    tests.mkdir()
    (tests / "test_x.py").write_text(TESTS, encoding="utf-8")
    (tests / "x_gate").symlink_to(Path("..") / "plugin" / "scripts" / "x_gate")
    (root / "shared").mkdir()


def digest(root: Path) -> str:
    """One hash of every file under `root`, by path and content, caches aside."""
    seen = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            seen.update(path.relative_to(root).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
    return seen.hexdigest()


def outcomes(result: dict[str, object]) -> dict[str, str]:
    rows = result["results"]
    assert isinstance(rows, list)
    return {str(row["id"]).removeprefix(SCRIPTS + "/"): str(row["status"]) for row in rows}


def result_file(folder: Path, name: str, mutants: int, statuses: dict[str, int], seconds: float) -> None:
    rows = [
        {"id": f"modules/{name}/plugin/scripts/g.py:{n}:0:num", "old": str(n), "new": str(n + 1), "status": s}
        for n, s in enumerate((s for status, count in statuses.items() for s in [status] * count), 1)
    ]
    one = {
        "module": name,
        "seed": "0",
        "budget": None if len(rows) == mutants else 5.0,
        "copies": 1,
        "tests": 3,
        "map_seconds": 1.4,
        "seconds": seconds,
        "mutants": mutants,
        "results": rows,
    }
    (folder / f"{name}.json").write_text(json.dumps(one), encoding="utf-8")


def confirmed(scratch: Path, exits: list[int]) -> str:
    """The outcome of one mutant when pytest's exits are `exits`, one per run, a run that exits 1 naming
    the one test as failed: the path a kill takes where more than one copy runs. An exit left unused
    is a run that was never made, and the outcome then says so."""
    copy = scratch / f"confirm-{'-'.join(map(str, exits))}"
    (copy / "run").mkdir(parents=True)
    target = copy / "g.py"
    target.write_text("N = 1\n", encoding="utf-8")
    left = list(exits)

    def run(
        command: list[str], cwd: Path, env: dict[str, str], limit: float
    ) -> tuple[int | None, str, float]:
        code = left.pop(0)
        if code in (0, 1):  # at any other exit no test ended, and the plugin wrote nothing
            Path(env[kit_mutation.SEEN_ENV]).write_text(
                json.dumps({"t::a": {"outcome": "passed" if code == 0 else "failed", "seconds": 0.1}}),
                encoding="utf-8",
            )
        return code, "", 0.1

    worker = kit_mutation.Worker(
        copy,
        "const-x",
        {},
        copy / "run",
        kit_mutation.LineMap({"t::a": 0.1}, {"g.py": {1: ["t::a"]}}, 0.1),
        kit_mutation.Limits(),
        True,
        run,
        1,
    )
    mutant = kit_mutation.Mutant("g.py:1:4:num", "g.py", 1, 1, (1,), "num", "1", "2", "N = (2)\n")
    result = worker.one(mutant)
    assert target.read_text(encoding="utf-8") == "N = 1\n"
    return str(result["status"]) + (f", {len(left)} run not made" if left else "")


def counting(calls: list[int]) -> kit_mutation.Run:
    """The run of a process, each call counted in `calls`."""

    def run(
        command: list[str], cwd: Path, env: dict[str, str], limit: float
    ) -> tuple[int | None, str, float]:
        calls.append(1)
        return kit_mutation.run_process(command, cwd, env, limit)

    return run


def self_test() -> int:  # noqa: C901 — one flat list of cases, each a few lines; no branch to follow
    ok = 0
    total = 0

    def case(title: str, passed: bool, evidence: str) -> None:
        nonlocal ok, total
        total += 1
        ok += 1 if passed else 0
        print(f"[{'ok' if passed else 'FAIL'}] {title}\n        {evidence}")

    limits = kit_mutation.Limits(floor=3.0, slack=0.0)
    with tempfile.TemporaryDirectory(prefix="module-mutation-self-test-") as scratch:
        base = Path(scratch)

        sample = base / "operators.py"
        sample.write_text(OPERATORS, encoding="utf-8")
        made = kit_mutation.file_mutants(sample, "operators.py")
        got = [(m.line, m.op, m.old, m.new) for m in made]
        case(
            "each operator makes its mutant; no docstring, annotation or f-string part is mutated",
            sorted(got) == sorted(OPERATORS_MUTANTS),
            f"{len(got)} mutants; unexpected {sorted(set(got) - set(OPERATORS_MUTANTS))}; missing"
            f" {sorted(set(OPERATORS_MUTANTS) - set(got))}",
        )
        lines = OPERATORS.count("\n")
        case(
            "every mutant compiles and keeps the file's line count",
            all(m.text.count("\n") == lines and compile(m.text, m.id, "exec") for m in made),
            f"{lines} lines each",
        )

        kit = base / "kit"
        fixture_kit(kit)
        before = digest(kit)
        runs_alone: list[int] = []
        whole = kit_mutation.measure(kit, "const-x", base / "whole", limits=limits, run=counting(runs_alone))
        seen = outcomes(whole)
        wrong = {k: (seen.get(k), v) for k, v in OUTCOMES.items() if seen.get(k) != v}
        case(
            "a whole run gives each mutant its outcome: killed in the pytest process, killed in a child"
            " alone, survived, timeout, not covered",
            seen == OUTCOMES,
            f"{len(seen)} mutants; (got, expected) where they differ: {wrong};"
            f" unexpected {sorted(set(seen) - set(OUTCOMES))}",
        )
        chosen = {
            str(row["id"]).removeprefix(SCRIPTS + "/"): row["tests"]
            for row in (whole["results"] if isinstance(whole["results"], list) else [])
        }
        picked = [
            chosen.get(k)
            for k in ("x_gate/calc.py:19:11:return", "x_gate/calc.py:3:8:num", "x_gate/calc.py:23:15:num")
        ]
        case(
            "a mutant meets the tests that reach it alone: one for a line of count, every test for a"
            " module-level line, none where no test reaches",
            picked == [1, TESTS_COUNT, 0],
            f"tests chosen: {picked}",
        )
        for blind, title in (
            ("copy", "a copy of the plugin's scripts that a test makes and runs counts as the module's file"),
            ("-S", "a child that a test starts under python3 -S is measured"),
            ("folded", "a continuation line of a folded constant counts as reached where its first line is"),
            ("size", "a child under a limit on the size of the files it writes is measured"),
        ):
            reached = {key: seen.get(key) for key in BLIND[blind]}
            case(
                f"{title}, so the test that kills its mutants runs them",
                reached == BLIND[blind],
                f"outcomes: {reached}",
            )
        case(
            "the kit measured is only read: every file as it was",
            digest(kit) == before,
            "one hash of the fixture kit before and after",
        )
        case(
            "every copy's files are taken back after the run",
            digest(base / "whole" / "copy-0" / SCRIPTS) == digest(kit / SCRIPTS),
            "the copy's script folder equals the kit's",
        )
        case(
            "the file of a module holds the mutants made, the tests that passed and the settings",
            (whole["mutants"], whole["tests"], whole["seed"], whole["budget"], whole["copies"])
            == (len(OUTCOMES), TESTS_COUNT, "0", None, 1),
            f"mutants {whole['mutants']}, tests {whole['tests']}",
        )

        none = kit_mutation.measure(kit, "const-x", base / "spent", budget=0.0, limits=limits)
        case(
            "a budget already spent runs no mutant and still counts them",
            none["results"] == [] and none["mutants"] == len(OUTCOMES),
            f"{none['mutants']} mutants, {len(outcomes(none))} run",
        )

        runs_two: list[int] = []
        two = kit_mutation.measure(
            kit, "const-x", base / "two", seed="another", copies=2, limits=limits, run=counting(runs_two)
        )
        rows = two["results"] if isinstance(two["results"], list) else []
        by_test = sum(1 for row in rows if row["status"] == "killed" and row["killer"] is not None)
        order = [str(row["id"]) for row in two["results"]] if isinstance(two["results"], list) else []
        first = [str(row["id"]) for row in whole["results"]] if isinstance(whole["results"], list) else []
        case(
            "two copies side by side give the same outcomes, and each kill by a failed test costs one run"
            " more, on the unmutated file",
            outcomes(two) == OUTCOMES and by_test > 0 and len(runs_two) - len(runs_alone) == by_test,
            f"{len(outcomes(two))} mutants; {len(runs_alone)} runs alone, {len(runs_two)} in two copies,"
            f" {by_test} kills by a failed test",
        )
        case(
            "the seed sets the order the mutants run in",
            sorted(order) == sorted(first) and order != first,
            f"first of seed 0: {first[:1]}; first of seed another: {order[:1]}",
        )
        case(
            "a kill whose test fails without the mutant too is unsure, and one whose test then passes is"
            " killed",
            (confirmed(base, [1, 1]), confirmed(base, [1, 0])) == ("unsure", "killed"),
            "pytest's exits 1, 1 and 1, 0",
        )
        case(
            "tests that could not be collected are a kill that is not run again, and any other exit of"
            " pytest is an error",
            (confirmed(base, [2, 0]), confirmed(base, [3])) == ("killed, 1 run not made", "error"),
            "pytest's exits 2, with a second run offered and not made, and 3",
        )

        (kit / "modules" / "const-x" / "tests" / "test_red.py").write_text(
            "def test_red():\n    assert False\n", encoding="utf-8"
        )
        try:
            kit_mutation.measure(kit, "const-x", base / "red", limits=limits)
            said = "no error"
        except kit_mutation.MutationError as bad:
            said = str(bad)
        case(
            "unmutated tests that are not green stop the measure, with why and the fix",
            said.startswith("the unmutated tests of const-x are not green (pytest exit 1):")
            and "\n  why: " in said
            and "\n  fix: run python3 scripts/check-aspects.py --run --module const-x" in said,
            said.splitlines()[0],
        )

        files = base / "files"
        files.mkdir()
        result_file(files, "const-a", 10, {"killed": 6, "timeout": 1, "survived": 2, "not covered": 1}, 10.2)
        result_file(files, "const-b", 100, {"killed": 4, "survived": 2, "not covered": 1, "unsure": 1}, 8.0)
        notes: list[str] = []
        measured = gather(files, ["const-a", "const-b", "const-c"], notes)
        printed = table(measured, totals(measured))
        case(
            "the table counts each outcome, scores a whole run without an error and a sample with one",
            printed == TITLE + "\n" + TABLE,
            "the table, line by line" if printed == TITLE + "\n" + TABLE else printed,
        )
        listed_survivors = survivors(measured).splitlines()
        case(
            "the survivors are listed in source order, each with what was replaced and by what",
            listed_survivors[:2] == [SURVIVORS, "  modules/const-a/plugin/scripts/g.py:8:0:num: 8 -> 9"]
            and len(listed_survivors) == 5,
            f"{len(listed_survivors) - 1} survivors; the first: {listed_survivors[1]}",
        )
        case(
            "a module folder with no file is a note, and the table leaves it out",
            notes == [f"const-c: no mutation file in {files}; the table leaves it out"],
            f"{notes}",
        )
        (files / "const-d.json").write_text('{"module": "const-d"}', encoding="utf-8")
        try:
            gather(files, [], [])
            said = "no error"
        except Broken as bad:
            said = str(bad)
        case(
            "a file that lacks a key is BROKEN, with why and the fix",
            said.startswith(f"{files / 'const-d.json'} cannot be read ('mutants')") and "\n  fix: " in said,
            said.splitlines()[0],
        )
    print(f"{ok}/{total} self-test cases green")
    return OK if ok == total else RED


# ---------------------------------------------------------------- entry


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="module-mutation", add_help=False, allow_abbrev=False)
    parser.add_argument("--from", dest="source")
    parser.add_argument("--json")
    parser.add_argument("--module", action="append")
    parser.add_argument("--budget", type=float)
    parser.add_argument("--seed")
    parser.add_argument("--copies", type=int)
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
        makes = [args.module, args.budget, args.seed, args.copies, args.out]
        alone = args.self_test and (args.source is not None or args.json is not None or any(makes))
        if alone or (args.source is not None and any(v is not None for v in makes)):
            raise SystemExit(2)
        if (args.budget is not None and args.budget < 0) or (args.copies is not None and args.copies < 1):
            raise SystemExit(2)
    except SystemExit:
        print(
            "BROKEN: misinvocation\n  why: an option or value the report does not know would measure"
            " something other than what was asked\n"
            "  fix: run with --self-test alone; or with --from <folder>; or with no --from and any of"
            " --module <name>, --budget <seconds>, --seed <text>, --copies <n> and --out <folder>; the"
            " last two forms with or without --json <path> or --json -"
        )
        return BROKEN
    if args.self_test:
        try:
            kit_mutation.preflight()
        except kit_mutation.MutationError as bad:
            print(f"BROKEN: {bad}")
            return BROKEN
        return self_test()
    notes: list[str] = []
    try:
        if args.source is not None:
            report(Path(args.source), listed(), args.json, notes)
        else:
            with tempfile.TemporaryDirectory(prefix="module-mutation-") as scratch:
                folder = Path(args.out) if args.out is not None else Path(scratch)
                ran = make(args.module, folder, args.seed or "0", args.budget, args.copies or 1)
                report(folder, ran, args.json, notes)
    except Broken as broken:
        print(f"BROKEN: {broken}")
        return BROKEN
    for note in notes:
        print(f"note: {note}", file=sys.stderr)
    return OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
