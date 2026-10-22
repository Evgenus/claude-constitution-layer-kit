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
    "BROKEN: const-locations needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    "\n"
    "BROKEN: the document could not be created — nothing was written\n"
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
    "BROKEN: const-locations needs the Python package constitution-layer-kit %s or a later %s.x release,"
    " and python3 cannot import it — fix: install it for python3 as %s says\n"
    "BROKEN: the document could not be created — nothing was written\n"
)

try:
    from constitution_layer_kit import cli  # noqa: E402  (after the floor check)
except ImportError:
    shown = GUIDE.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
    sys.stderr.write(NO_SHARED_CODE % (REQUIRES, REQUIRES.partition(".")[0], shown))  # noqa: UP031
    sys.exit(1)

# The release installed must serve this entry file, whatever it is: one older or newer than the one it
# was written for.
failure = cli.version_failure("const-locations", REQUIRES, GUIDE, "")
if failure is not None:
    sys.stderr.write(failure + "\n" + NO_SHARED_CODE.partition("\n")[2])
    sys.exit(1)

from locations_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main(sys.argv[1:]))
