#!/usr/bin/env python3
"""const-locations: the generator. It creates a governed document at its home. Entry point.

A generator, never a gate: it writes one file, and it refuses before writing anything.

Act:      --kind <policy id> --stem <stem> --title <text>
              [--type <meta-type>] [--segment <segment>] [--id <id>] [--dry-run]
          Derives the home from the policy's territory — <dir>/** or <dir>/**/*.md gives
          <dir>/<stem>.md; a pattern with one free segment, <dir>/*/NAME.md, gives the path
          with --segment filled and the file name the pattern fixes, --stem not taken; a
          single-path territory has no home — proves that the home lies in exactly that
          policy's territory, that nothing exists there and that no document carries the
          id, then writes the document: from the kind's template when the dials name one,
          with id, title and status as values and everything else as the template has it;
          from the envelope alone otherwise, --type saying which meta-type the kind is.
          The id is the stem, or name-<segment> for a free-segment kind — the fixed file name
          lower-cased — or --id.
          --dry-run prints the home and the template and writes nothing.
Reads:    constitution.yaml — root_policy, territory_dialect and every policy's territory,
          as every gate reads them; const-locations.templates for the template, .log_dir
          for the log. With no constitution.yaml, or no root_policy, it refuses.
Exit:     0 the document was created, or the dry run printed what a write would use;
          1 refused — every refusal is asked before anything is written — or it could
          not run. Never 2: a generator has no findings.
Output:   HOME, TEMPLATE, CREATED and the count on stdout; refusals (BROKEN) on stderr.
          Every print is also appended, as one record, to the output log.

This file stays parseable by any Python 3 so that an interpreter below the floor gets the
teaching message rather than a syntax error; the code lives in the package beside it.
"""

import sys

FLOOR = (3, 12)

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-locations needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    "\n"
    "BROKEN: the document could not be created — nothing was written\n"
)

if sys.version_info < FLOOR:
    sys.stderr.write(TOO_OLD % (FLOOR + tuple(sys.version_info[:2])))  # noqa: UP031
    sys.exit(1)

# The shared code is a directory beside this file. An install that dropped it must say so
# in words, not in a traceback: only the first stderr line reaches the user.
NO_SHARED_CODE = (
    "BROKEN: const-locations is installed without its shared code (scripts/constitution_layer_kit is missing"
    " or is not a directory) — fix: install the plugin from its marketplace, or load it from a"
    " full checkout of the repository it comes from; a copy of the plugin's folder must be made"
    " with links followed (cp -RL)\n"
    "BROKEN: the document could not be created — nothing was written\n"
)

try:
    from constitution_layer_kit import (
        cli,  # noqa: E402, F401  (after the floor check; an empty directory fails here too)
    )
except ImportError:
    sys.stderr.write(NO_SHARED_CODE)
    sys.exit(1)

from locations_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main(sys.argv[1:]))
