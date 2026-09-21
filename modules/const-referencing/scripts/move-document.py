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
          refusals (BROKEN) on stderr. Every printed line is also appended to the output log.

This file stays parseable by any Python 3 so that an interpreter below the floor gets the
teaching message rather than a syntax error; the code lives in the package beside it.
"""

import sys

FLOOR = (3, 12)

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

# The shared code is a directory beside this file. An install that dropped it must say so
# in words, not in a traceback: only the first stderr line reaches the user.
NO_SHARED_CODE = (
    "BROKEN: const-referencing is installed without its shared code (scripts/const_gate is missing"
    " or is not a directory) — fix: install the plugin from its marketplace, or load it from a"
    " full checkout of the repository it comes from; a copy of the plugin's folder must be made"
    " with links followed (cp -RL)\n"
    "BROKEN: the move could not run — nothing was changed\n"
)

try:
    from const_gate import cli  # noqa: E402, F401  (after the floor check; an empty directory fails here too)
except ImportError:
    sys.stderr.write(NO_SHARED_CODE)
    sys.exit(1)

from referencing_gate import mover_start  # noqa: E402

if __name__ == "__main__":
    sys.exit(mover_start.main(sys.argv[1:]))
