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
own; the environment's CLAUDE_CODE_PLUGIN_CACHE_DIR, CLAUDE_CODE_PLUGIN_SEED_DIR, CLAUDE_CODE_PLUGIN_DIRS and
CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE, each set or empty, removed from the environment of the version command and
of the whole run (`kit_module_doc.claude_env`), so that no `claude` command the check starts holds one
unless a block sets it itself, the case the cache's fix names for the first on the pinned version. They steer
where Claude Code finds, keeps or loads plugins, as its documentation and a probe of 2.1.282 show: the first
would have it write the kit's marketplace, its plugin cache and its records under the folder it names, a
person's own plugins root perhaps, and not into the run's empty configuration, and the plugins root is
otherwise `plugins` in the run's CLAUDE_CONFIG_DIR; the second, a session load the kit's plugins from the
cache of a read-only seed; the third, a session load a plugin folder in place of the install the claims
read; the fourth, the install write a zip file where the claims read a folder. Every other variable reaches
the version command and the run unchanged, CLAUDE_CODE_PLUGIN_PREFER_HTTPS, which the kit's CI sets for the
clone of its private repository over HTTPS, and the kit's own CONSTITUTION_KIT_* ones included, save those
the check sets itself, CLAUDE_CONFIG_DIR and DISABLE_AUTOUPDATER for both, HOME and GIT_CONFIG_GLOBAL for
the run; the kit cloned from the working
folder's HEAD to ~/dev/constitution-kit, so what is not committed is not run; the source the marketplace
block registers pointed at the change: the argument of its `claude plugin marketplace add` replaced by the
environment's CONSTITUTION_KIT_INSTALL_FROM, `<owner>/<repo>#<branch>` (the kit's CI names the change's GitHub
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
  marketplace  `claude plugin marketplace list --json`, run in the folder the block ended in, lists
               exactly one entry named as the kit's marketplace, by the name the clone's
               .claude-plugin/marketplace.json gives, read once by `kit_module_doc.marketplace_name`
               and typed nowhere: the later claims' `<module>@<name>` ids and install fix all use
               it; its `source` is github and its `repo` the source's repository: a local folder
               would run in place, never from the cache; and its `installLocation`, the platform's
               clone of the marketplace, holds the same modules at the same manifest versions as the
               kit's clone.
  install      `claude plugin list --json`, run in the project, lists each module of the kit once at
               project scope for the project (`id` the module's `<module>@<name>`, `scope` project,
               `projectPath` the project), its `version` the manifest's and its `installPath` the
               module's copy in the plugin cache, an existing folder, and the module is enabled in the
               project's .claude/settings.json. The copy is `cache/<name>/<module>/<version>/` under
               the plugins root (`Run.cached`): <name> the marketplace's, <version> the manifest's,
               and the root `plugins` in the run's CLAUDE_CONFIG_DIR, the environment the run gives its
               blocks holding none of the four variables `kit_module_doc.claude_env` removes, the plugins
               root CLAUDE_CODE_PLUGIN_CACHE_DIR among them, unless a block sets one itself. The `installPath`
               and that path are compared
               resolved, links and `..` followed: a copy kept in the marketplace's clone, in place, in
               the cache at another version, or in another marketplace's cache is a finding. And a
               headless session in the project, trusted in the configuration, reports each module's
               path as that cached copy — the frozen copy, never a clone's working files. The path is
               reported before the model is called, so the session needs no login. The fix of a copy
               listed outside the cache (`cache_fix`), on the pinned version: make the block install from
               the marketplace and set none of the four variables (`CACHE_FIX` names them, from
               `PLUGIN_PLACE_ENV`) in a block, or, if the platform now
               copies elsewhere, correct `Run.cached`; off the pin, where the reader is the pinned
               version's and not this one's, to run the check again on the pinned version.
  kernel       the project's docs/constitution/ holds every file of the kit's kernel/, and the kit's
               LICENSE and NOTICE, byte for byte.
  dials        not run: written as the project's constitution.yaml, and with it what the reader
               writes by hand, from the check's fixture — one policy per namespace of the dials that
               claims a territory, the root at `root_policy`, and decision record #1, named and placed by
               the dials' first catalog.
  scan         the block's exit: every scan it runs exits 0.
  commit       the project's working tree is clean.
  update       every module is listed as the install claim has it, at its manifest version, its
               `installPath` the cached copy, a folder, and enabled. That an update leaves a draft's
               change at an unchanged version untaken is not run: the platform fetches a GitHub
               marketplace from GitHub alone, so the run cannot put a change where it looks; the guide
               states it as an observed platform fact.
  reinstall    every module is listed as the install claim has it, and its cached copy holds the
               same files as the module in the marketplace's `installLocation`, read through its
               links, byte for byte: the install copied what the marketplace holds.
  uninstall    no module is enabled in the project's settings or listed by `claude plugin list --json`
               with the project as its `projectPath`, at any scope.
The first finding of the run ends it, since every later block builds on the one before. A finding
is red; a failure to run is a configuration failure, and each prints its own fix.
A missing `git`, met first when the guide is read, "install it and put it on PATH"; a `git`, `bash` or
`claude` not on PATH when the run starts, "install it; the check runs the guide's commands with it".
A guide that cannot be read: a folder that is no clone with a commit, "run the check from a clone of the
kit"; a guide not committed at HEAD, "commit the guide"; a file that cannot be read or written, "make the
kit's files readable and the system's temporary folder writable". A source the check cannot point at the
change: no origin on GitHub, "add one"; a detached HEAD, "check out a branch"; a branch whose origin copy
is not at HEAD, "push the branch (git push)"; each ends with "or set CONSTITUTION_KIT_INSTALL_FROM=
<owner>/<repo>#<branch>". A clone whose marketplace.json gives no name, each fault with the fix
`kit_module_doc.marketplace_name` prints: missing, "run the check from a checkout of the kit, which holds
the file"; no JSON, "restore the file as a JSON object"; no object, "restore the file as an object with
the marketplace's "name""; no "name", "give the marketplace its name, at the top of the object"; a "name"
that is no string, "write the name as a JSON string"; an empty one, "write the marketplace's name in it".
A `--json` command that fails, an exit other than 0 or a timeout (its exit 124), wrote no reply for a
reader to read: a configuration failure whose fix is worded by `kit_module_doc.command_fix` from the state
of the run, never a change to the guide: after a timeout, "run the check again"; after another exit, to run
the command in a folder of one's own with CLAUDE_CONFIG_DIR set to an empty folder, read why it fails, and
run the check again; off the pin, either one adds the run on the pinned version. A reply the claims
cannot read as documented: a reply that is no JSON or no list, an entry that is no object, an entry whose
identifying field is no string or is empty (`name` in the marketplace list, `id` in the plugin list, of an
entry of another marketplace or plugin too), two entries of the marketplace's name or two project-scope
entries of a module's id for the project, a field a claim reads (`source`, `installLocation`, `repo` of a
`github` entry, `installPath`, `version`, `scope`, and `projectPath` of a project- or local-scope entry)
that is no string or is empty, an `installLocation` that names no existing folder, a project's
.claude/settings.json that is unreadable, no JSON object, or whose `enabledPlugins` is no object, and the
headless session's `system/init` event, the first one of the stream being the one read, as the headless
page documents it: `plugins`, an array of objects each with a `name` and a `path`, both strings and not
empty. A `plugins` that is absent or no list, an entry that is no object, a `name` or `path` that is
absent, no string or empty, and two entries of one name, whatever their paths, are each a failure to run
(`init_paths`). The fix of these alone is worded by
`kit_module_doc.platform_fix` from the state of the run, and is never a change to the guide: on the pinned
version it is to update the kit's reader that the line names (`listed`, `platform_clone`,
`project_entries`, `session_paths` or `enabled`), to what that version writes; off the pin, to run again
on the pinned version. Of the same event three things stay findings against the guide, red with a fix of
their own, since the event is read whole: a well-formed `plugins` list that lacks a module of the kit, a
module whose path is not its copy in the plugin cache, and a session whose stream holds no init event.
Every other configuration failure prints a fix of its own, such as a module folder, document or manifest that
cannot be read (`kit_module_doc.module_folders`; a manifest with no version), a dials example the check
cannot read or place the first record by ("correct the guide's check=dials block"), a credential setting
that cannot be carried into the run ("correct that entry in the global git configuration") and a clone
that cannot be made ("check the clone"). Needs no
Claude account login: the plugin commands read none, and the session stops before the model. Git needs a
private repository's credentials.

The check asks `claude --version` (`kit_module_doc.claude_note`) before the clone and before any block runs,
and after the steps that run no `claude` command, in this order: the guide is read as committed at HEAD (a
missing `git`, a folder that is no clone, a guide not committed: BROKEN); its marks are read (a mark finding:
RED, no block run); the marketplace block is held to run `claude plugin marketplace add <source>` (if not:
RED, no block run); the source the block registers is taken (no origin on GitHub, a detached HEAD, or an
origin not at HEAD: BROKEN); `git`, `bash` and `claude` are found on PATH (BROKEN). The lines of a run that
ends at one of these steps, or at the version check itself, carry no note, since the version is not yet
known. The version is compared with the one the working folder's scripts/claude-code.version pins, which the
CI workflow installs from too; the clone carries the same file. It is the first word of the first non-blank
line of the output of `claude --version`. The pinned version: the run goes on. Another readable version: a
configuration failure, whose fix (`kit_module_doc.put_first`) has the check run on the pinned Claude Code
put first on PATH beside the person's own, which stays as it is: through `sh scripts/setup-claude.sh` and the
gate list, `sh scripts/gate-list.sh --run guide`, first, an install by hand second, unless
the environment's CONSTITUTION_KIT_ANY_CLAUDE is exactly `1`: the run then goes on, and each `RED:` finding
headline, each `BROKEN:` line and the closing `GREEN:` or `RED:` line from then on ends with a note naming
both versions. No readable version (the command fails, prints nothing, or opens with a word that is no
version) and a pin file that is missing, empty or no one version are configuration failures whatever the
variable says.

What the check reads of Claude Code, all as it writes it at the version scripts/claude-code.version pins.
From documented `--json` output: `claude plugin marketplace list --json`, per entry `name`, `source`, `repo`
(of a `github` entry) and `installLocation`; `claude plugin list --json`, per entry `id`, `scope`,
`version`, `installPath` and `projectPath` (required of a project- or local-scope entry). From documented
files: the project's .claude/settings.json, its `enabledPlugins`; the first `system/init` event of the
headless session's stream, its `plugins` with their `name` and `path`; and the trust flag
`projects[<project>].hasTrustDialogAccepted` of <config>/.claude.json, which the check writes before the
session, adding its key to whatever the file holds, documented for ~/.claude.json and put under
CLAUDE_CONFIG_DIR, the folder that holds the platform's settings. From a documented layout: the plugin
cache's path, `cache/<marketplace>/<plugin>/<version>/` under the plugins root ("Find plugins on disk" of the
loading page), a path the check builds and compares with the `installPath` of the list; the root is
`~/.claude/plugins` unless CLAUDE_CODE_PLUGIN_CACHE_DIR names it, a variable the check removes from the
environment it runs `claude` in, with three more (`kit_module_doc.claude_env`), so the root under
CLAUDE_CONFIG_DIR, `plugins` in it, is that default read from CLAUDE_CONFIG_DIR's own meaning. From an
undocumented place: none, since the record files of Claude Code are not read, and the plugin cache is read
only through the documented path of a module's copy; the files under an `installLocation` and under that
copy are read as plain files.

Modes:  no arguments   check the kit's guide;
        --self-test    prove the check with a toy kit, a toy guide and a fake `claude` that logs to a
                       file, in the groups that follow.
                       The marks: each kind of mark finding red once from the text alone; a mark where a
                       fence's language should be red; a misplaced dials mark red once, its fix a `yaml`
                       fence; a green guide's marks, a `text` fence needing none.
                       The guide as read: a guide not committed at HEAD a configuration failure, and the
                       committed one read whole, standard output alone; a folder that is no clone a
                       configuration failure, to the guide's reader and to the run; the toy kit left as it
                       was; a run whose git writes a trace to stderr green.
                       The run: a green toy run green; a block that exits 1 red; a block that reads another
                       block's variable red, though it would pass under `bash -e`; the dials before the
                       project red; a marketplace block with no source to point red.
                       Each claim red once against a fake or a block that breaks it: a block that makes no
                       repository, a marketplace never added, one added from a folder, an install that
                       enables nothing, a session that runs a module in place, a kernel copy that copies
                       nothing, one that leaves the license out, a commit that leaves the tree dirty, an
                       update that drops a module, a reinstall whose copy differs from the marketplace, an
                       uninstall that keeps the plugin enabled.
                       The installs and uninstalls as the platform lists them: an install listed for no
                       project, at user scope, for another project or at another version, in the
                       marketplace's clone (in place), at another version in the right cache or in a plugins
                       root a block moved, an uninstall that keeps the plugin installed or enabled alone or
                       leaves an entry of the user, local or managed scope for the project, each red.
                       The findings and their fixes: a marketplace from another repository, one whose
                       modules differ from the kit's and the fix it teaches, each marketplace and install
                       finding's own fix and the fix of a marketplace and an install block that exits 1, a
                       session that loads no module and one that reports no start, its own reason quoted.
                       The copies: a reinstall copy that lacks a file of the marketplace, the toy modules'
                       links into a toy shared/ read through on both sides, a reinstall that compares with
                       the clone the run kept, else the one listed.
                       The source and the credentials: the outer credential settings carried into the run
                       as git reads them, includes followed, nothing else of the outer configuration, and
                       the carried helper reaching the run's git; the source taken from the environment,
                       from origin at the branch's HEAD, and a kit with no origin on GitHub, a detached
                       HEAD and an origin behind HEAD each a configuration failure.
                       The report of one finding as literal lines with exit 2.
                       The kit's modules, the folders of `kit_module_doc.module_folders` with their
                       manifest versions: a folder `.x` or `_x` and a plain file skipped, a name without
                       `const-` listed, the list sorted whatever order the folder lists, and a folder
                       without its MODULE.md, a tree with no modules/, a modules/ with no folder and a
                       manifest with no version each a BROKEN.
                       The marketplace's name: the toy kit's marketplace named `toy-mp`, which the toy
                       guide's commands and the fake follow, so the green run, each claim's text and the
                       install fix use that name and no other; `kit_module_doc.marketplace_name` over a
                       file naming `toy-mp` and each of the six files it cannot read, the literal message
                       of each; a toy kit whose marketplace.json gives no name a BROKEN.
                       The pin: `kit_module_doc.pinned_claude` over a pin file of each form, the literal
                       message of each.
                       The version check: a fake `claude` that answers `--version` with the toy kit's pin,
                       another version, a longer or shorter one, no version, blank lines before the
                       version, a failure and a crash, the variable unset, at each other value than `1`
                       and at `1`; the run stopped before the clone with only `--version` run; the version
                       command run in an empty configuration folder of its own, the auto-updater off and
                       the four variables of `claude_env` absent, each of them set to a folder or to `1`
                       and set empty in the person's environment, CLAUDE_CODE_PLUGIN_PREFER_HTTPS and an
                       unrelated variable kept;
                       the reports of a run off the pin, a green one's and a finding's, as literal lines.
                       The platform's replies: the fake answering `plugin marketplace list --json` and
                       `plugin list --json` from a state of its own; the two readers over whole sets of
                       replies, an entry that is not the marketplace's or the module's for the project
                       first and last, a project's settings.json of each shape; an entry whose `name`
                       (marketplace list) or `id` (plugin list) is absent, no string or empty, a BROKEN
                       alone, first, between and last, whatever else the list holds; a valid list on
                       standard output with a warning on standard error read as the list; the marketplace
                       list run in the folder the block ended in and the plugin list in the project, in
                       the readers and in a whole run; a list that times out, at a timeout the runner is
                       given, a BROKEN and never an empty list (the process mocked, no wait); the update
                       claim over a local-scope entry of the id before, after and round the project-scope
                       one, the project-scope one picked, and over an `installPath` in the cache that is a
                       file or no folder, and one outside the cache copy `Run.cached` gives, naming both
                       places: in the marketplace's clone, in the right cache at another version, in
                       another marketplace's cache, at the module's folder without its version, below the
                       copy, each a finding, and a link to the copy or a path through `..` none; the cache's
                       path the same whatever CLAUDE_CODE_PLUGIN_CACHE_DIR the state's environment holds
                       (set to a folder, set and empty), and that variable not followed by the claim, copies
                       under the folder it names a finding; the fix of such a finding, `cache_fix`, on the
                       pin and off it, and off it in a whole run with the opt-out; a whole run with the
                       one of the four set in the person's environment, to a folder or `1` and empty:
                       green, every `claude` command (the version, the plugin commands, the session) run
                       with the four absent and the kept variables as set, and the folders the variables
                       name left empty; a block that exports one of the four itself, the variable present
                       for the commands of that block alone; CONSTITUTION_KIT_INSTALL_FROM still read
                       with the four set.
                       The lists that fail: a marketplace list and a plugin list that exit 1, 3 or 124 or
                       time out (the process mocked), a BROKEN with the fix `kit_module_doc.command_fix`
                       words, never a reader to update, on the pin and off it.
                       The session's init event: each fault of `plugins` that the headless page does not
                       document, a BROKEN that says what was found, the entry's place, the field and its
                       value where there is one, with the fix naming `session_paths`, never a finding
                       against the guide: `plugins` absent, null, an object or a string; an entry that is
                       a string; a `name` or a `path` that is absent, empty or a number; two entries of
                       one name, with the same path and with different ones, three of one name, and a name
                       with a line break; one of them in a whole run through `main`, off the pin and on it,
                       as literal lines; a built-in plugin, whose path is no folder, beside the modules
                       green; a second init event after a good first, malformed or with other paths, never
                       read; and the findings that stay: a well-formed list that holds a built-in plugin
                       alone or loads no module, a session whose path is its module's folder in place, and
                       a session that reports no start.
                       The BROKEN lines: a `repo` that is absent, empty or no string and an
                       `installLocation` that names no folder each a BROKEN and not a finding, a quotation
                       cut at 200 characters, the literal message of each BROKEN a reply or a settings file
                       gives, its fix as worded on the pinned version, and off the pin for one of them, a
                       list that is no JSON, in the whole report of the wrong shapes below.
                       The wrong shapes: each wrong shape of a reply, in a run, a BROKEN and never a
                       finding against the guide; one whole report of it through `main`, off the pin and on
                       it, as of a green run, a finding and a file the blocks' run cannot read.
Exit:   0 green; 2 a finding; 1 the check could not run.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import itertools
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
from kit_module_doc import (
    PLUGIN_PLACE_ENV,
    PLUGINS_ROOT_ENV,
    DocumentError,
    Note,
    claude_env,
    claude_note,
    command_fix,
    marketplace_name,
    module_folders,
    pinned_claude,
    platform_fix,
    put_first,
)

KIT = Path(__file__).resolve().parent.parent
GUIDE = "INSTALL.md"
EXIT_GREEN, EXIT_BROKEN, EXIT_RED = 0, 1, 2
CLONE = Path("dev") / "constitution-kit"  # the guide's placeholder for the kit's clone, rule 4 of plc-0011
SCRIPT = "scripts/check-install-guide.py"  # named in the fix of a reply the check's readers do not read
LIST_WHERE = (
    "a folder of your own, CLAUDE_CONFIG_DIR set to an empty folder"  # where a failed list is run again
)
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
CACHE_ENV = PLUGINS_ROOT_ENV  # the plugins root, "Find plugins on disk" of the loading page; one of the four
ADD = re.compile(r"(claude plugin marketplace add\s+)(\S+)")  # the source the marketplace block registers
GITHUB_URL = re.compile(r"github\.com[:/]([^/\s]+/[^/\s]+?)(?:\.git)?/?$")
LICENSE_FILES = ("LICENSE", "NOTICE")  # the kit's license and credit, copied beside the kernel
RECORD_SLUG = "adopt-constitution-kernel"
WHY = "a command nobody runs drifts from the platform unseen (rule 4 of plc-0011-install-guide)"
TIMEOUT = 900


class Broken(Exception):
    """The check could not run; the message says why and how to fix it. `note` is the note of a run on
    another Claude Code than the pin, set once the version is known, which ends each BROKEN line. `ran` is
    the number of blocks that ran before the failure, set once by `run_blocks` where its loop re-raises;
    a failure before any block leaves it 0."""

    note = ""
    ran = 0

    def stop(self) -> str:
        """The could-not-run line of a BROKEN report: no block ran, or how many ran before the failure."""
        said = "0 blocks run" if not self.ran else f"{self.ran} block(s) run"
        return f"BROKEN: the check could not run — {said}{self.note}"


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


def fence_block(lines: list[str], start: int, opened: re.Match[str]) -> tuple[Block, int]:
    """The block whose fence `opened` at `lines[start]`, and the index of the line after its closing fence."""
    indent, fence, info = opened.group(1), opened.group(2), opened.group(3).strip()
    body: list[str] = []
    end = start + 1
    while end < len(lines):
        closing = FENCE.match(lines[end])
        if closing and closing.group(2)[0] == fence[0] and len(closing.group(2)) >= len(fence):
            if not closing.group(3).strip():
                break
        body.append(lines[end][len(indent) :] if lines[end].startswith(indent) else lines[end].lstrip())
        end += 1
    words = info.split()
    language = words[0] if words else ""
    mark = MARK.search(" ".join(words[1:]))
    return Block(start + 1, language, mark.group(1) if mark else "", "\n".join(body) + "\n"), end + 1


def fenced_blocks(guide: str) -> list[Block]:
    """Every fenced block of the guide with its mark, in the order they stand."""
    found: list[Block] = []
    lines = guide.splitlines()
    i = 0
    while i < len(lines):
        opened = FENCE.match(lines[i])
        if not opened:
            i += 1
            continue
        block, i = fence_block(lines, i, opened)
        found.append(block)
    return found


def mark_finding(block: Block, seen: dict[str, int]) -> Finding | None:
    """The finding the mark of one block gives, None for a right mark; a first named block is entered in
    `seen` with its line."""
    if block.language.startswith("check="):
        return Finding(
            block.line,
            f"the fence opens with {block.language} where its language should stand",
            f"write the language first, then the mark: "
            f"```{'yaml' if block.language == 'check=dials' else 'bash'} {block.language}",
        )
    if block.language == "bash" and not block.name:
        return Finding(
            block.line,
            "a `bash` block names no check",
            f"write `check=<name>` after `bash` in its fence — one of {', '.join(NAMES)} — "
            "or `check=none` for a block the check does not run",
        )
    if not block.name or block.name == "none":
        return None
    if block.name not in NAMES:
        return Finding(
            block.line,
            f"check={block.name} is no name the check knows",
            f"use one of {', '.join(NAMES)}, or `none`",
        )
    wanted = "yaml" if block.name == "dials" else "bash"
    if block.language != wanted:
        return Finding(
            block.line,
            f"check={block.name} stands on a `{block.language}` fence",
            f"name a `{wanted}` fence check={block.name}",
        )
    if block.name in seen:
        return Finding(
            block.line,
            f"check={block.name} stands a second time, first at line {seen[block.name]}",
            "give each named block a name of its own: join the two blocks, or name one `none`",
        )
    seen[block.name] = block.line
    return None


def missing_findings(seen: dict[str, int], findings: list[Finding]) -> list[Finding]:
    """The finding for each name that no block carries and no finding already speaks of."""
    missing: list[Finding] = []
    for name in NAMES:
        said = (f"check={name} ", f"the fence opens with check={name} ")
        if name not in seen and not any(f.what.startswith(said) for f in findings):
            missing.append(
                Finding(
                    0, f"no block is named check={name}", f"name the block that {DOES[name]} check={name}"
                )
            )
    return missing


def blocks_of(guide: str) -> tuple[list[Block], list[Finding]]:
    """Every fenced block of the guide with its mark, and the findings the marks give."""
    found = fenced_blocks(guide)
    findings: list[Finding] = []
    seen: dict[str, int] = {}
    for block in found:
        finding = mark_finding(block, seen)
        if finding:
            findings.append(finding)
    findings += missing_findings(seen, findings)
    return [b for b in found if b.name in NAMES and seen.get(b.name) == b.line], findings


def spawn(
    argv: list[str], cwd: Path, env: dict[str, str], timeout: int
) -> subprocess.CompletedProcess[str] | None:
    """One command run to its end, None when it timed out; a missing program is a Broken."""
    try:
        return subprocess.run(
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
        return None


def run(
    argv: list[str], cwd: Path, env: dict[str, str], timeout: int = TIMEOUT, joined: bool = True
) -> tuple[int, str]:
    """The exit and the output of one command: standard output and error joined, for a message, or
    standard output alone where the output is read as data."""
    done = spawn(argv, cwd, env, timeout)
    if done is None:
        return 124, f"timed out after {timeout} s"
    both = done.stdout + ("\n" if done.stdout and done.stderr else "") + done.stderr  # never one line of two
    return done.returncode, (both if joined else done.stdout).strip()


def run_apart(
    argv: list[str], cwd: Path, env: dict[str, str], timeout: int = TIMEOUT
) -> tuple[int, str, str]:
    """The exit, the standard output and the standard error of one command, apart: the output is read as
    data and the error is for a message. A timeout is exit 124, no output and the reason as the error."""
    done = spawn(argv, cwd, env, timeout)
    if done is None:
        return 124, "", f"timed out after {timeout} s"
    return done.returncode, done.stdout, done.stderr


def last_line(said: str) -> str:
    return said.splitlines()[-1] if said else "no output"


def modules_of(kit: Path) -> dict[str, str]:
    """Each module of the kit with its manifest version, the folders those of the kit's one listing,
    `kit_module_doc.module_folders`: a plain file there is none, a name without `const-` is one, a
    folder without its MODULE.md, and a tree with no modules/, are BROKEN; so is a manifest that cannot be
    read, is no JSON object, has no `version`, or whose `version` is no string or number."""
    found: dict[str, str] = {}
    try:
        folders = module_folders(kit)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad
    for folder in folders:
        manifest = folder / ".claude-plugin" / "plugin.json"
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError) as bad:
            raise Broken(f"{manifest} gives no version ({bad}) — fix: restore the module's manifest") from bad
        if not isinstance(data, dict):
            raise Broken(
                f"{manifest} is no JSON object, it holds a {type(data).__name__}"
                " — fix: restore it as a JSON object"
            )
        if "version" not in data:
            raise Broken(f"{manifest} gives no version ('version') — fix: restore the module's manifest")
        version = data["version"]
        if isinstance(version, bool) or not isinstance(version, (str, int, float)):
            raise Broken(
                f"{manifest} gives a version that is no string or number, it holds a {type(version).__name__}"
                " — fix: restore the module's manifest"
            )
        found[folder.name] = str(version)
    if not found:
        raise Broken(f"no module under {kit / 'modules'} — fix: run the check from a clone of the kit")
    return found


def read_json(path: Path) -> dict[str, object]:
    """A JSON object from a file, `{}` for a file that is missing, no JSON or no object: for the trust
    write of `session_paths` alone, which adds its key to whatever the file holds and reads nothing of it."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def enabled(project: Path, note: Note) -> set[str]:
    """The plugins `enabledPlugins` of the project's .claude/settings.json (documented) holds as true. No
    file, or no `enabledPlugins` in it, enables none; a file that cannot be read, is no JSON or no object,
    or an `enabledPlugins` that is no object, is a Broken: a fault of the platform's write, never empty."""
    path = project / ".claude" / "settings.json"
    fix = platform_fix(note, SCRIPT, "enabled", "a settings file")
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return set()
    except OSError as bad:
        raise Broken(f"{path} cannot be read ({bad.strerror}){fix}") from bad
    try:
        data = json.loads(text)
    except ValueError as bad:
        raise Broken(f"{path} is no JSON ({bad}){fix}") from bad
    if not isinstance(data, dict):
        raise Broken(f"{path} is a JSON {type(data).__name__}, not an object{fix}")
    if "enabledPlugins" not in data:
        return set()
    plugins = data["enabledPlugins"]
    if not isinstance(plugins, dict):
        raise Broken(f"{path} gives an enabledPlugins that is a {type(plugins).__name__}, not an object{fix}")
    return {str(k) for k, v in plugins.items() if v is True}


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
    note: Note  # the state of the run against the pin: the note a run off it ends its lines with, and the fix
    project: Path | None = None
    clone: Path | None = None  # the platform's clone of the marketplace, its installLocation, once read

    def key(self, module: str) -> str:
        """The id the platform lists a module of the kit's marketplace by."""
        return f"{module}@{self.marketplace}"

    def cached(self, module: str) -> Path:
        """Where the platform copies a module of the kit's marketplace at install, in the layout that "Find
        plugins on disk" of its loading page documents: `cache/<marketplace>/<plugin>/<version>/` under the
        plugins root, the manifest's version here. The root is `plugins` in the run's configuration folder:
        the run's environment holds none of the four variables of `kit_module_doc.claude_env`, the plugins
        root CLAUDE_CODE_PLUGIN_CACHE_DIR the one that names a root (`run_blocks` removes them), so the
        platform is given no other root unless a block sets that variable itself, the case the cache's fix
        names on the pinned version."""
        return self.config / "plugins" / "cache" / self.marketplace / module / self.modules[module]


def shown(value: object) -> str:
    """A reply of Claude Code, or a field of it, as a message quotes it: its repr, at most 200 characters."""
    text = repr(value)
    return text if len(text) <= 200 else text[:200] + "…"


def listed(argv: list[str], cwd: Path, env: dict[str, str], note: Note) -> list[dict[str, object]]:
    """The entries of `claude <argv>`, a documented `--json` command that prints a JSON list of objects: a
    command that fails, a reply that is no JSON or no list, and an entry that is no object are each a Broken
    saying what was found. The fix of a command that fails (an exit other than 0, a timeout's 124 included)
    is the command's own, `kit_module_doc.command_fix`, since it wrote no reply; that of a reply that is no
    JSON, no list or holds an entry that is no object points at the Claude Code version, `platform_fix`."""
    command = f"`claude {' '.join(argv)}`"
    fix = platform_fix(note, SCRIPT, "listed", "a reply")
    code, out, err = run_apart(["claude", *argv], cwd, env)
    if (
        code != 0
    ):  # no reply was written: no reader to update, whatever the exit; 124 is `run_apart`'s timeout
        said = command_fix(note, command.strip("`"), LIST_WHERE, timed_out=code == 124)
        raise Broken(f"{command} exited {code} ({last_line((err or out).strip())}){said}")
    try:
        reply = json.loads(out)
    except ValueError as bad:
        raise Broken(f"{command} printed no JSON ({shown(out)}: {bad}){fix}") from bad
    if not isinstance(reply, list):
        raise Broken(f"{command} printed a JSON {type(reply).__name__}, not a list{fix}")
    entries: list[dict[str, object]] = []
    for entry in reply:
        if not isinstance(entry, dict):
            raise Broken(f"{command} lists an entry that is no object ({shown(entry)}){fix}")
        entries.append(entry)
    return entries


def command_of(argv: list[str]) -> str:
    """A documented `--json` command as a message names it."""
    return f"`claude {' '.join(argv)}`"


def text_of(entry: dict[str, object], field: str, what: str, source: str, note: Note, reader: str) -> str:
    """A field of an entry of a reply that must be a string and not empty, or a Broken whose fix names
    `reader`, the function that asked for the field and so knows what the platform writes. `source` names
    the reply as a message does: `command_of` of a list command, or the session's init event."""
    value = entry.get(field)
    if not isinstance(value, str) or not value:
        found = shown(value) if field in entry else "absent"
        raise Broken(
            f"{source} gives no {field} string for {what} ({field} is {found})"
            + platform_fix(note, SCRIPT, reader, "a reply")
        )
    return value


MARKETPLACES = ["plugin", "marketplace", "list", "--json"]
PLUGINS = ["plugin", "list", "--json"]


def platform_clone(state: Run) -> Path:
    """The platform's clone of the kit's marketplace, the `installLocation` of the one entry of
    `claude plugin marketplace list --json` named as the kit's marketplace. The entry is a finding
    (Misfit) when there is none, when its `source` is not `github` or its `repo` not the source's
    repository; two entries of the name, an entry of any name whose `name` is no string or is empty (an entry
    of another marketplace needs its `name` too, to be known as another), a `source`, an `installLocation`
    or, on a `github` entry, a `repo` that is no string or is empty, an `installLocation` that names no
    existing folder and any wrong shape of the reply are a Broken, the platform's reply being at fault and
    not the guide."""
    entries = listed(MARKETPLACES, state.cwd, state.env, state.note)
    names = [
        text_of(e, "name", f"the list's entry {n}", command_of(MARKETPLACES), state.note, "platform_clone")
        for n, e in enumerate(entries, 1)
    ]
    own = [e for e, name in zip(entries, names, strict=True) if name == state.marketplace]
    if not own:
        raise Misfit(
            f"the configuration knows no marketplace {state.marketplace}",
            "make the block register the kit's repository, `claude plugin marketplace add <owner>/<repo>`",
        )
    if len(own) > 1:
        raise Broken(
            f"`claude {' '.join(MARKETPLACES)}` lists {len(own)} entries named {state.marketplace}"
            + platform_fix(state.note, SCRIPT, "platform_clone", "a reply")
        )
    entry = own[0]

    def field(name: str) -> str:
        return text_of(entry, name, state.marketplace, command_of(MARKETPLACES), state.note, "platform_clone")

    source, location = field("source"), field("installLocation")
    if source != "github":
        raise Misfit(f"the marketplace is registered from a {source} source, not from GitHub", IN_PLACE)
    repo = field("repo")
    wanted = state.source.split("#")[0]
    if repo != wanted:
        raise Misfit(
            f"the marketplace is registered from {repo}, not from {wanted}",
            f"make the block register the source it is given, {FROM_ENV} or the clone's origin, "
            "and nothing after it",
        )
    if not Path(location).is_dir():
        raise Broken(
            f"`claude {' '.join(MARKETPLACES)}` names an installLocation that is no folder ({location})"
            + platform_fix(state.note, SCRIPT, "platform_clone", "a reply")
        )
    return Path(location)


def project_entries(state: Run, project: Path) -> dict[str, list[dict[str, str]]]:
    """For each module of the kit, the entries of `claude plugin list --json`, run in the project, whose
    `id` is the module's and whose `projectPath` is the project (as given or resolved), at any scope: the
    user-scope entry of the id, which has no `projectPath`, and the entry of another project are none of
    them. Each is read whole, `installPath`, `version` and `scope` strings, and a project- or local-scope
    entry a `projectPath` string too; a fault of shape in an entry of a module's id, an entry of any id whose
    `id` is no string or is empty (an entry of another plugin needs its `id` too, to be known as another),
    and two project-scope entries of one id for the project, are a Broken, whatever else the list holds."""
    here = {str(project), str(project.resolve())}
    found: dict[str, list[dict[str, str]]] = {module: [] for module in state.modules}
    for position, entry in enumerate(listed(PLUGINS, project, state.env, state.note), 1):
        nth = f"the list's entry {position}"
        identity = text_of(entry, "id", nth, command_of(PLUGINS), state.note, "project_entries")
        for module in state.modules:
            key = state.key(module)
            if identity != key:
                continue
            fields = {
                f: text_of(entry, f, key, command_of(PLUGINS), state.note, "project_entries")
                for f in ("installPath", "version", "scope")
            }
            if fields["scope"] in ("project", "local"):
                where = text_of(
                    entry,
                    "projectPath",
                    f"{key} at scope {fields['scope']}",
                    command_of(PLUGINS),
                    state.note,
                    "project_entries",
                )
            else:
                where = str(entry.get("projectPath", ""))
            if where in here:
                found[module].append(fields)
    for module, own in found.items():
        at_project = sum(e["scope"] == "project" for e in own)
        if at_project > 1:
            raise Broken(
                f"`claude {' '.join(PLUGINS)}` lists {at_project} project-scope entries of "
                f"{state.key(module)} for the project"
                + platform_fix(state.note, SCRIPT, "project_entries", "a reply")
            )
    return found


INIT_EVENT = "the headless session's `system/init` event"


def init_paths(event: dict[str, object], note: Note) -> dict[str, str]:
    """Each plugin's path by its name, from the `plugins` of the `system/init` event as the headless page
    documents it: an array of objects, each with a `name` and a `path`. The event is a platform reply, and a
    fault in it is a Broken, never an answer for the guide: a `plugins` that is absent or no list, an entry
    that is no object, a `name` or `path` that is absent, no string or empty, and two entries of one name,
    whatever their paths. An entry that is no module of the kit, a built-in plugin with a path that is no
    folder among them, is an entry like the others; the caller finds a module that is not listed. The fix
    of each Broken names `session_paths`, which asks for the event and so knows what the platform writes."""
    plugins = event.get("plugins")
    if not isinstance(plugins, list):
        found = shown(plugins) if "plugins" in event else "absent"
        raise Broken(
            f"{INIT_EVENT} gives no plugins list (plugins is {found})"
            + platform_fix(note, SCRIPT, "session_paths", "a reply")
        )
    names: list[str] = []
    paths: dict[str, str] = {}
    for n, plugin in enumerate(plugins, 1):
        if not isinstance(plugin, dict):
            raise Broken(
                f"{INIT_EVENT} gives plugins entry {n} that is no object ({shown(plugin)})"
                + platform_fix(note, SCRIPT, "session_paths", "a reply")
            )
        what = f"plugins entry {n}"
        name = text_of(plugin, "name", what, INIT_EVENT, note, "session_paths")
        names.append(name)
        paths[name] = text_of(plugin, "path", what, INIT_EVENT, note, "session_paths")
    for name in names:
        if names.count(name) > 1:
            at = [str(n) for n, other in enumerate(names, 1) if other == name]
            both = "both" if len(at) == 2 else "all"
            raise Broken(
                f"{INIT_EVENT} gives plugins entries {', '.join(at[:-1])} and {at[-1]} {both} named"
                f" {shown(name)}" + platform_fix(note, SCRIPT, "session_paths", "a reply")
            )
    return paths


def session_paths(state: Run, project: Path) -> tuple[dict[str, str] | None, str]:
    """Each plugin's path as a headless session in the project reports it at start, the project trusted
    in the configuration first — None when the session reported no start, the first `system/init` event
    being the one read, as the headless page documents one at the start of the stream — and its last line.
    An event of another shape than the page documents is a Broken (`init_paths`)."""
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
            return init_paths(event, state.note), ""
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


def claim_marketplace(state: Run) -> str:
    """What fails of the claim that the platform's clone of the marketplace matches the kit's."""
    clone = platform_clone(state)
    mend = (
        "bring the source branch to the kit's clone — merge main into it and push — or point "
        f"{FROM_ENV} at the branch the clone holds"
    )
    try:
        market = modules_of(clone)
    except Broken as bad:
        said = str(bad).split(" — fix:")[0]
        raise Misfit(f"the platform's clone of the marketplace cannot be read ({said})", mend) from bad
    if market != state.modules:
        raise Misfit(f"the marketplace holds {market}, the kit's clone {state.modules}", mend)
    state.clone = clone
    return ""


def cached_copies(state: Run, project: Path) -> tuple[dict[str, Path], str]:
    """The plugin-cache copy of each module, and what fails of the claim that each is installed."""
    mine, on = project_entries(state, project), enabled(project, state.note)
    copies: dict[str, Path] = {}
    for module in state.modules:
        own = [e for e in mine[module] if e["scope"] == "project"]
        if not own:
            return copies, f"{module} is not installed for the project"
        if own[0]["version"] != state.modules[module]:
            return copies, f"{module} is installed at {own[0]['version']}, not {state.modules[module]}"
        listed_at, copies[module] = own[0]["installPath"], state.cached(module)
        if Path(listed_at).resolve() != copies[module].resolve():
            raise Misfit(
                f"{module} is not in the plugin cache at {copies[module]} but at {listed_at}",
                cache_fix(state.note),
            )
        if not copies[module].is_dir():
            return copies, f"{module} is not in the plugin cache at {copies[module]}"
        if state.key(module) not in on:
            return copies, f"{module} is not enabled in the project's .claude/settings.json"
    return copies, ""


def claim_alike(state: Run, copies: dict[str, Path]) -> str:
    """What fails of the claim that each cached module is alike in the marketplace."""
    clone = state.clone or platform_clone(state)
    for module in state.modules:
        odd = differing(copies[module], clone / "modules" / module)
        if odd:
            return f"{module}'s {odd} is not alike in the cache and the marketplace"
    return ""


def claim_loaded(state: Run, project: Path, copies: dict[str, Path]) -> str:
    """What fails of the claim that a session in the project loads each module from the plugin cache."""
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
        if Path(where).resolve() != copies[module].resolve():
            raise Misfit(f"a session runs {module} from {where}, not from the plugin cache", IN_PLACE)
    return ""


def claim_installed(state: Run, project: Path, name: str) -> str:
    """What fails of the claim of an install, a reinstall or an update."""
    copies, odd = cached_copies(state, project)
    if odd:
        return odd
    if name == "reinstall":
        return claim_alike(state, copies)
    if name == "install":
        return claim_loaded(state, project, copies)
    return ""


def claim_kernel(state: Run, project: Path) -> str:
    """What fails of the claim that the kernel and the license files stand in the project's docs."""
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


def claim_commit(state: Run, project: Path) -> str:
    """What fails of the claim that the project's working tree is clean after the commit."""
    code, said = run(["git", "status", "--porcelain"], project, state.env, joined=False)
    return "" if code == 0 and not said else "the project's working tree is not clean after the commit"


def claim_uninstall(state: Run, project: Path) -> str:
    """What fails of the claim that no module is left installed for the project."""
    mine, on = project_entries(state, project), enabled(project, state.note)
    left = sorted(state.key(m) for m in state.modules if mine[m] or state.key(m) in on)
    return f"{', '.join(left)} still installed for the project" if left else ""


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
        return claim_marketplace(state)
    if name in ("install", "reinstall", "update"):
        return claim_installed(state, project, name)
    if name == "kernel":
        return claim_kernel(state, project)
    if name == "commit":
        return claim_commit(state, project)
    if name == "uninstall":
        return claim_uninstall(state, project)
    return ""


PLACE_ENV_NAMED = f"{', '.join(PLUGIN_PLACE_ENV[:-1])} and {PLUGIN_PLACE_ENV[-1]}"  # the four, in order
CACHE_FIX = (
    "make the block install each module from the marketplace, `claude plugin install "
    f"<module>@<marketplace> --scope project`, and set none of {PLACE_ENV_NAMED} in a block: the platform "
    "copies the module to <plugins root>/cache/<marketplace>/<module>/<version>, where Claude Code's "
    "loading page documents it; if it now copies elsewhere, correct `Run.cached` of the check"
)


def cache_fix(note: Note) -> str:
    """The fix of a module listed outside the plugin cache, by the state `note` records. On the pinned
    version, `CACHE_FIX`: the block, or the check's reader of that version's layout. Off the pin the reader
    is the pinned version's, not this one's, so the fix is the run on the pinned version, put first on PATH
    as `put_first` words it."""
    if note.found:
        return (
            f"this run is on {note.found}, not the pinned {note.pinned}: run the check again on the pinned"
            f" version, {put_first(note.pinned)}"
        )
    return CACHE_FIX


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


def claude_noted(kit: Path, env: dict[str, str]) -> Note:
    """The note for a run on another Claude Code than the kit pins, empty on the pinned one, from
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
        found, examined = run_blocks(named, kit, base_env, source, note)
    except Broken as bad:
        bad.note = note
        raise
    except OSError as bad:  # the note ends this BROKEN line too, so it is made here and not in main
        unreadable = Broken(unreadable_said(bad))
        unreadable.note = note
        raise unreadable from bad
    return found, examined, note


def home_env(home: Path, base_env: dict[str, str]) -> dict[str, str]:
    """The run's home folder made, with git's identity in its global configuration and the outer
    credential settings carried, and the environment of the run: none of the four variables, the plugins
    root being <config>/plugins."""
    config = home / ".claude"
    config.mkdir(parents=True)
    (home / ".gitconfig").write_text(
        "[user]\n\tname = install-guide\n\temail = install-guide@example.invalid\n"
        "[init]\n\tdefaultBranch = main\n[commit]\n\tgpgsign = false\n",
        encoding="utf-8",
    )
    carry_credentials(base_env, home / ".gitconfig")
    return claude_env(base_env) | {
        "HOME": str(home),
        "CLAUDE_CONFIG_DIR": str(config),
        "GIT_CONFIG_GLOBAL": str(home / ".gitconfig"),
        "DISABLE_AUTOUPDATER": "1",
    }


def cloned_kit(kit: Path, home: Path, env: dict[str, str]) -> Path:
    """The kit cloned from its working folder's HEAD into the run's home, the clone's path."""
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
    return clone


def prepared_run(scratch: Path, kit: Path, base_env: dict[str, str], source: str, note: Note) -> Run:
    """The state of a run over a home folder and a clone of the kit made under `scratch`."""
    home = scratch / "home"
    env = home_env(home, base_env)
    clone = cloned_kit(kit, home, env)
    try:
        marketplace = marketplace_name(clone)
    except DocumentError as bad:
        raise Broken(str(bad)) from bad
    return Run(home, clone, home / ".claude", env, modules_of(clone), home, source, marketplace, note)


def dials_refusal(block: Block, state: Run, ran: int) -> tuple[list[Finding], str] | None:
    """The dials example written into the project; None, or the finding and the count when no project exists
    yet."""
    if state.project is None:
        finding = Finding(
            block.line,
            "the dials example comes before the project exists",
            fix_for("dials", state.marketplace),
        )
        return [finding], f"{ran} block(s) run"
    fixture(state.project, block.text)
    return None


def run_block(block: Block, state: Run, scratch: Path, source: str) -> tuple[int, str, Path]:
    """One block sourced by a fresh `bash -eu` in the folder the block before it ended in: its exit, its
    output and the file that holds the folder this one ended in."""
    text = block.text
    if block.name == "marketplace":
        text = ADD.sub(lambda m: m.group(1) + source, text, count=1)
    script = scratch / f"{block.name}.sh"
    where = scratch / f"{block.name}.cwd"
    body = scratch / f"{block.name}.block.sh"
    body.write_text(text, encoding="utf-8")
    script.write_text(f'. "{body}"\npwd > "{where}"\n', encoding="utf-8")
    code, said = run(["bash", "-eu", str(script)], state.cwd, state.env)
    return code, said, where


def after_block(block: Block, state: Run, code: int, said: str) -> Finding | None:
    """The finding a block that ran gives: its exit, else what its claim finds."""
    if code != 0:
        what = f"the block named check={block.name} exited {code} — {last_line(said)}"
        return Finding(block.line, what, fix_for(block.name, state.marketplace))
    try:
        failed, fix = claim(state, block.name), fix_for(block.name, state.marketplace)
    except Misfit as misfit:
        failed, fix = misfit.what, misfit.fix
    return Finding(block.line, f"after check={block.name}: {failed}", fix) if failed else None


def run_blocks(
    named: list[Block], kit: Path, base_env: dict[str, str], source: str, note: Note
) -> tuple[list[Finding], str]:
    """The named blocks run in the guide's order in a home folder of their own, and what was examined."""
    with tempfile.TemporaryDirectory(prefix="install-guide-") as scratch:
        state = prepared_run(Path(scratch), kit, base_env, source, note)
        ran = 0
        try:
            for block in named:
                if block.name == "dials":
                    refused = dials_refusal(block, state, ran)
                    if refused:
                        return refused
                    continue
                code, said, where = run_block(block, state, Path(scratch), source)
                ran += 1
                if where.is_file():
                    state.cwd = Path(where.read_text(encoding="utf-8").strip())
                found = after_block(block, state, code, said)
                if found:
                    return [found], f"{ran} block(s) run"
        except Broken as bad:  # a failure of the loop or of a claim: the count is what ran before it
            bad.ran = ran
            raise
        except OSError as bad:  # the same, a file the loop could not read or write: one Broken, one count
            unreadable = Broken(unreadable_said(bad))
            unreadable.ran = ran
            raise unreadable from bad
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
to a file (FAKE_LOG, else the configuration folder's). It keeps its own state, the marketplaces added and
the plugins installed, in the configuration folder's fake-state.json, its clone of a marketplace under
fake-clone/ and its copies of the plugins where the platform puts them, cache/<marketplace>/<plugin>/<version>
under the plugins root (CLAUDE_CODE_PLUGIN_CACHE_DIR, else plugins/ in the configuration folder), and answers
`plugin marketplace list --json` and `plugin list --json` from that state, or with the text of the file
FAKE_MKT or FAKE_LIST names, and the exit FAKE_MKT_EXIT or FAKE_LIST_EXIT; the two list commands write
FAKE_STDERR, when set, to standard error and append `<which>|<the folder they run in>` to the file
FAKE_CWD names, when set. A marketplace added
from `<owner>/<repo>#<branch>` is a GitHub one, cloned from the toy kit the environment names; one added
from a path is a local folder. `--version` answers the pin of the toy kit, as the real one writes it, or
FAKE_SAYS (escapes read) with the exit FAKE_EXIT; for `--version` it logs to FAKE_ENV, when set, its
configuration folder, its auto-updater setting, how many entries the folder holds and whether it is a
folder. For every command it logs to FAKE_CACHE, when set, the arguments, then, each after a `|` and in this
order, the values of CLAUDE_CODE_PLUGIN_CACHE_DIR, CLAUDE_CODE_PLUGIN_SEED_DIR, CLAUDE_CODE_PLUGIN_DIRS,
CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE, CLAUDE_CODE_PLUGIN_PREFER_HTTPS, FAKE_KEEP,
CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS, CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE,
CLAUDE_CODE_SYNC_PLUGIN_INSTALL, CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS, FORCE_AUTOUPDATE_PLUGINS,
CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL and CLAUDE_CODE_PLUGIN_DIR_WATCH it holds, `absent` when
unset.
FAKE_MUTANT names the one thing it does wrong."""
import json, os, shutil, subprocess, sys
from pathlib import Path
mutant = os.environ.get("FAKE_MUTANT", "")
config = Path(os.environ["CLAUDE_CONFIG_DIR"])
with open(os.environ.get("FAKE_LOG") or config / "fake.log", "a", encoding="utf-8") as log:
    log.write(" ".join(sys.argv[1:]) + "\\n")
if os.environ.get("FAKE_CACHE"):
    with open(os.environ["FAKE_CACHE"], "a", encoding="utf-8") as seen:
        held = [os.environ.get(name, "absent") for name in (
            "CLAUDE_CODE_PLUGIN_CACHE_DIR", "CLAUDE_CODE_PLUGIN_SEED_DIR", "CLAUDE_CODE_PLUGIN_DIRS",
            "CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE", "CLAUDE_CODE_PLUGIN_PREFER_HTTPS", "FAKE_KEEP",
            "CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS", "CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE",
            "CLAUDE_CODE_SYNC_PLUGIN_INSTALL", "CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS",
            "FORCE_AUTOUPDATE_PLUGINS", "CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL",
            "CLAUDE_CODE_PLUGIN_DIR_WATCH",
        )]
        seen.write(" ".join(sys.argv[1:]) + "|" + "|".join(held) + "\\n")
if sys.argv[1:] == ["--version"]:
    if os.environ.get("FAKE_ENV"):
        with open(os.environ["FAKE_ENV"], "a", encoding="utf-8") as seen:
            seen.write("|".join([
                str(config), os.environ.get("DISABLE_AUTOUPDATER", ""), str(len(os.listdir(config))),
                "dir" if config.is_dir() else "",
            ]) + "\\n")
    pin = (Path(os.environ["FAKE_SOURCE"]) / "scripts" / "claude-code.version").read_text().strip()
    said = os.environ.get("FAKE_SAYS")
    sys.stdout.write(pin + " (Claude Code)\\n" if said is None else said.encode().decode("unicode_escape"))
    sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
name = json.loads(
    (Path(os.environ["FAKE_SOURCE"]) / ".claude-plugin" / "marketplace.json").read_text()
)["name"]
clone = config / "fake-clone" / name
plugins = Path(os.environ.get("CLAUDE_CODE_PLUGIN_CACHE_DIR") or config / "plugins")
copies = plugins / "cache" / name
store = config / "fake-state.json"
settings = Path.cwd() / ".claude" / "settings.json"
def load(path):
    return json.loads(path.read_text()) if path.is_file() else {}
def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
def state():
    return {"marketplaces": [], "plugins": []} | load(store)
def cache_of(module):
    manifest = clone / "modules" / module / ".claude-plugin" / "plugin.json"
    return copies / module / json.loads(manifest.read_text())["version"]
def reply(variable):
    if variable in os.environ:
        sys.stdout.write(Path(os.environ[variable]).read_text())
        sys.exit(int(os.environ.get(variable + "_EXIT", "0")))
def fail():
    print("boom", file=sys.stderr)
    sys.exit(1)
def listing(which):
    if os.environ.get("FAKE_CWD"):
        with open(os.environ["FAKE_CWD"], "a", encoding="utf-8") as seen:
            seen.write(which + "|" + str(Path.cwd()) + "\\n")
    if os.environ.get("FAKE_STDERR"):
        print(os.environ["FAKE_STDERR"], file=sys.stderr)
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
    subprocess.run(["git", "clone", "--quiet", os.environ["FAKE_SOURCE"], str(clone)], check=True)
    if mutant == "marketplace-fewer-modules":
        shutil.rmtree(clone / "modules" / "const-beta")
    if mutant == "marketplace-unreadable":
        (clone / "modules" / "const-beta" / "MODULE.md").unlink()
    data = state()
    data["marketplaces"] = [{"name": name} | source | {"installLocation": str(clone)}]
    save(store, data)
elif args[:3] == ["plugin", "marketplace", "update"]:
    pass
elif args == ["plugin", "marketplace", "list", "--json"]:
    listing("marketplace")
    reply("FAKE_MKT")
    entries = state()["marketplaces"]
    if mutant == "mkt-exit-1":
        fail()
    if mutant == "mkt-not-json":
        print("marketplaces: none")
        sys.exit(0)
    if entries:
        first = entries[0]
        if mutant == "mkt-no-installLocation":
            first.pop("installLocation")
        if mutant == "mkt-installLocation-number":
            first["installLocation"] = 7
        if mutant == "mkt-clone-gone":
            first["installLocation"] += "-gone"
        if mutant == "mkt-title-for-name":
            first["title"] = first.pop("name")
        if mutant == "mkt-no-source":
            first.pop("source")
        if mutant == "mkt-no-repo":
            first.pop("repo")
        if mutant == "mkt-source-number":
            first["source"] = 7
    other = {"name": "other-mp", "source": "github", "repo": "other/kit", "installLocation": "/nowhere/o"}
    if mutant == "mkt-two":
        entries = entries + entries
    if mutant == "mkt-other-first":
        entries = [other, *entries]
    if mutant == "mkt-other-last":
        entries = [*entries, other]
    if mutant == "mkt-entry-not-object":
        entries = ["x", *entries]
    print(json.dumps({"marketplaces": entries} if mutant == "mkt-not-list" else entries))
elif args == ["plugin", "list", "--json"]:
    listing("plugins")
    reply("FAKE_LIST")
    entries = state()["plugins"]
    if mutant == "list-exit-1":
        fail()
    if mutant == "list-not-json":
        print("no plugins yet")
        sys.exit(0)
    modules = sorted(p.name for p in (clone / "modules").iterdir()) if (clone / "modules").is_dir() else []
    elsewhere = [
        {"id": f"{m}@{name}", "version": "9.9.9", "scope": "user", "installPath": "/nowhere/" + m}
        for m in modules
    ]
    if mutant.startswith("list-other-project"):
        elsewhere = [
            e | {"scope": "project", "projectPath": "/elsewhere/project"} for e in elsewhere
        ]
    for entry in entries:
        if mutant == "list-wrong-version":
            entry["version"] = "9.9.9"
        for gone in ("projectPath", "installPath", "version", "scope", "id"):
            if mutant == "list-without-" + gone:
                entry.pop(gone)
    if mutant in ("list-user-first", "list-other-project-first"):
        entries = [*elsewhere, *entries]
    if mutant in ("list-user-last", "list-other-project-last"):
        entries = [*entries, *elsewhere]
    if mutant == "list-two-for-project":
        entries = [*entries, *entries]
    if mutant == "list-entry-not-object":
        entries = ["x", *entries]
    print(json.dumps({"plugins": entries} if mutant == "list-not-list" else entries))
elif args[:2] == ["plugin", "install"] or args[:2] == ["plugin", "update"]:
    module = args[2].split("@")[0]
    if args[1] == "update":
        if mutant == "update-drops":
            shutil.rmtree(cache_of(module), ignore_errors=True)
        if mutant == "settings-corrupt-on-update":
            settings.write_text("not json")
        print("already at the latest version")
        sys.exit(0)
    cache = cache_of(module)
    if cache.exists():
        shutil.rmtree(cache)
    shutil.copytree(clone / "modules" / module, cache)
    if mutant == "reinstall-stale" and (config / "fake.reinstall").exists():
        (cache / "stale.txt").write_text("an old copy\\n")
    if mutant == "reinstall-lacks" and (config / "fake.reinstall").exists():
        (cache / "MODULE.md").unlink()
    entry = {
        "id": args[2], "version": cache.name, "scope": "project", "enabled": True,
        "installPath": str(cache), "projectPath": str(Path.cwd()),
    }
    if os.environ.get("CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE") == "1":  # the platform lists a zip file then
        entry["installPath"] = str(cache) + ".zip"
    if mutant == "install-at-user-scope":
        entry = {k: v for k, v in entry.items() if k != "projectPath"} | {"scope": "user"}
    if mutant == "install-for-other-project":
        entry["projectPath"] = "/elsewhere/project"
    if mutant == "install-in-place":
        entry["installPath"] = str(clone / "modules" / module)
    if mutant == "install-other-version":
        entry["installPath"] = str(copies / module / "0.0.0")
        Path(entry["installPath"]).mkdir(parents=True, exist_ok=True)
    data = state()
    data["plugins"] = [e for e in data["plugins"] if e["id"] != args[2]]
    if mutant != "install-not-listed":
        data["plugins"].append(entry)
    save(store, data)
    if mutant != "install-no-enable":
        data = load(settings)
        data.setdefault("enabledPlugins", {})[args[2]] = True
        save(settings, data)
elif args[:2] == ["plugin", "uninstall"]:
    (config / "fake.reinstall").write_text("")
    module = args[2].split("@")[0]
    if mutant not in ("uninstall-keeps", "uninstall-keeps-installed"):
        data = state()
        data["plugins"] = [e for e in data["plugins"] if e["id"] != args[2]]
        save(store, data)
        shutil.rmtree(copies / module, ignore_errors=True)
    if mutant.startswith("uninstall-leaves-"):
        data = state()
        data["plugins"].append({
            "id": args[2], "version": "0.0.1", "scope": mutant.removeprefix("uninstall-leaves-"),
            "enabled": True, "installPath": "/nowhere/" + module, "projectPath": str(Path.cwd()),
        })
        save(store, data)
    if mutant not in ("uninstall-keeps", "uninstall-keeps-enabled"):
        data = load(settings)
        data.get("enabledPlugins", {}).pop(args[2], None)
        save(settings, data)
elif args[:1] == ["-p"] and mutant == "session-no-start":
    print("Error: the session could not start", file=sys.stderr)
    sys.exit(1)
elif args[:1] == ["-p"]:
    trusted = load(config / ".claude.json").get("projects", {}).get(str(Path.cwd()), {})
    found = []
    if trusted.get("hasTrustDialogAccepted"):
        for key, on in load(settings).get("enabledPlugins", {}).items():
            module = key.split("@")[0]
            where = clone / "modules" / module if mutant == "session-in-place" else cache_of(module)
            if on and mutant != "session-loads-nothing":
                found.append({"name": module, "path": str(where), "source": key})
    event = {"type": "system", "subtype": "init", "plugins": found}
    builtin = {"name": "agents-md", "path": "builtin", "source": "agents-md@builtin"}
    if mutant == "session-builtin":
        found.insert(0, builtin)
    if mutant == "session-builtin-only":
        found[:] = [builtin]
    if mutant == "session-plugins-absent":
        del event["plugins"]
    if mutant == "session-plugins-null":
        event["plugins"] = None
    if mutant == "session-plugins-object":
        event["plugins"] = {"name": "const-alpha"}
    if mutant == "session-plugins-string":
        event["plugins"] = "const-alpha"
    if mutant == "session-entry-string":
        found.insert(1, "const-beta")
    if mutant.startswith("session-name-"):
        if mutant == "session-name-absent":
            del found[0]["name"]
        else:
            found[0]["name"] = "" if mutant == "session-name-empty" else 7
    if mutant.startswith("session-path-"):
        if mutant == "session-path-absent":
            del found[1]["path"]
        else:
            found[1]["path"] = "" if mutant == "session-path-empty" else 7
    if mutant == "session-dup-same":
        found.append(dict(found[0]))
    if mutant == "session-dup-diff":
        found.append(dict(found[0]) | {"path": "/elsewhere/" + found[0]["name"]})
    if mutant == "session-dup-three":
        found[:] = [found[0], found[1], dict(found[0]), dict(found[0]) | {"path": "/elsewhere"}]
    if mutant == "session-dup-newline":
        found[:] = [found[0] | {"name": "a\\nb"}, found[1] | {"name": "a\\nb"}]
    print("a line that is no JSON")  # skipped, as an event of another type is
    print(json.dumps({"type": "system", "subtype": "hook_started", "plugins": None}))
    print(json.dumps(event))
    if mutant == "session-second-init-malformed":  # a later init event is never read
        print(json.dumps(event | {"plugins": None}))
    if mutant == "session-second-init-paths":
        print(json.dumps(event | {"plugins": [p | {"path": "/elsewhere/" + p["name"]} for p in found]}))
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


def without(entry: dict[str, object], *fields: str) -> dict[str, object]:
    """The entry of a reply with `fields` left out."""
    return {k: v for k, v in entry.items() if k not in fields}


def whats(findings: list[Finding]) -> str:
    """What each finding says, joined, or "no finding"."""
    return " | ".join(f.what for f in findings) or "no finding"


def fix_of(reader: str, wrote: str = "a reply") -> str:
    """The fix of a reply the kit's reader `reader` does not read; typed by hand, since a message
    function cannot check itself."""
    return (
        f" — fix: Claude Code 2.1.282 wrote {wrote} that the kit's reader, `{reader}` in"
        " scripts/check-install-guide.py, does not read: update that reader to what 2.1.282 writes"
    )


def broken_said(kit: Path) -> str:
    """What `modules_of` says over a kit folder when it is Broken, or "no Broken"."""
    try:
        modules_of(kit)
    except Broken as broken:
        return str(broken)
    except TypeError as crash:  # a traceback is a case that fails, not the run
        return f"{type(crash).__name__}: {crash}"
    return "no Broken"


@dataclass(frozen=True)
class Texts:
    """The notes and lines the groups of cases type by hand and share, built once: a message function
    cannot check itself, so none is taken from the check."""

    pin_note: Note  # the state of a run on the pin: the note empty
    other_note: Note  # the state of a run on 2.1.286 with the opt-out set
    off_fix: str  # the run is on 2.1.286, not the pinned 2.1.282
    pin_fix: str
    settings_fix: str
    off_what: str
    put_first: str
    cache_fix: str
    off_cache_fix: str  # off the pin: the run on the pinned version, not a reader to correct
    strict: str
    noted: str
    reinstall: str
    too_old: str
    seen_when_removed: str  # the fake's log after a command's arguments
    mkt_command: str
    listed_command: str
    no_json: str
    list_where: str
    alpha_pick: str
    beta_pick: str

    def stuck(self, what: str) -> str:
        """The BROKEN line of a `claude --version` that `what` describes."""
        return f"BROKEN: `claude --version` {what}{self.reinstall}"

    def stop_after(self, blocks: int) -> str:
        """The could-not-run line of a failure after `blocks` blocks ran."""
        return f"BROKEN: the check could not run — {blocks} block(s) run"  # typed by hand

    def picks(self, alpha: str = "", beta: str = "") -> str:
        """What `plugins_said` gives over the entries picked for the two toy modules."""
        return f"const-alpha={alpha}; const-beta={beta}"

    def exited_fix(self, command: str) -> str:
        """The fix of a list command that wrote no reply."""  # typed by hand
        return f" — fix: run `{command}` in {self.list_where}, read why it fails, then run the check again"

    def silent_fix(self, raw: str, code: int, on_pin: bool) -> str:
        """The command's own fix of the list command `raw` that exited `code` and wrote no reply, or timed
        out (124), on the pin or off it."""
        if code == 124:
            if on_pin:
                return " — fix: run the check again"
            return f" — fix: {self.off_what}: run the check again on the pinned version, {self.put_first}"
        read = f" — fix: run `{raw}` in {self.list_where}, read why it fails"
        if on_pin:
            return read + ", then run the check again"
        return (
            read + f"; {self.off_what}, so then run the check again on the pinned version, {self.put_first}"
        )

    def reply_fix(self, rest: str, reader: str) -> str:
        """The fix a BROKEN line ends with, by the function that reads: `reader`, which is
        `platform_clone` or `project_entries`, for what it asks of an entry or finds in the list (two
        entries of a name, a field that is no string, an installLocation that is no folder), and
        `listed` for the rest, as `rest` says what was found; a command that exited other than 0 wrote
        no reply, and has the command's own fix."""
        if re.search(r"\bexited \d+ \(", rest):
            return self.exited_fix(
                "claude plugin marketplace list --json"
                if reader == "platform_clone"
                else "claude plugin list --json"
            )
        asked = (
            "entries named",
            "project-scope entries",
            "gives no ",
            "installLocation that is no folder",
        )
        return fix_of(reader if any(word in rest for word in asked) else "listed")


def typed_texts() -> Texts:
    """The notes and lines typed by hand, made once for every group of cases."""
    off_what = "this run is on 2.1.286, not the pinned 2.1.282"
    put_first = (
        "put Claude Code 2.1.282 first on PATH for this run: either run sh scripts/setup-claude.sh in the"
        " kit's clone, then the check through sh scripts/gate-list.sh --run install-<module> (--run guide"
        " for the guide's check), which puts it first, or install it beside your own by hand (npm install"
        " --prefix <folder> @anthropic-ai/claude-code@2.1.282,"
        " then PATH=<folder>/node_modules/.bin:$PATH)"
    )
    return Texts(
        pin_note=Note("2.1.282"),
        other_note=Note("2.1.282", "2.1.286"),
        off_fix=(
            " — fix: this run is on 2.1.286, not the pinned 2.1.282: run it again on the pinned version,"
            " put Claude Code 2.1.282 first on PATH for this run: either run sh scripts/setup-claude.sh"
            " in the kit's clone, then the check through sh scripts/gate-list.sh --run install-<module>"
            " (--run guide for the guide's check), which puts it first, or install it beside your own by"
            " hand (npm install --prefix <folder> @anthropic-ai/claude-code@2.1.282, then"
            " PATH=<folder>/node_modules/.bin:$PATH)"
        ),
        pin_fix=(
            " — fix: write the one version Claude Code's npm package carries, e.g. 2.1.282, as the file's"
            " only line"
        ),  # typed by hand
        settings_fix=fix_of("enabled", "a settings file"),
        off_what=off_what,
        put_first=put_first,
        cache_fix=(
            "make the block install each module from the marketplace, `claude plugin install "
            "<module>@<marketplace> --scope project`, and set none of CLAUDE_CODE_PLUGIN_CACHE_DIR, "
            "CLAUDE_CODE_PLUGIN_SEED_DIR, CLAUDE_CODE_PLUGIN_DIRS and CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE in a "
            "block: the platform copies the module to <plugins root>/cache/<marketplace>/<module>/<version>, "
            "where Claude Code's loading page documents it; if it now copies elsewhere, correct `Run.cached` "
            "of the check"
        ),
        off_cache_fix=f"{off_what}: run the check again on the pinned version, {put_first}",
        strict=(
            "claude is {0}, and the kit's install checks read the platform as 2.1.282 writes it"
            " (scripts/claude-code.version) — fix: put Claude Code 2.1.282 first on PATH for this run:"
            " either run sh scripts/setup-claude.sh in the kit's clone, then the check through"
            " sh scripts/gate-list.sh --run install-<module> (--run guide for the guide's check), which puts"
            " it first, or install it beside your own by hand (npm install --prefix <folder>"
            " @anthropic-ai/claude-code@2.1.282, then PATH=<folder>/node_modules/.bin:$PATH), or set"
            " CONSTITUTION_KIT_ANY_CLAUDE=1 to run on"
            " {0} with a note on every headline line"
        ),
        noted=" [claude {0}, not the pinned 2.1.282: CONSTITUTION_KIT_ANY_CLAUDE=1]",
        reinstall=(
            " — fix: check that `claude` on PATH is Claude Code (`command -v claude`), and reinstall it"
        ),
        too_old="2.1.286 (Claude Code)\\n",
        seen_when_removed="|absent|absent|absent|absent|1|1|45000|keep|sync|30000|force|disable|watch",
        mkt_command="`claude plugin marketplace list --json`",
        listed_command="`claude plugin list --json`",
        no_json="Expecting value: line 1 column 1 (char 0)",
        list_where="a folder of your own, CLAUDE_CONFIG_DIR set to an empty folder",
        alpha_pick="project:0.0.1:/copies/const-alpha",
        beta_pick="project:0.0.1:/copies/const-beta",
    )


@dataclass(frozen=True)
class Toy:
    """The toy kit, a nameless one, and the environment the runs over them share."""

    root: Path
    kit: Path
    nameless: Path
    base: dict[str, str]  # the person's environment less the four variables, with the fake claude first
    four: dict[str, str]  # the four variables `claude_env` removes, each as a person who sets it would
    kept_vars: dict[str, str]  # the variables a run keeps, each its own value
    git: dict[str, str]


def toy_run(root: Path) -> Toy:
    """The toy kit and a nameless one under `root`, the fake claude, and the environment of the runs."""
    kit = toy_kit(root)
    fake = root / "bin"
    fake.mkdir()
    (fake / "claude").write_text(FAKE, encoding="utf-8")
    (fake / "claude").chmod(0o755)
    # typed by hand, a constant cannot check itself: the four variables `claude_env` removes, each with
    # what a person who sets it would set, a folder of the run's or `1`; the person's own are never the
    # environment of these runs, nor are the variables it keeps
    four = {
        "CLAUDE_CODE_PLUGIN_CACHE_DIR": "plugins-root",
        "CLAUDE_CODE_PLUGIN_SEED_DIR": "plugins-seed",
        "CLAUDE_CODE_PLUGIN_DIRS": "plugins-dirs",
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
    # the kit's CI's CLAUDE_CODE_PLUGIN_PREFER_HTTPS, an unrelated FAKE_KEEP and the seven: the platform's
    # environment-variables page documents them as tuning a clone's time, transport or retry, an update or
    # a wait, none as steering where plugins are found, kept or loaded
    kept_vars = {"CLAUDE_CODE_PLUGIN_PREFER_HTTPS": "1", "FAKE_KEEP": "1"} | documented_kept
    base = {
        k: v for k, v in os.environ.items() if k not in four and k not in kept_vars
    } | {  # the plugins root is the fake's own
        "PATH": f"{fake}{os.pathsep}{os.environ.get('PATH', '')}",
        FROM_ENV: "toy/kit#main",
        "FAKE_SOURCE": str(kit),
    }
    nameless = toy_kit(root / "nameless", {"plugins": []})
    return Toy(root, kit, nameless, base, four, kept_vars, os.environ | {"GIT_CONFIG_GLOBAL": os.devnull})


@dataclass(frozen=True)
class Listings:
    """The temporary folder of the listing cases, and the numbers of the folders they make in it."""

    folder: Path
    numbers: Iterator[int]

    def next_folder(self, prefix: str) -> Path:
        """The path of the next numbered folder in the temporary folder, not yet made."""
        return self.folder / f"{prefix}-{next(self.numbers)}"


@dataclass(frozen=True)
class Unit:
    """The folder of the readers' cases and the platform's replies, whole sets of them: the fake prints the
    text of a file as `plugin marketplace list --json` or `plugin list --json`, and the readers are held to
    each reply. It holds the places the replies name, and the helpers that print one and read it."""

    toy: Toy
    note: Note
    folder: Path
    platform: Path  # the platform's clone of the marketplace, a folder
    a_file: Path  # a place that exists and is no folder
    gone: Path  # a place that does not exist
    project: Path
    linked: Path
    replies: Iterator[int]

    def state(self, **extra: str) -> Run:
        """The state of a run over the toy kit in this folder, `extra` added to its environment."""
        env = self.toy.base | {
            "CLAUDE_CONFIG_DIR": str(self.folder / "config"),
            "FAKE_LOG": str(self.folder / "fake.log"),
        }
        return Run(
            self.folder,
            self.toy.kit,
            self.folder / "config",
            env | extra,
            modules_of(self.toy.kit),
            self.folder,
            "toy/kit#main",
            TOY_MP,
            self.note,
        )

    def reply_file(self, text: str) -> str:
        """The path of a new file in this folder that holds `text`, for the fake to print."""
        path = self.folder / f"reply-{next(self.replies)}.txt"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def mkt(self, **fields: object) -> dict[str, object]:
        """An entry of the marketplace list for the toy marketplace, `fields` replacing its own."""
        return {
            "name": TOY_MP,
            "source": "github",
            "repo": "toy/kit",
            "installLocation": str(self.platform),
        } | fields

    def plug(self, module: str = "const-alpha", /, **fields: object) -> dict[str, object]:
        """An entry of the plugin list for a toy module installed for the project, `fields` set over it."""
        return {
            "id": f"{module}@{TOY_MP}",
            "version": "0.0.1",
            "scope": "project",
            "enabled": True,
            "installPath": f"/copies/{module}",
            "projectPath": str(self.project),
        } | fields

    @property
    def both(self) -> list[dict[str, object]]:
        """The entries of both toy modules for the project."""
        return [self.plug(), self.plug("const-beta")]

    @property
    def other(self) -> dict[str, object]:
        """An entry of another marketplace."""
        return {"name": "other-mp", "source": "directory", "path": "/p", "installLocation": "/q"}

    @property
    def clone_of(self) -> str:
        """What `mkt_said` gives over a list that names the platform's clone."""
        return f"clone {self.platform}"

    def mkt_said(self, text: str, code: int = 0, **extra: str) -> str:
        """What `platform_clone` says over a marketplace list that prints `text` and exits `code`."""
        state = self.state(FAKE_MKT=self.reply_file(text), FAKE_MKT_EXIT=str(code), **extra)
        try:
            return f"clone {platform_clone(state)}"
        except Misfit as misfit:
            return f"RED {misfit.what}"
        except Broken as bad:
            return f"BROKEN {bad}"

    def plugins_said(self, text: str, code: int = 0, project: Path | None = None, **extra: str) -> str:
        """What `project_entries` picks over a plugin list that prints `text` and exits `code`."""
        state = self.state(FAKE_LIST=self.reply_file(text), FAKE_LIST_EXIT=str(code), **extra)
        try:
            found = project_entries(state, self.project if project is None else project)
        except Broken as bad:
            return f"BROKEN {bad}"
        return "; ".join(
            f"{m}=" + ",".join(f"{e['scope']}:{e['version']}:{e['installPath']}" for e in found[m])
            for m in sorted(found)
        )

    def held_copy(self, module: str) -> Path:
        """The module's copy in the plugin cache of the unit tests' configuration, where claims look."""
        return self.state().cached(module)

    def update_held(
        self,
        entries: list[dict[str, object]],
        config: Path | None = None,
        note: Note | None = None,
        env: dict[str, str] | None = None,
    ) -> str:
        """What the update claim, whose picks the install and the reinstall share, says of a list: its
        finding, `RED` and the finding of a Misfit, with its fix after ` | `, or the empty string; the
        run's configuration folder is `config` when one is given, else the default, its plugins root
        `plugins` in it, `env` is added to the run's environment and `note` is its state."""
        held = self.state(FAKE_LIST=self.reply_file(json.dumps(entries)), **(env or {}))
        if config is not None:
            held.config = config
            held.env = held.env | {"CLAUDE_CONFIG_DIR": str(config)}
        held.project = self.project
        held.note = self.note if note is None else note
        try:
            return claim(held, "update")
        except Misfit as misfit:
            return f"RED {misfit.what} | {misfit.fix}"

    def update_said(
        self,
        entries: list[dict[str, object]],
        config: Path | None = None,
        note: Note | None = None,
        env: dict[str, str] | None = None,
    ) -> str:
        """`update_held` without the fix of a finding."""
        return self.update_held(entries, config, note, env).split(" | ", 1)[0]


def unit_of(toy: Toy, note: Note) -> Unit:
    """The folder of the readers' cases under the toy root, with the places the replies name made."""
    folder = toy.root / "unit"
    (folder / "config").mkdir(parents=True)
    platform = folder / "platform" / "toy-mp"
    platform.mkdir(parents=True)
    a_file = folder / "platform" / "a-file"
    a_file.write_text("not a folder\n", encoding="utf-8")
    project = folder / "project"
    project.mkdir()
    linked = folder / "linked"
    linked.symlink_to(project)
    return Unit(
        toy, note, folder, platform, a_file, folder / "platform" / "gone", project, linked, itertools.count(1)
    )


@dataclass(frozen=True)
class Copies:
    """The folders the reinstall and update claims compare, and the copies the project lists."""

    wanted_clone: Path  # the platform's clone, which the reinstall's comparison reads from the state
    other_clone: Path  # a clone whose modules differ
    listed: list[dict[str, object]]  # the project-scope entries of both toy modules, at their cached copies


def copies_placed(unit: Unit) -> Copies:
    """The clones and the cached copies made in the unit folder, the project's settings enabling both
    modules, and the entries that list the copies."""
    wanted_clone, other_clone = unit.folder / "clone", unit.folder / "other-clone"
    for module in ("const-alpha", "const-beta"):
        for folder, text in (
            (wanted_clone / "modules" / module, "same\n"),
            (unit.held_copy(module), "same\n"),
            (other_clone / "modules" / module, "odd\n"),
        ):
            folder.mkdir(parents=True)
            (folder / "a.txt").write_text(text, encoding="utf-8")
    (unit.project / ".claude").mkdir()
    (unit.project / ".claude" / "settings.json").write_text(
        json.dumps({"enabledPlugins": {f"{m}@{TOY_MP}": True for m in ("const-alpha", "const-beta")}}),
        encoding="utf-8",
    )
    listed = [unit.plug(m, installPath=str(unit.held_copy(m))) for m in ("const-alpha", "const-beta")]
    return Copies(wanted_clone, other_clone, listed)


@dataclass(frozen=True)
class Person:
    """What a person sets of the four variables in their own environment, and the log the fake writes."""

    values: dict[str, tuple[str, str]]  # for each variable, how the value reads in a case name and the value
    seen_log: Path
    folders: tuple[Path, ...]  # the folders the variables name, made empty, to stay so


def person_of(unit: Unit, four: dict[str, str]) -> Person:
    """The folders the four variables name, made empty in the unit folder, and the values a person sets."""
    values: dict[str, tuple[str, str]] = {}
    folders: list[Path] = []
    for variable, shape in four.items():
        if shape != "1":
            (unit.folder / shape).mkdir()
            folders.append(unit.folder / shape)
        values[variable] = (
            ("set to 1", "1") if shape == "1" else ("set to a folder", str(unit.folder / shape))
        )
    return Person(values, unit.folder / "cache-seen.log", tuple(folders))


@dataclass(frozen=True)
class Versions:
    """The runs that ask `claude --version`: the answers the fake gives, and the file it logs them to."""

    toy: Toy
    log: Path

    def says_env(
        self, says: str, exits: int, optout: str | None, source: Path | None = None
    ) -> dict[str, str]:
        """The environment of a run whose `claude --version` says `says` and exits `exits`, the opt-out set
        to `optout` unless that is None."""
        env = {k: v for k, v in self.toy.base.items() if k != "CONSTITUTION_KIT_ANY_CLAUDE"} | {
            "FAKE_SAYS": says,
            "FAKE_EXIT": str(exits),
            "FAKE_LOG": str(self.log),
            "FAKE_SOURCE": str(self.toy.kit if source is None else source),
        }
        if optout is not None:
            env["CONSTITUTION_KIT_ANY_CLAUDE"] = optout
        return env

    def logged(self) -> list[str]:
        """The lines the fake logged for the runs since the log was last cleared."""
        return self.log.read_text(encoding="utf-8").splitlines() if self.log.exists() else []

    def outcome(self, env: dict[str, str]) -> str:
        """What the check does before its clone: the note it goes on with, or its BROKEN line."""
        self.log.unlink(missing_ok=True)
        try:
            return f"note:{claude_noted(self.toy.kit, env)}"
        except Broken as broken:
            return f"BROKEN: {broken}"

    def stopped_run(self, env: dict[str, str], where: Path | None = None) -> tuple[str, str]:
        """What `run_guide` over the toy guide ends in when it is Broken: its line and its note."""
        self.log.unlink(missing_ok=True)
        try:
            run_guide(toy_guide(), self.toy.kit if where is None else where, env)
        except Broken as broken:
            return str(broken), broken.note
        return "no Broken", ""

    def whole_run(self, env: dict[str, str], where: Path | None = None) -> tuple[int, list[str]]:
        """The exit and the lines `main` prints over the toy kit, whose guide is committed."""
        self.log.unlink(missing_ok=True)
        printed_lines = io.StringIO()
        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch.dict(globals(), {"KIT": self.toy.kit if where is None else where}),
            contextlib.redirect_stdout(printed_lines),
        ):
            status = main([])
        return status, printed_lines.getvalue().splitlines()


def outcome_kind(said_outcome: str) -> str:
    """What `Versions.outcome` says, in words for a case name."""
    if said_outcome == "note:":
        return "the run goes on"
    return "the run goes on with the note" if said_outcome.startswith("note:") else "BROKEN"


class SelfTestRun:
    """The self-test's cases, run in groups in order; each group is given the state it works on."""

    def __init__(self) -> None:
        self.failed = 0
        self.total = 0

    def case(self, name: str, ok: bool, got: str) -> None:
        """Print one case's line, and count it; a case that fails prints what it got."""
        self.total += 1
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
        if not ok:
            self.failed += 1
            print(f"        got: {got}")

    def listing_cases(self, texts: Texts) -> None:
        """The cases that read trees made in a temporary folder."""
        with tempfile.TemporaryDirectory(prefix="install-guide-listings-") as folder:
            listings = Listings(Path(folder), itertools.count(1))
            self.module_listing_cases(listings)
            self.marketplace_name_cases(listings)
            self.pin_file_cases(listings, texts)
            self.settings_file_cases(listings, texts)

    def guide_run_cases(self, texts: Texts) -> None:
        """The cases that run the guide against the fake claude in a temporary folder."""
        with tempfile.TemporaryDirectory(prefix="install-guide-self-test-") as scratch:
            toy = toy_run(Path(scratch))
            green_examined = self.green_run_cases(toy)
            unit = unit_of(toy, texts.pin_note)
            self.marketplace_list_cases(unit, texts)
            self.plugin_list_cases(unit, texts)
            self.list_identity_cases(unit, texts)
            self.list_command_cases(toy, unit, texts)
            copies = copies_placed(unit)
            self.reinstall_claim_cases(unit, copies)
            self.update_claim_cases(unit, copies)
            person = person_of(unit, toy.four)
            self.plugin_cache_location_cases(unit, texts, copies)
            self.install_run_cases(toy, texts, green_examined)
            self.person_environment_cases(toy, unit, texts, person, green_examined)
            self.broken_reply_cases(toy, unit, texts)
            versions = Versions(toy, toy.root / "version.log")
            self.claude_version_cases(toy, texts, person, versions)
            self.whole_run_cases(toy, texts, versions)
            self.run_finding_cases(toy, texts, versions)
            self.clone_and_source_cases(toy)

    def mark_cases(self) -> None:
        """The block-mark reader: each malformed fence one finding, a clean guide none."""
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
            self.case(name, len(findings) == 1 and findings[0].what.startswith(expected), whats(findings))
        _, misplaced = blocks_of(toy_guide().replace("```yaml check=dials", "```check=dials"))
        self.case(
            "a misplaced dials mark red once, its fix a yaml fence",
            len(misplaced) == 1 and misplaced[0].fix.endswith("```yaml check=dials"),
            " | ".join(f"{f.what} / {f.fix}" for f in misplaced),
        )
        _, clean = blocks_of(toy_guide() + "\n```text\nnot a command\n```\n")
        self.case(
            "a green guide gives no mark finding; a `text` fence needs no mark", not clean, whats(clean)
        )

    def module_listing_cases(self, listings: Listings) -> None:
        """The module folders of a tree: which are modules, in what order, and what a bad one says."""

        def tree(*folders: str, files: tuple[str, ...] = (), documents: bool = True) -> Path:
            """A tree whose modules/ holds each folder, with a manifest of version 1.0 and, unless
            `documents` is off, its MODULE.md, and each plain file; `modules/` is made even for none."""
            root = listings.next_folder("tree")
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
        self.case(
            "a folder `.x` and a folder `_x` are skipped silently",
            hidden == ["const-a", "const-b"],
            str(hidden),
        )
        mixed = list(modules_of(tree("glossary", "const-a")))
        self.case("a folder named without const- is a module", mixed == ["const-a", "glossary"], str(mixed))
        plain = list(modules_of(tree("const-a", files=("const-file",))))
        self.case("a plain file of modules/ is no module, and no BROKEN", plain == ["const-a"], str(plain))
        with listed_in_reverse():  # modules/ is listed reversed, whatever the filesystem lists
            ordered = list(modules_of(tree("const-b", "const-c", "const-a")))
        self.case(
            "the modules are sorted by name, whatever order the folder lists",
            ordered == ["const-a", "const-b", "const-c"],
            str(ordered),
        )
        said = broken_said(tree("const-ghost", documents=False))
        self.case(
            "a module folder without its MODULE.md is a teaching BROKEN line",
            said == "modules/const-ghost has no MODULE.md — fix: restore the module document",
            said,
        )
        no_modules = listings.folder / "no-modules"
        no_modules.mkdir()
        said = broken_said(no_modules)
        self.case(
            "a tree with no modules/ is a teaching BROKEN line",
            said == f"{no_modules} has no modules/ directory — fix: run the check from a checkout of the kit",
            said,
        )
        empty = tree(files=("const-file",))
        said = broken_said(empty)
        self.case(
            "a modules/ with no module folder is BROKEN, as the check always said",
            said == f"no module under {empty / 'modules'} — fix: run the check from a clone of the kit",
            said,
        )
        versionless = tree("const-a")
        (versionless / "modules" / "const-a" / ".claude-plugin" / "plugin.json").write_text(
            "{}", encoding="utf-8"
        )
        said = broken_said(versionless)
        self.case(
            "a manifest with no version is BROKEN, its version read as always",
            said.endswith("gives no version ('version') — fix: restore the module's manifest"),
            said,
        )
        for shape, manifest_text, held in (  # a manifest that is valid JSON and no object
            ("a list", "[]", "list"),
            ("a string", '"const-a"', "str"),
            ("a number", "3", "int"),
            ("null", "null", "NoneType"),
        ):
            odd = tree("const-a")
            odd_manifest = odd / "modules" / "const-a" / ".claude-plugin" / "plugin.json"
            odd_manifest.write_text(manifest_text, encoding="utf-8")
            said = broken_said(odd)
            self.case(
                f"a manifest that is {shape} is BROKEN, naming it and the kind it holds, never a traceback",
                said
                == f"{odd_manifest} is no JSON object, it holds a {held} — fix: restore it as a JSON object",
                said,
            )
        for shape, manifest_text, held in (  # a version that is no string or number
            ("null", '{"version": null}', "NoneType"),
            ("a list", '{"version": ["1.0"]}', "list"),
            ("an object", '{"version": {"major": 1}}', "dict"),
            ("true", '{"version": true}', "bool"),
        ):
            odd = tree("const-a")
            odd_manifest = odd / "modules" / "const-a" / ".claude-plugin" / "plugin.json"
            odd_manifest.write_text(manifest_text, encoding="utf-8")
            said = broken_said(odd)
            self.case(
                f"a manifest whose version is {shape} is BROKEN, naming the kind it holds",
                said == f"{odd_manifest} gives a version that is no string or number, it holds a {held}"
                " — fix: restore the module's manifest",
                said,
            )
        for shape, manifest_text, version_text in (  # a version that is a string or a number reads as it did
            ("a string", '{"version": "0.0.2"}', "0.0.2"),
            ("an integer", '{"version": 3}', "3"),
            ("a float", '{"version": 1.5}', "1.5"),
        ):
            fine = tree("const-a")
            (fine / "modules" / "const-a" / ".claude-plugin" / "plugin.json").write_text(
                manifest_text, encoding="utf-8"
            )
            read_back = modules_of(fine)
            self.case(
                f"a manifest whose version is {shape} is read as the text of it",
                read_back == {"const-a": version_text},
                str(read_back),
            )

    def marketplace_name_cases(self, listings: Listings) -> None:
        """The marketplace file's name, read as the check reads it."""

        def market_said(text: str | None, as_folder: bool = False) -> tuple[Path, str]:
            """The folder of a kit whose .claude-plugin/marketplace.json holds `text` (no file for None,
            a folder of that name for `as_folder`), and what `marketplace_name` gives over it: the name, or
            its DocumentError's message, or the OSError a read of it let escape."""
            folder = listings.next_folder("market")
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
        self.case("the marketplace's name is the file's top-level name", got == "toy-mp", got)
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
            self.case(
                f"{name} is a teaching DocumentError",
                got == f"{folder}/.claude-plugin/marketplace.json{tail}",
                got,
            )
        folder, got = market_said(None, as_folder=True)  # the file "unreadable" of the reader's docstring
        self.case(
            "a marketplace.json that is a folder, unreadable though it exists, is a teaching DocumentError",
            got == f"{folder}/.claude-plugin/marketplace.json cannot be read (Is a directory) — fix: run the"
            " check from a checkout of the kit, which holds the file",
            got,
        )

    def pin_file_cases(self, listings: Listings, texts: Texts) -> None:
        """The pin file's version, read as the check reads it."""

        def pin_said(content: bytes | None) -> tuple[Path, str]:
            """The folder of a kit whose scripts/claude-code.version holds `content` (no file for None),
            and what `pinned_claude` gives over it: the version, or its DocumentError's message."""
            folder = listings.next_folder("pin")
            (folder / "scripts").mkdir(parents=True)
            if content is not None:
                (folder / "scripts" / "claude-code.version").write_bytes(content)
            try:
                return folder, pinned_claude(folder)
            except DocumentError as bad:
                return folder, str(bad)

        for name, one_line in (("without a final line break", b"2.1.282"), ("with one", b"2.1.282\n")):
            folder, got = pin_said(one_line)
            self.case(f"a pin file holding one version {name} gives the version", got == "2.1.282", got)
        for name, content, tail in (
            (
                "missing",
                None,
                f" cannot be read (No such file or directory){texts.pin_fix}",
            ),
            ("empty", b"", f" is empty{texts.pin_fix}"),
            ("holding CRLF", b"2.1.282\r\n", f" is not one version ('2.1.282\\r\\n'){texts.pin_fix}"),
            (
                "holding a byte-order mark",
                b"\xef\xbb\xbf2.1.282\n",
                f" is not one version ('\\ufeff2.1.282\\n'){texts.pin_fix}",
            ),
            (
                "holding two lines",
                b"2.1.282\n2.1.286\n",
                f" is not one version ('2.1.282\\n2.1.286\\n'){texts.pin_fix}",
            ),
            ("holding a word", b"latest\n", f" is not one version ('latest\\n'){texts.pin_fix}"),
            (
                "holding a blank line after the version",
                b"2.1.282\n\n",
                f" is not one version ('2.1.282\\n\\n'){texts.pin_fix}",
            ),
            ("holding a line break alone", b"\n", f" is not one version ('\\n'){texts.pin_fix}"),
            ("holding two numbers", b"2.1\n", f" is not one version ('2.1\\n'){texts.pin_fix}"),
            (
                "holding a fourth number",
                b"2.1.282.1\n",
                f" is not one version ('2.1.282.1\\n'){texts.pin_fix}",
            ),
            (
                "holding a v before the version",
                b"v2.1.282\n",
                f" is not one version ('v2.1.282\\n'){texts.pin_fix}",
            ),
            (
                "holding a space after the version",
                b"2.1.282 \n",
                f" is not one version ('2.1.282 \\n'){texts.pin_fix}",
            ),
            (
                "holding a space before the version",
                b" 2.1.282\n",
                f" is not one version (' 2.1.282\\n'){texts.pin_fix}",
            ),
            (
                "holding another script's digits",
                "٢.١.٢٨٢\n".encode(),
                f" is not one version ('٢.١.٢٨٢\\n'){texts.pin_fix}",
            ),
            (
                "holding bytes that are no UTF-8",
                b"2.1.282\xff\n",
                f" is not one version ('2.1.282�\\n'){texts.pin_fix}",
            ),
        ):
            folder, got = pin_said(content)
            self.case(
                f"a pin file {name} is a teaching DocumentError",
                got == f"{folder}/scripts/claude-code.version{tail}",
                got,
            )

    def settings_file_cases(self, listings: Listings, texts: Texts) -> None:
        """The project's settings file: what it enables and what a bad one says."""

        def settings_said(text: str | None, as_folder: bool = False) -> tuple[Path, str]:
            """The project whose .claude/settings.json holds `text` (no file for None, a folder of that name
            for `as_folder`), and what `enabled` gives over it: the plugins it enables, sorted and joined by
            commas, or "none", or its Broken's message."""
            project = listings.next_folder("settings")
            (project / ".claude").mkdir(parents=True)
            if as_folder:
                (project / ".claude" / "settings.json").mkdir()
            elif text is not None:
                (project / ".claude" / "settings.json").write_text(text, encoding="utf-8")
            try:
                return project, ",".join(sorted(enabled(project, texts.pin_note))) or "none"
            except Broken as bad:
                return project, str(bad)

        for name, text, enables in (
            ("is missing", None, "none"),
            ("is an empty object", "{}", "none"),
            ("holds no enabledPlugins", '{"theme": "dark"}', "none"),
            ("holds an empty enabledPlugins", '{"enabledPlugins": {}}', "none"),
            (
                "holds true, false, a string and a number",
                '{"enabledPlugins": {"c@m": "yes", "b@m": false, "a@m": true, "d@m": 1, "e@m": true}}',
                "a@m,e@m",
            ),
        ):
            folder, got = settings_said(text)
            self.case(f"a project's settings file that {name} enables {enables}", got == enables, got)
        for name, text, tail in (
            (
                "is empty",
                "",
                f" is no JSON (Expecting value: line 1 column 1 (char 0)){texts.settings_fix}",
            ),
            (
                "is no JSON",
                "not json",
                f" is no JSON (Expecting value: line 1 column 1 (char 0)){texts.settings_fix}",
            ),
            ("is a JSON list", "[]", f" is a JSON list, not an object{texts.settings_fix}"),
            ("is a JSON string", '"x"', f" is a JSON str, not an object{texts.settings_fix}"),
            ("is a JSON null", "null", f" is a JSON NoneType, not an object{texts.settings_fix}"),
            (
                "holds an enabledPlugins list",
                '{"enabledPlugins": ["a@m"]}',
                f" gives an enabledPlugins that is a list, not an object{texts.settings_fix}",
            ),
            (
                "holds an enabledPlugins null",
                '{"enabledPlugins": null}',
                f" gives an enabledPlugins that is a NoneType, not an object{texts.settings_fix}",
            ),
            (
                "holds an enabledPlugins string",
                '{"enabledPlugins": "a@m"}',
                f" gives an enabledPlugins that is a str, not an object{texts.settings_fix}",
            ),
        ):
            folder, got = settings_said(text)
            self.case(
                f"a project's settings file that {name} is a teaching BROKEN",
                got == f"{folder}/.claude/settings.json{tail}",
                got,
            )
        folder, got = settings_said(None, as_folder=True)
        self.case(
            "a project's settings file that is a folder is a teaching BROKEN",
            got == f"{folder}/.claude/settings.json cannot be read (Is a directory){texts.settings_fix}",
            got,
        )

    def green_run_cases(self, toy: Toy) -> str:
        """A green run over the toy kit, and a run over the nameless one; what the green run examined."""
        green, examined, green_note = run_guide(toy_guide(), toy.kit, toy.base)
        self.case(
            "a green toy run on the pinned version green, with no note",
            not green and green_note == "",
            f"{whats(green)} ({examined}) {green_note!r}",
        )
        try:
            run_guide(toy_guide(), toy.nameless, toy.base | {"FAKE_SOURCE": str(toy.nameless)})
            unnamed = "no Broken"
        except Broken as broken:
            unnamed = str(broken)
        self.case(
            "a kit whose marketplace.json gives no name is a BROKEN, naming the clone's file",
            unnamed.endswith(
                '/dev/constitution-kit/.claude-plugin/marketplace.json has no "name"'
                " — fix: give the marketplace its name, at the top of the object"
            ),
            unnamed,
        )
        return examined

    def marketplace_list_cases(self, unit: Unit, texts: Texts) -> None:
        """The replies to the marketplace list: the clone they name, and each reply the reader refuses."""
        stray = unit.mkt(name="stray-mp", installLocation="/wrong")  # a GitHub entry of the right repository
        for name, entries, result in (
            ("one entry", [unit.mkt()], unit.clone_of),
            ("another marketplace's entry first", [unit.other, unit.mkt()], unit.clone_of),
            ("another marketplace's entry last", [unit.mkt(), unit.other], unit.clone_of),
            ("a GitHub entry of another name first", [stray, unit.mkt()], unit.clone_of),
            ("a GitHub entry of another name last", [unit.mkt(), stray], unit.clone_of),
            ("no entry", [], "RED the configuration knows no marketplace toy-mp"),
            ("only another marketplace's", [unit.other], "RED the configuration knows no marketplace toy-mp"),
            (
                "a directory source",
                [unit.mkt(source="directory", path="/p")],
                "RED the marketplace is registered from a directory source, not from GitHub",
            ),
            (
                "another repository",
                [unit.mkt(repo="other/kit")],
                "RED the marketplace is registered from other/kit, not from toy/kit",
            ),
            (
                "a directory source with no repository, whose clone is no folder: the source is the finding",
                [without(unit.mkt(source="directory", path="/p", installLocation=str(unit.gone)), "repo")],
                "RED the marketplace is registered from a directory source, not from GitHub",
            ),
            (
                "another repository, whose clone is no folder: the repository is the finding",
                [unit.mkt(repo="other/kit", installLocation=str(unit.gone))],
                "RED the marketplace is registered from other/kit, not from toy/kit",
            ),
        ):
            got = unit.mkt_said(json.dumps(entries))
            self.case(f"marketplace list, {name}: {result.split(' ')[0]}", got == result, got)
        for name, text, code, rest in (
            (
                "not JSON",
                "garbled",
                0,
                f"printed no JSON ('garbled': {texts.no_json})",
            ),
            ("empty", "", 0, f"printed no JSON ('': {texts.no_json})"),
            (
                "text whose quotation is exactly 200 characters",
                "x" * 198,
                0,
                f"printed no JSON ('{'x' * 198}': {texts.no_json})",
            ),
            (
                "text whose quotation is 201 characters, cut at 200 and ended with …",
                "x" * 199,
                0,
                f"printed no JSON ('{'x' * 199}…: {texts.no_json})",
            ),
            (
                "text much longer than that, cut at 200 characters",
                "garbled " * 40,
                0,
                f"printed no JSON ({('garbled ' * 40)!r:.200}…: {texts.no_json})",
            ),
            ("an object", "{}", 0, "printed a JSON dict, not a list"),
            ("a string", '"toy-mp"', 0, "printed a JSON str, not a list"),
            ("null", "null", 0, "printed a JSON NoneType, not a list"),
            ("a number", "7", 0, "printed a JSON int, not a list"),
            ("a string entry", '["x"]', 0, "lists an entry that is no object ('x')"),
            ("a number entry last", json.dumps([unit.mkt(), 7]), 0, "lists an entry that is no object (7)"),
            ("a number entry first", json.dumps([7, unit.mkt()]), 0, "lists an entry that is no object (7)"),
            (
                "a null entry last",
                json.dumps([unit.mkt(), None]),
                0,
                "lists an entry that is no object (None)",
            ),
            (
                "two entries of the name",
                json.dumps([unit.mkt(), unit.mkt()]),
                0,
                "lists 2 entries named toy-mp",
            ),
            (
                "two entries of the name round another",
                json.dumps([unit.mkt(), unit.other, unit.mkt(repo="other/kit")]),
                0,
                "lists 2 entries named toy-mp",
            ),
            (
                "no source",
                json.dumps([without(unit.mkt(), "source")]),
                0,
                "gives no source string for toy-mp (source is absent)",
            ),
            (
                "a source that is a number",
                json.dumps([unit.mkt(source=7)]),
                0,
                "gives no source string for toy-mp (source is 7)",
            ),
            (
                "an empty source",
                json.dumps([unit.mkt(source="")]),
                0,
                "gives no source string for toy-mp (source is '')",
            ),
            (
                "a source that is null",
                json.dumps([unit.mkt(source=None)]),
                0,
                "gives no source string for toy-mp (source is None)",
            ),
            (
                "no installLocation",
                json.dumps([without(unit.mkt(), "installLocation")]),
                0,
                "gives no installLocation string for toy-mp (installLocation is absent)",
            ),
            (
                "an installLocation that is a number",
                json.dumps([unit.mkt(installLocation=7)]),
                0,
                "gives no installLocation string for toy-mp (installLocation is 7)",
            ),
            (
                "an installLocation that is a list",
                json.dumps([unit.mkt(installLocation=["x"])]),
                0,
                "gives no installLocation string for toy-mp (installLocation is ['x'])",
            ),
            (
                "an empty installLocation",
                json.dumps([unit.mkt(installLocation="")]),
                0,
                "gives no installLocation string for toy-mp (installLocation is '')",
            ),
            (
                "no installLocation on a directory source, before the finding on its source",
                json.dumps([without(unit.mkt(source="directory", path="/p"), "installLocation")]),
                0,
                "gives no installLocation string for toy-mp (installLocation is absent)",
            ),
            (
                "no installLocation on another repository's entry, before the finding on its repository",
                json.dumps([without(unit.mkt(repo="other/kit"), "installLocation")]),
                0,
                "gives no installLocation string for toy-mp (installLocation is absent)",
            ),
            (
                "no repository on a GitHub entry",
                json.dumps([without(unit.mkt(), "repo")]),
                0,
                "gives no repo string for toy-mp (repo is absent)",
            ),
            (
                "a repository that is a number",
                json.dumps([unit.mkt(repo=7)]),
                0,
                "gives no repo string for toy-mp (repo is 7)",
            ),
            (
                "an empty repository",
                json.dumps([unit.mkt(repo="")]),
                0,
                "gives no repo string for toy-mp (repo is '')",
            ),
            (
                "a repository that is null",
                json.dumps([unit.mkt(repo=None)]),
                0,
                "gives no repo string for toy-mp (repo is None)",
            ),
            (
                "a repository that is a list",
                json.dumps([unit.mkt(repo=["toy/kit"])]),
                0,
                "gives no repo string for toy-mp (repo is ['toy/kit'])",
            ),
            (
                "an installLocation that does not exist",
                json.dumps([unit.mkt(installLocation=str(unit.gone))]),
                0,
                f"names an installLocation that is no folder ({unit.gone})",
            ),
            (
                "an installLocation that is a file",
                json.dumps([unit.mkt(installLocation=str(unit.a_file))]),
                0,
                f"names an installLocation that is no folder ({unit.a_file})",
            ),
            (
                "an installLocation that does not exist, on an entry round another marketplace's",
                json.dumps([unit.other, unit.mkt(installLocation=str(unit.gone)), stray]),
                0,
                f"names an installLocation that is no folder ({unit.gone})",
            ),
            ("an exit 1 with a message", "boom", 1, "exited 1 (boom)"),
            ("an exit 3 with a valid reply", "[]", 3, "exited 3 ([])"),
        ):
            got = unit.mkt_said(text, code)
            self.case(
                f"marketplace list, {name}: BROKEN",
                got == f"BROKEN {texts.mkt_command} {rest}{texts.reply_fix(rest, 'platform_clone')}",
                got,
            )

    def plugin_list_cases(self, unit: Unit, texts: Texts) -> None:
        """The replies to the plugin list: the entries they hold, and each reply the reader refuses."""
        alone = without(unit.plug(scope="user", version="9.9.9", installPath="/nowhere/u"), "projectPath")
        away = unit.plug(version="9.9.9", installPath="/nowhere/o", projectPath="/elsewhere/project")
        for name, entries, result, where in (
            ("no entries", [], texts.picks(), unit.project),
            ("both modules", unit.both, texts.picks(texts.alpha_pick, texts.beta_pick), unit.project),
            (
                "a user-scope entry of the id first",
                [alone, *unit.both],
                texts.picks(texts.alpha_pick, texts.beta_pick),
                unit.project,
            ),
            (
                "a user-scope entry of the id last",
                [*unit.both, alone],
                texts.picks(texts.alpha_pick, texts.beta_pick),
                unit.project,
            ),
            (
                "a user-scope entry between",
                [unit.plug(), alone, unit.plug("const-beta")],
                texts.picks(texts.alpha_pick, texts.beta_pick),
                unit.project,
            ),
            (
                "an entry for another project first",
                [away, *unit.both],
                texts.picks(texts.alpha_pick, texts.beta_pick),
                unit.project,
            ),
            (
                "an entry for another project last",
                [*unit.both, away],
                texts.picks(texts.alpha_pick, texts.beta_pick),
                unit.project,
            ),
            (
                "an entry for another project and a user-scope one round the right one",
                [away, alone, unit.plug(), alone, away],
                texts.picks(texts.alpha_pick),
                unit.project,
            ),
            ("two user-scope entries of the id", [alone, alone], texts.picks(), unit.project),
            (
                "an entry of another marketplace first, whatever its fields",
                [{"id": "const-alpha@other-mp", "scope": "project"}, *unit.both],
                texts.picks(texts.alpha_pick, texts.beta_pick),
                unit.project,
            ),
            (
                "an entry of a module the kit has not, whatever its fields",
                [{"id": f"const-ghost@{TOY_MP}", "scope": "project"}, *unit.both],
                texts.picks(texts.alpha_pick, texts.beta_pick),
                unit.project,
            ),
            (
                "a project and a local entry of the id for the project",
                [unit.plug(), unit.plug(scope="local", installPath="/copies/local-alpha")],
                texts.picks(texts.alpha_pick + ",local:0.0.1:/copies/local-alpha"),
                unit.project,
            ),
            (
                "the project given by a link, the entry holding its resolved path",
                [unit.plug(projectPath=str(unit.project.resolve()))],
                texts.picks(texts.alpha_pick),
                unit.linked,
            ),
            (
                "the project given by a link, the entry holding the link's path",
                [unit.plug(projectPath=str(unit.linked))],
                texts.picks(texts.alpha_pick),
                unit.linked,
            ),
        ):
            got = unit.plugins_said(json.dumps(entries), project=where)
            self.case(f"plugin list, {name}", got == result, got)
        for name, text, code, rest in (
            ("not JSON", "garbled", 0, f"printed no JSON ('garbled': {texts.no_json})"),
            ("empty", "", 0, f"printed no JSON ('': {texts.no_json})"),
            ("an object", "{}", 0, "printed a JSON dict, not a list"),
            ("null", "null", 0, "printed a JSON NoneType, not a list"),
            ("a string entry", '["x"]', 0, "lists an entry that is no object ('x')"),
            ("a number entry last", json.dumps([*unit.both, 7]), 0, "lists an entry that is no object (7)"),
            ("a number entry first", json.dumps([7, *unit.both]), 0, "lists an entry that is no object (7)"),
            ("an exit 1 with a message", "boom", 1, "exited 1 (boom)"),
            ("an exit 2 with a valid reply", json.dumps(unit.both), 2, f"exited 2 ({json.dumps(unit.both)})"),
        ):
            got = unit.plugins_said(text, code)
            self.case(
                f"plugin list, {name}: BROKEN",
                got == f"BROKEN {texts.listed_command} {rest}{texts.reply_fix(rest, 'project_entries')}",
                got,
            )
        for field in ("installPath", "version", "scope"):
            for shape, entry, said in (
                ("absent", without(unit.plug(), field), "absent"),
                ("a number", unit.plug(**{field: 7}), "7"),
                ("empty", unit.plug(**{field: ""}), "''"),
                ("null", unit.plug(**{field: None}), "None"),
            ):
                rest = f"gives no {field} string for const-alpha@toy-mp ({field} is {said})"
                # the user-scope entry of the id, which the check never takes, is read too: first and last
                for placed, entries in (
                    ("a project entry alone", [entry]),
                    ("a project entry last", [unit.plug("const-beta"), entry]),
                    ("a project entry first", [entry, unit.plug("const-beta")]),
                    (
                        "a user-scope entry last",
                        [
                            *unit.both,
                            without(entry, "projectPath") | ({} if field == "scope" else {"scope": "user"}),
                        ],
                    ),
                ):
                    got = unit.plugins_said(json.dumps(entries))
                    self.case(
                        f"plugin list, {field} {shape} on {placed}: BROKEN",
                        got == f"BROKEN {texts.listed_command} {rest}{fix_of('project_entries')}",
                        got,
                    )
        for scope in ("project", "local"):
            for shape, entry, said in (
                ("absent", without(unit.plug(scope=scope), "projectPath"), "absent"),
                ("a number", unit.plug(scope=scope, projectPath=7), "7"),
                ("empty", unit.plug(scope=scope, projectPath=""), "''"),
                ("null", unit.plug(scope=scope, projectPath=None), "None"),
            ):
                rest = (
                    "gives no projectPath string for const-alpha@toy-mp"
                    f" at scope {scope} (projectPath is {said})"
                )
                for placed, entries in (
                    ("alone", [entry]),
                    ("last", [*unit.both, entry]),
                    ("first", [entry, *unit.both]),
                ):
                    got = unit.plugins_said(json.dumps(entries))
                    self.case(
                        f"plugin list, a {scope}-scope entry with projectPath {shape}, {placed}: BROKEN",
                        got == f"BROKEN {texts.listed_command} {rest}{fix_of('project_entries')}",
                        got,
                    )
        twice = (
            f"lists 2 project-scope entries of const-alpha@toy-mp for the project{fix_of('project_entries')}"
        )
        for name, entries, rest in (
            ("two entries of the id", [unit.plug(), unit.plug()], twice),
            (
                "two entries round another module's",
                [unit.plug(), unit.plug("const-beta"), unit.plug()],
                twice,
            ),
            ("two entries round a user-scope one", [unit.plug(), alone, unit.plug()], twice),
            ("three entries", [unit.plug(), unit.plug(), unit.plug()], twice.replace("lists 2", "lists 3")),
            (
                "two entries of the second module",
                [unit.plug("const-beta"), unit.plug(), unit.plug("const-beta")],
                twice.replace("const-alpha", "const-beta"),
            ),
            (
                "a shape fault of the second module before the two entries of the first",
                [unit.plug(), unit.plug(), without(unit.plug("const-beta"), "version")],
                "gives no version string for const-beta@toy-mp (version is absent)"
                + fix_of("project_entries"),
            ),
        ):
            got = unit.plugins_said(json.dumps(entries))
            self.case(f"plugin list, {name}: BROKEN", got == f"BROKEN {texts.listed_command} {rest}", got)

    def list_identity_cases(self, unit: Unit, texts: Texts) -> None:
        """Names and ids in a reply, and a warning beside a valid list."""
        # every entry of either reply carries its identifying field as a string, an entry of another
        # marketplace or plugin too: an entry without it is a reply of the wrong shape, never an entry to skip
        for shape, entry, said in (
            ("absent", without(unit.mkt(), "name"), "absent"),
            (
                "absent, a `title` where the name stands",
                without(unit.mkt(), "name") | {"title": TOY_MP},
                "absent",
            ),
            ("absent on an entry that is another marketplace's", without(unit.other, "name"), "absent"),
            ("a number", unit.mkt(name=7), "7"),
            ("empty", unit.mkt(name=""), "''"),
            ("null", unit.mkt(name=None), "None"),
        ):
            for placed, entries, position in (
                ("alone", [entry], 1),
                ("first", [entry, unit.mkt()], 1),
                ("between", [unit.other, entry, unit.mkt()], 2),
                ("last", [unit.mkt(), entry], 2),
            ):
                rest = f"gives no name string for the list's entry {position} (name is {said})"
                got = unit.mkt_said(json.dumps(entries))
                self.case(
                    f"marketplace list, a name {shape}, {placed}: BROKEN",
                    got == f"BROKEN {texts.mkt_command} {rest}{fix_of('platform_clone')}",
                    got,
                )
        id_faults: list[tuple[str, dict[str, object], str]] = [
            ("absent", without(unit.plug(), "id"), "absent"),
            ("absent on an entry of nothing else", {"scope": "project"}, "absent"),
            ("a number", unit.plug(id=7), "7"),
            ("empty", unit.plug(id=""), "''"),
            ("null", unit.plug(id=None), "None"),
        ]
        for shape, entry, said in id_faults:
            for placed, entries, position in (
                ("alone", [entry], 1),
                ("first", [entry, *unit.both], 1),
                ("between", [unit.plug(), entry, unit.plug("const-beta")], 2),
                ("last", [*unit.both, entry], 3),
            ):
                rest = f"gives no id string for the list's entry {position} (id is {said})"
                got = unit.plugins_said(json.dumps(entries))
                self.case(
                    f"plugin list, an id {shape}, {placed}: BROKEN",
                    got == f"BROKEN {texts.listed_command} {rest}{fix_of('project_entries')}",
                    got,
                )
        # the list commands' output: standard output alone is the reply, a warning on standard error is not
        warning = "warning: the plugin cache is out of date"
        got = unit.mkt_said(json.dumps([unit.mkt()]), FAKE_STDERR=warning)
        self.case(
            "marketplace list, a valid list on standard output and a warning on standard error, exit 0: "
            "the list is read",
            got == unit.clone_of,
            got,
        )
        got = unit.plugins_said(json.dumps(unit.both), FAKE_STDERR=warning)
        self.case(
            "plugin list, a valid list on standard output and a warning on standard error, exit 0: "
            "the list is read",
            got == texts.picks(texts.alpha_pick, texts.beta_pick),
            got,
        )

    def list_command_cases(self, toy: Toy, unit: Unit, texts: Texts) -> None:
        """Where the list commands run, and a command that times out or says nothing."""
        # the folder each list runs in: the marketplace list where the block ended, the plugin list in the
        # project; neither in the run's home folder
        block_end = unit.folder / "block-end"
        block_end.mkdir()
        cwd_log = unit.folder / "cwd.log"
        where_state = unit.state(
            FAKE_MKT=unit.reply_file(json.dumps([unit.mkt()])),
            FAKE_LIST=unit.reply_file(json.dumps(unit.both)),
            FAKE_CWD=str(cwd_log),
        )
        where_state.cwd = block_end
        platform_clone(where_state)
        project_entries(where_state, unit.project)
        ran_in = dict(line.split("|", 1) for line in cwd_log.read_text(encoding="utf-8").splitlines())
        self.case(
            "marketplace list runs in the folder the block ended in",
            Path(ran_in.get("marketplace", "none")).resolve() == block_end.resolve(),
            str(ran_in),
        )
        self.case(
            "plugin list runs in the project",
            Path(ran_in.get("plugins", "none")).resolve() == unit.project.resolve(),
            str(ran_in),
        )
        # a list that times out is a BROKEN, never an empty list: the timeout is the runner's exit 124
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["claude"], 7)) as timing:
            apart = run_apart(["claude", "plugin", "list", "--json"], unit.folder, toy.base, timeout=7)
        self.case(
            "a command that times out is exit 124 with no output and the reason, at the timeout it was given",
            apart == (124, "", "timed out after 7 s") and timing.call_args.kwargs["timeout"] == 7,
            f"{apart} {timing.call_args}",
        )
        for which, command, reader in (
            ("marketplace", texts.mkt_command, "platform_clone"),
            ("plugin", texts.listed_command, "project_entries"),
        ):
            with mock.patch(
                "subprocess.run", side_effect=subprocess.TimeoutExpired(["claude"], TIMEOUT)
            ) as timing:
                got = (
                    unit.mkt_said(json.dumps([unit.mkt()]))
                    if which == "marketplace"
                    else unit.plugins_said(json.dumps(unit.both))
                )
            self.case(
                f"{which} list that times out: BROKEN, never an empty list, after the runner's timeout",
                got == f"BROKEN {command} exited 124 (timed out after {TIMEOUT} s) — fix: run the check again"
                and timing.call_args.kwargs["timeout"] == TIMEOUT,
                f"{got} ({reader}) {timing.call_args}",
            )
        # a list command that wrote no reply has no reader to update: the command's own fix, on the pin and
        # off it; the lines are typed by hand

        def silent_said(which: str, code: int, note: Note, timed_out: bool = False) -> str:
            """What the reader of the marketplace list or the plugin list says over a command that exits
            `code`, or that times out (the process mocked, no wait), in the state `note` records."""
            state = unit.state(
                FAKE_MKT=unit.reply_file(json.dumps([unit.mkt()])),
                FAKE_MKT_EXIT=str(code),
                FAKE_LIST=unit.reply_file(json.dumps(unit.both)),
                FAKE_LIST_EXIT=str(code),
            )
            state.note = note
            hang = subprocess.TimeoutExpired(["claude"], TIMEOUT)
            with contextlib.ExitStack() as stack:
                if timed_out:
                    stack.enter_context(mock.patch("subprocess.run", side_effect=hang))
                try:
                    if which == "marketplace":
                        platform_clone(state)
                    else:
                        project_entries(state, unit.project)
                except Broken as bad:
                    return f"BROKEN {bad}"
            return "no Broken"

        for which, command, raw in (
            ("marketplace", texts.mkt_command, "claude plugin marketplace list --json"),
            ("plugin", texts.listed_command, "claude plugin list --json"),
        ):
            reply = json.dumps([unit.mkt()]) if which == "marketplace" else json.dumps(unit.both)
            for code, timed_out in ((1, False), (3, False), (124, False), (124, True)):
                for state_name, note in (("on the pin", texts.pin_note), ("off the pin", texts.other_note)):
                    said = "timed out after " + str(TIMEOUT) + " s" if code == 124 and timed_out else reply
                    fix = texts.silent_fix(raw, code, note is texts.pin_note)
                    got = silent_said(which, code, note, timed_out)
                    what = "times out" if timed_out else "exits " + str(code)
                    self.case(
                        f"{which} list that {what}, {state_name}: BROKEN, the command's own fix, no reader",
                        got == f"BROKEN {command} exited {code} ({said}){fix}",
                        got,
                    )

    def reinstall_claim_cases(self, unit: Unit, copies: Copies) -> None:
        """The reinstall claim over the copies a project lists: where it reads the platform's clone from."""
        # the reinstall's comparison reads the platform's clone from the state, else from marketplace list
        reinstalling = unit.state(
            FAKE_LIST=unit.reply_file(json.dumps(copies.listed)),
            FAKE_MKT=unit.reply_file(json.dumps([unit.mkt(installLocation=str(copies.wanted_clone))])),
        )
        reinstalling.project = unit.project
        reinstalling.clone = None
        got = claim(reinstalling, "reinstall")
        self.case(
            "a reinstall with no clone on the state reads it from marketplace list: alike, no finding",
            got == "",
            got,
        )
        (unit.held_copy("const-alpha") / "a.txt").write_text("changed\n", encoding="utf-8")
        got = claim(reinstalling, "reinstall")
        self.case(
            "a reinstall with no clone on the state, a copy that differs from the listed clone's module",
            got == "const-alpha's a.txt is not alike in the cache and the marketplace",
            got,
        )
        (unit.held_copy("const-alpha") / "a.txt").write_text("same\n", encoding="utf-8")
        reinstalling.clone = copies.other_clone
        got = claim(reinstalling, "reinstall")
        self.case(
            "a reinstall compares with the clone the state keeps, not with a fresh read",
            got == "const-alpha's a.txt is not alike in the cache and the marketplace",
            got,
        )

    def update_claim_cases(self, unit: Unit, copies: Copies) -> None:
        """The update claim over the copies a project lists: which entries it picks, and an installPath that
        is no folder of the cache."""

        def local(module: str) -> dict[str, object]:
            """A local-scope entry for the project the claim must not pick: another version, no folder."""
            return unit.plug(module, scope="local", version="9.9.9", installPath=str(unit.gone / module))

        right_alpha, right_beta = copies.listed
        got = unit.update_said(copies.listed)
        self.case("update claim, the project-scope entries alone: no finding", got == "", got)
        for name, entries in (
            ("before", [local("const-alpha"), *copies.listed]),
            ("after", [*copies.listed, local("const-alpha")]),
            (
                "round each of two modules'",
                [local("const-alpha"), right_alpha, local("const-alpha"), local("const-beta"), right_beta]
                + [local("const-beta")],
            ),
        ):
            got = unit.update_said(entries)
            self.case(
                f"update claim, a local-scope entry of the id {name} the project-scope one: it is picked",
                got == "",
                got,
            )
        got = unit.update_said([local("const-alpha"), right_beta])
        self.case(
            "update claim, only a local-scope entry for a module: not installed for the project",
            got == "const-alpha is not installed for the project",
            got,
        )
        # the cache's copy is where the layout puts it, so the folder that fails is the cache's own
        for name, own_config, as_file in (
            ("a file", unit.folder / "config-file", True),
            ("no folder at all", unit.folder / "config-none", False),
        ):
            plugins_root = own_config / "plugins"
            at_config = unit.state()
            at_config.config = own_config
            target = at_config.cached("const-alpha")
            self.case(
                f"the copy of an installPath case, {name}, is under the plugins root of its configuration",
                plugins_root in target.parents,
                str(target),
            )
            if plugins_root not in target.parents:
                continue
            if as_file:
                target.parent.mkdir(parents=True)
                target.write_text("not a folder\n", encoding="utf-8")
            got = unit.update_said([unit.plug(installPath=str(target)), right_beta], own_config)
            self.case(
                f"update claim, an installPath in the cache that is {name}: not in the plugin cache",
                got == f"const-alpha is not in the plugin cache at {target}",
                got,
            )

    def plugin_cache_location_cases(self, unit: Unit, texts: Texts, copies: Copies) -> None:
        """Where the plugin cache is, and what the update claim holds of an installPath and what steers it."""
        # R4 of dec-0062, R4 and R5 of dec-0071: each module stands in the plugin cache, at its manifest
        # version; an installPath is held to the platform's documented layout, resolved on both sides
        _, right_beta = copies.listed
        alpha_cache = unit.held_copy("const-alpha")
        default_root = unit.folder / "config" / "plugins"
        self.case(
            "the plugin cache's copy of a module is cache/<marketplace>/<module>/<version> under the plugins "
            "root, which is plugins in the configuration folder by default",
            alpha_cache == default_root / "cache" / TOY_MP / "const-alpha" / "0.0.1",
            str(alpha_cache),
        )
        # the run drops CLAUDE_CODE_PLUGIN_CACHE_DIR from its environment, so the plugins root is the
        # configuration folder's and `Run.cached` reads no variable, whatever the state's environment holds
        env_root = unit.folder / "env-root"
        for name, value in (("set to a folder", str(env_root)), ("set and empty", "")):
            held_by_env = unit.state(**{CACHE_ENV: value}).cached("const-alpha")
            self.case(
                "the plugins root is plugins in the configuration folder, whatever"
                f" CLAUDE_CODE_PLUGIN_CACHE_DIR the environment holds ({name})",
                held_by_env == alpha_cache,
                str(held_by_env),
            )
        got = unit.update_held([unit.plug(installPath=str(alpha_cache.parent / "0.0.0")), right_beta])
        self.case(
            "update claim, an installPath outside the cache, on the pin: the cache's fix and its reader to"
            " correct",
            got.endswith(f" | {texts.cache_fix}"),
            got,
        )
        got = unit.update_held(
            [unit.plug(installPath=str(alpha_cache.parent / "0.0.0")), right_beta], note=texts.other_note
        )
        self.case(
            "update claim, an installPath outside the cache, off the pin: the run on the pinned version, no"
            " reader to correct",
            got.endswith(f" | {texts.off_cache_fix}") and "Run.cached" not in got,
            got,
        )
        outside = alpha_cache.parent / "0.0.0"  # the right cache, another version
        other_market = default_root / "cache" / "other-mp" / "const-alpha" / "0.0.1"
        not_module = alpha_cache.parent  # the module's folder, without its version
        under = alpha_cache / "sub"
        for name, place in (
            ("in the marketplace's clone, in place", copies.wanted_clone / "modules" / "const-alpha"),
            ("in the right cache at another version", outside),
            ("in another marketplace's cache", other_market),
            ("at the module's folder, without its version", not_module),
            ("below the module's copy", under),
        ):
            place.mkdir(parents=True, exist_ok=True)
            got = unit.update_said([unit.plug(installPath=str(place)), right_beta])
            self.case(
                f"update claim, an installPath {name}: not in the plugin cache, naming where it should be",
                got == f"RED const-alpha is not in the plugin cache at {alpha_cache} but at {place}",
                got,
            )
        by_link = unit.folder / "link-to-cache"
        by_link.symlink_to(alpha_cache)
        got = unit.update_said([unit.plug(installPath=str(by_link)), right_beta])
        self.case(
            "update claim, an installPath that is a link to the cache's copy: no finding", got == "", got
        )
        got = unit.update_said([unit.plug(installPath=str(alpha_cache) + "/../0.0.1"), right_beta])
        self.case(
            "update claim, an installPath reaching the cache's copy through `..`: no finding", got == "", got
        )
        env_copies = [
            unit.plug(m, installPath=str(env_root / "cache" / TOY_MP / m / "0.0.1"))
            for m in ("const-alpha", "const-beta")
        ]
        for module in ("const-alpha", "const-beta"):
            (env_root / "cache" / TOY_MP / module / "0.0.1").mkdir(parents=True, exist_ok=True)
        # the plugins root itself may be a link: the path listed and the path built are both resolved
        real_config, linked_config = unit.folder / "config-real", unit.folder / "config-linked"
        (real_config / "plugins").mkdir(parents=True)
        linked_config.mkdir()
        (linked_config / "plugins").symlink_to(real_config / "plugins")
        real_copies = [
            unit.plug(m, installPath=str(real_config / "plugins" / "cache" / TOY_MP / m / "0.0.1"))
            for m in ("const-alpha", "const-beta")
        ]
        for module in ("const-alpha", "const-beta"):
            (real_config / "plugins" / "cache" / TOY_MP / module / "0.0.1").mkdir(parents=True)
        got = unit.update_said(real_copies, linked_config)
        self.case(
            "update claim, the plugins root a link, the installPath the real folder it leads to: no finding",
            got == "",
            got,
        )
        got = unit.update_said(copies.listed, env={CACHE_ENV: str(env_root)})
        self.case(
            "update claim, CLAUDE_CODE_PLUGIN_CACHE_DIR in the state's environment, copies under the"
            " configuration's plugins root: no finding, the variable is not followed",
            got == "",
            got,
        )
        got = unit.update_said(env_copies, env={CACHE_ENV: str(env_root)})
        self.case(
            "update claim, CLAUDE_CODE_PLUGIN_CACHE_DIR in the state's environment, copies under the"
            " variable's folder: not in the cache, the variable is not followed",
            got == f"RED const-alpha is not in the plugin cache at {alpha_cache} but at "
            f"{env_root / 'cache' / TOY_MP / 'const-alpha' / '0.0.1'}",
            got,
        )
        got = unit.update_said(env_copies)
        self.case(
            "update claim, copies under a folder the environment does not name: not in the cache",
            got == f"RED const-alpha is not in the plugin cache at {alpha_cache} but at "
            f"{env_root / 'cache' / TOY_MP / 'const-alpha' / '0.0.1'}",
            got,
        )

    def install_run_cases(self, toy: Toy, texts: Texts, green_examined: str) -> None:
        """Whole runs over the toy guide that drop a module or place one, and entries the check skips."""
        still_installed = (
            "after check=uninstall: const-alpha@toy-mp, const-beta@toy-mp still installed for the project"
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
            (
                "an uninstall that keeps the plugin installed but not enabled red, through the list",
                {},
                "uninstall-keeps-installed",
                still_installed,
            ),
            (
                "an uninstall that keeps the plugin enabled but not installed red, through the settings",
                {},
                "uninstall-keeps-enabled",
                still_installed,
            ),
            (
                "an uninstall that leaves an entry of the user scope for the project red, at any scope",
                {},
                "uninstall-leaves-user",
                still_installed,
            ),
            (
                "an uninstall that leaves an entry of the local scope for the project red, at any scope",
                {},
                "uninstall-leaves-local",
                still_installed,
            ),
            (
                "an uninstall that leaves an entry of the managed scope for the project red, at any scope",
                {},
                "uninstall-leaves-managed",
                still_installed,
            ),
            (
                "an install the platform lists for no project red",
                {},
                "install-not-listed",
                "after check=install: const-alpha is not installed for the project",
            ),
            (
                "an install the platform lists at user scope red",
                {},
                "install-at-user-scope",
                "after check=install: const-alpha is not installed for the project",
            ),
            (
                "an install the platform lists for another project red",
                {},
                "install-for-other-project",
                "after check=install: const-alpha is not installed for the project",
            ),
            (
                "an install listed at another version than the manifest's red",
                {},
                "list-wrong-version",
                "after check=install: const-alpha is installed at 9.9.9, not 0.0.1",
            ),
        ]
        for name, replace, mutant, expected in runs:
            findings, examined, _ = run_guide(
                toy_guide(**replace), toy.kit, toy.base | {"FAKE_MUTANT": mutant}
            )
            self.case(
                name,
                len(findings) == 1 and findings[0].what.startswith(expected),
                f"{whats(findings)} ({examined})",
            )
        dropped, _, _ = run_guide(toy_guide(), toy.kit, toy.base | {"FAKE_MUTANT": "update-drops"})
        self.case(
            "an update that drops a module red, naming the folder the platform lists for it",
            len(dropped) == 1
            and dropped[0].what.startswith("after check=update: const-alpha is not in the plugin cache at ")
            and dropped[0].what.endswith("/.claude/plugins/cache/toy-mp/const-alpha/0.0.1"),
            whats(dropped),
        )
        # an install the platform lists outside the plugin cache is a finding, and the cache's layout is the
        # documented one: in place, at another version, or where a block moved the plugins root to
        moves = (  # a block that sets the plugins root for the install alone
            f"export {CACHE_ENV}=$HOME/other-plugins && for m in ~/dev/constitution-kit/modules/const-*; do "
            f'claude plugin install "$(basename "$m")@{TOY_MP}" --scope project; done'
        )
        zips = moves.replace(CACHE_ENV + "=$HOME/other-plugins", "CLAUDE_CODE_PLUGIN_USE_ZIP_CACHE=1")
        placements: list[tuple[str, dict[str, str], str]] = [
            ("in the marketplace's clone, in place", {}, "install-in-place"),
            ("at another version in the right cache", {}, "install-other-version"),
            ("in a plugins root the install's block moved", {"install": moves}, ""),
            ("in a zip file the install's block asked for", {"install": zips}, ""),
        ]
        for name, replace, mutant in placements:
            elsewhere, _, _ = run_guide(toy_guide(**replace), toy.kit, toy.base | {"FAKE_MUTANT": mutant})
            self.case(
                f"an install the platform lists {name}: one finding, not in the plugin cache, naming both "
                "places, with the cache's fix",
                len(elsewhere) == 1
                and elsewhere[0].what.startswith(
                    "after check=install: const-alpha is not in the plugin cache at "
                )
                and "/.claude/plugins/cache/toy-mp/const-alpha/0.0.1 but at /" in elsewhere[0].what
                and elsewhere[0].fix == texts.cache_fix,
                " | ".join(f"{f.what} / {f.fix}" for f in elsewhere),
            )
        # the decoys: entries the check must not take, first and last, and the run green
        for mutant in (
            "list-user-first",
            "list-user-last",
            "list-other-project-first",
            "list-other-project-last",
            "mkt-other-first",
            "mkt-other-last",
        ):
            decoyed, decoyed_examined, _ = run_guide(toy_guide(), toy.kit, toy.base | {"FAKE_MUTANT": mutant})
            self.case(
                f"{mutant}: an entry that is not the module's, or the marketplace's, is skipped",
                not decoyed and decoyed_examined == green_examined,
                f"{whats(decoyed)} ({decoyed_examined})",
            )

    def person_environment_cases(
        self, toy: Toy, unit: Unit, texts: Texts, person: Person, green_examined: str
    ) -> None:
        """Runs with the four variables set in the person's environment, and a block that sets one itself."""
        # none of the four variables reaches a `claude` the run starts, whichever the person sets and to what:
        # the version command, the blocks' commands and the headless session all see the four unset, the
        # platform's copies are made under the run's own configuration, and the folders the variables name
        # stay empty; CLAUDE_CODE_PLUGIN_PREFER_HTTPS, FAKE_KEEP and the seven documented ones reach every
        # command as the person set them, and CONSTITUTION_KIT_INSTALL_FROM, in `base`, is still read: the
        # run is green from its source
        for variable, (what, set_value) in person.values.items():
            for name, value in ((what, set_value), ("set and empty", "")):
                person.seen_log.unlink(missing_ok=True)
                rooted, rooted_examined, _ = run_guide(
                    toy_guide(),
                    toy.kit,
                    toy.base | toy.kept_vars | {variable: value, "FAKE_CACHE": str(person.seen_log)},
                )
                seen = (
                    person.seen_log.read_text(encoding="utf-8").splitlines()
                    if person.seen_log.exists()
                    else []
                )
                first_words = {line.split("|")[0].split()[0] for line in seen}
                self.case(
                    f"{variable} {name} in the person's environment: a green run, the whole of it, every"
                    " claude command (the version, the plugin commands, the session) run with the four"
                    " absent and CLAUDE_CODE_PLUGIN_PREFER_HTTPS, FAKE_KEEP and the seven documented ones as"
                    " set, the folders empty",
                    not rooted
                    and rooted_examined == green_examined
                    and bool(seen)
                    and all(line.endswith(texts.seen_when_removed) for line in seen)
                    and {"--version", "plugin", "-p"} <= first_words
                    and all(list(folder.iterdir()) == [] for folder in person.folders),
                    f"{whats(rooted)} ({rooted_examined}) {seen[:4]}",
                )
        # a block that exports one of the four itself has it for its own commands, and no other command
        for variable in toy.four:
            block_value = "1" if toy.four[variable] == "1" else "$HOME/block-value"
            person.seen_log.unlink(missing_ok=True)
            run_guide(
                toy_guide(
                    install=f"export {variable}={block_value} && "
                    "for m in ~/dev/constitution-kit/modules/const-*; "
                    f'do claude plugin install "$(basename "$m")@{TOY_MP}" --scope project; done'
                ),
                toy.kit,
                toy.base | toy.kept_vars | {"FAKE_CACHE": str(person.seen_log)},
            )
            seen = (
                person.seen_log.read_text(encoding="utf-8").splitlines() if person.seen_log.exists() else []
            )
            at_command = [(line.split("|")[0], line.split("|")[1:5]) for line in seen]
            slot = list(toy.four).index(variable)
            holds = [i for i, (_, fields) in enumerate(at_command) if fields[slot] != "absent"]
            installs = [i for i, (words, _) in enumerate(at_command) if words.startswith("plugin install")]
            self.case(
                f"a block that exports {variable} itself: the variable reaches the two `plugin install`"
                " commands of that block, one for each toy module, and no other claude command, and the"
                " other three reach none",
                len(installs) >= 2
                and holds == installs[:2]
                and all(f == "absent" for _, fields in at_command for i, f in enumerate(fields) if i != slot),
                " | ".join(seen[:6]),
            )

    def broken_reply_cases(self, toy: Toy, unit: Unit, texts: Texts) -> None:
        """The BROKEN lines for replies the platform gets wrong, and the guide as the commit holds it."""
        # the folders in a whole run: the marketplace list where its block ended, not in the project, the
        # plugin list in the project, and neither in the run's home folder
        run_cwd = unit.folder / "run-cwd.log"
        installing = (
            "cd ~/dev/my-project && for m in ~/dev/constitution-kit/modules/const-*; do "
            f'claude plugin install "$(basename "$m")@{TOY_MP}" --scope project; done'
        )
        away_run, _, _ = run_guide(
            toy_guide(
                marketplace="mkdir -p ~/elsewhere && cd ~/elsewhere && claude plugin marketplace add toy/kit",
                install=installing,
            ),
            toy.kit,
            toy.base | {"FAKE_CWD": str(run_cwd)},
        )
        listed_in = [line.split("|", 1) for line in run_cwd.read_text(encoding="utf-8").splitlines()]
        market_in = {where for which, where in listed_in if which == "marketplace"}
        plugins_in = {where for which, where in listed_in if which == "plugins"}
        self.case(
            "a run whose marketplace block ends outside the project: green, the marketplace list run where "
            "the block ended, the plugin list in the project",
            not away_run
            and len(market_in) == 1
            and next(iter(market_in)).endswith("/elsewhere")
            and len(plugins_in) == 1
            and next(iter(plugins_in)).endswith("/dev/my-project"),
            f"{whats(away_run)} {market_in} {plugins_in}",
        )

        def broke(mutant: str) -> str:
            """The Broken a run over the toy guide ends in with the fake doing `mutant`, or its findings."""
            try:
                found, _, _ = run_guide(toy_guide(), toy.kit, toy.base | {"FAKE_MUTANT": mutant})
            except Broken as bad:
                return str(bad)
            return f"no Broken: {whats(found)}"

        for mutant, rest in (
            (
                "mkt-not-json",
                f"{texts.mkt_command} printed no JSON ('marketplaces: none\\n': {texts.no_json})",
            ),
            ("mkt-not-list", f"{texts.mkt_command} printed a JSON dict, not a list"),
            ("mkt-two", f"{texts.mkt_command} lists 2 entries named toy-mp"),
            ("mkt-entry-not-object", f"{texts.mkt_command} lists an entry that is no object ('x')"),
            ("mkt-exit-1", f"{texts.mkt_command} exited 1 (boom)"),
            (
                "mkt-no-installLocation",
                f"{texts.mkt_command} gives no installLocation string for toy-mp (installLocation is absent)",
            ),
            (
                "mkt-installLocation-number",
                f"{texts.mkt_command} gives no installLocation string for toy-mp (installLocation is 7)",
            ),
            (
                "mkt-title-for-name",
                f"{texts.mkt_command} gives no name string for the list's entry 1 (name is absent)",
            ),
            ("mkt-no-source", f"{texts.mkt_command} gives no source string for toy-mp (source is absent)"),
            ("mkt-no-repo", f"{texts.mkt_command} gives no repo string for toy-mp (repo is absent)"),
            ("mkt-source-number", f"{texts.mkt_command} gives no source string for toy-mp (source is 7)"),
            (
                "list-not-json",
                f"{texts.listed_command} printed no JSON ('no plugins yet\\n': {texts.no_json})",
            ),
            ("list-not-list", f"{texts.listed_command} printed a JSON dict, not a list"),
            ("list-entry-not-object", f"{texts.listed_command} lists an entry that is no object ('x')"),
            ("list-exit-1", f"{texts.listed_command} exited 1 (boom)"),
            (
                "list-without-id",
                f"{texts.listed_command} gives no id string for the list's entry 1 (id is absent)",
            ),
            (
                "list-without-projectPath",
                f"{texts.listed_command} gives no projectPath string for const-alpha@toy-mp at scope project"
                " (projectPath is absent)",
            ),
            (
                "list-without-installPath",
                f"{texts.listed_command} gives no installPath string for const-alpha@toy-mp"
                " (installPath is absent)",
            ),
            (
                "list-without-version",
                f"{texts.listed_command} gives no version string for const-alpha@toy-mp (version is absent)",
            ),
            (
                "list-without-scope",
                f"{texts.listed_command} gives no scope string for const-alpha@toy-mp (scope is absent)",
            ),
            (
                "list-two-for-project",
                f"{texts.listed_command} lists 2 project-scope entries of const-alpha@toy-mp for the project",
            ),
        ):
            got = broke(mutant)
            self.case(
                f"{mutant}: a BROKEN pointing at the Claude Code version, never a finding against INSTALL.md",
                got
                == rest
                + texts.reply_fix(rest, "platform_clone" if mutant.startswith("mkt-") else "project_entries"),
                got,
            )
        got = broke("mkt-clone-gone")
        self.case(
            "mkt-clone-gone: an installLocation that is no folder is a BROKEN pointing at the Claude Code"
            " version, never a finding against INSTALL.md",
            got.startswith(f"{texts.mkt_command} names an installLocation that is no folder (/")
            and got.endswith(f"/.claude/fake-clone/toy-mp-gone){fix_of('platform_clone')}"),
            got,
        )
        got = broke("settings-corrupt-on-update")
        self.case(
            "settings.json the platform wrote as no JSON is a BROKEN at the update claim",
            got.startswith("/")
            and got.endswith(f"/.claude/settings.json is no JSON ({texts.no_json}){texts.settings_fix}"),
            got,
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
            exited, _, _ = run_guide(toy_guide(**replace), toy.kit, toy.base)
            self.case(
                f"{name} teaches its block's fix",
                len(exited) == 1 and "exited 1" in exited[0].what and exited[0].fix == fix,
                " | ".join(f"{f.what} / {f.fix}" for f in exited),
            )
        stopped, _, _ = run_guide(toy_guide(), toy.kit, toy.base | {"FAKE_MUTANT": "session-no-start"})
        self.case(
            "a session that reports no start says why, and teaches to reproduce it",
            len(stopped) == 1
            and stopped[0].what.endswith("reported no start (Error: the session could not start)")
            and stopped[0].fix.startswith("run §2 steps 1 to 3 in a project of your own, then `claude -p ok")
            and stopped[0].render().count("fix:") == 1,
            " | ".join(f"{f.what} / {f.fix}" for f in stopped),
        )
        # the init event as the headless page documents it: `plugins` an array of objects each with a `name`
        # and a `path` (both strings, not empty), one entry to a name. A fault in it is the platform's reply
        # unread, a BROKEN, never a finding against the guide; a built-in plugin, whose path is no folder,
        # is an entry like the others; the lines are typed by hand
        event = "the headless session's `system/init` event"
        for mutant, rest in (
            ("session-plugins-absent", f"{event} gives no plugins list (plugins is absent)"),
            ("session-plugins-null", f"{event} gives no plugins list (plugins is None)"),
            (
                "session-plugins-object",
                f"{event} gives no plugins list (plugins is {{'name': 'const-alpha'}})",
            ),
            ("session-plugins-string", f"{event} gives no plugins list (plugins is 'const-alpha')"),
            ("session-entry-string", f"{event} gives plugins entry 2 that is no object ('const-beta')"),
            ("session-name-absent", f"{event} gives no name string for plugins entry 1 (name is absent)"),
            ("session-name-empty", f"{event} gives no name string for plugins entry 1 (name is '')"),
            ("session-name-number", f"{event} gives no name string for plugins entry 1 (name is 7)"),
            ("session-path-absent", f"{event} gives no path string for plugins entry 2 (path is absent)"),
            ("session-path-empty", f"{event} gives no path string for plugins entry 2 (path is '')"),
            ("session-path-number", f"{event} gives no path string for plugins entry 2 (path is 7)"),
            ("session-dup-same", f"{event} gives plugins entries 1 and 3 both named 'const-alpha'"),
            ("session-dup-diff", f"{event} gives plugins entries 1 and 3 both named 'const-alpha'"),
            ("session-dup-three", f"{event} gives plugins entries 1, 3 and 4 all named 'const-alpha'"),
            ("session-dup-newline", f"{event} gives plugins entries 1 and 2 both named 'a\\nb'"),
        ):
            got = broke(mutant)
            self.case(
                f"{mutant}: a BROKEN pointing at the Claude Code version, never a finding against INSTALL.md",
                got == rest + fix_of("session_paths"),
                got,
            )
        builtin, _, _ = run_guide(toy_guide(), toy.kit, toy.base | {"FAKE_MUTANT": "session-builtin"})
        self.case(
            "a built-in plugin beside the modules in the init event: green, its path being no folder",
            not builtin,
            whats(builtin),
        )
        for mutant in ("session-second-init-malformed", "session-second-init-paths"):
            # the first init event is the one read: a second after a good first, malformed or with paths that
            # differ, is never looked at
            got = broke(mutant)
            self.case(
                f"{mutant}: the first init event is the one read, green", got == "no Broken: no finding", got
            )
        never, _, _ = run_guide(
            toy_guide(marketplace="true || claude plugin marketplace add toy/kit"), toy.kit, toy.base
        )
        self.case(
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
            # a well-formed list that holds a built-in plugin and lacks the modules: the same finding
            ("session-builtin-only", "run §2 steps 1 to 3 in a project of your own and read the Errors tab"),
        ):
            taught, _, _ = run_guide(toy_guide(), toy.kit, toy.base | {"FAKE_MUTANT": mutant})
            self.case(
                f"{mutant} teaches its own fix, one fix",
                len(taught) == 1 and taught[0].fix.startswith(fix) and taught[0].render().count("fix:") == 1,
                " | ".join(f"{f.what} / {f.fix}" for f in taught),
            )
        mended, _, _ = run_guide(
            toy_guide(), toy.kit, toy.base | {"FAKE_MUTANT": "marketplace-fewer-modules"}
        )
        self.case(
            "a marketplace whose modules differ teaches to bring the branch to the clone",
            len(mended) == 1 and mended[0].fix.startswith("bring the source branch to the kit's clone"),
            " | ".join(f.fix for f in mended),
        )
        dials = toy_guide().split("Step dials:")
        moved = dials[0].replace(
            "# Toy guide\n", "# Toy guide\n\nStep dials:" + dials[1].split("Step scan:")[0], 1
        )
        early, _, _ = run_guide(moved + "Step scan:" + dials[1].split("Step scan:")[1], toy.kit, toy.base)
        self.case(
            "the dials before the project red",
            len(early) == 1 and early[0].what.startswith("the dials example comes before the project exists"),
            whats(early),
        )
        try:
            committed_guide(toy.kit, os.environ | {"GIT_TRACE": "2"})
            absent = "no Broken"
        except Broken as broken:
            absent = str(broken)
        self.case(
            "a guide not committed at HEAD is a configuration failure",
            "is not committed at HEAD" in absent,
            absent,
        )
        (toy.kit / GUIDE).write_text(toy_guide(), encoding="utf-8")
        try:
            committed_guide(toy.kit, os.environ | {"GIT_TRACE": "2"})
            unread = "no Broken"
        except Broken as broken:
            unread = str(broken)
        self.case(
            "a guide written but not committed is not read", "is not committed at HEAD" in unread, unread
        )
        run(["git", "add", GUIDE], toy.kit, toy.git)
        run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "-m", "guide"],
            toy.kit,
            toy.git,
        )
        read = committed_guide(toy.kit, os.environ | {"GIT_TRACE": "2"})  # git writes its trace to stderr
        self.case("the committed guide is read whole, standard output alone", read == toy_guide(), read[:80])

    def claude_version_cases(self, toy: Toy, texts: Texts, person: Person, versions: Versions) -> None:
        """The version the run is on: the pin, the opt-out and the person's own environment."""
        # the version check, over every answer of `claude --version`; the lines are typed by hand
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
                "BROKEN: " + texts.strict.format("2.1.286"),
                "note:" + texts.noted.format("2.1.286"),
            ),
            (
                "2.1.2820 (Claude Code)\\n",
                0,
                "BROKEN: " + texts.strict.format("2.1.2820"),
                "note:" + texts.noted.format("2.1.2820"),
            ),
            (
                "2.1.28 (Claude Code)\\n",
                0,
                "BROKEN: " + texts.strict.format("2.1.28"),
                "note:" + texts.noted.format("2.1.28"),
            ),
            (
                "2.1.286",
                0,
                "BROKEN: " + texts.strict.format("2.1.286"),
                "note:" + texts.noted.format("2.1.286"),
            ),
            ("v2.1.282\\n", 0, texts.stuck("printed no version (v2.1.282)"), None),
            ("", 0, texts.stuck("printed no version (no output)"), None),
            ("", 1, texts.stuck("exited 1 (no output)"), None),
            ("2.1.282 (Claude Code)\\n", 1, texts.stuck("exited 1 (2.1.282 (Claude Code))"), None),
            ("2.1.286 (Claude Code)\\n", 1, texts.stuck("exited 1 (2.1.286 (Claude Code))"), None),
            ("", 139, texts.stuck("exited 139 (no output)"), None),
            (
                "extra\\n2.1.282 (Claude Code)\\n",
                0,
                texts.stuck("printed no version (2.1.282 (Claude Code))"),
                None,
            ),
        ]
        for says, exits, unset_out, one_out in rows:
            at_one = unset_out if one_out is None else one_out
            seen = [
                versions.outcome(versions.says_env(says, exits, None)),
                versions.outcome(versions.says_env(says, exits, "1")),
            ]
            ran = (
                versions.logged()
            )  # the second run only: each run leaves the one line its own command logged
            self.case(
                f'`claude --version` printing "{says}" with exit {exits}: {outcome_kind(unset_out)}'
                f" with the variable unset, {outcome_kind(at_one)} with it at 1",
                seen == [unset_out, at_one] and ran == ["--version"],
                f"{seen} {ran}",
            )
        for value in ("", "0", "yes", "true", " 1", "1 ", "TRUE", "01"):
            got = versions.outcome(versions.says_env(texts.too_old, 0, value))
            self.case(
                f"CONSTITUTION_KIT_ANY_CLAUDE={value!r} is not the opt-out: the other version is BROKEN",
                got == "BROKEN: " + texts.strict.format("2.1.286"),
                got,
            )

        own_config = toy.root / "person"  # the configuration folder of the person who runs the check
        own_config.mkdir()
        (own_config / "keep").write_text("the person's own configuration\n", encoding="utf-8")
        env_log = toy.root / "env.log"
        for name, own in (
            ("the person's CLAUDE_CONFIG_DIR and DISABLE_AUTOUPDATER=0", True),
            ("neither of the two variables", False),
        ):
            env_log.unlink(missing_ok=True)
            env = versions.says_env("2.1.282 (Claude Code)\\n", 0, None) | {"FAKE_ENV": str(env_log)}
            env = {
                k: v for k, v in env.items() if own or k not in ("CLAUDE_CONFIG_DIR", "DISABLE_AUTOUPDATER")
            }
            if own:
                env |= {"CLAUDE_CONFIG_DIR": str(own_config), "DISABLE_AUTOUPDATER": "0"}
            versions.outcome(env)
            seen_env = env_log.read_text(encoding="utf-8").splitlines() if env_log.exists() else []
            config, updater, held, is_dir = (seen_env[0].split("|") + ["", "", "", ""])[:4]
            self.case(
                f"`claude --version` runs in an empty configuration folder of its own, auto-updater off,"
                f" with {name}",
                len(seen_env) == 1
                and config not in ("", str(own_config))
                and is_dir == "dir"
                and held == "0"
                and updater == "1"
                and sorted(path.name for path in own_config.iterdir()) == ["keep"],
                f"{seen_env} {sorted(path.name for path in own_config.iterdir())}",
            )

        person.seen_log.unlink(missing_ok=True)
        opted, opted_examined, opted_note = run_guide(
            toy_guide(),
            toy.kit,
            versions.says_env(texts.too_old, 0, "1")
            | toy.kept_vars
            | {variable: set_value for variable, (_, set_value) in person.values.items()}
            | {"FAKE_CACHE": str(person.seen_log)},
        )
        seen = person.seen_log.read_text(encoding="utf-8").splitlines() if person.seen_log.exists() else []
        self.case(
            "all four set in the person's environment with CONSTITUTION_KIT_ANY_CLAUDE=1 on another version:"
            " the opt-out is still read (a green run with its note), every claude command run with the four"
            " absent",
            not opted
            and opted_note == texts.noted.format("2.1.286")
            and bool(seen)
            and all(line.endswith(texts.seen_when_removed) for line in seen),
            f"{whats(opted)} ({opted_examined}) {opted_note!r} {seen[:4]}",
        )

    def whole_run_cases(self, toy: Toy, texts: Texts, versions: Versions) -> None:
        """Whole runs on another version, on a crashed claude and over unreadable replies."""
        line, kept = versions.stopped_run(versions.says_env(texts.too_old, 0, None))
        self.case(
            "a run on another version stops before the clone and any block: only --version is run",
            line == texts.strict.format("2.1.286") and kept == "" and versions.logged() == ["--version"],
            f"{line} {kept!r} {versions.logged()}",
        )
        pinless = toy_kit(toy.root / "pinless")
        (pinless / "scripts" / "claude-code.version").unlink()
        line, kept = versions.stopped_run(versions.says_env(texts.too_old, 0, "1", pinless), pinless)
        self.case(
            "a kit with no pin file is BROKEN with the reader's line, before claude is run",
            line
            == f"{pinless}/scripts/claude-code.version cannot be read (No such file or directory)"
            f"{texts.pin_fix}"
            and kept == ""
            and versions.logged() == [],
            f"{line} {kept!r} {versions.logged()}",
        )
        line, kept = versions.stopped_run(versions.says_env("", 139, "1"))
        self.case(
            "a crashed claude stops the run before the clone, with no note, the opt-out notwithstanding",
            line == texts.stuck("exited 139 (no output)").removeprefix("BROKEN: ")
            and kept == ""
            and versions.logged() == ["--version"],
            f"{line} {kept!r} {versions.logged()}",
        )
        versions.log.unlink(missing_ok=True)
        off_findings, off_examined, off_note = run_guide(
            toy_guide(), toy.kit, versions.says_env(texts.too_old, 0, "1")
        )
        self.case(
            "with the opt-out a green run on another version goes on, asks the version once, and notes both",
            not off_findings
            and off_note == texts.noted.format("2.1.286")
            and versions.logged()[0] == "--version"
            and versions.logged().count("--version") == 1
            and len(versions.logged()) > 1,
            f"{whats(off_findings)} ({off_examined}) {off_note!r} {versions.logged()[:3]}",
        )
        in_place, _, _ = run_guide(
            toy_guide(),
            toy.kit,
            versions.says_env(texts.too_old, 0, "1") | {"FAKE_MUTANT": "install-in-place"},
        )
        self.case(
            "an install listed in the marketplace's clone, on another version with the opt-out: one finding"
            " against the cache, its fix the run on the pinned version and no reader to correct",
            len(in_place) == 1
            and in_place[0].what.startswith("after check=install: const-alpha is not in the plugin cache at ")
            and in_place[0].fix == texts.off_cache_fix,
            " | ".join(f"{f.what} / {f.fix}" for f in in_place),
        )
        line, kept = versions.stopped_run(
            versions.says_env(texts.too_old, 0, "1", toy.nameless), toy.nameless
        )
        self.case(
            "a BROKEN after the version is known carries the note",
            line.endswith(
                '/marketplace.json has no "name" — fix: give the marketplace its name, at the top of'
                " the object"
            )
            and kept == texts.noted.format("2.1.286"),
            f"{line} {kept!r}",
        )
        nameless_main = toy_kit(
            toy.root / "nameless-main", {"plugins": []}
        )  # its guide committed, as main reads it
        (nameless_main / GUIDE).write_text(toy_guide(), encoding="utf-8")
        run(["git", "add", GUIDE], nameless_main, toy.git)
        run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "-m", "guide"],
            nameless_main,
            toy.git,
        )

        stop = "BROKEN: the check could not run — 0 blocks run"  # a failure before any block ran

        ended, lines = versions.whole_run(versions.says_env(texts.too_old, 0, None))
        self.case(
            "a whole run on another version prints the two BROKEN lines, and runs no other claude command",
            ended == EXIT_BROKEN
            and lines == ["BROKEN: " + texts.strict.format("2.1.286"), stop]
            and versions.logged() == ["--version"],
            f"{ended} {lines} {versions.logged()}",
        )
        ended, lines = versions.whole_run(
            versions.says_env(texts.too_old, 0, "1", nameless_main), nameless_main
        )
        self.case(
            "a whole run with the opt-out ends each BROKEN line it prints with the note",
            ended == EXIT_BROKEN
            and len(lines) == 2
            and lines[0].endswith(
                '/dev/constitution-kit/.claude-plugin/marketplace.json has no "name"'
                " — fix: give the marketplace its name, at the top of the object"
                + texts.noted.format("2.1.286")
            )
            and lines[1] == stop + texts.noted.format("2.1.286"),
            f"{ended} {lines}",
        )
        ended, lines = versions.whole_run(versions.says_env("", 139, "1"))
        self.case(
            "a whole run on a crashed claude prints no note, the opt-out notwithstanding",
            ended == EXIT_BROKEN
            and lines == [texts.stuck("exited 139 (no output)"), stop]
            and versions.logged() == ["--version"],
            f"{ended} {lines} {versions.logged()}",
        )
        for shape, manifest_text, said_tail in (  # a manifest of a module, committed, over the whole run
            (
                "a list",
                "[]",
                "/modules/const-alpha/.claude-plugin/plugin.json is no JSON object, it holds a list"
                " — fix: restore it as a JSON object",
            ),
            (
                "a string",
                '"const-alpha"',
                "/modules/const-alpha/.claude-plugin/plugin.json is no JSON object, it holds a str"
                " — fix: restore it as a JSON object",
            ),
            (
                "an object with no version",
                "{}",
                "/modules/const-alpha/.claude-plugin/plugin.json gives no version ('version')"
                " — fix: restore the module's manifest",
            ),
        ):
            odd_kit = toy_kit(toy.root / f"manifest-{shape.replace(' ', '-')}")
            (odd_kit / GUIDE).write_text(toy_guide(), encoding="utf-8")
            (odd_kit / "modules" / "const-alpha" / ".claude-plugin" / "plugin.json").write_text(
                manifest_text, encoding="utf-8"
            )
            run(["git", "add", "-A"], odd_kit, toy.git)
            run(
                ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "-m", "odd"],
                odd_kit,
                toy.git,
            )
            try:
                ended, lines = versions.whole_run(toy.base | {"FAKE_SOURCE": str(odd_kit)}, odd_kit)
            except TypeError as crash:  # a traceback is a case that fails, not the run
                ended, lines = -1, [f"{type(crash).__name__}: {crash}"]
            self.case(
                f"a whole run over a manifest that is {shape} prints the BROKEN line and the could-not-run"
                " line, exit 1, after the clone and the marketplace's name",
                ended == EXIT_BROKEN
                and len(lines) == 2
                and lines[0].startswith("BROKEN: ")
                and lines[0].endswith(said_tail)
                and lines[1] == stop,
                f"{ended} {lines}",
            )
        unreadable_head = f"{texts.listed_command} printed no JSON ('no plugins yet\\n': {texts.no_json})"
        ended, lines = versions.whole_run(
            versions.says_env(texts.too_old, 0, "1") | {"FAKE_MUTANT": "list-not-json"}
        )
        self.case(
            "a whole run on a reply of the wrong shape off the pin prints the two BROKEN lines, the note at"
            " the end of each",
            ended == EXIT_BROKEN
            and lines
            == [
                "BROKEN: " + unreadable_head + texts.off_fix + texts.noted.format("2.1.286"),
                texts.stop_after(3)
                + texts.noted.format("2.1.286"),  # new-repo, marketplace and install had run
            ],
            f"{ended} {lines}",
        )
        ended, lines = versions.whole_run(toy.base | {"FAKE_MUTANT": "list-not-json"})
        self.case(
            "a whole run on a reply of the wrong shape on the pin prints the two BROKEN lines, no note, the"
            " second counting the three blocks that ran",
            ended == EXIT_BROKEN
            and lines == ["BROKEN: " + unreadable_head + fix_of("listed"), texts.stop_after(3)],
            f"{ended} {lines}",
        )
        unreadable_event = (  # the init event's, typed by hand
            "the headless session's `system/init` event gives no path string for plugins entry 2 (path is 7)"
        )
        ended, lines = versions.whole_run(
            versions.says_env(texts.too_old, 0, "1") | {"FAKE_MUTANT": "session-path-number"}
        )
        self.case(
            "a whole run on an init event of the wrong shape off the pin prints the two BROKEN lines, the"
            " note at the end of each, the fix the run on the pinned version",
            ended == EXIT_BROKEN
            and lines
            == [
                "BROKEN: " + unreadable_event + texts.off_fix + texts.noted.format("2.1.286"),
                texts.stop_after(3) + texts.noted.format("2.1.286"),
            ],
            f"{ended} {lines}",
        )
        ended, lines = versions.whole_run(toy.base | {"FAKE_MUTANT": "session-path-number"})
        self.case(
            "a whole run on an init event of the wrong shape on the pin prints the two BROKEN lines, no note,"
            " the second counting the three blocks that ran",
            ended == EXIT_BROKEN
            and lines == ["BROKEN: " + unreadable_event + fix_of("session_paths"), texts.stop_after(3)],
            f"{ended} {lines}",
        )
        ended, lines = versions.whole_run(toy.base | {"FAKE_MUTANT": "settings-corrupt-on-update"})
        self.case(
            "a whole run on a settings file the update left as no JSON prints the two BROKEN lines, the"
            " second counting the seven blocks that ran, the update's the last",
            ended == EXIT_BROKEN
            and len(lines) == 2
            and lines[0].endswith(f"/.claude/settings.json is no JSON ({texts.no_json}){texts.settings_fix}")
            and lines[1] == texts.stop_after(7),
            f"{ended} {lines}",
        )
        ended, lines = versions.whole_run(
            versions.says_env(texts.too_old, 0, "1") | {"FAKE_MUTANT": "settings-corrupt-on-update"}
        )
        self.case(
            "the same off the pin: the note ends the second line after the count",
            ended == EXIT_BROKEN
            and len(lines) == 2
            and lines[1] == texts.stop_after(7) + texts.noted.format("2.1.286"),
            f"{ended} {lines}",
        )
        green_line = (
            "GREEN: the install guide runs and does what it says"
            " — 9 block(s) run, 2 module(s), from toy/kit#main"
        )
        for name, env, note_wanted in (
            ("off the pin", versions.says_env(texts.too_old, 0, "1"), texts.noted.format("2.1.286")),
            ("on the pin", toy.base, ""),
        ):
            ended, lines = versions.whole_run(env)
            self.case(
                f"a whole green run {name} prints one GREEN line, the note at the end of it",
                ended == EXIT_GREEN and lines == [green_line + note_wanted],
                f"{ended} {lines}",
            )

    def run_finding_cases(self, toy: Toy, texts: Texts, versions: Versions) -> None:
        """Whole runs that end in a finding, and in a file the run cannot read."""
        red_main = toy_kit(toy.root / "red-main")  # its guide committed, with a block that exits 1
        (red_main / GUIDE).write_text(toy_guide(scan="false"), encoding="utf-8")
        run(["git", "add", GUIDE], red_main, toy.git)
        run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "-m", "guide"],
            red_main,
            toy.git,
        )
        scan_line = toy_guide(scan="false").splitlines().index("```bash check=scan") + 1
        for name, env, note_wanted in (
            (
                "off the pin",
                versions.says_env(texts.too_old, 0, "1", red_main),
                texts.noted.format("2.1.286"),
            ),
            ("on the pin", toy.base | {"FAKE_SOURCE": str(red_main)}, ""),
        ):
            ended, lines = versions.whole_run(env, red_main)
            self.case(
                f"a whole run {name} to a finding prints the RED lines, the note at the end of each headline",
                ended == EXIT_RED
                and lines
                == [
                    f"RED: INSTALL.md:{scan_line}: the block named check=scan exited 1 — no output"
                    + note_wanted,
                    f"  why: {WHY}",
                    "  fix: make the block named check=scan do what the guide says it does,"
                    " or correct the guide and the check",
                    f"RED: 1 finding(s) — 5 block(s) run{note_wanted}",
                ],
                f"{ended} {lines}",
            )

        def unreadable_run(env: dict[str, str]) -> tuple[int, list[str]]:
            """The lines `main` prints when the blocks' run meets a file it cannot read."""

            def refuses(*args: object, **kwargs: object) -> object:
                raise PermissionError(13, "Permission denied", "/the/file")

            with mock.patch.dict(globals(), {"run_blocks": refuses}):
                return versions.whole_run(env)

        unreadable_wanted = (  # typed by hand
            "BROKEN: a file could not be read or written ([Errno 13] Permission denied: '/the/file')"
            " — fix: make the kit's files readable and the system's temporary folder writable{}",
            "BROKEN: the check could not run — 0 blocks run{}",
        )
        for name, env, note_wanted in (
            ("off the pin", versions.says_env(texts.too_old, 0, "1"), texts.noted.format("2.1.286")),
            ("on the pin", toy.base, ""),
        ):
            ended, lines = unreadable_run(env)
            self.case(
                f"a file the blocks' run cannot read, {name}: the two BROKEN lines, the note at each end",
                ended == EXIT_BROKEN and lines == [line.format(note_wanted) for line in unreadable_wanted],
                f"{ended} {lines}",
            )

        real_claim = claim

        def unreadable_claim(state: Run, block: str) -> str:
            """A claim that reads a file it cannot at the install block, the others as they are."""
            if block == "install":
                raise PermissionError(13, "Permission denied", "/the/file")
            return real_claim(state, block)

        for name, env, note_wanted in (
            ("off the pin", versions.says_env(texts.too_old, 0, "1"), texts.noted.format("2.1.286")),
            ("on the pin", toy.base, ""),
        ):
            # the case above mocks run_blocks whole, so it cannot reach an OSError after blocks have run
            with mock.patch.dict(globals(), {"claim": unreadable_claim}):
                ended, lines = versions.whole_run(env)
            self.case(
                f"a file a claim cannot read after three blocks ran, {name}: the two BROKEN lines, the second"
                " counting the three, the note at each end",
                ended == EXIT_BROKEN
                and lines
                == [
                    unreadable_wanted[0].format(note_wanted),
                    texts.stop_after(3) + note_wanted,
                ],
                f"{ended} {lines}",
            )

    def clone_and_source_cases(self, toy: Toy) -> None:
        """Folders that are no clone, the carried credentials, and the source the marketplace block takes."""
        try:
            committed_guide(toy.root / "bin", os.environ | {"GIT_CEILING_DIRECTORIES": str(toy.root)})
            bare = "no Broken"
        except Broken as broken:
            bare = str(broken)
        self.case(
            "a folder that is no clone is a configuration failure",
            "is no git clone with a commit" in bare,
            bare,
        )
        no_clone = toy.root / "no-clone"  # holds the pin, which is asked before the clone, and no git history
        (no_clone / "scripts").mkdir(parents=True)
        (no_clone / "scripts" / "claude-code.version").write_text(TOY_PIN + "\n", encoding="utf-8")
        try:
            run_guide(toy_guide(), no_clone, toy.base | {"GIT_CEILING_DIRECTORIES": str(toy.root)})
            unrun = "no Broken"
        except Broken as broken:
            unrun = str(broken)
        self.case(
            "a run from a folder that is no clone is a configuration failure",
            "is no git clone (" in unrun,
            unrun,
        )
        traced, examined, _ = run_guide(toy_guide(), toy.kit, toy.base | {"GIT_TRACE": "2"})
        self.case(
            "a run whose git writes a trace to stderr green", not traced, f"{whats(traced)} ({examined})"
        )
        _, status = run(["git", "status", "--porcelain"], toy.kit, toy.git, joined=False)
        self.case("the toy kit is left as it was: the run works on a clone", not status, status)
        sourceless, _, _ = run_guide(
            toy_guide(marketplace="claude plugin marketplace list"), toy.kit, toy.base
        )
        self.case(
            "a marketplace block with no source to point red",
            len(sourceless) == 1 and "runs no `claude plugin marketplace add <source>`" in sourceless[0].what,
            whats(sourceless),
        )
        outer = toy.root / "outer.gitconfig"  # gh's helpers, the forms a hand-written file breaks, an alias
        (toy.root / "more.gitconfig").write_text('[credential]\n\tusername = "José"\n', encoding="utf-8")
        outer.write_text(
            '[credential "https://github.com"]\n\thelper =\n\thelper = !gh auth git-credential\n'
            '[credential "https://x y"]\n\thelper = "a \\"quoted\\" \\\\ value"\n'
            '[credential]\n\tuseHttpPath\n\tmultiline = "one\\ntwo"\n'
            f"[include]\n\tpath = {toy.root / 'more.gitconfig'}\n"
            "[alias]\n\tco = checkout\n",
            encoding="utf-8",
        )
        carried = toy.root / "carried.gitconfig"
        carried.write_text("", encoding="utf-8")
        carry_credentials(toy.git | {"GIT_CONFIG_GLOBAL": str(outer)}, carried)
        want = ["config", "--includes", "-z", "--get-regexp", r"^credential\."]
        had = run(["git", *want[:1], "--file", str(outer), *want[1:]], toy.root, toy.git, joined=False)[1]
        got = run(["git", *want[:1], "--file", str(carried), *want[1:]], toy.root, toy.git, joined=False)[1]
        self.case(
            "the outer credential settings carried as git reads them, includes followed, nothing else",
            got == had.replace("credential.usehttppath\0", "credential.usehttppath\ntrue\0")
            and "alias" not in carried.read_text(encoding="utf-8"),
            f"{had!r} / {got!r}",
        )
        helped = toy.base | {"GIT_CONFIG_GLOBAL": str(outer), "FAKE_NEEDS_HELPER": "1"}
        wired, examined, _ = run_guide(toy_guide(), toy.kit, helped)
        self.case("the carried helper reaches the run's git", not wired, f"{whats(wired)} ({examined})")
        given = source_of(toy.kit, toy.git | {FROM_ENV: "owner/repo#work/x"})
        self.case("the source taken from the environment", given == "owner/repo#work/x", given)
        try:
            source_of(toy.kit, {k: v for k, v in toy.git.items() if k != FROM_ENV})
            originless = "no Broken"
        except Broken as broken:
            originless = str(broken)
        self.case(
            "a kit with no origin on GitHub is a configuration failure",
            originless.startswith("the kit has no origin on GitHub to install from — fix:"),
            originless,
        )
        originals = {k: v for k, v in toy.git.items() if k != FROM_ENV}
        remote = toy.root / "github.com" / "toy" / "kit.git"  # a local origin whose URL reads as GitHub's
        run(["git", "clone", "--quiet", "--bare", str(toy.kit), str(remote)], toy.root, originals)
        run(["git", "remote", "add", "origin", str(remote)], toy.kit, originals)
        branch = run(["git", "symbolic-ref", "--short", "HEAD"], toy.kit, originals, joined=False)[1]
        found = source_of(toy.kit, originals)
        self.case("the source taken from origin at the branch's HEAD", found == f"toy/kit#{branch}", found)

        def refused(argv: list[str]) -> str:
            run(argv, toy.kit, originals)
            try:
                return f"no Broken: {source_of(toy.kit, originals)}"
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
        self.case(
            "an origin behind HEAD is a configuration failure",
            behind.startswith(f"origin's {branch} is not at HEAD, so the install would not come from"),
            behind,
        )
        detached = refused(["git", "checkout", "--quiet", "--detach"])
        self.case(
            "a detached HEAD is a configuration failure",
            detached.startswith("HEAD is detached, so no branch to install from — fix:"),
            detached,
        )

    def report_cases(self) -> None:
        """The report: its literal text for one finding, for a run off the pin and for a green run."""
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
        self.case(
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
        self.case(
            "the report of a run off the pin ends each headline line with the note",
            code == EXIT_RED and printed.getvalue() == literal,
            printed.getvalue(),
        )
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = report([], "9 block(s) run, 2 module(s), from toy/kit#main", off_pin)
            plain_code = report([], "9 block(s) run, 2 module(s), from toy/kit#main")
        literal = (  # typed by hand
            "GREEN: the install guide runs and does what it says — 9 block(s) run, 2 module(s),"
            " from toy/kit#main"
            " [claude 2.1.286, not the pinned 2.1.282: CONSTITUTION_KIT_ANY_CLAUDE=1]\n"
            "GREEN: the install guide runs and does what it says — 9 block(s) run, 2 module(s),"
            " from toy/kit#main\n"
        )
        self.case(
            "the green report ends with the note off the pin, and with none on it",
            code == plain_code == EXIT_GREEN and printed.getvalue() == literal,
            printed.getvalue(),
        )

    def fixture_cases(self) -> None:
        """The reader's hand-written files: record #1 is placed under its catalog's folder territory, and a
        dials example whose first catalog has no folder territory is refused."""
        no_home = (  # typed by hand
            "the dials example lists no catalog with a folder territory, so record #1 has no home — fix:"
            " correct the guide's check=dials block"
        )

        def catalog(territory: str) -> str:
            return yaml.safe_dump(
                {"const-catalogs": {"catalogs": [{"prefix": "dec", "territory": [territory]}]}}
            )

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "folder"
            folder.mkdir()
            fixture(folder, catalog("docs/decisions/**"))
            placed = (folder / "docs" / "decisions" / f"dec-0001-{RECORD_SLUG}.md").is_file()
            self.case(
                "record #1 is written under its catalog's folder territory", placed, f"placed: {placed}"
            )
            file_pattern = Path(tmp) / "file-pattern"
            file_pattern.mkdir()
            try:
                fixture(file_pattern, catalog("docs/*.md"))
                said = "nothing raised"
            except Broken as refused:
                said = str(refused)
            self.case(
                "a first catalog whose territory is no folder is refused, record #1 having no home",
                said == no_home,
                said,
            )

    def run(self) -> int:
        """Run every group in order, print the tally, and give the exit code."""
        texts = typed_texts()
        self.mark_cases()
        self.listing_cases(texts)
        self.guide_run_cases(texts)
        self.report_cases()
        self.fixture_cases()
        print(f"{self.total - self.failed}/{self.total} cases green")
        return EXIT_GREEN if self.failed == 0 else EXIT_RED


def self_test() -> int:
    return SelfTestRun().run()


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
        print(broken.stop())
        return EXIT_BROKEN
    except OSError as bad:
        print(f"BROKEN: {unreadable_said(bad)}")
        print("BROKEN: the check could not run — 0 blocks run")
        return EXIT_BROKEN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
