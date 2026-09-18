#!/usr/bin/env python3
"""const-meta-types: the write-time guard of claimed territory. Entry point.

Events:   PreToolUse on Write and Edit (hook mode); none (scan mode).
Modes:    no arguments  read one PreToolUse event on stdin, reconstruct the document as it
                        will be after the write, and judge it;
          --scan [DIR]  judge every Markdown document in claimed territory of the
                        repository containing DIR (default: the current directory).
Reads:    from the event: tool_name, tool_input.file_path, .content, .old_string,
          .new_string, .replace_all, cwd, session_id. From constitution.yaml: root_policy,
          territory_dialect, territory of every policy namespace, and this module's dials
          const-meta-types.severity (block | warn) and const-meta-types.log_dir.
The check: a Markdown document in claimed territory carries the envelope (id, type, title,
          status — valid values, id unique in the tree) and resolves to exactly one
          governing policy: by path first; by a `policy: <id>` declaration only where the
          path mapping is absent or ambiguous. Outside claimed territory nothing is checked.
Exit:     0 green, or nothing to examine (the count line says which);
          2 finding — hook mode blocks the write, unless severity is warn: then exit 0
            with JSON carrying the finding to the model and the user;
          1 configuration failure — the checker could not run. Never a silent pass.
Output:   findings on stderr (hook, block) or stdout (scan; hook warn as one JSON object);
          notes, green and skip lines on stdout; every printed line is also appended to the
          output log — under log_dir when set, else under the directory the platform names
          in the environment variable CLAUDE_PLUGIN_DATA, else nowhere.

This file stays parseable by any Python 3 so that an interpreter below the floor gets the
teaching message rather than a syntax error; the code lives in the package beside it.
"""

import sys

FLOOR = (3, 12)

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-meta-types needs Python %d.%d or newer, found %d.%d — fix: install a current"
    " Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    " — until then Markdown writes pass unchecked\n"
    "BROKEN: the check could not run — 0 documents examined\n"
)

if sys.version_info < FLOOR:
    sys.stderr.write(TOO_OLD % (FLOOR + tuple(sys.version_info[:2])))  # noqa: UP031
    sys.exit(1)

from meta_types_gate import cli  # noqa: E402  (after the floor check, by design)

if __name__ == "__main__":
    sys.exit(cli.run(sys.argv[1:]))
