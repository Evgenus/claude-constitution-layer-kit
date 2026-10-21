"""Kit tooling, never shipped in a module: a module's fixtures run under coverage.py, and what they reach.

`scripts/check-aspects.py --run` runs a module's runner — pytest over its tests/ —
under coverage.py when the environment variable `CONSTITUTION_KIT_COVERAGE` names a folder, and writes
`<folder>/<module>.json`; the kit's CI sets it in each module's job, and `scripts/module-coverage.py`
reads the files (decision
dec-0089-module-coverage-report). An empty or absent variable runs the runner plain.

The run is `python3 -m coverage run -m pytest …`, never pytest-cov, with branch coverage and
`patch = subprocess`: the fixtures run the gates as child processes, `sh` entry points that call
`python3`, and each such child is measured too. So that a gate's `python3` is the measured interpreter, a
folder holding a `python3` that calls the one running the check goes first on the runner's PATH. A child
started with an environment of its own, without coverage's variable, is not measured, and its lines count
as missed. coverage.py measures Python alone: a module's `.sh` files are not in these numbers. The
measured code is the module's own Python under modules/<module>/plugin/scripts and the shared
constitution_layer_kit
it links, read at shared/constitution_layer_kit; when the run left coverage data, a file there that no run
imports counts with all its lines missed. Nothing else is measured: not the runner, not the module's tests/ or
hooks/, not the shared test files.

The file of one module, the JSON keys as written:
  module        the module folder's name;
  runner_exit   pytest's exit: 0 when every item was green, 1 when one was red, another when it could not run;
  seconds       the run's wall-clock time, whole seconds;
  files         per measured file, its path from the kit root and coverage.py's own lists of it:
                `executed_lines`, `missing_lines`, `executed_branches`, `missing_branches`, a branch
                a pair of line numbers.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ENV = "CONSTITUTION_KIT_COVERAGE"
WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "gates.yml"
PINNED = re.compile(r'"coverage==([^"\s]+)"')


def fix_install() -> str:
    """The install command of the version the kit's CI pins, read from the workflow, which alone names
    it, so that no copy drifts; a plain command naming the workflow when it cannot be read there."""
    try:
        found = PINNED.search(WORKFLOW.read_text(encoding="utf-8"))
    except OSError:
        found = None
    if found is None:
        return f"{sys.executable} -m pip install coverage, at the version .github/workflows/gates.yml pins"
    return f'{sys.executable} -m pip install "coverage=={found[1]}"'


LISTS = ("executed_lines", "missing_lines", "executed_branches", "missing_branches")


class CoverageError(Exception):
    """A coverage run cannot be made or read: the message says what failed and the fix."""


def wanted() -> Path | None:
    """The folder the environment asks the files for, or None."""
    value = os.environ.get(ENV, "")
    return Path(value) if value else None


def prepare(root: Path, module: str, work: Path) -> tuple[list[str], dict[str, str]]:
    """The command prefix and the environment that run a runner under coverage.py, its data kept in
    `work`; CoverageError when coverage.py is not installed for this interpreter."""
    found = subprocess.run(
        [sys.executable, "-c", "import coverage"], capture_output=True, text=True, check=False
    )
    if found.returncode != 0:
        raise CoverageError(
            f"{ENV} asks for coverage, and coverage.py is not installed for {sys.executable}"
            f" — fix: {fix_install()}, or unset {ENV}"
        )
    rc = work / "coveragerc"
    sources = [root / "modules" / module / "plugin" / "scripts", root / "shared" / "constitution_layer_kit"]
    rc.write_text(
        "[run]\nbranch = true\nparallel = true\npatch = subprocess\n"
        f"data_file = {work / 'data'}\n"
        "source =\n" + "".join(f"    {source}\n" for source in sources),
        encoding="utf-8",
    )
    shim = work / "bin"
    shim.mkdir()
    python3 = shim / "python3"
    python3.write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n', encoding="utf-8")
    python3.chmod(0o755)
    env = dict(os.environ)
    env["PATH"] = f"{shim}{os.pathsep}{env.get('PATH', '')}"
    return [sys.executable, "-m", "coverage", "run", "--rcfile", str(rc)], env


def cli(work: Path, *args: str) -> None:
    done = subprocess.run(
        [sys.executable, "-m", "coverage", *args, "--rcfile", str(work / "coveragerc")],
        cwd=work,
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode != 0:
        said = (done.stderr or done.stdout).strip().splitlines()
        raise CoverageError(
            f"`coverage {args[0]}` exited {done.returncode}: {said[-1] if said else 'no output'}"
            f" — fix: {fix_install()}, the version the check is written against; at that version"
            " already, repair the cause that coverage.py's own line, quoted before this fix, names"
        )


def save(root: Path, module: str, work: Path, out: Path, runner_exit: int, seconds: int) -> Path:
    """Combine the run's data in `work` and write `<out>/<module>.json`; CoverageError when a step fails.
    A run that left no data is written with no files, so the report has nothing to count for the module
    and says so in a note."""
    files: dict[str, dict[str, list[object]]] = {}
    if any(work.glob("data.*")):
        cli(work, "combine", "-q")
        report = work / "coverage.json"
        cli(work, "json", "-q", "-o", str(report))
        try:
            measured = json.loads(report.read_text(encoding="utf-8"))["files"]
            for name, one in measured.items():
                path = Path(name).resolve().relative_to(root.resolve()).as_posix()
                files[path] = {key: one.get(key, []) for key in LISTS}
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as bad:
            raise CoverageError(
                f"coverage.py's JSON in {report} cannot be read ({bad}) — fix: {fix_install()}, the"
                " version whose JSON the check reads; at that version already, repair what the error in"
                " the parentheses names"
            ) from bad
    target = out / f"{module}.json"
    try:
        out.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(
                {"module": module, "runner_exit": runner_exit, "seconds": seconds, "files": files},
                indent=1,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError as bad:
        raise CoverageError(
            f"{target} cannot be written ({bad.strerror})"
            f" — fix: name in {ENV} a folder that can be written to"
        ) from bad
    return target
