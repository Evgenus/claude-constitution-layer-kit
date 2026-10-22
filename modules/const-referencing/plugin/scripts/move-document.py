#!/usr/bin/env python3
"""const-referencing: the mover. It moves a document and repairs the links. Entry point.

A generator, never a gate: it rewrites files. The gate's entry point beside it never does.

Acts:     OLD NEW          move the file with git mv, then repair: every covered document's
                           links to it, and its own relative links, so that each reaches
                           from the new place what it reached before;
          --moved OLD NEW  the same repair after a move already made by hand;
          --ids            point every link whose text is a covered document's id at the
                           document carrying that id — a repair that needs no knowledge of
                           what moved, since the envelope says where a document is.
          Paths are given from where the command is run. A link inside code, a comment or
          the YAML block that opens a file is never rewritten; a place that names the old
          path outside a link's destination — prose, code, a script — is listed, not changed.
          Changing a document's id is not offered.
Proof:    every act ends with the gate's scan of the whole tree and exits with its verdict:
          the rewrite is an assist, and the proof that no reference is left broken is the scan.
Reads:    constitution.yaml as the gate reads it: const-referencing.territories and
          .governed_only decide the covered documents, which are the documents a move repairs;
          the closing scan reads every dial the gate reads; .log_dir places the log.
          With no constitution.yaml the proof cannot run, and the act refuses.
Exit:     0 the act was made and the whole tree is green; 2 the act was made and the scan
          reports findings; 1 the act was refused — everything that can refuse is asked before
          anything moves, so the closing line says that nothing was changed — or it stopped
          midway, and the closing line says that instead and names what to do.
Output:   MOVED, REWROTE and MENTION lines and the count on stdout, then the scan's lines;
          refusals (BROKEN) on stderr. Every print is also appended, as one record, to the
          output log.

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
    "BROKEN: const-referencing needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    "\n"
    "BROKEN: the move could not run — nothing was changed\n"
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
    "BROKEN: const-referencing needs the Python package constitution-layer-kit %s or a later %s.x release,"
    " and python3 cannot import it — fix: install it for python3 as %s says\n"
    "BROKEN: the move could not run — nothing was changed\n"
)

try:
    from constitution_layer_kit import cli  # noqa: E402  (after the floor check)
except ImportError:
    shown = GUIDE.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
    sys.stderr.write(NO_SHARED_CODE % (REQUIRES, REQUIRES.partition(".")[0], shown))  # noqa: UP031
    sys.exit(1)

# The release installed must serve this entry file, whatever it is: one older or newer than the one it
# was written for.
failure = cli.version_failure("const-referencing", REQUIRES, GUIDE, "")
if failure is not None:
    sys.stderr.write(failure + "\n" + NO_SHARED_CODE.partition("\n")[2])
    sys.exit(1)

from referencing_gate import mover_start  # noqa: E402

if __name__ == "__main__":
    sys.exit(mover_start.main(sys.argv[1:]))
