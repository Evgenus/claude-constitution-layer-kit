#!/usr/bin/env python3
"""const-change-cost: the setup of the commit log. Entry point. Run by a person; advisory, a generator's.

Events:   none: a person runs it in the clone, and a session runs it only when the person asks.
Modes:    no argument  write hook.const-change-cost-commit on post-commit and hook.const-change-cost-merge
                       on post-merge into the clone's git configuration;
          --remove     remove both, and keep the logs and the counts;
          --check      say whether both stand, and exit 0 whether they do or not.
          Each hook is one whole command of git's own configuration that appends the commit's SHA, the time
          in milliseconds, CLAUDE_CODE_SESSION_ID and its event to commits.jsonl in the folder
          const-change-cost/ of the git common directory. It refuses a git older than 2.54.
Reads:    git's version and configuration, within no deadline: it runs as an act. It reads no dials file.
Writes:   the two hooks' keys, command and event, in the clone's own git configuration file, and nothing
          else into git's configuration; --remove deletes them.
Exit:     0 done, its line saying what stands; 1 a configuration failure — git too old, no git repository,
          a key git could not write, a misuse. Never 2: it has no finding.
Output:   SET, REMOVED or CHECK on stdout; BROKEN lines on stderr. Every print is also appended, as one
          record, to the output log, under CLAUDE_PLUGIN_DATA, else nowhere. The dials: none.

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
    "\n"
    "BROKEN: the setup could not run — setup-commit-log.sh --check shows what stands\n"
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
    "\n"
    "BROKEN: the setup could not run — setup-commit-log.sh --check shows what stands\n"
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
    "",
)
if failure is not None:
    sys.stderr.write(failure + "\n" + NO_SHARED_CODE.partition("\n")[2])
    sys.exit(1)

from change_cost_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.setup_main(sys.argv[1:]))
