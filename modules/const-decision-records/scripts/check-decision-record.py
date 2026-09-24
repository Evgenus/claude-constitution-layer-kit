#!/usr/bin/env python3
"""const-decision-records: the write-time gate on decision records. Entry point.

Events:   PreToolUse on Write and Edit (hook mode); none (scan mode).
Modes:    no arguments  read one PreToolUse event on stdin, reconstruct the document as it
                        will be after the write, and judge it;
          --scan [DIR]  judge every decision record of the repository containing DIR
                        (default: the current directory).
Reads:    from the event: tool_name, tool_input.file_path, .content, .old_string,
          .new_string, .replace_all, cwd, session_id. From constitution.yaml: root_policy,
          territory_dialect, territory of every policy namespace, and this module's dials
          const-decision-records.record_policies (the ids of the policies that govern
          decision records), .severity (block | warn) and .log_dir.
The check: a Markdown document governed by a record policy is a decision record, and its
          envelope carries what a record adds: type task-record, stakes process | product |
          architecture, decider a non-empty string. Stakes routine is its own finding: a
          routine call is a commit note, never a record. The rest of the envelope, and
          which policy governs a document, are not judged here. With no record policy
          named, nothing is examined, and the count line says so.
Exit:     0 green, or nothing to examine (the count line says which);
          2 finding — hook mode blocks the write, unless severity is warn: then exit 0
            with JSON carrying the finding to the model and the user;
          1 configuration failure — the checker could not run. Never a silent pass.
Output:   hook, block: findings, with any notes above them, on stderr; hook, warn: one JSON
          object on stdout and nothing else, the notes inside it; scan: everything on stdout.
          Green and skip lines, and the notes above them, on stdout. Configuration failures
          (BROKEN) on stderr in both modes. Every print is also appended, as one record, to
          the output log — under log_dir when set, else under the directory the platform
          names in the environment variable CLAUDE_PLUGIN_DATA, else nowhere.

This file stays parseable by any Python 3 so that an interpreter below the floor gets the
teaching message rather than a syntax error; the code lives in the package beside it.
"""

import sys

FLOOR = (3, 12)

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-decision-records needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    " — until then Markdown writes pass unchecked\n"
    "BROKEN: the check could not run — 0 documents examined\n"
)

if sys.version_info < FLOOR:
    sys.stderr.write(TOO_OLD % (FLOOR + tuple(sys.version_info[:2])))  # noqa: UP031
    sys.exit(1)

# The shared code is a directory beside this file. An install that dropped it must say so
# in words, not in a traceback: only the first stderr line reaches the user.
NO_SHARED_CODE = (
    "BROKEN: const-decision-records is installed without its shared code (scripts/const_gate is missing"
    " or is not a directory) — fix: install the plugin from its marketplace, or load it from a"
    " full checkout of the repository it comes from; a copy of the plugin's folder must be made"
    " with links followed (cp -RL) — until then Markdown writes pass unchecked\n"
    "BROKEN: the check could not run — 0 documents examined\n"
)

try:
    from const_gate import cli  # noqa: E402, F401  (after the floor check; an empty directory fails here too)
except ImportError:
    sys.stderr.write(NO_SHARED_CODE)
    sys.exit(1)

from decision_records_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main(sys.argv[1:]))
