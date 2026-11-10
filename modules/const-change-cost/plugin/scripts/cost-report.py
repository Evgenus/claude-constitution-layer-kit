#!/usr/bin/env python3
"""const-change-cost: the report and its three exports. Entry point. Run by a person; advisory, a generator's.

Events:   none: a person runs it, and a session runs it when the person asks, before a pull request is opened
          or merged. No hook calls it.
Modes:    [<range>]          the report: with no range every kept line; with a range, such as main..HEAD, each
                             commit of the range, counted or not, in the range's order, and the total;
          --trailer <range>  one Change-Cost-Commit trailer for each counted commit, then one Change-Cost
                             trailer with the total, for the last paragraph of a merge commit's message;
          --pr <range>       the block of the pull request's description, written between its markers through
                             gh where gh finds the branch's pull request, else printed;
          --notes <range>    one git note for each counted commit under refs/notes/change-cost.
          Every figure comes from the file of counts: input, output, cache write and cache read apart, their
          total, the cost at list price ("at least" where a model has no price), the replies, the tokens of
          each model, the compactions and the unpriced models. A commit of a range with no kept line is
          named with its reason. It reads no transcript and runs no ccusage.
Reads:    the file of counts, the commit log and the start log in the folder const-change-cost/ of the git
          common directory; git's commits for the range. It reads no dials file: the module has no dials.
Writes:   --pr: the pull request's description, through gh; --notes: the notes ref in the clone. Never a file
          of the working tree, and it never pushes: the person pushes the notes ref by naming it.
Exit:     0 done, the head line or the trailers saying how many commits were counted; 1 a configuration
          failure — a range git cannot read, no repository, a write that failed, a misuse. Never 2: it has
          no finding.
Output:   the report, the trailers, the block or the notes line on stdout; BROKEN lines on stderr. Every print
          is also appended, as one record, to the output log, under CLAUDE_PLUGIN_DATA, else nowhere.
          The dials: none.

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
    "BROKEN: const-change-cost needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    "\n"
    "BROKEN: the report could not run — nothing was shown or written\n"
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
    "BROKEN: the report could not run — nothing was shown or written\n"
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
    sys.exit(start.report_main(sys.argv[1:]))
