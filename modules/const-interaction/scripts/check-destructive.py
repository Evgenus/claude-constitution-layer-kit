#!/usr/bin/env python3
"""const-interaction: the gate on enumerated destructive shell commands. Entry point.

Events:   PreToolUse on the Bash tool (hook mode); none (scan mode).
Modes:    no arguments  read one PreToolUse event of the Bash tool on stdin and judge its
                        command: every subcommand of it — after the shell operators, the
                        substitutions, the strings a shell is told to run, the wrappers and the
                        assignments, the program path — against the entries of the destructive
                        dial, an entry's words matching with only options between them; a match
                        asks the platform to prompt the user, with the entry's teaching text as
                        the reason;
          --scan [DIR] --command <text>
                        explain what the dial of the repository containing DIR (default: the
                        current directory) does to the command text: the findings it would
                        raise, or the green line. --scan without --command is a visible skip.
Reads:    from the event: hook_event_name, tool_name, tool_input.command, cwd, session_id.
          From constitution.yaml: this module's dials const-interaction.destructive (a list of
          {command, flags, teach, alternative}; default: the list of the module's document),
          .wrappers and .shells (the programs the reading strips and the shells whose strings it
          reads, merged with the defaults), .severity (block | warn) and .log_dir; the other dials
          of the namespace are validated and unused here; the file as a whole is validated as every
          gate does. No policy is read; no document is judged.
Exit:     0 green, or nothing to examine (the count line says which) — and also a match at
            severity block: the verdict is then one JSON object on stdout asking the platform
            to prompt the user, the finding its reason, exit 0 because the yes is the
            platform's prompt, not this process's; where no prompt can be shown the platform
            denies the call with that reason;
          2 finding in the scan — the command matches an entry;
          1 configuration failure — the checker could not run. Never a silent pass.
Output:   hook, block: one JSON object on stdout; hook, warn: one JSON object on stdout with
          the finding as context and the command let through; scan: everything on stdout.
          Green and skip lines on stdout. Configuration failures (BROKEN) on stderr in both
          modes. Every print is also appended, as one record, to the output log — under
          log_dir when set, else under the directory the platform names in the environment
          variable CLAUDE_PLUGIN_DATA, else nowhere.

This file stays parseable by any Python 3 so that an interpreter below the floor gets the
teaching message rather than a syntax error; the code lives in the package beside it.
"""

import sys

FLOOR = (3, 12)

# Percent formatting on purpose: this file must parse on any Python 3, and f-strings do not.
TOO_OLD = (
    "BROKEN: const-interaction needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    " — until then shell commands pass unchecked\n"
    "BROKEN: the check could not run — 0 documents examined\n"
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
    " with links followed (cp -RL) — until then shell commands pass unchecked\n"
    "BROKEN: the check could not run — 0 documents examined\n"
)

try:
    from const_gate import cli  # noqa: E402, F401  (after the floor check; an empty directory fails here too)
except ImportError:
    sys.stderr.write(NO_SHARED_CODE)
    sys.exit(1)

from interaction_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main(sys.argv[1:]))
