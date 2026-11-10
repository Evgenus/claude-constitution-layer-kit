#!/usr/bin/env python3
"""const-change-cost: the start hook. Entry point. Advisory: it logs and prints, and blocks nothing.

Events:   SessionStart, every source — startup, resume, clear, compact, fork (hook mode); no other.
Modes:    no arguments  read one SessionStart event on stdin, append the session's start to the start log,
          and print the start line while a hook of the commit log is missing from git's configuration.
Reads:    from the event: session_id, source, transcript_path and cwd; from git, within 3 s each: the
          common directory and the two hooks' keys. It reads no dials file: the module has no dials.
Writes:   one line, the session, the time in milliseconds by this script's own clock, the source and the
          transcript's path, to starts.jsonl in the folder const-change-cost/ of the clone's git common
          directory, making the folder where it is missing. It never writes git's configuration: only
          setup-commit-log.sh, run by a person, does. Outside a git repository it writes and prints nothing.
Exit:     0 logged, or nothing to log; 1 a configuration failure — the start could not be logged, said on
          stderr and in the log. Never 2: it has no finding.
Output:   the start line on stdout, which the platform adds to the model's context, only while a hook of the
          commit log is missing; BROKEN lines on stderr. Every print is also appended, as one record, to the
          output log, under CLAUDE_PLUGIN_DATA, else nowhere. The dials: none.

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
    "BROKEN: const-change-cost needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    " — until then no session's start is logged, and its commits get no count\n"
    "BROKEN: const-change-cost could not log this session's start — its commits will get no count\n"
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
    "BROKEN: const-change-cost needs the Python package constitution-layer-kit %s or a later %s.x release,"
    " and python3 cannot import it — fix: install it for python3 as %s says"
    " — until then no session's start is logged, and its commits get no count\n"
    "BROKEN: const-change-cost could not log this session's start — its commits will get no count\n"
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
    "const-change-cost",
    REQUIRES,
    GUIDE,
    "until then no session's start is logged, and its commits get no count",
)
if failure is not None:
    sys.stderr.write(failure + "\n" + NO_SHARED_CODE.partition("\n")[2])
    sys.exit(1)

from change_cost_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.start_main(sys.argv[1:]))
