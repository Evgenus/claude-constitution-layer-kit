"""The counter: the pinned ccusage, where it stands, how it is installed, how it is run and how its output
is read.

It stands in the `node_modules` of the plugin's data folder, `${CLAUDE_PLUGIN_DATA}`, and nowhere else: the
plugin's `package.json` and `package-lock.json` stand in its folder `ccusage/`, not at the plugin root, so
that the platform's install of a copied plugin installs nothing. The count copies both files into the data
folder and runs `npm ci --ignore-scripts` there when the data folder's copy of the lockfile differs from the
plugin's or the pinned version is not what stands there. The data folder is one per plugin, shared by
every project, so the install runs under a lock of that folder. A run with no `CLAUDE_PLUGIN_DATA`, such as
a person's shell, uses the data folder that a hook recorded in the clone, when that folder still stands, and
has nowhere to install when none does.
It is run through the launcher in its `.bin` folder and never through a platform binary by its path, as
`ccusage claude session --id <session> --json --offline --config <plugin root>/ccusage.json` with
`CLAUDE_CONFIG_DIR` naming the throwaway folder of one window; a second run without `--id` names the models
its table lacks. The module's own code reads no token count of a transcript and uses no per-reply cost of
the output: the figures are those of the output. It passes its own environment on to ccusage; the variables
the installed `20.0.48` reads, other than the one set here, did not change its output on the known count."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Mapping
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path

from constitution_layer_kit.errors import ConfigurationFailure
from constitution_layer_kit.output import Output
from constitution_layer_kit.repository import first_line

from . import logs, messages
from .model import (
    CCUSAGE_SECONDS,
    INSTALL_LOCK,
    INSTALL_LOCK_SECONDS,
    NPM_SECONDS,
    PIN,
    Counted,
    Entry,
    Report,
)

LOCKFILE = "package-lock.json"
MANIFEST = "package.json"
SOURCE = "ccusage"  # the folder of the plugin that holds the manifest and the lockfile, never the plugin root
NPM_ARGUMENTS = ["npm", "ci", "--ignore-scripts"]


class NotAReport(Exception):
    """ccusage's output is not what a session report is; `detail` says in what way."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


@dataclass(frozen=True, slots=True)
class Ccusage:
    """The installed counter: its launcher, its version, and the plugin root whose `ccusage.json` it reads."""

    launcher: Path
    version: str
    plugin_root: Path


def launcher_of(base: Path) -> Path:
    return base / "node_modules" / ".bin" / "ccusage"


def installed_version(base: Path) -> str | None:
    """The version of the ccusage package under `base`, or None when none stands there."""
    try:
        parsed: object = json.loads(
            (base / "node_modules" / "ccusage" / MANIFEST).read_text(encoding="utf-8")
        )
    except (OSError, ValueError):
        return None
    version = parsed.get("version") if isinstance(parsed, dict) else None
    return version if isinstance(version, str) else None


def _same_lock(root: Path, data: Path) -> bool:
    try:
        return (root / SOURCE / LOCKFILE).read_bytes() == (data / LOCKFILE).read_bytes()
    except OSError:
        return False


def install(root: Path, data: Path) -> None:
    """Copies the plugin's manifest and lockfile into the data folder and runs `npm ci --ignore-scripts`
    there; the lockfile copy stays only when the install succeeded, so that a failed one is tried again."""
    if shutil.which("npm") is None:
        raise ConfigurationFailure(messages.j6_2_no_npm(str(data)))
    data.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / SOURCE / MANIFEST, data / MANIFEST)
    shutil.copyfile(root / SOURCE / LOCKFILE, data / LOCKFILE)
    try:
        done = subprocess.run(NPM_ARGUMENTS, cwd=data, capture_output=True, check=False, timeout=NPM_SECONDS)
    except subprocess.TimeoutExpired as exc:
        (data / LOCKFILE).unlink(missing_ok=True)
        raise ConfigurationFailure(messages.j6_5_npm_failed(str(data), messages.detail_npm_silent())) from exc
    except OSError as exc:
        (data / LOCKFILE).unlink(missing_ok=True)
        raise ConfigurationFailure(
            messages.j6_5_npm_failed(str(data), messages.detail_npm_line(str(exc)))
        ) from exc
    if done.returncode != 0:
        (data / LOCKFILE).unlink(missing_ok=True)
        said = first_line(done.stderr) if done.stderr.strip() else first_line(done.stdout)
        raise ConfigurationFailure(messages.j6_5_npm_failed(str(data), messages.detail_npm_line(said)))


def _wanted(root: Path, data: Path) -> bool:
    """Whether the data folder needs an install: its lockfile copy differs from the plugin's, or the pinned
    ccusage is not what stands there, whatever stands."""
    return not _same_lock(root, data) or installed_version(data) != PIN


def locate(root: Path, data: Path | None, output: Output, stack: ExitStack) -> Ccusage | None:
    """The pinned ccusage in the data folder, under the lock of that folder, which `stack` holds until the
    pass has made its last ccusage run: the data folder is one per plugin, shared by every project, and
    another pass must run neither a half-installed launcher nor another version's. Under the lock it checks
    what stands, installs when wanted, and checks that the pinned version stands, J6.4 or J6.5 where it does
    not, before J5.3 says an install was made. None, with the note J5.4, where another pass kept the lock
    past the wait: nothing is run, npm included, and a later pass counts the windows. `root` is the plugin
    root, which holds the manifest and the lockfile in its `ccusage/` folder and the file `ccusage.json`;
    `data` is None where no folder is known; a configuration failure, J6.1 to J6.5, where none can be had.
    The caller holds the lock of the file of counts first: the lock order is that one, then this one."""
    if shutil.which("node") is None:
        raise ConfigurationFailure(messages.j6_1_no_node())
    if data is None:
        raise ConfigurationFailure(messages.j6_3_no_data_folder())
    if not stack.enter_context(logs.locked(data, INSTALL_LOCK_SECONDS, INSTALL_LOCK)):
        output.out(messages.j5_4_install_lock_held(str(data)))
        return None
    installed = False
    if _wanted(root, data):
        install(root, data)
        installed = True
    there = installed_version(data)
    if there is None:
        raise ConfigurationFailure(messages.j6_5_nothing_installed(str(data)))
    if there != PIN:
        raise ConfigurationFailure(messages.j6_4_other_version(there, str(data)))
    if installed:
        output.out(messages.j5_3_installed(str(data)))
    return Ccusage(launcher_of(data), PIN, root)


def _whole(entry: Mapping[str, object], name: str) -> int:
    value = entry.get(name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise NotAReport(f"an entry lacks the whole number {name}")
    return value


def _entry(parsed: object) -> Entry:
    if not isinstance(parsed, dict):
        raise NotAReport("an entry is no object")
    model = parsed.get("model")
    if not isinstance(model, str):
        raise NotAReport("an entry lacks its model")
    return Entry(
        model,
        _whole(parsed, "inputTokens"),
        _whole(parsed, "outputTokens"),
        _whole(parsed, "cacheCreationTokens"),
        _whole(parsed, "cacheReadTokens"),
    )


def parse_report(text: str) -> Report:
    """The session report in `text`; the `null` ccusage prints for a session with no entry is an empty one."""
    try:
        parsed: object = json.loads(text)
    except ValueError as exc:
        raise NotAReport("it is not JSON") from exc
    if parsed is None:
        return Report((), 0, 0.0)
    if not isinstance(parsed, dict):
        raise NotAReport("it is no object")
    entries = parsed.get("entries")
    tokens = parsed.get("totalTokens")
    cost = parsed.get("totalCost")
    if not isinstance(entries, list):
        raise NotAReport("it has no entries list")
    if isinstance(tokens, bool) or not isinstance(tokens, int):
        raise NotAReport("it has no totalTokens")
    if isinstance(cost, bool) or not isinstance(cost, int | float):
        raise NotAReport("it has no totalCost")
    return Report(tuple(_entry(entry) for entry in entries), tokens, float(cost))


def parse_unpriced(text: str) -> tuple[str, ...]:
    """The models that the report without `--id` marks `missingPricing`, sorted and once each."""
    try:
        parsed: object = json.loads(text)
    except ValueError as exc:
        raise NotAReport("it is not JSON") from exc
    if parsed is None:
        return ()
    sessions = parsed.get("sessions") if isinstance(parsed, dict) else None
    if not isinstance(sessions, list):
        raise NotAReport("it has no sessions list")
    names: set[str] = set()
    for session in sessions:
        breakdowns = session.get("modelBreakdowns") if isinstance(session, dict) else None
        for breakdown in breakdowns if isinstance(breakdowns, list) else []:
            if isinstance(breakdown, dict) and breakdown.get("missingPricing") is True:
                name = breakdown.get("modelName")
                if isinstance(name, str):
                    names.add(name)
    return tuple(sorted(names))


def _run(counter: Ccusage, folder: Path, arguments: list[str], session: str) -> str:
    environment = {**os.environ, "CLAUDE_CONFIG_DIR": str(folder)}
    command = [
        str(counter.launcher),
        "claude",
        "session",
        *arguments,
        "--json",
        "--offline",
        "--config",
        str(counter.plugin_root / "ccusage.json"),
    ]
    try:
        done = subprocess.run(
            command,
            cwd=folder,
            env=environment,
            capture_output=True,
            check=False,
            timeout=CCUSAGE_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise ConfigurationFailure(
            messages.j6_6_no_count(session, messages.detail_ccusage_silent(), str(counter.launcher))
        ) from exc
    except OSError as exc:
        raise ConfigurationFailure(
            messages.j6_6_no_count(session, messages.detail_ccusage_output(str(exc)), str(counter.launcher))
        ) from exc
    if done.returncode != 0:
        detail = messages.detail_ccusage_exit(done.returncode, first_line(done.stderr))
        raise ConfigurationFailure(messages.j6_6_no_count(session, detail, str(counter.launcher)))
    return done.stdout.decode("utf-8", "replace")


def count(counter: Ccusage, folder: Path, session: str) -> Counted:
    """The window in `folder`, counted by ccusage: the session's report, and the models without a price."""
    try:
        report = parse_report(_run(counter, folder, ["--id", session], session))
        unpriced = parse_unpriced(_run(counter, folder, [], session))
    except NotAReport as exc:
        raise ConfigurationFailure(
            messages.j6_6_no_count(session, messages.detail_ccusage_output(exc.detail), str(counter.launcher))
        ) from exc
    return Counted(report, unpriced)
