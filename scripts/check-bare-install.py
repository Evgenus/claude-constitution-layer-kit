#!/usr/bin/env python3
"""Kit check: a module installs through Claude Code and operates on a bare repository with its
defaults alone — requirements A12.1 to A12.3, kernel plus one module (decision
dec-0059-bare-repo-install-in-ci). The bare repository and the install of steps 1 and 2 are the
functions of scripts/kit_install.py, which scripts/check-session-load.py shares (decision
dec-0093-module-evals-with-local-receipts, R10).

Before any other `claude` command the check asks `claude --version` (`kit_module_doc.claude_note`) and
compares it with the version the kit pins in scripts/claude-code.version, which the CI workflow
installs from too. The pinned version: the run goes on. Another readable version: a configuration
failure, whose fix (`kit_module_doc.put_first`) has the check run on the pinned Claude Code put first on
PATH beside the person's own, which stays as it is: through `sh scripts/setup-claude.sh` and the gate list,
`sh scripts/gate-list.sh --run install-<module>`, first, an install by hand second, unless the
environment's CONSTITUTION_KIT_ANY_CLAUDE is exactly `1`: the run then goes on, and each `RED:` finding
headline, each `BROKEN:` line and the closing `GREEN:` or `RED:` line ends with a note naming both
versions. No readable version (the command fails, prints nothing, or opens with a word that is no
version) and a pin file that is missing, empty or no one version are configuration failures whatever
the variable says.

What the check reads of Claude Code, all as it writes it at the version scripts/claude-code.version pins.
From documented `--json` output: the last standard output line of `claude plugin install <key> --json`, its
`outcome` and `scope`, and on a refusal its `failureCode` and `message`; `claude plugin list --json`, per
entry `id`, `scope` and `installPath`. From a documented file: the install record,
<config>/plugins/installed_plugins.json, which the plugin loading page documents as recording each install
with its `scope`, `installPath` and `version`; `installed_commit` reads, for a remote source alone, of the
entries under `plugins[<module>@<marketplace>]` their `installPath`, to find the copy's entry (the page
names the record's fields and does not describe how the file nests them). From an undocumented place:
one, the `gitCommitSha` of that entry, the one field read that no page documents, so the value is taken
only as a git object id. `claude plugin marketplace add` is read for its exit, and on a failure its last
output line is quoted; `claude --version` is read for its first word.

The shared code (decision dec-0099-shared-code-installed-as-a-pip-package, R7 and R17): a module's plugin
holds no copy of `shared/constitution_layer_kit/`, and its hooks and scans import the package that `python3`
finds. So that they find the change's own code and never a release a person installed, the check makes,
right after the bare repository, the environment of `kit_install.shared_path` under the same throwaway
folder: a virtual environment of the python3 the check runs under, with its system packages, whose `.pth`
file names the working folder's `shared/`; nothing is built and nothing needs the network. The marketplace
add, the install and the list of step 2, and every hook and scan of step 3, run with that environment's
`bin` first on PATH. The `claude --version` command is asked before any folder exists and loads no plugin,
so it keeps the person's PATH. A failure to make the environment is a configuration failure with the fix,
as that function words it.

For the module named, in throwaway folders that the check removes:
  1. a bare repository — `git init`, the kit's kernel copied to docs/constitution/ and committed,
     no constitution.yaml — and an empty Claude configuration folder (CLAUDE_CONFIG_DIR), which is the
     platform's whole plugin home for the run: four variables of the environment, each set or empty,
     CLAUDE_CODE_PLUGIN_CACHE_DIR, CLAUDE_CODE_PLUGIN_SEED_DIR, CLAUDE_CODE_PLUGIN_DIRS and
     CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE, are removed from the environment of every `claude` command the
     check runs (`kit_module_doc.claude_env`), the version command included, because they steer where
     Claude Code finds, keeps or loads plugins, as its documentation and a probe of 2.1.282 show: the
     first would have it write its marketplace, plugin cache and install records under the folder it
     names, perhaps the person's own plugins root, and not into that configuration, where the record of
     step 2 is read: <config>/plugins; the second would have it load plugin caches
     from a read-only seed folder and list the seed's marketplaces; the third, load plugin folders as
     `--plugin-dir` loads them, listed beside the install; the fourth, write the install as a zip file,
     where the check reads a folder. Every other variable reaches `claude` unchanged, save the
     CLAUDE_CONFIG_DIR the check sets and, for the version command, the DISABLE_AUTOUPDATER it sets,
     CLAUDE_CODE_PLUGIN_PREFER_HTTPS and the kit's own CONSTITUTION_KIT_* ones included;
  2. `claude plugin marketplace add <source>` and `claude plugin install <module>@<marketplace> --json`,
     the platform's own install, which writes a copy of the plugin into the configuration's cache.
     The marketplace's name is the one the kit's own .claude-plugin/marketplace.json gives, read by
     `kit_module_doc.marketplace_name` and typed nowhere in this check; a file that gives none is a
     configuration failure. The install source is --from, else the environment's
     CONSTITUTION_KIT_INSTALL_FROM, else the kit's working folder. The kit's CI names the change's GitHub
     repository and branch, `<owner>/<repo>#<branch>` — a pull request's head repository and branch, or the
     kit's main on a push to it — the copy a consumer's install writes; a fork the job's token cannot read
     fails; git clones it with the machine's own credentials, which a private remote needs. The working
     folder, a local-directory marketplace, gives a copy no session runs (shared/GATE.md, limit 3).
     The install's result is the last non-empty line of its standard output, one JSON object: an
     `outcome` of "failed" is a refusal, which carries the result's `failureCode` and `message`; "ok" with
     the exit 0 names the `scope` it wrote. The copy is the one entry of `claude plugin list --json`, run
     in the bare repository with the same configuration, whose `id` is `<module>@<marketplace>` at that
     scope, its `installPath` an existing folder. A remote source is compared with the kit's source at
     the commit the install came from, which Claude Code's install record names (gitCommitSha, on the
     version scripts/claude-code.version pins) in the entry of its `plugins` for the module whose
     `installPath` is that copy's: the check's one read of the record, in one function, which takes the
     value only when it is a git object id, 40 or 64 lower-case hexadecimal characters as git writes one,
     since git is handed it and would read a value that opens with `-` as an option; the source is
     read from the kit's git history and fetched when absent. An install from a local
     folder is compared with the module's plugin/ folder there and reads no record;
  3. what the kit's source of the module declares, held in that copy; the source is the module's `plugin/`
     folder, the folder the marketplace entry names and the install copies, and every read of its parts
     goes through it: no link of the source leads inside the plugin folder, the source, save a fixture
     runner's link tests/<package> -> ../scripts/<package> inside it to a package of the module's own
     (as own_packages of kit_module_doc derives them: a folder of
     scripts/, itself no link, holding an __init__.py, its name starting with neither `.` nor `_`,
     save constitution_layer_kit), which arrives as a link leading to that
     package in the copy — the platform keeps a link that stays inside the plugin; no module's plugin
     folder holds such a link today, since a module's runner's links stand in its `tests/`, beside
     `plugin/`; every
     other link arrives as a real file, or a real directory, with the
     same files byte for byte; the copy holds no link the source lacks; the copy holds nothing at
     scripts/constitution_layer_kit, no folder, no file and no link, whatever the source holds there: a plugin
     holds no shared code (decision dec-0099-shared-code-installed-as-a-pip-package, R7), and anything there
     would shadow the package pip installed, a script's folder coming first on Python's path; the copy holds
     the source's hooks file; every hook of the source's hooks/hooks.json, which is a `command` hook
     (`hooks_of`: a hook of another type, `http`, `mcp_tool`, `prompt` or `agent`, is a failure to run, since
     the check cannot prove a hook it does not run), run from the copy in
     exec form on a sample event of its kind with CLAUDE_PLUGIN_ROOT set to the copy, exits 0 on
     the bare repository, and its JSON on standard output neither blocks, denies, asks nor stops,
     each waited for its own `timeout`, else the seconds the hooks reference gives a `command` hook
     on its event: 600, but 30 on UserPromptSubmit, PreModelSwitch and PostModelSwitch, 10 on
     MessageDisplay and 1.5 on SessionEnd;
     every scan the module declares in the enforcement section (template §9) of its MODULE.md, which
     stays at the module folder's top beside the source and is never installed, run from the copy,
     exits 0 there. The scans are read by `kit_module_doc.enforcement`, whatever a row's indent
     or bold, the last cell of a row whether or not the row closes with a bar; an explain mode that
     carries the words `not a tree scan` is none. The problems with the form of the table are
     check-gate-lists', reported once and not here; a document without its `t9` anchor, or with it
     twice, or without `t10` while a later anchor stands, is a configuration failure, never a scan
     left unrun.
A red is a finding against the module, and so is an install Claude Code refuses (a result that says
"failed"). The configuration failures each print their own fix: a missing `claude` or `git`, "install it
and put it on PATH", and a `git` command that fails in the bare repository, "run git <subcommand> in a
new repository by hand and read why it fails"; a marketplace
the CLI cannot add (`claude plugin marketplace add` exits other than 0), "check the kit's marketplace.json,
and that git can reach the source"; an install that gives no result in its 300 s, "run the check again, and
check that git can reach the source"; a `claude plugin list --json` that times out (its exit 124), "run the
check again", or that exits with another code than 0, "run `claude plugin list --json` in a folder of
your own, CLAUDE_CONFIG_DIR set to an empty folder, read why it fails, then run the check again", each
worded by `kit_module_doc.command_fix` from the state of the run, which off the pin adds the run on the
pinned version, no reply having been written for a reader to read. Any other result, list or record that
cannot be read as step 2 says (a record of a remote source that names no commit, or one that is no object
id, included) is a configuration failure whose fix is worded by `kit_module_doc.platform_fix` from the
state of the run: on the pinned version, to update the kit's reader that the line names (`install_scope`
or `listed_install` in scripts/kit_install.py, `installed_commit` here), to what that version writes; off
the pin, to run again on the
pinned version. A hooks file the check cannot run is a configuration failure that names the file and, for a
fault inside it, the event and the place of the group and the hook, counted from 1, never another exception
or a hook left unrun: a file that is no JSON, no object, or without a "hooks" object of events, an event that
is no list of groups, a group that is no object with a "hooks" list of hook objects and, when it has one,
a "matcher" string; a hook with no `type`, or one the hooks reference does not name, "restore
hooks/hooks.json to the shape the hooks reference gives"; a `command` hook with no "command" string, whose
"args", when it has them, are no list of strings, or whose "timeout", when it has one, is no finite number
(a boolean is none), the same fix; a valid hook of a type other than `command`, "make it a `command`
hook, or teach `hooks_of` and `check_installed` in scripts/check-bare-install.py to run a <type> hook";
a hooks file that is there and cannot be read (its permissions, an I/O error), "make it a readable file,
or restore it with git checkout"; a hooks file whose place cannot be looked up (its folder cannot be
searched, an I/O error), "make its folder searchable". A command the check cannot start (an empty one,
a file with no execute permission, a NUL byte, any other `OSError` of starting it) is a configuration failure
that names the command, as `shown` quotes it, and the reason, with "give it a command that exists and can
run" (a hook's, "give the hook's command and args in hooks/hooks.json a command that exists and can run"),
and a path the check cannot look at (a folder on the way cannot be searched, an I/O error) one that names
the path and "give the folder search permission, `chmod u+rx <folder>`", the same on every Python (the
lookups of a path, an entry of a walk included), a missing path being the finding or failure it was. The
walks go through `entries_under`, which is `os.walk` and not `Path.rglob`, since `rglob` raises for a
folder below one it cannot list on one release of the language and lists nothing of it on another: a
folder below the source, the copy or a link's target that cannot be listed is a configuration failure
that names it and "give the folder search permission, `chmod u+rx <folder>`", the same on every Python;
a file of a link's target or of the copy that cannot be read when the two are compared (`bytes_of`) one
that names the file, with `chmod u+r <file>` for the source's and "run the check again" for the copy's.
A command not found is echoed as `plain` quotes it, a word as it is and any other as `shown` does, and a
working folder of `run` that does not exist is a failure of its own, "the working folder <folder> does not
exist", never "is not installed". A missing
hooks file or folder, a folder in the file's place (or a link to one), a dangling link or a link loop there,
or a path through a file, gives no hooks; a link to a regular file is that file. Every other configuration
failure prints a fix of its own, such as a commit the kit's history lacks and cannot fetch, a module
document that cannot be read, a module the kit lacks, a source that names a branch of no repository, a
marketplace file that gives no name. The run holds the case of an absent dials file; a module with
neither hook nor scan is held on its links alone.
Needs no Claude account login: plugin install reads none; git needs a private remote's credentials.

Modes:  --module <name> [--from <source>]  check one module of the kit;
        --self-test      prove step 3 on throwaway source and copy folders, no install: each branch
                         of the link, hooks-file, hook and scan checks red once, a green copy green,
                         a source document that cannot be read (none, no `t9`, `t9` on a heading or
                         twice, `t10` twice or gone with `t11` standing) a BROKEN line, the scans
                         read from rows of each form, a last cell with no closing bar included,
                         the hooks file in each shape `hooks_of` reads or cannot read, one table of
                         whole files with the hooks they give or the whole BROKEN line, nothing else
                         raised: a hook of each of the five types, `command` run and `http`, `mcp_tool`,
                         `prompt` and `agent` each a BROKEN and not a skip; a hook with no `type`, of a
                         name the reference does not give or of one that is no string; a `command` that
                         is absent, a number or a list; `args` of each wrong shape; a `timeout` of 0, -1,
                         5 and 5.5 accepted, and a string, a boolean, null, a list, NaN, an infinity and
                         an integer no float holds each a BROKEN; a matcher that is no string; a file that
                         is no JSON, no UTF-8, nested too deep, a list or lacking "hooks"; an event, a
                         group or a hook of the wrong shape, named by its place; a hooks file that is
                         there and cannot be read (a denied read, an I/O error, the read mocked), the
                         line of its own; a place that cannot be looked up (a hooks folder with no
                         permissions, real unless run as root, and the lookup mocked to a denial and
                         an I/O error), the line naming the folder; and a folder, a dangling link, a
                         link loop, a link to a folder and a path through a file in its place, each
                         real and each giving no hooks, a link to a regular file giving its hooks; the
                         matcher of a group null, 0, false, an empty list or an empty object each a
                         BROKEN, the empty string accepted; the git line
                         of the bare repository, `git init`, `git add` and `git commit` each failing at
                         the exits 1, 2, 124 and 128, the BROKEN named by the subcommand with the `-c`
                         options skipped, the last line quoted from the standard error, else from the
                         standard output, no failure, and a git missing from PATH, `run`'s own line;
                         a command `run` cannot start (an empty one, a file with no execute permission,
                         a NUL byte, each kind of OSError and a ValueError, the process mocked) a BROKEN
                         naming it, a hook's with the hook's own fix, the line for a command not found
                         as it was save that a command of no plain word is quoted as one token, a working
                         folder that does not exist the line naming the folder, and one that outlasts its
                         time as it was; a subfolder that cannot be listed (the listing mocked, and real
                         unless run as root) at each walk site, and a file that cannot be read in a link's
                         folder, in a differing folder and under a file link (the read mocked, and real
                         unless run as root), each a BROKEN naming it; a path the check cannot look at (a
                         module's document and plugin.json, an installPath, a --from source, a link's place
                         in the copy, a file or link of a folder that lists but cannot be searched, the
                         hooks file
                         of the copy, each under a folder of mode 000, real unless run as root, and an I/O
                         error mocked) a BROKEN naming the folder to open, the source's hooks file the
                         line `hooks_of` had, and a missing path, a link loop, a path through a file and
                         a NUL in a name each the result they had;
                         and the report of one finding as literal lines with exit 2; and step 2
                         over a toy kit whose marketplace is named `toy-mp` (its name read from its
                         file, a file with no name a BROKEN) and a fake `claude` asked for
                         `<module>@toy-mp --json`: each reply of the install (ok, failed with and
                         without a failureCode, no output, a human line, the JSON line not last, ok with
                         exit 1, exit 124 and a timeout, a list, no scope, an outcome of no known
                         word), of the list (empty, another scope, the id twice, no installPath, no
                         folder, not a list, no JSON, an exit other than 0 and a timeout, the right entry
                         among others in either order) and of the record (a commit, none, empty, no string,
                         missing, no JSON, no entry of the copy, the copy's entry told from entries of
                         another installPath, before it and after, and from entries of the copy's leaf name
                         in another folder and with no installPath or one that is no string, before it, a
                         commit that is no object id: an option, a word, 39 or 41 or 63 or 65 characters,
                         upper case, with a line break, cut at 200 characters, and git never handed it; a
                         local folder reading none), a reply or
                         a value quoted whole up to 200 characters and cut after, a list of five entries
                         named whole and one of six cut with "…", the install's timeout the one `run`
                         waits for, the wait of a hook with no timeout of its own by its event and of one
                         with its own, and that `check_installed` hands that wait to `run` (spied, no
                         hook run), the fix `platform_fix` words for an unreadable result, list and record,
                         each on the pin and one of each off it, the fix `command_fix` words for a list that
                         exits 1 or 3, that exits 124 and that times out (the process mocked, no wait), on
                         the pin and off it, and the reports of a refusal, of a finding, of a green run and
                         of configuration failures, a file the run cannot read included, as literal lines
                         through `main`, with and without the note; and of a module's source at a commit
                         from the kit's history (const-meta-types at HEAD, its plugin
                         free of shared code); and
                         the version check over a fake `claude` that answers `--version` with the pin,
                         another version, a longer or shorter one, no version, blank lines before the
                         version, a failure, a crash and no answer, the variable unset and at each other
                         value than `1`, and at `1`, the pin file missing and `claude` missing,
                         the run stopped with no other `claude` command run, that command run in an empty
                         configuration folder of its own with the auto-updater off, and the version
                         command, the marketplace add, the install and the list each run with none of the
                         four variables of `claude_env`, each set to a folder or to `1` and set empty in
                         the person's environment, and with CLAUDE_CODE_PLUGIN_PREFER_HTTPS and an
                         unrelated variable kept; the record read from the check's own configuration,
                         and the folders the variables name left empty; CONSTITUTION_KIT_ANY_CLAUDE and
                         CONSTITUTION_KIT_INSTALL_FROM still read with the four set; and the reports of
                         a run off the pin, a finding's and a green one's, as literal lines; and the shared
                         code's environment, over a toy kit whose shared package says a mark: a run making
                         it and handing its PATH to the marketplace add, the install, the list and the
                         check of the hooks and scans, the person's PATH after it; the PATH the step
                         returns with a PATH given, with none and with an empty one; its `.pth` file naming
                         the kit's `shared/` alone, and its python3 importing the toy kit's package and
                         PyYAML; a release in the user's site-packages never imported by it; a kit without
                         the package, a python3 whose venv fails, a `.pth` file that cannot be written, a
                         package that cannot be imported and a PYTHONPATH that puts another copy first
                         each a BROKEN line with its fix; the check run under a virtual environment, whose
                         packages the new environment sees; and a plugin with no link to the shared code,
                         whose hook and scan import it, green with the environment's PATH and red without
                         it, the hook and the scan each exiting 1; and a copy that holds a folder, a link, a
                         dangling link or a file at scripts/constitution_layer_kit, whatever its source holds
                         there, a finding that names what stands there, ahead of any other.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import errno
import io
import json
import math
import os
import re
import shlex
import shutil
import site
import stat
import subprocess
import sys
import tarfile
import tempfile
from collections.abc import Callable, Iterator
from dataclasses import dataclass, replace
from functools import partial
from pathlib import Path
from typing import Any
from unittest import mock

import kit_install
from kit_install import (
    FROM_ENV,
    SHARED_ENV,
    SHARED_PTH,
    Broken,
    Refused,
    bare_repository,
    blocking_folder,
    file_at,
    folder_at,
    git_command,
    install,
    kit_marketplace,
    last_line,
    link_at,
    listed_install,
    run,
    shared_path,
    shown,
    there,
)
from kit_module_doc import (
    DocumentError,
    Note,
    claude_note,
    enforcement,
    own_packages,
    platform_fix,
)

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
WHY = "a module must install and operate on a bare repository with its defaults alone (requirement A12.1)"
NOTE = "docs/note.md"
OBJECT_ID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")  # a git object id as git writes one: SHA-1 or SHA-256
SCRIPT = "scripts/check-bare-install.py"  # named in the fix of a reply the check's readers do not read
# How long a `command` hook that declares no `timeout` is waited for: the platform's own default on its event
# (the hooks reference, "Common fields" of a hook, and the sections of SessionEnd and MessageDisplay, read on
# 2026-10-08): 600 seconds, but 30 on UserPromptSubmit, PreModelSwitch and PostModelSwitch, 10 on
# MessageDisplay, and on SessionEnd the 1.5 seconds its hooks share, which one hook is waited for here.
HOOK_TIMEOUT = 600.0
HOOK_TYPES = ("command", "http", "mcp_tool", "prompt", "agent")  # the hooks reference's `type` values
EVENT_HOOK_TIMEOUT = {
    "UserPromptSubmit": 30.0,
    "PreModelSwitch": 30.0,
    "PostModelSwitch": 30.0,
    "MessageDisplay": 10.0,
    "SessionEnd": 1.5,
}


@dataclass(frozen=True)
class Finding:
    module: str
    what: str
    fix: str

    def render(self, note: str = "") -> str:
        """The finding as lines, the note of a run off the pin at the end of its headline."""
        return f"RED: {self.module}: {self.what}{note}\n  why: {WHY}\n  fix: {self.fix}"


@dataclass(frozen=True)
class Hook:
    event: str
    matcher: str
    command: str
    args: tuple[str, ...]
    timeout: float


HOOK_RUN_FIX = (
    'give the hook\'s "command" and "args" in the module\'s hooks/hooks.json a command that exists and can'
    " run, with no NUL byte in it or its arguments: a program on PATH, or a file of the module with the"
    " execute permission (`chmod u+x` it, and commit the mode), then run the check again"
)


def hooks_of(plugin: Path) -> list[Hook]:
    """The hooks of a plugin's hooks/hooks.json, each with the seconds it is waited for: its own `timeout`,
    else the platform's default for a `command` hook on its event (`EVENT_HOOK_TIMEOUT`, else
    `HOOK_TIMEOUT`). A hooks file that is a regular file and cannot be read (an `OSError`: its
    permissions, an I/O error) is a Broken of its own, with a fix to make it readable; so is a place
    that cannot be looked up (an `OSError` from `Path.stat`, one that is no missing file, no path through
    a file and no link loop: its folder cannot be searched, an I/O error), with a fix to make the folder
    searchable, since the file's permissions and `git checkout` do not mend that; `Path.stat` and not
    `Path.is_file` makes the lookup, since `is_file` returns False for such an error from release 3.14 of
    the language on, and the answer would differ by version. A missing hooks file or folder, or anything in
    its place that is no regular file (a folder, a link to one), gives no hooks, as does a path through a
    file, a dangling link or a link loop; a link to a regular file is that file. Every shape of the file
    the check cannot run is a Broken naming the file, the event and the hook's place (group and hook,
    counted from 1), never another exception: a file that is no object with a "hooks" object of events,
    each a list of groups, each an object with a "hooks" list of hook objects and a "matcher", when
    present, that is a string; a hook with no `type` of the five the hooks reference names; for a
    `command` hook, a "command" that is no string, "args" that are no list of strings, a "timeout" that is
    no finite number (a boolean is none); and a valid hook of a type other than `command`, which the
    check does not run and so cannot prove."""
    path = plugin / "hooks" / "hooks.json"
    text = hooks_file_text(path)
    if text is None:
        return []
    table = hooks_table(path, text)
    found: list[Hook] = []
    for event, groups in table.items():
        if not isinstance(groups, list):
            raise not_a_hooks_file(path, f"event {shown(event)}: {shown(groups)} is no list of groups")
        for number, group in enumerate(groups, 1):
            found.extend(group_hooks(path, event, number, group))
    return found


def not_a_hooks_file(path: Path, detail: str) -> Broken:
    """The Broken for a hooks file whose shape the check cannot run, with the fix to restore the shape."""
    fix = (
        "restore hooks/hooks.json to the shape the hooks reference gives,"
        " so that the check can read each hook it runs"
    )
    return Broken(f"{path} is not a hooks file ({detail}) — fix: {fix}")


def hooks_file_text(path: Path) -> str | None:
    """The text of a hooks file that is a regular file, None where there is none to read (no file, a
    folder in its place, a dangling link, a path through a file, a link loop); a Broken where the place
    cannot be looked up or the file cannot be read as UTF-8."""
    try:
        mode = path.stat().st_mode  # follows a link; `is_file` hides a PermissionError from release 3.14 on
    except (FileNotFoundError, NotADirectoryError):  # no file, a dangling link, a path through a file
        return None
    except OSError as bad:
        if bad.errno == errno.ELOOP:  # a link loop leads to no file either
            return None
        # the place cannot be looked up: no file to read, no shape to restore
        raise Broken(
            f"{path} cannot be looked up ({bad.strerror}) — fix: make its folder {path.parent} searchable"
            f" (its permissions), so that the check can find hooks/hooks.json and read each hook it runs"
        ) from bad
    if not stat.S_ISREG(mode):  # a folder in the file's place
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError as bad:  # the file is there and cannot be read: no shape to restore
        raise Broken(
            f"{path} cannot be read ({bad.strerror}) — fix: make it a readable file (its"
            f" permissions), or restore it with git checkout -- {path}, so that the check can read each"
            f" hook it runs"
        ) from bad
    except ValueError as bad:  # not UTF-8
        raise not_a_hooks_file(path, str(bad)) from bad


def hooks_table(path: Path, text: str) -> dict[str, object]:
    """The "hooks" object of events in the text of a hooks file; a Broken where the text is no JSON object
    holding one."""
    try:
        data: object = json.loads(text)
    except (ValueError, RecursionError) as bad:
        raise not_a_hooks_file(path, str(bad)) from bad
    if not isinstance(data, dict):
        raise not_a_hooks_file(path, f"the top level is {shown(data)}, not a JSON object")
    if "hooks" not in data:
        raise not_a_hooks_file(path, 'the top level has no "hooks" key')
    table = data["hooks"]
    if not isinstance(table, dict):
        raise not_a_hooks_file(path, f'"hooks" is {shown(table)}, not an object of events')
    return table


def group_hooks(path: Path, event: str, number: int, group: object) -> list[Hook]:
    """The hooks of one group of an event, `number` counted from 1; a Broken where the group is no object
    with a "hooks" list and a string "matcher", or one of its hooks cannot be run."""
    in_group = f"event {shown(event)}, group {number}"
    if not isinstance(group, dict):
        raise not_a_hooks_file(path, f"{in_group}: {shown(group)} is no object")
    if "hooks" not in group:
        raise not_a_hooks_file(path, f'{in_group}: no "hooks" key')
    if not isinstance(group["hooks"], list):
        raise not_a_hooks_file(path, f'{in_group}: "hooks" is {shown(group["hooks"])}, not a list')
    matcher = group.get("matcher", "")
    if not isinstance(matcher, str):
        raise not_a_hooks_file(path, f'{in_group}: "matcher" is {shown(matcher)}, not a string')
    return [
        command_hook(path, event, matcher, f"{in_group}, hook {place}", hook)
        for place, hook in enumerate(group["hooks"], 1)
    ]


def command_hook(path: Path, event: str, matcher: str, where: str, hook: object) -> Hook:
    """One hook object as a `Hook`, its wait its own `timeout` or the default of its event; a Broken where
    it is no valid `command` hook."""
    if not isinstance(hook, dict):
        raise not_a_hooks_file(path, f"{where}: {shown(hook)} is no object")
    kind = hook.get("type")
    if "type" not in hook:
        raise not_a_hooks_file(path, f'{where}: "type" is absent')
    if kind not in HOOK_TYPES:
        raise not_a_hooks_file(path, f'{where}: "type" is {shown(kind)}, not one of {", ".join(HOOK_TYPES)}')
    if kind != "command":
        raise Broken(
            f"{path} holds a hook of type {kind} ({where}) that check-bare-install does not run"
            f" — it runs only `command` hooks, and cannot prove a hook it does not run"
            f" — fix: make it a `command` hook, or teach `hooks_of` and `check_installed` in"
            f" {SCRIPT} to run a {kind} hook"
        )
    if "command" not in hook:
        raise not_a_hooks_file(path, f'{where}: "command" is absent')
    if not isinstance(hook["command"], str):
        raise not_a_hooks_file(path, f'{where}: "command" is {shown(hook["command"])}, not a string')
    args = hook.get("args", [])
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        raise not_a_hooks_file(path, f'{where}: "args" is {shown(args)}, not a list of strings')
    seconds = EVENT_HOOK_TIMEOUT.get(event, HOOK_TIMEOUT)
    if "timeout" in hook:
        declared = declared_seconds(hook["timeout"])
        if declared is None:
            raise not_a_hooks_file(
                path, f'{where}: "timeout" is {shown(hook["timeout"])}, not a finite number of seconds'
            )
        seconds = declared
    return Hook(event, matcher, hook["command"], tuple(args), seconds)


def declared_seconds(timeout: object) -> float | None:
    """A hook's declared `timeout` as seconds: a JSON number, an integer or a float, that is finite; a
    boolean (an `int` in Python), a string, a list, a null, NaN, an infinity and an integer no float holds
    are none. Zero and below are numbers, and stay as they are."""
    if isinstance(timeout, bool) or not isinstance(timeout, int | float):
        return None
    try:
        seconds = float(timeout)
    except OverflowError:  # an integer of more than 308 digits
        return None
    return seconds if math.isfinite(seconds) else None


def declared_scans(module_folder: Path) -> list[str]:
    """The scans a module declares, read from its MODULE.md, which stays at the module folder's top beside
    the plugin folder and is never installed."""
    document = module_folder / "MODULE.md"
    if not file_at(document):
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


def unlisted(bad: OSError) -> Broken:
    """The Broken for a folder a walk cannot list, naming it and the folder to open: the one itself, or the
    folder above it when that one cannot be searched. The walk is `os.walk` and not `Path.rglob`, which
    raises for a folder below one it cannot list on one release of the language and lists nothing on
    another, so that the answer would differ by version."""
    folder = Path(os.fsdecode(bad.filename)) if bad.filename is not None else Path()
    why = bad.strerror or str(bad)
    if bad.errno == errno.EACCES:
        try:
            os.stat(folder)
            opening = folder
        except PermissionError:
            opening = blocking_folder(folder)
        except OSError:
            opening = folder
        fix = f"give the folder {opening} search permission, `chmod u+rx {shlex.quote(str(opening))}`"
    else:
        fix = f"make the folder {folder} listable, `ls -ld {shlex.quote(str(folder))}` shows why not"
    return Broken(f"{folder} cannot be listed ({why}) — fix: {fix}, then run the check again")


def entries_under(folder: Path) -> list[Path]:
    """Every entry below a folder, files, folders and links (a link to a folder is one entry and is not
    entered), as `Path.rglob("*")` lists them; a folder that is not there lists nothing, and one that
    cannot be listed is a Broken naming it, on every Python."""
    found: list[Path] = []

    def failed(bad: OSError) -> None:
        if not isinstance(bad, FileNotFoundError | NotADirectoryError):
            raise unlisted(bad)

    for here, folders, files in os.walk(folder, onerror=failed):
        folders.sort()
        found.extend(Path(here) / name for name in (*folders, *files))
    return found


def bytes_of(path: Path, installed: bool) -> bytes:
    """The bytes of a file the links are compared by; a file that cannot be read is a Broken naming it.
    `installed` is whether the file is in the installed copy, which the check cannot mend and rebuilds."""
    try:
        return path.read_bytes()
    except OSError as bad:
        why = bad.strerror or str(bad)
        quoted = shlex.quote(str(path))
        if installed:
            fix = (
                "run the check again, and if it repeats, report that the install wrote a file the check"
                " cannot read, at the version the kit pins"
            )
        elif bad.errno == errno.EACCES:
            fix = f"give the file read permission, `chmod u+r {quoted}`, then run the check again"
        else:
            fix = f"make the file readable, `ls -l {quoted}` shows why not, then run the check again"
        raise Broken(f"{path} cannot be read ({why}) — fix: {fix}") from bad


def files_under(folder: Path) -> set[str]:
    """The files under a folder, by relative path, caches left out."""
    return {
        str(f.relative_to(folder))
        for f in entries_under(folder)
        if file_at(f) and not any(part in CACHES for part in f.relative_to(folder).parts)
    }


def runner_link(source: Path, link: Path) -> bool:
    """The fixture runner's link to a package of the module's own: tests/<name> leading to the folder
    scripts/<name> of the source, one of the packages own_packages of kit_module_doc derives."""
    where = link.relative_to(source)
    package = source / "scripts" / where.name
    return (
        where.parts == ("tests", where.name)
        and link.resolve() == package.resolve()
        and package in own_packages(source)
    )


def link_findings(module: str, source: Path, plugin: Path) -> list[Finding]:
    """No link of the source leads inside the plugin folder, the source, save the runner's link to a
    package of the module's own, which arrives as a link leading to that package in the copy; every other link
    arrives as a real file, or a real directory, with the same files byte for byte; the copy holds no
    link the source lacks."""
    findings: list[Finding] = []
    links = sorted(p for p in entries_under(source) if link_at(p))
    for link in links:
        where = link.relative_to(source)
        place = plugin / where
        target = link.resolve()
        if runner_link(source, link):
            package = plugin / "scripts" / where.name
            if not there(place) or not folder_at(package) or place.resolve() != package.resolve():
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
            "replace the link inside the plugin with the file it points at"
            if inside
            else "the install must carry what it runs — fire the fallback of limit 3 of"
            " shared/GATE.md §4, links replaced by copies"
        )
        if link_at(place) or not there(place):
            state = "left a link" if link_at(place) else "missing"
            findings.append(Finding(module, f"the link {where} is {state} in the installed copy", fix))
        elif inside:
            findings.append(Finding(module, f"the link {where} leads inside the plugin", fix))
        elif file_at(target) and folder_at(place):
            findings.append(Finding(module, f"the link {where} to a file arrived as a folder", fix))
        elif folder_at(target) and not folder_at(place):
            findings.append(Finding(module, f"the link {where} to a folder arrived as a file", fix))
        elif not there(target):
            findings.append(Finding(module, f"the link {where} leads nowhere in the source", fix))
        elif folder_at(target) and (
            files_under(place) != files_under(target)
            or any(bytes_of(place / f, True) != bytes_of(target / f, False) for f in files_under(target))
        ):
            differing = sorted(
                (files_under(target) ^ files_under(place))
                | {
                    f
                    for f in files_under(target) & files_under(place)
                    if bytes_of(place / f, True) != bytes_of(target / f, False)
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
        elif file_at(target) and bytes_of(place, True) != bytes_of(target, False):
            findings.append(
                Finding(module, f"the link {where} arrived with other bytes than its target", fix)
            )
    carried = {plugin / link.relative_to(source) for link in links}
    for extra in sorted(p for p in entries_under(plugin) if link_at(p) and p not in carried):
        findings.append(
            Finding(
                module,
                f"the installed copy holds a link its source lacks: {extra.relative_to(plugin)}",
                "find what makes the link in the install, and make the module carry a file instead",
            )
        )
    return findings


def shared_code_findings(module: str, plugin: Path) -> list[Finding]:
    """The installed copy holds nothing at scripts/constitution_layer_kit: no folder, no file, no link and no
    dangling link, whatever the source holds there. A plugin holds no shared code; its entry files import the
    package that pip installed for python3, and a folder at this place, which comes first on Python's path
    as the script's own folder, would shadow it."""
    place = plugin / "scripts" / "constitution_layer_kit"
    if not (there(place) or link_at(place)):
        return []
    found = "a link" if link_at(place) else "a folder" if folder_at(place) else "a file"
    return [
        Finding(
            module,
            f"the installed copy holds scripts/constitution_layer_kit, {found}, shared code in a plugin that"
            " imports the package pip installed",
            f"remove it from the module (git rm -r modules/{module}/plugin/scripts/constitution_layer_kit):"
            " the entry files import the Python package for python3, and anything at this place shadows it",
        )
    ]


def check_installed(
    module: str, source: Path, plugin: Path, repo: Path, data: Path, path: str | None = None
) -> list[Finding]:
    """What the kit's source of the module promises, held in its installed copy on a bare repository, every
    hook and scan run with `path` as its PATH when given, as `check_module` gives it; a
    failure that stops the check (a `Broken`) is raised in this order, the source's hooks file (`hooks_of`)
    and the copy's hooks-file lookup first, then the walks and lookups of the links, then the rest, so that
    a hooks folder that cannot be searched is named by its own lookup before a walk names it."""
    # The hooks file is looked up before the walks of `link_findings`, so that a hooks folder of the source
    # or of the copy that cannot be searched is the line of its own lookup (`hooks_of`, `file_at`) and not
    # the walk's, which names the same folder; the findings keep their order, the links first.
    hooks = hooks_of(source)
    lacks_hooks_file = file_at(source / "hooks" / "hooks.json") and not file_at(
        plugin / "hooks" / "hooks.json"
    )
    findings = shared_code_findings(module, plugin) + link_findings(module, source, plugin)
    if lacks_hooks_file:
        findings.append(
            Finding(module, "the installed copy has no hooks/hooks.json", "restore the hooks file")
        )
    env = (
        os.environ
        | {
            "CLAUDE_PLUGIN_ROOT": str(plugin),
            "CLAUDE_PROJECT_DIR": str(repo),
            "CLAUDE_PLUGIN_DATA": str(data),
        }
        | ({} if path is None else {"PATH": path})
    )
    for hook in hooks:
        argv = [a.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin)) for a in (hook.command, *hook.args)]
        shown = " ".join(argv[1:]).replace(str(plugin), "<plugin>")
        note = repo / NOTE
        if hook.event == "PostToolUse":
            note.write_text("# Note\n", encoding="utf-8")
        code, out, err = run(
            argv, repo, env, json.dumps(sample_event(hook, repo)), hook.timeout, fix=HOOK_RUN_FIX
        )
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
    for entry in declared_scans(source.parent):
        script = plugin / "scripts" / (entry if entry.endswith(".py") else f"{entry}.sh")
        # The scan runs as a consumer's machine would run it: `python3` found on PATH for a `.py` scan, `sh`
        # for a shell one, not the interpreter this check runs in.
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


def claude_noted(kit: Path, env: dict[str, str]) -> Note:
    """The note for a run on another Claude Code than the kit pins, empty on the pinned one, from
    `kit_module_doc.claude_note`; its refusal is a Broken with that function's line."""
    try:
        return claude_note(kit, env)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad


def installed_commit(config: Path, key: str, plugin: Path, note: Note) -> str:
    """The commit the install of `key` came from: the `gitCommitSha` of the entry of Claude Code's install
    record, `<config>/plugins/installed_plugins.json`, under `plugins[key]` whose `installPath` is the
    copy's folder that `claude plugin list --json` gave — the check's one read of a field the platform
    does not document, and the one place that reads the record. A record that is missing, no JSON, without
    that entry, or whose commit is absent, empty, no string or no git object id (40 or 64 characters of
    lower-case hexadecimal, as git writes one: the value goes on to git, which would read a value that
    opens with `-` as an option) is a Broken."""
    record = config / "plugins" / "installed_plugins.json"

    def unnamed(why: str) -> Broken:
        return Broken(
            f"the install record names no commit for {key} ({record}: {why})"
            + platform_fix(note, SCRIPT, "installed_commit", "a record")
        )

    try:
        data = json.loads(record.read_text(encoding="utf-8"))
    except OSError as bad:
        raise unnamed(f"cannot be read, {bad.strerror}") from bad
    except ValueError as bad:
        raise unnamed(f"is no JSON, {bad}") from bad
    plugins = data.get("plugins") if isinstance(data, dict) else None
    entries = plugins.get(key) if isinstance(plugins, dict) else None
    if not isinstance(entries, list):
        raise unnamed(f"holds no list under plugins[{key!r}]")
    own = [e for e in entries if isinstance(e, dict) and isinstance(e.get("installPath"), str)]
    entry = next((e for e in own if Path(e["installPath"]) == plugin), None)
    if entry is None:
        raise unnamed(f"holds no entry for {key} whose installPath is {plugin}")
    sha = entry.get("gitCommitSha")
    if not isinstance(sha, str) or not sha:
        what = (
            "absent" if "gitCommitSha" not in entry else "empty" if sha == "" else f"no string, {shown(sha)}"
        )
        raise unnamed(f"gitCommitSha is {what}")
    if not OBJECT_ID.fullmatch(sha):
        raise unnamed(
            f"gitCommitSha is no git object id (40 or 64 lower-case hexadecimal characters), {shown(sha)}"
        )
    return sha


def source_at(commit: str, module: str, root: Path) -> Path:
    """The kit's source of the module at a commit — its plugin folder and the module's document beside it —
    read from git history into a folder under root, the commit fetched when the clone lacks it; the plugin
    folder is what it returns. The plugin holds no link to the shared code, so the shared code is not read."""
    env = os.environ.copy()
    code, _, _ = run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], KIT, env)
    if code != 0:
        # `origin` is the remote that the CI job's checkout and a person's clone of the kit both name for the
        # repository they came from, where the commit the install came from is looked for. A clone with no
        # `origin`, or one whose `origin` lacks the commit, fails here, and that failure is the BROKEN below.
        code, out, err = run(["git", "fetch", "-q", "origin", commit], KIT, env)
        if code != 0:
            raise Broken(
                f"commit {commit} is not in the kit's history and cannot be fetched ({last_line(out, err)})"
                " — fix: run the check from a clone that holds it"
            )
    try:
        done = subprocess.run(
            ["git", "archive", "--format=tar", commit, f"modules/{module}"],
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
    return target / "modules" / module / "plugin"


def counted(source: Path) -> str:
    links = sum(1 for p in entries_under(source) if link_at(p))
    return f"{len(hooks_of(source))} hook(s), {len(declared_scans(source.parent))} scan(s), {links} link(s)"


def check_module(module: str, source: str, note: Note) -> tuple[list[Finding], str]:
    """The findings, and what was examined: the hooks, scans and links of the source compared."""
    if not file_at(KIT / "modules" / module / "plugin" / ".claude-plugin" / "plugin.json"):
        raise Broken(f"no module {module} in the kit — fix: name a folder under modules/ that holds a plugin")
    marketplace = kit_marketplace(KIT)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        repo = bare_repository(root)
        path = shared_path(root)  # the PATH of every `claude` command, hook and scan below
        try:
            plugin = install(module, root, repo, source, marketplace, note, path=path)
        except Refused as refused:
            refusal_finding = Finding(
                module,
                f"Claude Code refuses to install it ({refused})",
                "fix its manifest or its entry in marketplace.json",
            )
            return [refusal_finding], "no install"
        (root / "data").mkdir()
        if there(Path(source)):  # a local folder is copied as it stands, uncommitted edits included
            kit_source = Path(source).resolve() / "modules" / module / "plugin"
        else:
            commit = installed_commit(root / "config", f"{module}@{marketplace}", plugin, note)
            kit_source = source_at(commit, module, root)
        return check_installed(module, kit_source, plugin, repo, root / "data", path), counted(kit_source)


def report(module: str, findings: list[Finding], examined: str, note: str = "") -> int:
    if findings:
        for finding in findings:
            print(finding.render(note))
        print(f"RED: {len(findings)} finding(s) — {examined}{note}")
        return EXIT_RED
    print(f"GREEN: {module} installs and operates on a bare repository with its defaults — {examined}{note}")
    return EXIT_GREEN


# The self-test, `self_test` below: groups of cases, each a function that takes the `Tally` of the run,
# and the fixtures they share, each named for the cases it serves. The groups run in the order they print.
@dataclass
class Tally:
    """What a self-test run has counted: the cases failed, and the cases of the version check and of step 2,
    which print one by one."""

    failed: int = 0
    extra: int = 0


def version_case(tally: Tally, name: str, ok: bool, got: str) -> None:
    """Print one case as ok or FAIL, what was got beside a FAIL, and count it."""
    tally.extra += 1
    tally.failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] {name}")
    if not ok:
        print(f"        got: {got}")


# The fixtures of the link, hook and scan cases: a throwaway source and the copy an install made of it.
@contextlib.contextmanager
def patched_globals(values: dict[str, object]) -> Iterator[None]:
    """Patch names of this check for a case, and the same names in `kit_install`, whose install steps this
    check shares and which reads its own `run` and `KIT`."""
    shared = {name: value for name, value in values.items() if name in vars(kit_install)}
    with mock.patch.dict(globals(), values), mock.patch.dict(vars(kit_install), shared):
        yield


FIXTURE_MODULE_TEXT = (
    '<a id="t9"></a>\n| E1 | `check-x --scan`: all | `gate` |\n| E2 | `check-p.py --scan` | `gate` |\n'
    '<a id="t10"></a>\n'
)
FIXTURE_COMMAND = {"type": "command", "command": "sh", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/hook.sh"]}
FIXTURE_HOOKS = {"hooks": {"PreToolUse": [{"matcher": "Write|Edit", "hooks": [FIXTURE_COMMAND]}]}}
FIXTURE_DENY = '{"hookSpecificOutput": {"permissionDecision": "deny"}}'


def fixture_document(change: str) -> str:
    """The text of the source's MODULE.md that `change` asks for."""
    return {
        "no-t9": "no anchor\n",
        "t9-on-heading": FIXTURE_MODULE_TEXT.replace('<a id="t9"></a>\n', '## 9 <a id="t9"></a>\n'),
        "t9-twice": FIXTURE_MODULE_TEXT.replace('<a id="t9"></a>\n', '<a id="t9"></a>\n<a id="t9"></a>\n'),
        "t10-twice": FIXTURE_MODULE_TEXT.replace("| E2", '<a id="t10"></a>\n| E2'),
        "t10-missing": FIXTURE_MODULE_TEXT.replace('<a id="t10"></a>\n', '<a id="t11"></a>\n'),
        "indented-scan-red": FIXTURE_MODULE_TEXT.replace("| E1 |", "   | E1 |"),
        "explain-marked": FIXTURE_MODULE_TEXT.replace(
            '<a id="t10"></a>',
            "| E3 | `check-y --scan --since <date>`: the report, not a tree scan | `advisory` |\n"
            '<a id="t10"></a>',
        ),
    }.get(change, FIXTURE_MODULE_TEXT)


def fixture_hook_line(change: str) -> str:
    """The line that the source's hook script runs after it has checked its event, as `change` asks."""
    return {
        "hook-exit-1": "exit 1",
        "hook-exit-2": "exit 2",
        "hook-denies": f"echo '{FIXTURE_DENY}'",
        "hook-denies-and-warns": f"echo '{FIXTURE_DENY}'; echo 'WARNING: logged' >&2",
        "hook-blocks": """echo '{"decision": "block"}'""",
        "hook-asks": """echo '{"hookSpecificOutput": {"permissionDecision": "ask"}}'""",
        "hook-stops": """echo '{"continue": false}'""",
    }.get(change, "exit 0")


def fixture_source(root: Path, change: str) -> tuple[Path, Path]:
    """The source, the plugin folder of a module folder that holds its MODULE.md beside it, and the shared
    folder its `scripts/shared` links to, as `change` asks."""
    module, shared = root / "module", root / "shared"
    source = module / "plugin"
    (shared).mkdir()
    (shared / "code.py").write_text("x = 1\n", encoding="utf-8")
    (source / "hooks").mkdir(parents=True)
    (source / "scripts").mkdir()
    (source / "hooks" / "hooks.json").write_text(json.dumps(FIXTURE_HOOKS), encoding="utf-8")
    if change != "no-document":
        (module / "MODULE.md").write_text(fixture_document(change), encoding="utf-8")
    hook = fixture_hook_line(change)
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
    return source, shared


def fixture_copy_of(root: Path, source: Path, change: str) -> Path:
    """The copy an install made of the source, the plugin folder: its files, and its links left as real
    files; it holds no MODULE.md, which stays at the module folder's top."""
    copy = root / "copy"
    shutil.copytree(source, copy, symlinks=False)
    if change == "inner-link":
        shutil.rmtree(copy / "scripts" / "again")
        (copy / "scripts" / "again").symlink_to(copy / "hooks")
    return copy


def fixture_runner_package(root: Path, change: str, source: Path) -> tuple[str, str]:
    """The package and the folder of the runner's link in the source, as a case named runner-link-* asks."""
    package = {
        "runner-link-no-package": "data",
        "runner-link-constitution-layer-kit": "constitution_layer_kit",
        "runner-link-underscore": "_own_gate",
    }.get(change, "own_gate")
    # scripts/own_gate a link out of the module, as constitution_layer_kit
    if change == "runner-link-to-a-link":
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
    return package, holder


def fixture_runner_copy(change: str, source: Path, copy: Path, package: str, holder: str) -> None:
    """The runner's link in the copy: kept, or arrived as a folder, leading elsewhere, dangling or missing."""
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


def fixture_source_changes(change: str, source: Path, shared: Path, copy: Path) -> None:
    """The changes of a case that touch the source as well as the copy."""
    if change == "inner-link-copied":
        (source / "scripts" / "again").symlink_to(source / "hooks")
        shutil.copytree(source / "hooks", copy / "scripts" / "again")
    if change == "shared-code-folder":  # the old arrangement: a link to the shared code, arrived as a folder
        (source / "scripts" / "constitution_layer_kit").symlink_to(shared)
        shutil.copytree(shared, copy / "scripts" / "constitution_layer_kit")
    if change == "link-other-bytes":
        (source / "scripts" / "one").symlink_to(shared / "code.py")
        (copy / "scripts" / "one").write_text("x = 2\n", encoding="utf-8")
    if change == "file-link-as-folder":
        (source / "scripts" / "one").symlink_to(shared / "code.py")
        (copy / "scripts" / "one").mkdir()
    if change == "no-event":
        (source / "hooks" / "hooks.json").write_text(
            json.dumps({"hooks": {"PreToolUse": [{"matcher": "Write", "hooks": [FIXTURE_COMMAND]}]}}).replace(
                "PreToolUse", "PostToolUse"
            ),
            encoding="utf-8",
        )


def fixture_copy_changes(change: str, shared: Path, copy: Path) -> None:
    """The changes of a case that touch the copy alone."""
    if change == "link-left":
        shutil.rmtree(copy / "scripts" / "shared")
        (copy / "scripts" / "shared").symlink_to(shared)
    if change == "link-missing":
        shutil.rmtree(copy / "scripts" / "shared")
    if change == "no-hooks-file":
        (copy / "hooks" / "hooks.json").unlink()
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
    if change == "shared-code-link":
        (copy / "scripts" / "constitution_layer_kit").symlink_to(shared)
    if change == "shared-code-file":
        (copy / "scripts" / "constitution_layer_kit").write_text("x = 1\n", encoding="utf-8")
    if change == "shared-code-dangling":
        (copy / "scripts" / "constitution_layer_kit").symlink_to(copy / "nowhere")


def fixture_folders(root: Path, change: str) -> tuple[Path, Path]:
    """The source and the copy for a case: a green pair, `change` made to the pair."""
    source, shared = fixture_source(root, change)
    copy = fixture_copy_of(root, source, change)
    if change.startswith("runner-link"):
        package, holder = fixture_runner_package(root, change, source)
        fixture_runner_copy(change, source, copy, package, holder)
    fixture_source_changes(change, source, shared, copy)
    fixture_copy_changes(change, shared, copy)
    return source, copy


def fixture_findings(change: str) -> list[Finding]:
    """The findings of `check_installed` over the source and the copy that `change` makes."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        (root / "repo" / "docs").mkdir(parents=True)
        (root / "data").mkdir()
        source, copy = fixture_folders(root, change)
        return check_installed("const-x", source, copy, root / "repo", root / "data")


LINK_CASES = {
    "a copy whose hook and scans pass, its outside link a real directory, is green": ("", ""),
    "a link left a link in the copy is a finding": ("link-left", "is left a link"),
    "a link missing from the copy is a finding": ("link-missing", "is missing"),
    "a link inside the plugin left a link is a finding, fixed by the file it points at": (
        "inner-link",
        "again",
    ),
    "a link inside the plugin that arrived as a real directory is a finding": (
        "inner-link-copied",
        "leads inside the plugin",
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
    "a link to a package of the module's own from outside tests/ leads inside the plugin": (
        "runner-link-outside-tests",
        "the link skills/own_gate is left a link",
    ),
    "a link of tests/ to a folder of scripts/ that is itself a link is no runner's link": (
        "runner-link-to-a-link",
        "the link tests/own_gate is left a link",
    ),
    "a link of tests/ to a real folder scripts/constitution_layer_kit leads inside the plugin, beside the"
    " shared code the folder is": (
        "runner-link-constitution-layer-kit",
        "the link tests/constitution_layer_kit is left a link",
    ),
    "a link of tests/ to a package named with a leading _ leads inside the plugin": (
        "runner-link-underscore",
        "the link tests/_own_gate is left a link",
    ),
    "a link of tests/ to a folder of scripts/ with no __init__.py leads inside the plugin": (
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
    "a scan the source declares is run though the copy holds no document": (
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
    "a folder at scripts/constitution_layer_kit in the copy, the source's link to it arrived, is a finding": (
        "shared-code-folder",
        "holds scripts/constitution_layer_kit, a folder, shared code in a plugin",
    ),
    "a link at scripts/constitution_layer_kit in the copy is a finding, ahead of the link its source lacks": (
        "shared-code-link",
        "holds scripts/constitution_layer_kit, a link, shared code in a plugin",
    ),
    "a dangling link at scripts/constitution_layer_kit in the copy is a finding": (
        "shared-code-dangling",
        "holds scripts/constitution_layer_kit, a link, shared code in a plugin",
    ),
    "a file at scripts/constitution_layer_kit in the copy is a finding": (
        "shared-code-file",
        "holds scripts/constitution_layer_kit, a file, shared code in a plugin",
    ),
    "a hook given another event than its own is a finding": ("no-event", "exits 3"),
    "a shell scan that is red is a finding": ("scan-red", "check-x --scan"),
    "a Python scan that is red is a finding": ("py-scan-red", "check-p.py --scan"),
    "a red scan in an indented row is run, and is a finding": ("indented-scan-red", "check-x --scan"),
    "an explain with the mark is no scan, so none is run for it": ("explain-marked", ""),
}


UNREADABLE_ANCHOR = "on a line of its own — fix: restore the template's anchor, alone on its line"
UNREADABLE_CASES = {  # the source's document: its change, what the BROKEN line says
    "a source with no MODULE.md": ("no-document", "MODULE.md does not exist — fix: restore"),
    "a source whose document has no t9 anchor": (
        "no-t9",
        f'has no anchor <a id="t9"></a> {UNREADABLE_ANCHOR}',
    ),
    "a source whose t9 anchor has text on its line": (
        "t9-on-heading",
        f'has no anchor <a id="t9"></a> {UNREADABLE_ANCHOR}',
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


def link_cases(tally: Tally) -> None:
    """Each change of `LINK_CASES` over a source and its copy is green, or a finding that says what it is."""
    for name, (change, wanted) in LINK_CASES.items():
        got = [f.what for f in fixture_findings(change)]
        ok = got == [] if not wanted else len(got) >= 1 and all(wanted in g for g in got[:1])
        if (
            change == "runner-link-constitution-layer-kit"
        ):  # the folder is shared code, found ahead of the link
            ok = (
                len(got) == 2
                and "holds scripts/constitution_layer_kit, a folder" in got[0]
                and wanted in got[1]
            )
        if change == "no-hooks-file":
            ok = ok and len(got) == 1  # the file is missing; the hook the source names still runs in the copy
        if change == "inner-link":
            fixes = [f.fix for f in fixture_findings(change)]
            ok = ok and fixes[:1] == ["replace the link inside the plugin with the file it points at"]
        tally.failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"        got: {got}")


def unreadable_cases(tally: Tally) -> None:
    """Each source document that cannot be read is a teaching BROKEN line, never a scan left unrun."""
    for name, (change, said) in UNREADABLE_CASES.items():
        try:
            fixture_findings(change)
            ok, line = False, "no BROKEN"
        except Broken as broken:
            ok, line = said in str(broken), str(broken)
        tally.failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name} is a teaching BROKEN line, never a scan left unrun")
        if not ok:
            print(f"        got: {line}")


def scan_row_case(tally: Tally) -> None:
    """The scans a module declares are the rows it declares, read whatever their form."""
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
    tally.failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] a module's scans are the rows it declares, read whatever their form")


OFF_PIN = " [claude 2.1.286, not the pinned 2.1.282: CONSTITUTION_KIT_ANY_CLAUDE=1]"  # typed by hand


def report_cases(tally: Tally) -> None:
    """The report of one finding, of a run off the pin and of a green run is its literal text."""
    report_lines = [  # typed by hand: a message function cannot check itself
        "RED: const-x: its scan `check-x --scan` exits 2 on a bare repository (no output)",
        f"  why: {WHY}",
        "  fix: make the scan green, with a visible zero, where no constitution.yaml claims anything",
        "RED: 1 finding(s) — 1 hook(s), 2 scan(s)",
    ]
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        code = report("const-x", fixture_findings("scan-red"), "1 hook(s), 2 scan(s)")
    ok = code == EXIT_RED and printed.getvalue().splitlines() == report_lines
    tally.failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of one finding is its literal text, exit 2")
    if not ok:
        print(printed.getvalue())
    noted_lines = [  # a run off the pin: the note ends the headline line, not the why: and fix: lines
        f"RED: const-x: its scan `check-x --scan` exits 2 on a bare repository (no output){OFF_PIN}",
        f"  why: {WHY}",
        "  fix: make the scan green, with a visible zero, where no constitution.yaml claims anything",
        f"RED: 1 finding(s) — 1 hook(s), 2 scan(s){OFF_PIN}",
    ]
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        code = report("const-x", fixture_findings("scan-red"), "1 hook(s), 2 scan(s)", OFF_PIN)
    ok = code == EXIT_RED and printed.getvalue().splitlines() == noted_lines
    tally.failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the report of a run off the pin ends each headline line with the note")
    if not ok:
        print(printed.getvalue())
    green_lines = [  # typed by hand
        "GREEN: const-x installs and operates on a bare repository with its defaults — 1 hook(s), 2 scan(s)"
        " [claude 2.1.286, not the pinned 2.1.282: CONSTITUTION_KIT_ANY_CLAUDE=1]",
        "GREEN: const-x installs and operates on a bare repository with its defaults — 1 hook(s), 2 scan(s)",
    ]
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        code = report("const-x", [], "1 hook(s), 2 scan(s)", OFF_PIN)
        plain = report("const-x", [], "1 hook(s), 2 scan(s)")
    ok = code == plain == EXIT_GREEN and printed.getvalue().splitlines() == green_lines
    tally.failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the green report ends with the note off the pin, and with none on it")
    if not ok:
        print(printed.getvalue())


def marketplace_case(tally: Tally) -> None:
    """The marketplace's name is read from the kit's own file, and none is BROKEN."""
    with tempfile.TemporaryDirectory() as tmp:  # the marketplace's name is read from the kit's own file
        kit = Path(tmp) / "kit"
        (kit / ".claude-plugin").mkdir(parents=True)
        market = kit / ".claude-plugin" / "marketplace.json"
        market.write_text('{"name": "toy-mp", "plugins": []}', encoding="utf-8")
        ok = kit_marketplace(kit) == "toy-mp"
        market.write_text(
            '{"plugins": []}', encoding="utf-8"
        )  # no name: a BROKEN of the shared reader's line
        try:
            kit_marketplace(kit)
            unnamed = "no Broken"
        except Broken as broken:
            unnamed = str(broken)
        ok = ok and unnamed == (
            f'{market} has no "name" — fix: give the marketplace its name, at the top of the object'
        )
    tally.failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the marketplace's name is read from the kit's file, none is BROKEN")


# a fake claude that logs its arguments (to FAKE_LOG, else to the configuration folder; to FAKE_CALLS
# too, with its folder and configuration, when set), answers `--version` with FAKE_SAYS (printf's escapes
# read) and the exit FAKE_EXIT, hangs on FAKE_HANG, or on an install on FAKE_HANG_INSTALL, and answers
# an install with the text FAKE_INSTALL_OUT and the exit FAKE_INSTALL_EXIT after writing the record
# FAKE_RECORD, a plugin list with FAKE_LIST_OUT and FAKE_LIST_EXIT, each text as it stands; for
# `--version` it logs to FAKE_ENV, when set, its configuration folder, its auto-updater setting, how many
# entries the folder holds and whether it is a folder; to FAKE_CACHE, when set, each command's first two
# words and, in this order, the values of CLAUDE_CODE_PLUGIN_CACHE_DIR, CLAUDE_CODE_PLUGIN_SEED_DIR,
# CLAUDE_CODE_PLUGIN_DIRS, CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE, CLAUDE_CODE_PLUGIN_PREFER_HTTPS, FAKE_KEEP,
# CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS, CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE,
# CLAUDE_CODE_SYNC_PLUGIN_INSTALL, CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS, FORCE_AUTOUPDATE_PLUGINS,
# CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL and CLAUDE_CODE_PLUGIN_DIR_WATCH it holds
# (`absent` when unset), each after a `|`; to FAKE_PATHS, when set, each command's first two words and the
# first folder of its PATH, after a `|`; and it writes the record where the platform does, in
# CLAUDE_CODE_PLUGIN_CACHE_DIR's folder when it is set, else in the configuration's plugins/
FAKE_CLAUDE = (
    '#!/bin/sh\necho "$*" >> "${FAKE_LOG:-$CLAUDE_CONFIG_DIR/fake.log}"\n'
    '[ -n "$FAKE_PATHS" ] && echo "$1 $2|${PATH%%:*}" >> "$FAKE_PATHS"\n'
    '[ -n "$FAKE_CALLS" ] && echo "$* | $PWD | $CLAUDE_CONFIG_DIR" >> "$FAKE_CALLS"\n'
    '[ "$1" = --version ] && [ -n "$FAKE_ENV" ] && echo "$CLAUDE_CONFIG_DIR|$DISABLE_AUTOUPDATER|'
    '$(ls -A "$CLAUDE_CONFIG_DIR" | wc -l | tr -d " ")|'
    '$([ -d "$CLAUDE_CONFIG_DIR" ] && echo dir)" >> "$FAKE_ENV"\n'
    '[ -n "$FAKE_CACHE" ] && echo "$1 $2|${CLAUDE_CODE_PLUGIN_CACHE_DIR-absent}|'
    "${CLAUDE_CODE_PLUGIN_SEED_DIR-absent}|${CLAUDE_CODE_PLUGIN_DIRS-absent}|"
    "${CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE-absent}|${CLAUDE_CODE_PLUGIN_PREFER_HTTPS-absent}|"
    "${FAKE_KEEP-absent}|${CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS-absent}|"
    "${CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE-absent}|${CLAUDE_CODE_SYNC_PLUGIN_INSTALL-absent}|"
    "${CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS-absent}|${FORCE_AUTOUPDATE_PLUGINS-absent}|"
    "${CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL-absent}|"
    '${CLAUDE_CODE_PLUGIN_DIR_WATCH-absent}" >> "$FAKE_CACHE"\n'
    '[ -n "$FAKE_HANG" ] && exec tail -f /dev/null\n'
    '[ "$1" = --version ] && { printf \'%b\' "$FAKE_SAYS"; exit "${FAKE_EXIT:-0}"; }\n'
    '[ "$2" = install ] && [ -n "$FAKE_HANG_INSTALL" ] && exec tail -f /dev/null\n'
    '[ "$2" = install ] && {\n'
    '  root="${CLAUDE_CODE_PLUGIN_CACHE_DIR:-$CLAUDE_CONFIG_DIR/plugins}"\n'
    '  [ -n "$FAKE_RECORD" ] && mkdir -p "$root" &&\n'
    '    printf \'%s\' "$FAKE_RECORD" > "$root/installed_plugins.json"\n'
    '  printf \'%s\' "$FAKE_INSTALL_OUT"; exit "${FAKE_INSTALL_EXIT:-0}"; }\n'
    '[ "$2" = list ] && { printf \'%s\' "$FAKE_LIST_OUT"; exit "${FAKE_LIST_EXIT:-0}"; }\n'
    "exit 0\n"
)


BARE_HOOK: dict[str, object] = {"type": "command", "command": "true"}
BARE_RUN = Hook("PreToolUse", "", "true", (), 600.0)  # what `hooks_of` makes of BARE_HOOK
HookShape = tuple[str, str | bytes | OSError, list[Hook] | str | tuple[str, str]]

HOOKS_NOT_FOUND = (  # typed by hand; the folder is the one the fix names
    "BROKEN {path} cannot be looked up ({why}) — fix: make its folder {folder} searchable (its"
    " permissions), so that the check can find hooks/hooks.json and read each hook it runs"
)


def hook_waits_of(hooked: Path, hooks: dict[str, list[dict[str, object]]]) -> dict[str, float]:
    """The seconds `hooks_of` gives each hook of a hooks file with one hook per event."""
    table = {event: [{"hooks": [hook]}] for event, hook in ((e, h[0]) for e, h in hooks.items())}
    (hooked / "hooks" / "hooks.json").write_text(json.dumps({"hooks": table}), encoding="utf-8")
    return {hook.event: hook.timeout for hook in hooks_of(hooked)}


def single_hook_file(hook: object, **group: object) -> str:
    """A hooks file with one event, one group (with the keys of `group`) and one hook."""
    return json.dumps({"hooks": {"PreToolUse": [{"hooks": [hook]} | group]}})


def whole_hooks_file(table: object) -> str:
    """A hooks file of the table, as it stands."""
    return json.dumps({"hooks": table})


def hook_default_wait_cases(tally: Tally, hooked: Path) -> None:
    """A hook with no timeout is waited for as the default of its event, one with a timeout for that."""
    for event, seconds in (  # typed by hand from the hooks reference, as read on 2026-10-08
        ("PreToolUse", 600.0),
        ("PostToolUse", 600.0),
        ("SessionStart", 600.0),
        ("Stop", 600.0),
        ("UserPromptSubmit", 30.0),
        ("PreModelSwitch", 30.0),
        ("PostModelSwitch", 30.0),
        ("MessageDisplay", 10.0),
        ("SessionEnd", 1.5),
        ("SomeEventTheKitDoesNotKnow", 600.0),
    ):
        got = hook_waits_of(hooked, {event: [BARE_HOOK]})
        version_case(
            tally,
            f"a {event} hook that declares no timeout is waited for {seconds:g} s",
            got == {event: seconds} and all(isinstance(s, float) for s in got.values()),
            str(got),
        )
    for event, declared in (
        ("PreToolUse", 5),
        ("UserPromptSubmit", 90),
        ("SessionEnd", 5),
        ("MessageDisplay", 2.5),
        ("SomeEventTheKitDoesNotKnow", 1),
    ):
        got = hook_waits_of(hooked, {event: [BARE_HOOK | {"timeout": declared}]})
        version_case(
            tally,
            f"a {event} hook that declares a timeout of {declared:g} is waited for {declared:g} s",
            got == {event: float(declared)},
            str(got),
        )
    got = hook_waits_of(
        hooked,
        {event: [BARE_HOOK] for event in ("PreToolUse", "SessionEnd")}
        | {"Stop": [BARE_HOOK | {"timeout": 7}]},
    )
    version_case(
        tally,
        "the hooks of a file are each waited for by their own event and timeout",
        got == {"PreToolUse": 600.0, "SessionEnd": 1.5, "Stop": 7.0},
        str(got),
    )


def hook_spied_wait_case(tally: Tally, hooked: Path) -> None:
    """`check_installed` hands `run` the wait `hooks_of` gives each hook, and no hook is run."""
    # The wait `hooks_of` computes is the one `check_installed` hands `run`: `run` is spied, and
    # answers at once, so that no hook runs and nothing is waited for.
    (hooked.parent / "MODULE.md").write_text('<a id="t9"></a>\n<a id="t10"></a>\n', encoding="utf-8")
    (hooked / "repo").mkdir()
    handed: dict[str, float] = {}

    def run_spy(
        argv: list[str],
        cwd: Path,
        env: dict[str, str],
        stdin: str = "",
        timeout: float = 300,
        fix: str = "",
    ) -> tuple[int, str, str]:
        """`run`, but the timeout of each hook is kept by its event, and the hook is not run."""
        handed[json.loads(stdin)["hook_event_name"]] = timeout
        return 0, "", ""

    hook_waits_of(
        hooked,
        {"PreToolUse": [BARE_HOOK | {"timeout": 5}], "UserPromptSubmit": [BARE_HOOK]}
        | {"Stop": [BARE_HOOK | {"timeout": 90}], "SessionEnd": [BARE_HOOK]},
    )
    with patched_globals({"run": run_spy}):
        found = check_installed("const-x", hooked, hooked, hooked / "repo", hooked / "data")
    version_case(
        tally,
        "`check_installed` runs each hook with the wait `hooks_of` gives it: the declared timeout"
        " (5, 90), else the event's (30, 1.5), no hook run",
        handed == {"PreToolUse": 5.0, "UserPromptSubmit": 30.0, "Stop": 90.0, "SessionEnd": 1.5}
        and found == [],
        f"{handed} {found}",
    )


def hook_shape_table(hooks_path: Path) -> list[HookShape]:
    """The shapes of a hooks file `hooks_of` reads: each a whole file and either the hooks it gives or the
    whole BROKEN line, typed by hand; nothing but `Broken` may be raised. A line that holds the
    interpreter's own words for the reason is a pair instead: the line's start and its end, with a reason
    of any wording between them."""
    shape_fix = (  # typed by hand
        " — fix: restore hooks/hooks.json to the shape the hooks reference gives, so that the check"
        " can read each hook it runs"
    )
    at = "event 'PreToolUse', group 1, hook 1"

    single, whole = single_hook_file, whole_hooks_file

    def not_hooks(detail: str) -> str:
        return f"BROKEN {hooks_path} is not a hooks file ({detail}){shape_fix}"

    def not_read(why: str) -> str:
        return (
            f"BROKEN {hooks_path} cannot be read ({why}) — fix: make it a readable file (its"
            f" permissions), or restore it with git checkout -- {hooks_path}, so that the check can"
            f" read each hook it runs"
        )

    def not_run(kind: str) -> str:
        return (
            f"BROKEN {hooks_path} holds a hook of type {kind} ({at}) that check-bare-install does"
            f" not run — it runs only `command` hooks, and cannot prove a hook it does not run —"
            f" fix: make it a `command` hook, or teach `hooks_of` and `check_installed` in"
            f" scripts/check-bare-install.py to run a {kind} hook"
        )

    cmd, one = BARE_HOOK, BARE_RUN
    long_int = "1" + "0" * 400  # no float holds it
    shapes: list[HookShape] = [
        ("a command hook runs", single(cmd), [one]),
        ("an http hook is BROKEN, not a skip", single({"type": "http", "url": "u"}), not_run("http")),
        (
            "an mcp_tool hook is BROKEN, not a skip",
            single({"type": "mcp_tool", "server": "s", "tool": "t"}),
            not_run("mcp_tool"),
        ),
        (
            "a prompt hook is BROKEN, not a skip",
            single({"type": "prompt", "prompt": "p"}),
            not_run("prompt"),
        ),
        (
            "an agent hook is BROKEN, not a skip",
            single({"type": "agent", "prompt": "p"}),
            not_run("agent"),
        ),
        (
            "a hook with no type",
            single({"command": "true"}),
            not_hooks(f'{at}: "type" is absent'),
        ),
        (
            "a hook of type shell",
            single({"type": "shell", "command": "true"}),
            not_hooks(f"""{at}: "type" is 'shell', not one of command, http, mcp_tool, prompt, agent"""),
        ),
        (
            "a hook of a type that is no string",
            single({"type": ["command"], "command": "true"}),
            not_hooks(f"""{at}: "type" is ['command'], not one of command, http, mcp_tool, prompt, agent"""),
        ),
        (
            "a command hook with no command",
            single({"type": "command"}),
            not_hooks(f'{at}: "command" is absent'),
        ),
        (
            "a command that is a number",
            single({"type": "command", "command": 7}),
            not_hooks(f'{at}: "command" is 7, not a string'),
        ),
        (
            "a command that is a list",
            single({"type": "command", "command": ["sh", "-c"]}),
            not_hooks(f"""{at}: "command" is ['sh', '-c'], not a string"""),
        ),
        ("args absent", single(cmd), [one]),
        ("args an empty list", single(cmd | {"args": []}), [one]),
        (
            "args a list of strings",
            single(cmd | {"args": ["a", "b"]}),
            [Hook("PreToolUse", "", "true", ("a", "b"), 600.0)],
        ),
        (
            "args a string",
            single(cmd | {"args": "x"}),
            not_hooks(f"""{at}: "args" is 'x', not a list of strings"""),
        ),
        (
            "args a list holding a number",
            single(cmd | {"args": ["a", 1]}),
            not_hooks(f"""{at}: "args" is ['a', 1], not a list of strings"""),
        ),
        (
            "args null",
            single(cmd | {"args": None}),
            not_hooks(f"""{at}: "args" is None, not a list of strings"""),
        ),
        ("timeout absent, the event's default", single(cmd), [one]),
        ("timeout 5", single(cmd | {"timeout": 5}), [replace(one, timeout=5.0)]),
        ("timeout 5.5", single(cmd | {"timeout": 5.5}), [replace(one, timeout=5.5)]),
        (
            "timeout 0 is a number and accepted",
            single(cmd | {"timeout": 0}),
            [replace(one, timeout=0.0)],
        ),
        (
            "timeout -1 is a number and accepted",
            single(cmd | {"timeout": -1}),
            [replace(one, timeout=-1.0)],
        ),
        (
            "timeout the string 5",
            single(cmd | {"timeout": "5"}),
            not_hooks(f"""{at}: "timeout" is '5', not a finite number of seconds"""),
        ),
        (
            "timeout true",
            single(cmd | {"timeout": True}),
            not_hooks(f'{at}: "timeout" is True, not a finite number of seconds'),
        ),
        (
            "timeout false",
            single(cmd | {"timeout": False}),
            not_hooks(f'{at}: "timeout" is False, not a finite number of seconds'),
        ),
        (
            "timeout null",
            single(cmd | {"timeout": None}),
            not_hooks(f'{at}: "timeout" is None, not a finite number of seconds'),
        ),
        (
            "timeout NaN",
            single(cmd | {"timeout": float("nan")}),
            not_hooks(f'{at}: "timeout" is nan, not a finite number of seconds'),
        ),
        (
            "timeout Infinity",
            single(cmd | {"timeout": float("inf")}),
            not_hooks(f'{at}: "timeout" is inf, not a finite number of seconds'),
        ),
        (
            "timeout -Infinity",
            single(cmd | {"timeout": float("-inf")}),
            not_hooks(f'{at}: "timeout" is -inf, not a finite number of seconds'),
        ),
        (
            "timeout an integer no float holds",
            '{"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "true", "timeout": '
            + long_int
            + "}]}]}}",
            not_hooks(f'{at}: "timeout" is {long_int[:200]}…, not a finite number of seconds'),
        ),
        (
            "timeout a list",
            single(cmd | {"timeout": [5]}),
            not_hooks(f'{at}: "timeout" is [5], not a finite number of seconds'),
        ),
        (
            "a hooks key that is a list",
            '{"hooks": []}',
            not_hooks('"hooks" is [], not an object of events'),
        ),
        (
            "an event whose value is no list",
            whole({"PreToolUse": {}}),
            not_hooks("event 'PreToolUse': {} is no list of groups"),
        ),
        (
            "a group that is no object",
            whole({"PreToolUse": ["x"]}),
            not_hooks("event 'PreToolUse', group 1: 'x' is no object"),
        ),
        (
            "a group without hooks",
            whole({"PreToolUse": [{"matcher": "Write"}]}),
            not_hooks("event 'PreToolUse', group 1: no \"hooks\" key"),
        ),
        (
            "a group whose hooks are no list",
            whole({"PreToolUse": [{"hooks": {}}]}),
            not_hooks("event 'PreToolUse', group 1: \"hooks\" is {}, not a list"),
        ),
        (
            "a hook that is a string",
            whole({"PreToolUse": [{"hooks": ["true"]}]}),
            not_hooks(f"{at}: 'true' is no object"),
        ),
        (
            "a matcher that is a number",
            single(cmd, matcher=7),
            not_hooks("event 'PreToolUse', group 1: \"matcher\" is 7, not a string"),
        ),
        (
            "a matcher that is null",
            single(cmd, matcher=None),
            not_hooks("event 'PreToolUse', group 1: \"matcher\" is None, not a string"),
        ),
        (
            "a matcher that is 0",
            single(cmd, matcher=0),
            not_hooks("event 'PreToolUse', group 1: \"matcher\" is 0, not a string"),
        ),
        (
            "a matcher that is an empty list",
            single(cmd, matcher=[]),
            not_hooks("event 'PreToolUse', group 1: \"matcher\" is [], not a string"),
        ),
        (
            "a matcher that is an empty object",
            single(cmd, matcher={}),
            not_hooks("event 'PreToolUse', group 1: \"matcher\" is {}, not a string"),
        ),
        (
            "a matcher that is false",
            single(cmd, matcher=False),
            not_hooks("event 'PreToolUse', group 1: \"matcher\" is False, not a string"),
        ),
        (
            "a matcher that is the empty string is a string and accepted",
            single(cmd, matcher=""),
            [one],
        ),
        ("a matcher that is a string", single(cmd, matcher="Write"), [replace(one, matcher="Write")]),
        (
            "the second hook of the second group is named by its place",
            whole({"Stop": [{"hooks": [cmd]}, {"hooks": [cmd, {"type": "command"}]}]}),
            not_hooks("event 'Stop', group 2, hook 2: \"command\" is absent"),
        ),
        (
            "hooks come in the order of the file: events, groups, hooks",
            whole(
                {
                    "Stop": [
                        {"matcher": "m", "hooks": [cmd | {"command": "a"}, cmd | {"command": "b"}]},
                        {"hooks": [cmd | {"command": "c"}]},
                    ],
                    "PreToolUse": [{"hooks": [cmd | {"command": "d"}]}],
                }
            ),
            [
                Hook("Stop", "m", "a", (), 600.0),
                Hook("Stop", "m", "b", (), 600.0),
                Hook("Stop", "", "c", (), 600.0),
                Hook("PreToolUse", "", "d", (), 600.0),
            ],
        ),
        (
            "a hooks file that is not JSON",
            "not json",
            not_hooks("Expecting value: line 1 column 1 (char 0)"),
        ),
        ("a top level that is a list", "[]", not_hooks("the top level is [], not a JSON object")),
        ("a top level without hooks", "{}", not_hooks('the top level has no "hooks" key')),
        (
            "a file that is not UTF-8",
            b"\xff",
            not_hooks("'utf-8' codec can't decode byte 0xff in position 0: invalid start byte"),
        ),
        (
            "a value with a line break is quoted on one line",
            whole({"Pre\nTool": [{"hooks": [cmd | {"command": "a\nb", "timeout": "5\n6"}]}]}),
            not_hooks(
                "event 'Pre\\nTool', group 1, hook 1:"
                """ "timeout" is '5\\n6', not a finite number of seconds"""
            ),
        ),
        (
            "a file nested too deep to be read",
            "[" * 100000,
            (f"BROKEN {hooks_path} is not a hooks file (", f"){shape_fix}"),
        ),
        # A file that is there and cannot be read: the read is made to raise (a chmod alone would
        # not hold when run as root), and the line is its own, never the shape fix.
        (
            "a hooks file that is denied",
            PermissionError(13, "Permission denied"),
            not_read("Permission denied"),
        ),
        (
            "a hooks file with an I/O error",
            OSError(5, "Input/output error"),
            not_read("Input/output error"),
        ),
    ]
    return shapes


def hooks_file_shape_cases(tally: Tally, hooked: Path) -> None:
    """Each shape of a hooks file is read as the table says; nothing but `Broken` may be raised."""
    hooks_path = hooked / "hooks" / "hooks.json"
    for name, text, want in hook_shape_table(hooks_path):
        reading: contextlib.AbstractContextManager[object] = contextlib.nullcontext()
        if isinstance(text, OSError):
            hooks_path.write_text("{}", encoding="utf-8")  # the file is there; the read fails
            reading = mock.patch.object(Path, "read_text", side_effect=text)
        elif isinstance(text, bytes):
            hooks_path.write_bytes(text)
        else:
            hooks_path.write_text(text, encoding="utf-8")
        try:
            with reading:
                got_shape: list[Hook] | str = hooks_of(hooked)
        except Broken as broken:
            got_shape = f"BROKEN {broken}"
        except Exception as other:  # any other is the defect this table holds
            got_shape = f"raised {type(other).__name__}: {other}"
        if isinstance(want, tuple):
            start, end = want
            got_text = got_shape if isinstance(got_shape, str) else ""
            shape_ok = (
                got_text.startswith(start)
                and got_text.endswith(end)
                and len(got_text) > len(start) + len(end)
            )
        else:
            shape_ok = got_shape == want
        version_case(tally, f"hooks file: {name}", shape_ok, str(got_shape))


def hooks_folder_case(tally: Tally) -> None:
    """A folder in the hooks file's place gives no hooks, as a missing file does."""
    with tempfile.TemporaryDirectory() as other_tmp:  # a real folder, nothing mocked
        (Path(other_tmp) / "hooks" / "hooks.json").mkdir(parents=True)
        try:
            got_folder: list[Hook] | str = hooks_of(Path(other_tmp))
        except Exception as other:  # a Broken here too is the defect this case holds
            got_folder = f"raised {type(other).__name__}: {other}"
        version_case(
            tally,
            "hooks file: a folder in its place gives no hooks, as a missing file does",
            got_folder == [],
            str(got_folder),
        )


def hook_lookup_cases(tally: Tally, hooked: Path) -> None:
    """A hooks file whose place cannot be looked up is the line naming the folder to open."""
    hooks_path = hooked / "hooks" / "hooks.json"
    # A hooks file whose place cannot be looked up (its folder cannot be searched, an I/O error):
    # the lookup `Path.stat` makes is made to raise, and the line is its own, since the file's
    # permissions and `git checkout` do not mend a folder that cannot be searched. `Path.is_file` is
    # made to return False meanwhile, as it does from release 3.14 on, so that a lookup made by it
    # fails here on every Python, as it does on 3.14 for the real folder below.
    for name, lookup, why in (
        (
            "a hooks folder that cannot be searched",
            PermissionError(13, "Permission denied"),
            "Permission denied",
        ),
        (
            "a hooks file whose lookup has an I/O error",
            OSError(5, "Input/output error"),
            "Input/output error",
        ),
    ):
        try:
            with (
                mock.patch.object(Path, "stat", side_effect=lookup),
                mock.patch.object(Path, "is_file", return_value=False),
            ):
                got_lookup: list[Hook] | str = hooks_of(hooked)
        except Broken as broken:
            got_lookup = f"BROKEN {broken}"
        except Exception as other:  # any other is the defect this case holds
            got_lookup = f"raised {type(other).__name__}: {other}"
        version_case(
            tally,
            f"hooks file: {name}",
            got_lookup == HOOKS_NOT_FOUND.format(path=hooks_path, why=why, folder=hooks_path.parent),
            str(got_lookup),
        )


def hook_link_cases(tally: Tally) -> None:
    """What stands at hooks/hooks.json, real and nothing mocked, is a hooks file or none."""
    # What stands at hooks/hooks.json, real and nothing mocked: a dangling link, a link to itself (a
    # loop) and a path through a file are no hooks file, as a missing file is none; a link to a folder
    # is no regular file; a link to a regular file is that file, read.
    for name, kind, want_links in (
        ("a dangling link", "dangling", []),
        ("a link loop", "loop", []),
        ("a path through a file", "through a file", []),
        ("a link to a folder", "to a folder", []),
        ("a link to a regular file", "to a file", [BARE_RUN]),
    ):
        with tempfile.TemporaryDirectory() as link_tmp:
            link_root = Path(link_tmp)
            link_place = link_root / "hooks" / "hooks.json"
            if kind == "through a file":
                (link_root / "hooks").write_text("", encoding="utf-8")  # hooks is a file
            else:
                (link_root / "hooks").mkdir()
                if kind == "dangling":
                    link_place.symlink_to("nowhere.json")
                elif kind == "loop":
                    link_place.symlink_to("hooks.json")  # itself
                elif kind == "to a folder":
                    (link_root / "real").mkdir()
                    link_place.symlink_to("../real")
                else:
                    (link_root / "real.json").write_text(single_hook_file(BARE_HOOK), encoding="utf-8")
                    link_place.symlink_to("../real.json")
            try:
                got_link: list[Hook] | str = hooks_of(link_root)
            except Exception as other:  # a Broken here too is the defect this case holds
                got_link = f"raised {type(other).__name__}: {other}"
            version_case(tally, f"hooks file: {name} at its place", got_link == want_links, str(got_link))


def hook_shut_case(tally: Tally) -> None:
    """A real hooks folder that cannot be searched is the line naming it (not as root)."""
    if os.geteuid() != 0:  # root searches any folder: there, the mocked cases above are the proof
        with tempfile.TemporaryDirectory() as shut_tmp:
            shut = Path(shut_tmp) / "hooks"
            shut.mkdir()
            (shut / "hooks.json").write_text("{}", encoding="utf-8")
            shut.chmod(0o000)  # a real folder that cannot be searched; its mode is restored below
            try:
                got_shut: list[Hook] | str = hooks_of(Path(shut_tmp))
            except Broken as broken:
                got_shut = f"BROKEN {broken}"
            except Exception as other:  # any other is the defect this case holds
                got_shut = f"raised {type(other).__name__}: {other}"
            finally:
                shut.chmod(0o755)
            version_case(
                tally,
                "hooks file: a real hooks folder with no permissions is the line naming the folder",
                got_shut
                == HOOKS_NOT_FOUND.format(path=shut / "hooks.json", why="Permission denied", folder=shut),
                str(got_shut),
            )


def hook_wait_cases(tally: Tally) -> None:
    """A hook that declares no timeout is waited for as the platform gives its event; one that declares
    a timeout, for that: read from the `Hook` that `hooks_of` builds, nothing is waited for. A hooks
    file `hooks_of` cannot run, in each shape, is one BROKEN line and never another exception; one that
    is a regular file and cannot be read (a denied read, an I/O error) has a line and fix of its own, and
    so has one whose place cannot be looked up (a folder that cannot be searched, an I/O error)."""
    with tempfile.TemporaryDirectory() as tmp:
        hooked = Path(tmp) / "plugin"  # a source: the plugin folder, its module's document beside it
        (hooked / "hooks").mkdir(parents=True)
        hook_default_wait_cases(tally, hooked)
        hook_spied_wait_case(tally, hooked)
        hooks_file_shape_cases(tally, hooked)
        hooks_folder_case(tally)
        hook_lookup_cases(tally, hooked)
        hook_link_cases(tally)
        hook_shut_case(tally)


TYPED_RUN_FIX = (
    "give it a command that exists and can run, with no NUL byte in it or its arguments: a program on"
    " PATH, or a file with the execute permission (`chmod u+x` it), then run the check again"
)
TYPED_HOOK_FIX = (
    'give the hook\'s "command" and "args" in the module\'s hooks/hooks.json a command that'
    " exists and can run, with no NUL byte in it or its arguments: a program on PATH, or a file of"
    " the module with the execute permission (`chmod u+x` it, and commit the mode), then run the"
    " check again"
)


def result_of(call: Callable[[], object]) -> str:
    """What the call does: its result, or the BROKEN line it raises, or the other exception."""
    try:
        return f"returned {call()!r}"
    except Broken as bad:
        return f"BROKEN: {bad}"
    except Exception as other:  # any other is the defect these cases hold
        return f"raised {type(other).__name__}: {other}"


def cannot_search(path: Path, folder: Path) -> str:
    """The line for a path under a folder that refuses the search, typed by hand."""
    return (
        f"BROKEN: {path} cannot be searched (Permission denied) — fix: give the folder {folder}"
        f" search permission, `chmod u+rx '{folder}'`, then run the check again"
    )


def declared_of(plugin_at: Path) -> str:
    return result_of(lambda: declared_scans(plugin_at))


def started(argv: list[str]) -> str:
    return result_of(lambda: run(argv, Path.cwd(), dict(os.environ)))


# A folder the walks cannot list, and a file they cannot read: the walks (`files_under`, the
# source's and the copy's links in `link_findings`, a link's target folder, `counted`) each give one
# BROKEN line naming the folder, the same on every Python (`Path.rglob` raises on one and lists
# nothing on the other), and the byte comparisons of `link_findings` (a folder link's files, its
# differing files, a file link) one naming the file. The listing and the read are made to raise
# here, so that the cases hold as root too; the real folder and file of mode 000 follow below. No
# existing case fits: the walk cases above hold an entry that cannot be looked at, in a folder that
# lists, and the read cases a hooks file; these two failures are new.
def cannot_list(folder: Path) -> str:
    return (
        f"BROKEN: {folder} cannot be listed (Permission denied) — fix: give the folder {folder}"
        f" search permission, `chmod u+rx {shlex.quote(str(folder))}`, then run the check again"
    )


def cannot_read(path: Path, installed: bool) -> str:
    fix = (
        "run the check again, and if it repeats, report that the install wrote a file the check"
        " cannot read, at the version the kit pins"
        if installed
        else f"give the file read permission, `chmod u+r {shlex.quote(str(path))}`, then run the check again"
    )
    return f"BROKEN: {path} cannot be read (Permission denied) — fix: {fix}"


def walk_fixtures(root: Path, bad: Path) -> list[tuple[str, Callable[[], object]]]:
    """The walk sites, each reaching the folder `bad`: as the source, as the copy, as a link's target,
    and in the count."""
    empty = root / "empty copy"
    links_source = root / "links source"
    target_source, target_copy = root / "target source", root / "target copy"
    for folder in (empty, links_source, target_source, target_copy):
        folder.mkdir(parents=True)
    (links_source / "ln.txt").symlink_to("../outside.txt")
    (target_source / "shared").symlink_to(bad)
    (target_copy / "shared").mkdir()
    return [
        ("files_under", lambda: files_under(bad)),
        ("the source's links", lambda: link_findings("m", bad, empty)),
        ("the copy's extra links", lambda: link_findings("m", links_source, bad)),
        ("a link's target folder", lambda: link_findings("m", target_source, target_copy)),
        ("the count of the source", lambda: counted(bad)),
    ]


def bytes_fixture(root: Path) -> tuple[Path, Path, Path]:
    """A source with a link to a folder of two files and a link to a file, and a copy that holds the
    same bytes: the source, the copy, and the folder the first link leads to (its `locked.txt` is the
    file the cases make unreadable)."""
    folder = root / "shared dir"
    folder.mkdir(parents=True)
    (folder / "a.txt").write_text("a", encoding="utf-8")
    (folder / "locked.txt").write_text("l", encoding="utf-8")
    (root / "outside.txt").write_text("o", encoding="utf-8")
    source = root / "source"
    (source / "scripts").mkdir(parents=True)
    (source / "scripts" / "shared").symlink_to(folder)
    (source / "scripts" / "one.txt").symlink_to("../../outside.txt")
    copy = root / "copy"
    shutil.copytree(folder, copy / "scripts" / "shared")
    shutil.copy(root / "outside.txt", copy / "scripts" / "one.txt")
    return source, copy, folder


def run_start_cases(tally: Tally) -> None:
    """`run` turns a command that cannot start into one BROKEN line naming it, with the right fix."""
    for name, raised, why in (
        ("a PermissionError", PermissionError(13, "Permission denied"), "Permission denied"),
        ("an OSError of another kind", OSError(8, "Exec format error"), "Exec format error"),
        ("an OSError with no reason", OSError("odd"), "odd"),
        ("a NotADirectoryError", NotADirectoryError(20, "Not a directory"), "Not a directory"),
        ("a ValueError", ValueError("embedded null byte"), "embedded null byte"),
    ):
        with mock.patch("subprocess.run", side_effect=raised):
            got_start = started(["tool", "-x"])
        version_case(
            tally,
            f"run: {name} of starting a command is one BROKEN line naming the command",
            got_start
            == f"BROKEN: the command ['tool', '-x'] could not be started ({why}) — fix: {TYPED_RUN_FIX}",
            got_start,
        )
    with mock.patch("subprocess.run", side_effect=FileNotFoundError(2, "No such file or directory")):
        got_start = started(["tool"])
    version_case(
        tally,
        "run: a command that is not found is the line it was, install it",
        got_start
        == "BROKEN: tool is not installed (No such file or directory) — fix: install it and put it on"
        " PATH",
        got_start,
    )
    with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["tool"], 5)):
        got_start = started(["tool"])
    version_case(
        tally,
        "run: a command that outlasts its time is still the exit 124",
        got_start == "returned (124, '', 'timed out after 300 s')",
        got_start,
    )
    with tempfile.TemporaryDirectory() as run_tmp:
        plain = Path(run_tmp) / "plain"
        plain.write_text("#!/bin/sh\n", encoding="utf-8")
        plain.chmod(0o644)
        got_start = result_of(lambda: run([str(plain)], Path(run_tmp), dict(os.environ)))
        version_case(
            tally,
            "run: a file with no execute permission is one BROKEN line naming it",
            got_start
            == f"BROKEN: the command [{str(plain)!r}] could not be started (Permission denied) — fix:"
            f" {TYPED_RUN_FIX}",
            got_start,
        )
    got_start = started(["a\0b"])
    version_case(
        tally,
        "run: a command holding a NUL byte is one BROKEN line naming it, escaped",
        got_start == f"BROKEN: the command ['a\\x00b'] could not be started (embedded null byte) — fix:"
        f" {TYPED_RUN_FIX}",
        got_start,
    )
    got_start = started(["a\0b" + "x" * 300])
    cut_at = repr(["a\0b" + "x" * 300])[:200]
    version_case(
        tally,
        "run: a long command is cut at 200 characters, as every quoted reply is",
        got_start
        == f"BROKEN: the command {cut_at}… could not be started (embedded null byte) — fix: {TYPED_RUN_FIX}",
        got_start,
    )
    got_start = started([""])  # a PermissionError here, a missing file on Linux: both name the command
    version_case(
        tally,
        "run: an empty command is one BROKEN line, never a traceback",
        got_start
        in (
            f"BROKEN: the command [''] could not be started (Permission denied) — fix: {TYPED_RUN_FIX}",
            "BROKEN: '' is not installed (No such file or directory) — fix: install it and put it on PATH",
        ),
        got_start,
    )
    # A command that is not found is echoed as `shown` quotes it when it is no plain word, so that a
    # space, a quote or a line break reads as one token; a working folder that does not exist is its own
    # cause, whichever command is asked for. Both are real, no process mocked.
    got_start = started(["my tool's\nname"])
    version_case(
        tally,
        "run: a command with a space, a quote and a line break, not found, is quoted as one token",
        got_start
        == 'BROKEN: "my tool\'s\\nname" is not installed (No such file or directory) — fix: install it'
        " and put it on PATH",
        got_start,
    )
    with tempfile.TemporaryDirectory() as gone_tmp:
        gone = Path(gone_tmp) / "gone dir"
        no_folder = (
            f"BROKEN: the working folder {gone} does not exist — fix: make the folder"
            f" (`mkdir -p '{gone}'`), then run the check again"
        )
        for name, argv in (
            ("an existing command", ["sh", "-c", "true"]),
            ("a missing one", ["no-such-tool"]),
        ):
            got_start = result_of(partial(run, argv, gone, dict(os.environ)))
            version_case(
                tally,
                f"run: a working folder that does not exist is named, not {name} read as not installed",
                got_start == no_folder,
                got_start,
            )
    with tempfile.TemporaryDirectory() as hook_tmp:  # a hook run through check_installed has the hook's fix
        hooked_root = Path(hook_tmp) / "plugin"  # the source, its module's document beside it
        (hooked_root / "hooks").mkdir(parents=True)
        (hooked_root / "repo").mkdir()
        (hooked_root.parent / "MODULE.md").write_text('<a id="t9"></a>\n<a id="t10"></a>\n', encoding="utf-8")
        nul_hook = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "\0tool", "args": []}]}]}}
        (hooked_root / "hooks" / "hooks.json").write_text(json.dumps(nul_hook), encoding="utf-8")
        got_start = result_of(
            lambda: check_installed("m", hooked_root, hooked_root, hooked_root / "repo", hooked_root)
        )
        version_case(
            tally,
            "run: a hook whose command cannot be started is one BROKEN line with the hook's own fix",
            got_start == f"BROKEN: the command ['\\x00tool'] could not be started (embedded null byte) — fix:"
            f" {TYPED_HOOK_FIX}",
            got_start,
        )


def lookup_cases(tally: Tally) -> None:
    """A path that cannot be looked at is one BROKEN line, a missing one keeps its meaning."""
    # A missing path keeps its meaning at each site; a NUL in a name, a link loop and a path through a
    # file are missing paths too, as `Path.exists` has them.
    with tempfile.TemporaryDirectory() as miss_tmp:
        miss_root = Path(miss_tmp)
        (miss_root / "empty").mkdir()
        (miss_root / "loop").mkdir()
        (miss_root / "loop" / "MODULE.md").symlink_to("MODULE.md")
        (miss_root / "afile").write_text("", encoding="utf-8")
        no_doc = "BROKEN: {} does not exist — fix: restore the module's document, which declares its scans"
        for name, plugin_at in (
            ("a folder with no document", miss_root / "empty"),
            ("a document that is a link loop", miss_root / "loop"),
            ("a plugin that is a file, the document a path through it", miss_root / "afile"),
            ("a plugin that is no entry", miss_root / "nothing"),
        ):
            got_miss = declared_of(plugin_at)
            version_case(
                tally,
                f"lookups: {name} is the missing document it was",
                got_miss == no_doc.format(plugin_at / "MODULE.md"),
                got_miss,
            )
        version_case(
            tally,
            "lookups: a name that holds a NUL byte is a missing path, at every kind of lookup",
            not (
                there(Path("a\0b"))
                or file_at(Path("a\0b"))
                or folder_at(Path("a\0b"))
                or link_at(Path("a\0b"))
            ),
            "one of them found it",
        )
        toy_missing = miss_root / "kit"
        toy_missing.mkdir()
        with patched_globals({"KIT": toy_missing}):
            got_miss = result_of(lambda: check_module("m", str(miss_root), Note("2.1.282")))
        version_case(
            tally,
            "lookups: a module with no plugin.json is the line it was",
            got_miss
            == "BROKEN: no module m in the kit — fix: name a folder under modules/ that holds a plugin",
            got_miss,
        )
        with (
            patched_globals({"claude_noted": mock.Mock(side_effect=Broken("stopped here"))}),
            contextlib.redirect_stdout(io.StringIO()) as printed_miss,
        ):
            status_miss = main(["--module", "m", "--from", str(miss_root / "nothing")])
        version_case(
            tally,
            "lookups: a source that is no entry goes on as a remote, as it did",
            (status_miss, printed_miss.getvalue().splitlines())
            == (
                EXIT_BROKEN,
                ["BROKEN: stopped here", "BROKEN: the check could not run — 0 modules examined"],
            ),
            f"{status_miss} {printed_miss.getvalue()}",
        )
    with tempfile.TemporaryDirectory() as odd_tmp:  # an error that is no search permission: the other fix
        odd = Path(odd_tmp) / "odd plugin"
        odd.mkdir()
        with mock.patch.object(Path, "stat", side_effect=OSError(5, "Input/output error")):
            got_odd = result_of(lambda: declared_scans(odd))
        version_case(
            tally,
            "lookups: an I/O error is one BROKEN line, its fix to read why the folder is not searchable",
            got_odd == f"BROKEN: {odd / 'MODULE.md'} cannot be searched (Input/output error) — fix: make the"
            f" folder {odd} searchable, `ls -ld '{odd}'` shows why not, then run the check again",
            got_odd,
        )


def walk_list_cases(tally: Tally) -> None:
    """A subfolder that cannot be listed is one BROKEN line naming it, at every walk site."""
    with tempfile.TemporaryDirectory() as list_tmp:
        list_root = Path(list_tmp).resolve()
        walked = list_root / "walked folder"
        closed_sub = walked / "closed sub"
        closed_sub.mkdir(parents=True)
        (walked / "f.txt").write_text("f", encoding="utf-8")
        real_scandir = os.scandir

        def scandir_denying(path: str | os.PathLike[str] | None = None) -> object:
            if path is not None and os.fspath(path) == str(closed_sub):
                raise PermissionError(errno.EACCES, "Permission denied", str(closed_sub))
            return real_scandir(path)

        for name, call in walk_fixtures(list_root, walked):
            with mock.patch.object(os, "scandir", scandir_denying):
                got_list = result_of(call)
            version_case(
                tally,
                f"walks: a subfolder that cannot be listed ({name}) is one BROKEN line naming it",
                got_list == cannot_list(closed_sub),
                got_list,
            )


def read_denied_cases(tally: Tally) -> None:
    """A file that cannot be read is one BROKEN line naming it, at every byte comparison."""
    with tempfile.TemporaryDirectory() as bytes_tmp:
        bytes_root = Path(bytes_tmp).resolve()
        bytes_source, bytes_copy, shared_dir = bytes_fixture(bytes_root)
        copied_locked = bytes_copy / "scripts" / "shared" / "locked.txt"
        real_read = Path.read_bytes

        def read_denying(blocked: Path) -> contextlib.AbstractContextManager[object]:
            def read_bytes(self: Path) -> bytes:
                if self == blocked:
                    raise PermissionError(errno.EACCES, "Permission denied")
                return real_read(self)

            return mock.patch.object(Path, "read_bytes", read_bytes)

        got_bytes = result_of(lambda: link_findings("m", bytes_source, bytes_copy))
        version_case(
            tally, "reads: the copy and the source compared are green", got_bytes == "returned []", got_bytes
        )
        for name, blocked, installed in (
            ("a folder link's file of the source", shared_dir / "locked.txt", False),
            ("a folder link's file of the copy", copied_locked, True),
            ("a file link's file of the source", bytes_root / "outside.txt", False),
            ("a file link's file of the copy", bytes_copy / "scripts" / "one.txt", True),
        ):
            with read_denying(blocked):
                got_bytes = result_of(lambda: link_findings("m", bytes_source, bytes_copy))
            version_case(
                tally,
                f"reads: {name} that cannot be read is one BROKEN line naming it",
                got_bytes == cannot_read(blocked, installed),
                got_bytes,
            )
        (
            bytes_copy / "scripts" / "shared" / "a.txt"
        ).unlink()  # the trees differ: the differing files are named
        for name, blocked, installed in (
            ("a differing folder link's file of the source", shared_dir / "locked.txt", False),
            ("a differing folder link's file of the copy", copied_locked, True),
        ):
            with read_denying(blocked):
                got_bytes = result_of(lambda: link_findings("m", bytes_source, bytes_copy))
            version_case(
                tally,
                f"reads: {name} that cannot be read is one BROKEN line naming it",
                got_bytes == cannot_read(blocked, installed),
                got_bytes,
            )


def shut_folder_cases(tally: Tally) -> None:
    """The same cases over real folders and files of mode 000, which root would search."""
    with tempfile.TemporaryDirectory() as shut_tmp:
        shut_root = Path(shut_tmp).resolve()  # a link's target is resolved, so the folders are too
        closed = shut_root / "closed folder"
        document = closed / "deep" / "plugin"
        document.mkdir(parents=True)
        (document / "MODULE.md").write_text('<a id="t9"></a>\n<a id="t10"></a>\n', encoding="utf-8")
        (closed / "kit" / "modules" / "m" / "plugin" / ".claude-plugin").mkdir(parents=True)
        (closed / "kit" / "modules" / "m" / "plugin" / ".claude-plugin" / "plugin.json").write_text(
            "{}", encoding="utf-8"
        )
        (closed / "src").mkdir()
        (closed / "copy").mkdir()
        source_links = shut_root / "links"  # a source with a link to a file outside the module
        (source_links / "module").mkdir(parents=True)
        (shut_root / "links" / "outside.txt").write_text("o", encoding="utf-8")
        (source_links / "module" / "ln.txt").symlink_to("../outside.txt")
        listing = shut_root / "listing folder"  # a folder that lists but cannot be searched
        listing.mkdir()
        (listing / "f.txt").write_text("x", encoding="utf-8")
        hooks_source = shut_root / "hooks source" / "plugin"  # its module's document stands beside it
        hooks_copy = shut_root / "hooks copy"
        for tree in (hooks_source, hooks_copy):
            (tree / "hooks").mkdir(parents=True)
            (tree / "hooks" / "hooks.json").write_text('{"hooks": {}}', encoding="utf-8")
        (hooks_source.parent / "MODULE.md").write_text(
            '<a id="t9"></a>\n<a id="t10"></a>\n', encoding="utf-8"
        )
        (shut_root / "repo").mkdir()
        listing_json = json.dumps([{"id": "m@mp", "scope": "user", "installPath": str(document)}])
        walk, empty_copy = shut_root / "walk", shut_root / "empty copy"  # a subfolder that lists only
        (walk / "sub folder").mkdir(parents=True)
        (walk / "sub folder" / "y.txt").write_text("y", encoding="utf-8")
        empty_copy.mkdir()
        unlisted = shut_root / "unlisted folder"  # a subfolder that cannot be listed
        (unlisted / "closed sub").mkdir(parents=True)
        half = shut_root / "half root" / "half folder"  # a folder that lists but cannot be searched
        (half / "inner").mkdir(parents=True)
        (shut_root / "sites").mkdir()
        sites = walk_fixtures(shut_root / "sites", unlisted)
        real_source, real_copy, real_shared = bytes_fixture(shut_root / "real bytes")
        shut_modes = [
            (closed, 0o755),
            (listing, 0o755),
            (hooks_copy / "hooks", 0o755),
            (walk / "sub folder", 0o755),
            (unlisted / "closed sub", 0o755),
            (half, 0o755),
            (real_shared / "locked.txt", 0o644),
            (real_copy / "scripts" / "shared" / "locked.txt", 0o644),
        ]
        try:
            closed.chmod(0o000)
            listing.chmod(0o444)
            (walk / "sub folder").chmod(0o444)
            hooks_copy_hooks = hooks_copy / "hooks"
            hooks_copy_hooks.chmod(0o000)
            got_shut = result_of(lambda: declared_scans(document))
            version_case(
                tally,
                "lookups: a module document under a folder of mode 000 is one BROKEN line naming the"
                " folder to open",
                got_shut == cannot_search(document / "MODULE.md", closed),
                got_shut,
            )
            with patched_globals({"KIT": closed / "kit"}):
                got_shut = result_of(lambda: check_module("m", "owner/repo", Note("2.1.282")))
            version_case(
                tally,
                "lookups: a module's plugin.json under such a folder is the same line",
                got_shut
                == cannot_search(
                    closed / "kit" / "modules" / "m" / "plugin" / ".claude-plugin" / "plugin.json", closed
                ),
                got_shut,
            )
            with patched_globals({"run": lambda *args, **kwargs: (0, listing_json, "")}):
                got_shut = result_of(lambda: listed_install("m@mp", "user", shut_root, {}, Note("2.1.282")))
            version_case(
                tally,
                "lookups: an installPath under such a folder is the same line, not 'no folder'",
                got_shut == cannot_search(document, closed),
                got_shut,
            )
            with (
                patched_globals({"claude_noted": mock.Mock(side_effect=Broken("stopped here"))}),
                contextlib.redirect_stdout(io.StringIO()) as printed_shut,
            ):
                status_shut = main(["--module", "m", "--from", str(closed / "src")])
            version_case(
                tally,
                "lookups: a --from source under such a folder is the same line, not a remote source",
                (status_shut, printed_shut.getvalue().splitlines())
                == (
                    EXIT_BROKEN,
                    [
                        cannot_search(closed / "src", closed),
                        "BROKEN: the check could not run — 0 modules examined",
                    ],
                ),
                f"{status_shut} {printed_shut.getvalue()}",
            )
            got_shut = result_of(lambda: link_findings("m", source_links / "module", closed / "copy"))
            version_case(
                tally,
                "lookups: a link's place in the copy under such a folder is the same line",
                got_shut == cannot_search(closed / "copy" / "ln.txt", closed),
                got_shut,
            )
            entry = walk / "sub folder" / "y.txt"  # an entry of a walk that cannot be looked at
            for name, call in (
                ("a source's links", lambda: link_findings("m", walk, empty_copy)),
                ("the copy's extra links", lambda: link_findings("m", source_links / "module", walk)),
                ("the count of the source", lambda: counted(walk)),
            ):
                got_shut = result_of(call)
                version_case(
                    tally,
                    f"lookups: an entry of a walk that cannot be looked at ({name}) is the same line",
                    got_shut == cannot_search(entry, walk / "sub folder"),
                    got_shut,
                )
            got_shut = result_of(lambda: files_under(listing))
            version_case(
                tally,
                "lookups: a file of a folder that lists but cannot be searched is the same line",
                got_shut == cannot_search(listing / "f.txt", listing),
                got_shut,
            )
            got_shut = result_of(
                lambda: check_installed("m", hooks_source, hooks_copy, shut_root / "repo", shut_root)
            )
            version_case(
                tally,
                "lookups: the copy's hooks file under a folder of mode 000 is the same line",
                got_shut == cannot_search(hooks_copy / "hooks" / "hooks.json", hooks_copy / "hooks"),
                got_shut,
            )
            hooks_copy_hooks.chmod(0o755)
            (hooks_source / "hooks").chmod(0o000)
            shut_modes.append((hooks_source / "hooks", 0o755))
            got_shut = result_of(
                lambda: check_installed("m", hooks_source, hooks_copy, shut_root / "repo", shut_root)
            )
            version_case(
                tally,
                "lookups: the source's hooks file under such a folder is the line `hooks_of` had",
                got_shut == f"BROKEN: {hooks_source / 'hooks' / 'hooks.json'} cannot be looked up (Permission"
                f" denied) — fix: make its folder {hooks_source / 'hooks'} searchable (its permissions),"
                " so that the check can find hooks/hooks.json and read each hook it runs",
                got_shut,
            )
            (unlisted / "closed sub").chmod(0o000)  # a real subfolder that cannot be listed
            for name, site_call in sites:
                got_shut = result_of(site_call)
                version_case(
                    tally,
                    f"walks: a real subfolder of mode 000 ({name}) is one BROKEN line naming it",
                    got_shut == cannot_list(unlisted / "closed sub"),
                    got_shut,
                )
            half.chmod(0o444)
            got_shut = result_of(lambda: files_under(half.parent))
            version_case(
                tally,
                "walks: a folder below one that lists but cannot be searched names the folder to open",
                got_shut
                == (
                    f"BROKEN: {half / 'inner'} cannot be listed (Permission denied) — fix: give the"
                    f" folder {half} search permission, `chmod u+rx {shlex.quote(str(half))}`, then run"
                    " the check again"
                ),
                got_shut,
            )
            locked_shared = real_shared / "locked.txt"
            locked_copy = real_copy / "scripts" / "shared" / "locked.txt"
            for name, locked, installed in (
                ("a real file of the source", locked_shared, False),
                ("a real file of the copy", locked_copy, True),
            ):
                locked.chmod(0o000)
                got_shut = result_of(lambda: link_findings("m", real_source, real_copy))
                locked.chmod(0o644)
                version_case(
                    tally,
                    f"reads: {name} of mode 000 under a folder link is one BROKEN line naming it",
                    got_shut == cannot_read(locked, installed),
                    got_shut,
                )
        finally:
            for folder_back, mode_back in shut_modes:
                folder_back.chmod(mode_back)


def start_and_lookup_cases(tally: Tally) -> None:
    """A command `run` cannot start and a path the check cannot look at are each one BROKEN line, never a
    traceback and never a missing path read in the place of one that cannot be searched: `run` turns any
    `OSError` of starting the command and a `ValueError` (a NUL byte) into a line naming the command, the
    reason and a fix (the hook's own where a hook is run), the not-found and timeout branches as they
    were; `file_at`, `folder_at`, `there` and `link_at` tell a missing path (no entry, a path through a
    file, a link loop, a NUL in the name), whose meaning each site keeps, from one that cannot be
    searched, a line naming the path and the folder to open, on every Python (`Path.is_file` and
    `exists` return False for it from release 3.14 on). No existing case fits: the hook cases read a
    hooks file, the bare-repository cases git's exits, and the rest a `claude`; the lookups are in
    different functions of the check, so this table is new; its real folders of mode 000 are skipped as
    root, which searches any folder."""
    run_start_cases(tally)
    lookup_cases(tally)
    walk_list_cases(tally)
    read_denied_cases(tally)
    if os.geteuid() == 0:  # root searches any folder: there, the cases above are the proof
        return
    shut_folder_cases(tally)


def bare_repository_cases(tally: Tally) -> None:
    """A git command of `bare_repository` that exits other than 0 is one BROKEN line naming it as
    `git <subcommand>` and a fix that can be followed (git ran, so "install git" is none); a missing
    git is `run`'s own line, unchanged. No existing case fits: the hook cases read a hooks file and the
    version cases a `claude`, so this one table is new. Any exit other than 0 counts (1, 2, 124, 128),
    and the line quotes the last line of the standard error, else of the standard output."""
    by_hand = "run {0} in a new repository by hand and read why it fails"
    init_line = "BROKEN: git init failed in the bare repository (fatal: simulated) — fix: " + by_hand.format(
        "git init"
    )
    add_line = "BROKEN: git add failed in the bare repository (fatal: simulated) — fix: " + by_hand.format(
        "git add"
    )
    commit_line = (
        "BROKEN: git commit failed in the bare repository (fatal: simulated) — fix: "
        + by_hand.format("git commit")
    )
    ran: list[list[str]] = []

    simulated = (1, "", "warning: x\nfatal: simulated")  # the exit, stdout and stderr of a failure

    def failing_at(word: str | None, failure: tuple[int, str, str]) -> Callable[..., tuple[int, str, str]]:
        def fake_run(
            argv: list[str], cwd: Path, env: dict[str, str], stdin: str = "", timeout: float = 300
        ) -> tuple[int, str, str]:
            """`run`, but nothing is run: every command exits 0, the one with `word` gives `failure`."""
            ran.append(argv)
            return failure if word in argv else (0, "", "")

        return fake_run

    def line_of(word: str | None, path: str | None = None, failure: tuple[int, str, str] = simulated) -> str:
        """The BROKEN line `bare_repository` raises with `run` giving `failure` at `word`, or `ok`; with
        `path`, the real `run` and that PATH."""
        ran.clear()
        with tempfile.TemporaryDirectory() as tmp:
            with patched_globals({"run": failing_at(word, failure)} if path is None else {}):
                with mock.patch.dict(os.environ, {} if path is None else {"PATH": path}):
                    try:
                        bare_repository(Path(tmp))
                    except Broken as broken:
                        return f"BROKEN: {broken}"
                    except Exception as other:  # any other is the defect this table holds
                        return f"raised {type(other).__name__}: {other}"
        return "ok"

    for name, word, want in (
        ("`git init` failing", "init", init_line),
        ("`git add` failing", "add", add_line),
        ("the `git -c … commit` failing is `git commit`, never `git -c`", "commit", commit_line),
    ):
        got_line = line_of(word)
        version_case(tally, f"bare repository: {name}", got_line == want, got_line)

    def failed(name: str, said: str) -> str:
        """The whole line of git command `name` failing with `said` as the last line it printed."""
        return f"BROKEN: git {name} failed in the bare repository ({said}) — fix: " + by_hand.format(
            f"git {name}"
        )

    # Any exit other than 0 is a failure (git's fatal is 128, `run`'s own timeout 124 with a message
    # of its own), at each of the three commands; and the last line quoted is the standard error's,
    # the standard output's only when the standard error is empty.
    for name in ("init", "add", "commit"):
        for code, said in ((128, "fatal: simulated"), (124, "timed out after 300 s"), (2, "error: x")):
            got_line = line_of(name, failure=(code, "", said))
            version_case(
                tally,
                f"bare repository: `git {name}` exiting {code}",
                got_line == failed(name, said),
                got_line,
            )
        got_line = line_of(name, failure=(1, "out one\nout last", "err one\nerr last"))
        version_case(
            tally,
            f"bare repository: `git {name}` printing on both streams quotes the standard error",
            got_line == failed(name, "err last"),
            got_line,
        )
        got_line = line_of(name, failure=(1, "out one\nout last", ""))
        version_case(
            tally,
            f"bare repository: `git {name}` printing on the standard output alone quotes it",
            got_line == failed(name, "out last"),
            got_line,
        )
    got_line = line_of(None)
    version_case(
        tally,
        "bare repository: no failure: the three commands, in their order",
        got_line == "ok"
        and ran
        == [
            ["git", "init", "-q", "-b", "main"],
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
        ],
        f"{got_line} {ran}",
    )
    with tempfile.TemporaryDirectory() as none_here:
        got_line = line_of(None, none_here)
    version_case(
        tally,
        "bare repository: git missing from PATH is run's own line, unchanged",
        got_line == "BROKEN: git is not installed (No such file or directory) — fix: install it and put it"
        " on PATH",
        got_line,
    )
    for argv, named in (
        (["git", "init", "-q", "-b", "main"], "git init"),
        (["git", "add", "-A"], "git add"),
        (["git", "-c", "user.name=a", "-c", "user.email=b", "commit", "-q"], "git commit"),
        (["git", "-C", "x", "status"], "git status"),
        (["git", "-c", "commit.gpgsign=false", "-C", "x", "-c", "a=b", "log"], "git log"),
        (["git", "--git-dir=x", "status"], "git status"),
        (["git", "--no-pager", "-p", "diff", "HEAD"], "git diff"),
        (["git", "-c", "status"], "git"),
        (["git", "-C"], "git"),
        (["git", "--version"], "git"),
        (["git"], "git"),
    ):
        try:
            got_name = git_command(argv)
        except Exception as other:  # any other is the defect this table holds
            got_name = f"raised {type(other).__name__}: {other}"
        version_case(tally, f"bare repository: {argv} is named {named!r}", got_name == named, got_name)


# the lines, typed by hand: a message function cannot check itself
STRICT = (
    "claude is {0}, and the kit's install checks read the platform as 2.1.282 writes it"
    " (scripts/claude-code.version) — fix: put Claude Code 2.1.282 first on PATH for this run:"
    " either run sh scripts/setup-claude.sh in the kit's clone, then the check through"
    " sh scripts/gate-list.sh --run install-<module>"
    " (--run session-<module> for the session check, --run guide for the guide's check), which puts"
    " it first, or install it beside your own by hand (npm install --prefix <folder>"
    " @anthropic-ai/claude-code@2.1.282, then PATH=<folder>/node_modules/.bin:$PATH), or set"
    " CONSTITUTION_KIT_ANY_CLAUDE=1 to run on"
    " {0} with a note on every headline line"
)
NOTED = " [claude {0}, not the pinned 2.1.282: CONSTITUTION_KIT_ANY_CLAUDE=1]"
REINSTALL = " — fix: check that `claude` on PATH is Claude Code (`command -v claude`), and reinstall it"


# typed by hand, a constant cannot check itself: the four variables `claude_env` removes, each with
# what a person who sets it would set, a folder of the run's or `1`, and the variables it keeps, the
# kit's CI's CLAUDE_CODE_PLUGIN_PREFER_HTTPS, an unrelated FAKE_KEEP and the seven other plugin
# variables of the platform's environment-variables page that tune a clone's time, transport or retry,
# an update or a wait, and steer nowhere plugins are found, kept or loaded, each with a value of its
# own; `seen_when_removed` is what the fake logs after a command's first two words
# (CLAUDE_CODE_PLUGIN_CACHE_DIR, …_SEED_DIR, …_DIRS, …_USE_ZIP_CACHE, CLAUDE_CODE_PLUGIN_PREFER_HTTPS,
# FAKE_KEEP, then …_PLUGIN_GIT_TIMEOUT_MS, …_KEEP_MARKETPLACE_ON_FAILURE,
# CLAUDE_CODE_SYNC_PLUGIN_INSTALL, …_TIMEOUT_MS, FORCE_AUTOUPDATE_PLUGINS,
# …_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL, …_PLUGIN_DIR_WATCH) when the four are gone and the rest
# stay
PLUGIN_VARS = {
    "CLAUDE_CODE_PLUGIN_CACHE_DIR": "person-cache",
    "CLAUDE_CODE_PLUGIN_SEED_DIR": "person-seed",
    "CLAUDE_CODE_PLUGIN_DIRS": "person-dirs",
    "CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE": "1",
}
DOCUMENTED_KEPT = {  # typed by hand, never the code's: the seven documented ones, each its own value
    "CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS": "45000",
    "CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE": "keep",
    "CLAUDE_CODE_SYNC_PLUGIN_INSTALL": "sync",
    "CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS": "30000",
    "FORCE_AUTOUPDATE_PLUGINS": "force",
    "CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL": "disable",
    "CLAUDE_CODE_PLUGIN_DIR_WATCH": "watch",
}
KEPT_VARS = {"CLAUDE_CODE_PLUGIN_PREFER_HTTPS": "1", "FAKE_KEEP": "1"} | DOCUMENTED_KEPT
SEEN_WHEN_REMOVED = "|absent|absent|absent|absent|1|1|45000|keep|sync|30000|force|disable|watch"


def person_plugin_values(under: Path) -> dict[str, tuple[str, str]]:
    """Each of the four variables with the words for its set value and the value, the folders made
    empty under `under`."""
    values: dict[str, tuple[str, str]] = {}
    for variable, folder in PLUGIN_VARS.items():
        if folder == "1":
            values[variable] = ("set to 1", "1")
        else:
            (under / folder).mkdir()
            values[variable] = ("set to a folder", str(under / folder))
    return values


def stuck_line(what: str) -> str:
    return f"BROKEN: `claude --version` {what}{REINSTALL}"


# what `--version` says, its exit, what the run does with the variable unset, and with it at 1
# (None: the same)
VERSION_ROWS: list[tuple[str, int, str, str | None]] = [
    ("2.1.282 (Claude Code)\\n", 0, "note:", None),
    ("2.1.282 (Claude Code)\\r\\n", 0, "note:", None),  # CR is white space: the first word is read
    ("2.1.282 (Claude Code)\\nextra\\n", 0, "note:", None),  # the first line alone is read
    ("\\n2.1.282 (Claude Code)\\n", 0, "note:", None),  # blank lines before it are skipped
    ("  \\n\\n 2.1.282 (Claude Code)\\n", 0, "note:", None),  # white space too, and before the word
    (
        "2.1.286 (Claude Code)\\n",
        0,
        "BROKEN: " + STRICT.format("2.1.286"),
        "note:" + NOTED.format("2.1.286"),
    ),
    (
        "2.1.2820 (Claude Code)\\n",
        0,
        "BROKEN: " + STRICT.format("2.1.2820"),
        "note:" + NOTED.format("2.1.2820"),
    ),
    (
        "2.1.28 (Claude Code)\\n",
        0,
        "BROKEN: " + STRICT.format("2.1.28"),
        "note:" + NOTED.format("2.1.28"),
    ),
    ("2.1.286", 0, "BROKEN: " + STRICT.format("2.1.286"), "note:" + NOTED.format("2.1.286")),
    ("v2.1.282\\n", 0, stuck_line("printed no version (v2.1.282)"), None),
    ("", 0, stuck_line("printed no version (no output)"), None),
    ("", 1, stuck_line("exited 1 (no output)"), None),
    ("2.1.282 (Claude Code)\\n", 1, stuck_line("exited 1 (2.1.282 (Claude Code))"), None),
    ("2.1.286 (Claude Code)\\n", 1, stuck_line("exited 1 (2.1.286 (Claude Code))"), None),
    ("", 139, stuck_line("exited 139 (no output)"), None),
    (
        "extra\\n2.1.282 (Claude Code)\\n",
        0,
        stuck_line("printed no version (2.1.282 (Claude Code))"),
        None,
    ),
]


TOO_OLD = "2.1.286 (Claude Code)\\n"


def kind_of(said_outcome: str) -> str:
    if said_outcome == "note:":
        return "the run goes on"
    return "the run goes on with the note" if said_outcome.startswith("note:") else "BROKEN"


@dataclass(frozen=True)
class ClaudeStub:
    """The toy kit of the version check, the folder of the fake `claude`, and the log the fake writes."""

    base_dir: Path
    toy_kit: Path
    fake_dir: Path
    fake_log: Path

    def claude_env(self, said: str, code: int, optout: str | None, path: str | None = None) -> dict[str, str]:
        env = {k: v for k, v in os.environ.items() if k != "CONSTITUTION_KIT_ANY_CLAUDE"}
        env |= {
            "PATH": path if path is not None else f"{self.fake_dir}{os.pathsep}{env.get('PATH', '')}",
            "FAKE_SAYS": said,
            "FAKE_EXIT": str(code),
            "FAKE_LOG": str(self.fake_log),
        }
        if optout is not None:
            env["CONSTITUTION_KIT_ANY_CLAUDE"] = optout
        return env

    def outcome(self, env: dict[str, str], root: Path | None = None) -> str:
        """What the check does before its install: the note it goes on with, or its BROKEN line."""
        self.fake_log.unlink(missing_ok=True)
        try:
            return f"note:{claude_noted(self.toy_kit if root is None else root, env)}"
        except Broken as broken:
            return f"BROKEN: {broken}"

    def logged(self) -> list[str]:
        return self.fake_log.read_text(encoding="utf-8").splitlines() if self.fake_log.exists() else []

    def whole_run(
        self, said: str, code: int, optout: str | None, *args: str
    ) -> tuple[int, list[str], list[str]]:
        """The exit and the lines `main` prints on the toy kit, and what the fake claude logged."""
        self.fake_log.unlink(missing_ok=True)
        printed_lines = io.StringIO()
        with (
            mock.patch.dict(os.environ, self.claude_env(said, code, optout)),
            patched_globals({"KIT": self.toy_kit}),
            contextlib.redirect_stdout(printed_lines),
        ):
            if optout is None:  # patch.dict adds to the environment, so the ambient variable goes by hand
                os.environ.pop("CONSTITUTION_KIT_ANY_CLAUDE", None)
            status = main(["--module", "const-nope", *args])
        return status, printed_lines.getvalue().splitlines(), self.logged()


def claude_stub(base_dir: Path) -> ClaudeStub:
    """The toy kit that pins 2.1.282, a folder holding the fake `claude`, and its log, under `base_dir`."""
    toy_kit, fake_dir, fake_log = base_dir / "kit", base_dir / "bin", base_dir / "claude.log"
    (toy_kit / "scripts").mkdir(parents=True)
    (toy_kit / "scripts" / "claude-code.version").write_text("2.1.282\n", encoding="utf-8")
    fake_dir.mkdir()
    (fake_dir / "claude").write_text(FAKE_CLAUDE, encoding="utf-8")
    (fake_dir / "claude").chmod(0o755)
    (base_dir / "empty").mkdir()
    return ClaudeStub(base_dir, toy_kit, fake_dir, fake_log)


def version_answer_cases(tally: Tally, stub: ClaudeStub) -> None:
    """The version check over every answer of `claude --version`: a pinned one, another one, none."""
    base_dir, toy_kit, fake_log, claude_env, outcome, logged = (
        stub.base_dir,
        stub.toy_kit,
        stub.fake_log,
        stub.claude_env,
        stub.outcome,
        stub.logged,
    )
    for says, exits, unset_out, one_out in VERSION_ROWS:
        at_one = unset_out if one_out is None else one_out
        seen = [outcome(claude_env(says, exits, None)), outcome(claude_env(says, exits, "1"))]
        ran = logged()  # the second run only: each run leaves the one line its own command logged
        version_case(
            tally,
            f'`claude --version` printing "{says}" with exit {exits}: {kind_of(unset_out)} with the variable'
            f" unset, {kind_of(at_one)} with it at 1",
            seen == [unset_out, at_one] and ran == ["--version"],
            f"{seen} {ran}",
        )
    for value in ("", "0", "yes", "true", " 1", "1 ", "TRUE", "01"):
        version_case(
            tally,
            f"CONSTITUTION_KIT_ANY_CLAUDE={value!r} is not the opt-out: the other version is BROKEN",
            outcome(claude_env(TOO_OLD, 0, value)) == "BROKEN: " + STRICT.format("2.1.286"),
            outcome(claude_env(TOO_OLD, 0, value)),
        )
    no_pin = base_dir / "empty"
    said_no_pin = outcome(claude_env(TOO_OLD, 0, "1"), no_pin)
    version_case(
        tally,
        "a kit with no pin file is BROKEN with the reader's line, and claude is not run",
        said_no_pin
        == f"BROKEN: {no_pin}/scripts/claude-code.version cannot be read (No such file or directory)"
        " — fix: write the one version Claude Code's npm package carries, e.g. 2.1.282, as the file's"
        " only line"
        and logged() == [],
        f"{said_no_pin} {logged()}",
    )
    said_no_claude = outcome(claude_env(TOO_OLD, 0, "1", path=str(no_pin)))
    version_case(
        tally,
        "no claude on PATH is BROKEN, the opt-out notwithstanding",
        said_no_claude
        == "BROKEN: claude is not installed (No such file or directory) — fix: install it and put it on"
        " PATH",
        said_no_claude,
    )
    fake_log.unlink(missing_ok=True)
    try:
        claude_note(toy_kit, claude_env("", 0, "1") | {"FAKE_HANG": "1"}, timeout=0.2)
        said_hung = "no DocumentError"
    except DocumentError as hung:
        said_hung = str(hung)
    version_case(
        tally,
        "a claude that does not answer in time is no version, the opt-out notwithstanding",
        said_hung == f"`claude --version` exited 124 (timed out after 0.2 s){REINSTALL}"
        and logged() == ["--version"],
        f"{said_hung} {logged()}",
    )


def config_folder_cases(tally: Tally, stub: ClaudeStub) -> None:
    """`claude --version` runs in an empty configuration folder of its own, auto-updater off."""
    base_dir, claude_env, outcome = stub.base_dir, stub.claude_env, stub.outcome
    person = base_dir / "person"  # the configuration folder of the person who runs the check
    person.mkdir()
    (person / "keep").write_text("the person's own configuration\n", encoding="utf-8")
    env_log = base_dir / "env.log"
    for name, own in (
        ("the person's CLAUDE_CONFIG_DIR and DISABLE_AUTOUPDATER=0", True),
        ("neither of the two variables", False),
    ):
        env_log.unlink(missing_ok=True)
        env = claude_env("2.1.282 (Claude Code)\\n", 0, None) | {"FAKE_ENV": str(env_log)}
        env = {k: v for k, v in env.items() if own or k not in ("CLAUDE_CONFIG_DIR", "DISABLE_AUTOUPDATER")}
        if own:
            env |= {"CLAUDE_CONFIG_DIR": str(person), "DISABLE_AUTOUPDATER": "0"}
        outcome(env)
        seen_env = env_log.read_text(encoding="utf-8").splitlines() if env_log.exists() else []
        config, updater, held, is_dir = (seen_env[0].split("|") + ["", "", "", ""])[:4]
        version_case(
            tally,
            f"`claude --version` runs in an empty configuration folder of its own, auto-updater off,"
            f" with {name}",
            len(seen_env) == 1
            and config not in ("", str(person))
            and is_dir == "dir"
            and held == "0"
            and updater == "1"
            and sorted(path.name for path in person.iterdir()) == ["keep"],
            f"{seen_env} {sorted(path.name for path in person.iterdir())}",
        )


def plugin_variable_cases(tally: Tally, stub: ClaudeStub) -> None:
    """None of the four plugin variables of the person reaches `claude --version`; the kept ones do."""
    base_dir, claude_env, outcome = stub.base_dir, stub.claude_env, stub.outcome
    cache_seen = base_dir / "cache-seen.log"
    person_values = person_plugin_values(base_dir)
    for variable, (what, set_value) in person_values.items():
        for name, value in ((what, set_value), ("set and empty", "")):
            cache_seen.unlink(missing_ok=True)
            env = claude_env("2.1.282 (Claude Code)\\n", 0, None) | KEPT_VARS
            env |= {"FAKE_CACHE": str(cache_seen), variable: value}
            said_version = outcome(env)
            seen_version = cache_seen.read_text(encoding="utf-8").splitlines() if cache_seen.exists() else []
            version_case(
                tally,
                f"{variable} {name} in the person's environment: `claude --version` runs with the four"
                " absent, CLAUDE_CODE_PLUGIN_PREFER_HTTPS, FAKE_KEEP and the seven documented as set",
                said_version == "note:" and seen_version == ["--version " + SEEN_WHEN_REMOVED],
                f"{said_version} {seen_version}",
            )
    cache_seen.unlink(missing_ok=True)
    env = claude_env(TOO_OLD, 0, "1") | KEPT_VARS | {"FAKE_CACHE": str(cache_seen)}
    env |= {variable: set_value for variable, (_, set_value) in person_values.items()}
    said_all = outcome(env)
    seen_all = cache_seen.read_text(encoding="utf-8").splitlines() if cache_seen.exists() else []
    version_case(
        tally,
        "all four set in the person's environment with CONSTITUTION_KIT_ANY_CLAUDE=1 on another version:"
        " the opt-out is still read, and `claude --version` runs with the four absent",
        said_all == "note:" + NOTED.format("2.1.286") and seen_all == ["--version " + SEEN_WHEN_REMOVED],
        f"{said_all} {seen_all}",
    )


def whole_run_cases(tally: Tally, stub: ClaudeStub) -> None:
    """A whole run of `main` stops at the version it cannot accept, and goes on with a note when allowed."""
    whole_run = stub.whole_run
    stop = "BROKEN: the check could not run — 0 modules examined"
    status, lines, ran = whole_run("2.1.286 (Claude Code)\\n", 0, None)
    version_case(
        tally,
        "a run on another version stops at its first line, and no other claude command runs",
        status == EXIT_BROKEN
        and lines == ["BROKEN: " + STRICT.format("2.1.286"), stop]
        and ran == ["--version"],
        f"{status} {lines} {ran}",
    )
    status, lines, ran = whole_run("2.1.286 (Claude Code)\\n", 0, "1")
    version_case(
        tally,
        "with the opt-out the run goes on, and each BROKEN line it ends with ends with the note",
        status == EXIT_BROKEN
        and lines
        == [
            "BROKEN: no module const-nope in the kit — fix: name a folder under modules/ that holds a"
            " plugin" + NOTED.format("2.1.286"),
            stop + NOTED.format("2.1.286"),
        ]
        and ran == ["--version"],
        f"{status} {lines} {ran}",
    )
    status, lines, ran = whole_run("", 139, "1")
    version_case(
        tally,
        "a crashed claude stops the run with no note, the opt-out notwithstanding",
        status == EXIT_BROKEN
        and lines == [f"BROKEN: `claude --version` exited 139 (no output){REINSTALL}", stop]
        and ran == ["--version"],
        f"{status} {lines} {ran}",
    )


def version_check_cases(tally: Tally) -> None:
    """The version check over every answer of `claude --version`."""
    with tempfile.TemporaryDirectory() as tmp:  # the version check over every answer of `claude --version`
        stub = claude_stub(Path(tmp))
        version_answer_cases(tally, stub)
        config_folder_cases(tally, stub)
        plugin_variable_cases(tally, stub)
        whole_run_cases(tally, stub)


# Step 2 over a toy kit, its marketplace named toy-mp, and a fake claude.
TOY_KEY = "const-x@toy-mp"
PIN_NOTE = Note("2.1.282")  # the state of a run on the pin: the note empty
GONE = 'Plugin "const-x" not found in any configured marketplace'
# what the platform replies, typed by hand
OK_LINE = json.dumps({"command": "install", "outcome": "ok", "message": "Installed", "scope": "user"})
FAILED_LINE = json.dumps(
    {"command": "install", "outcome": "failed", "message": GONE, "failureCode": "not_found"}
)
SHA = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"  # an object id: 40 lower-case hexadecimal characters
SHA_WRONG, SHA_RIGHT = "0f" * 20, "c0ffee" * 6 + "c0ff"


def recorded(*entries: dict[str, object]) -> str:
    return json.dumps({"version": 2, "plugins": {TOY_KEY: list(entries)}})


def unrecord(text: str) -> str:  # the record's place is under a folder the run makes and removes
    return re.sub(r"[^\s(]+/config/plugins/installed_plugins\.json", "<record>", text)


INSTALL_COMMAND = f"`claude plugin install {TOY_KEY} --json`"
LISTING_COMMAND = "`claude plugin list --json`"


def fix_of(reader: str, wrote: str = "a reply", script: str = "scripts/check-bare-install.py") -> str:
    return (  # typed by hand: a message function cannot check itself
        f" — fix: Claude Code 2.1.282 wrote {wrote} that the kit's reader, `{reader}` in"
        f" {script}, does not read: update that reader to what 2.1.282 writes"
    )


OFF_FIX = (  # typed by hand: the run is on 2.1.286, not the pinned 2.1.282
    " — fix: this run is on 2.1.286, not the pinned 2.1.282: run it again on the pinned version,"
    " put Claude Code 2.1.282 first on PATH for this run: either run sh scripts/setup-claude.sh"
    " in the kit's clone, then the check through sh scripts/gate-list.sh --run install-<module>"
    " (--run session-<module> for the session check,"
    " --run guide for the guide's check), which puts it first, or install it beside your own by hand"
    " (npm install --prefix <folder> @anthropic-ai/claude-code@2.1.282,"
    " then PATH=<folder>/node_modules/.bin:$PATH)"
)
INSTALL_FIX = fix_of("install_scope", script="scripts/kit_install.py")
LIST_FIX = fix_of("listed_install", script="scripts/kit_install.py")
REFUSED = "RED: Claude Code refuses to install it ({}) | fix its manifest or its entry in marketplace.json"
NO_OBJECT = "not one JSON object (exit {})"
BAD_OUTCOME = 'an object that {}, not "ok" or "failed" (exit 0)'
TIMED_OUT = " gave no result in {} s — fix: run the check again, and check that git can reach the source"
INSTALL_ROWS: list[tuple[str, str, int, str]] = [
    ("an ok result, exit 0, goes on", OK_LINE, 0, "on"),
    (
        "an ok result after two other lines goes on: the last line is read",
        f"A\nB\n{OK_LINE}",
        0,
        "on",
    ),
    ("an ok result with blank lines after it goes on", f"{OK_LINE}\n\n  \n", 0, "on"),
    (
        "a failed result with its failureCode is a refusal naming both",
        FAILED_LINE,
        1,
        REFUSED.format(f"not_found: {GONE}"),
    ),
    (
        "a failed result without a failureCode is a refusal naming its message",
        json.dumps({"outcome": "failed", "message": GONE}),
        1,
        REFUSED.format(GONE),
    ),
    (
        "a failed result with exit 0 is a refusal",
        FAILED_LINE,
        0,
        REFUSED.format(f"not_found: {GONE}"),
    ),
    (
        "a failed result with neither field is a refusal naming the exit",
        '{"outcome": "failed"}',
        1,
        REFUSED.format("exit 1"),
    ),
    (
        "an empty standard output, exit 1, is BROKEN",
        "",
        1,
        f"BROKEN: {INSTALL_COMMAND} printed nothing on standard output (exit 1){INSTALL_FIX}",
    ),
    (
        "an empty standard output, exit 0, is BROKEN",
        "",
        0,
        f"BROKEN: {INSTALL_COMMAND} printed nothing on standard output (exit 0){INSTALL_FIX}",
    ),
    (
        "the JSON line followed by a human line is BROKEN: the last line is no JSON",
        f"{OK_LINE}\nInstalled const-x",
        0,
        f"BROKEN: {INSTALL_COMMAND} ended with 'Installed const-x', " + NO_OBJECT.format(0) + INSTALL_FIX,
    ),
    (
        "a human line only, exit 0, is BROKEN",
        "✔ Installed const-x",
        0,
        f"BROKEN: {INSTALL_COMMAND} ended with '✔ Installed const-x', " + NO_OBJECT.format(0) + INSTALL_FIX,
    ),
    (
        "a human line only, exit 1, is BROKEN",
        "✘ Failed to install const-x",
        1,
        f"BROKEN: {INSTALL_COMMAND} ended with '✘ Failed to install const-x', "
        + NO_OBJECT.format(1)
        + INSTALL_FIX,
    ),
    (
        "an ok line with exit 1 is BROKEN",
        OK_LINE,
        1,
        f"BROKEN: {INSTALL_COMMAND} said ok and exited 1{INSTALL_FIX}",
    ),
    (
        "exit 124 with nothing printed is BROKEN, no refusal",
        "",
        124,
        f"BROKEN: {INSTALL_COMMAND}{TIMED_OUT.format(300)}",
    ),
    ("exit 124 beats an ok line", OK_LINE, 124, f"BROKEN: {INSTALL_COMMAND}{TIMED_OUT.format(300)}"),
    (
        "exit 124 beats a failed line",
        FAILED_LINE,
        124,
        f"BROKEN: {INSTALL_COMMAND}{TIMED_OUT.format(300)}",
    ),
    (
        "a human line whose quotation is exactly 200 characters is quoted whole",
        "x" * 198,
        0,
        f"BROKEN: {INSTALL_COMMAND} ended with '{'x' * 198}', {NO_OBJECT.format(0)}{INSTALL_FIX}",
    ),
    (
        "a human line whose quotation is 201 characters is cut at 200 and ends with …",
        "x" * 199,
        0,
        f"BROKEN: {INSTALL_COMMAND} ended with '{'x' * 199}…, {NO_OBJECT.format(0)}{INSTALL_FIX}",
    ),
    (
        "a long human line is cut at 200 characters",
        "✔ " + " ".join(["installed"] * 30),
        0,
        f"BROKEN: {INSTALL_COMMAND} ended with {('✔ ' + ' '.join(['installed'] * 30))!r:.200}…, "
        + NO_OBJECT.format(0)
        + INSTALL_FIX,
    ),
    (
        "a JSON list is BROKEN",
        "[1, 2]",
        0,
        f"BROKEN: {INSTALL_COMMAND} ended with '[1, 2]', {NO_OBJECT.format(0)}{INSTALL_FIX}",
    ),
    (
        "an ok result without a scope is BROKEN",
        json.dumps({"outcome": "ok"}),
        0,
        f"BROKEN: {INSTALL_COMMAND} said ok without a scope string (scope is absent){INSTALL_FIX}",
    ),
    (
        "an ok result whose scope is a number is BROKEN",
        json.dumps({"outcome": "ok", "scope": 5}),
        0,
        f"BROKEN: {INSTALL_COMMAND} said ok without a scope string (scope is 5){INSTALL_FIX}",
    ),
    (
        "an object with no outcome is BROKEN",
        json.dumps({"scope": "user"}),
        0,
        f"BROKEN: {INSTALL_COMMAND} ended with " + BAD_OUTCOME.format("has no outcome") + INSTALL_FIX,
    ),
    (
        "an outcome of another word is BROKEN",
        json.dumps({"outcome": "maybe", "scope": "user"}),
        0,
        f"BROKEN: {INSTALL_COMMAND} ended with "
        + BAD_OUTCOME.format("has the outcome 'maybe'")
        + INSTALL_FIX,
    ),
    (
        "an outcome that is no string is BROKEN",
        json.dumps({"outcome": True, "scope": "user"}),
        0,
        f"BROKEN: {INSTALL_COMMAND} ended with " + BAD_OUTCOME.format("has the outcome True") + INSTALL_FIX,
    ),
]
NO_ENTRY = "lists no entry whose id is " + TOY_KEY + " at the scope user the install wrote ({})"
# A list command that wrote no reply (it exited other than 0, or timed out) has no reader to update:
# its fix is the command's own, not `fix_of`'s; the lines are typed by hand
CASE_LIST_WHERE = "a folder of your own, CLAUDE_CONFIG_DIR set to an empty folder"
PUT_FIRST = (
    "put Claude Code 2.1.282 first on PATH for this run: either run sh scripts/setup-claude.sh in the"
    " kit's clone, then the check through sh scripts/gate-list.sh --run install-<module>"
    " (--run session-<module> for the session check, --run guide"
    " for the guide's check), which puts it first, or install it beside your own by hand (npm install"
    " --prefix <folder> @anthropic-ai/claude-code@2.1.282,"
    " then PATH=<folder>/node_modules/.bin:$PATH)"
)
OFF_WHAT = "this run is on 2.1.286, not the pinned 2.1.282"
FIX_TIMED_OUT = " — fix: run the check again"
FIX_TIMED_OUT_OFF = f" — fix: {OFF_WHAT}: run the check again on the pinned version, {PUT_FIRST}"
FIX_EXITED = (
    f" — fix: run `claude plugin list --json` in {CASE_LIST_WHERE}, read why it fails,"
    " then run the check again"
)
FIX_EXITED_OFF = (
    f" — fix: run `claude plugin list --json` in {CASE_LIST_WHERE}, read why it fails; {OFF_WHAT}, so then"
    f" run the check again on the pinned version, {PUT_FIRST}"
)
OFF_NOTE = Note("2.1.282", "2.1.286")  # the state of a run on 2.1.286 with the opt-out set
NO_COMMIT = "BROKEN: the install record names no commit for " + TOY_KEY + " (<record>: {})"  # by hand
UNNAMED = NO_COMMIT + fix_of("installed_commit", "a record")
UNNAMED_OFF = NO_COMMIT + OFF_FIX
SAYS_OFF, SAYS_PINNED = "2.1.286 (Claude Code)\\n", "2.1.282 (Claude Code)\\n"
GREEN_LINE = "GREEN: const-x installs and operates on a bare repository with its defaults"


@dataclass(frozen=True)
class Scene:
    """One run of the check over the fake claude: what its install, its list and the record say."""

    out: str
    code: int
    listing: str
    list_code: int
    record: str
    source: str  # `remote`: no folder, `local`: the toy kit's folder, `linked`: one with a link


@dataclass(frozen=True)
class StepTwo:
    """The toy kit of step 2, its installed copy, the folders round them, the fake `claude`, its logs."""

    base: Path
    toy: Path
    bin_dir: Path
    cache: Path
    copy: Path
    other: Path
    fake_log: Path
    calls_log: Path
    cache_log: Path
    linked: Path
    no_kernel: Path
    work: Path
    repo: Path

    def listed(self, **over: object) -> dict[str, object]:
        return {"id": TOY_KEY, "scope": "user", "installPath": str(self.copy)} | over

    def commit(self, **over: object) -> dict[str, object]:
        return {"installPath": str(self.copy), "scope": "user", "gitCommitSha": SHA} | over

    @property
    def good(self) -> str:
        """The list of one entry, the installed copy, as the fake's `plugin list` says it."""
        return json.dumps([self.listed()])

    @property
    def no_sha(self) -> dict[str, object]:
        """An entry of the install record that names the installed copy and no commit."""
        return {"installPath": str(self.copy)}

    def new_scene(
        self,
        out: str = OK_LINE,
        code: int = 0,
        listing: str | None = None,
        list_code: int = 0,
        record: str | None = None,
        source: str = "remote",
    ) -> Scene:
        """A scene of the installed copy, its list and its record, whatever it is not given."""
        return Scene(
            out,
            code,
            self.good if listing is None else listing,
            list_code,
            recorded(self.commit()) if record is None else record,
            source,
        )

    def environment(self, scene: Scene, says: str = "2.1.282 (Claude Code)\\n") -> dict[str, str]:
        for log in (self.fake_log, self.calls_log, self.cache_log):
            log.unlink(missing_ok=True)
        return {
            "PATH": f"{self.bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
            "FAKE_SAYS": says,
            "FAKE_LOG": str(self.fake_log),
            "FAKE_CALLS": str(self.calls_log),
            "FAKE_CACHE": str(self.cache_log),
            "FAKE_INSTALL_OUT": scene.out,
            "FAKE_INSTALL_EXIT": str(scene.code),
            "FAKE_LIST_OUT": scene.listing,
            "FAKE_LIST_EXIT": str(scene.list_code),
            "FAKE_RECORD": scene.record,
        }

    def where(self, scene: Scene) -> str:
        return {"local": str(self.toy), "linked": str(self.linked)}.get(scene.source, "owner/repo")

    def drive(self, scene: Scene, extra: dict[str, str] | None = None) -> tuple[str, list[str], list[str]]:
        """What `check_module` does: `on` (the copy is compared), the finding, or the BROKEN line; the
        commits the source was asked at, and the copies it was compared with; `extra` is added to the
        environment the check runs in."""
        fetched: list[str] = []
        compared: list[str] = []

        def source_spy(at: str, name: str, root: Path) -> Path:
            fetched.append(at)
            return self.toy / "modules" / name / "plugin"

        def installed_spy(
            name: str, src: Path, plugin: Path, repo: Path, data: Path, path: str | None = None
        ) -> list[Finding]:
            compared.append(str(plugin))
            return []

        patched = {"KIT": self.toy, "source_at": source_spy, "check_installed": installed_spy}
        with (
            mock.patch.dict(os.environ, self.environment(scene) | (extra or {})),
            patched_globals(patched),
        ):
            try:
                found, _ = check_module("const-x", self.where(scene), PIN_NOTE)
            except Broken as broken:
                return unrecord(f"BROKEN: {broken}"), fetched, compared
            except (KeyError, TypeError) as escaped:  # a record's entry read wrongly: a case that fails
                return f"escaped {type(escaped).__name__}: {escaped}", fetched, compared
        return "; ".join(f"RED: {f.what} | {f.fix}" for f in found) or "on", fetched, compared

    def expect(
        self, tally: Tally, name: str, scene: Scene, wanted: str, fetched: list[str] | None = None
    ) -> None:
        """`wanted` is what `drive` says, `fetched` the commits the source was asked at; when it goes on,
        the copy compared is the installed one."""
        got = self.drive(scene)
        version_case(
            tally, name, got == (wanted, fetched or [], [str(self.copy)] if wanted == "on" else []), str(got)
        )

    def list_said(self, scene: Scene, note: Note) -> str:
        """What `listed_install` says over the fake's list for `scene` in the state `note` records."""
        try:
            listed_install(TOY_KEY, "user", self.repo, self.environment(scene), note)
        except Broken as bad:
            return f"BROKEN: {bad}"
        return "no Broken"

    def lines_of(
        self, scene: Scene, says: str, optout: bool, kit: Path | None = None
    ) -> tuple[int, list[str]]:
        """The exit and the lines `main` prints for the toy kit's module over the fake claude."""
        printed_lines = io.StringIO()
        with (
            mock.patch.dict(os.environ, self.environment(scene, says)),
            patched_globals({"KIT": self.toy if kit is None else kit}),
            contextlib.redirect_stdout(printed_lines),
        ):
            os.environ.pop("CONSTITUTION_KIT_ANY_CLAUDE", None)
            if optout:
                os.environ["CONSTITUTION_KIT_ANY_CLAUDE"] = "1"
            status = main(["--module", "const-x", "--from", self.where(scene)])
        return status, [unrecord(line) for line in printed_lines.getvalue().splitlines()]


TOY_MARK = "toy-shared"  # what a toy kit's shared package says, so that no other copy passes for it


def toy_shared(kit: Path, body: str = f'MARK = "{TOY_MARK}"\n') -> Path:
    """The shared package of the toy kit `kit`, `shared/constitution_layer_kit/` with `body` as its
    `__init__.py`, which every run of `shared_path` over the kit imports; the kit's `shared/` folder."""
    package = kit / "shared" / "constitution_layer_kit"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(body, encoding="utf-8")
    return kit / "shared"


def step_two_scene(base: Path) -> StepTwo:
    """The toy kit of step 2 under `base`: an installed copy, a folder that is not it, the fake claude."""
    toy, bin_dir, cache = base / "kit", base / "bin", base / "cache"
    toy_shared(toy)
    (toy / ".claude-plugin").mkdir(parents=True)
    (toy / ".claude-plugin" / "marketplace.json").write_text('{"name": "toy-mp"}', encoding="utf-8")
    (toy / "scripts").mkdir()
    (toy / "scripts" / "claude-code.version").write_text("2.1.282\n", encoding="utf-8")
    (toy / "kernel").mkdir()
    (toy / "kernel" / "CONVENTIONS.md").write_text("A kernel.\n", encoding="utf-8")
    toy_module = toy / "modules" / "const-x"
    toy_plugin = toy_module / "plugin"
    (toy_plugin / ".claude-plugin").mkdir(parents=True)
    (toy_plugin / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
    (toy_module / "MODULE.md").write_text('<a id="t9"></a>\n<a id="t10"></a>\n', encoding="utf-8")
    copy, other = cache / "const-x", cache / "other"
    shutil.copytree(toy_plugin, copy)  # the installed copy, of the plugin folder; `other` is not it
    other.mkdir()
    (cache / "a-file").write_text("not a folder\n", encoding="utf-8")
    bin_dir.mkdir()
    (bin_dir / "claude").write_text(FAKE_CLAUDE, encoding="utf-8")
    (bin_dir / "claude").chmod(0o755)
    fake_log, calls_log, cache_log = base / "fake.log", base / "calls.log", base / "cache.log"
    linked = base / "linked-kit"  # the toy kit whose module holds a link its installed copy lacks
    shutil.copytree(toy, linked, symlinks=True)
    (linked / "modules" / "const-x" / "plugin" / "linked").symlink_to(".claude-plugin/plugin.json")
    no_kernel = base / "no-kernel"  # the toy kit without its kernel/, which a bare repository copies
    shutil.copytree(toy, no_kernel)
    shutil.rmtree(no_kernel / "kernel")
    work, repo = base / "work", base / "repo"
    work.mkdir()
    repo.mkdir()
    return StepTwo(
        base, toy, bin_dir, cache, copy, other, fake_log, calls_log, cache_log, linked, no_kernel, work, repo
    )


def install_reply_cases(tally: Tally, step: StepTwo) -> None:
    """What `claude plugin install` replies, row by row, and an install that gives no result in time."""
    work, repo, environment, expect, new_scene = (
        step.work,
        step.repo,
        step.environment,
        step.expect,
        step.new_scene,
    )
    for name, out, code, wanted in INSTALL_ROWS:
        expect(tally, f"install replies: {name}", new_scene(out=out, code=code, source="local"), wanted)
    real_run = run
    waits: list[float] = []  # the timeout each `claude plugin install` is run with, by `run`'s parameter

    def run_cut(
        argv: list[str], cwd: Path, env: dict[str, str], stdin: str = "", timeout: float = 300
    ) -> tuple[int, str, str]:
        """`run`, but a command that hangs is cut after 2 s whatever its timeout: a timeout that never
        reached `run` is then seen in `waits` at once, not after the 300 s of the default."""
        if argv[:3] == ["claude", "plugin", "install"]:
            waits.append(timeout)
        return real_run(argv, cwd, env, stdin, min(timeout, 2))

    with (
        mock.patch.dict(os.environ, environment(new_scene()) | {"FAKE_HANG_INSTALL": "1"}),
        patched_globals({"run": run_cut}),
    ):
        try:
            install("const-x", work, repo, "owner/repo", "toy-mp", PIN_NOTE, timeout=0.3)
            said_slow = "nothing raised"
        except (Broken, Refused) as slow:
            said_slow = f"{type(slow).__name__}: {slow}"
    version_case(
        tally,
        "an install that gives no result within its timeout is BROKEN, no refusal, and its timeout is the"
        " one `run` waits for",
        said_slow == f"Broken: {INSTALL_COMMAND}{TIMED_OUT.format('0.3')}" and waits == [0.3],
        f"{said_slow} {waits}",
    )


def list_reply_cases(tally: Tally, step: StepTwo) -> None:
    """What `claude plugin list` replies, row by row, is the entry looked for or a BROKEN line."""
    cache, other, listed, expect, new_scene = step.cache, step.other, step.listed, step.expect, step.new_scene
    no_path = "gives no installPath string for " + TOY_KEY + " at scope user (installPath is {})"
    no_json = "printed no JSON ({!r}: Expecting value: line 1 column 1 (char 0))"
    missing, a_file = str(cache / "missing"), str(cache / "a-file")
    bare = {"id": TOY_KEY, "scope": "user"}

    def others(count: int) -> str:
        """A list of `count` entries at the install's scope, none of them with the id looked for."""
        return json.dumps([listed(id=f"const-{i}@toy-mp", installPath=str(other)) for i in range(count)])

    list_rows: list[tuple[str, str, str]] = [
        ("an empty list", "[]", NO_ENTRY.format("no entries")),
        (
            "an entry at another scope only",
            json.dumps([listed(scope="project")]),
            NO_ENTRY.format("entries: 'const-x@toy-mp' at 'project'"),
        ),
        (
            "two entries of the id at the install's scope",
            json.dumps([listed(), listed(installPath=str(other))]),
            "lists 2 entries whose id is " + TOY_KEY + " at the scope user the install wrote"
            " (entries: 'const-x@toy-mp' at 'user', 'const-x@toy-mp' at 'user')",
        ),
        ("an entry without installPath", json.dumps([bare]), no_path.format("absent")),
        ("an installPath that is a number", json.dumps([listed(installPath=7)]), no_path.format("7")),
        (
            "an installPath that is no folder",
            json.dumps([listed(installPath=missing)]),
            f"names an installPath that is no folder ({missing})",
        ),
        (
            "an installPath that is a file",
            json.dumps([listed(installPath=a_file)]),
            f"names an installPath that is no folder ({a_file})",
        ),
        ("an object", '{"id": "x"}', "printed a JSON dict, not a list"),
        (
            "five entries of other ids, all named",
            others(5),
            NO_ENTRY.format("entries: " + ", ".join(f"'const-{i}@toy-mp' at 'user'" for i in range(5))),
        ),
        (
            "six entries of other ids, the first five named and the rest cut with …",
            others(6),
            NO_ENTRY.format(
                "entries: " + ", ".join(f"'const-{i}@toy-mp' at 'user'" for i in range(5)) + ", …"
            ),
        ),
        (
            "entries that are no objects, shown as they are",
            json.dumps(["x", 7]),
            NO_ENTRY.format("entries: 'x', 7"),
        ),
        ("text that is no JSON", "no plugins installed", no_json.format("no plugins installed")),
        ("nothing", "", no_json.format("")),
    ]
    for name, listing, wanted in list_rows:
        expect(
            tally,
            f"list replies: {name} is BROKEN",
            new_scene(listing=listing, source="local"),
            f"BROKEN: {LISTING_COMMAND} {wanted}{LIST_FIX}",
        )


def list_exit_cases(tally: Tally, step: StepTwo) -> None:
    """A list that exits other than 0 or times out has a fix of its own; the right entry is picked."""
    other, good, listed, expect, list_said, new_scene = (
        step.other,
        step.good,
        step.listed,
        step.expect,
        step.list_said,
        step.new_scene,
    )
    for code, wanted_on, wanted_off in (
        (1, FIX_EXITED, FIX_EXITED_OFF),
        (3, FIX_EXITED, FIX_EXITED_OFF),
        (124, FIX_TIMED_OUT, FIX_TIMED_OUT_OFF),
    ):
        for state, note, fix in (
            ("on the pin", PIN_NOTE, wanted_on),
            ("off the pin", OFF_NOTE, wanted_off),
        ):
            said_list = list_said(new_scene(listing=good, list_code=code), note)
            version_case(
                tally,
                f"list replies: a good list with exit {code} is BROKEN, {state},"
                f" its fix the command's own{' (a timeout)' if code == 124 else ''}",
                said_list == f"BROKEN: {LISTING_COMMAND} exited {code} ({good}){fix}",
                said_list,
            )
    expect(
        tally,
        "list replies: a good list with exit 1 is BROKEN, through the run",
        new_scene(listing=good, list_code=1, source="local"),
        f"BROKEN: {LISTING_COMMAND} exited 1 ({good}){FIX_EXITED}",
    )
    for state, note, fix in (
        ("on the pin", PIN_NOTE, FIX_TIMED_OUT),
        ("off the pin", OFF_NOTE, FIX_TIMED_OUT_OFF),
    ):
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["claude"], 300)):
            said_list = list_said(new_scene(listing=good), note)
        version_case(
            tally,
            f"list replies: a list that times out is BROKEN, {state}, never a reader to update",
            said_list == f"BROKEN: {LISTING_COMMAND} exited 124 (timed out after 300 s){fix}",
            said_list,
        )
    on_project = json.dumps({"outcome": "ok", "scope": "project"})
    picks: list[tuple[str, Scene]] = [
        (
            "the entry at the right scope, an entry at another scope first, is the one",
            new_scene(listing=json.dumps([listed(scope="project", installPath=str(other)), listed()])),
        ),
        (
            "the entry at the right scope, an entry at another scope last, is the one",
            new_scene(listing=json.dumps([listed(), listed(scope="project", installPath=str(other))])),
        ),
        (
            "the entry of the id, entries of other ids around it, is the one",
            new_scene(
                listing=json.dumps(
                    [
                        listed(id="const-y@toy-mp", installPath=str(other)),
                        listed(id="const-x@other-mp", installPath=str(other)),
                        listed(),
                    ]
                )
            ),
        ),
        (
            "the entry at the scope the install wrote, not at `user`, is the one",
            new_scene(
                out=on_project,
                listing=json.dumps([listed(installPath=str(other)), listed(scope="project")]),
            ),
        ),
    ]
    for name, scene in picks:
        expect(tally, f"list replies: {name}", replace(scene, source="local"), "on")


def record_cases(tally: Tally, step: StepTwo) -> None:
    """The install record names the commit of a remote source, or each row is a BROKEN line."""
    copy, other, no_sha, commit, expect, new_scene = (
        step.copy,
        step.other,
        step.no_sha,
        step.commit,
        step.expect,
        step.new_scene,
    )
    no_list = f"holds no list under plugins['{TOY_KEY}']"
    record_rows: list[tuple[str, str, str]] = [
        ("a commit that is absent", recorded(no_sha), "gitCommitSha is absent"),
        ("a commit that is empty", recorded(commit(gitCommitSha="")), "gitCommitSha is empty"),
        (
            "a commit that is a number",
            recorded(commit(gitCommitSha=12345)),
            "gitCommitSha is no string, 12345",
        ),
        ("a commit that is null", recorded(commit(gitCommitSha=None)), "gitCommitSha is no string, None"),
        (
            "a commit that is a list",
            recorded(commit(gitCommitSha=["a"])),
            "gitCommitSha is no string, ['a']",
        ),
        ("no record", "", "cannot be read, No such file or directory"),
        ("a record that is no JSON", "not json", "is no JSON, Expecting value: line 1 column 1 (char 0)"),
        ("a record that is a list", "[]", no_list),
        ("a record without a plugins object", '{"version": 2}', no_list),
        (
            "a record of another marketplace's name",
            json.dumps({"plugins": {"const-x@other-mp": [commit()]}}),
            no_list,
        ),
        (
            "a record whose entry for the id is an object",
            json.dumps({"plugins": {TOY_KEY: commit()}}),
            no_list,
        ),
        (
            "an entry whose installPath is another folder",
            recorded(commit(installPath=str(other))),
            f"holds no entry for {TOY_KEY} whose installPath is {copy}",
        ),
        (
            "entries that are no objects",
            json.dumps({"plugins": {TOY_KEY: ["x", 7]}}),
            f"holds no entry for {TOY_KEY} whose installPath is {copy}",
        ),
    ]
    for name, text, why in record_rows:
        expect(
            tally,
            f"the record: {name} is BROKEN for a remote source",
            new_scene(record=text),
            UNNAMED.format(why),
        )
    expect(tally, "the record: a commit gives the source at that commit", new_scene(), "on", [SHA])


def person_variable_cases(tally: Tally, step: StepTwo) -> dict[str, tuple[str, str]]:
    """None of the four plugin variables of the person reaches `claude`; the kept ones do."""
    base, copy, cache_log, drive, new_scene = step.base, step.copy, step.cache_log, step.drive, step.new_scene
    # none of the four variables reaches `claude`, whichever the person sets and to what: the platform's
    # plugins root is the check's own configuration's plugins/, where the record is read, and the folders
    # the person's variables name stay empty; the kept variables, PREFER_HTTPS, FAKE_KEEP and the seven
    # documented ones, reach it unchanged
    person_values = person_plugin_values(base)
    for variable, (what, set_value) in person_values.items():
        for name, value in ((what, set_value), ("set and empty", "")):
            driven = drive(new_scene(), {variable: value} | KEPT_VARS)
            seen_cache = cache_log.read_text(encoding="utf-8").splitlines() if cache_log.exists() else []
            version_case(
                tally,
                f"{variable} {name} in the person's environment: the marketplace add, the install and"
                " the list run with the four absent, CLAUDE_CODE_PLUGIN_PREFER_HTTPS, FAKE_KEEP and the"
                " seven documented ones as set, the record is read from the check's own configuration,"
                " and the folders stay empty",
                driven == ("on", [SHA], [str(copy)])
                and seen_cache
                == [
                    f"plugin marketplace{SEEN_WHEN_REMOVED}",
                    f"plugin install{SEEN_WHEN_REMOVED}",
                    f"plugin list{SEEN_WHEN_REMOVED}",
                ]
                and all(list(Path(f).iterdir()) == [] for _, f in person_values.values() if f != "1"),
                f"{driven} {seen_cache}",
            )
    return person_values


def record_entry_cases(tally: Tally, step: StepTwo) -> None:
    """The entry of the installed copy is the one read, whichever entries stand round it."""
    copy, other, commit, expect, new_scene = step.copy, step.other, step.commit, step.expect, step.new_scene
    wrong = commit(installPath=str(other), gitCommitSha=SHA_WRONG)
    right = commit(gitCommitSha=SHA_RIGHT)
    # an entry whose installPath is the copy's leaf name in another folder: the whole path decides
    same_leaf = commit(installPath=str(other / copy.name), gitCommitSha=SHA_WRONG)
    no_install_path: dict[str, object] = {"scope": "user", "gitCommitSha": SHA_WRONG}
    for name, entries in (
        ("an entry of another installPath first", (wrong, right)),
        ("an entry of another installPath last", (right, wrong)),
        ("an entry with the copy's leaf name in another folder first", (same_leaf, right)),
        ("an entry with the copy's leaf name in another folder between", (wrong, same_leaf, right)),
        ("an entry without an installPath first", (no_install_path, right)),
        ("an entry whose installPath is a number first", (commit(installPath=7), right)),
        ("an entry without an installPath, others round the right one", (wrong, no_install_path, right)),
    ):
        expect(
            tally,
            f"the record: the entry of the installed copy is the one read, {name}",
            new_scene(record=recorded(*entries)),
            "on",
            [SHA_RIGHT],
        )


def record_form_cases(tally: Tally, step: StepTwo) -> None:
    """A commit that is no git object id is BROKEN and never handed to git; one that is, is read at."""
    base, toy, commit, environment, expect, new_scene = (
        step.base,
        step.toy,
        step.commit,
        step.environment,
        step.expect,
        step.new_scene,
    )
    marker = base / "git-ran-this"  # made by `touch` if git is ever handed the next value as an option
    option = f"--upload-pack=touch {marker}"
    sha64 = "0123456789abcdef" * 4
    id_form = "40 or 64 lower-case hexadecimal characters"
    for name, value in (
        ("an option, -x", "-x"),
        ("an option that makes git run a command, --upload-pack", option),
        ("a word that is no hexadecimal", "not a sha"),
        ("a branch name", "main"),
        ("39 hexadecimal characters", SHA[:-1]),
        ("41 hexadecimal characters", SHA + "0"),
        ("63 hexadecimal characters", sha64[:-1]),
        ("65 hexadecimal characters", sha64 + "0"),
        ("an id in upper case, which git never writes", SHA.upper()),
        ("an id in mixed case", SHA[:20] + SHA[20:].upper()),
        ("an id with a line break after it", SHA + "\n"),
        ("an id with a space before it", " " + SHA),
        ("an abbreviated id", SHA[:7]),
        ("an id of 40 characters, one of them not hexadecimal", SHA[:-1] + "g"),
    ):
        expect(
            tally,
            f"the record: a commit that is {name} is BROKEN for a remote source, never handed to git",
            new_scene(record=recorded(commit(gitCommitSha=value))),
            UNNAMED.format(f"gitCommitSha is no git object id ({id_form}), {value!r}"),
        )
    for name, value in (("40 hexadecimal characters", SHA), ("64 hexadecimal characters", sha64)):
        expect(
            tally,
            f"the record: a commit of {name} is an object id: the source is read at it",
            new_scene(record=recorded(commit(gitCommitSha=value))),
            "on",
            [value],
        )
    long_value = "x" * 250
    expect(
        tally,
        "the record: a commit that is a long word is quoted, cut at 200 characters",
        new_scene(record=recorded(commit(gitCommitSha=long_value))),
        UNNAMED.format(f"gitCommitSha is no git object id ({id_form}), " + repr(long_value)[:200] + "…"),
    )
    git_kit = base / "git-kit"  # the toy kit as a git clone whose origin is itself: git can really be run
    shutil.copytree(toy, git_kit)
    for argv in (
        ["git", "init", "-q"],
        ["git", "add", "-A"],
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "toy"],
        ["git", "remote", "add", "origin", str(git_kit)],
    ):
        run(argv, git_kit, os.environ | {"GIT_CONFIG_GLOBAL": os.devnull})
    with (
        mock.patch.dict(os.environ, environment(new_scene(record=recorded(commit(gitCommitSha=option))))),
        patched_globals({"KIT": git_kit}),
    ):
        try:
            check_module("const-x", "owner/repo", PIN_NOTE)
            handed = "no Broken"
        except Broken as broken:
            handed = unrecord(str(broken))
    version_case(
        tally,
        "the record: a commit that is an option, with git really run, is BROKEN and git runs no command",
        handed.startswith("the install record names no commit for const-x@toy-mp (<record>:")
        and "gitCommitSha is no git object id" in handed
        and not marker.exists(),
        f"{handed} {marker.exists()}",
    )


def local_source_cases(tally: Tally, step: StepTwo) -> None:
    """A local folder is compared with itself, and a run asks the three claude commands in order."""
    other, fake_log, calls_log, no_sha, commit, drive, expect, new_scene = (
        step.other,
        step.fake_log,
        step.calls_log,
        step.no_sha,
        step.commit,
        step.drive,
        step.expect,
        step.new_scene,
    )
    for name, text in (
        ("no record", ""),
        ("a record that is no JSON", "not json"),
        ("a record without a commit", recorded(no_sha)),
        ("a record of another install", recorded(commit(installPath=str(other)))),
    ):
        expect(
            tally,
            f"the record: a local folder is compared with itself, {name} is read by no one",
            new_scene(record=text, source="local"),
            "on",
        )
    drive(new_scene())
    asked = fake_log.read_text(encoding="utf-8").splitlines()
    calls = [line.split(" | ") for line in calls_log.read_text(encoding="utf-8").splitlines()]
    version_case(
        tally,
        "a run asks the marketplace, the install with --json and the list with --json, in the bare"
        " repository and the configuration folder of the run",
        asked
        == ["plugin marketplace add owner/repo", f"plugin install {TOY_KEY} --json", "plugin list --json"]
        and len(calls) == 3
        and calls[0][1:] == calls[1][1:] == calls[2][1:]
        and calls[0][1].endswith("/repo")
        and calls[0][2].endswith("/config"),
        f"{asked} {calls}",
    )


def step_report_cases(tally: Tally, step: StepTwo) -> None:
    """The report of a run is its literal lines, the note at the end of each headline."""
    toy, linked, good, no_sha, lines_of, new_scene = (
        step.toy,
        step.linked,
        step.good,
        step.no_sha,
        step.lines_of,
        step.new_scene,
    )
    stop = "BROKEN: the check could not run — 0 modules examined"
    refused_lines = [  # typed by hand: a message function cannot check itself
        f"RED: const-x: Claude Code refuses to install it (not_found: {GONE}){{}}",
        f"  why: {WHY}",
        "  fix: fix its manifest or its entry in marketplace.json",
        "RED: 1 finding(s) — no install, from owner/repo{}",
    ]
    link_lines = [  # typed by hand: a module's link its copy lacks, a finding that is no refusal
        "RED: const-x: the link linked is missing in the installed copy{}",
        f"  why: {WHY}",
        "  fix: replace the link inside the plugin with the file it points at",
        f"RED: 1 finding(s) — 0 hook(s), 0 scan(s), 1 link(s), from {linked}{{}}",
    ]
    reports: list[tuple[str, Scene, str, bool, int, list[str]]] = [
        (
            "a green run, off the pin",
            new_scene(source="local"),
            SAYS_OFF,
            True,
            EXIT_GREEN,
            [f"{GREEN_LINE} — 0 hook(s), 0 scan(s), 0 link(s), from {toy}{OFF_PIN}"],
        ),
        (
            "a green run, on the pin",
            new_scene(source="local"),
            SAYS_PINNED,
            False,
            EXIT_GREEN,
            [f"{GREEN_LINE} — 0 hook(s), 0 scan(s), 0 link(s), from {toy}"],
        ),
        (
            "a finding of the installed copy, off the pin",
            new_scene(source="linked"),
            SAYS_OFF,
            True,
            EXIT_RED,
            [line.format(OFF_PIN) for line in link_lines],
        ),
        (
            "a finding of the installed copy, on the pin",
            new_scene(source="linked"),
            SAYS_PINNED,
            False,
            EXIT_RED,
            [line.format("") for line in link_lines],
        ),
        (
            "a refusal, off the pin",
            new_scene(out=FAILED_LINE, code=1),
            SAYS_OFF,
            True,
            EXIT_RED,
            [line.format(OFF_PIN) for line in refused_lines],
        ),
        (
            "a refusal, on the pin",
            new_scene(out=FAILED_LINE, code=1),
            SAYS_PINNED,
            False,
            EXIT_RED,
            [line.format("") for line in refused_lines],
        ),
        (
            "an install that printed nothing, off the pin",
            new_scene(out=""),
            SAYS_OFF,
            True,
            EXIT_BROKEN,
            [
                f"BROKEN: {INSTALL_COMMAND} printed nothing on standard output (exit 0)" + OFF_FIX + OFF_PIN,
                stop + OFF_PIN,
            ],
        ),
        (
            "an install that printed nothing, on the pin",
            new_scene(out=""),
            SAYS_PINNED,
            False,
            EXIT_BROKEN,
            [f"BROKEN: {INSTALL_COMMAND} printed nothing on standard output (exit 0){INSTALL_FIX}", stop],
        ),
        (
            "an install record without a commit, off the pin",
            new_scene(record=recorded(no_sha)),
            SAYS_OFF,
            True,
            EXIT_BROKEN,
            [UNNAMED_OFF.format("gitCommitSha is absent") + OFF_PIN, stop + OFF_PIN],
        ),
        (
            "a list without the install, off the pin",
            new_scene(listing="[]"),
            SAYS_OFF,
            True,
            EXIT_BROKEN,
            [
                f"BROKEN: {LISTING_COMMAND} {NO_ENTRY.format('no entries')}{OFF_FIX}{OFF_PIN}",
                stop + OFF_PIN,
            ],
        ),
        (
            "a list that exits 1, off the pin",
            new_scene(listing=good, list_code=1),
            SAYS_OFF,
            True,
            EXIT_BROKEN,
            [f"BROKEN: {LISTING_COMMAND} exited 1 ({good}){FIX_EXITED_OFF}{OFF_PIN}", stop + OFF_PIN],
        ),
        (
            "a list that exits 1, on the pin",
            new_scene(listing=good, list_code=1),
            SAYS_PINNED,
            False,
            EXIT_BROKEN,
            [f"BROKEN: {LISTING_COMMAND} exited 1 ({good}){FIX_EXITED}", stop],
        ),
    ]
    for name, scene, says, optout, status_wanted, lines_wanted in reports:
        got_status, got_lines = lines_of(scene, says, optout)
        version_case(
            tally,
            f"the report of {name} is its literal lines, the note at the end of each headline",
            (got_status, got_lines) == (status_wanted, lines_wanted),
            f"{got_status} {got_lines}",
        )


def person_variable_run_case(tally: Tally, step: StepTwo, person_values: dict[str, tuple[str, str]]) -> None:
    """The kit's own variables are read by the check itself, not taken away with the four."""
    toy, cache_log, environment, new_scene = step.toy, step.cache_log, step.environment, step.new_scene
    # the kit's own variables are read by the check itself, not taken away with the four: the source is
    # CONSTITUTION_KIT_INSTALL_FROM and the run on another version goes on by CONSTITUTION_KIT_ANY_CLAUDE
    # while all four are set; the fake claude, run by the same check, holds none of the four
    env_kit = {variable: set_value for variable, (_, set_value) in person_values.items()}
    env_kit |= KEPT_VARS | {FROM_ENV: str(toy), "CONSTITUTION_KIT_ANY_CLAUDE": "1"}
    env_kit |= environment(new_scene(source="local"), SAYS_OFF)
    printed_kit = io.StringIO()
    with (
        mock.patch.dict(os.environ, env_kit),
        patched_globals({"KIT": toy}),
        contextlib.redirect_stdout(printed_kit),
    ):
        status_kit = main(["--module", "const-x"])
    seen_kit = cache_log.read_text(encoding="utf-8").splitlines() if cache_log.exists() else []
    version_case(
        tally,
        "all four set in the person's environment, with CONSTITUTION_KIT_INSTALL_FROM and"
        " CONSTITUTION_KIT_ANY_CLAUDE=1: both still read by the check (the source, the run on another"
        " version with its note), and every claude command runs with the four absent",
        (status_kit, [unrecord(line) for line in printed_kit.getvalue().splitlines()])
        == (EXIT_GREEN, [f"{GREEN_LINE} — 0 hook(s), 0 scan(s), 0 link(s), from {toy}{OFF_PIN}"])
        and seen_kit
        == [
            f"--version {SEEN_WHEN_REMOVED}",
            f"plugin marketplace{SEEN_WHEN_REMOVED}",
            f"plugin install{SEEN_WHEN_REMOVED}",
            f"plugin list{SEEN_WHEN_REMOVED}",
        ],
        f"{status_kit} {printed_kit.getvalue()!r} {seen_kit}",
    )


def unreadable_file_cases(tally: Tally, step: StepTwo) -> None:
    """A file the run cannot read is the two BROKEN lines, the note at the end of each."""
    no_kernel, lines_of, new_scene = step.no_kernel, step.lines_of, step.new_scene
    unreadable_lines = [  # typed by hand: a file the run could not read, after the version is known
        f"BROKEN: a file could not be read ([Errno 2] No such file or directory: '{no_kernel}/kernel')"
        " — fix: make the module's files readable{}",
        "BROKEN: the check could not run — 0 modules examined{}",
    ]
    for name, says, optout, note_wanted in (
        ("off the pin", SAYS_OFF, True, OFF_PIN),
        ("on the pin", SAYS_PINNED, False, ""),
    ):
        got_status, got_lines = lines_of(new_scene(), says, optout, no_kernel)
        version_case(
            tally,
            f"a file the run cannot read, {name}: the two BROKEN lines, the note at the end of each",
            (got_status, got_lines) == (EXIT_BROKEN, [line.format(note_wanted) for line in unreadable_lines]),
            f"{got_status} {got_lines}",
        )


def unmade_path(root: Path, shared: Path | None = None, path: str | None = None) -> str:
    """`shared_path` without the environment: the PATH it would put the environment's bin before. The cases of
    the platform's replies and of the report run over it, since each makes a run and the environment of a run
    is held by the cases of `shared_environment_cases` and `shared_path_run_case`."""
    return os.environ.get("PATH", "") if path is None else path


def step_two_cases(tally: Tally) -> None:
    """Step 2 over a toy kit, its marketplace named toy-mp, and a fake claude."""
    with tempfile.TemporaryDirectory() as tmp:
        step = step_two_scene(Path(tmp).resolve())
        with patched_globals({"shared_path": unmade_path}):
            install_reply_cases(tally, step)
            list_reply_cases(tally, step)
            list_exit_cases(tally, step)
            record_cases(tally, step)
            person_values = person_variable_cases(tally, step)
            record_entry_cases(tally, step)
            record_form_cases(tally, step)
            local_source_cases(tally, step)
            step_report_cases(tally, step)
            person_variable_run_case(tally, step, person_values)
            unreadable_file_cases(tally, step)
        shared_path_run_case(tally, step)


def source_at_commit_case(tally: Tally) -> None:
    """The source at a commit is read from the kit's own history."""
    with tempfile.TemporaryDirectory() as tmp:  # the kit's own history: the source at the commit checked out
        head = run(["git", "rev-parse", "HEAD"], KIT, os.environ.copy())[1]
        root = Path(tmp).resolve()
        extracted = source_at(head, "const-meta-types", root)
        ok = extracted == root / "source" / "modules" / "const-meta-types" / "plugin"
        shared_code = extracted / "scripts" / "constitution_layer_kit"
        ok = (
            ok
            and (extracted.parent / "MODULE.md").is_file()
            and (extracted / "hooks" / "hooks.json").is_file()
            and not (shared_code.is_symlink() or shared_code.exists())  # the plugin holds no shared code
            and not (root / "source" / "shared").exists()  # and none is read for it
        )
    tally.failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the source at a commit is read from the kit's history")


def shared_path_run_case(tally: Tally, step: StepTwo) -> None:
    """A run over the toy kit makes the environment of its shared package, and gives its PATH to the three
    `claude` commands of the install and to the check of the hooks and scans."""
    paths_log = step.base / "paths.log"
    handed: list[str | None] = []

    def source_spy(at: str, name: str, root: Path) -> Path:
        return step.toy / "modules" / name / "plugin"

    def installed_spy(
        name: str, src: Path, plugin: Path, repo: Path, data: Path, path: str | None = None
    ) -> list[Finding]:
        handed.append(path)
        return []

    scene = step.new_scene()
    environment = step.environment(scene) | {"FAKE_PATHS": str(paths_log)}
    with (
        mock.patch.dict(os.environ, environment),
        patched_globals({"KIT": step.toy, "source_at": source_spy, "check_installed": installed_spy}),
    ):
        check_module("const-x", "owner/repo", PIN_NOTE)
    seen = [line.split("|") for line in paths_log.read_text(encoding="utf-8").splitlines()]
    heads = {head for _, head in seen}
    head = next(iter(heads))
    version_case(
        tally,
        "a run makes the environment of the shared package, and the marketplace, the install and the list"
        " run with its bin first on PATH, the hooks and scans with the same PATH, the person's after it",
        [words for words, _ in seen] == ["plugin marketplace", "plugin install", "plugin list"]
        and len(heads) == 1
        and head.endswith(f"/{SHARED_ENV}/bin")
        and handed == [f"{head}{os.pathsep}{environment['PATH']}"],
        f"{seen} {handed}",
    )


def says_mark(python: Path, env: dict[str, str], cwd: Path) -> str:
    """What `python` says for `import constitution_layer_kit, yaml`: the package's MARK, else the last line
    of its error."""
    done = subprocess.run(
        [str(python), "-c", "import constitution_layer_kit as c, yaml; print(c.MARK)"],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return done.stdout.strip() or last_line("", done.stderr.strip())


def shared_made_cases(tally: Tally, base: Path, shared: Path) -> None:
    """The environment `shared_path` makes over the toy kit's `shared/`: its PATH, its `.pth` file, what its
    python3 imports, and a release in the user's site-packages that never comes first."""
    work = base / "work"
    work.mkdir()
    root = work / "made"
    root.mkdir()
    bin_folder = root / SHARED_ENV / "bin"
    given = shared_path(root, shared, "/where")
    env = dict(os.environ)
    pth = next((root / SHARED_ENV / "lib").glob(f"python3*/site-packages/{SHARED_PTH}"), None)
    named = pth.read_text(encoding="utf-8") if pth else "no .pth file"
    mark = says_mark(bin_folder / "python3", env, work)
    version_case(
        tally,
        "the shared step: the PATH is the environment's bin first and the PATH given after it; its .pth file"
        " names the kit's shared/ and nothing else; its python3 imports the kit's shared package and PyYAML",
        given == f"{bin_folder}{os.pathsep}/where" and named == f"{shared}\n" and mark == TOY_MARK,
        f"{given!r} {named!r} {mark!r}",
    )
    by_default_root, by_empty_root = work / "by-default", work / "by-empty"
    by_default_root.mkdir()
    by_empty_root.mkdir()
    with mock.patch.dict(os.environ, {"PATH": "/x:/y"}):
        by_default = shared_path(by_default_root, shared)
    by_empty = shared_path(by_empty_root, shared, "")
    version_case(
        tally,
        "the shared step: with no PATH given the person's is put after the bin, and an empty one leaves the"
        " bin alone",
        by_default == f"{by_default_root}/{SHARED_ENV}/bin{os.pathsep}/x:/y"
        and by_empty == f"{by_empty_root}/{SHARED_ENV}/bin",
        f"{by_default!r} {by_empty!r}",
    )
    user = base / "user"
    asked = subprocess.run(
        [sys.executable, "-c", "import site; print(site.getusersitepackages())"],
        env=env | {"PYTHONUSERBASE": str(user)},
        capture_output=True,
        text=True,
        check=False,
    )
    release = Path(asked.stdout.strip()) / "constitution_layer_kit"
    release.mkdir(parents=True)
    (release / "__init__.py").write_text('MARK = "release"\n', encoding="utf-8")
    with_release = env | {"PYTHONUSERBASE": str(user)}
    own, inside = (
        says_mark(Path(sys.executable), with_release, work),
        says_mark(bin_folder / "python3", with_release, work),
    )
    version_case(
        tally,
        "the shared step: a release installed in the user's site-packages, which the python3 that runs the"
        " check imports, is never imported by the environment's python3, the kit's shared/ comes first",
        inside == TOY_MARK and (own == "release" or not site.ENABLE_USER_SITE),
        f"environment {inside!r}, the check's own python3 {own!r}",
    )


def shared_failed_cases(tally: Tally, base: Path, shared: Path) -> None:
    """Each way `shared_path` fails is one BROKEN line with its fix."""
    work = base / "failures"
    work.mkdir()

    def fresh(name: str) -> Path:
        (work / name).mkdir()
        return work / name

    empty = fresh("no-kit")
    got = result_of(lambda: shared_path(empty, base / "bare-kit"))
    version_case(
        tally,
        "the shared step: a kit with no shared/constitution_layer_kit/ is BROKEN, the fix a clone of the kit",
        got
        == f"BROKEN: the shared code is not at {base}/bare-kit/constitution_layer_kit — fix: run the check"
        " from a clone of the kit, which holds shared/constitution_layer_kit/",
        got,
    )
    root = fresh("no-venv")
    broken_python = work / "python3"
    broken_python.write_text("#!/bin/sh\necho 'venv is broken' >&2\nexit 3\n", encoding="utf-8")
    broken_python.chmod(0o755)
    with mock.patch.object(sys, "executable", str(broken_python)):
        got = result_of(lambda: shared_path(root, shared))
    version_case(
        tally,
        "the shared step: a python3 whose venv fails is BROKEN, the command, its exit and its last line"
        " named, the fix to run it by hand",
        got == f"BROKEN: {broken_python} -m venv --system-site-packages --without-pip {root}/{SHARED_ENV}"
        " exited 3 (venv is broken) — fix: run that command by hand and read why it fails, then run the"
        " check again",
        got,
    )
    root = fresh("no-pth")
    real_write = Path.write_text

    def refuse(self: Path, *args: Any, **kwargs: Any) -> int:
        if self.name == SHARED_PTH:
            raise PermissionError(errno.EACCES, "Permission denied")
        return real_write(self, *args, **kwargs)

    with mock.patch.object(Path, "write_text", refuse):
        got = result_of(lambda: shared_path(root, shared))
    version_case(
        tally,
        "the shared step: a .pth file that cannot be written is BROKEN, the file named and the fix to make"
        " the check's folder writable",
        got.startswith(f"BROKEN: {root}/{SHARED_ENV}/lib/python3")
        and f"/site-packages/{SHARED_PTH} could not be written (Permission denied) — fix: make the folder"
        f" {root} writable, then run the check again"
        in got,
        got,
    )
    root = fresh("no-import")
    unimportable = toy_shared(base / "unimportable-kit", 'raise ImportError("toy broken")\n')
    got = result_of(lambda: shared_path(root, unimportable))
    version_case(
        tally,
        "the shared step: a shared package the new environment cannot import is BROKEN, its error quoted, the"
        " fix PyYAML for the python3 that runs the check and a run by hand",
        got.startswith("BROKEN: the new environment cannot import the shared code and PyYAML (ImportError:")
        and "toy broken) — fix: PyYAML must be installed for the python3 that runs the check" in got,
        got,
    )
    other = base / "other-copy"
    (other / "constitution_layer_kit").mkdir(parents=True)
    (other / "constitution_layer_kit" / "__init__.py").write_text('MARK = "other"\n', encoding="utf-8")
    root = fresh("other-first")
    with mock.patch.dict(os.environ, {"PYTHONPATH": str(other)}):
        got = result_of(lambda: shared_path(root, shared))
    version_case(
        tally,
        "the shared step: another copy of the package first on sys.path, a PYTHONPATH's, is BROKEN, the copy"
        " found and the shared/ expected named, the fix to unset PYTHONPATH",
        got
        == f"BROKEN: the new environment imports constitution_layer_kit from {other}/constitution_layer_kit,"
        f" not from {shared}/constitution_layer_kit — fix: take the other copy off the way for this run:"
        " unset PYTHONPATH, which puts a folder first, then run the check again",
        got,
    )


def shared_outer_case(tally: Tally, base: Path, shared: Path) -> None:
    """A check that runs under a virtual environment: the new environment sees that one's packages."""
    outer = base / "outer"
    done = subprocess.run(
        [sys.executable, "-m", "venv", "--system-site-packages", "--without-pip", str(outer)],
        capture_output=True,
        text=True,
        check=False,
    )
    site_packages = next((outer / "lib").glob("python3*/site-packages"), outer)
    (site_packages / "outer_only.py").write_text("WHERE = 'outer'\n", encoding="utf-8")
    root = base / "work" / "under-venv"
    root.mkdir()
    code = (
        f"import sys; sys.path.insert(0, {str(Path(__file__).resolve().parent)!r}); import kit_install;"
        f" from pathlib import Path; print(kit_install.shared_path(Path({str(root)!r}),"
        f" Path({str(shared)!r}), ''))"
    )
    ran = subprocess.run(
        [str(outer / "bin" / "python3"), "-c", code], cwd=base, capture_output=True, text=True, check=False
    )
    made = ran.stdout.strip()
    seen = subprocess.run(
        [str(Path(made) / "python3"), "-c", "import outer_only, constitution_layer_kit as c; print(c.MARK)"],
        cwd=base,
        capture_output=True,
        text=True,
        check=False,
    )
    version_case(
        tally,
        "the shared step under a virtual environment: the new environment imports a package of that one,"
        " where a plain venv would not, and the kit's shared package as before",
        done.returncode == 0 and seen.stdout.strip() == TOY_MARK,
        f"{done.stderr.strip()} {ran.stderr.strip()} {made} {seen.stderr.strip()}",
    )


def linkless_plugin(root: Path) -> Path:
    """The plugin of a toy module whose hook and scan import the shared package and hold it to be the toy
    kit's, with no link to the shared code beside them; the plugin folder."""
    module = root / "module"
    plugin = module / "plugin"
    (plugin / "hooks").mkdir(parents=True)
    (plugin / "scripts").mkdir()
    script = (
        f"import constitution_layer_kit\nassert constitution_layer_kit.MARK == {TOY_MARK!r}\nprint('rule')\n"
    )
    (plugin / "scripts" / "entry.py").write_text(script, encoding="utf-8")
    (plugin / "scripts" / "check-p.py").write_text(script, encoding="utf-8")
    hook = {"type": "command", "command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/entry.py"]}
    (plugin / "hooks" / "hooks.json").write_text(
        json.dumps({"hooks": {"SessionStart": [{"hooks": [hook]}]}}), encoding="utf-8"
    )
    (module / "MODULE.md").write_text(
        '<a id="t9"></a>\n| E1 | `check-p.py --scan` | `gate` |\n<a id="t10"></a>\n', encoding="utf-8"
    )
    return plugin


def shared_hook_cases(tally: Tally, base: Path, shared: Path) -> None:
    """A hook and a scan that import the shared package with no link beside them pass only with the PATH of
    the environment, the one `check_installed` is given: the red without it, the green with it."""
    plugin = linkless_plugin(base / "linkless")
    (base / "repo" / "docs").mkdir(parents=True)
    (base / "data").mkdir()
    root = base / "work" / "linkless-env"
    root.mkdir()
    path = shared_path(root, shared)
    green = check_installed("const-x", plugin, plugin, base / "repo", base / "data", path)
    red = check_installed("const-x", plugin, plugin, base / "repo", base / "data")
    version_case(
        tally,
        "a hook and a scan that import the shared package, a plugin with no link to it, are green with the"
        " environment's PATH, and red without it: the hook exits 1 and the scan exits 1",
        green == []
        and len(red) == 2
        and "its SessionStart hook `<plugin>/scripts/entry.py` exits 1 on a bare repository" in red[0].what
        and "its scan `check-p.py --scan` exits 1 on a bare repository" in red[1].what,
        f"{green} {red}",
    )


def shared_environment_cases(tally: Tally) -> None:
    """The shared step of `kit_install` (decision dec-0099-shared-code-installed-as-a-pip-package, R17) over a
    toy kit: the environment it makes, each failure, a check under a virtual environment, and the red and
    the green of a plugin that imports the shared package with no link."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp).resolve()
        shared = toy_shared(base / "kit")
        shared_made_cases(tally, base, shared)
        shared_failed_cases(tally, base, shared)
        shared_outer_case(tally, base, shared)
        shared_hook_cases(tally, base, shared)


def self_test() -> int:
    """Red→green on throwaway source and copy folders, no install: a green copy is green; each branch
    of the link check — a link inside the plugin, the runner's link to its own package arrived as a
    directory, leading elsewhere, dangling or missing, a link left a link, missing, with files lost, added or
    changed, a file link with other bytes or arrived as a folder, a link the source lacks — each branch of
    the hooks-file, hook and scan checks, and a red scan the source declares where the copy holds no
    document, are each a finding; a source document that cannot be read is a teaching BROKEN line, and
    the scans are read from rows of each form; the report of one finding is its literal text, exit 2."""
    tally = Tally()
    link_cases(tally)
    unreadable_cases(tally)
    scan_row_case(tally)
    report_cases(tally)
    marketplace_case(tally)
    hook_wait_cases(tally)
    start_and_lookup_cases(tally)
    bare_repository_cases(tally)
    version_check_cases(tally)
    step_two_cases(tally)
    source_at_commit_case(tally)
    shared_environment_cases(tally)
    total = len(LINK_CASES) + len(UNREADABLE_CASES) + 6 + tally.extra
    print(f"{total - tally.failed}/{total} cases green")
    return EXIT_GREEN if tally.failed == 0 else EXIT_RED


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
    note = ""  # set once the version is asked, and ends every headline line the run prints after it
    try:
        if args.self_test:
            return self_test()
        module = str(args.module)
        source = args.source or os.environ.get(FROM_ENV) or str(KIT)
        if there(Path(source)):  # the install runs in another folder, so a local source is made absolute
            source = str(Path(source).resolve())
        claude = claude_noted(KIT, dict(os.environ))  # before any other `claude` command, once per run
        note = claude
        findings, examined = check_module(module, source, claude)
        return report(module, findings, f"{examined}, from {source}", note)
    except Broken as broken:
        print(f"BROKEN: {broken}{note}")
        print(f"BROKEN: the check could not run — 0 modules examined{note}")
        return EXIT_BROKEN
    except OSError as bad:
        print(f"BROKEN: a file could not be read ({bad}) — fix: make the module's files readable{note}")
        print(f"BROKEN: the check could not run — 0 modules examined{note}")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
