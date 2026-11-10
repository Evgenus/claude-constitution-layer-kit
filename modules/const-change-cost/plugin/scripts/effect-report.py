#!/usr/bin/env python3
"""const-change-cost: entry point of the effect report, the count of where the module's rules applied, were
bypassed or were missed in a project that installs it.

It hands the module's rules, held by its package, to the shared runner, which reads the evidence — the
transcripts the module's output log names, and those of a folder `--transcripts` names; the project's git
history — and prints the report. The rules also read the module's own logs in the clone's git common
directory, the commit log and the file of counts.

Events:   none: it runs on demand, a person's or a session's, and is wired to no hook.
Modes:    no arguments                 print the report over the transcripts the module's log names;
          --transcripts DIR            also read the transcripts of the folder DIR;
          --since YYYY-MM-DD           keep what is at or after the date;
          --reader                     let a fresh reader judge the reader rules (a subscription login);
                                       the module has none.
Reads:    the output log under CLAUDE_PLUGIN_DATA and the transcripts it names; the transcripts of DIR; the
          project's git history; the commit log and the file of counts in the clone's git common directory;
          the plugin list that `claude` shows; the project's dials file, `constitution.yaml`, through the
          shared runner (see The dials). It reads no event on its standard input.
Exit:     0 the report is printed, whatever it counts; 1 it could not run. Never red, never 2.
Output:   the report on stdout; BROKEN lines on stderr. Every print is also appended, as one record, to the
          output log, in the folder the dial `log_dir` of the namespace const-change-cost names, when the
          dials file sets one and git ignores that folder (else the run fails with the shared C13), else under
          CLAUDE_PLUGIN_DATA, else nowhere.
The dials: the module has none of its own, but this entry alone reads the dials file, for the dial `log_dir`
          that every module's namespace takes; with no file or no `log_dir` it reads nothing more, and a file
          the shared reader finds malformed stops the report. No other entry reads the file.

This file stays parseable by any Python 3, as the gate's entry does.
"""

import os
import sys

FLOOR = (3, 12)
REQUIRES = "2.2.0"  # the release of the Python package constitution-layer-kit this file needs

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-change-cost needs Python %d.%d or newer, found %d.%d — fix: install a current"
    " Python 3 (https://www.python.org/downloads/) and put it first on PATH\n"
    "BROKEN: the report could not run — no rule counted\n"
)

if sys.version_info < FLOOR:
    sys.stderr.write(TOO_OLD % (FLOOR + tuple(sys.version_info[:2])))  # noqa: UP031
    sys.exit(1)

GUIDE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "INSTALL.md")
NO_SHARED_CODE = (
    "BROKEN: const-change-cost needs the Python package constitution-layer-kit %s or a later %s.x release,"
    " and python3 cannot import it — fix: install it for python3 as %s says\n"
    "BROKEN: the report could not run — no rule counted\n"
)

try:
    from constitution_layer_kit import cli  # noqa: E402  (after the floor check)
except ImportError:
    shown = GUIDE.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
    sys.stderr.write(NO_SHARED_CODE % (REQUIRES, REQUIRES.partition(".")[0], shown))  # noqa: UP031
    sys.exit(1)

failure = cli.version_failure("const-change-cost", REQUIRES, GUIDE, "")
if failure is not None:
    sys.stderr.write(failure + "\n" + NO_SHARED_CODE.partition("\n")[2])
    sys.exit(1)

from change_cost_gate import effect_rules, start  # noqa: E402
from constitution_layer_kit import effect  # noqa: E402

if __name__ == "__main__":
    sys.exit(effect.run(sys.argv[1:], start.EFFECT, effect_rules.rules))
