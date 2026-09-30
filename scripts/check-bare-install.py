#!/usr/bin/env python3
"""Kit check: a module installs through Claude Code and operates on a bare repository with its
defaults alone — requirements A12.1 to A12.3, kernel plus one module (decision
dec-0059-bare-repo-install-in-ci).

For the module named, in throwaway folders that the check removes:
  1. a bare repository — `git init`, the kit's kernel copied to docs/constitution/ and committed,
     no constitution.yaml — and an empty Claude configuration folder (CLAUDE_CONFIG_DIR);
  2. `claude plugin marketplace add <kit>` and `claude plugin install <module>@constitution-kit`,
     the platform's own install, which writes a copy of the plugin into the configuration's cache;
  3. what the kit's source of the module declares, held in that copy: no link of the source
     leads inside the module; every link arrives as a real file, or a real directory, with the
     same files byte for byte; the copy holds no link the source lacks; the copy holds
     the source's hooks file; every hook of the source's hooks/hooks.json, run from the copy in
     exec form on a sample event of its kind with CLAUDE_PLUGIN_ROOT set to the copy, exits 0 on
     the bare repository, and its JSON on standard output neither blocks, denies, asks nor stops;
     every scan the source declares in its enforcement section (template §9), run from the copy,
     exits 0 there.
A red is a finding against the module, and so is an install Claude Code refuses; a missing
`claude` or `git`, or a marketplace the CLI cannot add, is a configuration failure. The run holds
the case of an absent dials file; a module with neither hook nor scan is held on its links alone.
Needs no login: plugin install reads no account.

Modes:  --module <name>  check one module of the kit;
        --self-test      prove step 3 on throwaway source and copy folders, no install: each branch
                         of the link, hooks-file, hook and scan checks red once, a green copy green,
                         and the report of one finding as literal lines with exit 2.
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


class Refused(Exception):
    """The platform refused to install the module: a finding against the module."""


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
) -> tuple[int, str, str]:
    """The exit, the standard output and the standard error of one command."""
    try:
        done = subprocess.run(
            argv, cwd=cwd, env=env, input=stdin, capture_output=True, text=True, timeout=timeout, check=False
        )
    except FileNotFoundError as bad:
        raise Broken(
            f"{argv[0]} is not installed ({bad.strerror}) — fix: install it and put it on PATH"
        ) from bad
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout} s"
    return done.returncode, done.stdout.strip(), done.stderr.strip()


def last_line(out: str, err: str) -> str:
    said = err or out
    return said.splitlines()[-1] if said else "no output"


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


def refusal(said: str) -> str:
    """A decision a hook that exits 0 still gives in the JSON of its standard output: a block, a
    denial, a question or a stop."""
    try:
        answer = json.loads(said) if said.startswith("{") else {}
    except ValueError:
        return ""
    if not isinstance(answer, dict):
        return ""
    specific = answer.get("hookSpecificOutput")
    decision = specific.get("permissionDecision") if isinstance(specific, dict) else None
    if answer.get("decision") == "block":
        return "block"
    if decision in ("deny", "ask"):
        return str(decision)
    if answer.get("continue") is False:
        return "stop"
    return ""


CACHES = ("__pycache__", ".mypy_cache", ".ruff_cache")


def files_under(folder: Path) -> set[str]:
    """The files under a folder, by relative path, caches left out."""
    return {
        str(f.relative_to(folder))
        for f in folder.rglob("*")
        if f.is_file() and not any(part in CACHES for part in f.relative_to(folder).parts)
    }


def link_findings(module: str, source: Path, plugin: Path) -> list[Finding]:
    """No link of the source leads inside the module; every link arrives as a real file, or a real
    directory, with the same files byte for byte; the copy holds no link the source lacks."""
    findings: list[Finding] = []
    links = sorted(p for p in source.rglob("*") if p.is_symlink())
    for link in links:
        where = link.relative_to(source)
        place = plugin / where
        target = link.resolve()
        inside = target.is_relative_to(source.resolve())
        fix = (
            "replace the link inside the module with the file it points at"
            if inside
            else "the install must carry what it runs — fire the fallback of limit 3 of"
            " shared/GATE.md §4, links replaced by copies"
        )
        if place.is_symlink() or not place.exists():
            state = "left a link" if place.is_symlink() else "missing"
            findings.append(Finding(module, f"the link {where} is {state} in the installed copy", fix))
        elif inside:
            findings.append(Finding(module, f"the link {where} leads inside the module", fix))
        elif target.is_file() and place.is_dir():
            findings.append(Finding(module, f"the link {where} to a file arrived as a folder", fix))
        elif target.is_dir() and (
            files_under(place) != files_under(target)
            or any((place / f).read_bytes() != (target / f).read_bytes() for f in files_under(target))
        ):
            differing = sorted(
                (files_under(target) ^ files_under(place))
                | {
                    f
                    for f in files_under(target) & files_under(place)
                    if (place / f).read_bytes() != (target / f).read_bytes()
                }
            )
            findings.append(
                Finding(
                    module,
                    f"the link {where} arrived with other files than its target: {', '.join(differing[:3])}",
                    fix,
                )
            )
        elif target.is_file() and place.read_bytes() != target.read_bytes():
            findings.append(
                Finding(module, f"the link {where} arrived with other bytes than its target", fix)
            )
    carried = {plugin / link.relative_to(source) for link in links}
    for extra in sorted(p for p in plugin.rglob("*") if p.is_symlink() and p not in carried):
        findings.append(
            Finding(
                module,
                f"the installed copy holds a link its source lacks: {extra.relative_to(plugin)}",
                "find what makes the link in the install, and make the module carry a file instead",
            )
        )
    return findings


def check_installed(module: str, source: Path, plugin: Path, repo: Path, data: Path) -> list[Finding]:
    """What the kit's source of the module promises, held in its installed copy on a bare repository."""
    findings = link_findings(module, source, plugin)
    if (source / "hooks" / "hooks.json").is_file() and not (plugin / "hooks" / "hooks.json").is_file():
        findings.append(
            Finding(module, "the installed copy has no hooks/hooks.json", "restore the hooks file")
        )
    env = os.environ | {
        "CLAUDE_PLUGIN_ROOT": str(plugin),
        "CLAUDE_PROJECT_DIR": str(repo),
        "CLAUDE_PLUGIN_DATA": str(data),
    }
    for hook in hooks_of(source):
        argv = [a.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin)) for a in (hook.command, *hook.args)]
        shown = " ".join(argv[1:]).replace(str(plugin), "<plugin>")
        note = repo / NOTE
        if hook.event == "PostToolUse":
            note.write_text("# Note\n", encoding="utf-8")
        code, out, err = run(argv, repo, env, json.dumps(sample_event(hook, repo)), hook.timeout)
        note.unlink(missing_ok=True)
        answered = refusal(out) if code == 0 else ""
        if code != 0 or answered:
            last = last_line(out, err)
            what = f"exits {code}" if code != 0 else f"answers {answered}"
            findings.append(
                Finding(
                    module,
                    f"its {hook.event} hook `{shown}` {what} on a bare repository ({last})",
                    "make the hook pass with a visible zero where no constitution.yaml claims anything",
                )
            )
    for entry in declared_scans(source):
        script = plugin / "scripts" / (entry if entry.endswith(".py") else f"{entry}.sh")
        argv = ["python3" if entry.endswith(".py") else "sh", str(script), "--scan"]
        code, out, err = run(argv, repo, env)
        if code != 0:
            last = last_line(out, err)
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
        code, out, err = run(argv, repo, env)
        if code != 0:
            raise Broken(f"git init failed ({last_line(out, err)}) — fix: install git")
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
        code, out, err = run(argv, repo, env)
        if code != 0:
            said = last_line(out, err)
            raise Broken(f"{' '.join(argv[:2])} failed in the bare repository ({said}) — fix: install git")
    return repo


def install(module: str, root: Path, repo: Path) -> Path:
    config = root / "config"
    config.mkdir()
    env = os.environ | {"CLAUDE_CONFIG_DIR": str(config)}
    code, out, err = run(["claude", "plugin", "marketplace", "add", str(KIT)], repo, env)
    if code != 0:
        last = last_line(out, err)
        raise Broken(
            f"`claude plugin marketplace add` exited {code} ({last}) — fix: check the kit's marketplace.json"
        )
    code, out, err = run(["claude", "plugin", "install", f"{module}@{MARKETPLACE}"], repo, env)
    if code != 0:
        raise Refused(last_line(out, err) if out or err else f"exit {code}")
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
        try:
            plugin = install(module, root, repo)
        except Refused as refused:
            return [
                Finding(
                    module,
                    f"Claude Code refuses to install it ({refused})",
                    "fix its manifest or its entry in marketplace.json",
                )
            ]
        (root / "data").mkdir()
        return check_installed(module, KIT / "modules" / module, plugin, repo, root / "data")


def report(module: str, findings: list[Finding], examined: str) -> int:
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {examined}")
        return EXIT_RED
    print(f"GREEN: {module} installs and operates on a bare repository with its defaults — {examined}")
    return EXIT_GREEN


def self_test() -> int:
    """Red→green on throwaway source and copy folders, no install: a green copy is green; each branch
    of the link check — a link inside the module, left a link, missing, with files lost, added or
    changed, a file link with other bytes or arrived as a folder, a link the source lacks — each branch of
    the hooks-file, hook and scan checks, and a red scan the source declares where the copy lost its
    document, are each a finding; the report of one finding is its literal text, exit 2."""
    module_text = (
        '<a id="t9"></a>\n| E1 | `check-x --scan`: all | `gate` |\n| E2 | `check-p.py --scan` | `gate` |\n'
        '<a id="t10"></a>\n'
    )
    command = {"type": "command", "command": "sh", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/hook.sh"]}
    hooks = {"hooks": {"PreToolUse": [{"matcher": "Write|Edit", "hooks": [command]}]}}
    deny = '{"hookSpecificOutput": {"permissionDecision": "deny"}}'

    def folders(root: Path, change: str) -> tuple[Path, Path]:
        source, shared = root / "source", root / "shared"
        (shared).mkdir()
        (shared / "code.py").write_text("x = 1\n", encoding="utf-8")
        (source / "hooks").mkdir(parents=True)
        (source / "scripts").mkdir()
        (source / "hooks" / "hooks.json").write_text(json.dumps(hooks), encoding="utf-8")
        (source / "MODULE.md").write_text(module_text, encoding="utf-8")
        hook = {
            "hook-exit-1": "exit 1",
            "hook-exit-2": "exit 2",
            "hook-denies": f"echo '{deny}'",
            "hook-denies-and-warns": f"echo '{deny}'; echo 'WARNING: logged' >&2",
            "hook-blocks": """echo '{"decision": "block"}'""",
            "hook-asks": """echo '{"hookSpecificOutput": {"permissionDecision": "ask"}}'""",
            "hook-stops": """echo '{"continue": false}'""",
        }.get(change, "exit 0")
        (source / "scripts" / "hook.sh").write_text(
            f'grep -q \'"hook_event_name": "PreToolUse"\' || exit 3\n{hook}\n', encoding="utf-8"
        )
        (source / "scripts" / "check-x.sh").write_text(
            f"exit {2 if change in ('scan-red', 'copy-without-document') else 0}\n", encoding="utf-8"
        )
        (source / "scripts" / "check-p.py").write_text(
            f"raise SystemExit({2 if change == 'py-scan-red' else 0})\n", encoding="utf-8"
        )
        (source / "scripts" / "shared").symlink_to(shared)
        if change == "inner-link":
            (source / "scripts" / "again").symlink_to(source / "hooks")
        copy = root / "copy"
        shutil.copytree(source, copy, symlinks=False)
        if change == "inner-link":
            shutil.rmtree(copy / "scripts" / "again")
            (copy / "scripts" / "again").symlink_to(copy / "hooks")
        if change == "inner-link-copied":
            (source / "scripts" / "again").symlink_to(source / "hooks")
            shutil.copytree(source / "hooks", copy / "scripts" / "again")
        if change == "link-other-bytes":
            (source / "scripts" / "one").symlink_to(shared / "code.py")
            (copy / "scripts" / "one").write_text("x = 2\n", encoding="utf-8")
        if change == "file-link-as-folder":
            (source / "scripts" / "one").symlink_to(shared / "code.py")
            (copy / "scripts" / "one").mkdir()
        if change == "link-left":
            shutil.rmtree(copy / "scripts" / "shared")
            (copy / "scripts" / "shared").symlink_to(shared)
        if change == "link-missing":
            shutil.rmtree(copy / "scripts" / "shared")
        if change == "no-hooks-file":
            (copy / "hooks" / "hooks.json").unlink()
        if change == "copy-without-document":
            (copy / "MODULE.md").unlink()
        if change == "link-emptied":
            (copy / "scripts" / "shared" / "code.py").unlink()
        if change == "link-edited":
            (copy / "scripts" / "shared" / "code.py").write_text("x = 3\n", encoding="utf-8")
        if change == "link-grown":
            (copy / "scripts" / "shared" / "added.py").write_text("y = 1\n", encoding="utf-8")
        if change == "extra-link":
            (copy / "scripts" / "made").symlink_to(copy / "hooks")
        if change == "no-event":
            (source / "hooks" / "hooks.json").write_text(
                json.dumps({"hooks": {"PreToolUse": [{"matcher": "Write", "hooks": [command]}]}}).replace(
                    "PreToolUse", "PostToolUse"
                ),
                encoding="utf-8",
            )
        return source, copy

    def findings_of(change: str) -> list[Finding]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "repo" / "docs").mkdir(parents=True)
            (root / "data").mkdir()
            source, copy = folders(root, change)
            return check_installed("const-x", source, copy, root / "repo", root / "data")

    failed = 0
    cases = {
        "a copy whose hook and scans pass, its outside link a real directory, is green": ("", ""),
        "a link left a link in the copy is a finding": ("link-left", "is left a link"),
        "a link missing from the copy is a finding": ("link-missing", "is missing"),
        "a link inside the module left a link is a finding, fixed by the file it points at": (
            "inner-link",
            "again",
        ),
        "a link inside the module that arrived as a real directory is a finding": (
            "inner-link-copied",
            "leads inside the module",
        ),
        "a link to a file that arrived with other bytes is a finding": ("link-other-bytes", "other bytes"),
        "a copy without its hooks file is a finding": ("no-hooks-file", "no hooks/hooks.json"),
        "a hook that exits 1 is a finding": ("hook-exit-1", "exits 1"),
        "a hook that exits 2 is a finding": ("hook-exit-2", "exits 2"),
        "a hook that exits 0 but denies is a finding": ("hook-denies", "answers deny"),
        "a hook that denies and writes a warning to standard error is a finding": (
            "hook-denies-and-warns",
            "answers deny",
        ),
        "a hook that exits 0 but blocks is a finding": ("hook-blocks", "answers block"),
        "a hook that exits 0 but asks is a finding": ("hook-asks", "answers ask"),
        "a hook that exits 0 but stops is a finding": ("hook-stops", "answers stop"),
        "a scan the source declares is run though the copy lost its document": (
            "copy-without-document",
            "check-x --scan",
        ),
        "a link that arrived without its files is a finding": ("link-emptied", "code.py"),
        "a link that arrived with a file its target lacks is a finding": ("link-grown", "added.py"),
        "a link to a file that arrived as a folder is a finding": (
            "file-link-as-folder",
            "arrived as a folder",
        ),
        "a linked folder whose file arrived with other bytes is a finding": ("link-edited", "code.py"),
        "a link in the copy that the source lacks is a finding": ("extra-link", "a link its source lacks"),
        "a hook given another event than its own is a finding": ("no-event", "exits 3"),
        "a shell scan that is red is a finding": ("scan-red", "check-x --scan"),
        "a Python scan that is red is a finding": ("py-scan-red", "check-p.py --scan"),
    }
    for name, (change, wanted) in cases.items():
        got = [f.what for f in findings_of(change)]
        ok = got == [] if not wanted else len(got) >= 1 and all(wanted in g for g in got[:1])
        if change == "no-hooks-file":
            ok = ok and len(got) == 1  # the file is missing; the hook the source names still runs in the copy
        if change == "inner-link":
            fixes = [f.fix for f in findings_of(change)]
            ok = ok and fixes[:1] == ["replace the link inside the module with the file it points at"]
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"        got: {got}")
    report_lines = [  # typed by hand: a message function cannot check itself
        "RED: const-x: its scan `check-x --scan` exits 2 on a bare repository (no output)",
        f"  why: {WHY}",
        "  fix: make the scan green, with a visible zero, where no constitution.yaml claims anything",
        "RED: 1 finding(s) — 1 hook(s), 2 scan(s)",
    ]
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        code = report("const-x", findings_of("scan-red"), "1 hook(s), 2 scan(s)")
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
        links = sum(1 for p in plugin.rglob("*") if p.is_symlink())
        examined = f"{len(hooks_of(plugin))} hook(s), {len(declared_scans(plugin))} scan(s), {links} link(s)"
        return report(module, check_module(module), examined)
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 modules examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
