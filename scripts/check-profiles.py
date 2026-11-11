#!/usr/bin/env python3
"""Kit check: every profile under profiles/ is a dials file a project can take as it stands.

A profile is a prewritten constitution.yaml that the kit ships (kernel section 6). A project takes its
lines in place of writing them by hand, so a fault in a profile becomes a fault in every project
that takes it, and no gate of the kit reads the profiles: its gates read the kit's own dials file.

For every file git lists under profiles/, tracked or not, ignored ones excepted, the check holds:
  kind        the file is profiles/<kebab-case-name>.yaml, so the folder holds profiles alone;
  yaml        PyYAML's safe loader reads it, anchors and aliases resolved;
  schema      it is valid against the kernel's dials schema, by the jsonschema library, as
              scripts/check-dials-schema.py holds the kit's own file;
  style       it is in block style, as scripts/check-yaml-style.py holds the kit's own file: the
              same script, run on the profile;
  namespace   every top-level key that starts with the profile's module_prefix names a module
              folder: no module reads another key, so the schema and the scans pass it in silence;
  scan        in a throwaway repository that holds the profile as constitution.yaml and one policy
              for each namespace that claims a territory and is no module's, every scan a module
              document declares exits 0 and prints no note. The kernel's schema leaves a module's
              namespace open, so the module's own reader is the one check of its keys and values:
              exit 1 is a dial the module refuses, exit 2 a finding on a repository that has
              written nothing of its own, and a note names what the profile points at and the
              repository lacks.
And it holds that the folder has a profile at all.

Before the profiles, every scan runs once on a repository of its own, which holds no policy and a
dials file of one line, `module_prefix: const-`, the kit's own prefix. A scan that is not green there
cannot run on this machine, a tool or the shared package missing, and the check stops BROKEN instead
of blaming a profile. A profile that fails yaml
or schema is not handed to the scans: every scan would stop on the same fault.

What the check does not hold, left to review: that a profile writes no dial at its default, that
two profiles agree where they should, that a profile which sets `severity` for the gates that run in
a hook names every module that has one, and the dials of a module that has no scan, which no run
here reads.

Modes:  no arguments   check the kit's profiles;
        --self-test    prove the check: each rule red on a sample and its report typed by hand, a
                       sound sample green, each profile of the kit red with one key broken, and
                       each way the check cannot run a teaching BROKEN line.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import jsonschema
    import yaml
except ImportError as missing:
    print(f"BROKEN: {missing.name} is not installed — fix: python3 -m pip install jsonschema pyyaml")
    print("BROKEN: the check could not run — 0 profiles examined")
    sys.exit(1)

import kit_module_doc

KIT = Path(__file__).resolve().parent.parent
FOLDER = "profiles"
DIALS = "constitution.yaml"
SCHEMA = "docs/constitution/schemas/constitution.schema.json"
STYLE = "scripts/check-yaml-style.py"
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
NAME = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\.yaml")
FLOW = re.compile(r"RED: [^:]+:(\d+): (a (?:list|mapping) written in flow style: .*)")
WORKERS = 4  # scans run side by side: each reads the repository and writes nothing into it
POLICY = (  # a policy of the throwaway repository: plain prose that every module's defaults pass
    "---\nid: {id}\ntype: current-state\ntitle: A policy of the profile check\nstatus: active\n---\n\n"
    "# A policy of the profile check\n\n"
    "This policy stands for the one a project writes. It holds one rule.\n"
)

WHY_KIND = (
    "a project picks a profile by its file name, and no rule of this check reads a file of another kind"
)
WHY_YAML = (
    "a project takes the profile as its constitution.yaml, and every gate stops on a file that is no YAML"
)
WHY_SCHEMA = (
    "a project takes the profile as its constitution.yaml, and every gate refuses what the schema refuses"
)
WHY_STYLE = (
    "a dials file is read line by line and reviewed by diff, and a profile is the form a project starts from"
)
WHY_NAMESPACE = "no module reads the key, so the module it was meant for runs on its defaults in silence"
WHY_REFUSED = (
    "the kernel's schema leaves a module's namespace open, so the module's own reader is its one check"
)
WHY_FINDING = (
    "a project takes a profile before it has written a document, so a finding there is the profile's"
)
WHY_NOTE = (
    "on a repository that holds only the profile's own policies, a note names what the profile points at"
    " in vain"
)
WHY_EMPTY = "the install guide tells a project to take a profile from this folder"


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    path: str  # the profile, from the kit's root
    what: str
    why: str
    fix: str

    def render(self) -> str:
        return f"RED: {self.path}: {self.what}\n  why: {self.why}\n  fix: {self.fix}"


@dataclass(frozen=True)
class Scan:
    module: str  # the module folder's name
    entry: Path  # the scan's shell entry


@dataclass(frozen=True)
class Verdict:
    code: int
    lines: tuple[str, ...]  # what the scan printed, stdout then stderr


Runner = Callable[[Path, Scan], Verdict]


# ---------------------------------------------------------------- what the kit holds


def listed(kit: Path) -> list[str]:
    """The files git lists under profiles/, tracked or not, ignored ones excepted, from the kit's root.
    Git looks for the repository at `kit` and no higher, so a folder that is no clone is BROKEN even
    where a repository stands above it."""
    command = ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", FOLDER]
    env = os.environ | {"GIT_CEILING_DIRECTORIES": str(kit.parent)}
    try:
        result = subprocess.run(command, cwd=kit, env=env, capture_output=True, text=True, check=False)
        heard = "".join(result.stderr.strip().splitlines()[:1]) or "no message"
        failed = result.returncode != 0
    except OSError as bad:
        heard, failed = str(bad), True
    if failed:
        raise Broken(f"git cannot list {FOLDER}/ ({heard}) — fix: run the check from a clone of the kit")
    return sorted(name for name in result.stdout.split("\0") if name and (kit / name).is_file())


def scans(kit: Path) -> list[Scan]:
    """The scans the module documents declare, each by its shell entry under the module's plugin."""
    found: list[Scan] = []
    try:
        folders = kit_module_doc.module_folders(kit)
        for folder in folders:
            path = f"modules/{folder.name}/MODULE.md"
            declared, _ = kit_module_doc.enforcement((folder / "MODULE.md").read_text(encoding="utf-8"), path)
            for name in declared:
                entry = folder / "plugin" / "scripts" / f"{name.removesuffix('.py')}.sh"
                if not entry.is_file():
                    raise Broken(
                        f"{path} declares the scan `{name} --scan`, but {entry.relative_to(kit)} is no"
                        " file — fix: restore the entry, or correct the module document"
                    )
                found.append(Scan(folder.name, entry))
    except kit_module_doc.DocumentError as bad:
        raise Broken(str(bad)) from bad
    except (OSError, UnicodeDecodeError) as bad:
        raise Broken(f"a module document cannot be read ({bad}) — fix: restore the file") from bad
    if not found:
        raise Broken("no module document declares a scan — fix: run the check from a clone of the kit")
    return found


def rules(kit: Path) -> dict[str, Any]:
    """The kernel's dials schema, checked against its own draft."""
    try:
        schema = json.loads((kit / SCHEMA).read_text(encoding="utf-8"))
    except (OSError, ValueError) as bad:
        raise Broken(f"{SCHEMA} cannot be read as JSON ({bad}) — fix: restore the schema") from bad
    if not isinstance(schema, dict):
        raise Broken(f"{SCHEMA} is not a JSON object — fix: restore the schema")
    try:
        jsonschema.validators.validator_for(schema).check_schema(schema)
    except jsonschema.SchemaError as bad:
        raise Broken(f"{SCHEMA} breaks its own draft ({bad.message}) — fix: repair the schema") from bad
    return schema


# ---------------------------------------------------------------- the rules that read the file alone


def kind(path: str) -> list[Finding]:
    name = path.removeprefix(f"{FOLDER}/")
    if NAME.fullmatch(name):
        return []
    fix = f"name it {FOLDER}/<kebab-case-name>.yaml if it is a profile, or move it out of {FOLDER}/"
    return [Finding(path, "the file is no profile by its name", WHY_KIND, fix)]


def read(path: str, text: str) -> tuple[dict[str, Any] | None, list[Finding]]:
    """The profile's data, or the finding that it is no YAML mapping."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as bad:
        said = " ".join(str(bad).split())
        return None, [Finding(path, f"the file is no YAML ({said})", WHY_YAML, "repair the YAML")]
    if not isinstance(data, dict):
        what = "the file holds no mapping of keys"
        return None, [Finding(path, what, WHY_YAML, "write the keys of a dials file, module_prefix first")]
    return data, []


def schema_findings(path: str, data: dict[str, Any], schema: dict[str, Any]) -> list[Finding]:
    validator = jsonschema.validators.validator_for(schema)(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: [str(p) for p in e.absolute_path])
    return [
        Finding(
            path,
            f"{where}: {error.message}",
            WHY_SCHEMA,
            f"change {where} to what {SCHEMA} allows",
        )
        for error in errors
        for where in ["/".join(str(p) for p in error.absolute_path) or "the file"]
    ]


def style_findings(kit: Path, path: str, file: Path) -> list[Finding]:
    """The flow collections of the profile, as the kit's style check reports them on the file."""
    result = subprocess.run(
        [sys.executable, str(kit / STYLE), str(file)], capture_output=True, text=True, check=False
    )
    if result.returncode == EXIT_GREEN:
        return []
    found = [FLOW.fullmatch(line) for line in result.stdout.splitlines()]
    hits = [hit for hit in found if hit is not None]
    if result.returncode != EXIT_RED or not hits:
        said = (result.stderr.strip() or result.stdout.strip()).splitlines()[:1]
        raise Broken(
            f"{STYLE} could not read {path} ({''.join(said) or f'exit {result.returncode}'}) — fix: run"
            f" python3 {STYLE} {path} and repair what it names"
        )
    fix = f"python3 {STYLE} --fix {path} rewrites the file in block style"
    return [Finding(path, f"line {hit[1]}: {hit[2]}", WHY_STYLE, fix) for hit in hits]


def namespace_findings(path: str, data: dict[str, Any], modules: Sequence[str]) -> list[Finding]:
    prefix = data.get("module_prefix")
    if not isinstance(prefix, str):
        return []
    fix = "rename the key to the name of a module folder under modules/, or delete it"
    return [
        Finding(path, f"the key `{key}` opens with the module prefix and names no module", WHY_NAMESPACE, fix)
        for key in data
        if isinstance(key, str) and key.startswith(prefix) and key != "module_prefix" and key not in modules
    ]


# ---------------------------------------------------------------- the rule that runs the scans


def policies(data: dict[str, Any]) -> dict[str, str]:
    """The policy files of the throwaway repository, path to text: the root at root_policy, and
    beside it one per namespace that claims a territory and is no module's, named by its id."""
    root = data.get("root_policy")
    if not isinstance(root, str) or not root.endswith(".md"):
        return {}
    prefix = str(data.get("module_prefix", ""))
    home = Path(root).parent
    ids = [
        key
        for key, value in data.items()
        if isinstance(key, str)
        and isinstance(value, dict)
        and "territory" in value
        and not (prefix and key.startswith(prefix))
    ]
    files = {str(home / f"{name}.md"): POLICY.format(id=name) for name in ids}
    files.setdefault(root, POLICY.format(id=Path(root).stem))
    return files


def repository(folder: Path, dials: str, files: dict[str, str]) -> None:
    """A git repository at `folder` with the dials file and the policy files committed on main."""
    env = os.environ | {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    identity = ["-c", "user.name=profile check", "-c", "user.email=profile-check@example.invalid"]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / DIALS).write_text(dials, encoding="utf-8")
    for name, text in files.items():
        (folder / name).parent.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text(text, encoding="utf-8")
    for command in (
        ["git", "init", "--quiet", "-b", "main"],
        ["git", "add", "-A"],
        ["git", *identity, "commit", "--quiet", "-m", "The profile and its policies"],
    ):
        done = subprocess.run(command, cwd=folder, env=env, capture_output=True, text=True, check=False)
        if done.returncode != 0:
            said = (done.stderr.strip() or done.stdout.strip()).splitlines()[:1]
            raise Broken(
                f"`{' '.join(command[:2])}` failed in the throwaway repository"
                f" ({''.join(said) or 'no message'}) — fix: check that git runs here"
            )


def run_scan(kit: Path) -> Runner:
    """The runner of the real scans: the entry under `sh`, the kit's shared code first on the path."""

    def run(folder: Path, scan: Scan) -> Verdict:
        env = os.environ | {
            "PYTHONPATH": str(kit / "shared"),
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
        }
        for name in ("CLAUDE_PLUGIN_DATA", "CLAUDE_PLUGIN_ROOT", "CLAUDE_PROJECT_DIR"):
            env.pop(name, None)
        try:
            done = subprocess.run(
                ["sh", str(scan.entry), "--scan"],
                cwd=folder,
                env=env,
                capture_output=True,
                text=True,
                check=False,
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            return Verdict(EXIT_BROKEN, ("the scan did not end within 300 seconds",))
        return Verdict(done.returncode, tuple((done.stdout + done.stderr).splitlines()))

    return run


def verdicts(folder: Path, entries: Sequence[Scan], run: Runner) -> list[Verdict]:
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        return list(pool.map(lambda scan: run(folder, scan), entries))


def first(lines: Sequence[str], opening: str) -> str:
    """The first printed line that opens with `opening`, else the last line, else a word for none."""
    for line in lines:
        if line.startswith(opening):
            return line
    return lines[-1] if lines else "it printed nothing"


def scan_findings(path: str, scan: Scan, verdict: Verdict) -> list[Finding]:
    module = scan.module
    dial = f"section 7 of modules/{module}/MODULE.md gives the dial"
    if verdict.code == EXIT_RED:
        what = f"the scan of {module} is red on a new repository that holds the profile: "
        fix = f"correct the dial of the profile that the line names, as {dial}, or take the dial out"
        return [Finding(path, what + first(verdict.lines, "RED:"), WHY_FINDING, fix)]
    if verdict.code != EXIT_GREEN:
        what = f"{module} cannot read the profile: "
        fix = f"correct the key or the value that the line names, as {dial}"
        return [Finding(path, what + first(verdict.lines, "BROKEN:"), WHY_REFUSED, fix)]
    fix = "name in the profile what the note asks for, or take out the key that points at it"
    return [
        Finding(path, f"the scan of {module} prints a note on a new repository: {line}", WHY_NOTE, fix)
        for line in verdict.lines
        if line.startswith("note:")
    ]


def control(folder: Path, prefix: str, entries: Sequence[Scan], run: Runner) -> None:
    """Every scan green on a repository whose dials file is the module prefix alone, else BROKEN."""
    repository(folder, f"module_prefix: {prefix}\n", {})
    for scan, verdict in zip(entries, verdicts(folder, entries, run), strict=True):
        if verdict.code != EXIT_GREEN:
            opening = "RED:" if verdict.code == EXIT_RED else "BROKEN:"
            raise Broken(
                f"the scan of {scan.module} is not green on an empty repository, exit {verdict.code}"
                f" ({first(verdict.lines, opening)}) — fix: install what the line names, then run"
                f" `sh scripts/gate-list.sh --run profiles` again"
            )


# ---------------------------------------------------------------- the check


@dataclass(frozen=True)
class Kit:
    root: Path
    schema: dict[str, Any]
    modules: tuple[str, ...]
    entries: tuple[Scan, ...]
    run: Runner


def profile(kit: Kit, path: str, file: Path, scratch: Path) -> list[Finding]:
    """The findings of one profile; `scratch` is where its throwaway repository is made."""
    found = kind(path)
    if found:
        return found
    try:
        text = file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as bad:
        return [Finding(path, f"the file cannot be read as UTF-8 text ({bad})", WHY_YAML, "repair the file")]
    data, found = read(path, text)
    if data is None:
        return found
    found = schema_findings(path, data, kit.schema)
    sound = not found
    found += style_findings(kit.root, path, file)
    found += namespace_findings(path, data, kit.modules)
    if sound:
        repository(scratch, text, policies(data))
        for scan, verdict in zip(kit.entries, verdicts(scratch, kit.entries, kit.run), strict=True):
            found += scan_findings(path, scan, verdict)
    return found


def check(kit: Kit, paths: Sequence[str], folder: Path | None = None) -> tuple[list[Finding], int]:
    """The findings over `paths`, files of profiles/ named from the kit's root and read under
    `folder`, the kit's root by default; and how many of them are profiles by their name."""
    base = kit.root if folder is None else folder
    if not any(NAME.fullmatch(path.removeprefix(f"{FOLDER}/")) for path in paths):
        fix = f"write {FOLDER}/<kebab-case-name>.yaml, a dials file a project can take as it stands"
        empty = Finding(f"{FOLDER}/", "the folder holds no profile", WHY_EMPTY, fix)
        return [empty, *[finding for path in paths for finding in kind(path)]], 0
    found: list[Finding] = []
    with tempfile.TemporaryDirectory() as tmp:
        control(Path(tmp) / "control", "const-", kit.entries, kit.run)
        for number, path in enumerate(paths):
            found += profile(kit, path, base / path, Path(tmp) / f"profile-{number}")
    return found, sum(1 for path in paths if not kind(path))


def report(found: list[Finding], profiles: int, entries: int) -> int:
    counts = f"{profiles} profile(s) examined against {SCHEMA}, {entries} scan(s) run on each sound one"
    if found:
        for finding in found:
            print(finding.render())
        print(f"RED: {len(found)} finding(s) — {counts}")
        return EXIT_RED
    print(f"GREEN: every profile is a dials file a project can take as it stands — {counts}")
    return EXIT_GREEN


def load(root: Path) -> Kit:
    entries = scans(root)
    modules = tuple(folder.name for folder in kit_module_doc.module_folders(root))
    return Kit(root, rules(root), modules, tuple(entries), run_scan(root))


# ---------------------------------------------------------------- the self-test

SOUND = (
    "root_policy: docs/policies/pol-0001-root-policy.md\n"
    "module_prefix: const-\n"
    "pol-0001-root-policy:\n"
    "  territory:\n"
    '    - "docs/policies/**"\n'
    "pol-0002-records:\n"
    "  territory:\n"
    '    - "docs/decisions/**"\n'
    "const-decision-records:\n"
    "  severity: warn\n"
    "  record_policies:\n"
    "    - pol-0002-records\n"
    "const-catalogs:\n"
    "  catalogs:\n"
    "    - prefix: pol\n"
    "      width: 4\n"
    "      territory:\n"
    '        - "docs/policies/**"\n'
)


def sample(kit: Kit, files: dict[str, str]) -> tuple[list[Finding], int]:
    """The check over throwaway files, named from a kit's root: `profiles/<name>` to text."""
    with tempfile.TemporaryDirectory() as tmp:
        for name, text in files.items():
            (Path(tmp) / name).parent.mkdir(parents=True, exist_ok=True)
            (Path(tmp) / name).write_text(text, encoding="utf-8")
        return check(kit, sorted(files), Path(tmp))


def said(kit: Kit, files: dict[str, str]) -> tuple[int, list[str]]:
    """The report of the check over throwaway files: its exit and its lines."""
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        code = report(*sample(kit, files), len(kit.entries))
    return code, printed.getvalue().splitlines()


def canned(answers: dict[str, Verdict]) -> Runner:
    """A runner that runs nothing: green on the control, and on a profile the module's answer."""

    def run(folder: Path, scan: Scan) -> Verdict:
        green = Verdict(EXIT_GREEN, (f"GREEN: {scan.module}: 0 document(s) examined",))
        return green if folder.name == "control" else answers.get(scan.module, green)

    return run


def literal_cases(kit: Kit) -> list[tuple[str, bool]]:
    """Each rule's report, typed by hand, on a sample that breaks that rule alone; no scan runs."""
    one = Scan("const-one", kit.root / "one.sh")
    tail = f"examined against {SCHEMA}, 1 scan(s) run on each sound one"
    x = "profiles/x.yaml"

    def lines(files: dict[str, str], answers: dict[str, Verdict] | None = None) -> tuple[int, list[str]]:
        toy = Kit(
            kit.root,
            kit.schema,
            ("const-one", "const-decision-records", "const-catalogs"),
            (one,),
            canned(answers or {}),
        )
        return said(toy, files)

    cases: list[tuple[str, dict[str, str], dict[str, Verdict] | None, list[str]]] = [
        (
            "a sound profile is green",
            {x: SOUND},
            None,
            [f"GREEN: every profile is a dials file a project can take as it stands — 1 profile(s) {tail}"],
        ),
        (
            "a file that is no profile by its name is red, the profile beside it still examined",
            {x: SOUND, "profiles/Notes.txt": "a note\n"},
            None,
            [
                "RED: profiles/Notes.txt: the file is no profile by its name",
                f"  why: {WHY_KIND}",
                "  fix: name it profiles/<kebab-case-name>.yaml if it is a profile, or move it out of"
                " profiles/",
                f"RED: 1 finding(s) — 1 profile(s) {tail}",
            ],
        ),
        (
            "a folder with no profile is red",
            {},
            None,
            [
                "RED: profiles/: the folder holds no profile",
                f"  why: {WHY_EMPTY}",
                "  fix: write profiles/<kebab-case-name>.yaml, a dials file a project can take as it stands",
                f"RED: 1 finding(s) — 0 profile(s) {tail}",
            ],
        ),
        (
            "a profile that holds no mapping is red",
            {x: "- one\n- two\n"},
            None,
            [
                "RED: profiles/x.yaml: the file holds no mapping of keys",
                f"  why: {WHY_YAML}",
                "  fix: write the keys of a dials file, module_prefix first",
                f"RED: 1 finding(s) — 1 profile(s) {tail}",
            ],
        ),
        (
            "a profile the schema refuses is red, and no scan reads it",
            {x: SOUND.replace("module_prefix: const-\n", "module_prefix: const\n")},
            {"const-one": Verdict(EXIT_RED, ("RED: never reached",))},
            [
                "RED: profiles/x.yaml: module_prefix: 'const' does not match"
                " '^[a-z][a-z0-9]*(-[a-z0-9]+)*-$'",
                f"  why: {WHY_SCHEMA}",
                f"  fix: change module_prefix to what {SCHEMA} allows",
                f"RED: 1 finding(s) — 1 profile(s) {tail}",
            ],
        ),
        (
            "a list in flow style is red, its line named",
            {
                x: SOUND.replace(
                    '  territory:\n    - "docs/decisions/**"\n', '  territory: ["docs/decisions/**"]\n'
                )
            },
            None,
            [
                'RED: profiles/x.yaml: line 7: a list written in flow style: ["docs/decisions/**"]',
                f"  why: {WHY_STYLE}",
                f"  fix: python3 {STYLE} --fix profiles/x.yaml rewrites the file in block style",
                f"RED: 1 finding(s) — 1 profile(s) {tail}",
            ],
        ),
        (
            "a key with the module prefix that names no module is red",
            {x: SOUND + "const-nothing:\n  severity: warn\n"},
            None,
            [
                "RED: profiles/x.yaml: the key `const-nothing` opens with the module prefix and names no"
                " module",
                f"  why: {WHY_NAMESPACE}",
                "  fix: rename the key to the name of a module folder under modules/, or delete it",
                f"RED: 1 finding(s) — 1 profile(s) {tail}",
            ],
        ),
        (
            "a scan that cannot read the profile is red, its own line shown",
            {x: SOUND},
            {
                "const-one": Verdict(
                    EXIT_BROKEN, ("BROKEN: const-one: `sevrity` is no dial", "BROKEN: 0 examined")
                )
            },
            [
                "RED: profiles/x.yaml: const-one cannot read the profile: BROKEN: const-one: `sevrity` is no"
                " dial",
                f"  why: {WHY_REFUSED}",
                "  fix: correct the key or the value that the line names, as section 7 of"
                " modules/const-one/MODULE.md gives the dial",
                f"RED: 1 finding(s) — 1 profile(s) {tail}",
            ],
        ),
        (
            "a scan that is red on the new repository is red, its first finding shown",
            {x: SOUND},
            {"const-one": Verdict(EXIT_RED, ("RED: a.md:1: a finding", "  why: w", "RED: 1 finding(s)"))},
            [
                "RED: profiles/x.yaml: the scan of const-one is red on a new repository that holds the"
                " profile: RED: a.md:1: a finding",
                f"  why: {WHY_FINDING}",
                "  fix: correct the dial of the profile that the line names, as section 7 of"
                " modules/const-one/MODULE.md gives the dial, or take the dial out",
                f"RED: 1 finding(s) — 1 profile(s) {tail}",
            ],
        ),
        (
            "a green scan that prints a note is red",
            {x: SOUND},
            {
                "const-one": Verdict(
                    EXIT_GREEN, ("note: `plc-9` names no policy", "GREEN: const-one: 0 examined")
                )
            },
            [
                "RED: profiles/x.yaml: the scan of const-one prints a note on a new repository: note: `plc-9`"
                " names no policy",
                f"  why: {WHY_NOTE}",
                "  fix: name in the profile what the note asks for, or take out the key that points at it",
                f"RED: 1 finding(s) — 1 profile(s) {tail}",
            ],
        ),
    ]
    results: list[tuple[str, bool]] = []
    code, got = lines({x: "root_policy: [docs\n"})  # the parser's own words follow, so the opening is held
    opens = "RED: profiles/x.yaml: the file is no YAML ("
    tail_lines = [f"  why: {WHY_YAML}", "  fix: repair the YAML", f"RED: 1 finding(s) — 1 profile(s) {tail}"]
    results.append(
        (
            "a profile that is no YAML is red",
            code == EXIT_RED and got[0].startswith(opens) and got[1:] == tail_lines,
        )
    )
    for name, files, answers, wanted in cases:
        code, got = lines(files, answers)
        ok = got == wanted and code == (EXIT_GREEN if wanted[0].startswith("GREEN") else EXIT_RED)
        results.append((name, ok))
        if not ok:
            print("\n".join(["        got:", *got]))
    return results


def real_cases(kit: Kit) -> list[tuple[str, bool]]:
    """The real scans on samples: a sound one green, and each fault only a module's reader sees red."""
    x = "profiles/x.yaml"
    cases: list[tuple[str, str, list[str]]] = [
        ("the sound sample is green under the real scans", SOUND, []),
        (
            "a misspelt dial is red by its module's reader",
            SOUND.replace("  catalogs:\n", "  catalog:\n"),
            ["const-catalogs cannot read the profile: "],
        ),
        (
            "a value a module refuses is red by its reader",
            SOUND.replace("severity: warn", "severity: loud"),
            ["const-decision-records cannot read the profile: "],
        ),
        (
            "a record policy that names no policy is red by the note",
            SOUND.replace("    - pol-0002-records\n", "    - pol-0002-record\n"),
            ["the scan of const-decision-records prints a note on a new repository: "],
        ),
        (
            "a dial the check's own policy text fails is red by the finding",
            SOUND + "const-questions:\n  markers:\n    - stands\n",
            ["the scan of const-questions is red on a new repository that holds the profile: "],
        ),
    ]
    results: list[tuple[str, bool]] = []
    for name, text, wanted in cases:
        found, _ = sample(kit, {x: text})
        got = [finding.what for finding in found]
        ok = len(got) == len(wanted) and all(
            what.startswith(start) for what, start in zip(got, wanted, strict=True)
        )
        results.append((name, ok))
        if not ok:
            print("\n".join(["        got:", *got]))
    return results


def kit_cases(kit: Kit) -> list[tuple[str, bool]]:
    """Each profile of the kit, one key broken: a dial of the first module's namespace misspelt
    where the profile has one, else the module prefix; the fault is red and names the profile."""
    results: list[tuple[str, bool]] = []
    for path in [p for p in listed(kit.root) if not kind(p)]:
        text = (kit.root / path).read_text(encoding="utf-8")
        hit = re.search(r"(?m)^const-[a-z-]+:[^\n]*\n(?:[ \t]*#[^\n]*\n)*  ([a-z_]+):", text)
        if hit is not None:
            broken = text[: hit.start(1)] + hit[1] + "x" + text[hit.end(1) :]
            wanted = " cannot read the profile: "
        else:
            broken = text.replace("module_prefix: const-", "module_prefix: const", 1)
            wanted = "module_prefix: "
        found, _ = sample(kit, {path: broken})
        ok = (
            broken != text
            and len(found) >= 1
            and all(f.path == path for f in found)
            and wanted in found[0].what
        )
        results.append((f"{path} with one key broken is red", ok))
        if not ok:
            print("\n".join(["        got:", *[finding.what for finding in found]]))
    return results


def broken_cases(kit: Kit) -> list[tuple[str, bool]]:
    """Each way the check cannot run is a BROKEN line that names the fix."""
    one = Scan("const-one", kit.root / "one.sh")

    def stops(name: str, wanted: str, act: Callable[[], object]) -> tuple[str, bool]:
        try:
            act()
        except Broken as broken:
            return name, wanted in str(broken) and "fix:" in str(broken)
        return name, False

    def never(folder: Path, scan: Scan) -> Verdict:
        return Verdict(EXIT_BROKEN, ("BROKEN: const-one: vale is not installed",))

    toy = Kit(kit.root, kit.schema, kit.modules, (one,), never)
    with tempfile.TemporaryDirectory() as tmp:
        empty = Path(tmp)
        (empty / "docs").mkdir()
        (empty / "docs" / "bad.json").write_text('{"type": 3}', encoding="utf-8")
        return [
            stops(
                "a scan that is not green on an empty repository",
                "the scan of const-one is not green on an empty repository, exit 1 (BROKEN: const-one: vale",
                lambda: sample(toy, {"profiles/x.yaml": SOUND}),
            ),
            stops("a folder that is no clone of the kit", "has no modules/ directory", lambda: scans(empty)),
            stops("a schema that is absent", "cannot be read as JSON", lambda: rules(empty)),
            stops("a folder git cannot list", "git cannot list profiles/", lambda: listed(empty)),
        ]


def self_test() -> int:
    kit = load(KIT)
    results = [*literal_cases(kit), *real_cases(kit), *kit_cases(kit), *broken_cases(kit)]
    for name, ok in results:
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    failed = sum(1 for _, ok in results if not ok)
    print(f"{len(results) - failed}/{len(results)} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-profiles", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 profiles examined")
        return EXIT_BROKEN
    try:
        if args.self_test:
            return self_test()
        kit = load(KIT)
        return report(*check(kit, listed(KIT)), len(kit.entries))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 profiles examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
