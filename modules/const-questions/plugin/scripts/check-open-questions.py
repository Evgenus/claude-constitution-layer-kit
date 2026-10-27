#!/usr/bin/env python3
"""const-questions: the gate on open-question markers in delivered documents. Entry point.

Events:   PreToolUse on Write and Edit (hook mode); none (scan mode).
Modes:    no arguments  read one event on stdin, reconstruct the document as it will be after
                        the write, and judge it when the module's territories cover it — a line
                        carrying a marker blocks the write;
          --scan [DIR]  judge every covered document of the repository containing DIR (default:
                        the current directory) — the check for CI and before a merge.
Reads:    from the event: hook_event_name, tool_name, tool_input.file_path, .content, .old_string,
          .new_string, .replace_all, cwd, session_id. From constitution.yaml: this module's dials
          const-questions.territories (path patterns; default every Markdown file),
          .markers (the marker texts; default '[decide:', 'TODO', 'TBD', 'FIXME'),
          .severity (block | warn) and .log_dir; .preferences and .boundary_examples are the
          skill's, refused by name only and read by nobody here; the file as a whole is validated
          as every gate does. No policy is read.
The check: outside fenced code blocks and code spans, no line of a covered document carries a
          marker: a marker that begins or ends with a word character must stand at a word
          boundary there, and the match is case-sensitive. A marker inside code is a quotation.
          A deferred question written in prose carries no marker and is not seen.
Exit:     0 green, or nothing to examine (the count line says which);
          2 finding — in hook mode this blocks the write; with severity warn exit 0 with JSON
            carrying the finding to the model and the user;
          1 configuration failure — the checker could not run. Never a silent pass.
Output:   hook, block: findings on stderr; hook, warn: one JSON object on stdout and nothing
          else; scan: everything on stdout. Green and skip lines on stdout. Configuration
          failures (BROKEN) on stderr in both modes. Every print is also appended, as one
          record, to the output log — under log_dir when set, else under the directory the
          platform names in the environment variable CLAUDE_PLUGIN_DATA, else nowhere.

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
REQUIRES = "2.0.0"  # the release of the Python package constitution-layer-kit this file needs

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-questions needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
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
    "BROKEN: const-questions needs the Python package constitution-layer-kit %s or a later %s.x release,"
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
failure = cli.version_failure("const-questions", REQUIRES, GUIDE, "until then Markdown writes pass unchecked")
if failure is not None:
    sys.stderr.write(failure + "\n" + NO_SHARED_CODE.partition("\n")[2])
    sys.exit(1)

from questions_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main(sys.argv[1:]))
