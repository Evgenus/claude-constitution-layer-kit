#!/usr/bin/env python3
"""const-locations: the grant of the plugin's own create command. Entry point of the hook.

A grant, never a gate: it judges nothing, blocks nothing and has no finding. It answers `allow` for
one command line and says nothing about any other.

Events:   PreToolUse on the shell tool (Bash), filtered by the hooks file to calls that start a
          subcommand with `sh `.
Modes:    no arguments  read one PreToolUse event on stdin; when its command is exactly
                        `sh <plugin root>/scripts/new-document.sh` followed by zero or more
                        arguments, each plain (ASCII letters, digits and _ . / : , @ + -) or in
                        single quotes with no single quote, line break, carriage return or NUL
                        inside, one space before each, answer `allow`; for any other command
                        give no answer. The plugin root is the one the platform names in the
                        environment variable CLAUDE_PLUGIN_ROOT, an absolute path of ASCII
                        letters, digits and _ . / @ + -, a trailing slash ignored; any other root
                        is matched by nothing.
Reads:    from the event: hook_event_name, tool_name, tool_input.command, session_id, transcript_path. No
          constitution.yaml and no dial: the grant does not depend on the repository it runs in.
Exit:     0 the answer was given, or the call is not this plugin's command and nothing is printed;
          1 the grant could not run — nothing is granted, and the platform asks for the call as for
            any other. Never 2: a grant has no finding.
Output:   the answer, one JSON object, on stdout; configuration failures (BROKEN) on stderr. Every
          print is also appended, as one record, to the output log under the directory the platform
          names in the environment variable CLAUDE_PLUGIN_DATA, else nowhere.

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
    "BROKEN: const-locations needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    "\n"
    "BROKEN: the command was not granted — the platform asks for it as for any other command\n"
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
    "BROKEN: the command was not granted — the platform asks for it as for any other command\n"
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
    sys.exit(start.grant_main(sys.argv[1:]))
