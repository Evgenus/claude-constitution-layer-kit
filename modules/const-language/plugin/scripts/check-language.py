#!/usr/bin/env python3
"""const-language: the prose gate — a readability-grade ceiling, a sentence-length limit and the
constructions plain language avoids, checked by Vale over the covered documents. Entry point.

Events:   PostToolUse on Write and Edit (the plugin's wiring): the document as it is on disk after
          the write. A PreToolUse payload is judged the same way on the document the write would
          produce, should a consumer wire it there. Any other event is a configuration failure.
Modes:    (hook)          one tool event, JSON on stdin — the written document, when the dial
                          `territories` covers it, is prepared (the envelope, and every Vale comment
                          outside a fence or a code span, blanked with line numbers kept) and
                          checked by Vale with a configuration generated from the dials; a rule at
                          level error is a finding, at warning a note, off unwritten; a Vale comment
                          outside a fence or a code span is a finding of its own.
          --scan [DIR]    every covered Markdown file git lists in the repository containing DIR
                          (default: the current directory), the same way, one Vale run.
Reads:    from the event: hook_event_name, tool_name, tool_input.file_path, .content, .old_string,
          .new_string and .replace_all, cwd, session_id. From constitution.yaml: this module's dials
          const-language.severity, .log_dir, .territories, .grade_ceiling, .sentence_words, .levels,
          .forbidden, .simpler and .exceptions; the file as a whole is validated as every gate does.
          No policy is read; no envelope is judged. The vale binary on PATH, 3.23.0 or newer, is required.
Exit:     0 green, or nothing to examine (the count line says which);
          2 finding — a document is over the ceiling or the limit, holds a construction the rules
            name at level error, or a Vale comment outside a fence or a code span;
          1 configuration failure — the checker could not run: a missing or old vale among them.
          Never a silent pass.
Output:   stdout for green and notes — after a write with notes, one JSON object and nothing
          else, the notes and the green line in its additionalContext; a block verdict on stderr;
          warn as one JSON object on stdout; configuration failures (BROKEN) on stderr. Every print
          is also appended, as one record, to the output log — under log_dir when set, else under
          the directory the platform names in the environment variable CLAUDE_PLUGIN_DATA, else
          nowhere.

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
    "BROKEN: const-language needs Python %d.%d or newer, found %d.%d — fix: install a"
    " current Python 3 (https://www.python.org/downloads/) and put it first on PATH"
    " — until then Markdown writes pass unchecked\n"
    "BROKEN: the check could not run — 0 documents examined\n"
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
    "BROKEN: const-language needs the Python package constitution-layer-kit %s or a later %s.x release,"
    " and python3 cannot import it — fix: install it for python3 as %s says"
    " — until then Markdown writes pass unchecked\n"
    "BROKEN: the check could not run — 0 documents examined\n"
)

try:
    from constitution_layer_kit import cli  # noqa: E402  (after the floor check)
except ImportError:
    shown = GUIDE.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
    sys.stderr.write(NO_SHARED_CODE % (REQUIRES, REQUIRES.partition(".")[0], shown))  # noqa: UP031
    sys.exit(1)

# The release installed must serve this entry file, whatever it is: one older or newer than the one it
# was written for.
failure = cli.version_failure("const-language", REQUIRES, GUIDE, "until then Markdown writes pass unchecked")
if failure is not None:
    sys.stderr.write(failure + "\n" + NO_SHARED_CODE.partition("\n")[2])
    sys.exit(1)

from language_gate import start  # noqa: E402

if __name__ == "__main__":
    sys.exit(start.main(sys.argv[1:]))
