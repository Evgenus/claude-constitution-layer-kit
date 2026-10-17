"""Kit tooling, never shipped in a module: the module evals and their receipts (decision
dec-0093-module-evals-with-local-receipts).

A module ships its eval cases in `evals/` at its root, which `claude plugin eval` runs. The kit keeps one
receipt per module in `scripts/eval-receipts.json`, written by `scripts/run-evals.py` and held by
`scripts/check-eval-receipts.py`. This file is what both read the same way:

  `eval_model`   the model the runs use: the text of `scripts/eval-model`, with at most one final line break
                 removed, one model id of lowercase letters, digits, `.` and `-`.
  `eval_files`   what a session of the module loads, and its cases: every file git tracks under
                 `modules/<module>/`, links followed, save `MODULE.md`, `README.md` and `INSTALL.md` at the
                 module's root and the folders `tests/` and `evals/results/`. A link to a folder stands for
                 every file git tracks under the folder it leads to, each named through the link; a link to a
                 file, for that file. A link that leads outside the kit, or to nothing, is an `EvalError`.
  `eval_hash`    `sha256:` and the hex digest over those files in name order, each its name, a zero byte, its
                 size in decimal, a zero byte and its bytes, as the working tree holds them.
  `dirty`        the files of `eval_files` that differ from HEAD or that git does not track yet, read by
                 `git status`: a run is made only on committed files, so that its receipt names what CI sees.
  `read_receipts` / `write_receipts`  the receipts file: one JSON object, a key per module, each entry an
                 object with `hash`, `claude` (the version of `scripts/claude-code.version` the run used),
                 `model`, and `attempts`, a list of objects each with `at` (UTC, ISO 8601), `cases`, `passed`
                 and `score`. An attempt passes when it ran at least one case and every case passed. A file
                 that is absent reads as no receipts; one that is no such object is an `EvalError`. The file
                 is written with sorted keys, an indent of 2 and a final line break.

Every failure is an `EvalError` whose message says what failed and the fix.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

EVAL_MODEL = "scripts/eval-model"
RECEIPTS = "scripts/eval-receipts.json"
EVALS = "evals"
LEFT_OUT_FILES = ("MODULE.md", "README.md", "INSTALL.md")  # at the module's root
LEFT_OUT_FOLDERS = ("tests", "evals/results")
MODEL = re.compile(r"[a-z0-9][a-z0-9.-]*")
HASH = re.compile(r"sha256:[0-9a-f]{64}")
MODEL_FIX = "write the one model id the runs use, e.g. claude-opus-5-5, as the file's only line"
RECEIPTS_FIX = (
    "restore the file from git (git checkout -- scripts/eval-receipts.json), then run the evals again"
)


class EvalError(Exception):
    """The evals or their receipts cannot be read; the message says why and how to fix it."""


@dataclass(frozen=True)
class Attempt:
    at: str
    cases: int
    passed: int
    score: float

    @property
    def passing(self) -> bool:
        return self.cases > 0 and self.passed == self.cases


@dataclass(frozen=True)
class Receipt:
    hash: str
    claude: str
    model: str
    attempts: tuple[Attempt, ...]


def eval_model(root: Path) -> str:
    """The model id of `<root>/scripts/eval-model`, else `EvalError` with the fix."""
    path = root / EVAL_MODEL
    try:
        text = path.read_bytes().decode("utf-8", errors="replace")
    except OSError as bad:
        raise EvalError(f"{EVAL_MODEL} cannot be read ({bad.strerror}) — fix: {MODEL_FIX}") from bad
    model = text.removesuffix("\n")
    if not MODEL.fullmatch(model):
        raise EvalError(f"{EVAL_MODEL} is not one model id ({text!r}) — fix: {MODEL_FIX}")
    return model


def git(root: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if done.returncode != 0:
        said = done.stderr.strip().splitlines()
        raise EvalError(
            f"git {args[0]} exited {done.returncode} ({said[-1] if said else 'no output'})"
            " — fix: run the command from a clone of the kit"
        )
    return done.stdout


def tracked(root: Path, folder: str) -> list[str]:
    """The paths git tracks under `folder`, relative to `root`, in git's order."""
    return [p for p in git(root, "ls-files", "-z", "--", folder).split("\0") if p]


def left_out(name: str) -> bool:
    return name in LEFT_OUT_FILES or any(name == f or name.startswith(f"{f}/") for f in LEFT_OUT_FOLDERS)


def eval_files(root: Path, module: str) -> list[tuple[str, Path]]:
    """Each file a session of the module loads, as (its name within the module, its path on disk), in
    name order."""
    base = f"modules/{module}"
    kit = root.resolve()
    files: dict[str, Path] = {}
    for path in tracked(root, base):
        name = path[len(base) + 1 :]
        if left_out(name):
            continue
        where = root / path
        if not where.is_symlink():
            files[name] = where
            continue
        target = where.resolve()
        if not target.exists() or not target.is_relative_to(kit):
            raise EvalError(
                f"{path} is a link to {target}, which is not a file or folder of the kit"
                " — fix: point the link at the kit's own source"
            )
        if target.is_file():
            files[name] = target
            continue
        inside = target.relative_to(kit).as_posix()
        for under in tracked(root, inside):
            files[f"{name}/{under[len(inside) + 1 :]}"] = root / under
    return sorted(files.items())


def eval_hash(root: Path, module: str) -> str:
    digest = hashlib.sha256()
    for name, path in eval_files(root, module):
        data = path.read_bytes()
        digest.update(name.encode("utf-8") + b"\0" + str(len(data)).encode("ascii") + b"\0" + data)
    return f"sha256:{digest.hexdigest()}"


def dirty(root: Path, module: str) -> list[str]:
    """The kit paths behind the module's eval files that differ from HEAD or are not tracked yet."""
    kit = root.resolve()
    paths = sorted({path.resolve().relative_to(kit).as_posix() for _, path in eval_files(root, module)})
    said = git(
        root, "status", "--porcelain", "-z", "--untracked-files=all", "--", f"modules/{module}", *paths
    )
    fields = [e for e in said.split("\0") if e]
    changed: set[str] = set()
    skip = False
    for entry in fields:  # a rename or copy names its source in the field after its own entry
        if skip:
            skip = False
            continue
        if len(entry) > 3:
            changed.add(entry[3:])
        skip = entry[:1] in ("R", "C")
    return [p for p in sorted(changed) if not left_out(p.removeprefix(f"modules/{module}/"))]


def number(value: object, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise EvalError(f"{RECEIPTS}: {what} is not a number — fix: {RECEIPTS_FIX}")
    return float(value)


def attempt_of(value: object, what: str) -> Attempt:
    if not isinstance(value, dict) or not isinstance(value.get("at"), str):
        raise EvalError(f"{RECEIPTS}: {what} is no object with a string `at` — fix: {RECEIPTS_FIX}")
    cases, passed = number(value.get("cases"), f"{what} cases"), number(value.get("passed"), f"{what} passed")
    if not cases.is_integer() or not passed.is_integer() or not 0 <= passed <= cases:
        raise EvalError(
            f"{RECEIPTS}: {what} counts are not whole numbers, passed ≤ cases — fix: {RECEIPTS_FIX}"
        )
    return Attempt(value["at"], int(cases), int(passed), number(value.get("score"), f"{what} score"))


def receipt_of(module: str, value: object) -> Receipt:
    texts = ("hash", "claude", "model")
    if not isinstance(value, dict) or not all(isinstance(value.get(k), str) for k in texts):
        raise EvalError(
            f"{RECEIPTS}: the entry of {module} is no object with string `hash`, `claude` and `model`"
            f" — fix: {RECEIPTS_FIX}"
        )
    attempts = value.get("attempts")
    if not isinstance(attempts, list):
        raise EvalError(f"{RECEIPTS}: the entry of {module} has no `attempts` list — fix: {RECEIPTS_FIX}")
    found = tuple(attempt_of(a, f"attempt {n} of {module}") for n, a in enumerate(attempts, 1))
    return Receipt(value["hash"], value["claude"], value["model"], found)


def read_receipts(root: Path) -> dict[str, Receipt]:
    path = root / RECEIPTS
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as bad:
        raise EvalError(f"{RECEIPTS} cannot be read as JSON ({bad}) — fix: {RECEIPTS_FIX}") from bad
    if not isinstance(data, dict):
        raise EvalError(f"{RECEIPTS} is no JSON object — fix: {RECEIPTS_FIX}")
    return {module: receipt_of(module, entry) for module, entry in data.items()}


def write_receipts(root: Path, receipts: dict[str, Receipt]) -> None:
    data = {
        module: {
            "hash": r.hash,
            "claude": r.claude,
            "model": r.model,
            "attempts": [
                {"at": a.at, "cases": a.cases, "passed": a.passed, "score": a.score} for a in r.attempts
            ],
        }
        for module, r in receipts.items()
    }
    (root / RECEIPTS).write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
