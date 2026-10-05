#!/usr/bin/env python3
"""const-interaction: the session-start printer. Entry point. Advisory: its output shapes
context and blocks nothing.

Events:   SessionStart, every source (hook mode); no other mode.
Modes:    no arguments  read one SessionStart event on stdin and print, after the rules the
                        POSIX wrapper printed: the value of the verbosity dial, the default
                        where no dials file can be read; one line when the destructive-command
                        gate examines nothing in the session's repository — no repository, no
                        constitution.yaml, an empty destructive dial — then one line for each
                        default wrapper or shell the wrappers and shells dials drop or replace,
                        and the project's own boundary examples, numbered.
Reads:    from the event: cwd, session_id. From constitution.yaml: this module's dials
          const-interaction.destructive, .wrappers, .shells, .boundary_examples and .verbosity,
          the whole namespace validated;
          the file as a whole is validated as every gate does.
Exit:     0 printed, or nothing to print; 1 configuration failure — the dials could not be
          read, said on stderr and in the log. Never a silent pass.
Output:   stdout, which the platform adds to the model's context; configuration failures
          (BROKEN) on stderr. Every print is also appended, as one record, to the output log —
          under log_dir when set, else under the directory the platform names in the
          environment variable CLAUDE_PLUGIN_DATA, else nowhere.

This file stays parseable by any Python 3 so that an interpreter below the floor gets the
teaching message rather than a syntax error; the code lives in the package beside it.
"""

import sys

FLOOR = (3, 12)

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-interaction needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    " — until then the gate's state is not said at session start\n"
    "BROKEN: the session-start line could not be printed — the gate's state is unknown\n"
)

if sys.version_info < FLOOR:
    sys.stderr.write(TOO_OLD % (FLOOR + tuple(sys.version_info[:2])))  # noqa: UP031
    sys.exit(1)

# The shared code is a directory beside this file. An install that dropped it must say so
# in words, not in a traceback: only the first stderr line reaches the user.
NO_SHARED_CODE = (
    "BROKEN: const-interaction is installed without its shared code (scripts/const_gate is missing"
    " or is not a directory) — fix: install the plugin from its marketplace, or load it from a"
    " full checkout of the repository it comes from; a copy of the plugin's folder must be made"
    " with links followed (cp -RL) — until then the gate's state is not said at session start\n"
    "BROKEN: the session-start line could not be printed — the gate's state is unknown\n"
)

try:
    from const_gate import cli  # noqa: E402, F401  (after the floor check; an empty directory fails here too)
except ImportError:
    sys.stderr.write(NO_SHARED_CODE)
    sys.exit(1)

from interaction_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main_session(sys.argv[1:]))
