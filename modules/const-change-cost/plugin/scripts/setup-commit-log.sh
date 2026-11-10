#!/bin/sh
# const-change-cost: POSIX entry point of the setup — it writes, removes and checks the two hooks of the commit log.
# Reads no YAML. Finds python3, then hands the arguments to the Python entry point, which checks the
# interpreter floor. A missing or too-old interpreter is a configuration failure: exit 1 with the fix on
# the first line, never a silent pass. (Declared libraries are preflighted by the Python side, from the
# plugin's requirements file.)
here=$(dirname "$0")
if ! command -v python3 >/dev/null 2>&1; then
  echo "BROKEN: const-change-cost needs python3 — fix: install Python 3.12 or newer (https://www.python.org/downloads/)" >&2
  echo "BROKEN: the setup could not run — setup-commit-log.sh --check shows what stands" >&2
  exit 1
fi
exec python3 "$here/setup-commit-log.py" "$@"
