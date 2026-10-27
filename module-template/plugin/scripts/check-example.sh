#!/bin/sh
# const-<aspect-name>: POSIX entry point of the gate. Reads no YAML. Finds python3, then hands
# stdin and arguments to the Python entry point, which checks the interpreter floor and the shared
# package. A missing interpreter is a configuration failure: exit 1 with the fix on the first line,
# never a silent pass. Replace <what passes unchecked> with what the gate stops guarding, and
# check-example.py with the module's own Python entry file, which the template does not ship.
here=$(dirname "$0")
if ! command -v python3 >/dev/null 2>&1; then
  echo "BROKEN: const-<aspect-name> needs python3 — fix: install Python 3.12 or newer (https://www.python.org/downloads/) — until then <what passes unchecked>" >&2
  echo "BROKEN: the check could not run — 0 <items> examined" >&2
  exit 1
fi
exec python3 "$here/check-example.py" "$@"
