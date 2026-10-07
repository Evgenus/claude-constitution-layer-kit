#!/usr/bin/env python3
"""Kit check: a module installs through Claude Code and operates on a bare repository with its
defaults alone — requirements A12.1 to A12.3, kernel plus one module (decision
dec-0059-bare-repo-install-in-ci).

For the module named, in throwaway folders that the check removes:
  1. a bare repository — `git init`, the kit's kernel copied to docs/constitution/ and committed,
     no constitution.yaml — and an empty Claude configuration folder (CLAUDE_CONFIG_DIR);
  2. `claude plugin marketplace add <source>` and `claude plugin install <module>@constitution-kit`,
     the platform's own install, which writes a copy of the plugin into the configuration's cache.
     The source is --from, else the environment's CONSTITUTION_KIT_INSTALL_FROM, else the kit's
     working folder. The kit's CI names the change's GitHub repository and branch,
     `<owner>/<repo>#<branch>` — a pull request's head repository and branch, or the kit's main on
     a push to it — the copy a consumer's install writes; a fork the job's token cannot read fails; git
     clones it with the machine's own credentials, which a private remote needs. The working
     folder, a local-directory marketplace, gives a copy no session runs (shared/GATE.md, limit 3).
     The copy is compared with the kit's source at the commit the install came from, which Claude
     Code's install record names (gitCommitSha, on 2.1.282), read from the kit's git history and
     fetched when absent; an install from a local folder is compared with that folder, and a remote
     install whose record names no commit with the working folder;
  3. what the kit's source of the module declares, held in that copy: no link of the source
     leads inside the module, save the fixture runner's link tests/<package> -> ../scripts/<package>
     to a package of the module's own (a folder of scripts/, itself no link, holding an __init__.py,
     its name starting with neither `.` nor `_`, save const_gate), which arrives as a link leading to that
     package in the copy — the platform keeps a link that stays inside the plugin; every
     other link arrives as a real file, or a real directory, with the
     same files byte for byte; the copy holds no link the source lacks; the copy holds
     the source's hooks file; every hook of the source's hooks/hooks.json, run from the copy in
     exec form on a sample event of its kind with CLAUDE_PLUGIN_ROOT set to the copy, exits 0 on
     the bare repository, and its JSON on standard output neither blocks, denies, asks nor stops;
     every scan the source declares in its enforcement section (template §9), run from the copy,
     exits 0 there. The scans are read by `kit_module_doc.enforcement`, whatever a row's indent
     or bold, the last cell of a row whether or not the row closes with a bar; an explain mode that
     carries the words `not a tree scan` is none. The problems with the form of the table are
     check-gate-lists', reported once and not here; a document without its `t9` anchor, or with it
     twice, or without `t10` while a later anchor stands, is a configuration failure, never a scan
     left unrun.
A red is a finding against the module, and so is an install Claude Code refuses; a missing
`claude` or `git`, or a marketplace the CLI cannot add, is a configuration failure. The run holds
the case of an absent dials file; a module with neither hook nor scan is held on its links alone.
Needs no Claude account login: plugin install reads none; git needs a private remote's credentials.

Modes:  --module <name> [--from <source>]  check one module of the kit;
        --self-test      prove step 3 on throwaway source and copy folders, no install: each branch
                         of the link, hooks-file, hook and scan checks red once, a green copy green,
                         a source document that cannot be read (none, no `t9`, `t9` on a heading or
                         twice, `t10` twice or gone with `t11` standing) a BROKEN line, the scans
                         read from rows of each form, a last cell with no closing bar included,
                         and the report of one finding as literal lines with exit 2; and step 2's
                         reading of the install record, and of a module's source at a commit from
                         the kit's history (const-meta-types at HEAD, its links reaching shared/).
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path

from kit_module_doc import DocumentError, enforcement

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
MARKETPLACE = "constitution-kit"
WHY = "a module must install and operate on a bare repository with its defaults alone (requirement A12.1)"
NOTE = "docs/note.md"
FROM_ENV = "CONSTITUTION_KIT_INSTALL_FROM"


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
        raise Broken(
            f"{document} does not exist — fix: restore the module's document, which declares its scans"
        )
    try:
        scans, _ = enforcement(
            document.read_text(encoding="utf-8"), str(document)
        )  # check-gate-lists reports
    except DocumentError as bad:  # the problems, once; this check runs the scans that read
        raise Broken(str(bad)) from bad
    return scans


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


def runner_link(source: Path, link: Path) -> bool:
    """The fixture runner's link to a package of the module's own: tests/<name> leading to the folder
    scripts/<name> of the source, itself no link, which holds an __init__.py, its name starting with
    neither . nor _, save the shared const_gate."""
    where = link.relative_to(source)
    name = where.name
    return (
        where.parts == ("tests", name)
        and name != "const_gate"
        and not name.startswith((".", "_"))
        and link.resolve() == (source / "scripts" / name).resolve()
        and not (source / "scripts" / name).is_symlink()
        and (source / "scripts" / name / "__init__.py").is_file()
    )


def link_findings(module: str, source: Path, plugin: Path) -> list[Finding]:
    """No link of the source leads inside the module, save the runner's link to a package of the
    module's own, which arrives as a link leading to that package in the copy; every other link
    arrives as a real file, or a real directory, with the same files byte for byte; the copy holds no
    link the source lacks."""
    findings: list[Finding] = []
    links = sorted(p for p in source.rglob("*") if p.is_symlink())
    for link in links:
        where = link.relative_to(source)
        place = plugin / where
        target = link.resolve()
        if runner_link(source, link):
            package = plugin / "scripts" / where.name
            if not place.exists() or not package.is_dir() or place.resolve() != package.resolve():
                findings.append(
                    Finding(
                        module,
                        f"the runner's link {where} did not arrive as a link to its package in the installed"
                        " copy",
                        f"keep {where} a relative link to ../scripts/{where.name}, a real folder of the"
                        " module; if the platform's install no longer keeps such a link, record that as a"
                        " decision before changing the runner",
                    )
                )
            continue
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
        elif target.is_dir() and not place.is_dir():
            findings.append(Finding(module, f"the link {where} to a folder arrived as a file", fix))
        elif not target.exists():
            findings.append(Finding(module, f"the link {where} leads nowhere in the source", fix))
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
                    f"the link {where} arrived with other files or bytes than its target:"
                    f" {', '.join(differing[:3])}",
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


def installed_entry(record: Path, module: str) -> tuple[Path, str]:
    """The installed copy's folder and the commit it came from ("" when the record names none),
    from Claude Code's install record."""
    try:
        entry = json.loads(record.read_text(encoding="utf-8"))["plugins"][f"{module}@{MARKETPLACE}"][0]
        return Path(entry["installPath"]), str(entry.get("gitCommitSha") or "")
    except (OSError, ValueError, KeyError, IndexError, TypeError) as bad:
        raise Broken(
            f"{record} names no install of {module} ({bad}) — fix: check the Claude Code version"
        ) from bad


def source_at(commit: str, module: str, root: Path) -> Path:
    """The kit's source of the module at a commit — its folder and the shared code its links reach —
    read from git history into a folder under root, the commit fetched when the clone lacks it."""
    env = os.environ.copy()
    code, _, _ = run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], KIT, env)
    if code != 0:
        code, out, err = run(["git", "fetch", "-q", "origin", commit], KIT, env)
        if code != 0:
            raise Broken(
                f"commit {commit} is not in the kit's history and cannot be fetched ({last_line(out, err)})"
                " — fix: run the check from a clone that holds it"
            )
    try:
        done = subprocess.run(
            ["git", "archive", "--format=tar", commit, f"modules/{module}", "shared"],
            cwd=KIT,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as bad:
        raise Broken(
            f"git archive of {commit} failed ({bad.stderr.decode().strip()}) — fix: check the commit"
        ) from bad
    target = root / "source"
    with tarfile.open(fileobj=io.BytesIO(done.stdout)) as archive:
        archive.extractall(target, filter="data")
    return target / "modules" / module


def install(module: str, root: Path, repo: Path, source: str) -> tuple[Path, str]:
    if source.startswith("#"):
        raise Broken(
            f"the source {source} names a branch of no repository — the pull request's head repository is"
            " gone — fix: open the change again from a branch of a repository that exists"
        )
    config = root / "config"
    config.mkdir()
    env = os.environ | {"CLAUDE_CONFIG_DIR": str(config)}
    code, out, err = run(["claude", "plugin", "marketplace", "add", source], repo, env)
    if code != 0:
        last = last_line(out, err)
        raise Broken(
            f"`claude plugin marketplace add {source}` exited {code} ({last}) — fix: check the kit's"
            " marketplace.json, and that git can reach the source"
        )
    code, out, err = run(["claude", "plugin", "install", f"{module}@{MARKETPLACE}"], repo, env)
    if code != 0:
        raise Refused(last_line(out, err) if out or err else f"exit {code}")
    return installed_entry(config / "plugins" / "installed_plugins.json", module)


def counted(source: Path) -> str:
    links = sum(1 for p in source.rglob("*") if p.is_symlink())
    return f"{len(hooks_of(source))} hook(s), {len(declared_scans(source))} scan(s), {links} link(s)"


def check_module(module: str, source: str) -> tuple[list[Finding], str]:
    """The findings, and what was examined: the hooks, scans and links of the source compared."""
    if not (KIT / "modules" / module / ".claude-plugin" / "plugin.json").is_file():
        raise Broken(f"no module {module} in the kit — fix: name a folder under modules/ that holds a plugin")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        repo = bare_repository(root)
        try:
            plugin, commit = install(module, root, repo, source)
        except Refused as refused:
            refusal_finding = Finding(
                module,
                f"Claude Code refuses to install it ({refused})",
                "fix its manifest or its entry in marketplace.json",
            )
            return [refusal_finding], "no install"
        (root / "data").mkdir()
        if Path(source).exists():  # a local folder is copied as it stands, uncommitted edits included
            kit_source = Path(source).resolve() / "modules" / module
        else:
            kit_source = source_at(commit, module, root) if commit else KIT / "modules" / module
        return check_installed(module, kit_source, plugin, repo, root / "data"), counted(kit_source)


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
    of the link check — a link inside the module, the runner's link to its own package arrived as a
    directory, leading elsewhere, dangling or missing, a link left a link, missing, with files lost, added or
    changed, a file link with other bytes or arrived as a folder, a link the source lacks — each branch of
    the hooks-file, hook and scan checks, and a red scan the source declares where the copy lost its
    document, are each a finding; a source document that cannot be read is a teaching BROKEN line, and
    the scans are read from rows of each form; the report of one finding is its literal text, exit 2."""
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
        document = {
            "no-t9": "no anchor\n",
            "t9-on-heading": module_text.replace('<a id="t9"></a>\n', '## 9 <a id="t9"></a>\n'),
            "t9-twice": module_text.replace('<a id="t9"></a>\n', '<a id="t9"></a>\n<a id="t9"></a>\n'),
            "t10-twice": module_text.replace("| E2", '<a id="t10"></a>\n| E2'),
            "t10-missing": module_text.replace('<a id="t10"></a>\n', '<a id="t11"></a>\n'),
            "indented-scan-red": module_text.replace("| E1 |", "   | E1 |"),
            "explain-marked": module_text.replace(
                '<a id="t10"></a>',
                "| E3 | `check-y --scan --since <date>`: the report, not a tree scan | `advisory` |\n"
                '<a id="t10"></a>',
            ),
        }.get(change, module_text)
        if change != "no-document":
            (source / "MODULE.md").write_text(document, encoding="utf-8")
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
            f"exit {2 if change in ('scan-red', 'copy-without-document', 'indented-scan-red') else 0}\n",
            encoding="utf-8",
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
        if change.startswith("runner-link"):
            package = {
                "runner-link-no-package": "data",
                "runner-link-const-gate": "const_gate",
                "runner-link-underscore": "_own_gate",
            }.get(change, "own_gate")
            if change == "runner-link-to-a-link":  # scripts/own_gate a link out of the module, as const_gate
                (root / "outside_gate").mkdir()
                (root / "outside_gate" / "__init__.py").write_text("", encoding="utf-8")
                (source / "scripts" / package).symlink_to(root / "outside_gate")
            else:
                (source / "scripts" / package).mkdir()
            if change not in ("runner-link-no-package", "runner-link-to-a-link"):
                (source / "scripts" / package / "__init__.py").write_text("", encoding="utf-8")
            holder = "skills" if change == "runner-link-outside-tests" else "tests"
            (source / holder).mkdir()
            (source / holder / package).symlink_to(f"../scripts/{package}")
            shutil.copytree(source / "scripts" / package, copy / "scripts" / package)
            (copy / holder).mkdir()
            if change == "runner-link-outside-tests":
                (copy / holder / package).symlink_to(f"../scripts/{package}")
            elif change == "runner-link-copied":
                shutil.copytree(source / "scripts" / package, copy / "tests" / package)
            elif change == "runner-link-to-a-link":
                (copy / "tests" / package).symlink_to(f"../scripts/{package}")
            elif change == "runner-link-dangling":
                shutil.rmtree(copy / "scripts" / package)
                (copy / "tests" / package).symlink_to(f"../scripts/{package}")
            elif change == "runner-link-elsewhere":
                (copy / "tests" / package).symlink_to("../hooks")
            elif change != "runner-link-missing":
                (copy / "tests" / package).symlink_to(f"../scripts/{package}")
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
        if change == "folder-link-as-file":
            shutil.rmtree(copy / "scripts" / "shared")
            (copy / "scripts" / "shared").write_text("x = 1\n", encoding="utf-8")
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
        "the runner's link to a package of the module's own, kept a link to it, is green": (
            "runner-link",
            "",
        ),
        "the runner's link that arrived as a real directory is a finding": (
            "runner-link-copied",
            "the runner's link tests/own_gate did not arrive as a link to its package",
        ),
        "the runner's link that arrived leading elsewhere is a finding": (
            "runner-link-elsewhere",
            "the runner's link tests/own_gate did not arrive as a link to its package",
        ),
        "the runner's link kept, its package missing from the copy, is a finding": (
            "runner-link-dangling",
            "the runner's link tests/own_gate did not arrive as a link to its package",
        ),
        "the runner's link missing from the copy is a finding": (
            "runner-link-missing",
            "the runner's link tests/own_gate did not arrive as a link to its package",
        ),
        "a link to a package of the module's own from outside tests/ leads inside the module": (
            "runner-link-outside-tests",
            "the link skills/own_gate is left a link",
        ),
        "a link of tests/ to a folder of scripts/ that is itself a link is no runner's link": (
            "runner-link-to-a-link",
            "the link tests/own_gate is left a link",
        ),
        "a link of tests/ to a real folder scripts/const_gate leads inside the module": (
            "runner-link-const-gate",
            "the link tests/const_gate is left a link",
        ),
        "a link of tests/ to a package named with a leading _ leads inside the module": (
            "runner-link-underscore",
            "the link tests/_own_gate is left a link",
        ),
        "a link of tests/ to a folder of scripts/ with no __init__.py leads inside the module": (
            "runner-link-no-package",
            "the link tests/data is left a link",
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
        "a link to a folder that arrived as a file is a finding": (
            "folder-link-as-file",
            "arrived as a file",
        ),
        "a link in the copy that the source lacks is a finding": ("extra-link", "a link its source lacks"),
        "a hook given another event than its own is a finding": ("no-event", "exits 3"),
        "a shell scan that is red is a finding": ("scan-red", "check-x --scan"),
        "a Python scan that is red is a finding": ("py-scan-red", "check-p.py --scan"),
        "a red scan in an indented row is run, and is a finding": ("indented-scan-red", "check-x --scan"),
        "an explain with the mark is no scan, so none is run for it": ("explain-marked", ""),
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
    anchor = "on a line of its own — fix: restore the template's anchor, alone on its line"
    unreadable = {  # the source's document: its change, what the BROKEN line says
        "a source with no MODULE.md": ("no-document", "MODULE.md does not exist — fix: restore"),
        "a source whose document has no t9 anchor": ("no-t9", f'has no anchor <a id="t9"></a> {anchor}'),
        "a source whose t9 anchor has text on its line": (
            "t9-on-heading",
            f'has no anchor <a id="t9"></a> {anchor}',
        ),
        "a source whose t9 anchor stands twice": (
            "t9-twice",
            'holds the anchor <a id="t9"></a> twice, lines 1 and 2 — fix: keep the one before',
        ),
        "a source whose t10 anchor is gone while t11 stands": (
            "t10-missing",
            'has no anchor <a id="t10"></a> after <a id="t9"></a> — fix: restore it',
        ),
        "a source with a second t10 anchor above an E-row": (
            "t10-twice",
            'holds the anchor <a id="t10"></a> twice, lines 3 and 5 — fix: keep the one before',
        ),
    }
    for name, (change, said) in unreadable.items():
        try:
            findings_of(change)
            ok, line = False, "no BROKEN"
        except Broken as broken:
            ok, line = said in str(broken), str(broken)
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name} is a teaching BROKEN line, never a scan left unrun")
        if not ok:
            print(f"        got: {line}")
    with tempfile.TemporaryDirectory() as tmp:  # what a row reads as, its problems left to check-gate-lists
        plugin = Path(tmp)
        declares: dict[str, list[str]] = {
            "   | E1 | `check-x --scan` | `gate` |\n": ["check-x"],
            "|**E1**|`check-x --scan`|`gate`|\n": ["check-x"],
            "| G1 | `check-x --scan` | `gate` |\n": ["check-x"],
            "| E1 | `check-x --scan --command <t>`: the explain, not a tree scan | `gate` |\n": [],
            "| E1 | `check-x --scan --command <t>` | `gate` |\n": [],
            "| E1 | `gate` | `check-x --scan`\n": ["check-x"],  # no closing bar: the last cell is read
            "| E1 | `check-x.py --scan`\n": ["check-x.py"],
            "| E1 | `gate` | `check-x --scan --command <t>`: not a tree scan\n": [],
            "| E1 | `sh scripts/x.sh --scan` | `gate` |\n": [],
            "Run `check-x --scan` here.\n": [],
        }
        ok = True
        for text_row, expected in declares.items():
            (plugin / "MODULE.md").write_text(
                f'<a id="t9"></a>\n{text_row}<a id="t10"></a>\n', encoding="utf-8"
            )
            ok = ok and declared_scans(plugin) == expected
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a module's scans are the rows it declares, read whatever their form")
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
    with tempfile.TemporaryDirectory() as tmp:
        record = Path(tmp) / "installed_plugins.json"
        entry = {"installPath": "/cache/const-x/0.0.1", "gitCommitSha": "abc"}
        record.write_text(json.dumps({"plugins": {f"const-x@{MARKETPLACE}": [entry]}}), encoding="utf-8")
        ok = installed_entry(record, "const-x") == (Path("/cache/const-x/0.0.1"), "abc")
        del entry["gitCommitSha"]
        record.write_text(json.dumps({"plugins": {f"const-x@{MARKETPLACE}": [entry]}}), encoding="utf-8")
        ok = ok and installed_entry(record, "const-x") == (Path("/cache/const-x/0.0.1"), "")
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the install record gives the copy's folder and its commit, or none")
    with tempfile.TemporaryDirectory() as tmp:  # the kit's own history: the source at the commit checked out
        head = run(["git", "rev-parse", "HEAD"], KIT, os.environ.copy())[1]
        root = Path(tmp).resolve()
        extracted = source_at(head, "const-meta-types", root)
        ok = extracted == root / "source" / "modules" / "const-meta-types"
        ok = (
            ok and (extracted / "MODULE.md").is_file() and (extracted / "scripts" / "const_gate").is_symlink()
        )
        target = (extracted / "scripts" / "const_gate").resolve()
        ok = ok and target.is_relative_to(root / "source" / "shared") and target.is_dir()
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the source at a commit is read from the kit's history")
    total = len(cases) + len(unreadable) + 4
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-bare-install", add_help=False, allow_abbrev=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--module")
    group.add_argument("--self-test", action="store_true")
    parser.add_argument("--from", dest="source")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with --module <name> [--from <source>], or with --self-test")
        print("BROKEN: the check could not run — 0 modules examined")
        return EXIT_BROKEN
    try:
        if args.self_test:
            return self_test()
        module = str(args.module)
        source = args.source or os.environ.get(FROM_ENV) or str(KIT)
        if Path(source).exists():  # the install runs in another folder, so a local source is made absolute
            source = str(Path(source).resolve())
        findings, examined = check_module(module, source)
        return report(module, findings, f"{examined}, from {source}")
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 modules examined")
        return EXIT_BROKEN
    except OSError as bad:
        print(f"BROKEN: a file could not be read ({bad}) — fix: make the module's files readable")
        print("BROKEN: the check could not run — 0 modules examined")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
