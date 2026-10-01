#!/usr/bin/env python3
"""Kit check: the install guide's commands run, and do what the guide says they do — rule 4 of
plc-0011-install-guide (decision dec-0062-install-guide-governed-kind).

The guide is INSTALL.md at the kit's root, read as committed at the working folder's HEAD, the
commit the run clones. First its marks, read from the text:
  every `bash` fence names `check=<name>` after its language — a name of the set below, each
  standing in the guide exactly once, or `none`, a block the check does not run, as often as
  needed; the dials example is the one `yaml` fence named `check=dials`.
Then the run, in throwaway folders the check removes: a home folder of its own, HOME and
CLAUDE_CONFIG_DIR (<home>/.claude) under it and git's identity in a global configuration of its
own; the kit cloned from the working folder's HEAD to ~/dev/constitution-kit, so what is not
committed is not run; and the named blocks run in the guide's order, each written to a file and
sourced by a fresh `bash -eu` in the folder the block before it ended in, the first in the home
folder, so a block that relies on a variable another block set fails on it, unset. A block's exit is
what `bash -eu` gives the sourcing: a block's last command decides it, and a command that fails
inside an `&&` list earlier in the block, other than the list's last, stops no block, so what such a
block does is held by the claims below, not by its exit.
Beside every block's exit 0, the check holds at each name:
  new-repo     the block ends in a git repository: the project.
  marketplace  the configuration's plugins/known_marketplaces.json knows `constitution-kit`.
  install      every module of the kit stands in the plugin cache at its manifest version and is
               enabled in the project's .claude/settings.json.
  kernel       the project's docs/constitution/ holds every file of the kit's kernel/, byte for byte.
  dials        not run: written as the project's constitution.yaml, and with it what the reader
               writes by hand, from the check's fixture — one policy per namespace of the dials that
               claims a territory, the root at `root_policy`, and decision record #1, named and placed by
               the dials' first catalog.
  scan         the block's exit: every scan it runs exits 0.
  commit       the project's working tree is clean.
  update       before it, the check commits a probe file into the first module of its clone; after
               it, the cache does not hold the probe — the guide says a draft is not updated at an
               unchanged version, and a red here means the platform no longer does as it says.
  reinstall    the cache holds the probe.
  uninstall    no module is enabled in the project's settings or recorded for the project in the
               configuration's plugins/installed_plugins.json.
The first finding of the run ends it, since every later block builds on the one before. A finding
is red; a missing `claude`, `git` or `bash`, or a guide that cannot be read, is a configuration
failure. Needs no Claude account login: the plugin commands read none.

Modes:  no arguments   check the kit's guide;
        --self-test    prove the check with a toy kit, a toy guide and a fake `claude` that logs to
                       a file: each kind of mark finding red once from the text alone; a green toy run
                       green; a mark where a fence's language should be red; a block that exits 1 red; a
                       block that reads another block's variable red, though it would pass under
                       `bash -e`; a guide not committed at HEAD a configuration failure, and the
                       committed one read whole;
                       the dials before the project red; each claim red once against a fake or a block
                       that breaks it — a block that makes no repository, a marketplace never added,
                       an install that enables nothing, a kernel copy that copies nothing, a
                       commit that leaves the tree dirty, an update that takes a draft's change, an
                       install that keeps a stale copy, an uninstall that keeps the plugin enabled; the
                       report of one finding as literal lines with exit 2.
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

import yaml

KIT = Path(__file__).resolve().parent.parent
GUIDE = "INSTALL.md"
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
MARKETPLACE = "constitution-kit"
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
PROBE = ".install-guide-probe"
RECORD_SLUG = "adopt-constitution-kernel"
WHY = "a command nobody runs drifts from the platform unseen (rule 4 of plc-0011-install-guide)"
TIMEOUT = 900


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


@dataclass(frozen=True)
class Finding:
    line: int
    what: str
    fix: str

    def render(self) -> str:
        where = f"{GUIDE}:{self.line}" if self.line else GUIDE
        return f"RED: {where}: {self.what}\n  why: {WHY}\n  fix: {self.fix}"


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
                    f"write the language first, then the mark: ```bash {block.language}",
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
        if name not in seen and not any(f.what.startswith(f"check={name} ") for f in findings):
            findings.append(
                Finding(
                    0, f"no block is named check={name}", f"name the block that {DOES[name]} check={name}"
                )
            )
    return [b for b in found if b.name in NAMES and seen.get(b.name) == b.line], findings


def run(argv: list[str], cwd: Path, env: dict[str, str], timeout: int = TIMEOUT) -> tuple[int, str]:
    """The exit and the combined output of one command."""
    try:
        done = subprocess.run(
            argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False
        )
    except FileNotFoundError as bad:
        raise Broken(
            f"{argv[0]} is not installed ({bad.strerror}) — fix: install it and put it on PATH"
        ) from bad
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout} s"
    return done.returncode, (done.stdout + done.stderr).strip()


def last_line(said: str) -> str:
    return said.splitlines()[-1] if said else "no output"


def modules_of(kit: Path) -> dict[str, str]:
    """Each module of the kit with its manifest version."""
    found: dict[str, str] = {}
    for folder in sorted((kit / "modules").glob("const-*")):
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
    project: Path | None = None

    def cache(self, module: str) -> Path:
        return self.config / "plugins" / "cache" / MARKETPLACE / module / self.modules[module]


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
        known = read_json(state.config / "plugins" / "known_marketplaces.json")
        return "" if MARKETPLACE in known else f"the configuration knows no marketplace {MARKETPLACE}"
    if name in ("install", "reinstall"):
        on = enabled(project)
        for module in state.modules:
            if not state.cache(module).is_dir():
                return f"{module} is not in the plugin cache at {state.modules[module]}"
            if f"{module}@{MARKETPLACE}" not in on:
                return f"{module} is not enabled in the project's .claude/settings.json"
        if name == "reinstall" and not (state.cache(next(iter(state.modules))) / PROBE).is_file():
            return (
                "the cache does not hold the kit's change, "
                "so uninstalling and installing again took no draft's change"
            )
        return ""
    if name == "kernel":
        source = state.kit / "kernel"
        for path in sorted(p for p in source.rglob("*") if p.is_file()):
            copy = project / "docs" / "constitution" / path.relative_to(source)
            if not copy.is_file() or copy.read_bytes() != path.read_bytes():
                return f"docs/constitution/{path.relative_to(source)} is not the kernel's file"
        return ""
    if name == "commit":
        code, said = run(["git", "status", "--porcelain"], project, state.env)
        return "" if code == 0 and not said else "the project's working tree is not clean after the commit"
    if name == "update":
        if (state.cache(next(iter(state.modules))) / PROBE).is_file():
            return (
                "the update took a draft's change at an unchanged version, which the guide says it does not"
            )
        return ""
    if name == "uninstall":
        left = sorted(
            {f"{m}@{MARKETPLACE}" for m in state.modules}
            & (enabled(project) | recorded(state.config, project))
        )
        return f"{', '.join(left)} still installed for the project" if left else ""
    return ""


def fix_for(name: str) -> str:
    if name == "update":
        return (
            "the platform changed: rewrite the update section of the guide to what the platform now does, "
            "and this claim of the check with it"
        )
    return (
        f"make the block named check={name} do what the guide says it does, "
        "or correct the guide and the check"
    )


def probe(state: Run) -> None:
    module = next(iter(state.modules))
    (state.kit / "modules" / module / PROBE).write_text(
        "a change of the install-guide check\n", encoding="utf-8"
    )
    for argv in (
        ["git", "add", "-A"],
        ["git", "commit", "--quiet", "--no-verify", "-m", "install-guide probe"],
    ):
        code, said = run(argv, state.kit, state.env)
        if code != 0:
            raise Broken(
                f"the probe could not be committed in the clone ({last_line(said)}) — fix: check git"
            )


def run_guide(guide: str, kit: Path, base_env: dict[str, str]) -> tuple[list[Finding], str]:
    """The guide's findings, its marks first and then its run, and what was examined."""
    named, findings = blocks_of(guide)
    if findings:
        return findings, f"{len(named)} named block(s), not run"
    for tool in ("git", "bash", "claude"):
        if shutil.which(tool, path=base_env.get("PATH")) is None:
            raise Broken(
                f"{tool} is not on PATH — fix: install it; the check runs the guide's commands with it"
            )
    with tempfile.TemporaryDirectory(prefix="install-guide-") as scratch:
        home = Path(scratch) / "home"
        config = home / ".claude"
        config.mkdir(parents=True)
        (home / ".gitconfig").write_text(
            "[user]\n\tname = install-guide\n\temail = install-guide@example.invalid\n"
            "[init]\n\tdefaultBranch = main\n[commit]\n\tgpgsign = false\n",
            encoding="utf-8",
        )
        env = base_env | {
            "HOME": str(home),
            "CLAUDE_CONFIG_DIR": str(config),
            "GIT_CONFIG_GLOBAL": str(home / ".gitconfig"),
            "DISABLE_AUTOUPDATER": "1",
        }
        clone = home / "dev" / MARKETPLACE
        clone.parent.mkdir(parents=True)
        head = run(["git", "rev-parse", "HEAD"], kit, env)
        if head[0] != 0:
            raise Broken(
                f"{kit} is no git clone ({last_line(head[1])}) — fix: run the check from a clone of the kit"
            )
        for argv, where in (
            (["git", "clone", "--quiet", "--no-checkout", str(kit), str(clone)], home),
            (["git", "checkout", "--quiet", "--detach", head[1]], clone),
        ):
            code, said = run(argv, where, env)
            if code != 0:
                raise Broken(f"the kit could not be cloned ({last_line(said)}) — fix: check the clone")
        state = Run(home, clone, config, env, modules_of(clone), home)
        ran = 0
        for block in named:
            if block.name == "dials":
                if state.project is None:
                    return [
                        Finding(
                            block.line, "the dials example comes before the project exists", fix_for("dials")
                        )
                    ], f"{ran} block(s) run"
                fixture(state.project, block.text)
                continue
            if block.name == "update":
                probe(state)
            script = Path(scratch) / f"{block.name}.sh"
            where = Path(scratch) / f"{block.name}.cwd"
            body = Path(scratch) / f"{block.name}.block.sh"
            body.write_text(block.text, encoding="utf-8")
            script.write_text(f'. "{body}"\npwd > "{where}"\n', encoding="utf-8")
            code, said = run(["bash", "-eu", str(script)], state.cwd, env)
            ran += 1
            if where.is_file():
                state.cwd = Path(where.read_text(encoding="utf-8").strip())
            if code != 0:
                what = f"the block named check={block.name} exited {code} — {last_line(said)}"
                return [Finding(block.line, what, fix_for(block.name))], f"{ran} block(s) run"
            failed = claim(state, block.name)
            if failed:
                return [
                    Finding(block.line, f"after check={block.name}: {failed}", fix_for(block.name))
                ], f"{ran} block(s) run"
        return [], f"{ran} block(s) run, {len(state.modules)} module(s)"


def committed_guide(kit: Path) -> str:
    """The guide as committed at the kit's HEAD, the commit the run clones: standard output alone."""
    env = dict(os.environ)
    if run(["git", "rev-parse", "HEAD"], kit, env)[0] != 0:
        raise Broken(f"{kit} is no git clone with a commit — fix: run the check from a clone of the kit")
    try:
        done = subprocess.run(
            ["git", "show", f"HEAD:{GUIDE}"], cwd=kit, env=env, capture_output=True, text=True, check=False
        )
    except FileNotFoundError as bad:
        raise Broken(f"git is not installed ({bad.strerror}) — fix: install it and put it on PATH") from bad
    if done.returncode != 0:
        raise Broken(
            f"{GUIDE} is not committed at HEAD ({last_line(done.stderr.strip())}) — fix: commit the guide"
        )
    return done.stdout


def report(findings: list[Finding], examined: str) -> int:
    if findings:
        for finding in findings:
            print(finding.render())
        print(f"RED: {len(findings)} finding(s) — {examined}")
        return EXIT_RED
    print(f"GREEN: the install guide runs and does what it says — {examined}")
    return EXIT_GREEN


FAKE = '''#!/usr/bin/env python3
"""A fake claude for the self-test: the plugin commands the guide runs, logged to a file."""
import json, os, shutil, sys
from pathlib import Path
mutant = os.environ.get("FAKE_MUTANT", "")
config = Path(os.environ["CLAUDE_CONFIG_DIR"])
with open(config / "fake.log", "a", encoding="utf-8") as log:
    log.write(" ".join(sys.argv[1:]) + "\\n")
plugins = config / "plugins"
plugins.mkdir(parents=True, exist_ok=True)
known = plugins / "known_marketplaces.json"
installed = plugins / "installed_plugins.json"
settings = Path.cwd() / ".claude" / "settings.json"
def load(path):
    return json.loads(path.read_text()) if path.is_file() else {}
def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
args = sys.argv[1:]
if args[:3] == ["plugin", "marketplace", "add"]:
    source = {"source": "directory", "path": str(Path(args[3]).resolve())}
    save(known, {"constitution-kit": {"source": source}})
elif args[:3] == ["plugin", "marketplace", "update"]:
    pass
elif args[:2] == ["plugin", "install"] or args[:2] == ["plugin", "update"]:
    module = args[2].split("@")[0]
    if args[1] == "update" and mutant != "update-takes":
        print("already at the latest version")
        sys.exit(0)
    kit = Path(load(known)["constitution-kit"]["source"]["path"])
    version = json.loads((kit / "modules" / module / ".claude-plugin" / "plugin.json").read_text())["version"]
    cache = plugins / "cache" / "constitution-kit" / module / version
    if cache.exists() and mutant != "reinstall-stale":
        shutil.rmtree(cache)
    if not cache.exists():
        shutil.copytree(kit / "modules" / module, cache)
    record = load(installed)
    record.setdefault("plugins", {})[args[2]] = [{"scope": "project", "projectPath": str(Path.cwd())}]
    save(installed, record)
    if mutant != "install-no-enable":
        data = load(settings)
        data.setdefault("enabledPlugins", {})[args[2]] = True
        save(settings, data)
elif args[:2] == ["plugin", "uninstall"]:
    if mutant != "uninstall-keeps":
        record = load(installed)
        record.get("plugins", {}).pop(args[2], None)
        save(installed, record)
        data = load(settings)
        data.get("enabledPlugins", {}).pop(args[2], None)
        save(settings, data)
        if mutant != "reinstall-stale":
            module = args[2].split("@")[0]
            shutil.rmtree(plugins / "cache" / "constitution-kit" / module, ignore_errors=True)
else:
    print("fake claude: unknown command " + " ".join(args), file=sys.stderr)
    sys.exit(3)
'''

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
        "marketplace": "claude plugin marketplace add ~/dev/constitution-kit",
        "install": "for m in ~/dev/constitution-kit/modules/const-*; do "
        'claude plugin install "$(basename "$m")@constitution-kit" --scope project; done',
        "kernel": "mkdir -p docs/constitution && cp -r ~/dev/constitution-kit/kernel/. docs/constitution/",
        "dials": TOY_DIALS.rstrip("\n"),
        "scan": "test -f constitution.yaml && test -f docs/policies/root-policy.md && "
        "test -f docs/policies/records.md && test -f docs/records/rec-0001-adopt-constitution-kernel.md",
        "commit": 'git add -A && git commit --quiet -m "Adopt the constitution kernel"',
        "update": "claude plugin marketplace update constitution-kit && "
        "for m in ~/dev/constitution-kit/modules/const-*; "
        'do claude plugin update "$(basename "$m")@constitution-kit" --scope project; done',
        "reinstall": "for m in ~/dev/constitution-kit/modules/const-*; do claude plugin uninstall "
        '"$(basename "$m")@constitution-kit" --scope project && claude plugin install '
        '"$(basename "$m")@constitution-kit" --scope project; done',
        "uninstall": "for m in ~/dev/constitution-kit/modules/const-*; do "
        'claude plugin uninstall "$(basename "$m")@constitution-kit" --scope project; done',
    } | replace
    parts = ["# Toy guide\n", "```bash check=none\nbrew install vale\n```\n"]
    for name, text in blocks.items():
        language = "yaml" if name == "dials" else "bash"
        parts.append(f"Step {name}:\n\n```{language} check={name}\n{text}\n```\n")
    return "\n".join(parts)


def toy_kit(root: Path) -> Path:
    kit = root / "kit"
    (kit / "kernel").mkdir(parents=True)
    (kit / "kernel" / "CONVENTIONS.md").write_text("# Kernel\n", encoding="utf-8")
    for module in ("const-alpha", "const-beta"):
        manifest = kit / "modules" / module / ".claude-plugin"
        manifest.mkdir(parents=True)
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
    _, clean = blocks_of(toy_guide() + "\n```text\nnot a command\n```\n")
    case("a green guide gives no mark finding; a `text` fence needs no mark", not clean, whats(clean))

    with tempfile.TemporaryDirectory(prefix="install-guide-self-test-") as scratch:
        root = Path(scratch)
        kit = toy_kit(root)
        fake = root / "bin"
        fake.mkdir()
        (fake / "claude").write_text(FAKE, encoding="utf-8")
        (fake / "claude").chmod(0o755)
        base = os.environ | {"PATH": f"{fake}{os.pathsep}{os.environ.get('PATH', '')}"}
        green, examined = run_guide(toy_guide(), kit, base)
        case("a green toy run green", not green, f"{whats(green)} ({examined})")
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
                {"marketplace": "true"},
                "",
                "after check=marketplace: the configuration knows no marketplace",
            ),
            (
                "a block that reads another block's variable red",
                {
                    "marketplace": 'KIT=~/dev/constitution-kit && claude plugin marketplace add "$KIT"',
                    "kernel": 'echo "$KIT" && mkdir -p docs/constitution && '
                    "cp -r ~/dev/constitution-kit/kernel/. docs/constitution/",
                },
                "",
                "the block named check=kernel exited",
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
                "a commit that leaves the tree dirty red",
                {"commit": "touch stray"},
                "",
                "after check=commit: the project's working tree",
            ),
            (
                "an update that takes a draft's change red",
                {},
                "update-takes",
                "after check=update: the update took a draft's change",
            ),
            (
                "an install that keeps a stale copy red",
                {},
                "reinstall-stale",
                "after check=reinstall: the cache does not hold",
            ),
            (
                "an uninstall that keeps the plugin red",
                {},
                "uninstall-keeps",
                "after check=uninstall: const-alpha@constitution-kit",
            ),
        ]
        for name, replace, mutant, expected in runs:
            findings, examined = run_guide(toy_guide(**replace), kit, base | {"FAKE_MUTANT": mutant})
            case(
                name,
                len(findings) == 1 and findings[0].what.startswith(expected),
                f"{whats(findings)} ({examined})",
            )
        dials = toy_guide().split("Step dials:")
        moved = dials[0].replace(
            "# Toy guide\n", "# Toy guide\n\nStep dials:" + dials[1].split("Step scan:")[0], 1
        )
        early, _ = run_guide(moved + "Step scan:" + dials[1].split("Step scan:")[1], kit, base)
        case(
            "the dials before the project red",
            len(early) == 1 and early[0].what.startswith("the dials example comes before the project exists"),
            whats(early),
        )
        try:
            committed_guide(kit)
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
            committed_guide(kit)
            unread = "no Broken"
        except Broken as broken:
            unread = str(broken)
        case("a guide written but not committed is not read", "is not committed at HEAD" in unread, unread)
        git = os.environ | {"GIT_CONFIG_GLOBAL": os.devnull}
        run(["git", "add", GUIDE], kit, git)
        run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "-m", "guide"], kit, git
        )
        read = committed_guide(kit)
        case("the committed guide is read whole, standard output alone", read == toy_guide(), read[:80])
        logged = (root / "kit").exists()
        case(
            "the toy kit is left as it was: the run works on a clone",
            logged and not (kit / "modules" / "const-alpha" / PROBE).exists(),
            "the probe reached the source",
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
        findings, examined = run_guide(committed_guide(KIT), KIT, dict(os.environ))
        return report(findings, examined)
    except Broken as broken:
        print(f"BROKEN: {broken}")
        print("BROKEN: the check could not run — 0 blocks run")
        return EXIT_BROKEN
    except OSError as bad:
        print(
            f"BROKEN: a file could not be read or written ({bad}) — "
            "fix: check the kit's clone and the temporary folder"
        )
        print("BROKEN: the check could not run — 0 blocks run")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
