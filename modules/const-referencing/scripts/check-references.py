#!/usr/bin/env python3
"""const-referencing: the gate on references. Entry point.

Events:   PreToolUse on Write and Edit (hook mode); none (scan mode).
Modes:    no arguments  read one PreToolUse event on stdin, reconstruct the document as it
                        will be after the write, and judge the forms of its references;
          --scan [DIR]  judge every covered document of the repository containing DIR
                        (default: the current directory) — the check for CI on a pull request.
Reads:    from the event: tool_name, tool_input.file_path, .content, .old_string,
          .new_string, .replace_all, cwd, session_id. From constitution.yaml: this module's
          dials const-referencing.territories (path patterns; default every Markdown file),
          .bare_ids (refuse | allow), .lanes (a list of {pattern, names, fix, home}),
          .severity (block | warn) and .log_dir; the file as a whole is validated as every
          gate does. No policy is read.
The check: outside the YAML block that opens the file, code, HTML comments and links, a
          covered document cites nothing by a bare form a lane declares; a covered document's
          id does not stand in backticks outside a link; a link whose text is a covered
          document's id opens that document; and nothing names a path on one machine. The
          ids are those of the covered documents' envelopes, read at each run.
Exit:     0 green, or nothing to examine (the count line says which);
          2 finding — hook mode blocks the write, unless severity is warn: then exit 0
            with JSON carrying the finding to the model and the user;
          1 configuration failure — the checker could not run. Never a silent pass.
Output:   hook, block: findings on stderr; hook, warn: one JSON object on stdout and nothing
          else; scan: everything on stdout. Green and skip lines on stdout. Configuration
          failures (BROKEN) on stderr in both modes. Every printed line is also appended to
          the output log — under log_dir when set, else under the directory the platform
          names in the environment variable CLAUDE_PLUGIN_DATA, else nowhere.

This file stays parseable by any Python 3 so that an interpreter below the floor gets the
teaching message rather than a syntax error; the code lives in the package beside it.
"""

import sys

FLOOR = (3, 12)

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-referencing needs Python %d.%d or newer, found %d.%d — fix: install a"
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
    "BROKEN: const-referencing is installed without its shared code (scripts/const_gate is missing"
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

from referencing_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main(sys.argv[1:]))
