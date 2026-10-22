#!/usr/bin/env python3
"""Kit check: the shared code builds into the distribution `constitution-layer-kit`, which installs and
imports in a fresh virtual environment (decision dec-0099-shared-code-installed-as-a-pip-package, R19).

The distribution is described by `shared/pyproject.toml`. The check copies `shared/` into a throwaway
folder, so that the build leaves nothing in the tree, and builds a wheel from the copy. The build tool is
the one `[build-system] requires` names, installed once into a throwaway virtual environment, and the wheel
is built there with pip's build isolation off: a failure to fetch the build tool is told apart from a
failure of the build. The wheel is then installed into a second, fresh virtual environment, one with no
system packages, and the environment's own Python, in isolated mode and from a folder that holds nothing,
imports `constitution_layer_kit`. Three things are held, each a RED finding with the fix when it fails:
  - the version the installed distribution reports, `importlib.metadata`'s, equals `__version__` of the
    package, the version's one source: two sources of one pin drift;
  - the package imports from the environment's site-packages and not from a source folder: an import
    that finds the source would hide a package the wheel left out;
  - PyYAML is installed beside the package, which only its declared dependency can have put there.
A `shared/pyproject.toml` that is no TOML or names no build requirements, a build that fails, a wheel
that holds no importable package and a distribution of another name are RED too, each with its own text.
This is the one check of the kit that needs the package index: pip fetches the build tool and the
dependency from it. A Python without `venv` or `ensurepip`, a build tool or a dependency that pip cannot
fetch, a child process that cannot start or runs longer than five minutes, and a missing
`shared/pyproject.toml` are BROKEN with the fix, never a pass. Every folder the check makes is removed
when it ends.

Modes:  no arguments   check the distribution built from shared/ of the kit;
        --self-test    prove the check on toy distributions in throwaway folders, whose build tool is
                       installed once and shared by their builds: a right one green with its literal line;
                       a version the metadata names that differs from `__version__`, one with no PyYAML
                       among its dependencies, and one with the package left out of its wheel, each red
                       with its literal lines; a `pyproject.toml` that is no TOML, one with no build
                       requirements and a build that fails, red; each judgment of the installed facts
                       alone, the origin of the import among them; a Python without `venv`, a build tool
                       and a dependency that pip cannot fetch, a missing `pyproject.toml` and a
                       misinvocation, BROKEN with literal lines; every folder removed after a green, a red
                       and a BROKEN run.
Exit:   0 green; 2 a finding; 1 the check could not run.
Output: the GREEN line, or the RED findings and their count, or the BROKEN line and the closing line, on
        stdout.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
SOURCE = "shared"  # the folder the distribution is built from
PROJECT = "shared/pyproject.toml"
DISTRIBUTION = "constitution-layer-kit"
PACKAGE = "constitution_layer_kit"
DEPENDENCY = "PyYAML"
TIMEOUT = 300  # seconds one child may run: pip retries a dead network for minutes
PIP_FLAGS = ("--disable-pip-version-check", "--no-input")
UNBUILT = (
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "build",
    "dist",
    "*.egg-info",
    "*.pyc",
)
BUILD_TOOL = "setuptools>=77"  # the self-test's toys; the kit's own run reads `[build-system] requires`
WHY_BUILD = (
    "the file is what pip reads to build the shared code, so a project outside this kit installs the shared"
    " code only from a distribution it describes"
)
CLOSING = "BROKEN: the check could not run — no distribution was examined"

# Run by the environment's own Python, isolated, from a folder that holds nothing: what the installed
# package and its metadata say, as one JSON object.
PROBE = """
import importlib.metadata
import json
import sysconfig

facts = {"purelib": sysconfig.get_path("purelib"), "platlib": sysconfig.get_path("platlib")}
try:
    import constitution_layer_kit as package
except Exception as bad:
    facts["import_error"] = f"{type(bad).__name__}: {bad}"
else:
    facts["file"] = package.__file__
    facts["dunder"] = getattr(package, "__version__", None)
for key, name in (("version", "constitution-layer-kit"), ("pyyaml", "PyYAML")):
    try:
        facts[key] = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        facts[key] = None
print(json.dumps(facts))
"""

Finder = Callable[[str], object | None]


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    what: str
    why: str
    fix: str

    def render(self) -> str:
        return f"RED: {self.what}\n  why: {self.why}\n  fix: {self.fix}"


class Defect(Exception):
    """The distribution is wrong at a stage that stops the check there; it carries the finding."""

    def __init__(self, finding: Finding) -> None:
        super().__init__(finding.what)
        self.finding = finding


@dataclass(frozen=True)
class Facts:
    """What the fresh environment says about the installed distribution."""

    purelib: str
    platlib: str
    import_error: str | None  # the import of the package failed with this
    file: str | None  # where the package was imported from
    dunder: str | None  # `__version__` of the package
    version: str | None  # the version `importlib.metadata` reports for the distribution
    pyyaml: str | None  # the version of PyYAML installed in the environment


@dataclass(frozen=True)
class Verdict:
    findings: list[Finding]
    facts: Facts | None  # None when the check stopped before the import


def child_env() -> dict[str, str]:
    """The caller's environment, save the variables that put another interpreter's folders on the path."""
    return {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV")}


def shown(command: Sequence[str | Path]) -> str:
    """The command on one line, cut at 100 characters: the probe's program stands in it whole."""
    line = " ".join(str(part).replace("\n", " ") for part in command)
    return line if len(line) <= 100 else line[:99] + "…"


def run(command: Sequence[str | Path], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [str(part) for part in command],
            cwd=cwd,
            env=child_env(),
            capture_output=True,
            text=True,
            check=False,
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired as late:
        raise Broken(
            f"`{shown(command)}` ran longer than {TIMEOUT} seconds — fix: check the network and the package"
            " index, then run the check again"
        ) from late
    except OSError as bad:
        raise Broken(
            f"`{shown(command)}` could not start ({bad.strerror}) — fix: repair the Python that runs the"
            " check, then run it again"
        ) from bad


def tail(done: subprocess.CompletedProcess[str]) -> str:
    """Why a child failed, on one line: the last two of the error lines it printed on stderr, else the last
    two lines of what it printed."""
    printed = [line.strip() for line in (done.stderr or done.stdout).splitlines() if line.strip()]
    errors = [line for line in printed if line.lower().startswith("error")]
    return " | ".join((errors or printed)[-2:]) or "no output"


def preflight(find: Finder = importlib.util.find_spec) -> None:
    """The modules that make a virtual environment with a pip of its own, else BROKEN with the fix."""
    for name in ("venv", "ensurepip"):
        if find(name) is None:
            raise Broken(
                f"this Python has no module {name}, which makes a virtual environment with a pip in it"
                " — fix: install it (on Debian and Ubuntu, `apt install python3-venv`), then run the check"
                " again"
            )


def make_env(folder: Path, packages: Sequence[str], pip_args: Sequence[str]) -> Path:
    """A virtual environment with no system packages and pip, the `packages` installed in it; its Python."""
    made = run([sys.executable, "-m", "venv", folder])
    if made.returncode != 0:
        raise Broken(
            f"`python3 -m venv` failed ({tail(made)}) — fix: install what makes a virtual environment (on"
            " Debian and Ubuntu, `apt install python3-venv`), then run the check again"
        )
    python = folder / "bin" / "python"
    if packages:
        got = run([python, "-m", "pip", "install", *PIP_FLAGS, "--quiet", *pip_args, *packages])
        if got.returncode != 0:
            raise Broken(
                f"pip could not install the build requirements {', '.join(packages)} ({tail(got)}) — fix:"
                " check that the package index is reachable, since pip fetches the build tool from it, and"
                " that `[build-system] requires` of the project names a package that exists, then run the"
                " check again"
            )
    return python


def read_requires(source: Path) -> list[str]:
    """`[build-system] requires` of the source's pyproject.toml; a file that is missing is BROKEN, one
    that is no TOML or names no requirement is a defect of the distribution."""
    try:
        data = tomllib.loads((source / "pyproject.toml").read_text(encoding="utf-8"))
    except FileNotFoundError as missing:
        raise Broken(f"{PROJECT} is missing — fix: restore it from the kit's history") from missing
    except OSError as bad:
        raise Broken(f"{PROJECT} cannot be read ({bad.strerror}) — fix: make it readable") from bad
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as bad:
        raise Defect(
            Finding(f"{PROJECT} is no valid TOML ({bad})", WHY_BUILD, "repair the file, then run the check")
        ) from bad
    system = data.get("build-system")
    requires = system.get("requires") if isinstance(system, dict) else None
    if not (isinstance(requires, list) and requires and all(isinstance(each, str) for each in requires)):
        raise Defect(
            Finding(
                f"{PROJECT} names no build requirements in [build-system]",
                WHY_BUILD,
                'add `[build-system]` with `requires = ["setuptools>=77"]` and'
                ' `build-backend = "setuptools.build_meta"`',
            )
        )
    return [str(each) for each in requires]


def build_wheel(python: Path, src: Path, dist: Path) -> Path:
    """The one wheel pip builds from the copy, in the environment that holds the build tool."""
    done = run(
        [python, "-m", "pip", "wheel", *PIP_FLAGS, "--no-deps", "--no-build-isolation", "-w", dist, src]
    )
    if done.returncode != 0:
        raise Defect(
            Finding(
                f"the distribution does not build: pip exited {done.returncode} — {tail(done)}",
                "a distribution that does not build cannot be installed by a project outside this kit",
                f"repair what the line above names in {PROJECT} or in the package, then run the check again",
            )
        )
    wheels = sorted(dist.glob("*.whl"))
    if len(wheels) != 1:
        raise Broken(
            f"pip built {len(wheels)} wheels from the copy of {SOURCE}/, and the check reads one — fix: run"
            " the check again, and report it if it stays"
        )
    return wheels[0]


def install(python: Path, wheel: Path, install_args: Sequence[str]) -> None:
    done = run([python, "-m", "pip", "install", *PIP_FLAGS, "--quiet", *install_args, wheel])
    if done.returncode != 0:
        raise Broken(
            f"pip could not install the built wheel ({tail(done)}) — fix: check that the package index is"
            " reachable, since pip fetches the dependencies the wheel declares from it, and that each"
            " dependency in [project] of the project names a package that exists, then run the check again"
        )


def text_of(data: dict[str, object], key: str) -> str | None:
    value = data.get(key)
    return value if isinstance(value, str) else None


def probe(python: Path, folder: Path) -> Facts:
    folder.mkdir()
    done = run([python, "-I", "-c", PROBE], cwd=folder)
    if done.returncode != 0:
        raise Broken(
            f"the new environment's Python could not read the installed package ({tail(done)}) — fix: run"
            " the check again, and report it if it stays"
        )
    try:
        data = json.loads(done.stdout)
    except ValueError as bad:
        raise Broken(
            f"the new environment's Python printed no JSON object ({tail(done)}) — fix: run the check again,"
            " and report it if it stays"
        ) from bad
    if not isinstance(data, dict):
        raise Broken("the new environment's Python printed no JSON object — fix: run the check again")
    return Facts(
        purelib=text_of(data, "purelib") or "",
        platlib=text_of(data, "platlib") or "",
        import_error=text_of(data, "import_error"),
        file=text_of(data, "file"),
        dunder=text_of(data, "dunder"),
        version=text_of(data, "version"),
        pyyaml=text_of(data, "pyyaml"),
    )


def inside(file: str, roots: Sequence[str]) -> bool:
    place = Path(file).resolve()
    return any(place.is_relative_to(Path(root).resolve()) for root in roots)


def judge(facts: Facts) -> list[Finding]:
    """The findings of what the fresh environment says, in a fixed order."""
    found: list[Finding] = []
    if facts.import_error is not None:
        found.append(
            Finding(
                f"the installed distribution cannot import {PACKAGE} ({facts.import_error})",
                "a wheel that holds no importable package installs the metadata and nothing a module can"
                " import, so every module outside this kit would stop at its first import",
                f'list the package in [tool.setuptools] packages of {PROJECT} as `["{PACKAGE}"]`, and keep'
                f" the package folder named {PACKAGE} beside the file",
            )
        )
    elif facts.dunder is None:
        found.append(
            Finding(
                f"the installed package {PACKAGE} declares no __version__",
                "the version is the one pin a module's check reads and a release tag names, and it has one"
                " source, the package's __version__",
                f'declare `__version__ = "<major>.<minor>.<patch>"` in {PACKAGE}/__init__.py',
            )
        )
    if facts.version is None:
        found.append(
            Finding(
                f"no distribution named {DISTRIBUTION} is installed",
                "a project asks pip for the distribution by this name, so the name is part of the promise",
                f"name the project `{DISTRIBUTION}` under [project] in {PROJECT}",
            )
        )
    elif facts.dunder is not None and facts.version != facts.dunder:
        found.append(
            Finding(
                f"the installed distribution reports version {facts.version}, and __version__ of the package"
                f" is {facts.dunder}",
                "the version is one pin that a release tag names and a module's check compares, so two"
                " sources of it drift apart",
                f'give {PROJECT} `dynamic = ["version"]` and `[tool.setuptools.dynamic] version = {{attr ='
                f' "{PACKAGE}.__version__"}}`, and no `version` key under [project]',
            )
        )
    if facts.file is not None and not inside(facts.file, (facts.purelib, facts.platlib)):
        found.append(
            Finding(
                f"{PACKAGE} was imported from {facts.file}, outside the site-packages of the new environment"
                f" ({facts.purelib})",
                "an import that finds the source folder would hide a package the wheel left out, and the"
                " check would pass for a distribution nobody can install",
                "remove from the distribution what points the new environment at a source folder, such as a"
                " .pth file, so that the package it installs is the one in its site-packages",
            )
        )
    if facts.pyyaml is None:
        found.append(
            Finding(
                f"{DEPENDENCY} was not installed with the distribution",
                f"the shared code imports {DEPENDENCY}, so a project that installs the distribution alone"
                " would fail at the first gate it runs",
                f'declare `dependencies = ["{DEPENDENCY}>=6.0"]` under [project] in {PROJECT}',
            )
        )
    return found


def check_source(
    source: Path,
    build_python: Path | None = None,
    pip_args: Sequence[str] = (),
    install_args: Sequence[str] = (),
    parent: Path | None = None,
) -> Verdict:
    """Build the distribution of `source` from a copy, install it into a fresh environment, import it there.
    `build_python` is a Python that holds the build tool, else one is made from `[build-system] requires`;
    `pip_args` go to the install of the build tool and `install_args` to that of the wheel; `parent`
    holds the throwaway folder. The folder is removed, whatever the outcome."""
    with tempfile.TemporaryDirectory(prefix="check-shared-package-", dir=parent) as tmp:
        work = Path(tmp).resolve()
        try:
            requires = read_requires(source)
            python = build_python or make_env(work / "build-env", requires, pip_args)
            shutil.copytree(source, work / "src", symlinks=True, ignore=shutil.ignore_patterns(*UNBUILT))
            wheel = build_wheel(python, work / "src", work / "dist")
        except Defect as defect:
            return Verdict([defect.finding], None)
        env = make_env(work / "env", [], ())
        install(env, wheel, install_args)
        facts = probe(env, work / "probe")
    return Verdict(judge(facts), facts)


def report(verdict: Verdict) -> int:
    if verdict.findings:
        for item in verdict.findings:
            print(item.render())
        print(f"RED: {len(verdict.findings)} finding(s) — the distribution of {SOURCE}/ is not as owed")
        return EXIT_RED
    version = verdict.facts.version if verdict.facts else None
    print(
        f"GREEN: {DISTRIBUTION} {version} builds, installs into a fresh virtual environment and imports"
        f" from its site-packages there, with {DEPENDENCY} installed as its dependency"
    )
    return EXIT_GREEN


def run_kit(kit: Path) -> int:
    preflight()
    return report(check_source(kit / SOURCE))


class Cases:
    """The self-test's tally: one line per case, the total counted as the cases run."""

    def __init__(self) -> None:
        self.total = 0
        self.failed = 0

    def check(self, ok: bool, text: str) -> None:
        self.total += 1
        self.failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {text}")


VERSION = "1.0.0"  # the toys' own
BASE_PYPROJECT = """[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "constitution-layer-kit"
{version}
dependencies = {dependencies}

[tool.setuptools]
packages = {packages}
{dynamic}"""
DYNAMIC = '[tool.setuptools.dynamic]\nversion = {attr = "constitution_layer_kit.__version__"}\n'


def toy(
    root: Path,
    *,
    version: str = 'dynamic = ["version"]',
    dynamic: str = DYNAMIC,
    dependencies: str = '["PyYAML>=6.0"]',
    packages: str = '["constitution_layer_kit"]',
    dunder: str = VERSION,
) -> Path:
    """A toy distribution: the package folder named as the real one, its pyproject.toml filled by the
    keywords."""
    (root / PACKAGE).mkdir(parents=True)
    (root / PACKAGE / "__init__.py").write_text(f'__version__ = "{dunder}"\n', encoding="utf-8")
    (root / PACKAGE / "py.typed").write_text("", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        BASE_PYPROJECT.format(version=version, dynamic=dynamic, dependencies=dependencies, packages=packages),
        encoding="utf-8",
    )
    return root


def printed(verdict: Verdict) -> tuple[int, list[str]]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = report(verdict)
    return code, out.getvalue().splitlines()


def facts_of(**given: str | None) -> Facts:
    """Facts of a right installation, with the keywords changed."""
    right: dict[str, str | None] = {
        "purelib": "/env/lib/site-packages",
        "platlib": "/env/lib/site-packages",
        "import_error": None,
        "file": "/env/lib/site-packages/constitution_layer_kit/__init__.py",
        "dunder": VERSION,
        "version": VERSION,
        "pyyaml": "6.0.2",
    }
    merged = right | given
    return Facts(
        purelib=merged["purelib"] or "",
        platlib=merged["platlib"] or "",
        import_error=merged["import_error"],
        file=merged["file"],
        dunder=merged["dunder"],
        version=merged["version"],
        pyyaml=merged["pyyaml"],
    )


def self_test() -> int:
    cases = Cases()
    preflight()
    self_test_judgments(cases)
    self_test_broken(cases)
    with tempfile.TemporaryDirectory(prefix="check-shared-package-test-") as tmp:
        root = Path(tmp).resolve()
        build_python = make_env(root / "build-env", [BUILD_TOOL], ())  # the build tool, installed once
        self_test_toys(cases, root, build_python)
        self_test_stops(cases, root, build_python)
    print(f"{cases.total - cases.failed}/{cases.total} cases green")
    return EXIT_GREEN if cases.failed == 0 else EXIT_RED


def self_test_judgments(cases: Cases) -> None:
    """Each hold on the facts of an installation alone, no build: right is green, each wrong one red."""
    cases.check(judge(facts_of()) == [], "the facts of a right installation are green")
    right_folder = "/env/lib/site-packages"
    wrong: list[tuple[str, dict[str, str | None], list[str]]] = [
        (
            "an installed version that differs from __version__",
            {"version": "2.0.0"},
            [
                "RED: the installed distribution reports version 2.0.0, and __version__ of the package is"
                f" {VERSION}",
                "  why: the version is one pin that a release tag names and a module's check compares, so two"
                " sources of it drift apart",
                '  fix: give shared/pyproject.toml `dynamic = ["version"]` and `[tool.setuptools.dynamic]'
                ' version = {attr = "constitution_layer_kit.__version__"}`, and no `version` key under'
                " [project]",
            ],
        ),
        (
            "an import from a source folder",
            {"file": "/work/src/constitution_layer_kit/__init__.py"},
            [
                "RED: constitution_layer_kit was imported from /work/src/constitution_layer_kit/__init__.py,"
                f" outside the site-packages of the new environment ({right_folder})",
                "  why: an import that finds the source folder would hide a package the wheel left out, and"
                " the check would pass for a distribution nobody can install",
                "  fix: remove from the distribution what points the new environment at a source folder, such"
                " as a .pth file, so that the package it installs is the one in its site-packages",
            ],
        ),
        (
            "no PyYAML",
            {"pyyaml": None},
            [
                "RED: PyYAML was not installed with the distribution",
                "  why: the shared code imports PyYAML, so a project that installs the distribution alone"
                " would fail at the first gate it runs",
                '  fix: declare `dependencies = ["PyYAML>=6.0"]` under [project] in shared/pyproject.toml',
            ],
        ),
        (
            "a package that does not import",
            {"import_error": "ModuleNotFoundError: No module named 'constitution_layer_kit'", "file": None},
            [
                "RED: the installed distribution cannot import constitution_layer_kit"
                " (ModuleNotFoundError: No module named 'constitution_layer_kit')",
                "  why: a wheel that holds no importable package installs the metadata and nothing a module"
                " can import, so every module outside this kit would stop at its first import",
                "  fix: list the package in [tool.setuptools] packages of shared/pyproject.toml as"
                ' `["constitution_layer_kit"]`, and keep the package folder named constitution_layer_kit'
                " beside the file",
            ],
        ),
        (
            "a package with no __version__",
            {"dunder": None},
            [
                "RED: the installed package constitution_layer_kit declares no __version__",
                "  why: the version is the one pin a module's check reads and a release tag names, and it has"
                " one source, the package's __version__",
                '  fix: declare `__version__ = "<major>.<minor>.<patch>"` in'
                " constitution_layer_kit/__init__.py",
            ],
        ),
        (
            "a distribution of another name",
            {"version": None},
            [
                "RED: no distribution named constitution-layer-kit is installed",
                "  why: a project asks pip for the distribution by this name, so the name is part of the"
                " promise",
                "  fix: name the project `constitution-layer-kit` under [project] in shared/pyproject.toml",
            ],
        ),
    ]
    for name, given, said in wrong:
        found = judge(facts_of(**given))
        cases.check(
            [item.render().splitlines() for item in found] == [said], f"{name} is red, with its literal lines"
        )
    both = judge(facts_of(version="2.0.0", pyyaml=None))
    cases.check(
        [item.what.split(" ")[0] for item in both] == ["the", "PyYAML"],
        "two wrong facts are two findings, in a fixed order: the version, then PyYAML",
    )
    climbing = judge(
        facts_of(file="/env/lib/site-packages/../../elsewhere/constitution_layer_kit/__init__.py")
    )
    cases.check(
        [item.what.split(" outside ")[0] for item in climbing]
        == [
            "constitution_layer_kit was imported from"
            " /env/lib/site-packages/../../elsewhere/constitution_layer_kit/__init__.py,"
        ],
        "an import that climbs out of site-packages by `..` is outside it",
    )


def broken_text(action: Callable[..., object], *given: object) -> str:
    """The message of the BROKEN that `action(*given)` raises, else `no BROKEN`."""
    try:
        action(*given)
    except Broken as broken:
        return str(broken)
    return "no BROKEN"


def without(name: str) -> Finder:
    """A finder that finds every module save `name`."""
    return lambda wanted: None if wanted == name else object()


def self_test_broken(cases: Cases) -> None:
    """The failures that are no verdict on the distribution, as their literal BROKEN lines."""
    venv_fix = "install it (on Debian and Ubuntu, `apt install python3-venv`), then run the check again"
    for name in ("venv", "ensurepip"):
        cases.check(
            broken_text(preflight, without(name))
            == f"this Python has no module {name}, which makes a virtual environment with a pip in it"
            f" — fix: {venv_fix}",
            f"a Python without {name} is its literal BROKEN line",
        )
    cases.check(broken_text(preflight) == "no BROKEN", "the Python that runs the check passes the preflight")
    with tempfile.TemporaryDirectory(prefix="check-shared-package-test-") as tmp:
        root = Path(tmp).resolve()
        cases.check(
            broken_text(lambda: check_source(root / "nowhere", parent=root))
            == "shared/pyproject.toml is missing — fix: restore it from the kit's history",
            "a source with no pyproject.toml is its literal BROKEN line",
        )
        said = broken_text(lambda: make_env(root / "no-index", [BUILD_TOOL], ["--no-index"]))
        cases.check(
            said.startswith("pip could not install the build requirements setuptools>=77 (")
            and said.endswith(
                ") — fix: check that the package index is reachable, since pip fetches the build tool from"
                " it, and that `[build-system] requires` of the project names a package that exists, then"
                " run the check again"
            ),
            "a build tool that pip cannot fetch is a BROKEN line that names the requirement and pip's reason",
        )
        cases.check(
            broken_text(lambda: probe(Path("/nowhere/python"), root / "probe")).startswith(
                "`/nowhere/python -I -c "
            ),
            "a Python that cannot start is a BROKEN line that names the command",
        )
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):  # argparse's usage
        code = main(["--bogus"])
    cases.check(
        code == EXIT_BROKEN
        and out.getvalue().splitlines()
        == [
            "BROKEN: misinvocation — fix: run with no arguments, or with --self-test",
            CLOSING,
        ],
        "a misinvocation is its literal BROKEN lines, exit 1",
    )


def self_test_toys(cases: Cases, root: Path, build_python: Path) -> None:
    """Toy distributions built, installed and imported for real, with the build tool `build_python`
    holds."""
    summary = "RED: 1 finding(s) — the distribution of shared/ is not as owed"
    parent = root / "work"
    parent.mkdir()
    code, lines = printed(check_source(toy(root / "right"), build_python, parent=parent))
    cases.check(
        code == EXIT_GREEN
        and lines
        == [
            f"GREEN: constitution-layer-kit {VERSION} builds, installs into a fresh virtual environment and"
            " imports from its site-packages there, with PyYAML installed as its dependency"
        ],
        "a right distribution is green, with its literal line",
    )
    code, lines = printed(
        check_source(
            toy(root / "version", version='version = "2.0.0"', dynamic=""), build_python, parent=parent
        )
    )
    cases.check(
        code == EXIT_RED
        and lines[0]
        == "RED: the installed distribution reports version 2.0.0, and __version__ of the package is 1.0.0"
        and lines[-1] == summary
        and len(lines) == 4,
        "a version in the metadata that differs from __version__ is red: one finding, its lines, the count",
    )
    code, lines = printed(check_source(toy(root / "yaml", dependencies="[]"), build_python, parent=parent))
    cases.check(
        code == EXIT_RED
        and lines
        == [
            "RED: PyYAML was not installed with the distribution",
            "  why: the shared code imports PyYAML, so a project that installs the distribution alone would"
            " fail at the first gate it runs",
            '  fix: declare `dependencies = ["PyYAML>=6.0"]` under [project] in shared/pyproject.toml',
            summary,
        ],
        "a distribution that does not declare PyYAML is red, with its literal lines",
    )
    code, lines = printed(check_source(toy(root / "left-out", packages="[]"), build_python, parent=parent))
    cases.check(
        code == EXIT_RED
        and lines[0]
        == "RED: the installed distribution cannot import constitution_layer_kit"
        " (ModuleNotFoundError: No module named 'constitution_layer_kit')"
        and lines[-1] == summary
        and len(lines) == 4,
        "a package left out of the wheel is red: the import fails in the new environment",
    )
    cases.check(
        sorted(parent.iterdir()) == [],
        "every folder of a green and of two red runs is removed",
    )


def self_test_stops(cases: Cases, root: Path, build_python: Path) -> None:
    """The distributions that stop the check before an installation, and the installation pip cannot make."""
    parent = root / "stops"
    parent.mkdir()
    code, lines = printed(
        check_source(toy(root / "no-build", packages='["nowhere"]'), build_python, parent=parent)
    )
    cases.check(
        code == EXIT_RED
        and lines[0].startswith("RED: the distribution does not build: pip exited 1 — ")
        and lines[1:3]
        == [
            "  why: a distribution that does not build cannot be installed by a project outside this kit",
            "  fix: repair what the line above names in shared/pyproject.toml or in the package, then run the"
            " check again",
        ],
        "a build that fails is red, with pip's last lines in the finding",
    )
    code, lines = printed(
        check_source(toy(root / "no-toml", packages="[", dynamic=""), build_python, parent=parent)
    )
    cases.check(
        code == EXIT_RED
        and lines[0].startswith("RED: shared/pyproject.toml is no valid TOML (")
        and lines[-2] == "  fix: repair the file, then run the check",
        "a pyproject.toml that is no TOML is red, before any build",
    )
    plain = toy(root / "no-requires")
    (plain / "pyproject.toml").write_text('[project]\nname = "constitution-layer-kit"\n', encoding="utf-8")
    code, lines = printed(check_source(plain, build_python, parent=parent))
    cases.check(
        code == EXIT_RED
        and lines[0] == "RED: shared/pyproject.toml names no build requirements in [build-system]"
        and lines[2]
        == '  fix: add `[build-system]` with `requires = ["setuptools>=77"]` and'
        ' `build-backend = "setuptools.build_meta"`',
        "a pyproject.toml with no build requirements is red, with the fix typed out",
    )
    said = broken_text(
        lambda: check_source(toy(root / "offline"), build_python, install_args=["--no-index"], parent=parent)
    )
    cases.check(
        said.startswith("pip could not install the built wheel (")
        and said.endswith(
            ") — fix: check that the package index is reachable, since pip fetches the dependencies the wheel"
            " declares from it, and that each dependency in [project] of the project names a package that"
            " exists, then run the check again"
        ),
        "a dependency that pip cannot fetch is a BROKEN line, not a finding",
    )
    cases.check(
        sorted(parent.iterdir()) == [],
        "every folder of two reds before an install, and of a BROKEN run, is removed",
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-shared-package", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print(CLOSING)
        return EXIT_BROKEN
    try:
        return self_test() if args.self_test else run_kit(KIT)
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print(CLOSING)
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
