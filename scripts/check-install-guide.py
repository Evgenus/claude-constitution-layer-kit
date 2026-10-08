#!/usr/bin/env python3
"""Kit check: the install guide's commands run, and do what the guide says they do — rule 4 of
plc-0011-install-guide (decision dec-0062-install-guide-governed-kind).

The guide is INSTALL.md at the kit's root, read as committed at the working folder's HEAD, the
commit the run clones. First its marks, read from the text:
  every `bash` fence names `check=<name>` after its language — a name of the set below, each
  standing in the guide exactly once, or `none`, a block the check does not run, as often as
  needed; the dials example is the one `yaml` fence named `check=dials`; a fence that opens with
  `check=<name>` where its language should stand is red too.
Then the run, in throwaway folders the check removes: a home folder of its own, HOME and
CLAUDE_CONFIG_DIR (<home>/.claude) under it and git's identity in a global configuration of its
own; the kit cloned from the working folder's HEAD to ~/dev/constitution-kit, so what is not
committed is not run; the source the marketplace block registers pointed at the change: the
argument of its `claude plugin marketplace add` replaced by the environment's
CONSTITUTION_KIT_INSTALL_FROM, `<owner>/<repo>#<branch>` (the kit's CI names the change's GitHub
repository and branch), else by the working folder's origin on GitHub at the branch checked out,
which must be at HEAD. In CI the clone is the job's checkout of the change, a pull request's merge
commit, and the source its head branch: the marketplace claim holds that both give the same
modules at the same versions. And the named blocks
run in the guide's order, each written to a file and
sourced by a fresh `bash -eu` in the folder the block before it ended in, the first in the home
folder, so a block that relies on a variable another block set fails on it, unset. A block's exit is
what `bash -eu` gives the sourcing: a block's last command decides it, and a command that fails
inside an `&&` list earlier in the block, other than the list's last, stops no block, so what such a
block does is held by the claims below, not by its exit.
Beside every block's exit 0, the check holds at each name:
  new-repo     the block ends in a git repository: the project.
  marketplace  the configuration's plugins/known_marketplaces.json knows the kit's marketplace, by the
               name the clone's .claude-plugin/marketplace.json gives, read once by
               `kit_module_doc.marketplace_name` and typed nowhere: the later claims' `<module>@<name>`
               keys, cache and marketplace-clone folders and install fix all use it; from
               a GitHub source naming the source's repository: a local folder would run in place,
               never from the cache; and the platform's clone of the marketplace holds the same
               modules at the same manifest versions as the kit's clone.
  install      every module of the kit stands in the plugin cache at its manifest version and is
               enabled in the project's .claude/settings.json; and a headless session in the
               project, trusted in the configuration, reports each module's path in the plugin
               cache — the frozen copy, never a clone's working files. The path is reported before
               the model is called, so the session needs no login.
  kernel       the project's docs/constitution/ holds every file of the kit's kernel/, and the kit's
               LICENSE and NOTICE, byte for byte.
  dials        not run: written as the project's constitution.yaml, and with it what the reader
               writes by hand, from the check's fixture — one policy per namespace of the dials that
               claims a territory, the root at `root_policy`, and decision record #1, named and placed by
               the dials' first catalog.
  scan         the block's exit: every scan it runs exits 0.
  commit       the project's working tree is clean.
  update       every module stays in the plugin cache at its manifest version and enabled. That an
               update leaves a draft's change at an unchanged version untaken is not run: the
               platform fetches a GitHub marketplace from GitHub alone, so the run cannot put a
               change where it looks; the guide states it as an observed platform fact.
  reinstall    every module stands in the plugin cache at its version and is enabled, and its copy
               there holds the same files as the module in the platform's clone of the marketplace,
               read through its links, byte for byte: the install copied what the marketplace holds.
  uninstall    no module is enabled in the project's settings or recorded for the project in the
               configuration's plugins/installed_plugins.json.
The first finding of the run ends it, since every later block builds on the one before. A finding
is red; a missing `claude`, `git` or `bash`, or a guide that cannot be read, is a configuration
failure, and so is a source the check cannot point at the change: no origin on GitHub, a detached
HEAD, or a branch whose origin copy is not at HEAD, and a clone whose marketplace.json gives no name
(missing, no JSON, no object, no "name", one that is no string or is empty). Needs no Claude account
login: the plugin commands read none, and the session stops before the model. Git needs a private
repository's credentials.

Before the clone, and before any block runs, once the marks are read and `claude` is found on PATH, the
check asks `claude --version` (`kit_module_doc.claude_note`) and compares it with the version the
working folder's scripts/claude-code.version pins, which the CI workflow installs from too; the clone
carries the same file. The pinned version: the run goes on. Another readable version: a configuration
failure, whose fix puts the pinned Claude Code first on PATH beside the person's own, unless the
environment's CONSTITUTION_KIT_ANY_CLAUDE is exactly `1`: the run then goes on, and each `RED:` finding
headline, each `BROKEN:` line and the closing `GREEN:` or `RED:` line ends with a note naming both
versions. No readable version (the command fails, prints nothing, or opens with a word that is no
version) and a pin file that is missing, empty or no one version are configuration failures whatever
the variable says. A guide whose marks are red is reported before any of this, since it runs no `claude`.

Modes:  no arguments   check the kit's guide;
        --self-test    prove the check with a toy kit, a toy guide and a fake `claude` that logs to
                       a file: each kind of mark finding red once from the text alone; a green toy run
                       green; a mark where a fence's language should be red; a block that exits 1 red; a
                       block that reads another block's variable red, though it would pass under
                       `bash -e`; a guide not committed at HEAD a configuration failure, and the
                       committed one read whole, standard output alone; a folder that is no clone a
                       configuration failure, to the guide's reader and to the run; a misplaced
                       dials mark red once, its fix a `yaml` fence; a run whose git writes a trace
                       to stderr green;
                       the dials before the project red; a marketplace block with no source to point
                       red; each claim red once against a fake or a block that breaks it — a block
                       that makes no repository, a marketplace never added, one added from a folder,
                       an install that enables nothing, a session that runs a module in place, a
                       kernel copy that copies nothing, one that leaves the license out, a commit
                       that leaves the tree dirty, an update that drops a module, a reinstall whose
                       copy differs from the marketplace, an uninstall that keeps the plugin enabled;
                       a marketplace from another repository, one whose modules differ from the kit's and
                       the fix it teaches, each marketplace and install finding's own fix and the fix of a
                       marketplace and an install block that exits 1, a session that loads no module and
                       one that reports no start, its own reason quoted, a reinstall copy that lacks a
                       file of the marketplace, the toy modules' links into a toy shared/ read through on
                       both sides; the outer credential settings carried into the run as git reads them,
                       includes followed, nothing else of the outer configuration, and the carried helper
                       reaching the run's git; the toy kit left as it was, and a green guide's marks with
                       a `text` fence needing none; the source taken from the environment, from origin at
                       the branch's HEAD, and a kit with no origin on GitHub, a detached HEAD and an
                       origin behind HEAD each a configuration failure; the
                       report of one finding as literal lines with exit 2; the kit's modules, the
                       folders of `kit_module_doc.module_folders` with their manifest versions: a
                       folder `.x` or `_x` and a plain file skipped, a name without `const-` listed,
                       the list sorted whatever order the folder lists, and a folder without its
                       MODULE.md, a tree with no modules/, a modules/ with no folder and a manifest
                       with no version each a BROKEN; the toy kit's marketplace named `toy-mp`, which
                       the toy guide's commands and the fake follow, so the green run, each claim's
                       text and the install fix use that name and no other; `kit_module_doc.marketplace_name`
                       over a file naming `toy-mp` and each of the six files it cannot read, the literal
                       message of each; a toy kit whose marketplace.json gives no name a BROKEN;
                       `kit_module_doc.pinned_claude` over a pin file of each form, the literal message
                       of each; the version check over a fake `claude` that answers `--version` with the
                       toy kit's pin, another version, a longer or shorter one, no version, a failure and
                       a crash, the variable unset, at each other value than `1` and at `1`, the run
                       stopped before the clone with only `--version` run, and the reports of a run off
                       the pin, a finding's and a green one's, as literal lines.
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
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from unittest import mock

import yaml
from kit_module_doc import DocumentError, claude_note, marketplace_name, module_folders, pinned_claude

KIT = Path(__file__).resolve().parent.parent
GUIDE = "INSTALL.md"
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
CLONE = Path("dev") / "constitution-kit"  # the guide's placeholder for the kit's clone, rule 4 of plc-0011
NAMES = (
    "new-repo",
    "marketplace",
    "install",
    "kernel",
    "dials",
    "scan",
    "commit",
    "update",
    "reinstall",
    "uninstall",
)
DOES = {
    "new-repo": "creates the project's repository",
    "marketplace": "registers the kit as a marketplace",
    "install": "installs every module at project scope",
    "kernel": "copies the kernel",
    "dials": "is the dials example",
    "scan": "runs every module's scan",
    "commit": "commits the bootstrap",
    "update": "updates the plugins",
    "reinstall": "uninstalls and installs each module again",
    "uninstall": "uninstalls every module",
}
FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
MARK = re.compile(r"(?:^|\s)check=(\S*)")
FROM_ENV = "CONSTITUTION_KIT_INSTALL_FROM"
ADD = re.compile(r"(claude plugin marketplace add\s+)(\S+)")  # the source the marketplace block registers
GITHUB_URL = re.compile(r"github\.com[:/]([^/\s]+/[^/\s]+?)(?:\.git)?/?$")
LICENSE_FILES = ("LICENSE", "NOTICE")  # the kit's license and credit, copied beside the kernel
RECORD_SLUG = "adopt-constitution-kernel"
WHY = "a command nobody runs drifts from the platform unseen (rule 4 of plc-0011-install-guide)"
TIMEOUT = 900


class Broken(Exception):
    """The check could not run; the message says why and how to fix it. `note` is the note of a run on
    another Claude Code than the pin, set once the version is known, which ends each BROKEN line."""

    note = ""


class Misfit(Exception):
    """A claim that failed with a fix of its own, not the one its name teaches."""

    def __init__(self, what: str, fix: str) -> None:
        super().__init__(what)
        self.what, self.fix = what, fix


@dataclass(frozen=True)
class Finding:
    line: int
    what: str
    fix: str

    def render(self, note: str = "") -> str:
        """The finding as lines, the note of a run off the pin at the end of its headline."""
        where = f"{GUIDE}:{self.line}" if self.line else GUIDE
        return f"RED: {where}: {self.what}{note}\n  why: {WHY}\n  fix: {self.fix}"


@dataclass(frozen=True)
class Block:
    line: int
    language: str
    name: str
    text: str


def blocks_of(guide: str) -> tuple[list[Block], list[Finding]]:
    """Every fenced block of the guide with its mark, and the findings the marks give."""
    found: list[Block] = []
    findings: list[Finding] = []
    lines = guide.splitlines()
    i = 0
    while i < len(lines):
        opened = FENCE.match(lines[i])
        if not opened:
            i += 1
            continue
        indent, fence, info = opened.group(1), opened.group(2), opened.group(3).strip()
        body: list[str] = []
        j = i + 1
        while j < len(lines):
            closing = FENCE.match(lines[j])
            if closing and closing.group(2)[0] == fence[0] and len(closing.group(2)) >= len(fence):
                if not closing.group(3).strip():
                    break
            body.append(lines[j][len(indent) :] if lines[j].startswith(indent) else lines[j].lstrip())
            j += 1
        words = info.split()
        language = words[0] if words else ""
        mark = MARK.search(" ".join(words[1:]))
        found.append(Block(i + 1, language, mark.group(1) if mark else "", "\n".join(body) + "\n"))
        i = j + 1
    seen: dict[str, int] = {}
    for block in found:
        if block.language.startswith("check="):
            findings.append(
                Finding(
                    block.line,
                    f"the fence opens with {block.language} where its language should stand",
                    f"write the language first, then the mark: "
                    f"```{'yaml' if block.language == 'check=dials' else 'bash'} {block.language}",
                )
            )
            continue
        if block.language == "bash" and not block.name:
            findings.append(
                Finding(
                    block.line,
                    "a `bash` block names no check",
                    f"write `check=<name>` after `bash` in its fence — one of {', '.join(NAMES)} — "
                    "or `check=none` for a block the check does not run",
                )
            )
            continue
        if not block.name or block.name == "none":
            continue
        if block.name not in NAMES:
            findings.append(
                Finding(
                    block.line,
                    f"check={block.name} is no name the check knows",
                    f"use one of {', '.join(NAMES)}, or `none`",
                )
            )
            continue
        wanted = "yaml" if block.name == "dials" else "bash"
        if block.language != wanted:
            findings.append(
                Finding(
                    block.line,
                    f"check={block.name} stands on a `{block.language}` fence",
                    f"name a `{wanted}` fence check={block.name}",
                )
            )
            continue
        if block.name in seen:
            findings.append(
                Finding(
                    block.line,
                    f"check={block.name} stands a second time, first at line {seen[block.name]}",
                    "give each named block a name of its own: join the two blocks, or name one `none`",
                )
            )
            continue
        seen[block.name] = block.line
    for name in NAMES:
        said = (f"check={name} ", f"the fence opens with check={name} ")
        if name not in seen and not any(f.what.startswith(said) for f in findings):
            findings.append(
                Finding(
                    0, f"no block is named check={name}", f"name the block that {DOES[name]} check={name}"
                )
            )
    return [b for b in found if b.name in NAMES and seen.get(b.name) == b.line], findings


def run(
    argv: list[str], cwd: Path, env: dict[str, str], timeout: int = TIMEOUT, joined: bool = True
) -> tuple[int, str]:
    """The exit and the output of one command: standard output and error joined, for a message, or
    standard output alone where the output is read as data."""
    try:
        done = subprocess.run(
            argv,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as bad:
        raise Broken(
            f"{argv[0]} is not installed ({bad.strerror}) — fix: install it and put it on PATH"
        ) from bad
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout} s"
    both = done.stdout + ("\n" if done.stdout and done.stderr else "") + done.stderr  # never one line of two
    return done.returncode, (both if joined else done.stdout).strip()


def last_line(said: str) -> str:
    return said.splitlines()[-1] if said else "no output"


def modules_of(kit: Path) -> dict[str, str]:
    """Each module of the kit with its manifest version, the folders those of the kit's one listing,
    `kit_module_doc.module_folders`: a plain file there is none, a name without `const-` is one, a
    folder without its MODULE.md, and a tree with no modules/, are BROKEN."""
    found: dict[str, str] = {}
    try:
        folders = module_folders(kit)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad
    for folder in folders:
        manifest = folder / ".claude-plugin" / "plugin.json"
        try:
            found[folder.name] = str(json.loads(manifest.read_text(encoding="utf-8"))["version"])
        except (OSError, ValueError, KeyError) as bad:
            raise Broken(f"{manifest} gives no version ({bad}) — fix: restore the module's manifest") from bad
    if not found:
        raise Broken(f"no module under {kit / 'modules'} — fix: run the check from a clone of the kit")
    return found


def read_json(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def enabled(project: Path) -> set[str]:
    plugins = read_json(project / ".claude" / "settings.json").get("enabledPlugins")
    return {str(k) for k, v in plugins.items() if v is True} if isinstance(plugins, dict) else set()


def recorded(config: Path, project: Path) -> set[str]:
    plugins = read_json(config / "plugins" / "installed_plugins.json").get("plugins")
    found: set[str] = set()
    if isinstance(plugins, dict):
        for key, entries in plugins.items():
            for entry in entries if isinstance(entries, list) else []:
                if isinstance(entry, dict) and str(entry.get("projectPath", "")) in (
                    str(project),
                    str(project.resolve()),
                ):
                    found.add(str(key))
    return found


def fixture(project: Path, dials: str) -> None:
    """What the reader writes by hand: the dials file, one policy per namespace that claims a
    territory, the root at `root_policy`, and decision record #1, named and placed by the dials' first
    catalog."""
    (project / "constitution.yaml").write_text(dials, encoding="utf-8")
    try:
        data = yaml.safe_load(dials)
    except yaml.YAMLError as bad:
        raise Broken(
            f"the dials example is no YAML ({bad}) — fix: correct the guide's check=dials block"
        ) from bad
    if not isinstance(data, dict):
        raise Broken("the dials example is no mapping — fix: correct the guide's check=dials block")
    root = str(data.get("root_policy", ""))
    for key, value in data.items():
        if not (isinstance(value, dict) and "territory" in value):
            continue
        path = project / (root if root.endswith(f"/{key}.md") else f"docs/policies/{key}.md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nid: {key}\ntype: current-state\ntitle: The {key} policy\nstatus: active\n---\n\n"
            f"# The {key} policy\n\nThis policy governs one kind of document.\n",
            encoding="utf-8",
        )
    catalogs = (
        data.get("const-catalogs", {}).get("catalogs")
        if isinstance(data.get("const-catalogs"), dict)
        else None
    )
    first = catalogs[0] if isinstance(catalogs, list) and catalogs and isinstance(catalogs[0], dict) else None
    territory = first.get("territory") if first else None
    if not (first and isinstance(territory, list) and territory and str(territory[0]).endswith("/**")):
        raise Broken(
            "the dials example lists no catalog with a folder territory, so record #1 has no home — "
            "fix: correct the guide's check=dials block"
        )
    stem = f"{first.get('prefix')}-{1:0{int(first.get('width', 4))}d}-{RECORD_SLUG}"
    record = project / str(territory[0]).removesuffix("/**").lstrip("/") / f"{stem}.md"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(
        f"---\nid: {stem}\ntype: task-record\ntitle: Adopt constitution kernel\n"
        "status: inactive\nstakes: process\ndecider: the owner\n---\n\n# Adopt constitution kernel\n\n"
        "We adopt the kernel.\n",
        encoding="utf-8",
    )


@dataclass
class Run:
    home: Path
    kit: Path
    config: Path
    env: dict[str, str]
    modules: dict[str, str]
    cwd: Path
    source: str
    marketplace: str  # the name the kit's clone gives its marketplace, read once from its marketplace.json
    project: Path | None = None

    def cache(self, module: str) -> Path:
        return self.config / "plugins" / "cache" / self.marketplace / module / self.modules[module]

    def market(self, module: str) -> Path:
        """The module in the platform's own clone of the marketplace."""
        return self.config / "plugins" / "marketplaces" / self.marketplace / "modules" / module


def session_paths(state: Run, project: Path) -> tuple[dict[str, str] | None, str]:
    """Each plugin's path as a headless session in the project reports it at start, the project trusted
    in the configuration first — None when the session reported no start — and its last line."""
    dot = state.config / ".claude.json"
    data = read_json(dot)
    projects = data.get("projects")
    if not isinstance(projects, dict):
        projects = data["projects"] = {}
    for key in {str(project), str(project.resolve())}:
        entry = projects.get(key)
        projects[key] = (entry if isinstance(entry, dict) else {}) | {"hasTrustDialogAccepted": True}
    dot.write_text(json.dumps(data), encoding="utf-8")
    argv = ["claude", "-p", "Reply with the single word ok.", "--output-format", "stream-json"]
    _, said = run([*argv, "--verbose", "--max-turns", "1"], project, state.env, timeout=300)
    for line in said.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("type") == "system" and event.get("subtype") == "init":
            plugins = event.get("plugins")
            return {
                str(p.get("name")): str(p.get("path"))
                for p in (plugins if isinstance(plugins, list) else [])
                if isinstance(p, dict)
            }, ""
    return None, last_line(said)


def files_through_links(folder: Path) -> dict[str, Path]:
    """Every file under a folder by its relative path, links to folders followed, caches left out."""
    found: dict[str, Path] = {}
    for where, folders, files in os.walk(folder, followlinks=True):
        folders[:] = [f for f in folders if f != "__pycache__"]
        for name in files:
            path = Path(where) / name
            if path.is_file():
                found[str(path.relative_to(folder))] = path
    return found


def differing(cache: Path, market: Path) -> str:
    """The first file that the cached copy and the marketplace clone's module do not hold alike, read
    through their links, or the empty string."""
    held, wanted = files_through_links(cache), files_through_links(market)
    for name in sorted(held.keys() | wanted.keys()):
        if name not in held or name not in wanted or held[name].read_bytes() != wanted[name].read_bytes():
            return name
    return ""


def claim(state: Run, name: str) -> str:
    """What fails of the guide's claim at a name, or the empty string."""
    project = state.project
    if name == "new-repo":
        code, _ = run(["git", "rev-parse", "--show-toplevel"], state.cwd, state.env)
        if code != 0:
            return "the block ends in no git repository"
        state.project = state.cwd
        return ""
    if project is None:
        return "no block named check=new-repo made the project first"
    if name == "marketplace":
        known = read_json(state.config / "plugins" / "known_marketplaces.json").get(state.marketplace)
        if not isinstance(known, dict):
            raise Misfit(
                f"the configuration knows no marketplace {state.marketplace}",
                "make the block register the kit's repository, "
                "`claude plugin marketplace add <owner>/<repo>`",
            )
        source = known.get("source")
        kind = source.get("source") if isinstance(source, dict) else None
        if kind != "github":
            raise Misfit(f"the marketplace is registered from a {kind} source, not from GitHub", IN_PLACE)
        repo = source.get("repo") if isinstance(source, dict) else None
        wanted = state.source.split("#")[0]
        if repo != wanted:
            raise Misfit(
                f"the marketplace is registered from {repo}, not from {wanted}",
                f"make the block register the source it is given, {FROM_ENV} or the clone's origin, "
                "and nothing after it",
            )
        mend = (
            "bring the source branch to the kit's clone — merge main into it and push — or point "
            f"{FROM_ENV} at the branch the clone holds"
        )
        try:
            market = modules_of(state.config / "plugins" / "marketplaces" / state.marketplace)
        except Broken as bad:
            said = str(bad).split(" — fix:")[0]
            raise Misfit(f"the platform's clone of the marketplace cannot be read ({said})", mend) from bad
        if market != state.modules:
            raise Misfit(f"the marketplace holds {market}, the kit's clone {state.modules}", mend)
        return ""
    if name in ("install", "reinstall", "update"):
        on = enabled(project)
        for module in state.modules:
            if not state.cache(module).is_dir():
                return f"{module} is not in the plugin cache at {state.modules[module]}"
            if f"{module}@{state.marketplace}" not in on:
                return f"{module} is not enabled in the project's .claude/settings.json"
        if name == "reinstall":
            for module in state.modules:
                odd = differing(state.cache(module), state.market(module))
                if odd:
                    return f"{module}'s {odd} is not alike in the cache and the marketplace"
        if name == "install":
            paths, last = session_paths(state, project)
            if paths is None:
                raise Misfit(
                    f"a session in the project reported no start ({last})",
                    "run §2 steps 1 to 3 in a project of your own, then `claude -p ok --output-format "
                    "stream-json --verbose` there, and read why it stops before its start event",
                )
            for module in state.modules:
                where = paths.get(module)
                if where is None:
                    raise Misfit(
                        f"a session in the project loads no {module}",
                        "run §2 steps 1 to 3 in a project of your own and read the Errors tab of `/plugin` "
                        "in a session there: a module cached and enabled that a session does not load "
                        "failed to load",
                    )
                if Path(where).resolve() != state.cache(module).resolve():
                    raise Misfit(f"a session runs {module} from {where}, not from the plugin cache", IN_PLACE)
        return ""
    if name == "kernel":
        source = state.kit / "kernel"
        for path in sorted(p for p in source.rglob("*") if p.is_file()):
            copy = project / "docs" / "constitution" / path.relative_to(source)
            if not copy.is_file() or copy.read_bytes() != path.read_bytes():
                return f"docs/constitution/{path.relative_to(source)} is not the kernel's file"
        for held in LICENSE_FILES:
            copy = project / "docs" / "constitution" / held
            if not copy.is_file() or copy.read_bytes() != (state.kit / held).read_bytes():
                return f"docs/constitution/{held} is not the kit's file"
        return ""
    if name == "commit":
        code, said = run(["git", "status", "--porcelain"], project, state.env, joined=False)
        return "" if code == 0 and not said else "the project's working tree is not clean after the commit"
    if name == "uninstall":
        left = sorted(
            {f"{m}@{state.marketplace}" for m in state.modules}
            & (enabled(project) | recorded(state.config, project))
        )
        return f"{', '.join(left)} still installed for the project" if left else ""
    return ""


IN_PLACE = (
    "register the kit from GitHub, `claude plugin marketplace add <owner>/<repo>`: a marketplace added from "
    "a local folder runs that folder's working files in place, never the frozen copy"
)


def fix_for(name: str, marketplace: str) -> str:
    if name == "marketplace":
        return (
            f"let git clone the source the block is given — {FROM_ENV}, `<owner>/<repo>#<branch>`, else the "
            "clone's origin at the branch checked out, naming a "
            "repository and branch that exist — with a credential for github.com while the repository is "
            "private, as `gh auth setup-git` sets one up; and make the block's other commands succeed"
        )
    if name == "install":
        return (
            "make the block install each module at project scope, "
            f"`claude plugin install <module>@{marketplace} --scope project`"
        )
    return (
        f"make the block named check={name} do what the guide says it does, "
        "or correct the guide and the check"
    )


def source_of(kit: Path, env: dict[str, str]) -> str:
    """Where the marketplace block installs from: the environment's CONSTITUTION_KIT_INSTALL_FROM, else
    the kit's origin on GitHub at the branch checked out, which must be at HEAD."""
    given = env.get(FROM_ENV, "").strip()
    if given:
        return given
    teach = f"or set {FROM_ENV}=<owner>/<repo>#<branch>"
    code, url = run(["git", "remote", "get-url", "origin"], kit, env, joined=False)
    found = GITHUB_URL.search(url) if code == 0 else None
    if not found:
        raise Broken(f"the kit has no origin on GitHub to install from — fix: add one, {teach}")
    code, branch = run(["git", "symbolic-ref", "--quiet", "--short", "HEAD"], kit, env, joined=False)
    if code != 0 or not branch:
        raise Broken(f"HEAD is detached, so no branch to install from — fix: check out a branch, {teach}")
    _, head = run(["git", "rev-parse", "HEAD"], kit, env, joined=False)
    code, remote = run(["git", "ls-remote", "origin", f"refs/heads/{branch}"], kit, env, joined=False)
    if code != 0 or not head or not remote.startswith(head):
        raise Broken(
            f"origin's {branch} is not at HEAD, so the install would not come from what the clone holds — "
            f"fix: push the branch (git push), {teach}"
        )
    return f"{found.group(1)}#{branch}"


def carry_credentials(env: dict[str, str], gitconfig: Path) -> None:
    """Add the outer git configuration's credential settings, includes followed, to the run's own
    configuration, git writing each entry so that it reads back the same: the run replaces HOME and the
    global configuration, and a private repository's clone needs the helper the machine or the CI job set
    up, and nothing else of that configuration. A key git holds with no value is a true boolean."""
    argv = ["git", "config", "--global", "--includes", "-z", "--get-regexp", r"^credential\."]
    code, said = run(argv, Path.cwd(), env, joined=False)
    for entry in said.split("\0") if code == 0 else []:
        if not entry:
            continue
        key, newline, value = entry.partition("\n")
        code, wrote = run(
            ["git", "config", "--file", str(gitconfig), "--add", key, value if newline else "true"],
            Path.cwd(),
            env,
        )
        if code != 0:
            raise Broken(
                f"the credential setting {key} could not be carried ({last_line(wrote)}) — "
                "fix: correct that entry in the global git configuration, "
                "or in the file it includes that holds it"
            )


def unreadable_said(bad: OSError) -> str:
    return (
        f"a file could not be read or written ({bad}) — "
        "fix: make the kit's files readable and the system's temporary folder writable"
    )


def claude_noted(kit: Path, env: dict[str, str]) -> str:
    """The note for a run on another Claude Code than the kit pins, "" on the pinned one, from
    `kit_module_doc.claude_note`; its refusal is a Broken with that function's line."""
    try:
        return claude_note(kit, env)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad


def run_guide(guide: str, kit: Path, base_env: dict[str, str]) -> tuple[list[Finding], str, str]:
    """The guide's findings, its marks first and then its run, what was examined, and the note of a run
    on another Claude Code than the kit pins ("" when no `claude` was asked or it is the pinned one). The
    version is asked once the marks are read and `claude` is found on PATH, before the clone and before
    any block runs, against the pin of the kit's working folder."""
    named, findings = blocks_of(guide)
    if findings:
        return findings, f"{len(named)} named block(s), not run", ""
    for block in named:
        if block.name == "marketplace" and not ADD.search(block.text):
            return (
                [
                    Finding(
                        block.line,
                        "the block named check=marketplace runs no `claude plugin marketplace add <source>` "
                        "the check can point at the change",
                        "register the kit with `claude plugin marketplace add <owner>/<repo>`",
                    )
                ],
                f"{len(named)} named block(s), not run",
                "",
            )
    source = source_of(kit, base_env)
    for tool in ("git", "bash", "claude"):
        if shutil.which(tool, path=base_env.get("PATH")) is None:
            raise Broken(
                f"{tool} is not on PATH — fix: install it; the check runs the guide's commands with it"
            )
    note = claude_noted(kit, base_env)
    try:
        found, examined = run_blocks(named, kit, base_env, source)
    except Broken as bad:
        bad.note = note
        raise
    except OSError as bad:  # the note ends this BROKEN line too, so it is made here and not in main
        unreadable = Broken(unreadable_said(bad))
        unreadable.note = note
        raise unreadable from bad
    return found, examined, note


def run_blocks(
    named: list[Block], kit: Path, base_env: dict[str, str], source: str
) -> tuple[list[Finding], str]:
    """The named blocks run in the guide's order in a home folder of their own, and what was examined."""
    with tempfile.TemporaryDirectory(prefix="install-guide-") as scratch:
        home = Path(scratch) / "home"
        config = home / ".claude"
        config.mkdir(parents=True)
        (home / ".gitconfig").write_text(
            "[user]\n\tname = install-guide\n\temail = install-guide@example.invalid\n"
            "[init]\n\tdefaultBranch = main\n[commit]\n\tgpgsign = false\n",
            encoding="utf-8",
        )
        carry_credentials(base_env, home / ".gitconfig")
        env = base_env | {
            "HOME": str(home),
            "CLAUDE_CONFIG_DIR": str(config),
            "GIT_CONFIG_GLOBAL": str(home / ".gitconfig"),
            "DISABLE_AUTOUPDATER": "1",
        }
        clone = home / CLONE
        clone.parent.mkdir(parents=True)
        head = subprocess.run(  # standard output alone, so no warning on stderr joins the commit
            ["git", "rev-parse", "HEAD"], cwd=kit, env=env, capture_output=True, text=True, check=False
        )
        if head.returncode != 0:
            raise Broken(
                f"{kit} is no git clone ({last_line(head.stderr.strip())}) — "
                "fix: run the check from a clone of the kit"
            )
        for argv, where in (
            (["git", "clone", "--quiet", "--no-checkout", str(kit), str(clone)], home),
            (["git", "checkout", "--quiet", "--detach", head.stdout.strip()], clone),
        ):
            code, said = run(argv, where, env)
            if code != 0:
                raise Broken(f"the kit could not be cloned ({last_line(said)}) — fix: check the clone")
        try:
            marketplace = marketplace_name(clone)
        except DocumentError as bad:
            raise Broken(str(bad)) from bad
        state = Run(home, clone, config, env, modules_of(clone), home, source, marketplace)
        ran = 0
        for block in named:
            if block.name == "dials":
                if state.project is None:
                    return [
                        Finding(
                            block.line,
                            "the dials example comes before the project exists",
                            fix_for("dials", state.marketplace),
                        )
                    ], f"{ran} block(s) run"
                fixture(state.project, block.text)
                continue
            text = block.text
            if block.name == "marketplace":
                text = ADD.sub(lambda m: m.group(1) + source, text, count=1)
            script = Path(scratch) / f"{block.name}.sh"
            where = Path(scratch) / f"{block.name}.cwd"
            body = Path(scratch) / f"{block.name}.block.sh"
            body.write_text(text, encoding="utf-8")
            script.write_text(f'. "{body}"\npwd > "{where}"\n', encoding="utf-8")
            code, said = run(["bash", "-eu", str(script)], state.cwd, env)
            ran += 1
            if where.is_file():
                state.cwd = Path(where.read_text(encoding="utf-8").strip())
            if code != 0:
                what = f"the block named check={block.name} exited {code} — {last_line(said)}"
                return [
                    Finding(block.line, what, fix_for(block.name, state.marketplace))
                ], f"{ran} block(s) run"
            try:
                failed, fix = claim(state, block.name), fix_for(block.name, state.marketplace)
            except Misfit as misfit:
                failed, fix = misfit.what, misfit.fix
            if failed:
                return [
                    Finding(block.line, f"after check={block.name}: {failed}", fix)
                ], f"{ran} block(s) run"
        return [], f"{ran} block(s) run, {len(state.modules)} module(s), from {source}"


def committed_guide(kit: Path, env: dict[str, str]) -> str:
    """The guide as committed at the kit's HEAD, the commit the run clones: standard output alone."""
    if run(["git", "rev-parse", "HEAD"], kit, env)[0] != 0:  # run() turns a missing git into Broken
        raise Broken(f"{kit} is no git clone with a commit — fix: run the check from a clone of the kit")
    done = subprocess.run(
        ["git", "show", f"HEAD:{GUIDE}"], cwd=kit, env=env, capture_output=True, text=True, check=False
    )
    if done.returncode != 0:
        raise Broken(
            f"{GUIDE} is not committed at HEAD ({last_line(done.stderr.strip())}) — fix: commit the guide"
        )
    return done.stdout


def report(findings: list[Finding], examined: str, note: str = "") -> int:
    if findings:
        for finding in findings:
            print(finding.render(note))
        print(f"RED: {len(findings)} finding(s) — {examined}{note}")
        return EXIT_RED
    print(f"GREEN: the install guide runs and does what it says — {examined}{note}")
    return EXIT_GREEN


FAKE = '''#!/usr/bin/env python3
"""A fake claude for the self-test: the plugin commands the guide runs and a session's start, logged
to a file (FAKE_LOG, else the configuration folder's). A marketplace added from `<owner>/<repo>#<branch>`
is a GitHub one, cloned from the toy kit the environment names; one added from a path is a local folder.
`--version` answers the pin of the toy kit, as the real one writes it, or FAKE_SAYS (escapes read) with
the exit FAKE_EXIT."""
import json, os, shutil, subprocess, sys
from pathlib import Path
mutant = os.environ.get("FAKE_MUTANT", "")
config = Path(os.environ["CLAUDE_CONFIG_DIR"])
with open(os.environ.get("FAKE_LOG") or config / "fake.log", "a", encoding="utf-8") as log:
    log.write(" ".join(sys.argv[1:]) + "\\n")
if sys.argv[1:] == ["--version"]:
    pin = (Path(os.environ["FAKE_SOURCE"]) / "scripts" / "claude-code.version").read_text().strip()
    said = os.environ.get("FAKE_SAYS")
    sys.stdout.write(pin + " (Claude Code)\\n" if said is None else said.encode().decode("unicode_escape"))
    sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
plugins = config / "plugins"
plugins.mkdir(parents=True, exist_ok=True)
known = plugins / "known_marketplaces.json"
installed = plugins / "installed_plugins.json"
name = json.loads(
    (Path(os.environ["FAKE_SOURCE"]) / ".claude-plugin" / "marketplace.json").read_text()
)["name"]
market = plugins / "marketplaces" / name
settings = Path.cwd() / ".claude" / "settings.json"
def load(path):
    return json.loads(path.read_text()) if path.is_file() else {}
def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
def cache_of(module):
    manifest = market / "modules" / module / ".claude-plugin" / "plugin.json"
    version = json.loads(manifest.read_text())["version"]
    return plugins / "cache" / name / module / version
args = sys.argv[1:]
if args[:3] == ["plugin", "marketplace", "add"]:
    if Path(os.path.expanduser(args[3])).exists() or mutant == "marketplace-directory":
        source = {"source": "directory", "path": args[3]}
    elif os.environ.get("FAKE_NEEDS_HELPER") and "!gh auth git-credential" not in subprocess.run(
        ["git", "config", "--global", "--get-all", "credential.https://github.com.helper"],
        capture_output=True, text=True,
    ).stdout:
        print("fatal: unable to get password from user", file=sys.stderr)
        sys.exit(1)
    elif args[3] != os.environ["CONSTITUTION_KIT_INSTALL_FROM"]:
        print("fake claude: no such repository " + args[3], file=sys.stderr)
        sys.exit(4)
    else:
        repo = "other/kit" if mutant == "marketplace-other-repo" else args[3].split("#")[0]
        source = {"source": "github", "repo": repo}
    subprocess.run(["git", "clone", "--quiet", os.environ["FAKE_SOURCE"], str(market)], check=True)
    if mutant == "marketplace-fewer-modules":
        shutil.rmtree(market / "modules" / "const-beta")
    if mutant == "marketplace-unreadable":
        (market / "modules" / "const-beta" / "MODULE.md").unlink()
    save(known, {name: {"source": source}})
elif args[:3] == ["plugin", "marketplace", "update"]:
    pass
elif args[:2] == ["plugin", "install"] or args[:2] == ["plugin", "update"]:
    module = args[2].split("@")[0]
    if args[1] == "update":
        if mutant == "update-drops":
            shutil.rmtree(cache_of(module).parent, ignore_errors=True)
        print("already at the latest version")
        sys.exit(0)
    cache = cache_of(module)
    if cache.exists():
        shutil.rmtree(cache)
    shutil.copytree(market / "modules" / module, cache)
    if mutant == "reinstall-stale" and (config / "fake.reinstall").exists():
        (cache / "stale.txt").write_text("an old copy\\n")
    if mutant == "reinstall-lacks" and (config / "fake.reinstall").exists():
        (cache / "MODULE.md").unlink()
    record = load(installed)
    record.setdefault("plugins", {})[args[2]] = [{"scope": "project", "projectPath": str(Path.cwd())}]
    save(installed, record)
    if mutant != "install-no-enable":
        data = load(settings)
        data.setdefault("enabledPlugins", {})[args[2]] = True
        save(settings, data)
elif args[:2] == ["plugin", "uninstall"]:
    (config / "fake.reinstall").write_text("")
    if mutant != "uninstall-keeps":
        record = load(installed)
        record.get("plugins", {}).pop(args[2], None)
        save(installed, record)
        data = load(settings)
        data.get("enabledPlugins", {}).pop(args[2], None)
        save(settings, data)
        module = args[2].split("@")[0]
        shutil.rmtree(plugins / "cache" / name / module, ignore_errors=True)
elif args[:1] == ["-p"] and mutant == "session-no-start":
    print("Error: the session could not start", file=sys.stderr)
    sys.exit(1)
elif args[:1] == ["-p"]:
    trusted = load(config / ".claude.json").get("projects", {}).get(str(Path.cwd()), {})
    found = []
    if trusted.get("hasTrustDialogAccepted"):
        for key, on in load(settings).get("enabledPlugins", {}).items():
            module = key.split("@")[0]
            where = market / "modules" / module if mutant == "session-in-place" else cache_of(module)
            if on and mutant != "session-loads-nothing":
                found.append({"name": module, "path": str(where), "source": key})
    print(json.dumps({"type": "system", "subtype": "init", "plugins": found}))
    print(json.dumps({"type": "result", "subtype": "success", "result": "Not logged in"}))
    sys.exit(1)
else:
    print("fake claude: unknown command " + " ".join(args), file=sys.stderr)
    sys.exit(3)
'''

TOY_MP = "toy-mp"  # the toy kit's marketplace name, which its marketplace.json gives and the fake follows
TOY_PIN = "2.1.282"  # the toy kit's pin of the Claude Code version, which the fake answers `--version` with
TOY_DIALS = (
    'root_policy: docs/policies/root-policy.md\nroot-policy:\n  territory: ["docs/policies/**"]\n'
    'records:\n  territory: ["docs/records/**"]\n'
    'const-catalogs:\n  catalogs:\n    - prefix: rec\n      width: 4\n      territory: ["docs/records/**"]\n'
)


def toy_guide(**replace: str) -> str:
    """A guide with every name, the commands of the real one in small; `replace` swaps a block's text."""
    blocks = {
        "new-repo": "mkdir -p ~/dev/my-project && cd ~/dev/my-project && git init --quiet && "
        'git commit --quiet --allow-empty -m "Initial commit"',
        "marketplace": "claude plugin marketplace add toy/kit",
        "install": "for m in ~/dev/constitution-kit/modules/const-*; do "
        f'claude plugin install "$(basename "$m")@{TOY_MP}" --scope project; done',
        "kernel": "mkdir -p docs/constitution && cp -r ~/dev/constitution-kit/kernel/. docs/constitution/\n"
        "cp ~/dev/constitution-kit/LICENSE ~/dev/constitution-kit/NOTICE docs/constitution/",
        "dials": TOY_DIALS.rstrip("\n"),
        "scan": "test -f constitution.yaml && test -f docs/policies/root-policy.md && "
        "test -f docs/policies/records.md && test -f docs/records/rec-0001-adopt-constitution-kernel.md",
        "commit": 'git add -A && git commit --quiet -m "Adopt the constitution kernel"',
        "update": f"claude plugin marketplace update {TOY_MP} && "
        "for m in ~/dev/constitution-kit/modules/const-*; "
        f'do claude plugin update "$(basename "$m")@{TOY_MP}" --scope project; done',
        "reinstall": "for m in ~/dev/constitution-kit/modules/const-*; do claude plugin uninstall "
        f'"$(basename "$m")@{TOY_MP}" --scope project && claude plugin install '
        f'"$(basename "$m")@{TOY_MP}" --scope project; done',
        "uninstall": "for m in ~/dev/constitution-kit/modules/const-*; do "
        f'claude plugin uninstall "$(basename "$m")@{TOY_MP}" --scope project; done',
    } | replace
    parts = ["# Toy guide\n", "```bash check=none\nbrew install vale\n```\n"]
    for name, text in blocks.items():
        language = "yaml" if name == "dials" else "bash"
        parts.append(f"Step {name}:\n\n```{language} check={name}\n{text}\n```\n")
    return "\n".join(parts)


def toy_kit(root: Path, market: dict[str, object] | None = None) -> Path:
    """A toy kit under root, committed; `market` is its .claude-plugin/marketplace.json, by default
    a marketplace named `TOY_MP`."""
    kit = root / "kit"
    (kit / ".claude-plugin").mkdir(parents=True)
    (kit / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps({"name": TOY_MP, "plugins": []} if market is None else market), encoding="utf-8"
    )
    (kit / "scripts").mkdir()
    (kit / "scripts" / "claude-code.version").write_text(TOY_PIN + "\n", encoding="utf-8")
    (kit / "kernel").mkdir(parents=True)
    (kit / "kernel" / "CONVENTIONS.md").write_text("# Kernel\n", encoding="utf-8")
    for name in LICENSE_FILES:
        (kit / name).write_text(f"toy {name}\n", encoding="utf-8")
    (kit / "shared" / "gate").mkdir(parents=True)
    (kit / "shared" / "gate" / "code.py").write_text("x = 1\n", encoding="utf-8")
    for module in ("const-alpha", "const-beta"):
        (kit / "modules" / module / "scripts").mkdir(parents=True)
        (kit / "modules" / module / "scripts" / "gate").symlink_to("../../../shared/gate")
        manifest = kit / "modules" / module / ".claude-plugin"
        manifest.mkdir(parents=True)
        (kit / "modules" / module / "MODULE.md").write_text("A module.\n", encoding="utf-8")
        (manifest / "plugin.json").write_text(
            json.dumps({"name": module, "version": "0.0.1"}), encoding="utf-8"
        )
    env = os.environ | {"GIT_CONFIG_GLOBAL": os.devnull}
    for argv in (
        ["git", "init", "--quiet"],
        ["git", "add", "-A"],
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "-m", "toy"],
    ):
        run(argv, kit, env)
    return kit


@contextlib.contextmanager
def listed_in_reverse() -> Iterator[None]:
    """For the cases inside, `Path.iterdir` yields its entries sorted by name and reversed, whatever the
    filesystem lists: a case that holds an order is then red on every filesystem for a check that does not
    sort, never by the chance of a listing that happens to be unsorted. Restored on leaving."""
    real = Path.iterdir

    def reversed_iterdir(self: Path) -> Iterator[Path]:
        return iter(sorted(real(self), key=lambda path: path.name, reverse=True))

    Path.iterdir = reversed_iterdir  # type: ignore[method-assign,assignment]
    try:
        yield
    finally:
        Path.iterdir = real  # type: ignore[method-assign]


def self_test() -> int:
    failed = 0
    total = 0

    def case(name: str, ok: bool, got: str) -> None:
        nonlocal failed, total
        total += 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
        if not ok:
            failed += 1
            print(f"        got: {got}")

    def whats(findings: list[Finding]) -> str:
        return " | ".join(f.what for f in findings) or "no finding"

    marks = [
        (
            "an unmarked `bash` block red",
            toy_guide() + "\n```bash\nls\n```\n",
            "a `bash` block names no check",
        ),
        (
            "an unknown name red",
            toy_guide() + "\n```bash check=deploy\nls\n```\n",
            "check=deploy is no name the check knows",
        ),
        (
            "a name twice red",
            toy_guide() + "\n```bash check=scan\nls\n```\n",
            "check=scan stands a second time, first at line",
        ),
        (
            "a missing name red",
            toy_guide().replace("check=uninstall", "check=none"),
            "no block is named check=uninstall",
        ),
        (
            "dials on a bash fence red",
            toy_guide().replace("```yaml check=dials", "```bash check=dials"),
            "check=dials stands on a `bash` fence",
        ),
        (
            "a mark where the language should be red",
            toy_guide() + "\n```check=scan\nls\n```\n",
            "the fence opens with check=scan where its language should stand",
        ),
        (
            "a bash name on a yaml fence red",
            toy_guide().replace("```bash check=scan", "```yaml check=scan"),
            "check=scan stands on a `yaml` fence",
        ),
    ]
    for name, guide, expected in marks:
        _, findings = blocks_of(guide)
        case(name, len(findings) == 1 and findings[0].what.startswith(expected), whats(findings))
    _, misplaced = blocks_of(toy_guide().replace("```yaml check=dials", "```check=dials"))
    case(
        "a misplaced dials mark red once, its fix a yaml fence",
        len(misplaced) == 1 and misplaced[0].fix.endswith("```yaml check=dials"),
        " | ".join(f"{f.what} / {f.fix}" for f in misplaced),
    )
    _, clean = blocks_of(toy_guide() + "\n```text\nnot a command\n```\n")
    case("a green guide gives no mark finding; a `text` fence needs no mark", not clean, whats(clean))

    def broken_said(kit: Path) -> str:
        try:
            modules_of(kit)
        except Broken as broken:
            return str(broken)
        return "no Broken"

    with tempfile.TemporaryDirectory(prefix="install-guide-listings-") as listings:
        count = 0

        def tree(*folders: str, files: tuple[str, ...] = (), documents: bool = True) -> Path:
            """A tree whose modules/ holds each folder, with a manifest of version 1.0 and, unless
            `documents` is off, its MODULE.md, and each plain file; `modules/` is made even for none."""
            nonlocal count
            count += 1
            root = Path(listings) / f"tree-{count}"
            (root / "modules").mkdir(parents=True)
            for folder in folders:
                (root / "modules" / folder / ".claude-plugin").mkdir(parents=True)
                manifest = root / "modules" / folder / ".claude-plugin" / "plugin.json"
                manifest.write_text(json.dumps({"version": "1.0"}), encoding="utf-8")
                if documents:
                    (root / "modules" / folder / "MODULE.md").write_text("A module.\n", encoding="utf-8")
            for name in files:
                (root / "modules" / name).write_text("not a folder\n", encoding="utf-8")
            return root

        hidden = list(modules_of(tree("const-b", ".x", "_x", "const-a")))
        case(
            "a folder `.x` and a folder `_x` are skipped silently",
            hidden == ["const-a", "const-b"],
            str(hidden),
        )
        mixed = list(modules_of(tree("glossary", "const-a")))
        case("a folder named without const- is a module", mixed == ["const-a", "glossary"], str(mixed))
        plain = list(modules_of(tree("const-a", files=("const-file",))))
        case("a plain file of modules/ is no module, and no BROKEN", plain == ["const-a"], str(plain))
        with listed_in_reverse():  # modules/ is listed reversed, whatever the filesystem lists
            ordered = list(modules_of(tree("const-b", "const-c", "const-a")))
        case(
            "the modules are sorted by name, whatever order the folder lists",
            ordered == ["const-a", "const-b", "const-c"],
            str(ordered),
        )
        said = broken_said(tree("const-ghost", documents=False))
        case(
            "a module folder without its MODULE.md is a teaching BROKEN line",
            said == "modules/const-ghost has no MODULE.md — fix: restore the module document",
            said,
        )
        no_modules = Path(listings) / "no-modules"
        no_modules.mkdir()
        said = broken_said(no_modules)
        case(
            "a tree with no modules/ is a teaching BROKEN line",
            said == f"{no_modules} has no modules/ directory — fix: run the check from a checkout of the kit",
            said,
        )
        empty = tree(files=("const-file",))
        said = broken_said(empty)
        case(
            "a modules/ with no module folder is BROKEN, as the check always said",
            said == f"no module under {empty / 'modules'} — fix: run the check from a clone of the kit",
            said,
        )
        versionless = tree("const-a")
        (versionless / "modules" / "const-a" / ".claude-plugin" / "plugin.json").write_text(
            "{}", encoding="utf-8"
        )
        said = broken_said(versionless)
        case(
            "a manifest with no version is BROKEN, its version read as always",
            said.endswith("gives no version ('version') — fix: restore the module's manifest"),
            said,
        )

        def market_said(text: str | None, as_folder: bool = False) -> tuple[Path, str]:
            """The folder of a kit whose .claude-plugin/marketplace.json holds `text` (no file for None,
            a folder of that name for `as_folder`), and what `marketplace_name` gives over it: the name, or
            its DocumentError's message, or the OSError a read of it let escape."""
            nonlocal count
            count += 1
            folder = Path(listings) / f"market-{count}"
            (folder / ".claude-plugin").mkdir(parents=True)
            if as_folder:
                (folder / ".claude-plugin" / "marketplace.json").mkdir()
            elif text is not None:
                (folder / ".claude-plugin" / "marketplace.json").write_text(text, encoding="utf-8")
            try:
                return folder, marketplace_name(folder)
            except DocumentError as bad:
                return folder, str(bad)
            except OSError as bad:
                return folder, f"escaped {type(bad).__name__}: {bad}"

        folder, got = market_said('{"name": "toy-mp", "plugins": []}')
        case("the marketplace's name is the file's top-level name", got == "toy-mp", got)
        for name, text, tail in (
            (
                "a marketplace.json that is missing",
                None,
                " cannot be read (No such file or directory) — fix: run the check from a checkout of the kit,"
                " which holds the file",
            ),
            (
                "a marketplace.json that is no JSON",
                "not json",
                " is not JSON (Expecting value: line 1 column 1 (char 0)) — fix: restore the file as a JSON"
                " object",
            ),
            (
                "a marketplace.json that is a JSON list",
                "[]",
                ' is not a JSON object — fix: restore the file as an object with the marketplace\'s "name"',
            ),
            (
                "a marketplace.json with no name",
                '{"plugins": []}',
                ' has no "name" — fix: give the marketplace its name, at the top of the object',
            ),
            (
                "a marketplace.json whose name is a number",
                '{"name": 7}',
                ' gives a "name" that is not a string — fix: write the name as a JSON string',
            ),
            (
                "a marketplace.json whose name is empty",
                '{"name": ""}',
                ' gives an empty "name" — fix: write the marketplace\'s name in it',
            ),
        ):
            folder, got = market_said(text)
            case(
                f"{name} is a teaching DocumentError",
                got == f"{folder}/.claude-plugin/marketplace.json{tail}",
                got,
            )
        folder, got = market_said(None, as_folder=True)  # the file "unreadable" of the reader's docstring
        case(
            "a marketplace.json that is a folder, unreadable though it exists, is a teaching DocumentError",
            got == f"{folder}/.claude-plugin/marketplace.json cannot be read (Is a directory) — fix: run the"
            " check from a checkout of the kit, which holds the file",
            got,
        )

        def pin_said(content: bytes | None) -> tuple[Path, str]:
            """The folder of a kit whose scripts/claude-code.version holds `content` (no file for None),
            and what `pinned_claude` gives over it: the version, or its DocumentError's message."""
            nonlocal count
            count += 1
            folder = Path(listings) / f"pin-{count}"
            (folder / "scripts").mkdir(parents=True)
            if content is not None:
                (folder / "scripts" / "claude-code.version").write_bytes(content)
            try:
                return folder, pinned_claude(folder)
            except DocumentError as bad:
                return folder, str(bad)

        for name, one_line in (("without a final line break", b"2.1.282"), ("with one", b"2.1.282\n")):
            folder, got = pin_said(one_line)
            case(f"a pin file holding one version {name} gives the version", got == "2.1.282", got)
        pin_fix = (
            " — fix: write the one version Claude Code's npm package carries, e.g. 2.1.282, as the file's"
            " only line"
        )  # typed by hand
        for name, content, tail in (
            (
                "missing",
                None,
                f" cannot be read (No such file or directory){pin_fix}",
            ),
            ("empty", b"", f" is empty{pin_fix}"),
            ("holding CRLF", b"2.1.282\r\n", f" is not one version ('2.1.282\\r\\n'){pin_fix}"),
            (
                "holding a byte-order mark",
                b"\xef\xbb\xbf2.1.282\n",
                f" is not one version ('\\ufeff2.1.282\\n'){pin_fix}",
            ),
            (
                "holding two lines",
                b"2.1.282\n2.1.286\n",
                f" is not one version ('2.1.282\\n2.1.286\\n'){pin_fix}",
            ),
            ("holding a word", b"latest\n", f" is not one version ('latest\\n'){pin_fix}"),
            (
                "holding a blank line after the version",
                b"2.1.282\n\n",
                f" is not one version ('2.1.282\\n\\n'){pin_fix}",
            ),
            ("holding a line break alone", b"\n", f" is not one version ('\\n'){pin_fix}"),
            ("holding two numbers", b"2.1\n", f" is not one version ('2.1\\n'){pin_fix}"),
            ("holding a fourth number", b"2.1.282.1\n", f" is not one version ('2.1.282.1\\n'){pin_fix}"),
            (
                "holding a v before the version",
                b"v2.1.282\n",
                f" is not one version ('v2.1.282\\n'){pin_fix}",
            ),
            (
                "holding a space after the version",
                b"2.1.282 \n",
                f" is not one version ('2.1.282 \\n'){pin_fix}",
            ),
            (
                "holding a space before the version",
                b" 2.1.282\n",
                f" is not one version (' 2.1.282\\n'){pin_fix}",
            ),
            (
                "holding another script's digits",
                "٢.١.٢٨٢\n".encode(),
                f" is not one version ('٢.١.٢٨٢\\n'){pin_fix}",
            ),
            (
                "holding bytes that are no UTF-8",
                b"2.1.282\xff\n",
                f" is not one version ('2.1.282�\\n'){pin_fix}",
            ),
        ):
            folder, got = pin_said(content)
            case(
                f"a pin file {name} is a teaching DocumentError",
                got == f"{folder}/scripts/claude-code.version{tail}",
                got,
            )

    with tempfile.TemporaryDirectory(prefix="install-guide-self-test-") as scratch:
        root = Path(scratch)
        kit = toy_kit(root)
        fake = root / "bin"
        fake.mkdir()
        (fake / "claude").write_text(FAKE, encoding="utf-8")
        (fake / "claude").chmod(0o755)
        base = os.environ | {
            "PATH": f"{fake}{os.pathsep}{os.environ.get('PATH', '')}",
            FROM_ENV: "toy/kit#main",
            "FAKE_SOURCE": str(kit),
        }
        green, examined, green_note = run_guide(toy_guide(), kit, base)
        case(
            "a green toy run on the pinned version green, with no note",
            not green and green_note == "",
            f"{whats(green)} ({examined}) {green_note!r}",
        )
        nameless = toy_kit(root / "nameless", {"plugins": []})
        try:
            run_guide(toy_guide(), nameless, base | {"FAKE_SOURCE": str(nameless)})
            unnamed = "no Broken"
        except Broken as broken:
            unnamed = str(broken)
        case(
            "a kit whose marketplace.json gives no name is a BROKEN, naming the clone's file",
            unnamed.endswith(
                '/dev/constitution-kit/.claude-plugin/marketplace.json has no "name"'
                " — fix: give the marketplace its name, at the top of the object"
            ),
            unnamed,
        )
        runs: list[tuple[str, dict[str, str], str, str]] = [
            ("a block that exits 1 red", {"scan": "false"}, "", "the block named check=scan exited 1"),
            (
                "a block that makes no repository red",
                {"new-repo": "mkdir -p ~/dev/my-project && cd ~/dev/my-project"},
                "",
                "after check=new-repo: the block ends in no git repository",
            ),
            (
                "a marketplace never added red",
                {"marketplace": "true || claude plugin marketplace add toy/kit"},
                "",
                "after check=marketplace: the configuration knows no marketplace toy-mp",
            ),
            (
                "a marketplace added from a folder red",
                {},
                "marketplace-directory",
                "after check=marketplace: the marketplace is registered from a directory source",
            ),
            (
                "a marketplace from another repository red",
                {},
                "marketplace-other-repo",
                "after check=marketplace: the marketplace is registered from other/kit, not from toy/kit",
            ),
            (
                "a marketplace whose modules differ from the kit's red",
                {},
                "marketplace-fewer-modules",
                "after check=marketplace: the marketplace holds {'const-alpha': '0.0.1'}",
            ),
            (
                "a block that reads another block's variable red",
                {
                    "new-repo": "KIT=~/dev/constitution-kit && mkdir -p ~/dev/my-project && "
                    "cd ~/dev/my-project && git init --quiet && "
                    'git commit --quiet --allow-empty -m "Initial commit"',
                    "kernel": 'echo "$KIT" && mkdir -p docs/constitution && '
                    "cp -r ~/dev/constitution-kit/kernel/. docs/constitution/",
                },
                "",
                "the block named check=kernel exited",
            ),
            (
                "a session that runs a module in place red",
                {},
                "session-in-place",
                "after check=install: a session runs const-alpha from",
            ),
            (
                "an install that enables nothing red",
                {},
                "install-no-enable",
                "after check=install: const-alpha is not enabled",
            ),
            (
                "a kernel copy that copies nothing red",
                {"kernel": "mkdir -p docs/constitution"},
                "",
                "after check=kernel: docs/constitution/CONVENTIONS.md is not the kernel's file",
            ),
            (
                "a kernel copy that leaves the license out red",
                {
                    "kernel": "mkdir -p docs/constitution && "
                    "cp -r ~/dev/constitution-kit/kernel/. docs/constitution/"
                },
                "",
                "after check=kernel: docs/constitution/LICENSE is not the kit's file",
            ),
            (
                "a commit that leaves the tree dirty red",
                {"commit": "touch stray"},
                "",
                "after check=commit: the project's working tree",
            ),
            (
                "an update that drops a module red",
                {},
                "update-drops",
                "after check=update: const-alpha is not in the plugin cache",
            ),
            (
                "a reinstall whose copy differs from the marketplace red",
                {},
                "reinstall-stale",
                "after check=reinstall: const-alpha's stale.txt is not alike in the cache and the "
                "marketplace",
            ),
            (
                "a reinstall copy that lacks a file of the marketplace red",
                {},
                "reinstall-lacks",
                "after check=reinstall: const-alpha's MODULE.md is not alike in the cache and the "
                "marketplace",
            ),
            (
                "an uninstall that keeps the plugin red",
                {},
                "uninstall-keeps",
                "after check=uninstall: const-alpha@toy-mp",
            ),
        ]
        for name, replace, mutant, expected in runs:
            findings, examined, _ = run_guide(toy_guide(**replace), kit, base | {"FAKE_MUTANT": mutant})
            case(
                name,
                len(findings) == 1 and findings[0].what.startswith(expected),
                f"{whats(findings)} ({examined})",
            )
        for name, replace, fix in (
            (
                "a marketplace block that exits 1",
                {"marketplace": "false && claude plugin marketplace add toy/kit"},
                "let git clone the source the block is given — CONSTITUTION_KIT_INSTALL_FROM, "
                "`<owner>/<repo>#<branch>`, else the clone's origin at the branch checked out, naming a "
                "repository and branch that exist — with a credential for github.com while the repository "
                "is private, as `gh auth setup-git` sets one up; and make the block's other commands succeed",
            ),
            (
                "an install block that exits 1",
                {"install": "false"},
                "make the block install each module at project scope, "
                "`claude plugin install <module>@toy-mp --scope project`",  # typed by hand: the toy's name
            ),
        ):
            exited, _, _ = run_guide(toy_guide(**replace), kit, base)
            case(
                f"{name} teaches its block's fix",
                len(exited) == 1 and "exited 1" in exited[0].what and exited[0].fix == fix,
                " | ".join(f"{f.what} / {f.fix}" for f in exited),
            )
        stopped, _, _ = run_guide(toy_guide(), kit, base | {"FAKE_MUTANT": "session-no-start"})
        case(
            "a session that reports no start says why, and teaches to reproduce it",
            len(stopped) == 1
            and stopped[0].what.endswith("reported no start (Error: the session could not start)")
            and stopped[0].fix.startswith("run §2 steps 1 to 3 in a project of your own, then `claude -p ok")
            and stopped[0].render().count("fix:") == 1,
            " | ".join(f"{f.what} / {f.fix}" for f in stopped),
        )
        never, _, _ = run_guide(
            toy_guide(marketplace="true || claude plugin marketplace add toy/kit"), kit, base
        )
        case(
            "a marketplace never added teaches to register the repository",
            len(never) == 1 and never[0].fix.startswith("make the block register the kit's repository"),
            " | ".join(f.fix for f in never),
        )
        for mutant, fix in (
            ("marketplace-other-repo", "make the block register the source it is given"),
            ("marketplace-unreadable", "bring the source branch to the kit's clone"),
            ("marketplace-directory", "register the kit from GitHub"),
            ("session-in-place", "register the kit from GitHub"),
            ("install-no-enable", "make the block install each module at project scope"),
            ("session-loads-nothing", "run §2 steps 1 to 3 in a project of your own and read the Errors tab"),
        ):
            taught, _, _ = run_guide(toy_guide(), kit, base | {"FAKE_MUTANT": mutant})
            case(
                f"{mutant} teaches its own fix, one fix",
                len(taught) == 1 and taught[0].fix.startswith(fix) and taught[0].render().count("fix:") == 1,
                " | ".join(f"{f.what} / {f.fix}" for f in taught),
            )
        mended, _, _ = run_guide(toy_guide(), kit, base | {"FAKE_MUTANT": "marketplace-fewer-modules"})
        case(
            "a marketplace whose modules differ teaches to bring the branch to the clone",
            len(mended) == 1 and mended[0].fix.startswith("bring the source branch to the kit's clone"),
            " | ".join(f.fix for f in mended),
        )
        dials = toy_guide().split("Step dials:")
        moved = dials[0].replace(
            "# Toy guide\n", "# Toy guide\n\nStep dials:" + dials[1].split("Step scan:")[0], 1
        )
        early, _, _ = run_guide(moved + "Step scan:" + dials[1].split("Step scan:")[1], kit, base)
        case(
            "the dials before the project red",
            len(early) == 1 and early[0].what.startswith("the dials example comes before the project exists"),
            whats(early),
        )
        try:
            committed_guide(kit, os.environ | {"GIT_TRACE": "2"})
            absent = "no Broken"
        except Broken as broken:
            absent = str(broken)
        case(
            "a guide not committed at HEAD is a configuration failure",
            "is not committed at HEAD" in absent,
            absent,
        )
        (kit / GUIDE).write_text(toy_guide(), encoding="utf-8")
        try:
            committed_guide(kit, os.environ | {"GIT_TRACE": "2"})
            unread = "no Broken"
        except Broken as broken:
            unread = str(broken)
        case("a guide written but not committed is not read", "is not committed at HEAD" in unread, unread)
        git = os.environ | {"GIT_CONFIG_GLOBAL": os.devnull}
        run(["git", "add", GUIDE], kit, git)
        run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "-m", "guide"], kit, git
        )
        read = committed_guide(kit, os.environ | {"GIT_TRACE": "2"})  # git writes its trace to stderr
        case("the committed guide is read whole, standard output alone", read == toy_guide(), read[:80])
        # the version check, over every answer of `claude --version`; the lines are typed by hand
        version_log = root / "version.log"
        strict = (
            "claude is {0}, and the kit's install checks read the platform as 2.1.282 writes it"
            " (scripts/claude-code.version) — fix: put Claude Code 2.1.282 first on PATH for this run,"
            " installed beside your own (npm install --prefix <folder> @anthropic-ai/claude-code@2.1.282,"
            " then PATH=<folder>/node_modules/.bin:$PATH), or set CONSTITUTION_KIT_ANY_CLAUDE=1 to run on"
            " {0} with a note on every line"
        )
        noted = " [claude {0}, not the pinned 2.1.282: CONSTITUTION_KIT_ANY_CLAUDE=1]"
        reinstall = (
            " — fix: check that `claude` on PATH is Claude Code (`command -v claude`), and reinstall it"
        )
        no_opt_out = {k: v for k, v in base.items() if k != "CONSTITUTION_KIT_ANY_CLAUDE"}

        def stuck(what: str) -> str:
            return f"BROKEN: `claude --version` {what}{reinstall}"

        def says_env(says: str, exits: int, optout: str | None, source: Path = kit) -> dict[str, str]:
            env = no_opt_out | {
                "FAKE_SAYS": says,
                "FAKE_EXIT": str(exits),
                "FAKE_LOG": str(version_log),
                "FAKE_SOURCE": str(source),
            }
            if optout is not None:
                env["CONSTITUTION_KIT_ANY_CLAUDE"] = optout
            return env

        def outcome(env: dict[str, str]) -> str:
            """What the check does before its clone: the note it goes on with, or its BROKEN line."""
            version_log.unlink(missing_ok=True)
            try:
                return f"note:{claude_noted(kit, env)}"
            except Broken as broken:
                return f"BROKEN: {broken}"

        def logged() -> list[str]:
            return version_log.read_text(encoding="utf-8").splitlines() if version_log.exists() else []

        def kind(said_outcome: str) -> str:
            if said_outcome == "note:":
                return "the run goes on"
            return "the run goes on with the note" if said_outcome.startswith("note:") else "BROKEN"

        # what `--version` says, its exit, what the run does with the variable unset, and with it at 1
        # (None: the same)
        rows: list[tuple[str, int, str, str | None]] = [
            ("2.1.282 (Claude Code)\\n", 0, "note:", None),
            ("2.1.282 (Claude Code)\\r\\n", 0, "note:", None),  # CR is white space: the first word is read
            ("2.1.282 (Claude Code)\\nextra\\n", 0, "note:", None),  # the first line alone is read
            (
                "2.1.286 (Claude Code)\\n",
                0,
                "BROKEN: " + strict.format("2.1.286"),
                "note:" + noted.format("2.1.286"),
            ),
            (
                "2.1.2820 (Claude Code)\\n",
                0,
                "BROKEN: " + strict.format("2.1.2820"),
                "note:" + noted.format("2.1.2820"),
            ),
            (
                "2.1.28 (Claude Code)\\n",
                0,
                "BROKEN: " + strict.format("2.1.28"),
                "note:" + noted.format("2.1.28"),
            ),
            ("2.1.286", 0, "BROKEN: " + strict.format("2.1.286"), "note:" + noted.format("2.1.286")),
            ("v2.1.282\\n", 0, stuck("printed no version (v2.1.282)"), None),
            ("", 0, stuck("printed no version (no output)"), None),
            ("", 1, stuck("exited 1 (no output)"), None),
            ("2.1.282 (Claude Code)\\n", 1, stuck("exited 1 (2.1.282 (Claude Code))"), None),
            ("2.1.286 (Claude Code)\\n", 1, stuck("exited 1 (2.1.286 (Claude Code))"), None),
            ("", 139, stuck("exited 139 (no output)"), None),
            (
                "extra\\n2.1.282 (Claude Code)\\n",
                0,
                stuck("printed no version (2.1.282 (Claude Code))"),
                None,
            ),
        ]
        for says, exits, unset_out, one_out in rows:
            at_one = unset_out if one_out is None else one_out
            seen = [outcome(says_env(says, exits, None)), outcome(says_env(says, exits, "1"))]
            ran = logged()  # the second run only: each run leaves the one line its own command logged
            case(
                f'`claude --version` printing "{says}" with exit {exits}: {kind(unset_out)} with the variable'
                f" unset, {kind(at_one)} with it at 1",
                seen == [unset_out, at_one] and ran == ["--version"],
                f"{seen} {ran}",
            )
        too_old = "2.1.286 (Claude Code)\\n"
        for value in ("", "0", "yes", "true", " 1", "1 ", "TRUE", "01"):
            got = outcome(says_env(too_old, 0, value))
            case(
                f"CONSTITUTION_KIT_ANY_CLAUDE={value!r} is not the opt-out: the other version is BROKEN",
                got == "BROKEN: " + strict.format("2.1.286"),
                got,
            )

        def stopped_run(env: dict[str, str], where: Path = kit) -> tuple[str, str]:
            """What `run_guide` over the toy guide ends in when it is Broken: its line and its note."""
            version_log.unlink(missing_ok=True)
            try:
                run_guide(toy_guide(), where, env)
            except Broken as broken:
                return str(broken), broken.note
            return "no Broken", ""

        line, kept = stopped_run(says_env(too_old, 0, None))
        case(
            "a run on another version stops before the clone and any block: only --version is run",
            line == strict.format("2.1.286") and kept == "" and logged() == ["--version"],
            f"{line} {kept!r} {logged()}",
        )
        pinless = toy_kit(root / "pinless")
        (pinless / "scripts" / "claude-code.version").unlink()
        line, kept = stopped_run(says_env(too_old, 0, "1", pinless), pinless)
        case(
            "a kit with no pin file is BROKEN with the reader's line, before claude is run",
            line
            == f"{pinless}/scripts/claude-code.version cannot be read (No such file or directory){pin_fix}"
            and kept == ""
            and logged() == [],
            f"{line} {kept!r} {logged()}",
        )
        line, kept = stopped_run(says_env("", 139, "1"))
        case(
            "a crashed claude stops the run before the clone, with no note, the opt-out notwithstanding",
            line == stuck("exited 139 (no output)").removeprefix("BROKEN: ")
            and kept == ""
            and logged() == ["--version"],
            f"{line} {kept!r} {logged()}",
        )
        version_log.unlink(missing_ok=True)
        off_findings, off_examined, off_note = run_guide(toy_guide(), kit, says_env(too_old, 0, "1"))
        case(
            "with the opt-out a green run on another version goes on, asks the version once, and notes both",
            not off_findings
            and off_note == noted.format("2.1.286")
            and logged()[0] == "--version"
            and logged().count("--version") == 1
            and len(logged()) > 1,
            f"{whats(off_findings)} ({off_examined}) {off_note!r} {logged()[:3]}",
        )
        line, kept = stopped_run(says_env(too_old, 0, "1", nameless), nameless)
        case(
            "a BROKEN after the version is known carries the note",
            line.endswith(
                '/marketplace.json has no "name" — fix: give the marketplace its name, at the top of'
                " the object"
            )
            and kept == noted.format("2.1.286"),
            f"{line} {kept!r}",
        )
        nameless_main = toy_kit(
            root / "nameless-main", {"plugins": []}
        )  # its guide committed, as main reads it
        (nameless_main / GUIDE).write_text(toy_guide(), encoding="utf-8")
        run(["git", "add", GUIDE], nameless_main, git)
        run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "-m", "guide"],
            nameless_main,
            git,
        )

        def whole_run(env: dict[str, str], where: Path = kit) -> tuple[int, list[str]]:
            """The exit and the lines `main` prints over the toy kit, whose guide is committed."""
            version_log.unlink(missing_ok=True)
            printed_lines = io.StringIO()
            with (
                mock.patch.dict(os.environ, env, clear=True),
                mock.patch.dict(globals(), {"KIT": where}),
                contextlib.redirect_stdout(printed_lines),
            ):
                status = main([])
            return status, printed_lines.getvalue().splitlines()

        stop = "BROKEN: the check could not run — 0 blocks run"
        ended, lines = whole_run(says_env(too_old, 0, None))
        case(
            "a whole run on another version prints the two BROKEN lines, and runs no other claude command",
            ended == EXIT_BROKEN
            and lines == ["BROKEN: " + strict.format("2.1.286"), stop]
            and logged() == ["--version"],
            f"{ended} {lines} {logged()}",
        )
        ended, lines = whole_run(says_env(too_old, 0, "1", nameless_main), nameless_main)
        case(
            "a whole run with the opt-out ends each BROKEN line it prints with the note",
            ended == EXIT_BROKEN
            and len(lines) == 2
            and lines[0].endswith(
                '/dev/constitution-kit/.claude-plugin/marketplace.json has no "name"'
                " — fix: give the marketplace its name, at the top of the object" + noted.format("2.1.286")
            )
            and lines[1] == stop + noted.format("2.1.286"),
            f"{ended} {lines}",
        )
        ended, lines = whole_run(says_env("", 139, "1"))
        case(
            "a whole run on a crashed claude prints no note, the opt-out notwithstanding",
            ended == EXIT_BROKEN
            and lines == [stuck("exited 139 (no output)"), stop]
            and logged() == ["--version"],
            f"{ended} {lines} {logged()}",
        )
        try:
            committed_guide(root / "bin", os.environ | {"GIT_CEILING_DIRECTORIES": str(root)})
            bare = "no Broken"
        except Broken as broken:
            bare = str(broken)
        case(
            "a folder that is no clone is a configuration failure",
            "is no git clone with a commit" in bare,
            bare,
        )
        no_clone = root / "no-clone"  # holds the pin, which is asked before the clone, and no git history
        (no_clone / "scripts").mkdir(parents=True)
        (no_clone / "scripts" / "claude-code.version").write_text(TOY_PIN + "\n", encoding="utf-8")
        try:
            run_guide(toy_guide(), no_clone, base | {"GIT_CEILING_DIRECTORIES": str(root)})
            unrun = "no Broken"
        except Broken as broken:
            unrun = str(broken)
        case(
            "a run from a folder that is no clone is a configuration failure",
            "is no git clone (" in unrun,
            unrun,
        )
        traced, examined, _ = run_guide(toy_guide(), kit, base | {"GIT_TRACE": "2"})
        case("a run whose git writes a trace to stderr green", not traced, f"{whats(traced)} ({examined})")
        _, status = run(["git", "status", "--porcelain"], kit, git, joined=False)
        case("the toy kit is left as it was: the run works on a clone", not status, status)
        sourceless, _, _ = run_guide(toy_guide(marketplace="claude plugin marketplace list"), kit, base)
        case(
            "a marketplace block with no source to point red",
            len(sourceless) == 1 and "runs no `claude plugin marketplace add <source>`" in sourceless[0].what,
            whats(sourceless),
        )
        outer = root / "outer.gitconfig"  # gh's helpers, the forms a hand-written file breaks, an alias
        (root / "more.gitconfig").write_text('[credential]\n\tusername = "José"\n', encoding="utf-8")
        outer.write_text(
            '[credential "https://github.com"]\n\thelper =\n\thelper = !gh auth git-credential\n'
            '[credential "https://x y"]\n\thelper = "a \\"quoted\\" \\\\ value"\n'
            '[credential]\n\tuseHttpPath\n\tmultiline = "one\\ntwo"\n'
            f"[include]\n\tpath = {root / 'more.gitconfig'}\n"
            "[alias]\n\tco = checkout\n",
            encoding="utf-8",
        )
        carried = root / "carried.gitconfig"
        carried.write_text("", encoding="utf-8")
        carry_credentials(git | {"GIT_CONFIG_GLOBAL": str(outer)}, carried)
        want = ["config", "--includes", "-z", "--get-regexp", r"^credential\."]
        had = run(["git", *want[:1], "--file", str(outer), *want[1:]], root, git, joined=False)[1]
        got = run(["git", *want[:1], "--file", str(carried), *want[1:]], root, git, joined=False)[1]
        case(
            "the outer credential settings carried as git reads them, includes followed, nothing else",
            got == had.replace("credential.usehttppath\0", "credential.usehttppath\ntrue\0")
            and "alias" not in carried.read_text(encoding="utf-8"),
            f"{had!r} / {got!r}",
        )
        helped = base | {"GIT_CONFIG_GLOBAL": str(outer), "FAKE_NEEDS_HELPER": "1"}
        wired, examined, _ = run_guide(toy_guide(), kit, helped)
        case("the carried helper reaches the run's git", not wired, f"{whats(wired)} ({examined})")
        given = source_of(kit, git | {FROM_ENV: "owner/repo#work/x"})
        case("the source taken from the environment", given == "owner/repo#work/x", given)
        try:
            source_of(kit, {k: v for k, v in git.items() if k != FROM_ENV})
            originless = "no Broken"
        except Broken as broken:
            originless = str(broken)
        case(
            "a kit with no origin on GitHub is a configuration failure",
            originless.startswith("the kit has no origin on GitHub to install from — fix:"),
            originless,
        )
        originals = {k: v for k, v in git.items() if k != FROM_ENV}
        remote = root / "github.com" / "toy" / "kit.git"  # a local origin whose URL reads as GitHub's
        run(["git", "clone", "--quiet", "--bare", str(kit), str(remote)], root, originals)
        run(["git", "remote", "add", "origin", str(remote)], kit, originals)
        branch = run(["git", "symbolic-ref", "--short", "HEAD"], kit, originals, joined=False)[1]
        found = source_of(kit, originals)
        case("the source taken from origin at the branch's HEAD", found == f"toy/kit#{branch}", found)

        def refused(argv: list[str]) -> str:
            run(argv, kit, originals)
            try:
                return f"no Broken: {source_of(kit, originals)}"
            except Broken as broken:
                return str(broken)

        behind = refused(
            [
                "git",
                "-c",
                "user.name=t",
                "-c",
                "user.email=t@t",
                "commit",
                "--quiet",
                "--allow-empty",
                "-m",
                "x",
            ]
        )
        case(
            "an origin behind HEAD is a configuration failure",
            behind.startswith(f"origin's {branch} is not at HEAD, so the install would not come from"),
            behind,
        )
        detached = refused(["git", "checkout", "--quiet", "--detach"])
        case(
            "a detached HEAD is a configuration failure",
            detached.startswith("HEAD is detached, so no branch to install from — fix:"),
            detached,
        )

    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        code = report(
            [Finding(12, "a `bash` block names no check", "write `check=<name>`")],
            "3 named block(s), not run",
        )
    literal = (
        "RED: INSTALL.md:12: a `bash` block names no check\n"
        f"  why: {WHY}\n"
        "  fix: write `check=<name>`\n"
        "RED: 1 finding(s) — 3 named block(s), not run\n"
    )
    case(
        "the report of one finding is its literal text, exit 2",
        code == EXIT_RED and printed.getvalue() == literal,
        printed.getvalue(),
    )
    off_pin = " [claude 2.1.286, not the pinned 2.1.282: CONSTITUTION_KIT_ANY_CLAUDE=1]"  # typed by hand
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        code = report(
            [Finding(12, "a `bash` block names no check", "write `check=<name>`")],
            "3 named block(s), not run",
            off_pin,
        )
    literal = (  # the note ends the headline lines, not the why: and fix: lines
        f"RED: INSTALL.md:12: a `bash` block names no check{off_pin}\n"
        f"  why: {WHY}\n"
        "  fix: write `check=<name>`\n"
        f"RED: 1 finding(s) — 3 named block(s), not run{off_pin}\n"
    )
    case(
        "the report of a run off the pin ends each headline line with the note",
        code == EXIT_RED and printed.getvalue() == literal,
        printed.getvalue(),
    )
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        code = report([], "9 block(s) run, 2 module(s), from toy/kit#main", off_pin)
        plain_code = report([], "9 block(s) run, 2 module(s), from toy/kit#main")
    literal = (  # typed by hand
        "GREEN: the install guide runs and does what it says — 9 block(s) run, 2 module(s), from toy/kit#main"
        " [claude 2.1.286, not the pinned 2.1.282: CONSTITUTION_KIT_ANY_CLAUDE=1]\n"
        "GREEN: the install guide runs and does what it says — 9 block(s) run, 2 module(s),"
        " from toy/kit#main\n"
    )
    case(
        "the green report ends with the note off the pin, and with none on it",
        code == plain_code == EXIT_GREEN and printed.getvalue() == literal,
        printed.getvalue(),
    )
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-install-guide", add_help=False, allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        print("BROKEN: misinvocation — fix: run with no arguments, or with --self-test")
        print("BROKEN: the check could not run — 0 blocks run")
        return EXIT_BROKEN
    try:
        if args.self_test:
            return self_test()
        findings, examined, note = run_guide(committed_guide(KIT, dict(os.environ)), KIT, dict(os.environ))
        return report(findings, examined, note)
    except Broken as broken:
        print(f"BROKEN: {broken}{broken.note}")
        print(f"BROKEN: the check could not run — 0 blocks run{broken.note}")
        return EXIT_BROKEN
    except OSError as bad:
        print(f"BROKEN: {unreadable_said(bad)}")
        print("BROKEN: the check could not run — 0 blocks run")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
