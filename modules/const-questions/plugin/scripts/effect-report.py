#!/usr/bin/env python3
"""const-questions: the effect report. Entry point.

It counts, over the sessions of the project, where the module's rules apply and whether each was applied,
bypassed or missed: a Markdown write its hook did not examine (W1), the module switched off or its dials
loosened (W2), a workaround after a red (W3), the skill skipped after a red (W4) or before a choice put in
lettered options (W5), the decision shape missed (W6), a marker on the main branch (W7), and, judged by a
fresh reader, a question priced right (W8). The shared runner reads the evidence and prints the report.

Modes:    no arguments                 print the report over the transcripts the module's log names;
          --transcripts DIR            also read the transcripts of the folder DIR;
          --since YYYY-MM-DD           keep what is at or after the date;
          --reader                     let a fresh reader judge the reader rules (a subscription login).
Exit:     0 the report is printed, whatever it counts; 1 it could not run. Never red.

This file stays parseable by any Python 3, as the gate's entry does. It states the release of the Python
package constitution-layer-kit that it needs, `REQUIRES`, and imports `cli` from the package that pip
installed for python3: when that fails, it prints the teaching line, which names the plugin's own
INSTALL.md, and the closing line, and exits 1; when `cli.version_failure` finds the installed release
below `REQUIRES` or of another major, it does the same with its line.
"""

import os
import sys

FLOOR = (3, 12)
REQUIRES = "2.1.0"  # the release of the Python package constitution-layer-kit this file needs

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-questions needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    "\n"
    "BROKEN: the report could not run — no rule counted\n"
)

if sys.version_info < FLOOR:
    sys.stderr.write(TOO_OLD % (FLOOR + tuple(sys.version_info[:2])))  # noqa: UP031
    sys.exit(1)

GUIDE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "INSTALL.md")
NO_SHARED_CODE = (
    "BROKEN: const-questions needs the Python package constitution-layer-kit %s or a later %s.x release,"
    " and python3 cannot import it — fix: install it for python3 as %s says"
    "\n"
    "BROKEN: the report could not run — no rule counted\n"
)

try:
    from constitution_layer_kit import cli  # noqa: E402  (after the floor check)
except ImportError:
    shown = GUIDE.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
    sys.stderr.write(NO_SHARED_CODE % (REQUIRES, REQUIRES.partition(".")[0], shown))  # noqa: UP031
    sys.exit(1)

failure = cli.version_failure("const-questions", REQUIRES, GUIDE, "")
if failure is not None:
    sys.stderr.write(failure + "\n" + NO_SHARED_CODE.partition("\n")[2])
    sys.exit(1)

from constitution_layer_kit import effect  # noqa: E402
from questions_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(effect.run(sys.argv[1:], start.EFFECT, start.load_rules))
