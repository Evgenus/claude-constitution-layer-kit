#!/usr/bin/env python3
"""const-doc-budgets: the session-start printer. Entry point. Advisory: its output shapes context
and blocks nothing.

Events:   SessionStart, every source (hook mode); no other mode.
Modes:    no arguments  read one SessionStart event on stdin and print one line when the gate
                        examines nothing in the session's repository — no repository, no
                        constitution.yaml, an empty or absent ceilings dial — and nothing when
                        a ceiling is set.
Reads:    from the event: cwd, session_id, transcript_path. From constitution.yaml: this module's dial
          const-doc-budgets.ceilings, the whole namespace validated; the file as a whole is
          validated as every gate does.
Exit:     0 printed, or nothing to print; 1 configuration failure — the dials could not be
          read, said on stderr and in the log. Never a silent pass.
Output:   stdout, which the platform adds to the model's context; configuration failures
          (BROKEN) on stderr. Every print is also appended, as one record, to the output log —
          under log_dir when set, else under the directory the platform names in the
          environment variable CLAUDE_PLUGIN_DATA, else nowhere.

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
REQUIRES = "2.1.0"  # the release of the Python package constitution-layer-kit this file needs

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-doc-budgets needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    " — until then the gate's state is not said at session start\n"
    "BROKEN: the session-start line could not be printed — the gate's state is unknown\n"
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
    "BROKEN: const-doc-budgets needs the Python package constitution-layer-kit %s or a later %s.x release,"
    " and python3 cannot import it — fix: install it for python3 as %s says"
    " — until then the gate's state is not said at session start\n"
    "BROKEN: the session-start line could not be printed — the gate's state is unknown\n"
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
    "const-doc-budgets", REQUIRES, GUIDE, "until then the gate's state is not said at session start"
)
if failure is not None:
    sys.stderr.write(failure + "\n" + NO_SHARED_CODE.partition("\n")[2])
    sys.exit(1)

from budgets_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main_session(sys.argv[1:]))
