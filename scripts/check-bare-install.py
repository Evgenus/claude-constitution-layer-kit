#!/usr/bin/env python3
"""Kit check: a module installs through Claude Code and operates on a bare repository with its
defaults alone — requirements A12.1 to A12.3, kernel plus one module (decision
dec-0059-bare-repo-install-in-ci).

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
     configuration failure. The source is --from, else the environment's CONSTITUTION_KIT_INSTALL_FROM,
     else the kit's working folder. The kit's CI names the change's GitHub repository and branch,
     `<owner>/<repo>#<branch>` — a pull request's head repository and branch, or the kit's main on
     a push to it — the copy a consumer's install writes; a fork the job's token cannot read fails; git
     clones it with the machine's own credentials, which a private remote needs. The working
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
     folder is compared with that folder and reads no record;
  3. what the kit's source of the module declares, held in that copy: no link of the source
     leads inside the module, save the fixture runner's link tests/<package> -> ../scripts/<package>
     to a package of the module's own (as own_packages of kit_module_doc derives them: a folder of
     scripts/, itself no link, holding an __init__.py, its name starting with neither `.` nor `_`,
     save const_gate), which arrives as a link leading to that
     package in the copy — the platform keeps a link that stays inside the plugin; every
     other link arrives as a real file, or a real directory, with the
     same files byte for byte; the copy holds no link the source lacks; the copy holds
     the source's hooks file; every hook of the source's hooks/hooks.json, which is a `command` hook
     (`hooks_of`: a hook of another type, `http`, `mcp_tool`, `prompt` or `agent`, is a failure to run, since
     the check cannot prove a hook it does not run), run from the copy in
     exec form on a sample event of its kind with CLAUDE_PLUGIN_ROOT set to the copy, exits 0 on
     the bare repository, and its JSON on standard output neither blocks, denies, asks nor stops,
     each waited for its own `timeout`, else the seconds the hooks reference gives a `command` hook
     on its event: 600, but 30 on UserPromptSubmit, PreModelSwitch and PostModelSwitch, 10 on
     MessageDisplay and 1.5 on SessionEnd;
     every scan the source declares in its enforcement section (template §9), run from the copy,
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
state of the run: on the pinned version, to update the kit's reader that the line names (`install_scope`,
`listed_install` or `installed_commit`), to what that version writes; off the pin, to run again on the
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
                         from the kit's history (const-meta-types at HEAD, its links reaching shared/); and
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
                         a run off the pin, a finding's and a green one's, as literal lines.
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
import stat
import subprocess
import sys
import tarfile
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import partial
from pathlib import Path
from unittest import mock

from kit_module_doc import (
    DocumentError,
    Note,
    claude_env,
    claude_note,
    command_fix,
    enforcement,
    marketplace_name,
    own_packages,
    platform_fix,
)

KIT = Path(__file__).resolve().parent.parent
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
WHY = "a module must install and operate on a bare repository with its defaults alone (requirement A12.1)"
NOTE = "docs/note.md"
FROM_ENV = "CONSTITUTION_KIT_INSTALL_FROM"
INSTALL_TIMEOUT = 300  # seconds the install is given, kit tuning and no platform fact
OBJECT_ID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")  # a git object id as git writes one: SHA-1 or SHA-256
SCRIPT = "scripts/check-bare-install.py"  # named in the fix of a reply the check's readers do not read
LIST_WHERE = (
    "a folder of your own, CLAUDE_CONFIG_DIR set to an empty folder"  # where the failed list is run again
)
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


class Broken(Exception):
    """The check could not run; the message says why and how to fix it."""


class Refused(Exception):
    """The platform refused to install the module: a finding against the module."""


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


RUN_FIX = (
    "give it a command that exists and can run, with no NUL byte in it or its arguments: a program on"
    " PATH, or a file with the execute permission (`chmod u+x` it), then run the check again"
)


HOOK_RUN_FIX = (
    'give the hook\'s "command" and "args" in the module\'s hooks/hooks.json a command that exists and can'
    " run, with no NUL byte in it or its arguments: a program on PATH, or a file of the module with the"
    " execute permission (`chmod u+x` it, and commit the mode), then run the check again"
)


def plain(command: str) -> str:
    """A command as a message echoes it: a plain word as it is, else as `shown` quotes it, so that one with a
    space, a quote, a line break or no characters at all reads as one token."""
    return command if re.fullmatch(r"[\w@%+=:,./-]+", command) else shown(command)


def run(
    argv: list[str],
    cwd: Path,
    env: dict[str, str],
    stdin: str = "",
    timeout: float = 300,
    fix: str = RUN_FIX,
) -> tuple[int, str, str]:
    """The exit, the standard output and the standard error of one command. A command that is not found
    is a Broken saying to install it, as `plain` echoes it, and a working folder that does not exist a
    Broken of its own, naming the folder; any other `OSError` of starting it (an empty command, a file with no
    execute permission, a folder that cannot be searched) and a `ValueError` (a NUL byte) are a Broken that
    names the command, as `shown` quotes it, and the reason, with `fix` to follow; one that outlasts its
    `timeout` is the exit 124."""
    try:
        done = subprocess.run(
            argv, cwd=cwd, env=env, input=stdin, capture_output=True, text=True, timeout=timeout, check=False
        )
    except FileNotFoundError as bad:
        if not os.path.isdir(cwd):  # the working folder is what is missing, whichever command is asked for
            raise Broken(
                f"the working folder {cwd} does not exist — fix: make the folder"
                f" (`mkdir -p {shlex.quote(str(cwd))}`), then run the check again"
            ) from bad
        raise Broken(
            f"{plain(argv[0])} is not installed ({bad.strerror}) — fix: install it and put it on PATH"
        ) from bad
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout} s"
    except (OSError, ValueError) as bad:
        why = (bad.strerror if isinstance(bad, OSError) else None) or str(bad)
        raise Broken(f"the command {shown(argv)} could not be started ({why}) — fix: {fix}") from bad
    return done.returncode, done.stdout.strip(), done.stderr.strip()


def looked_up(path: Path, follow: bool = True) -> os.stat_result | None:
    """What `os.stat` says of a path (`os.lstat` when `follow` is False): None for a path that is not
    there (no entry, a path through a file, a link loop, a name that holds a NUL byte), a Broken for a
    path that cannot be looked up (a folder on the way cannot be searched, an I/O error). The check asks
    this and not `Path.is_file`, `is_dir` or `exists`: from release 3.14 of the language on they return
    False for the error that earlier releases raise, and the answer would differ by version, a path the
    check cannot look at read as a missing one."""
    try:
        return path.stat() if follow else path.lstat()
    except (FileNotFoundError, NotADirectoryError, ValueError):
        return None
    except OSError as bad:
        if bad.errno == errno.ELOOP:
            return None
        why = bad.strerror or str(bad)
        if bad.errno == errno.EACCES:
            folder = blocking_folder(path)
            fix = f"give the folder {folder} search permission, `chmod u+rx {shlex.quote(str(folder))}`"
        else:
            folder = path.parent
            fix = f"make the folder {folder} searchable, `ls -ld {shlex.quote(str(folder))}` shows why not"
        raise Broken(f"{path} cannot be searched ({why}) — fix: {fix}, then run the check again") from bad


def blocking_folder(path: Path) -> Path:
    """The folder on the way to a path that refuses the search: the first, from the root down, below which
    `os.stat` is denied; the path's own folder when none is."""
    chain = [*reversed(path.parents), path]
    for folder, below in zip(chain, chain[1:], strict=False):
        try:
            os.stat(below)
        except PermissionError:
            return folder
        except OSError:
            continue
    return path.parent


def file_at(path: Path) -> bool:
    """Whether a regular file (or a link to one) stands at the path; a Broken where it cannot be looked up."""
    found = looked_up(path)
    return found is not None and stat.S_ISREG(found.st_mode)


def folder_at(path: Path) -> bool:
    """Whether a folder (or a link to one) stands at the path; a Broken where it cannot be looked up."""
    found = looked_up(path)
    return found is not None and stat.S_ISDIR(found.st_mode)


def there(path: Path) -> bool:
    """Whether anything stands at the path (a link is followed); a Broken where it cannot be looked up."""
    return looked_up(path) is not None


def link_at(path: Path) -> bool:
    """Whether a link stands at the path, itself and not what it leads to; a Broken where it cannot be
    looked up."""
    found = looked_up(path, follow=False)
    return found is not None and stat.S_ISLNK(found.st_mode)


def last_line(out: str, err: str) -> str:
    said = err or out
    return said.splitlines()[-1] if said else "no output"


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
    try:
        mode = path.stat().st_mode  # follows a link; `is_file` hides a PermissionError from release 3.14 on
    except (FileNotFoundError, NotADirectoryError):  # no file, a dangling link, a path through a file
        return []
    except OSError as bad:
        if bad.errno == errno.ELOOP:  # a link loop leads to no file either
            return []
        # the place cannot be looked up: no file to read, no shape to restore
        raise Broken(
            f"{path} cannot be looked up ({bad.strerror}) — fix: make its folder {path.parent} searchable"
            f" (its permissions), so that the check can find hooks/hooks.json and read each hook it runs"
        ) from bad
    if not stat.S_ISREG(mode):  # a folder in the file's place
        return []
    fix = (
        "restore hooks/hooks.json to the shape the hooks reference gives,"
        " so that the check can read each hook it runs"
    )

    def unreadable(detail: str) -> Broken:
        return Broken(f"{path} is not a hooks file ({detail}) — fix: {fix}")

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as bad:  # the file is there and cannot be read: no shape to restore
        raise Broken(
            f"{path} cannot be read ({bad.strerror}) — fix: make it a readable file (its"
            f" permissions), or restore it with git checkout -- {path}, so that the check can read each"
            f" hook it runs"
        ) from bad
    except ValueError as bad:  # not UTF-8
        raise unreadable(str(bad)) from bad
    try:
        data: object = json.loads(text)
    except (ValueError, RecursionError) as bad:
        raise unreadable(str(bad)) from bad
    if not isinstance(data, dict):
        raise unreadable(f"the top level is {shown(data)}, not a JSON object")
    if "hooks" not in data:
        raise unreadable('the top level has no "hooks" key')
    table = data["hooks"]
    if not isinstance(table, dict):
        raise unreadable(f'"hooks" is {shown(table)}, not an object of events')
    found: list[Hook] = []
    for event, groups in table.items():
        if not isinstance(groups, list):
            raise unreadable(f"event {shown(event)}: {shown(groups)} is no list of groups")
        for number, group in enumerate(groups, 1):
            in_group = f"event {shown(event)}, group {number}"
            if not isinstance(group, dict):
                raise unreadable(f"{in_group}: {shown(group)} is no object")
            if "hooks" not in group:
                raise unreadable(f'{in_group}: no "hooks" key')
            if not isinstance(group["hooks"], list):
                raise unreadable(f'{in_group}: "hooks" is {shown(group["hooks"])}, not a list')
            matcher = group.get("matcher", "")
            if not isinstance(matcher, str):
                raise unreadable(f'{in_group}: "matcher" is {shown(matcher)}, not a string')
            for place, hook in enumerate(group["hooks"], 1):
                where = f"{in_group}, hook {place}"
                if not isinstance(hook, dict):
                    raise unreadable(f"{where}: {shown(hook)} is no object")
                kind = hook.get("type")
                if "type" not in hook:
                    raise unreadable(f'{where}: "type" is absent')
                if kind not in HOOK_TYPES:
                    raise unreadable(f'{where}: "type" is {shown(kind)}, not one of {", ".join(HOOK_TYPES)}')
                if kind != "command":
                    raise Broken(
                        f"{path} holds a hook of type {kind} ({where}) that check-bare-install does not run"
                        f" — it runs only `command` hooks, and cannot prove a hook it does not run"
                        f" — fix: make it a `command` hook, or teach `hooks_of` and `check_installed` in"
                        f" {SCRIPT} to run a {kind} hook"
                    )
                if "command" not in hook:
                    raise unreadable(f'{where}: "command" is absent')
                if not isinstance(hook["command"], str):
                    raise unreadable(f'{where}: "command" is {shown(hook["command"])}, not a string')
                args = hook.get("args", [])
                if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
                    raise unreadable(f'{where}: "args" is {shown(args)}, not a list of strings')
                seconds = EVENT_HOOK_TIMEOUT.get(event, HOOK_TIMEOUT)
                if "timeout" in hook:
                    declared = declared_seconds(hook["timeout"])
                    if declared is None:
                        raise unreadable(
                            f'{where}: "timeout" is {shown(hook["timeout"])}, not a finite number of seconds'
                        )
                    seconds = declared
                found.append(Hook(event, matcher, hook["command"], tuple(args), seconds))
    return found


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


def declared_scans(plugin: Path) -> list[str]:
    document = plugin / "MODULE.md"
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
    """No link of the source leads inside the module, save the runner's link to a package of the
    module's own, which arrives as a link leading to that package in the copy; every other link
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
            "replace the link inside the module with the file it points at"
            if inside
            else "the install must carry what it runs — fire the fallback of limit 3 of"
            " shared/GATE.md §4, links replaced by copies"
        )
        if link_at(place) or not there(place):
            state = "left a link" if link_at(place) else "missing"
            findings.append(Finding(module, f"the link {where} is {state} in the installed copy", fix))
        elif inside:
            findings.append(Finding(module, f"the link {where} leads inside the module", fix))
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


def check_installed(module: str, source: Path, plugin: Path, repo: Path, data: Path) -> list[Finding]:
    """What the kit's source of the module promises, held in its installed copy on a bare repository."""
    # The hooks file is looked up before the walks of `link_findings`, so that a hooks folder of the source
    # or of the copy that cannot be searched is the line of its own lookup (`hooks_of`, `file_at`) and not
    # the walk's, which names the same folder; the findings keep their order, the links first.
    hooks = hooks_of(source)
    lacks_hooks_file = file_at(source / "hooks" / "hooks.json") and not file_at(
        plugin / "hooks" / "hooks.json"
    )
    findings = link_findings(module, source, plugin)
    if lacks_hooks_file:
        findings.append(
            Finding(module, "the installed copy has no hooks/hooks.json", "restore the hooks file")
        )
    env = os.environ | {
        "CLAUDE_PLUGIN_ROOT": str(plugin),
        "CLAUDE_PROJECT_DIR": str(repo),
        "CLAUDE_PLUGIN_DATA": str(data),
    }
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
    for entry in declared_scans(source):
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


def git_command(argv: list[str]) -> str:
    """The name of a git command: `git <subcommand>`, the subcommand being the first argument after `git`
    that is neither an option nor the value of one. `-c` and `-C` take the next argument as their value (an
    option joined to its value with `=` takes none); the commands of `bare_repository` use no other option
    that does. An argv with no subcommand is named `git`."""
    skip = False
    for arg in argv[1:]:
        if skip:
            skip = False
        elif arg in ("-c", "-C"):
            skip = True
        elif not arg.startswith("-"):
            return f"git {arg}"
    return "git"


def git_failed(argv: list[str], out: str, err: str) -> Broken:
    """The BROKEN line of a git command of `bare_repository` that exited other than 0. `run` has turned a
    missing git into its own line, so git ran and "install git" would be no fix: run the command by hand."""
    name = git_command(argv)
    return Broken(
        f"{name} failed in the bare repository ({last_line(out, err)}) — fix: run {name} in a new"
        " repository by hand and read why it fails"
    )


def bare_repository(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    env = os.environ | {"GIT_CONFIG_GLOBAL": os.devnull}
    for argv in (["git", "init", "-q", "-b", "main"],):
        code, out, err = run(argv, repo, env)
        if code != 0:
            raise git_failed(argv, out, err)
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
            raise git_failed(argv, out, err)
    return repo


def kit_marketplace(kit: Path) -> str:
    """The name of the marketplace the kit at `kit` declares, read from its marketplace.json by
    `kit_module_doc.marketplace_name`; a file that gives none is a Broken with that function's line."""
    try:
        return marketplace_name(kit)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad


def claude_noted(kit: Path, env: dict[str, str]) -> Note:
    """The note for a run on another Claude Code than the kit pins, empty on the pinned one, from
    `kit_module_doc.claude_note`; its refusal is a Broken with that function's line."""
    try:
        return claude_note(kit, env)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad


def shown(value: object) -> str:
    """A reply of Claude Code, or a field of it, as a message quotes it: its repr, at most 200 characters."""
    text = repr(value)
    return text if len(text) <= 200 else text[:200] + "…"


def install_scope(key: str, code: int, out: str, timeout: float, note: Note) -> str:
    """The scope the install of `key` wrote, from the result of `claude plugin install --json`: the
    last non-empty line of its standard output, one JSON object whose `outcome` is "ok" or "failed". The
    run's own timeout (exit 124), no such line, an `outcome` of neither value, and "ok" with an exit other
    than 0 or with no `scope` string are a Broken; "failed" is a Refused, carrying the result's
    `failureCode` and `message` when present."""
    command = f"`claude plugin install {key} --json`"
    fix = platform_fix(note, SCRIPT, "install_scope", "a reply")
    if code == 124:
        raise Broken(
            f"{command} gave no result in {timeout:g} s — fix: run the check again, and check that git can"
            " reach the source"
        )
    lines = [line for line in out.splitlines() if line.strip()]
    if not lines:
        raise Broken(f"{command} printed nothing on standard output (exit {code}){fix}")
    try:
        result = json.loads(lines[-1])
    except ValueError:
        result = None
    if not isinstance(result, dict):
        raise Broken(f"{command} ended with {shown(lines[-1])}, not one JSON object (exit {code}){fix}")
    outcome = result.get("outcome")
    if outcome == "failed":
        said = [str(result[k]) for k in ("failureCode", "message") if isinstance(result.get(k), str)]
        raise Refused(": ".join(s for s in said if s) or f"exit {code}")
    if outcome != "ok":
        what = "has no outcome" if "outcome" not in result else f"has the outcome {shown(outcome)}"
        raise Broken(f'{command} ended with an object that {what}, not "ok" or "failed" (exit {code}){fix}')
    if code != 0:
        raise Broken(f"{command} said ok and exited {code}{fix}")
    scope = result.get("scope")
    if not isinstance(scope, str):
        what = "absent" if "scope" not in result else shown(scope)
        raise Broken(f"{command} said ok without a scope string (scope is {what}){fix}")
    return scope


def listed_install(key: str, scope: str, repo: Path, env: dict[str, str], note: Note) -> Path:
    """The installed copy's folder, from `claude plugin list --json` run in the bare repository: a JSON
    list with exactly one entry whose `id` is `key` and whose `scope` is the one the install wrote, its
    `installPath` a string naming an existing folder; anything else is a Broken saying what was found."""
    command = "`claude plugin list --json`"
    fix = platform_fix(note, SCRIPT, "listed_install", "a reply")
    code, out, err = run(["claude", "plugin", "list", "--json"], repo, env)
    if code != 0:  # no reply was written: no reader to update, whatever the exit; 124 is `run`'s timeout
        said = command_fix(note, "claude plugin list --json", LIST_WHERE, timed_out=code == 124)
        raise Broken(f"{command} exited {code} ({last_line(out, err)}){said}")
    try:
        entries = json.loads(out)
    except ValueError as bad:
        raise Broken(f"{command} printed no JSON ({shown(out)}: {bad}){fix}") from bad
    if not isinstance(entries, list):
        raise Broken(f"{command} printed a JSON {type(entries).__name__}, not a list{fix}")
    own = [e for e in entries if isinstance(e, dict) and e.get("id") == key and e.get("scope") == scope]
    if len(own) != 1:
        found = ", ".join(
            f"{e.get('id')!r} at {e.get('scope')!r}" if isinstance(e, dict) else shown(e) for e in entries[:5]
        )
        listed = f"entries: {found}{', …' if len(entries) > 5 else ''}" if entries else "no entries"
        what = f"lists {len(own)} entries" if own else "lists no entry"
        raise Broken(
            f"{command} {what} whose id is {key} at the scope {scope} the install wrote ({listed}){fix}"
        )
    path = own[0].get("installPath")
    if not isinstance(path, str):
        raise Broken(
            f"{command} gives no installPath string for {key} at scope {scope} (installPath is"
            f" {shown(path) if 'installPath' in own[0] else 'absent'}){fix}"
        )
    if not folder_at(Path(path)):
        raise Broken(f"{command} names an installPath that is no folder ({path}){fix}")
    return Path(path)


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
    """The kit's source of the module at a commit — its folder and the shared code its links reach —
    read from git history into a folder under root, the commit fetched when the clone lacks it."""
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


def install(
    module: str,
    root: Path,
    repo: Path,
    source: str,
    marketplace: str,
    note: Note,
    timeout: float = INSTALL_TIMEOUT,
) -> Path:
    """Add the marketplace and install the module at the default scope, in the bare repository and an
    empty configuration folder `root/config`, every `claude` command in the person's environment less the
    four variables of `claude_env` that steer where Claude Code finds, keeps or loads plugins, so that the
    platform's plugins root is that folder's `plugins`; the installed copy's folder, as `listed_install`
    finds it."""
    if source.startswith("#"):
        raise Broken(
            f"the source {source} names a branch of no repository — the pull request's head repository is"
            " gone — fix: open the change again from a branch of a repository that exists"
        )
    config = root / "config"
    config.mkdir()
    env = claude_env(os.environ) | {"CLAUDE_CONFIG_DIR": str(config)}
    code, out, err = run(["claude", "plugin", "marketplace", "add", source], repo, env)
    if code != 0:
        last = last_line(out, err)
        raise Broken(
            f"`claude plugin marketplace add {source}` exited {code} ({last}) — fix: check the kit's"
            " marketplace.json, and that git can reach the source"
        )
    key = f"{module}@{marketplace}"
    code, out, _ = run(["claude", "plugin", "install", key, "--json"], repo, env, timeout=timeout)
    return listed_install(key, install_scope(key, code, out, timeout, note), repo, env, note)


def counted(source: Path) -> str:
    links = sum(1 for p in entries_under(source) if link_at(p))
    return f"{len(hooks_of(source))} hook(s), {len(declared_scans(source))} scan(s), {links} link(s)"


def check_module(module: str, source: str, note: Note) -> tuple[list[Finding], str]:
    """The findings, and what was examined: the hooks, scans and links of the source compared."""
    if not file_at(KIT / "modules" / module / ".claude-plugin" / "plugin.json"):
        raise Broken(f"no module {module} in the kit — fix: name a folder under modules/ that holds a plugin")
    marketplace = kit_marketplace(KIT)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        repo = bare_repository(root)
        try:
            plugin = install(module, root, repo, source, marketplace, note)
        except Refused as refused:
            refusal_finding = Finding(
                module,
                f"Claude Code refuses to install it ({refused})",
                "fix its manifest or its entry in marketplace.json",
            )
            return [refusal_finding], "no install"
        (root / "data").mkdir()
        if there(Path(source)):  # a local folder is copied as it stands, uncommitted edits included
            kit_source = Path(source).resolve() / "modules" / module
        else:
            commit = installed_commit(root / "config", f"{module}@{marketplace}", plugin, note)
            kit_source = source_at(commit, module, root)
        return check_installed(module, kit_source, plugin, repo, root / "data"), counted(kit_source)


def report(module: str, findings: list[Finding], examined: str, note: str = "") -> int:
    if findings:
        for finding in findings:
            print(finding.render(note))
        print(f"RED: {len(findings)} finding(s) — {examined}{note}")
        return EXIT_RED
    print(f"GREEN: {module} installs and operates on a bare repository with its defaults — {examined}{note}")
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
    off_pin = " [claude 2.1.286, not the pinned 2.1.282: CONSTITUTION_KIT_ANY_CLAUDE=1]"  # typed by hand
    noted_lines = [  # a run off the pin: the note ends the headline line, not the why: and fix: lines
        f"RED: const-x: its scan `check-x --scan` exits 2 on a bare repository (no output){off_pin}",
        f"  why: {WHY}",
        "  fix: make the scan green, with a visible zero, where no constitution.yaml claims anything",
        f"RED: 1 finding(s) — 1 hook(s), 2 scan(s){off_pin}",
    ]
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        code = report("const-x", findings_of("scan-red"), "1 hook(s), 2 scan(s)", off_pin)
    ok = code == EXIT_RED and printed.getvalue().splitlines() == noted_lines
    failed += 0 if ok else 1
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
        code = report("const-x", [], "1 hook(s), 2 scan(s)", off_pin)
        plain = report("const-x", [], "1 hook(s), 2 scan(s)")
    ok = code == plain == EXIT_GREEN and printed.getvalue().splitlines() == green_lines
    failed += 0 if ok else 1
    print(f"[{'ok' if ok else 'FAIL'}] the green report ends with the note off the pin, and with none on it")
    if not ok:
        print(printed.getvalue())
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
    failed += 0 if ok else 1
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
    # (`absent` when unset), each after a `|`; and it writes the record where the platform does, in
    # CLAUDE_CODE_PLUGIN_CACHE_DIR's folder when it is set, else in the configuration's plugins/
    fake_claude = (
        '#!/bin/sh\necho "$*" >> "${FAKE_LOG:-$CLAUDE_CONFIG_DIR/fake.log}"\n'
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
    extra = 0  # the cases of the version check and of step 2, printed one by one

    def version_case(name: str, ok: bool, got: str) -> None:
        nonlocal failed, extra
        extra += 1
        failed += 0 if ok else 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"        got: {got}")

    def hook_wait_cases() -> None:
        """A hook that declares no timeout is waited for as the platform gives its event; one that declares
        a timeout, for that: read from the `Hook` that `hooks_of` builds, nothing is waited for. A hooks
        file `hooks_of` cannot run, in each shape, is one BROKEN line and never another exception; one that
        is a regular file and cannot be read (a denied read, an I/O error) has a line and fix of its own, and
        so has one whose place cannot be looked up (a folder that cannot be searched, an I/O error)."""
        with tempfile.TemporaryDirectory() as tmp:
            hooked = Path(tmp)
            (hooked / "hooks").mkdir()
            bare_hook: dict[str, object] = {"type": "command", "command": "true"}

            def hook_waits(hooks: dict[str, list[dict[str, object]]]) -> dict[str, float]:
                """The seconds `hooks_of` gives each hook of a hooks file with one hook per event."""
                table = {event: [{"hooks": [hook]}] for event, hook in ((e, h[0]) for e, h in hooks.items())}
                (hooked / "hooks" / "hooks.json").write_text(json.dumps({"hooks": table}), encoding="utf-8")
                return {hook.event: hook.timeout for hook in hooks_of(hooked)}

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
                got = hook_waits({event: [bare_hook]})
                version_case(
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
                got = hook_waits({event: [bare_hook | {"timeout": declared}]})
                version_case(
                    f"a {event} hook that declares a timeout of {declared:g} is waited for {declared:g} s",
                    got == {event: float(declared)},
                    str(got),
                )
            got = hook_waits(
                {event: [bare_hook] for event in ("PreToolUse", "SessionEnd")}
                | {"Stop": [bare_hook | {"timeout": 7}]}
            )
            version_case(
                "the hooks of a file are each waited for by their own event and timeout",
                got == {"PreToolUse": 600.0, "SessionEnd": 1.5, "Stop": 7.0},
                str(got),
            )
            # The wait `hooks_of` computes is the one `check_installed` hands `run`: `run` is spied, and
            # answers at once, so that no hook runs and nothing is waited for.
            (hooked / "MODULE.md").write_text('<a id="t9"></a>\n<a id="t10"></a>\n', encoding="utf-8")
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

            hook_waits(
                {"PreToolUse": [bare_hook | {"timeout": 5}], "UserPromptSubmit": [bare_hook]}
                | {"Stop": [bare_hook | {"timeout": 90}], "SessionEnd": [bare_hook]}
            )
            with mock.patch.dict(globals(), {"run": run_spy}):
                found = check_installed("const-x", hooked, hooked, hooked / "repo", hooked / "data")
            version_case(
                "`check_installed` runs each hook with the wait `hooks_of` gives it: the declared timeout"
                " (5, 90), else the event's (30, 1.5), no hook run",
                handed == {"PreToolUse": 5.0, "UserPromptSubmit": 30.0, "Stop": 90.0, "SessionEnd": 1.5}
                and found == [],
                f"{handed} {found}",
            )
            # The shapes of a hooks file `hooks_of` reads: one table, each case a whole file and either the
            # hooks it gives or the whole BROKEN line, typed by hand; nothing but `Broken` may be raised. A
            # line that holds the interpreter's own words for the reason is a pair instead: the line's start
            # and its end, with a reason of any wording between them.
            hooks_path = hooked / "hooks" / "hooks.json"
            shape_fix = (  # typed by hand
                " — fix: restore hooks/hooks.json to the shape the hooks reference gives, so that the check"
                " can read each hook it runs"
            )
            at = "event 'PreToolUse', group 1, hook 1"

            def single(hook: object, **group: object) -> str:
                """A hooks file with one event, one group (with the keys of `group`) and one hook."""
                return json.dumps({"hooks": {"PreToolUse": [{"hooks": [hook]} | group]}})

            def whole(table: object) -> str:
                """A hooks file of the table, as it stands."""
                return json.dumps({"hooks": table})

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

            cmd: dict[str, object] = {"type": "command", "command": "true"}
            one = Hook("PreToolUse", "", "true", (), 600.0)
            long_int = "1" + "0" * 400  # no float holds it
            shapes: list[tuple[str, str | bytes | OSError, list[Hook] | str | tuple[str, str]]] = [
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
                    not_hooks(
                        f"""{at}: "type" is 'shell', not one of command, http, mcp_tool, prompt, agent"""
                    ),
                ),
                (
                    "a hook of a type that is no string",
                    single({"type": ["command"], "command": "true"}),
                    not_hooks(
                        f"""{at}: "type" is ['command'], not one of command, http, mcp_tool, prompt, agent"""
                    ),
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
            for name, text, want in shapes:
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
                version_case(f"hooks file: {name}", shape_ok, str(got_shape))
            with tempfile.TemporaryDirectory() as other_tmp:  # a real folder, nothing mocked
                (Path(other_tmp) / "hooks" / "hooks.json").mkdir(parents=True)
                try:
                    got_folder: list[Hook] | str = hooks_of(Path(other_tmp))
                except Exception as other:  # a Broken here too is the defect this case holds
                    got_folder = f"raised {type(other).__name__}: {other}"
                version_case(
                    "hooks file: a folder in its place gives no hooks, as a missing file does",
                    got_folder == [],
                    str(got_folder),
                )
            # A hooks file whose place cannot be looked up (its folder cannot be searched, an I/O error):
            # the lookup `Path.stat` makes is made to raise, and the line is its own, since the file's
            # permissions and `git checkout` do not mend a folder that cannot be searched. `Path.is_file` is
            # made to return False meanwhile, as it does from release 3.14 on, so that a lookup made by it
            # fails here on every Python, as it does on 3.14 for the real folder below.
            not_found = (  # typed by hand; the folder is the one the fix names
                "BROKEN {path} cannot be looked up ({why}) — fix: make its folder {folder} searchable (its"
                " permissions), so that the check can find hooks/hooks.json and read each hook it runs"
            )
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
                    f"hooks file: {name}",
                    got_lookup == not_found.format(path=hooks_path, why=why, folder=hooks_path.parent),
                    str(got_lookup),
                )
            # What stands at hooks/hooks.json, real and nothing mocked: a dangling link, a link to itself (a
            # loop) and a path through a file are no hooks file, as a missing file is none; a link to a folder
            # is no regular file; a link to a regular file is that file, read.
            for name, kind, want_links in (
                ("a dangling link", "dangling", []),
                ("a link loop", "loop", []),
                ("a path through a file", "through a file", []),
                ("a link to a folder", "to a folder", []),
                ("a link to a regular file", "to a file", [one]),
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
                            (link_root / "real.json").write_text(single(cmd), encoding="utf-8")
                            link_place.symlink_to("../real.json")
                    try:
                        got_link: list[Hook] | str = hooks_of(link_root)
                    except Exception as other:  # a Broken here too is the defect this case holds
                        got_link = f"raised {type(other).__name__}: {other}"
                    version_case(f"hooks file: {name} at its place", got_link == want_links, str(got_link))
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
                        "hooks file: a real hooks folder with no permissions is the line naming the folder",
                        got_shut
                        == not_found.format(path=shut / "hooks.json", why="Permission denied", folder=shut),
                        str(got_shut),
                    )

    def start_and_lookup_cases() -> None:
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
        fix_run = (
            "give it a command that exists and can run, with no NUL byte in it or its arguments: a program on"
            " PATH, or a file with the execute permission (`chmod u+x` it), then run the check again"
        )
        fix_hook = (
            'give the hook\'s "command" and "args" in the module\'s hooks/hooks.json a command that'
            " exists and can run, with no NUL byte in it or its arguments: a program on PATH, or a file of"
            " the module with the execute permission (`chmod u+x` it, and commit the mode), then run the"
            " check again"
        )

        def said(call: Callable[[], object]) -> str:
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
            return said(lambda: declared_scans(plugin_at))

        def started(argv: list[str]) -> str:
            return said(lambda: run(argv, Path.cwd(), dict(os.environ)))

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
                f"run: {name} of starting a command is one BROKEN line naming the command",
                got_start
                == f"BROKEN: the command ['tool', '-x'] could not be started ({why}) — fix: {fix_run}",
                got_start,
            )
        with mock.patch("subprocess.run", side_effect=FileNotFoundError(2, "No such file or directory")):
            got_start = started(["tool"])
        version_case(
            "run: a command that is not found is the line it was, install it",
            got_start
            == "BROKEN: tool is not installed (No such file or directory) — fix: install it and put it on"
            " PATH",
            got_start,
        )
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["tool"], 5)):
            got_start = started(["tool"])
        version_case(
            "run: a command that outlasts its time is still the exit 124",
            got_start == "returned (124, '', 'timed out after 300 s')",
            got_start,
        )
        with tempfile.TemporaryDirectory() as run_tmp:
            plain = Path(run_tmp) / "plain"
            plain.write_text("#!/bin/sh\n", encoding="utf-8")
            plain.chmod(0o644)
            got_start = said(lambda: run([str(plain)], Path(run_tmp), dict(os.environ)))
            version_case(
                "run: a file with no execute permission is one BROKEN line naming it",
                got_start
                == f"BROKEN: the command [{str(plain)!r}] could not be started (Permission denied) — fix:"
                f" {fix_run}",
                got_start,
            )
        got_start = started(["a\0b"])
        version_case(
            "run: a command holding a NUL byte is one BROKEN line naming it, escaped",
            got_start
            == f"BROKEN: the command ['a\\x00b'] could not be started (embedded null byte) — fix: {fix_run}",
            got_start,
        )
        got_start = started(["a\0b" + "x" * 300])
        cut_at = repr(["a\0b" + "x" * 300])[:200]
        version_case(
            "run: a long command is cut at 200 characters, as every quoted reply is",
            got_start
            == f"BROKEN: the command {cut_at}… could not be started (embedded null byte) — fix: {fix_run}",
            got_start,
        )
        got_start = started([""])  # a PermissionError here, a missing file on Linux: both name the command
        version_case(
            "run: an empty command is one BROKEN line, never a traceback",
            got_start
            in (
                f"BROKEN: the command [''] could not be started (Permission denied) — fix: {fix_run}",
                "BROKEN: '' is not installed (No such file or directory) — fix: install it and put it on"
                " PATH",
            ),
            got_start,
        )
        # A command that is not found is echoed as `shown` quotes it when it is no plain word, so that a
        # space, a quote or a line break reads as one token; a working folder that does not exist is its own
        # cause, whichever command is asked for. Both are real, no process mocked.
        got_start = started(["my tool's\nname"])
        version_case(
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
                got_start = said(partial(run, argv, gone, dict(os.environ)))
                version_case(
                    f"run: a working folder that does not exist is named, not {name} read as not installed",
                    got_start == no_folder,
                    got_start,
                )
        with (
            tempfile.TemporaryDirectory() as hook_tmp
        ):  # a hook run through check_installed has the hook's fix
            hooked_root = Path(hook_tmp)
            (hooked_root / "hooks").mkdir()
            (hooked_root / "repo").mkdir()
            (hooked_root / "MODULE.md").write_text('<a id="t9"></a>\n<a id="t10"></a>\n', encoding="utf-8")
            nul_hook = {
                "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "\0tool", "args": []}]}]}
            }
            (hooked_root / "hooks" / "hooks.json").write_text(json.dumps(nul_hook), encoding="utf-8")
            got_start = said(
                lambda: check_installed("m", hooked_root, hooked_root, hooked_root / "repo", hooked_root)
            )
            version_case(
                "run: a hook whose command cannot be started is one BROKEN line with the hook's own fix",
                got_start
                == f"BROKEN: the command ['\\x00tool'] could not be started (embedded null byte) — fix:"
                f" {fix_hook}",
                got_start,
            )
        # A missing path keeps its meaning at each site; a NUL in a name, a link loop and a path through a
        # file are missing paths too, as `Path.exists` has them.
        with tempfile.TemporaryDirectory() as miss_tmp:
            miss_root = Path(miss_tmp)
            (miss_root / "empty").mkdir()
            (miss_root / "loop").mkdir()
            (miss_root / "loop" / "MODULE.md").symlink_to("MODULE.md")
            (miss_root / "afile").write_text("", encoding="utf-8")
            no_doc = (
                "BROKEN: {} does not exist — fix: restore the module's document, which declares its scans"
            )
            for name, plugin_at in (
                ("a folder with no document", miss_root / "empty"),
                ("a document that is a link loop", miss_root / "loop"),
                ("a plugin that is a file, the document a path through it", miss_root / "afile"),
                ("a plugin that is no entry", miss_root / "nothing"),
            ):
                got_miss = declared_of(plugin_at)
                version_case(
                    f"lookups: {name} is the missing document it was",
                    got_miss == no_doc.format(plugin_at / "MODULE.md"),
                    got_miss,
                )
            version_case(
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
            with mock.patch.dict(globals(), {"KIT": toy_missing}):
                got_miss = said(lambda: check_module("m", str(miss_root), Note("2.1.282")))
            version_case(
                "lookups: a module with no plugin.json is the line it was",
                got_miss
                == "BROKEN: no module m in the kit — fix: name a folder under modules/ that holds a plugin",
                got_miss,
            )
            with (
                mock.patch.dict(globals(), {"claude_noted": mock.Mock(side_effect=Broken("stopped here"))}),
                contextlib.redirect_stdout(io.StringIO()) as printed_miss,
            ):
                status_miss = main(["--module", "m", "--from", str(miss_root / "nothing")])
            version_case(
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
                got_odd = said(lambda: declared_scans(odd))
            version_case(
                "lookups: an I/O error is one BROKEN line, its fix to read why the folder is not searchable",
                got_odd
                == f"BROKEN: {odd / 'MODULE.md'} cannot be searched (Input/output error) — fix: make the"
                f" folder {odd} searchable, `ls -ld '{odd}'` shows why not, then run the check again",
                got_odd,
            )

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
                else f"give the file read permission, `chmod u+r {shlex.quote(str(path))}`,"
                " then run the check again"
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
                    got_list = said(call)
                version_case(
                    f"walks: a subfolder that cannot be listed ({name}) is one BROKEN line naming it",
                    got_list == cannot_list(closed_sub),
                    got_list,
                )
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

            got_bytes = said(lambda: link_findings("m", bytes_source, bytes_copy))
            version_case(
                "reads: the copy and the source compared are green", got_bytes == "returned []", got_bytes
            )
            for name, blocked, installed in (
                ("a folder link's file of the source", shared_dir / "locked.txt", False),
                ("a folder link's file of the copy", copied_locked, True),
                ("a file link's file of the source", bytes_root / "outside.txt", False),
                ("a file link's file of the copy", bytes_copy / "scripts" / "one.txt", True),
            ):
                with read_denying(blocked):
                    got_bytes = said(lambda: link_findings("m", bytes_source, bytes_copy))
                version_case(
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
                    got_bytes = said(lambda: link_findings("m", bytes_source, bytes_copy))
                version_case(
                    f"reads: {name} that cannot be read is one BROKEN line naming it",
                    got_bytes == cannot_read(blocked, installed),
                    got_bytes,
                )
        if os.geteuid() == 0:  # root searches any folder: there, the cases above are the proof
            return
        with tempfile.TemporaryDirectory() as shut_tmp:
            shut_root = Path(shut_tmp).resolve()  # a link's target is resolved, so the folders are too
            closed = shut_root / "closed folder"
            document = closed / "deep" / "plugin"
            document.mkdir(parents=True)
            (document / "MODULE.md").write_text('<a id="t9"></a>\n<a id="t10"></a>\n', encoding="utf-8")
            (closed / "kit" / "modules" / "m" / ".claude-plugin").mkdir(parents=True)
            (closed / "kit" / "modules" / "m" / ".claude-plugin" / "plugin.json").write_text(
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
            hooks_source, hooks_copy = shut_root / "hooks source", shut_root / "hooks copy"
            for tree in (hooks_source, hooks_copy):
                (tree / "hooks").mkdir(parents=True)
                (tree / "hooks" / "hooks.json").write_text('{"hooks": {}}', encoding="utf-8")
                (tree / "MODULE.md").write_text('<a id="t9"></a>\n<a id="t10"></a>\n', encoding="utf-8")
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
                got_shut = said(lambda: declared_scans(document))
                version_case(
                    "lookups: a module document under a folder of mode 000 is one BROKEN line naming the"
                    " folder to open",
                    got_shut == cannot_search(document / "MODULE.md", closed),
                    got_shut,
                )
                with mock.patch.dict(globals(), {"KIT": closed / "kit"}):
                    got_shut = said(lambda: check_module("m", "owner/repo", Note("2.1.282")))
                version_case(
                    "lookups: a module's plugin.json under such a folder is the same line",
                    got_shut
                    == cannot_search(
                        closed / "kit" / "modules" / "m" / ".claude-plugin" / "plugin.json", closed
                    ),
                    got_shut,
                )
                with mock.patch.dict(globals(), {"run": lambda *args, **kwargs: (0, listing_json, "")}):
                    got_shut = said(lambda: listed_install("m@mp", "user", shut_root, {}, Note("2.1.282")))
                version_case(
                    "lookups: an installPath under such a folder is the same line, not 'no folder'",
                    got_shut == cannot_search(document, closed),
                    got_shut,
                )
                with (
                    mock.patch.dict(
                        globals(), {"claude_noted": mock.Mock(side_effect=Broken("stopped here"))}
                    ),
                    contextlib.redirect_stdout(io.StringIO()) as printed_shut,
                ):
                    status_shut = main(["--module", "m", "--from", str(closed / "src")])
                version_case(
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
                got_shut = said(lambda: link_findings("m", source_links / "module", closed / "copy"))
                version_case(
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
                    got_shut = said(call)
                    version_case(
                        f"lookups: an entry of a walk that cannot be looked at ({name}) is the same line",
                        got_shut == cannot_search(entry, walk / "sub folder"),
                        got_shut,
                    )
                got_shut = said(lambda: files_under(listing))
                version_case(
                    "lookups: a file of a folder that lists but cannot be searched is the same line",
                    got_shut == cannot_search(listing / "f.txt", listing),
                    got_shut,
                )
                got_shut = said(
                    lambda: check_installed("m", hooks_source, hooks_copy, shut_root / "repo", shut_root)
                )
                version_case(
                    "lookups: the copy's hooks file under a folder of mode 000 is the same line",
                    got_shut == cannot_search(hooks_copy / "hooks" / "hooks.json", hooks_copy / "hooks"),
                    got_shut,
                )
                hooks_copy_hooks.chmod(0o755)
                (hooks_source / "hooks").chmod(0o000)
                shut_modes.append((hooks_source / "hooks", 0o755))
                got_shut = said(
                    lambda: check_installed("m", hooks_source, hooks_copy, shut_root / "repo", shut_root)
                )
                version_case(
                    "lookups: the source's hooks file under such a folder is the line `hooks_of` had",
                    got_shut
                    == f"BROKEN: {hooks_source / 'hooks' / 'hooks.json'} cannot be looked up (Permission"
                    f" denied) — fix: make its folder {hooks_source / 'hooks'} searchable (its permissions),"
                    " so that the check can find hooks/hooks.json and read each hook it runs",
                    got_shut,
                )
                (unlisted / "closed sub").chmod(0o000)  # a real subfolder that cannot be listed
                for name, call in sites:
                    got_shut = said(call)
                    version_case(
                        f"walks: a real subfolder of mode 000 ({name}) is one BROKEN line naming it",
                        got_shut == cannot_list(unlisted / "closed sub"),
                        got_shut,
                    )
                half.chmod(0o444)
                got_shut = said(lambda: files_under(half.parent))
                version_case(
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
                    got_shut = said(lambda: link_findings("m", real_source, real_copy))
                    locked.chmod(0o644)
                    version_case(
                        f"reads: {name} of mode 000 under a folder link is one BROKEN line naming it",
                        got_shut == cannot_read(locked, installed),
                        got_shut,
                    )
            finally:
                for folder_back, mode_back in shut_modes:
                    folder_back.chmod(mode_back)

    def bare_repository_cases() -> None:
        """A git command of `bare_repository` that exits other than 0 is one BROKEN line naming it as
        `git <subcommand>` and a fix that can be followed (git ran, so "install git" is none); a missing
        git is `run`'s own line, unchanged. No existing case fits: the hook cases read a hooks file and the
        version cases a `claude`, so this one table is new. Any exit other than 0 counts (1, 2, 124, 128),
        and the line quotes the last line of the standard error, else of the standard output."""
        by_hand = "run {0} in a new repository by hand and read why it fails"
        init_line = (
            "BROKEN: git init failed in the bare repository (fatal: simulated) — fix: "
            + by_hand.format("git init")
        )
        add_line = (
            "BROKEN: git add failed in the bare repository (fatal: simulated) — fix: "
            + by_hand.format("git add")
        )
        commit_line = (
            "BROKEN: git commit failed in the bare repository (fatal: simulated) — fix: "
            + by_hand.format("git commit")
        )
        ran: list[list[str]] = []

        simulated = (1, "", "warning: x\nfatal: simulated")  # the exit, stdout and stderr of a failure

        def failing_at(
            word: str | None, failure: tuple[int, str, str]
        ) -> Callable[..., tuple[int, str, str]]:
            def fake_run(
                argv: list[str], cwd: Path, env: dict[str, str], stdin: str = "", timeout: float = 300
            ) -> tuple[int, str, str]:
                """`run`, but nothing is run: every command exits 0, the one with `word` gives `failure`."""
                ran.append(argv)
                return failure if word in argv else (0, "", "")

            return fake_run

        def line_of(
            word: str | None, path: str | None = None, failure: tuple[int, str, str] = simulated
        ) -> str:
            """The BROKEN line `bare_repository` raises with `run` giving `failure` at `word`, or `ok`; with
            `path`, the real `run` and that PATH."""
            ran.clear()
            with tempfile.TemporaryDirectory() as tmp:
                with mock.patch.dict(globals(), {"run": failing_at(word, failure)} if path is None else {}):
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
            version_case(f"bare repository: {name}", got_line == want, got_line)

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
                    f"bare repository: `git {name}` exiting {code}",
                    got_line == failed(name, said),
                    got_line,
                )
            got_line = line_of(name, failure=(1, "out one\nout last", "err one\nerr last"))
            version_case(
                f"bare repository: `git {name}` printing on both streams quotes the standard error",
                got_line == failed(name, "err last"),
                got_line,
            )
            got_line = line_of(name, failure=(1, "out one\nout last", ""))
            version_case(
                f"bare repository: `git {name}` printing on the standard output alone quotes it",
                got_line == failed(name, "out last"),
                got_line,
            )
        got_line = line_of(None)
        version_case(
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
            "bare repository: git missing from PATH is run's own line, unchanged",
            got_line
            == "BROKEN: git is not installed (No such file or directory) — fix: install it and put it"
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
            version_case(f"bare repository: {argv} is named {named!r}", got_name == named, got_name)

    hook_wait_cases()
    start_and_lookup_cases()
    bare_repository_cases()
    with tempfile.TemporaryDirectory() as tmp:  # the version check over every answer of `claude --version`
        base_dir = Path(tmp)
        toy_kit, fake_dir, fake_log = base_dir / "kit", base_dir / "bin", base_dir / "claude.log"
        (toy_kit / "scripts").mkdir(parents=True)
        (toy_kit / "scripts" / "claude-code.version").write_text("2.1.282\n", encoding="utf-8")
        fake_dir.mkdir()
        (fake_dir / "claude").write_text(fake_claude, encoding="utf-8")
        (fake_dir / "claude").chmod(0o755)
        (base_dir / "empty").mkdir()
        # the lines, typed by hand: a message function cannot check itself
        strict = (
            "claude is {0}, and the kit's install checks read the platform as 2.1.282 writes it"
            " (scripts/claude-code.version) — fix: put Claude Code 2.1.282 first on PATH for this run:"
            " either run sh scripts/setup-claude.sh in the kit's clone, then the check through"
            " sh scripts/gate-list.sh --run install-<module> (--run guide for the guide's check), which puts"
            " it first, or install it beside your own by hand (npm install --prefix <folder>"
            " @anthropic-ai/claude-code@2.1.282, then PATH=<folder>/node_modules/.bin:$PATH), or set"
            " CONSTITUTION_KIT_ANY_CLAUDE=1 to run on"
            " {0} with a note on every headline line"
        )
        noted = " [claude {0}, not the pinned 2.1.282: CONSTITUTION_KIT_ANY_CLAUDE=1]"
        reinstall = (
            " — fix: check that `claude` on PATH is Claude Code (`command -v claude`), and reinstall it"
        )

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
        plugin_vars = {
            "CLAUDE_CODE_PLUGIN_CACHE_DIR": "person-cache",
            "CLAUDE_CODE_PLUGIN_SEED_DIR": "person-seed",
            "CLAUDE_CODE_PLUGIN_DIRS": "person-dirs",
            "CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE": "1",
        }
        documented_kept = {  # typed by hand, never the code's: the seven documented ones, each its own value
            "CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS": "45000",
            "CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE": "keep",
            "CLAUDE_CODE_SYNC_PLUGIN_INSTALL": "sync",
            "CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS": "30000",
            "FORCE_AUTOUPDATE_PLUGINS": "force",
            "CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL": "disable",
            "CLAUDE_CODE_PLUGIN_DIR_WATCH": "watch",
        }
        kept_vars = {"CLAUDE_CODE_PLUGIN_PREFER_HTTPS": "1", "FAKE_KEEP": "1"} | documented_kept
        seen_when_removed = "|absent|absent|absent|absent|1|1|45000|keep|sync|30000|force|disable|watch"

        def person_plugin_values(under: Path) -> dict[str, tuple[str, str]]:
            """Each of the four variables with the words for its set value and the value, the folders made
            empty under `under`."""
            values: dict[str, tuple[str, str]] = {}
            for variable, folder in plugin_vars.items():
                if folder == "1":
                    values[variable] = ("set to 1", "1")
                else:
                    (under / folder).mkdir()
                    values[variable] = ("set to a folder", str(under / folder))
            return values

        def claude_env(said: str, code: int, optout: str | None, path: str | None = None) -> dict[str, str]:
            env = {k: v for k, v in os.environ.items() if k != "CONSTITUTION_KIT_ANY_CLAUDE"}
            env |= {
                "PATH": path if path is not None else f"{fake_dir}{os.pathsep}{env.get('PATH', '')}",
                "FAKE_SAYS": said,
                "FAKE_EXIT": str(code),
                "FAKE_LOG": str(fake_log),
            }
            if optout is not None:
                env["CONSTITUTION_KIT_ANY_CLAUDE"] = optout
            return env

        def outcome(env: dict[str, str], root: Path = toy_kit) -> str:
            """What the check does before its install: the note it goes on with, or its BROKEN line."""
            fake_log.unlink(missing_ok=True)
            try:
                return f"note:{claude_noted(root, env)}"
            except Broken as broken:
                return f"BROKEN: {broken}"

        def logged() -> list[str]:
            return fake_log.read_text(encoding="utf-8").splitlines() if fake_log.exists() else []

        def stuck(what: str) -> str:
            return f"BROKEN: `claude --version` {what}{reinstall}"

        # what `--version` says, its exit, what the run does with the variable unset, and with it at 1
        # (None: the same)
        rows: list[tuple[str, int, str, str | None]] = [
            ("2.1.282 (Claude Code)\\n", 0, "note:", None),
            ("2.1.282 (Claude Code)\\r\\n", 0, "note:", None),  # CR is white space: the first word is read
            ("2.1.282 (Claude Code)\\nextra\\n", 0, "note:", None),  # the first line alone is read
            ("\\n2.1.282 (Claude Code)\\n", 0, "note:", None),  # blank lines before it are skipped
            ("  \\n\\n 2.1.282 (Claude Code)\\n", 0, "note:", None),  # white space too, and before the word
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

        def kind(said_outcome: str) -> str:
            if said_outcome == "note:":
                return "the run goes on"
            return "the run goes on with the note" if said_outcome.startswith("note:") else "BROKEN"

        for says, exits, unset_out, one_out in rows:
            at_one = unset_out if one_out is None else one_out
            seen = [outcome(claude_env(says, exits, None)), outcome(claude_env(says, exits, "1"))]
            ran = logged()  # the second run only: each run leaves the one line its own command logged
            version_case(
                f'`claude --version` printing "{says}" with exit {exits}: {kind(unset_out)} with the variable'
                f" unset, {kind(at_one)} with it at 1",
                seen == [unset_out, at_one] and ran == ["--version"],
                f"{seen} {ran}",
            )
        too_old = "2.1.286 (Claude Code)\\n"
        for value in ("", "0", "yes", "true", " 1", "1 ", "TRUE", "01"):
            version_case(
                f"CONSTITUTION_KIT_ANY_CLAUDE={value!r} is not the opt-out: the other version is BROKEN",
                outcome(claude_env(too_old, 0, value)) == "BROKEN: " + strict.format("2.1.286"),
                outcome(claude_env(too_old, 0, value)),
            )
        no_pin = base_dir / "empty"
        said_no_pin = outcome(claude_env(too_old, 0, "1"), no_pin)
        version_case(
            "a kit with no pin file is BROKEN with the reader's line, and claude is not run",
            said_no_pin
            == f"BROKEN: {no_pin}/scripts/claude-code.version cannot be read (No such file or directory)"
            " — fix: write the one version Claude Code's npm package carries, e.g. 2.1.282, as the file's"
            " only line"
            and logged() == [],
            f"{said_no_pin} {logged()}",
        )
        said_no_claude = outcome(claude_env(too_old, 0, "1", path=str(no_pin)))
        version_case(
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
            "a claude that does not answer in time is no version, the opt-out notwithstanding",
            said_hung == f"`claude --version` exited 124 (timed out after 0.2 s){reinstall}"
            and logged() == ["--version"],
            f"{said_hung} {logged()}",
        )

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
            env = {
                k: v for k, v in env.items() if own or k not in ("CLAUDE_CONFIG_DIR", "DISABLE_AUTOUPDATER")
            }
            if own:
                env |= {"CLAUDE_CONFIG_DIR": str(person), "DISABLE_AUTOUPDATER": "0"}
            outcome(env)
            seen_env = env_log.read_text(encoding="utf-8").splitlines() if env_log.exists() else []
            config, updater, held, is_dir = (seen_env[0].split("|") + ["", "", "", ""])[:4]
            version_case(
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

        cache_seen = base_dir / "cache-seen.log"
        person_values = person_plugin_values(base_dir)
        for variable, (what, set_value) in person_values.items():
            for name, value in ((what, set_value), ("set and empty", "")):
                cache_seen.unlink(missing_ok=True)
                env = claude_env("2.1.282 (Claude Code)\\n", 0, None) | kept_vars
                env |= {"FAKE_CACHE": str(cache_seen), variable: value}
                said_version = outcome(env)
                seen_version = (
                    cache_seen.read_text(encoding="utf-8").splitlines() if cache_seen.exists() else []
                )
                version_case(
                    f"{variable} {name} in the person's environment: `claude --version` runs with the four"
                    " absent, CLAUDE_CODE_PLUGIN_PREFER_HTTPS, FAKE_KEEP and the seven documented as set",
                    said_version == "note:" and seen_version == ["--version " + seen_when_removed],
                    f"{said_version} {seen_version}",
                )
        cache_seen.unlink(missing_ok=True)
        env = claude_env(too_old, 0, "1") | kept_vars | {"FAKE_CACHE": str(cache_seen)}
        env |= {variable: set_value for variable, (_, set_value) in person_values.items()}
        said_all = outcome(env)
        seen_all = cache_seen.read_text(encoding="utf-8").splitlines() if cache_seen.exists() else []
        version_case(
            "all four set in the person's environment with CONSTITUTION_KIT_ANY_CLAUDE=1 on another version:"
            " the opt-out is still read, and `claude --version` runs with the four absent",
            said_all == "note:" + noted.format("2.1.286") and seen_all == ["--version " + seen_when_removed],
            f"{said_all} {seen_all}",
        )

        def whole_run(
            said: str, code: int, optout: str | None, *args: str
        ) -> tuple[int, list[str], list[str]]:
            """The exit and the lines `main` prints on the toy kit, and what the fake claude logged."""
            fake_log.unlink(missing_ok=True)
            printed_lines = io.StringIO()
            with (
                mock.patch.dict(os.environ, claude_env(said, code, optout)),
                mock.patch.dict(globals(), {"KIT": toy_kit}),
                contextlib.redirect_stdout(printed_lines),
            ):
                if optout is None:  # patch.dict adds to the environment, so the ambient variable goes by hand
                    os.environ.pop("CONSTITUTION_KIT_ANY_CLAUDE", None)
                status = main(["--module", "const-nope", *args])
            return status, printed_lines.getvalue().splitlines(), logged()

        stop = "BROKEN: the check could not run — 0 modules examined"
        status, lines, ran = whole_run("2.1.286 (Claude Code)\\n", 0, None)
        version_case(
            "a run on another version stops at its first line, and no other claude command runs",
            status == EXIT_BROKEN
            and lines == ["BROKEN: " + strict.format("2.1.286"), stop]
            and ran == ["--version"],
            f"{status} {lines} {ran}",
        )
        status, lines, ran = whole_run("2.1.286 (Claude Code)\\n", 0, "1")
        version_case(
            "with the opt-out the run goes on, and each BROKEN line it ends with ends with the note",
            status == EXIT_BROKEN
            and lines
            == [
                "BROKEN: no module const-nope in the kit — fix: name a folder under modules/ that holds a"
                " plugin" + noted.format("2.1.286"),
                stop + noted.format("2.1.286"),
            ]
            and ran == ["--version"],
            f"{status} {lines} {ran}",
        )
        status, lines, ran = whole_run("", 139, "1")
        version_case(
            "a crashed claude stops the run with no note, the opt-out notwithstanding",
            status == EXIT_BROKEN
            and lines == [f"BROKEN: `claude --version` exited 139 (no output){reinstall}", stop]
            and ran == ["--version"],
            f"{status} {lines} {ran}",
        )
    with (
        tempfile.TemporaryDirectory() as tmp
    ):  # step 2 over a toy kit, its marketplace named toy-mp, and a fake claude
        base = Path(tmp).resolve()
        toy, bin_dir, cache = base / "kit", base / "bin", base / "cache"
        (toy / ".claude-plugin").mkdir(parents=True)
        (toy / ".claude-plugin" / "marketplace.json").write_text('{"name": "toy-mp"}', encoding="utf-8")
        (toy / "scripts").mkdir()
        (toy / "scripts" / "claude-code.version").write_text("2.1.282\n", encoding="utf-8")
        (toy / "kernel").mkdir()
        (toy / "kernel" / "CONVENTIONS.md").write_text("A kernel.\n", encoding="utf-8")
        toy_module = toy / "modules" / "const-x"
        (toy_module / ".claude-plugin").mkdir(parents=True)
        (toy_module / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
        (toy_module / "MODULE.md").write_text('<a id="t9"></a>\n<a id="t10"></a>\n', encoding="utf-8")
        copy, other = cache / "const-x", cache / "other"
        shutil.copytree(toy_module, copy)  # the installed copy; `other` is a folder that is not it
        other.mkdir()
        (cache / "a-file").write_text("not a folder\n", encoding="utf-8")
        bin_dir.mkdir()
        (bin_dir / "claude").write_text(fake_claude, encoding="utf-8")
        (bin_dir / "claude").chmod(0o755)
        fake_log, calls_log, cache_log = base / "fake.log", base / "calls.log", base / "cache.log"
        key = "const-x@toy-mp"
        pin_note = Note("2.1.282")  # the state of a run on the pin: the note empty
        gone = 'Plugin "const-x" not found in any configured marketplace'
        # what the platform replies, typed by hand
        ok_line = json.dumps({"command": "install", "outcome": "ok", "message": "Installed", "scope": "user"})
        failed_line = json.dumps(
            {"command": "install", "outcome": "failed", "message": gone, "failureCode": "not_found"}
        )

        def listed(**over: object) -> dict[str, object]:
            return {"id": key, "scope": "user", "installPath": str(copy)} | over

        sha = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"  # an object id: 40 lower-case hexadecimal characters
        sha_wrong, sha_right = "0f" * 20, "c0ffee" * 6 + "c0ff"

        def recorded(*entries: dict[str, object]) -> str:
            return json.dumps({"version": 2, "plugins": {key: list(entries)}})

        def commit(**over: object) -> dict[str, object]:
            return {"installPath": str(copy), "scope": "user", "gitCommitSha": sha} | over

        @dataclass(frozen=True)
        class Scene:
            """One run of the check over the fake claude: what its install, its list and the record say."""

            out: str = ok_line
            code: int = 0
            listing: str = json.dumps([listed()])
            list_code: int = 0
            record: str = recorded(commit())
            source: str = (
                "remote"  # `remote`: no folder, `local`: the toy kit's folder, `linked`: one with a link
            )

        def environment(scene: Scene, says: str = "2.1.282 (Claude Code)\\n") -> dict[str, str]:
            for log in (fake_log, calls_log, cache_log):
                log.unlink(missing_ok=True)
            return {
                "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
                "FAKE_SAYS": says,
                "FAKE_LOG": str(fake_log),
                "FAKE_CALLS": str(calls_log),
                "FAKE_CACHE": str(cache_log),
                "FAKE_INSTALL_OUT": scene.out,
                "FAKE_INSTALL_EXIT": str(scene.code),
                "FAKE_LIST_OUT": scene.listing,
                "FAKE_LIST_EXIT": str(scene.list_code),
                "FAKE_RECORD": scene.record,
            }

        linked = base / "linked-kit"  # the toy kit whose module holds a link its installed copy lacks
        shutil.copytree(toy, linked, symlinks=True)
        (linked / "modules" / "const-x" / "linked").symlink_to("MODULE.md")
        no_kernel = base / "no-kernel"  # the toy kit without its kernel/, which a bare repository copies
        shutil.copytree(toy, no_kernel)
        shutil.rmtree(no_kernel / "kernel")

        def where(scene: Scene) -> str:
            return {"local": str(toy), "linked": str(linked)}.get(scene.source, "owner/repo")

        def unrecord(text: str) -> str:  # the record's place is under a folder the run makes and removes
            return re.sub(r"[^\s(]+/config/plugins/installed_plugins\.json", "<record>", text)

        def drive(scene: Scene, extra: dict[str, str] | None = None) -> tuple[str, list[str], list[str]]:
            """What `check_module` does: `on` (the copy is compared), the finding, or the BROKEN line; the
            commits the source was asked at, and the copies it was compared with; `extra` is added to the
            environment the check runs in."""
            fetched: list[str] = []
            compared: list[str] = []

            def source_spy(at: str, name: str, root: Path) -> Path:
                fetched.append(at)
                return toy / "modules" / name

            def installed_spy(name: str, src: Path, plugin: Path, repo: Path, data: Path) -> list[Finding]:
                compared.append(str(plugin))
                return []

            patched = {"KIT": toy, "source_at": source_spy, "check_installed": installed_spy}
            with (
                mock.patch.dict(os.environ, environment(scene) | (extra or {})),
                mock.patch.dict(globals(), patched),
            ):
                try:
                    found, _ = check_module("const-x", where(scene), pin_note)
                except Broken as broken:
                    return unrecord(f"BROKEN: {broken}"), fetched, compared
                except (KeyError, TypeError) as escaped:  # a record's entry read wrongly: a case that fails
                    return f"escaped {type(escaped).__name__}: {escaped}", fetched, compared
            return "; ".join(f"RED: {f.what} | {f.fix}" for f in found) or "on", fetched, compared

        def expect(name: str, scene: Scene, wanted: str, fetched: list[str] | None = None) -> None:
            """`wanted` is what `drive` says, `fetched` the commits the source was asked at; when it goes on,
            the copy compared is the installed one."""
            got = drive(scene)
            version_case(
                name, got == (wanted, fetched or [], [str(copy)] if wanted == "on" else []), str(got)
            )

        install_command = f"`claude plugin install {key} --json`"
        listing_command = "`claude plugin list --json`"

        def fix_of(reader: str, wrote: str = "a reply") -> str:  # typed by hand: a message function cannot
            return (  # check itself
                f" — fix: Claude Code 2.1.282 wrote {wrote} that the kit's reader, `{reader}` in"
                " scripts/check-bare-install.py, does not read: update that reader to what 2.1.282 writes"
            )

        off_fix = (  # typed by hand: the run is on 2.1.286, not the pinned 2.1.282
            " — fix: this run is on 2.1.286, not the pinned 2.1.282: run it again on the pinned version,"
            " put Claude Code 2.1.282 first on PATH for this run: either run sh scripts/setup-claude.sh"
            " in the kit's clone, then the check through sh scripts/gate-list.sh --run install-<module>"
            " (--run guide for the guide's check), which puts it first, or install it beside your own by hand"
            " (npm install --prefix <folder> @anthropic-ai/claude-code@2.1.282,"
            " then PATH=<folder>/node_modules/.bin:$PATH)"
        )
        install_fix, list_fix = fix_of("install_scope"), fix_of("listed_install")
        refused = (
            "RED: Claude Code refuses to install it ({}) | fix its manifest or its entry in marketplace.json"
        )
        no_object = "not one JSON object (exit {})"
        bad_outcome = 'an object that {}, not "ok" or "failed" (exit 0)'
        timed_out = (
            " gave no result in {} s — fix: run the check again, and check that git can reach the source"
        )
        install_rows: list[tuple[str, str, int, str]] = [
            ("an ok result, exit 0, goes on", ok_line, 0, "on"),
            (
                "an ok result after two other lines goes on: the last line is read",
                f"A\nB\n{ok_line}",
                0,
                "on",
            ),
            ("an ok result with blank lines after it goes on", f"{ok_line}\n\n  \n", 0, "on"),
            (
                "a failed result with its failureCode is a refusal naming both",
                failed_line,
                1,
                refused.format(f"not_found: {gone}"),
            ),
            (
                "a failed result without a failureCode is a refusal naming its message",
                json.dumps({"outcome": "failed", "message": gone}),
                1,
                refused.format(gone),
            ),
            (
                "a failed result with exit 0 is a refusal",
                failed_line,
                0,
                refused.format(f"not_found: {gone}"),
            ),
            (
                "a failed result with neither field is a refusal naming the exit",
                '{"outcome": "failed"}',
                1,
                refused.format("exit 1"),
            ),
            (
                "an empty standard output, exit 1, is BROKEN",
                "",
                1,
                f"BROKEN: {install_command} printed nothing on standard output (exit 1){install_fix}",
            ),
            (
                "an empty standard output, exit 0, is BROKEN",
                "",
                0,
                f"BROKEN: {install_command} printed nothing on standard output (exit 0){install_fix}",
            ),
            (
                "the JSON line followed by a human line is BROKEN: the last line is no JSON",
                f"{ok_line}\nInstalled const-x",
                0,
                f"BROKEN: {install_command} ended with 'Installed const-x', "
                + no_object.format(0)
                + install_fix,
            ),
            (
                "a human line only, exit 0, is BROKEN",
                "✔ Installed const-x",
                0,
                f"BROKEN: {install_command} ended with '✔ Installed const-x', "
                + no_object.format(0)
                + install_fix,
            ),
            (
                "a human line only, exit 1, is BROKEN",
                "✘ Failed to install const-x",
                1,
                f"BROKEN: {install_command} ended with '✘ Failed to install const-x', "
                + no_object.format(1)
                + install_fix,
            ),
            (
                "an ok line with exit 1 is BROKEN",
                ok_line,
                1,
                f"BROKEN: {install_command} said ok and exited 1{install_fix}",
            ),
            (
                "exit 124 with nothing printed is BROKEN, no refusal",
                "",
                124,
                f"BROKEN: {install_command}{timed_out.format(300)}",
            ),
            ("exit 124 beats an ok line", ok_line, 124, f"BROKEN: {install_command}{timed_out.format(300)}"),
            (
                "exit 124 beats a failed line",
                failed_line,
                124,
                f"BROKEN: {install_command}{timed_out.format(300)}",
            ),
            (
                "a human line whose quotation is exactly 200 characters is quoted whole",
                "x" * 198,
                0,
                f"BROKEN: {install_command} ended with '{'x' * 198}', {no_object.format(0)}{install_fix}",
            ),
            (
                "a human line whose quotation is 201 characters is cut at 200 and ends with …",
                "x" * 199,
                0,
                f"BROKEN: {install_command} ended with '{'x' * 199}…, {no_object.format(0)}{install_fix}",
            ),
            (
                "a long human line is cut at 200 characters",
                "✔ " + " ".join(["installed"] * 30),
                0,
                f"BROKEN: {install_command} ended with {('✔ ' + ' '.join(['installed'] * 30))!r:.200}…, "
                + no_object.format(0)
                + install_fix,
            ),
            (
                "a JSON list is BROKEN",
                "[1, 2]",
                0,
                f"BROKEN: {install_command} ended with '[1, 2]', {no_object.format(0)}{install_fix}",
            ),
            (
                "an ok result without a scope is BROKEN",
                json.dumps({"outcome": "ok"}),
                0,
                f"BROKEN: {install_command} said ok without a scope string (scope is absent){install_fix}",
            ),
            (
                "an ok result whose scope is a number is BROKEN",
                json.dumps({"outcome": "ok", "scope": 5}),
                0,
                f"BROKEN: {install_command} said ok without a scope string (scope is 5){install_fix}",
            ),
            (
                "an object with no outcome is BROKEN",
                json.dumps({"scope": "user"}),
                0,
                f"BROKEN: {install_command} ended with " + bad_outcome.format("has no outcome") + install_fix,
            ),
            (
                "an outcome of another word is BROKEN",
                json.dumps({"outcome": "maybe", "scope": "user"}),
                0,
                f"BROKEN: {install_command} ended with "
                + bad_outcome.format("has the outcome 'maybe'")
                + install_fix,
            ),
            (
                "an outcome that is no string is BROKEN",
                json.dumps({"outcome": True, "scope": "user"}),
                0,
                f"BROKEN: {install_command} ended with "
                + bad_outcome.format("has the outcome True")
                + install_fix,
            ),
        ]
        for name, out, code, wanted in install_rows:
            expect(f"install replies: {name}", Scene(out=out, code=code, source="local"), wanted)
        work, repo = base / "work", base / "repo"
        work.mkdir()
        repo.mkdir()
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
            mock.patch.dict(os.environ, environment(Scene()) | {"FAKE_HANG_INSTALL": "1"}),
            mock.patch.dict(globals(), {"run": run_cut}),
        ):
            try:
                install("const-x", work, repo, "owner/repo", "toy-mp", pin_note, timeout=0.3)
                said_slow = "nothing raised"
            except (Broken, Refused) as slow:
                said_slow = f"{type(slow).__name__}: {slow}"
        version_case(
            "an install that gives no result within its timeout is BROKEN, no refusal, and its timeout is the"
            " one `run` waits for",
            said_slow == f"Broken: {install_command}{timed_out.format('0.3')}" and waits == [0.3],
            f"{said_slow} {waits}",
        )
        no_entry = "lists no entry whose id is " + key + " at the scope user the install wrote ({})"
        no_path = "gives no installPath string for " + key + " at scope user (installPath is {})"
        no_json = "printed no JSON ({!r}: Expecting value: line 1 column 1 (char 0))"
        missing, a_file = str(cache / "missing"), str(cache / "a-file")
        bare = {"id": key, "scope": "user"}

        def others(count: int) -> str:
            """A list of `count` entries at the install's scope, none of them with the id looked for."""
            return json.dumps([listed(id=f"const-{i}@toy-mp", installPath=str(other)) for i in range(count)])

        list_rows: list[tuple[str, str, str]] = [
            ("an empty list", "[]", no_entry.format("no entries")),
            (
                "an entry at another scope only",
                json.dumps([listed(scope="project")]),
                no_entry.format("entries: 'const-x@toy-mp' at 'project'"),
            ),
            (
                "two entries of the id at the install's scope",
                json.dumps([listed(), listed(installPath=str(other))]),
                "lists 2 entries whose id is " + key + " at the scope user the install wrote"
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
                no_entry.format("entries: " + ", ".join(f"'const-{i}@toy-mp' at 'user'" for i in range(5))),
            ),
            (
                "six entries of other ids, the first five named and the rest cut with …",
                others(6),
                no_entry.format(
                    "entries: " + ", ".join(f"'const-{i}@toy-mp' at 'user'" for i in range(5)) + ", …"
                ),
            ),
            (
                "entries that are no objects, shown as they are",
                json.dumps(["x", 7]),
                no_entry.format("entries: 'x', 7"),
            ),
            ("text that is no JSON", "no plugins installed", no_json.format("no plugins installed")),
            ("nothing", "", no_json.format("")),
        ]
        for name, listing, wanted in list_rows:
            expect(
                f"list replies: {name} is BROKEN",
                Scene(listing=listing, source="local"),
                f"BROKEN: {listing_command} {wanted}{list_fix}",
            )
        good = json.dumps([listed()])
        # A list command that wrote no reply (it exited other than 0, or timed out) has no reader to update:
        # its fix is the command's own, not `fix_of`'s; the lines are typed by hand
        list_where = "a folder of your own, CLAUDE_CONFIG_DIR set to an empty folder"
        put_first = (
            "put Claude Code 2.1.282 first on PATH for this run: either run sh scripts/setup-claude.sh in the"
            " kit's clone, then the check through sh scripts/gate-list.sh --run install-<module> (--run guide"
            " for the guide's check), which puts it first, or install it beside your own by hand (npm install"
            " --prefix <folder> @anthropic-ai/claude-code@2.1.282,"
            " then PATH=<folder>/node_modules/.bin:$PATH)"
        )
        off_what = "this run is on 2.1.286, not the pinned 2.1.282"
        fix_timed_out = " — fix: run the check again"
        fix_timed_out_off = f" — fix: {off_what}: run the check again on the pinned version, {put_first}"
        fix_exited = (
            f" — fix: run `claude plugin list --json` in {list_where}, read why it fails,"
            " then run the check again"
        )
        fix_exited_off = (
            f" — fix: run `claude plugin list --json` in {list_where}, read why it fails; {off_what}, so then"
            f" run the check again on the pinned version, {put_first}"
        )
        off_note = Note("2.1.282", "2.1.286")  # the state of a run on 2.1.286 with the opt-out set

        def list_said(scene: Scene, note: Note) -> str:
            """What `listed_install` says over the fake's list for `scene` in the state `note` records."""
            try:
                listed_install(key, "user", repo, environment(scene), note)
            except Broken as bad:
                return f"BROKEN: {bad}"
            return "no Broken"

        for code, wanted_on, wanted_off in (
            (1, fix_exited, fix_exited_off),
            (3, fix_exited, fix_exited_off),
            (124, fix_timed_out, fix_timed_out_off),
        ):
            for state, note, fix in (
                ("on the pin", pin_note, wanted_on),
                ("off the pin", off_note, wanted_off),
            ):
                said_list = list_said(Scene(listing=good, list_code=code), note)
                version_case(
                    f"list replies: a good list with exit {code} is BROKEN, {state},"
                    f" its fix the command's own{' (a timeout)' if code == 124 else ''}",
                    said_list == f"BROKEN: {listing_command} exited {code} ({good}){fix}",
                    said_list,
                )
        expect(
            "list replies: a good list with exit 1 is BROKEN, through the run",
            Scene(listing=good, list_code=1, source="local"),
            f"BROKEN: {listing_command} exited 1 ({good}){fix_exited}",
        )
        for state, note, fix in (
            ("on the pin", pin_note, fix_timed_out),
            ("off the pin", off_note, fix_timed_out_off),
        ):
            with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["claude"], 300)):
                said_list = list_said(Scene(listing=good), note)
            version_case(
                f"list replies: a list that times out is BROKEN, {state}, never a reader to update",
                said_list == f"BROKEN: {listing_command} exited 124 (timed out after 300 s){fix}",
                said_list,
            )
        on_project = json.dumps({"outcome": "ok", "scope": "project"})
        picks: list[tuple[str, Scene]] = [
            (
                "the entry at the right scope, an entry at another scope first, is the one",
                Scene(listing=json.dumps([listed(scope="project", installPath=str(other)), listed()])),
            ),
            (
                "the entry at the right scope, an entry at another scope last, is the one",
                Scene(listing=json.dumps([listed(), listed(scope="project", installPath=str(other))])),
            ),
            (
                "the entry of the id, entries of other ids around it, is the one",
                Scene(
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
                Scene(
                    out=on_project,
                    listing=json.dumps([listed(installPath=str(other)), listed(scope="project")]),
                ),
            ),
        ]
        for name, scene in picks:
            expect(f"list replies: {name}", replace(scene, source="local"), "on")
        no_commit = "BROKEN: the install record names no commit for " + key + " (<record>: {})"  # by hand
        unnamed = no_commit + fix_of("installed_commit", "a record")
        unnamed_off = no_commit + off_fix
        no_list = f"holds no list under plugins['{key}']"
        no_sha: dict[str, object] = {"installPath": str(copy)}
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
                json.dumps({"plugins": {"const-x@constitution-kit": [commit()]}}),
                no_list,
            ),
            (
                "a record whose entry for the id is an object",
                json.dumps({"plugins": {key: commit()}}),
                no_list,
            ),
            (
                "an entry whose installPath is another folder",
                recorded(commit(installPath=str(other))),
                f"holds no entry for {key} whose installPath is {copy}",
            ),
            (
                "entries that are no objects",
                json.dumps({"plugins": {key: ["x", 7]}}),
                f"holds no entry for {key} whose installPath is {copy}",
            ),
        ]
        for name, text, why in record_rows:
            expect(
                f"the record: {name} is BROKEN for a remote source", Scene(record=text), unnamed.format(why)
            )
        expect("the record: a commit gives the source at that commit", Scene(), "on", [sha])
        # none of the four variables reaches `claude`, whichever the person sets and to what: the platform's
        # plugins root is the check's own configuration's plugins/, where the record is read, and the folders
        # the person's variables name stay empty; the kept variables, PREFER_HTTPS, FAKE_KEEP and the seven
        # documented ones, reach it unchanged
        person_values = person_plugin_values(base)
        for variable, (what, set_value) in person_values.items():
            for name, value in ((what, set_value), ("set and empty", "")):
                driven = drive(Scene(), {variable: value} | kept_vars)
                seen_cache = cache_log.read_text(encoding="utf-8").splitlines() if cache_log.exists() else []
                version_case(
                    f"{variable} {name} in the person's environment: the marketplace add, the install and"
                    " the list run with the four absent, CLAUDE_CODE_PLUGIN_PREFER_HTTPS, FAKE_KEEP and the"
                    " seven documented ones as set, the record is read from the check's own configuration,"
                    " and the folders stay empty",
                    driven == ("on", [sha], [str(copy)])
                    and seen_cache
                    == [
                        f"plugin marketplace{seen_when_removed}",
                        f"plugin install{seen_when_removed}",
                        f"plugin list{seen_when_removed}",
                    ]
                    and all(list(Path(f).iterdir()) == [] for _, f in person_values.values() if f != "1"),
                    f"{driven} {seen_cache}",
                )
        wrong = commit(installPath=str(other), gitCommitSha=sha_wrong)
        right = commit(gitCommitSha=sha_right)
        # an entry whose installPath is the copy's leaf name in another folder: the whole path decides
        same_leaf = commit(installPath=str(other / copy.name), gitCommitSha=sha_wrong)
        no_install_path: dict[str, object] = {"scope": "user", "gitCommitSha": sha_wrong}
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
                f"the record: the entry of the installed copy is the one read, {name}",
                Scene(record=recorded(*entries)),
                "on",
                [sha_right],
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
            ("39 hexadecimal characters", sha[:-1]),
            ("41 hexadecimal characters", sha + "0"),
            ("63 hexadecimal characters", sha64[:-1]),
            ("65 hexadecimal characters", sha64 + "0"),
            ("an id in upper case, which git never writes", sha.upper()),
            ("an id in mixed case", sha[:20] + sha[20:].upper()),
            ("an id with a line break after it", sha + "\n"),
            ("an id with a space before it", " " + sha),
            ("an abbreviated id", sha[:7]),
            ("an id of 40 characters, one of them not hexadecimal", sha[:-1] + "g"),
        ):
            expect(
                f"the record: a commit that is {name} is BROKEN for a remote source, never handed to git",
                Scene(record=recorded(commit(gitCommitSha=value))),
                unnamed.format(f"gitCommitSha is no git object id ({id_form}), {value!r}"),
            )
        for name, value in (("40 hexadecimal characters", sha), ("64 hexadecimal characters", sha64)):
            expect(
                f"the record: a commit of {name} is an object id: the source is read at it",
                Scene(record=recorded(commit(gitCommitSha=value))),
                "on",
                [value],
            )
        long_value = "x" * 250
        expect(
            "the record: a commit that is a long word is quoted, cut at 200 characters",
            Scene(record=recorded(commit(gitCommitSha=long_value))),
            unnamed.format(f"gitCommitSha is no git object id ({id_form}), " + repr(long_value)[:200] + "…"),
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
            mock.patch.dict(os.environ, environment(Scene(record=recorded(commit(gitCommitSha=option))))),
            mock.patch.dict(globals(), {"KIT": git_kit}),
        ):
            try:
                check_module("const-x", "owner/repo", pin_note)
                handed = "no Broken"
            except Broken as broken:
                handed = unrecord(str(broken))
        version_case(
            "the record: a commit that is an option, with git really run, is BROKEN and git runs no command",
            handed.startswith("the install record names no commit for const-x@toy-mp (<record>:")
            and "gitCommitSha is no git object id" in handed
            and not marker.exists(),
            f"{handed} {marker.exists()}",
        )
        for name, text in (
            ("no record", ""),
            ("a record that is no JSON", "not json"),
            ("a record without a commit", recorded(no_sha)),
            ("a record of another install", recorded(commit(installPath=str(other)))),
        ):
            expect(
                f"the record: a local folder is compared with itself, {name} is read by no one",
                Scene(record=text, source="local"),
                "on",
            )
        drive(Scene())
        asked = fake_log.read_text(encoding="utf-8").splitlines()
        calls = [line.split(" | ") for line in calls_log.read_text(encoding="utf-8").splitlines()]
        version_case(
            "a run asks the marketplace, the install with --json and the list with --json, in the bare"
            " repository and the configuration folder of the run",
            asked
            == ["plugin marketplace add owner/repo", f"plugin install {key} --json", "plugin list --json"]
            and len(calls) == 3
            and calls[0][1:] == calls[1][1:] == calls[2][1:]
            and calls[0][1].endswith("/repo")
            and calls[0][2].endswith("/config"),
            f"{asked} {calls}",
        )

        def lines_of(scene: Scene, says: str, optout: bool, kit: Path = toy) -> tuple[int, list[str]]:
            """The exit and the lines `main` prints for the toy kit's module over the fake claude."""
            printed_lines = io.StringIO()
            with (
                mock.patch.dict(os.environ, environment(scene, says)),
                mock.patch.dict(globals(), {"KIT": kit}),
                contextlib.redirect_stdout(printed_lines),
            ):
                os.environ.pop("CONSTITUTION_KIT_ANY_CLAUDE", None)
                if optout:
                    os.environ["CONSTITUTION_KIT_ANY_CLAUDE"] = "1"
                status = main(["--module", "const-x", "--from", where(scene)])
            return status, [unrecord(line) for line in printed_lines.getvalue().splitlines()]

        off, pinned = "2.1.286 (Claude Code)\\n", "2.1.282 (Claude Code)\\n"
        stop = "BROKEN: the check could not run — 0 modules examined"
        refused_lines = [  # typed by hand: a message function cannot check itself
            f"RED: const-x: Claude Code refuses to install it (not_found: {gone}){{}}",
            f"  why: {WHY}",
            "  fix: fix its manifest or its entry in marketplace.json",
            "RED: 1 finding(s) — no install, from owner/repo{}",
        ]
        green = "GREEN: const-x installs and operates on a bare repository with its defaults"
        link_lines = [  # typed by hand: a module's link its copy lacks, a finding that is no refusal
            "RED: const-x: the link linked is missing in the installed copy{}",
            f"  why: {WHY}",
            "  fix: replace the link inside the module with the file it points at",
            f"RED: 1 finding(s) — 0 hook(s), 0 scan(s), 1 link(s), from {linked}{{}}",
        ]
        unreadable_lines = [  # typed by hand: a file the run could not read, after the version is known
            f"BROKEN: a file could not be read ([Errno 2] No such file or directory: '{no_kernel}/kernel')"
            " — fix: make the module's files readable{}",
            "BROKEN: the check could not run — 0 modules examined{}",
        ]
        reports: list[tuple[str, Scene, str, bool, int, list[str]]] = [
            (
                "a green run, off the pin",
                Scene(source="local"),
                off,
                True,
                EXIT_GREEN,
                [f"{green} — 0 hook(s), 0 scan(s), 0 link(s), from {toy}{off_pin}"],
            ),
            (
                "a green run, on the pin",
                Scene(source="local"),
                pinned,
                False,
                EXIT_GREEN,
                [f"{green} — 0 hook(s), 0 scan(s), 0 link(s), from {toy}"],
            ),
            (
                "a finding of the installed copy, off the pin",
                Scene(source="linked"),
                off,
                True,
                EXIT_RED,
                [line.format(off_pin) for line in link_lines],
            ),
            (
                "a finding of the installed copy, on the pin",
                Scene(source="linked"),
                pinned,
                False,
                EXIT_RED,
                [line.format("") for line in link_lines],
            ),
            (
                "a refusal, off the pin",
                Scene(out=failed_line, code=1),
                off,
                True,
                EXIT_RED,
                [line.format(off_pin) for line in refused_lines],
            ),
            (
                "a refusal, on the pin",
                Scene(out=failed_line, code=1),
                pinned,
                False,
                EXIT_RED,
                [line.format("") for line in refused_lines],
            ),
            (
                "an install that printed nothing, off the pin",
                Scene(out=""),
                off,
                True,
                EXIT_BROKEN,
                [
                    f"BROKEN: {install_command} printed nothing on standard output (exit 0)"
                    + off_fix
                    + off_pin,
                    stop + off_pin,
                ],
            ),
            (
                "an install that printed nothing, on the pin",
                Scene(out=""),
                pinned,
                False,
                EXIT_BROKEN,
                [f"BROKEN: {install_command} printed nothing on standard output (exit 0){install_fix}", stop],
            ),
            (
                "an install record without a commit, off the pin",
                Scene(record=recorded(no_sha)),
                off,
                True,
                EXIT_BROKEN,
                [unnamed_off.format("gitCommitSha is absent") + off_pin, stop + off_pin],
            ),
            (
                "a list without the install, off the pin",
                Scene(listing="[]"),
                off,
                True,
                EXIT_BROKEN,
                [
                    f"BROKEN: {listing_command} {no_entry.format('no entries')}{off_fix}{off_pin}",
                    stop + off_pin,
                ],
            ),
            (
                "a list that exits 1, off the pin",
                Scene(listing=good, list_code=1),
                off,
                True,
                EXIT_BROKEN,
                [f"BROKEN: {listing_command} exited 1 ({good}){fix_exited_off}{off_pin}", stop + off_pin],
            ),
            (
                "a list that exits 1, on the pin",
                Scene(listing=good, list_code=1),
                pinned,
                False,
                EXIT_BROKEN,
                [f"BROKEN: {listing_command} exited 1 ({good}){fix_exited}", stop],
            ),
        ]
        for name, scene, says, optout, status_wanted, lines_wanted in reports:
            got_status, got_lines = lines_of(scene, says, optout)
            version_case(
                f"the report of {name} is its literal lines, the note at the end of each headline",
                (got_status, got_lines) == (status_wanted, lines_wanted),
                f"{got_status} {got_lines}",
            )
        # the kit's own variables are read by the check itself, not taken away with the four: the source is
        # CONSTITUTION_KIT_INSTALL_FROM and the run on another version goes on by CONSTITUTION_KIT_ANY_CLAUDE
        # while all four are set; the fake claude, run by the same check, holds none of the four
        env_kit = {variable: set_value for variable, (_, set_value) in person_values.items()}
        env_kit |= kept_vars | {FROM_ENV: str(toy), "CONSTITUTION_KIT_ANY_CLAUDE": "1"}
        env_kit |= environment(Scene(source="local"), off)
        printed_kit = io.StringIO()
        with (
            mock.patch.dict(os.environ, env_kit),
            mock.patch.dict(globals(), {"KIT": toy}),
            contextlib.redirect_stdout(printed_kit),
        ):
            status_kit = main(["--module", "const-x"])
        seen_kit = cache_log.read_text(encoding="utf-8").splitlines() if cache_log.exists() else []
        version_case(
            "all four set in the person's environment, with CONSTITUTION_KIT_INSTALL_FROM and"
            " CONSTITUTION_KIT_ANY_CLAUDE=1: both still read by the check (the source, the run on another"
            " version with its note), and every claude command runs with the four absent",
            (status_kit, [unrecord(line) for line in printed_kit.getvalue().splitlines()])
            == (EXIT_GREEN, [f"{green} — 0 hook(s), 0 scan(s), 0 link(s), from {toy}{off_pin}"])
            and seen_kit
            == [
                f"--version {seen_when_removed}",
                f"plugin marketplace{seen_when_removed}",
                f"plugin install{seen_when_removed}",
                f"plugin list{seen_when_removed}",
            ],
            f"{status_kit} {printed_kit.getvalue()!r} {seen_kit}",
        )
        for name, says, optout, note_wanted in (
            ("off the pin", off, True, off_pin),
            ("on the pin", pinned, False, ""),
        ):
            got_status, got_lines = lines_of(Scene(), says, optout, no_kernel)
            version_case(
                f"a file the run cannot read, {name}: the two BROKEN lines, the note at the end of each",
                (got_status, got_lines)
                == (EXIT_BROKEN, [line.format(note_wanted) for line in unreadable_lines]),
                f"{got_status} {got_lines}",
            )
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
    total = len(cases) + len(unreadable) + 6 + extra
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
