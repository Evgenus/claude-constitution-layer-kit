#!/bin/sh
# const-interaction: POSIX entry point of session-start. Reads no YAML. Finds python3, then hands stdin
# and arguments to the Python entry point, which checks the interpreter floor. A missing or
# too-old interpreter is a configuration failure: exit 1 with the fix on the first line, never
# a silent pass. (Declared libraries are preflighted by the Python side.)
here=$(dirname "$0")
cat "$here/rules.txt"
if ! command -v python3 >/dev/null 2>&1; then
  echo "BROKEN: const-interaction needs python3 — fix: install Python 3.12 or newer (https://www.python.org/downloads/) — until then the gate's state is not said at session start" >&2
  echo "BROKEN: the session-start line could not be printed — the gate's state is unknown" >&2
  exit 1
fi
exec python3 "$here/session-start.py" "$@"
