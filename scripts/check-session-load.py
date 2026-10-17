#!/usr/bin/env python3
"""Kit check: a module, installed through Claude Code into a bare repository, loads in a session — its
skills listed and its start hooks run (decision dec-0093-module-evals-with-local-receipts, R10).

For the module named, in throwaway folders the check removes:
  1. the bare repository and the install of `kit_install`, the steps `scripts/check-bare-install.py` takes
     too, from --from, else the environment's CONSTITUTION_KIT_INSTALL_FROM, else the kit's working folder;
  2. one headless session in the bare repository, in the install's configuration folder,
     `claude -p <prompt> --output-format stream-json --verbose --include-hook-events`, with no login: the
     environment drops the variables that would give one (ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN,
     CLAUDE_CODE_OAUTH_TOKEN and those that select a cloud provider), so the model is never called. The
     session reports its start and its start hooks, then stops for want of a login; its exit is not read.
What it reads of the stream, one JSON object per line, as Claude Code 2.1.282 writes it: the first event of
`type` "system" and `subtype` "init", its `plugins` (each with a `name`) and its `skills` (each
`<plugin>:<skill>`); and every event of `subtype` "hook_response" whose `hook_event` is "SessionStart", its
`exit_code`, `outcome` and `output`.
It holds, each failure one finding:
  the `init` event lists the module among its plugins;
  its skills hold `<module>:<name>` for each folder of the module's `skills/` that holds a SKILL.md;
  as many SessionStart hooks answered as the module declares in hooks/hooks.json for a start, `command`
  hooks of a group whose matcher is absent, empty, `*` or names `startup` among its `|` alternatives — the
  stream does not name a hook's plugin, and in the empty configuration the module's are the only ones;
  each answered with exit 0, the outcome "success" and output that is not empty.
What the module declares is read from the kit's working folder, the change CI checks out.
A stream with no `init` event, a session that outlasts its 120 s, and a failure of the install are each a
BROKEN line with the fix; a refusal of the install is a finding.

Modes:  --module <name> [--from <source>]   check one module;
        --self-test    prove the reading of a stream on a toy module: a full stream green; a missing plugin,
                       a missing skill, one hook too few, one too many, a hook that exits 1, one whose outcome
                       is no success with exit 0, and one that prints nothing each a finding; the report of
                       one finding as literal lines with exit 2; a stream with no init event a BROKEN line;
                       and the whole run, install and session, against a fake `claude` on PATH, green.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
import tempfile
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from unittest import mock

import kit_install
from kit_install import FROM_ENV, Broken, Refused, bare_repository, install, kit_marketplace, run, there
from kit_module_doc import DocumentError, Note, claude_env, claude_note

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
SESSION_TIMEOUT = 120  # seconds the session is given, kit tuning and no platform fact
PROMPT = "Reply with the single word ok."
NO_LOGIN = (  # the variables that would let the session call a model
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_OAUTH_TOKEN",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
)
WHY = "a module's skills and start rules work only if a session of the installed copy loads them"


@dataclass(frozen=True)
class Finding:
    module: str
    what: str
    fix: str

    def render(self, note: str = "") -> str:
        return f"RED: {self.module}: {self.what}{note}\n  why: {WHY}\n  fix: {self.fix}"


@dataclass(frozen=True)
class Answer:
    exit_code: object
    outcome: object
    output: str


@dataclass(frozen=True)
class Start:
    plugins: tuple[str, ...]
    skills: tuple[str, ...]
    answers: tuple[Answer, ...]


def expected_skills(source: Path, module: str) -> list[str]:
    folder = source / "skills"
    names = sorted(d.name for d in folder.iterdir() if (d / "SKILL.md").is_file()) if folder.is_dir() else []
    return [f"{module}:{name}" for name in names]


def expected_hooks(source: Path) -> int:
    """The `command` hooks the module declares for a session's start."""
    path = source / "hooks" / "hooks.json"
    if not path.is_file():
        return 0
    try:
        table = json.loads(path.read_text(encoding="utf-8"))["hooks"]
        groups = table.get("SessionStart", [])
        count = 0
        for group in groups:
            matcher = str(group.get("matcher", ""))
            if matcher in ("", "*") or "startup" in matcher.split("|"):
                count += sum(1 for hook in group["hooks"] if hook.get("type") == "command")
    except (ValueError, KeyError, TypeError, AttributeError) as bad:
        raise Broken(
            f"{path} cannot be read as a hooks file ({bad!r}) — fix: restore the module's hooks file; the"
            " bare-install check names the fault"
        ) from bad
    return count


def start_of(stream: str) -> Start:
    """The session's start, read from its stream: the `init` event and the SessionStart answers."""
    init: dict[str, object] | None = None
    answers: list[Answer] = []
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict) or event.get("type") != "system":
            continue
        if event.get("subtype") == "init" and init is None:
            init = event
        elif event.get("subtype") == "hook_response" and event.get("hook_event") == "SessionStart":
            output = event.get("output")
            answers.append(
                Answer(
                    event.get("exit_code"), event.get("outcome"), output if isinstance(output, str) else ""
                )
            )
    if init is None:
        said = [line for line in stream.splitlines() if line.strip()]
        raise Broken(
            f"the session reported no start event ({said[-1][:200] if said else 'no output'}) — fix: run"
            " `claude -p ok --output-format stream-json --verbose` in a repository of your own with the"
            " module installed, and read why it stops before its start"
        )
    plugins = init.get("plugins")
    names = (
        tuple(p["name"] for p in plugins if isinstance(p, dict) and isinstance(p.get("name"), str))
        if isinstance(plugins, list)
        else ()
    )
    skills = init.get("skills")
    listed = tuple(s for s in skills if isinstance(s, str)) if isinstance(skills, list) else ()
    return Start(names, listed, tuple(answers))


def judge(module: str, source: Path, start: Start) -> list[Finding]:
    found: list[Finding] = []
    if module not in start.plugins:
        found.append(
            Finding(
                module,
                "the session does not load the installed module"
                f" (plugins: {', '.join(start.plugins) or 'none'})",
                "check the module's .claude-plugin/plugin.json and its entry in the marketplace",
            )
        )
        return found
    for skill in expected_skills(source, module):
        if skill not in start.skills:
            found.append(
                Finding(
                    module,
                    f"the session lists no skill {skill}",
                    f"check the frontmatter of skills/{skill.split(':', 1)[1]}/SKILL.md: a `name` and a"
                    " `description`, valid YAML",
                )
            )
    wanted = expected_hooks(source)
    if len(start.answers) != wanted:
        found.append(
            Finding(
                module,
                f"{len(start.answers)} start hook(s) answered, but hooks/hooks.json declares {wanted}",
                "check the SessionStart groups of hooks/hooks.json: their matchers and their commands",
            )
        )
    for n, answer in enumerate(start.answers, 1):
        if answer.exit_code != 0 or answer.outcome != "success":
            found.append(
                Finding(
                    module,
                    f"start hook {n} answered with exit {answer.exit_code} ({answer.outcome})",
                    "run the hook's command on a bare repository and read why it fails",
                )
            )
        elif not answer.output.strip():
            found.append(
                Finding(
                    module,
                    f"start hook {n} printed nothing",
                    "make the hook print its rule or its pointer line at a session's start",
                )
            )
    return found


def session(repo: Path, config: Path) -> str:
    env = {k: v for k, v in claude_env(os.environ).items() if k not in NO_LOGIN}
    env |= {"CLAUDE_CONFIG_DIR": str(config), "DISABLE_AUTOUPDATER": "1"}
    argv = ["claude", "-p", PROMPT, "--output-format", "stream-json", "--verbose", "--include-hook-events"]
    code, out, err = run(argv, repo, env, timeout=SESSION_TIMEOUT)
    if code == 124:
        raise Broken(f"the session ran past {SESSION_TIMEOUT} s — fix: run the check again")
    return out


def check_module(module: str, source: str, note: Note) -> tuple[list[Finding], str]:
    kit_source = KIT / "modules" / module
    if not (kit_source / ".claude-plugin" / "plugin.json").is_file():
        raise Broken(f"no module {module} in the kit — fix: name a folder under modules/ that holds a plugin")
    marketplace = kit_marketplace(KIT)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        repo = bare_repository(root)
        try:
            install(module, root, repo, source, marketplace, note)
        except Refused as refused:
            return [
                Finding(module, f"Claude Code refuses to install it ({refused})", "fix its manifest")
            ], "no install"
        start = start_of(session(repo, root / "config"))
    examined = (
        f"{len(expected_skills(kit_source, module))} skill(s), {expected_hooks(kit_source)} start hook(s)"
    )
    return judge(module, kit_source, start), examined


def report(module: str, findings: list[Finding], examined: str, note: str = "") -> int:
    if findings:
        for finding in findings:
            print(finding.render(note))
        print(f"RED: {len(findings)} finding(s) — {examined}{note}")
        return EXIT_RED
    print(f"GREEN: {module} loads in a session, its skills listed and its start hooks run — {examined}{note}")
    return EXIT_GREEN


def toy_module(root: Path) -> Path:
    module = root / "modules" / "const-x"
    (module / "skills" / "s").mkdir(parents=True)
    (module / "skills" / "s" / "SKILL.md").write_text("---\nname: s\ndescription: d\n---\n", encoding="utf-8")
    (module / "skills" / "notes").mkdir()
    (module / "hooks").mkdir()
    hook = {"type": "command", "command": "sh", "args": ["x.sh"]}
    table = {
        "SessionStart": [{"hooks": [hook]}, {"matcher": "resume", "hooks": [hook]}],
        "Stop": [{"hooks": [hook]}],
    }
    (module / "hooks" / "hooks.json").write_text(json.dumps({"hooks": table}), encoding="utf-8")
    (module / ".claude-plugin").mkdir()
    (module / ".claude-plugin" / "plugin.json").write_text('{"name": "const-x"}', encoding="utf-8")
    return module


def stream(plugins: list[str], skills: list[str], answers: list[dict[str, object]]) -> str:
    events: list[dict[str, object]] = [
        {"type": "system", "subtype": "hook_started", "hook_event": "SessionStart"}
    ]
    events += [
        {"type": "system", "subtype": "hook_response", "hook_event": "SessionStart"} | a for a in answers
    ]
    events.append(
        {"type": "system", "subtype": "init", "plugins": [{"name": p} for p in plugins], "skills": skills}
    )
    events.append({"type": "result", "is_error": True, "result": "Not logged in"})
    return "\n".join(json.dumps(e) for e in events) + "\n"


GOOD = {"exit_code": 0, "outcome": "success", "output": "const-x (advisory): load the skill const-x:s.\n"}


def fake_claude(folder: Path, plugin: Path, said: str) -> Path:
    """A `claude` that answers the install's three commands and prints `said` as the session's stream."""
    script = folder / "claude"
    entry = json.dumps([{"id": "const-x@toy", "scope": "user", "installPath": str(plugin)}])
    script.write_text(
        "#!/bin/sh\n"
        'case "$1 $2" in\n'
        '  "plugin marketplace") exit 0 ;;\n'
        '  "plugin install") echo \'{"outcome": "ok", "scope": "user"}\' ;;\n'
        f"  \"plugin list\") echo '{entry}' ;;\n"
        f"  *) cat {folder / 'stream.jsonl'} ; exit 1 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    (folder / "stream.jsonl").write_text(said, encoding="utf-8")
    return folder


@contextlib.contextmanager
def toy_kit(root: Path) -> Iterator[Path]:
    """The kit's names read from a toy kit at `root`: its module, its kernel and its marketplace."""
    (root / "kernel").mkdir()
    (root / "kernel" / "CONVENTIONS.md").write_text("# kernel\n", encoding="utf-8")
    (root / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "marketplace.json").write_text(
        '{"name": "toy", "plugins": []}', encoding="utf-8"
    )
    with mock.patch.dict(globals(), {"KIT": root}), mock.patch.dict(vars(kit_install), {"KIT": root}):
        yield root


def self_test() -> int:
    cases: dict[str, tuple[str, list[str]]] = {
        "a full stream is green": (stream(["const-x"], ["const-x:s"], [GOOD]), []),
        "a module the session does not load is a finding": (
            stream(["other"], ["const-x:s"], [GOOD]),
            ["const-x"],
        ),
        "a missing skill is a finding": (stream(["const-x"], [], [GOOD]), ["const-x"]),
        "one start hook too few is a finding": (stream(["const-x"], ["const-x:s"], []), ["const-x"]),
        "one start hook too many is a finding": (
            stream(["const-x"], ["const-x:s"], [GOOD, GOOD]),
            ["const-x"],
        ),
        "a start hook whose outcome is no success, with exit 0, is a finding": (
            stream(["const-x"], ["const-x:s"], [GOOD | {"outcome": "cancelled"}]),
            ["const-x"],
        ),
        "a start hook that exits 1 is a finding": (
            stream(["const-x"], ["const-x:s"], [GOOD | {"exit_code": 1, "outcome": "error"}]),
            ["const-x"],
        ),
        "a start hook that prints nothing is a finding": (
            stream(["const-x"], ["const-x:s"], [GOOD | {"output": " \n"}]),
            ["const-x"],
        ),
    }
    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        module = toy_module(Path(tmp))
        for name, (said, wanted) in cases.items():
            got = [f.module for f in judge("const-x", module, start_of(said))]
            ok = got == wanted
            failed += 0 if ok else 1
            print(f"[{'ok' if ok else 'FAIL'}] {name}")
            if not ok:
                print(f"        got {got}")
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report(
                "const-x", judge("const-x", module, start_of(stream(["const-x"], [], [GOOD]))), "1 skill(s)"
            )
        report_lines = [  # typed by hand: a message function cannot check itself
            "RED: const-x: the session lists no skill const-x:s",
            f"  why: {WHY}",
            "  fix: check the frontmatter of skills/s/SKILL.md: a `name` and a `description`, valid YAML",
            "RED: 1 finding(s) — 1 skill(s)",
        ]
        ok = code == EXIT_RED and printed.getvalue().splitlines() == report_lines
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] the report of one finding is its literal text, exit 2")
        if not ok:
            print(printed.getvalue())
        try:
            start_of('{"type": "result", "result": "Not logged in"}\n')
            ok = False
        except Broken as broken:
            ok = "reported no start event (" in str(broken) and "fix:" in str(broken)
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] a stream with no init event is a teaching BROKEN line")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        module = toy_module(root)
        bin_folder = root / "bin"
        bin_folder.mkdir()
        fake_claude(bin_folder, module, stream(["const-x"], ["const-x:s"], [GOOD]))
        path = {"PATH": f"{bin_folder}{os.pathsep}{os.environ.get('PATH', '')}"}
        with toy_kit(root), mock.patch.dict(os.environ, path):
            findings, examined = check_module("const-x", str(root), Note("2.1.282"))
        ok = findings == [] and examined == "1 skill(s), 1 start hook(s)"
        failed += 0 if ok else 1
        print(
            f"[{'ok' if ok else 'FAIL'}] the whole run against a fake claude, install and session, is green"
        )
        if not ok:
            print(f"        got {findings} {examined}")
    total = len(cases) + 3
    print(f"{total - failed}/{total} cases green")
    return EXIT_GREEN if failed == 0 else EXIT_RED


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check-session-load", add_help=False, allow_abbrev=False)
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
    note = ""
    try:
        if args.self_test:
            return self_test()
        module = str(args.module)
        source = args.source or os.environ.get(FROM_ENV) or str(KIT)
        if there(Path(source)):
            source = str(Path(source).resolve())
        try:
            claude = claude_note(KIT, dict(os.environ))
        except DocumentError as bad:
            raise Broken(str(bad)) from bad
        note = claude
        findings, examined = check_module(module, source, claude)
        return report(module, findings, f"{examined}, from {source}", note)
    except Broken as broken:
        print(f"BROKEN: {broken}{note}")
        print(f"BROKEN: the check could not run — 0 modules examined{note}")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
