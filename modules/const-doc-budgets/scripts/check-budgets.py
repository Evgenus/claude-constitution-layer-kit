#!/usr/bin/env python3
"""const-doc-budgets: the length gate — a character ceiling per group of documents, measured after
the fact. Entry point.

Events:   PostToolUse on Write and Edit (the plugin's wiring): the document as it is on disk after
          the write. A PreToolUse payload is judged the same way on the document the write would
          produce, should a consumer wire it there — and a finding there refuses the write. An event
          of another name carrying a write's input is a configuration failure; one that carries no
          file is a visible skip.
Modes:    (hook)          one tool event, JSON on stdin — the written document, when a ceiling of the
                          dial `ceilings` holds it, is counted in characters; over a ceiling at level
                          error it is a finding, at level warning a note; under a departure that
                          lifts its ceiling it is measured and passes.
          --scan [DIR]    every Markdown file git lists in the repository containing DIR (default:
                          the current directory) that a ceiling holds, the same way, with one note
                          per ceiling on what it holds and how close the longest document is.
          --scan [DIR] --since <YYYY-MM-DD>
                          the history report: per ceiling and per day since the date, the longest
                          document on the first-parent line of HEAD; judges nothing.
Reads:    from the event: hook_event_name, tool_name, tool_input.file_path, .content, .old_string,
          .new_string and .replace_all, cwd, session_id. From constitution.yaml: this module's dials
          const-doc-budgets.severity, .log_dir, .ceilings and .departures; the file as a whole is
          validated as every gate does. No policy is read; no envelope is judged. The report reads
          git's history.
Exit:     0 green, a report, or nothing to examine (the count line says which);
          2 finding — a document is over a ceiling at level error;
          1 configuration failure — the checker could not run: two ceilings holding one document,
            and a ceiling at level error set from fewer than 30 days of data, among them.
          Never a silent pass.
Output:   stdout for green and notes — after a write with notes, one JSON object and nothing
          else, the notes and the green line in its additionalContext; a block verdict on stderr;
          warn as one JSON object on stdout; configuration failures (BROKEN) on stderr. Every print
          is also appended, as one record, to the output log — under log_dir when set, else under
          the directory the platform names in the environment variable CLAUDE_PLUGIN_DATA, else
          nowhere.

This file stays parseable by any Python 3 so that an interpreter below the floor gets the
teaching message rather than a syntax error; the code lives in the package beside it.
"""

import sys

FLOOR = (3, 12)

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-doc-budgets needs Python %d.%d or newer, found %d.%d — fix: install a"
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
    "BROKEN: const-doc-budgets is installed without its shared code (scripts/constitution_layer_kit is"
    " missing"
    " or is not a directory) — fix: install the plugin from its marketplace, or load it from a"
    " full checkout of the repository it comes from; a copy of the plugin's folder must be made"
    " with links followed (cp -RL) — until then Markdown writes pass unchecked\n"
    "BROKEN: the check could not run — 0 documents examined\n"
)

try:
    from constitution_layer_kit import (
        cli,  # noqa: E402, F401  (after the floor check; an empty directory fails here too)
    )
except ImportError:
    sys.stderr.write(NO_SHARED_CODE)
    sys.exit(1)

from budgets_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main(sys.argv[1:]))
