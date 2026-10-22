#!/usr/bin/env python3
"""const-meta-types: the write-time guard of claimed territory. Entry point.

Events:   PreToolUse on Write and Edit (hook mode); none (scan mode).
Modes:    no arguments  read one PreToolUse event on stdin, reconstruct the document as it
                        will be after the write, and judge it;
          --scan [DIR]  judge every Markdown document in claimed territory of the
                        repository containing DIR (default: the current directory).
Reads:    from the event: tool_name, tool_input.file_path, .content, .old_string,
          .new_string, .replace_all, cwd, session_id. From constitution.yaml: module_prefix,
          root_policy, territory_dialect, territory of every policy namespace, and this module's dials
          const-meta-types.severity (block | warn) and const-meta-types.log_dir.
The check: a Markdown document in claimed territory carries the envelope (id, type, title,
          status — valid values, id unique in the tree) and resolves to exactly one
          governing policy: by path first; by a `policy: <id>` declaration only where the
          path mapping is absent or ambiguous. Outside claimed territory nothing is checked.
Exit:     0 green, or nothing to examine (the count line says which);
          2 finding — hook mode blocks the write, unless severity is warn: then exit 0
            with JSON carrying the finding to the model and the user;
          1 configuration failure — the checker could not run. Never a silent pass.
Output:   hook, block: findings, with any notes above them, on stderr; hook, warn: one JSON
          object on stdout and nothing else, the notes inside it; scan: everything on stdout.
          Green and skip lines on stdout: in hook mode with notes, one JSON object and nothing
          else, the notes and the line in its additionalContext; otherwise the notes above the
          line, plain. Configuration failures
          (BROKEN) on stderr in both modes. Every print is also appended, as one record, to
          the output log — under log_dir when set, else under the directory the platform
          names in the environment variable CLAUDE_PLUGIN_DATA, else nowhere. A green write in
          claimed territory, the first of its session for the repository and the policy, adds one
          advisory line naming the governing policy to the JSON's additionalContext and records
          it in the memo <log name>.pointed beside the log; with no log location there is no memo
          and no line, and an event that names no session earns none either.

This file stays parseable by any Python 3 so that an interpreter below the floor gets the
teaching message rather than a syntax error. It states the release of the Python package
constitution-layer-kit that it needs, `REQUIRES`, and imports `cli` from the package that pip
installed for python3: when that fails, it prints the teaching line, which names the plugin's own
INSTALL.md, and the closing line, and exits 1; when `cli.version_failure` finds the installed release
below `REQUIRES` or of another major, it does the same with its line. Only then does it import the
package beside it, which holds the code.
"""

import os
import sys

FLOOR = (3, 12)
REQUIRES = "1.0.0"  # the release of the Python package constitution-layer-kit this file needs

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

# The shared code is the Python package constitution-layer-kit, which pip installs for python3. An
# environment without it must say so in words, not in a traceback: only the first stderr line reaches
# the user. The line names the install note of this plugin, the folder above this file's: its path is
# shown with a backslash and a line break escaped, by hand, since nothing can be imported to do it.
GUIDE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "INSTALL.md")
NO_SHARED_CODE = (
    "BROKEN: const-meta-types needs the Python package constitution-layer-kit %s or a later %s.x release,"
    " and python3 cannot import it — fix: install it for python3 as %s says"
    " — until then Markdown writes pass unchecked\n"
    "BROKEN: the check could not run — 0 documents examined\n"
)

try:
    from constitution_layer_kit import cli  # noqa: E402  (after the floor check)
except ImportError:
    shown = GUIDE.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
    sys.stderr.write(NO_SHARED_CODE % (REQUIRES, REQUIRES.partition(".")[0], shown))  # noqa: UP031
    sys.exit(1)

# The release installed must serve this entry file, whatever it is: one older or newer than the one it
# was written for.
failure = cli.version_failure(
    "const-meta-types", REQUIRES, GUIDE, "until then Markdown writes pass unchecked"
)
if failure is not None:
    sys.stderr.write(failure + "\n" + NO_SHARED_CODE.partition("\n")[2])
    sys.exit(1)

from meta_types_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main(sys.argv[1:]))
