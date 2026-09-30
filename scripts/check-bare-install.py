#!/usr/bin/env python3
"""Kit check: a module installs through Claude Code and operates on a bare repository with its
defaults alone — requirements A12.1 to A12.3, kernel plus one module (decision
dec-0059-bare-repo-install-in-ci).

For the module named, in throwaway folders that the check removes:
  1. a bare repository — `git init`, the kit's kernel copied to docs/constitution/ and committed,
     no constitution.yaml — and an empty Claude configuration folder (CLAUDE_CONFIG_DIR);
  2. `claude plugin marketplace add <kit>` and `claude plugin install <module>@constitution-kit`,
     the platform's own install, which copies the plugin into the configuration's cache;
  3. in the installed copy: no symbolic link is left, since an installed plugin carries what it
     runs; every hook of hooks/hooks.json, run in exec form with CLAUDE_PLUGIN_ROOT set to the
     copy, exits 0 on a sample event of its kind in the bare repository; every scan the module
     declares in its enforcement section (template §9) exits 0 there.
A red is a finding against the module; a missing `claude` or `git`, or an install the CLI
refuses, is a configuration failure. Needs no login: plugin install reads no account.

Modes:  --module <name>  check one module of the kit;
        --self-test      prove step 3 on throwaway plugin folders: a green one green; a link left,
                         a hook that fails on the bare repository and a scan that is red each one
                         finding; the report of one finding as literal lines with exit 2.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
MARKETPLACE = "constitution-kit"
DECLARED = re.compile(r"`([a-z][a-z0-9-]*?(?:\.py)?) --scan`")
WHY = "a module must install and operate on a bare repository with its defaults alone (requirement A12.1)"
NOTE = "docs/note.md"


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    module: str
    what: str
    fix: str

    def render(self) -> str:
        return f"RED: {self.module}: {self.what}\n  why: {WHY}\n  fix: {self.fix}"


@dataclass(frozen=True)
class Hook:
    event: str
    matcher: str
    command: str
    args: tuple[str, ...]
    timeout: int


def run(
    argv: list[str], cwd: Path, env: dict[str, str], stdin: str = "", timeout: int = 300
) -> tuple[int, str]:
    try:
        done = subprocess.run(
            argv, cwd=cwd, env=env, input=stdin, capture_output=True, text=True, timeout=timeout, check=False
        )
    except FileNotFoundError as bad:
        raise Broken(
            f"{argv[0]} is not installed ({bad.strerror}) — fix: install it and put it on PATH"
        ) from bad
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout} s"
    return done.returncode, (done.stdout + done.stderr).strip()


def hooks_of(plugin: Path) -> list[Hook]:
    path = plugin / "hooks" / "hooks.json"
    if not path.is_file():
        return []
    try:
        table = json.loads(path.read_text(encoding="utf-8"))["hooks"]
    except (ValueError, KeyError, TypeError) as bad:
        raise Broken(f"{path} is not a hooks file ({bad}) — fix: restore hooks/hooks.json") from bad
    found: list[Hook] = []
    for event, groups in table.items():
        for group in groups:
            for hook in group["hooks"]:
                found.append(
                    Hook(
                        str(event),
                        str(group.get("matcher", "")),
                        str(hook["command"]),
                        tuple(str(a) for a in hook.get("args", [])),
                        int(hook.get("timeout", 60)),
                    )
                )
    return found


def declared_scans(plugin: Path) -> list[str]:
    document = plugin / "MODULE.md"
    if not document.is_file():
        return []
    lines = document.read_text(encoding="utf-8").splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == '<a id="t9"></a>'), None)
    if start is None:
        return []
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].strip() == '<a id="t10"></a>'), len(lines)
    )
    rows = [line for line in lines[start:end] if line.startswith("| E")]
    return sorted({m[1] for row in rows for m in DECLARED.finditer(row)})


def sample_event(hook: Hook, repo: Path) -> dict[str, object]:
    event: dict[str, object] = {"hook_event_name": hook.event, "cwd": str(repo), "session_id": "bare-install"}
    if hook.event in ("PreToolUse", "PostToolUse"):
        tools = hook.matcher.split("|")
        if "Write" in tools or not hook.matcher:
            event |= {
                "tool_name": "Write",
                "tool_input": {"file_path": str(repo / NOTE), "content": "# Note\n"},
            }
        elif "Bash" in tools:
            event |= {"tool_name": "Bash", "tool_input": {"command": "ls"}}
        else:
            event |= {"tool_name": tools[0], "tool_input": {}}
    if hook.event == "SessionStart":
        event["source"] = "startup"
    if hook.event == "Stop":
        event["stop_hook_active"] = False
    return event


def check_installed(module: str, plugin: Path, repo: Path, data: Path) -> list[Finding]:
    findings: list[Finding] = []
    links = sorted(str(p.relative_to(plugin)) for p in plugin.rglob("*") if p.is_symlink())
    if links:
        findings.append(
            Finding(
                module,
                f"the installed copy keeps {len(links)} symbolic link(s): {', '.join(links[:3])}",
                "the install must carry what it runs — fire the fallback of limit 3 of shared/GATE.md §4,"
                " links replaced by copies",
            )
        )
    env = os.environ | {
        "CLAUDE_PLUGIN_ROOT": str(plugin),
        "CLAUDE_PROJECT_DIR": str(repo),
        "CLAUDE_PLUGIN_DATA": str(data),
    }
    for hook in hooks_of(plugin):
        argv = [a.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin)) for a in (hook.command, *hook.args)]
        event = sample_event(hook, repo)
        note = repo / NOTE
        if hook.event == "PostToolUse":
            note.write_text("# Note\n", encoding="utf-8")
        code, said = run(argv, repo, env, json.dumps(event), hook.timeout)
        note.unlink(missing_ok=True)
        if code != 0:
            last = said.splitlines()[-1] if said else "no output"
            findings.append(
                Finding(
                    module,
                    f"its {hook.event} hook `{' '.join(argv[1:]).replace(str(plugin), '<plugin>')}` exits"
                    f" {code} on a bare repository ({last})",
                    "make the hook pass with a visible zero where no constitution.yaml claims anything",
                )
            )
    for entry in declared_scans(plugin):
        script = plugin / "scripts" / (entry if entry.endswith(".py") else f"{entry}.sh")
        argv = ["python3" if entry.endswith(".py") else "sh", str(script), "--scan"]
        code, said = run(argv, repo, env)
        if code != 0:
            last = said.splitlines()[-1] if said else "no output"
            findings.append(
                Finding(
                    module,
                    f"its scan `{entry} --scan` exits {code} on a bare repository ({last})",
                    "make the scan green, with a visible zero, where no constitution.yaml claims anything",
                )
            )
    return findings


def bare_repository(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    env = os.environ | {"GIT_CONFIG_GLOBAL": os.devnull}
    for argv in (["git", "init", "-q", "-b", "main"],):
        code, said = run(argv, repo, env)
        if code != 0:
            raise Broken(f"git init failed ({said}) — fix: install git")
    shutil.copytree(KIT / "kernel", repo / "docs" / "constitution")
    for argv in (
        ["git", "add", "-A"],
        [
            "git",
            "-c",
            "user.name=bare",
            "-c",
            "user.email=bare@example.invalid",
            "commit",
            "-q",
            "-m",
            "kernel",
        ],
    ):
        code, said = run(argv, repo, env)
        if code != 0:
            raise Broken(f"{' '.join(argv[:2])} failed in the bare repository ({said}) — fix: install git")
    return repo


def install(module: str, root: Path, repo: Path) -> Path:
    config = root / "config"
    config.mkdir()
    env = os.environ | {"CLAUDE_CONFIG_DIR": str(config)}
    for argv in (
        ["claude", "plugin", "marketplace", "add", str(KIT)],
        ["claude", "plugin", "install", f"{module}@{MARKETPLACE}"],
    ):
        code, said = run(argv, repo, env)
        if code != 0:
            last = said.splitlines()[-1] if said else "no output"
            raise Broken(f"`{' '.join(argv[:3])} …` exited {code} ({last}) — fix: read its output above")
    record = config / "plugins" / "installed_plugins.json"
    try:
        entries = json.loads(record.read_text(encoding="utf-8"))["plugins"][f"{module}@{MARKETPLACE}"]
        return Path(entries[0]["installPath"])
    except (OSError, ValueError, KeyError, IndexError, TypeError) as bad:
        raise Broken(
            f"{record} names no install of {module} ({bad}) — fix: check the Claude Code version"
        ) from bad


def check_module(module: str) -> list[Finding]:
    if not (KIT / "modules" / module / ".claude-plugin" / "plugin.json").is_file():
        raise Broken(f"no module {module} in the kit — fix: name a folder under modules/ that holds a plugin")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        repo = bare_repository(root)
        plugin = install(module, root, repo)
        (root / "data").mkdir()
        return check_installed(module, plugin, repo, root / "data")


def report(module: str, findings: list[Finding], examined: str) -> int:
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {examined}")
        return EXIT_RED
    print(f"GREEN: {module} installs and operates on a bare repository with its defaults — {examined}")
    return EXIT_GREEN


def self_test() -> int:
    """Red→green on throwaway plugin folders, no install: a plugin whose hook and scan pass is green;
    a link left in it, a hook that exits 1 and a scan that exits 2 are one finding each; the report
    of one finding is its literal text with exit 2."""
    module_text = '<a id="t9"></a>\n| E1 | `check-x --scan`: all | `gate` |\n<a id="t10"></a>\n'
    hooks = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Write|Edit",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "sh",
                            "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/hook.sh"],
                        }
                    ],
                }
            ]
        }
    }

    def plugin_in(root: Path, hook_exit: int = 0, scan_exit: int = 0, link: bool = False) -> Path:
        plugin = root / "plugin"
        (plugin / "hooks").mkdir(parents=True)
        (plugin / "scripts").mkdir()
        (plugin / "hooks" / "hooks.json").write_text(json.dumps(hooks), encoding="utf-8")
        (plugin / "MODULE.md").write_text(module_text, encoding="utf-8")
        (plugin / "scripts" / "hook.sh").write_text(f"cat >/dev/null\nexit {hook_exit}\n", encoding="utf-8")
        (plugin / "scripts" / "check-x.sh").write_text(f"echo scanned\nexit {scan_exit}\n", encoding="utf-8")
        if link:
            (plugin / "scripts" / "shared").symlink_to(plugin / "hooks")
        return plugin

    def findings_of(**kind: int | bool) -> list[Finding]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "repo" / "docs").mkdir(parents=True)
            (root / "data").mkdir()
            plugin = plugin_in(root, **kind)  # type: ignore[arg-type]
            return check_installed("const-x", plugin, root / "repo", root / "data")

    failed = 0
    cases: dict[str, tuple[dict[str, int | bool], list[str]]] = {
        "a plugin whose hook and scan pass on a bare repository is green": ({}, []),
        "a symbolic link left in the installed copy is a finding": ({"link": True}, ["symbolic link"]),
        "a hook that exits 1 on a bare repository is a finding": ({"hook_exit": 1}, ["PreToolUse hook"]),
        "a scan that is red on a bare repository is a finding": ({"scan_exit": 2}, ["scan `check-x --scan`"]),
    }
    for name, (kind, wanted) in cases.items():
        got = [f.what for f in findings_of(**kind)]
        ok = len(got) == len(wanted) and all(w in g for w, g in zip(wanted, got, strict=True))
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    report_lines = [  # typed by hand: a message function cannot check itself
        "RED: const-x: its scan `check-x --scan` exits 2 on a bare repository (scanned)",
        f"  why: {WHY}",
        "  fix: make the scan green, with a visible zero, where no constitution.yaml claims anything",
        "RED: 1 finding(s) — 1 hook(s), 1 scan(s)",
    ]
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        code = report("const-x", findings_of(scan_exit=2), "1 hook(s), 1 scan(s)")
    ok = code == EXIT_RED and printed.getvalue().splitlines() == report_lines
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of one finding is its literal text, exit 2")
    if not ok:
        print(printed.getvalue())
    total = len(cases) + 1
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-bare-install", add_help=False, allow_abbrev=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--module")
    group.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with --module <name>, or with --self-test")
        print("BROKEN: the check could not run — 0 modules examined")
        return EXIT_BROKEN
    try:
        if args.self_test:
            return self_test()
        module = str(args.module)
        plugin = KIT / "modules" / module
        examined = f"{len(hooks_of(plugin))} hook(s), {len(declared_scans(plugin))} scan(s)"
        return report(module, check_module(module), examined)
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 modules examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
