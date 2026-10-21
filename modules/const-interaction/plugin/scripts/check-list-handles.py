#!/usr/bin/env python3
"""const-interaction: the scan of list handles. Entry point.

Events:   none — the check has no hook mode and the plugin wires it to no event; run as a hook
          it says so and exits 1.
Modes:    --scan [DIR]   every top-level bullet list of two or more items, outside fenced
                         blocks, in the covered Markdown files git lists in the repository
                         containing DIR (default: the current directory): a list whose items do
                         not all open with a handle of the handles dial is a finding naming its
                         first such item.
Reads:    from constitution.yaml: this module's dials const-interaction.territories (path
          patterns, default every Markdown file), .handles (regular expressions, default the
          forms of the module's document) and .log_dir; the other dials of the namespace are
          validated and unused here; the file as a whole is validated as every gate does. No
          policy is read; no envelope is judged.
Exit:     0 green, or nothing to examine (the count line says which);
          2 finding — a list has an item with no handle;
          1 configuration failure — the checker could not run. Never a silent pass.
Output:   everything on stdout; configuration failures (BROKEN) on stderr. Every print is also
          appended, as one record, to the output log — under log_dir when set, else under the
          directory the platform names in the environment variable CLAUDE_PLUGIN_DATA, else
          nowhere.

This file stays parseable by any Python 3 so that an interpreter below the floor gets the
teaching message rather than a syntax error; the code lives in the package beside it.
"""

import sys

FLOOR = (3, 12)

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-interaction needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    " — until then no list is scanned\n"
    "BROKEN: the check could not run — 0 documents examined\n"
)

if sys.version_info < FLOOR:
    sys.stderr.write(TOO_OLD % (FLOOR + tuple(sys.version_info[:2])))  # noqa: UP031
    sys.exit(1)

# The shared code is a directory beside this file. An install that dropped it must say so
# in words, not in a traceback: only the first stderr line reaches the user.
NO_SHARED_CODE = (
    "BROKEN: const-interaction is installed without its shared code (scripts/constitution_layer_kit is"
    " missing"
    " or is not a directory) — fix: install the plugin from its marketplace, or load it from a"
    " full checkout of the repository it comes from; a copy of the plugin's folder must be made"
    " with links followed (cp -RL) — until then no list is scanned\n"
    "BROKEN: the check could not run — 0 documents examined\n"
)

try:
    from constitution_layer_kit import (
        cli,  # noqa: E402, F401  (after the floor check; an empty directory fails here too)
    )
except ImportError:
    sys.stderr.write(NO_SHARED_CODE)
    sys.exit(1)

from interaction_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main_lists(sys.argv[1:]))
