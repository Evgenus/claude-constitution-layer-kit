#!/usr/bin/env python3
"""Kit check: no installed component of a module names a place in someone's project.

The grep of requirement A12.1, as the row words it since decision
dec-0056-portability-grep-and-gate-lists. It reads the installed components of every module —
the files git lists under `skills/`, `hooks/`, `scripts/`, `commands/`, `agents/`, the install
note `INSTALL.md` and `.claude-plugin/`, never the module document `MODULE.md` nor `tests/` —
and the shared gate code under `shared/const_gate/`, which every module installs as its
`scripts/const_gate`. A symbolic link is read at its source, once. A module is every folder under
`modules/` whose name opens with neither a dot nor an underscore.

A finding is one of these forms, outside a public URL:
  - a path under a home directory: `/Users/…`, `/home/…`, `~/`, `$HOME/…`, `${HOME}/…` or a
    Windows user folder;
  - a `file:/` link;
  - a relative path with a slash and a file extension or a glob, `docs/notes.md`, `docs/**` or
    `**/docs/*.md`, that is no file or directory of the plugin. A glob whose parts before the last
    are all wildcards and whose last part names files by an extension, `**/*.md`, names no
    particular place, so it is no finding; `**/decisions` names a folder and is one.
    `constitution.yaml`, the one repository path a module may name, has no slash and so is never
    one.
Not read: in Markdown, fenced blocks and inline code, which show an example to adapt, not a
location. There is no exemption marker; an interpreter line is read as any other, so
`#!/usr/bin/env` passes and a home path there does not.

A heuristic, as the row says: the bare-repository run on defaults stays the gate of record. Not
seen here — a folder named with neither an extension nor a glob, a system path such as `/srv/…`,
a home path in a form not listed — is held by review, and by that run where the path acts on a
bare repository.

Modes:  no arguments   check the kit;
        --self-test    prove the check on a throwaway tree: each form red with its count typed
                       by hand and green once fixed; every place not read stays green; the report
                       of one finding as literal lines with exit 2; a file that is not UTF-8 as a
                       BROKEN line.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
INSTALLED = ("skills/", "hooks/", "scripts/", "commands/", "agents/", "INSTALL.md", ".claude-plugin/")
SHARED = "shared/const_gate"

URL = re.compile(r"https?://[^\s)>\"'`]+")
HOME = re.compile(
    r"(?<![\w.$}~-])/(?:Users|home)/[^\s)>\"'`]*"
    r"|\$\{?HOME\}?/[^\s)>\"'`]*"
    r"|\b[A-Za-z]:[\\/]Users[\\/][^\s)>\"'`]*"
)
TILDE = re.compile(r"~/")
FILE_LINK = re.compile(r"\bfile:/")
RELATIVE = re.compile(r"(?<![\w/.$}{~:*-])((?:[\w.*-]+/)+[\w.*-]*)")
WILDCARD = re.compile(r"\*+")
NAMES_A_FILE = re.compile(r"(\.[A-Za-z]{1,5}$|\*)")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)+?\1")
WHY = "a module installs into any project, so it names no place in one (law 2 of CLAUDE.md)"
FIXES = {
    "home": "name the place in words, or read it from the dials file",
    "tilde": "name the place in words, or read it from the dials file",
    "file": "link a public URL, or name the document in words",
    "relative": "write it `${CLAUDE_PLUGIN_ROOT}`-relative if it is the plugin's, read it from the dials"
    " file if it is the project's, or show it in a fenced example",
}
WHAT = {
    "home": "a path under a home directory",
    "tilde": "a path under `~/`",
    "file": "a `file:/` link",
    "relative": "a relative path that is no file of the plugin",
}


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str
    text: str

    def render(self) -> str:
        return (
            f"RED: {self.path}:{self.line}: {WHAT[self.kind]}, '{self.text}'\n"
            f"  why: {WHY}\n"
            f"  fix: {FIXES[self.kind]}"
        )


def listed(root: Path, where: str) -> list[str]:
    try:
        done = subprocess.run(
            ["git", "ls-files", "-z", "--", where], cwd=root, capture_output=True, text=True, check=False
        )
    except FileNotFoundError as missing:
        raise Broken("git is not on PATH — fix: install git, then run the check again") from missing
    if done.returncode != 0:
        first = (done.stderr.splitlines() or ["no message"])[0]
        raise Broken(f"git ls-files failed: {first} — fix: run the check from a checkout of the kit")
    return sorted(p for p in done.stdout.split("\0") if p)


def read(root: Path, path: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except UnicodeDecodeError as bad:
        raise Broken(
            f"{path} is not UTF-8 ({bad.reason} at byte {bad.start}) — fix: save it as UTF-8"
        ) from bad
    except OSError as bad:
        raise Broken(f"{path} cannot be read ({bad.strerror}) — fix: make it readable") from bad


def examine(path: str, text: str, plugins: list[Path]) -> list[Finding]:
    """The findings of one file; `plugins` are the roots against which a relative path is looked up."""
    findings: list[Finding] = []
    markdown = path.endswith(".md")
    fence: str | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        if markdown:
            opener = FENCE.match(line)
            if fence is not None:
                if opener and opener[1][0] == fence[0] and len(opener[1]) >= len(fence):
                    fence = None
                continue
            if opener:
                fence = opener[1]
                continue
            line = CODE_SPAN.sub(" ", line)
        line = URL.sub(" ", line)
        for kind, pattern in (("home", HOME), ("tilde", TILDE), ("file", FILE_LINK)):
            findings.extend(Finding(path, number, kind, m[0][:60]) for m in pattern.finditer(line))
        for m in RELATIVE.finditer(line):
            candidate = m[1].rstrip(".")
            if not NAMES_A_FILE.search(candidate):
                continue
            parts = candidate.split("/")
            if all(WILDCARD.fullmatch(part) for part in parts[:-1]) and "." in parts[-1]:
                continue  # wildcards before files named by extension: no particular place
            plain = candidate.split("*")[0].rstrip("/")
            if plain and any((plugin / plain).exists() for plugin in plugins):
                continue
            findings.append(Finding(path, number, "relative", candidate[:60]))
    return findings


def check_kit(root: Path) -> tuple[list[Finding], int, int]:
    base = root / "modules"
    if not base.is_dir():
        raise Broken(f"{root} has no modules/ directory — fix: run the check from a checkout of the kit")
    modules = sorted(d for d in base.iterdir() if d.is_dir() and not d.name.startswith((".", "_")))
    findings: list[Finding] = []
    files = 0
    for module in modules:
        prefix = f"modules/{module.name}/"
        for path in listed(root, prefix):
            inside = path[len(prefix) :]
            if not inside.startswith(INSTALLED) or (root / path).is_symlink() or not (root / path).is_file():
                continue
            files += 1
            findings.extend(examine(path, read(root, path), [module]))
    for path in listed(root, SHARED):
        if (root / path).is_file():
            files += 1
            findings.extend(examine(path, read(root, path), modules))
    return findings, files, len(modules)


def report(findings: list[Finding], files: int, modules: int) -> int:
    counts = f"{files} installed file(s) of {modules} module(s) and the shared code examined"
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {counts}")
        return EXIT_RED
    print(f"GREEN: no installed component names a place in a project — {counts}")
    return EXIT_GREEN


def self_test() -> int:
    """Red→green on a throwaway tree: each form is red where the check reads, with its number of
    findings typed by hand, and green once fixed; every place not read stays green; the report of
    one finding is its literal text with exit 2; a file that is not UTF-8 is a teaching BROKEN."""
    red: dict[str, tuple[str, str, str, int]] = {  # case: file, green, red, its findings by hand
        "a home path in a script": (
            "scripts/gate.py",
            "ROOT = 'docs'\n",
            "ROOT = '/home/ann/project/docs'\n",
            1,
        ),
        "a macOS home path in a skill": (
            "skills/s/SKILL.md",
            "Read the dials file.\n",
            "Read /Users/ann/work/constitution.yaml.\n",
            1,
        ),
        "a tilde path in an install note": ("INSTALL.md", "Clone the kit.\n", "Clone into ~/kit.\n", 1),
        "a home path through the variable": ("scripts/gate.sh", "cd docs\n", "cd $HOME/work/notes.md\n", 1),
        "a braced home variable and a Windows user folder": (
            "INSTALL.md",
            "Install.\n",
            "Copy ${HOME}/x/y.md or C:\\Users\\ann\\x.md there.\n",
            2,
        ),
        "a glob ending in a folder after a wildcard": (
            "scripts/gate.py",
            "P = 'docs'\n",
            "P = '**/decisions'\n",
            1,
        ),
        "a glob naming a folder after a wildcard": (
            "skills/s/SKILL.md",
            'paths: "**/*.md"\n',
            'paths: "**/docs/decisions/*.md"\n',
            1,
        ),
        "a home path in an interpreter line": (
            "scripts/run.sh",
            "#!/usr/bin/env sh\n",
            "#!/home/ann/bin/sh\n",
            1,
        ),
        "a file link in a hook": ("hooks/hooks.json", '{"a": 1}\n', '{"a": "file:///srv/x"}\n', 1),
        "a project path in a message": (
            "scripts/gate/messages.py",
            "FIX = 'name it in the dials file'\n",
            "FIX = 'edit docs/decisions/index.md and docs/**'\n",
            2,
        ),
        "a path on the manifest": (
            ".claude-plugin/plugin.json",
            '{"name": "const-x"}\n',
            '{"name": "const-x", "docs": "notes/readme.md"}\n',
            1,
        ),
        "a project path in the shared code": ("SHARED", "X = 1\n", "X = 'var/data/state.json'\n", 1),
    }
    green: dict[str, tuple[str, str]] = {  # case: file, text with a form the check does not read
        "the module document": ("MODULE.md", "See /home/ann/notes.md and docs/x.md.\n"),
        "a test": ("tests/run.py", "PATH = '/Users/someone/a.md'\n"),
        "a system interpreter line": ("scripts/gate.sh", "#!/usr/bin/env sh\necho ok\n"),
        "a fenced example": ("INSTALL.md", "```yaml\npaths:\n  - docs/records/*.md\n```\n"),
        "inline code": ("skills/s/SKILL.md", "Name `docs/**` in the dial.\n"),
        "a public URL": ("INSTALL.md", "See https://example.org/~/docs/page.md for more.\n"),
        "a file of the plugin": ("INSTALL.md", "The skill is skills/s/SKILL.md.\n"),
        "the dials file": ("scripts/gate.py", "NAME = 'constitution.yaml'\n"),
        "a folder of the plugin by its glob": ("INSTALL.md", "Every skills/**/SKILL.md file.\n"),
        "wildcards before files named by an extension": ("skills/s/SKILL.md", 'paths: "**/*.md"\n'),
        "a path with no extension or glob": ("scripts/gate.py", "REF = 'refs/heads/main'\n"),
        "a plugin-root path": ("hooks/hooks.json", '{"args": ["${CLAUDE_PLUGIN_ROOT}/scripts/x/y.sh"]}\n'),
    }
    report_lines = [  # the report of the tilde case, typed by hand: a message function cannot check itself
        "RED: modules/const-x/INSTALL.md:1: a path under `~/`, '~/'",
        "  why: a module installs into any project, so it names no place in one (law 2 of CLAUDE.md)",
        "  fix: name the place in words, or read it from the dials file",
        "RED: 1 finding(s) — 3 installed file(s) of 1 module(s) and the shared code examined",
    ]

    def fresh(root: Path) -> None:
        try:
            subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
        except (OSError, subprocess.CalledProcessError) as failed:
            raise Broken(f"git init failed in {root} — fix: install git, then run the self-test") from failed
        write(root, "modules/const-x/skills/s/SKILL.md", "A skill.\n")
        write(root, "modules/const-x/INSTALL.md", "Install.\n")
        write(root, f"{SHARED}/model.py", "Y = 2\n")

    def write(root: Path, path: str, text: str) -> None:
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", path], cwd=root, check=True, capture_output=True)

    def at(path: str) -> str:
        return f"{SHARED}/state.py" if path == "SHARED" else f"modules/const-x/{path}"

    failed = 0
    for name, (path, good, bad, count) in red.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, at(path), good)
            green_before = not check_kit(root)[0]
            write(root, at(path), bad)
            findings = check_kit(root)[0]
            red_after = len(findings) == count and all(f.path == at(path) for f in findings)
        ok = green_before and red_after
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the fixed text is green, {name} is red")
    for name, (path, text) in green.items():
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fresh(root)
            write(root, at(path), text)
            ok = not check_kit(root)[0]
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name} is not a finding")
    with tempfile.TemporaryDirectory() as tmp:  # a module folder of another name is read too
        root = Path(tmp).resolve()
        fresh(root)
        write(root, "modules/other/INSTALL.md", "Clone into ~/kit.\n")
        ok = [f.path for f in check_kit(root)[0]] == ["modules/other/INSTALL.md"]
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a module folder not named const- is read as a module")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        write(root, at("INSTALL.md"), red["a tilde path in an install note"][2])
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(*check_kit(root))
    ok = code == EXIT_RED and printed.getvalue().splitlines() == report_lines
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of one finding is its literal text, exit 2")
    if not ok:
        print(printed.getvalue())
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        fresh(root)
        (root / "modules/const-x/INSTALL.md").write_bytes(b"caf\xe9\n")
        try:
            check_kit(root)
            ok = False
        except Broken as broken:
            ok = str(broken).startswith("modules/const-x/INSTALL.md is not UTF-8") and "fix:" in str(broken)
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a file that is not UTF-8 is a teaching BROKEN line, never a traceback")
    total = len(red) + len(green) + 3
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-portability", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 files examined")
        return EXIT_BROKEN
    try:
        return self_test() if args.self_test else report(*check_kit(KIT))
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 files examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
