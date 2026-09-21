#!/usr/bin/env python3
"""const-referencing: the gate on references. Entry point.

Events:   PreToolUse and PostToolUse on Write and Edit (hook mode), told apart by the event's
          hook_event_name; none (scan mode).
Modes:    no arguments  read one event on stdin. Before the write: reconstruct the document as
                        it will be and judge the forms of its references — this can block.
                        After the write: check the whole tree and report the findings that
                        involve the written document — its own links, and other documents'
                        links into it. This cannot block: it is feedback, in the turn that
                        breaks a reference;
          --scan [DIR]  judge every covered document of the repository containing DIR
                        (default: the current directory), forms and resolution alike — the
                        check for CI on a pull request, and the gate for resolution.
Reads:    from the event: hook_event_name, tool_name, tool_input.file_path, .content, .old_string,
          .new_string, .replace_all, cwd, session_id. From constitution.yaml: this module's
          dials const-referencing.territories (path patterns; default every Markdown file),
          .governed_only (true | false; true reads the policies too, and needs root_policy),
          .mentions (a list of {pattern, files}; scan only),
          .bare_ids and .heading_anchors (refuse | allow), .lanes (a list of {pattern, names, fix, home}),
          .severity (block | warn) and .log_dir; the file as a whole is validated as every
          gate does. No policy is read unless governed_only asks for it.
The check: outside the YAML block that opens the file, code, HTML comments and links, a
          covered document cites nothing by a bare form a lane declares; a covered document's
          id does not stand in backticks outside a link; a link whose text is a covered
          document's id opens that document; and nothing names a path on one machine. In the
          whole tree every link of a covered document names a file that exists and, where it
          cites a place inside a covered document, an anchor written there — not a heading's
          generated name, unless heading_anchors allows it. Resolution is asked of lychee,
          0.24.2 or newer, which the gate finds on PATH and starts outside the repository
          with its own configuration; a missing, older or silent lychee is exit 1. The ids
          are those of the covered documents' envelopes, read at each run. In the scan, where
          mentions declares how an id looks outside Markdown, every such name in a file git
          lists — no Markdown, no link, not binary — is the id of a covered document.
Exit:     0 green, or nothing to examine (the count line says which);
          2 finding — before the write this blocks it; after the write nothing can be
            blocked, and exit 2 carries the finding to the model as an error. With severity
            warn both are exit 0 with JSON carrying the finding to the model and the user;
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
