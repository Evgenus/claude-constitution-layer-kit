#!/usr/bin/env python3
"""const-change-cost: the count. Entry point.

Events:   SessionStart (async), Stop (async) — the hooks only start it; none of its own. A person runs it too.
Modes:    --all      count every complete window not yet counted, of every session in the clone's logs;
          --session  the same for the session CLAUDE_CODE_SESSION_ID names, and no other.
          Both run as an act: git and ccusage have no deadline here. A hook hands it no input; it reads none.
Reads:    the three logs in the folder const-change-cost/ of the clone's git common directory (the start log,
          the commit log, the file of counts); the transcripts the start log names; from the environment
          CLAUDE_CODE_SESSION_ID for --session and CLAUDE_PLUGIN_DATA, where the pinned ccusage is installed
          when the plugin root holds none. It reads no dials file: the module has no dials.
The count: per commit, the window from the session's previous commit, or its start, to the commit's time in
          milliseconds, cut from the session's own records dated at or after its earliest logged start, and
          counted by the pinned ccusage over a throwaway folder that holds that window alone. A window is
          complete once a record of the session is dated after the commit; an incomplete one waits. Each
          count is one line of the file of counts, written once and never made again. A commit whose session
          has no logged start gets no count. This file reads no token count of a transcript.
Exit:     0 done, nothing to do included, the closing line saying how many commits were counted, waited or
          never will be; 1 a configuration failure — the count could not run. Never 2: it has no finding.
          It fails open by design: an advisory count that blocks nothing and judges nothing.
Output:   the closing line and the notes on stdout; BROKEN lines on stderr. Every print is also appended, as
          one record, to the output log, under CLAUDE_PLUGIN_DATA, else nowhere. The dials: none.

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
    " — until then no commit is counted\n"
    "BROKEN: the count could not run — no commit was counted\n"
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
    " — until then no commit is counted\n"
    "BROKEN: the count could not run — no commit was counted\n"
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
    "until then no commit is counted",
)
if failure is not None:
    sys.stderr.write(failure + "\n" + NO_SHARED_CODE.partition("\n")[2])
    sys.exit(1)

from change_cost_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.count_main(sys.argv[1:]))
