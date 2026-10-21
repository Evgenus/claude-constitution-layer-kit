#!/usr/bin/env python3
"""const-task-close: the gate on task close. Entry point.

Events:   Stop (hook mode) — the end of a turn; none (scan mode).
Modes:    no arguments  read one Stop event on stdin and judge the working tree of the
                        repository the event's cwd lies in: a dirty tree — any line of
                        git status --porcelain — is a finding on the turn's first stop;
                        on a later stop of the same turn (stop_hook_active) the turn ends;
          --scan [DIR] [--since <ref> | --change <commit>] [--body <file>]
                        judge one change of the repository containing DIR (default: the
                        current directory) against the coverage map: --since names the base
                        and the change is what the head adds since their merge-base;
                        --change names one landed commit and the change is its first-parent
                        diff; neither: the base is the trunk the dials name — the remote's
                        tracking branch when git finds the local branch its ancestor or
                        equal to it, or finds none, else the local branch — or, on the trunk
                        itself, the last landed change. --body gives the pull request's
                        description as a file, read for declarations beside the commits'
                        trailers. The check for CI on a pull request, and before a merge.
Reads:    from the event: hook_event_name, cwd, session_id, stop_hook_active. From
          constitution.yaml: this module's dials const-task-close.coverage (a list of
          {name, code, docs}), .trunk (a branch name; default main), .trunk_remote (a
          remote's name; default origin), .declaration_key (a trailer key; default
          No-Doc-Impact), .working_files (patterns), .severity (block | warn) and .log_dir; the
          file as a whole is validated as every gate does. No policy is read; no envelope is
          judged.
The check: in the scan, every pair whose code patterns match a path of the range, its own
          documents excepted, has one of its documents among the range's paths, or a
          declaration — the trailer "<key>: <pair> — <reason>" on a commit of the range, or
          the same line in the body — naming it; a declaration naming no pair, or carrying
          no reason, is a finding of its own; a document the map names must exist in the
          repository's HEAD unless the range touched it. In hook mode, the working tree is clean.
Exit:     0 green, or nothing to examine (the count line says which);
          2 finding — in hook mode this continues the turn once, the message reaching the
            model; with severity warn it is exit 0 with the finding in a systemMessage for
            the user; the scan always exits 2 on a finding;
          1 configuration failure — the checker could not run. Never a silent pass.
Output:   hook, block: findings on stderr; hook, warn: one JSON object on stdout and nothing
          else; scan: everything on stdout. Green and skip lines on stdout. Configuration
          failures (BROKEN) on stderr in both modes. Every print is also appended, as one
          record, to the output log — under log_dir when set, else under the directory the
          platform names in the environment variable CLAUDE_PLUGIN_DATA, else nowhere.

This file stays parseable by any Python 3 so that an interpreter below the floor gets the
teaching message rather than a syntax error; the code lives in the package beside it.
"""

import sys

FLOOR = (3, 12)

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-task-close needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    " — until then neither the tree at turn end nor a change's documents are checked\n"
    "BROKEN: the check could not run — 0 documents examined\n"
)

if sys.version_info < FLOOR:
    sys.stderr.write(TOO_OLD % (FLOOR + tuple(sys.version_info[:2])))  # noqa: UP031
    sys.exit(1)

# The shared code is a directory beside this file. An install that dropped it must say so
# in words, not in a traceback: only the first stderr line reaches the user.
NO_SHARED_CODE = (
    "BROKEN: const-task-close is installed without its shared code (scripts/constitution_layer_kit is missing"
    " or is not a directory) — fix: install the plugin from its marketplace, or load it from a"
    " full checkout of the repository it comes from; a copy of the plugin's folder must be made"
    " with links followed (cp -RL)"
    " — until then neither the tree at turn end nor a change's documents are checked\n"
    "BROKEN: the check could not run — 0 documents examined\n"
)

try:
    from constitution_layer_kit import (
        cli,  # noqa: E402, F401  (after the floor check; an empty directory fails here too)
    )
except ImportError:
    sys.stderr.write(NO_SHARED_CODE)
    sys.exit(1)

from task_close_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main(sys.argv[1:]))
