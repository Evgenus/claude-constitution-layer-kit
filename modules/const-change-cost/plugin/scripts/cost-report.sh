#!/bin/sh
# const-change-cost: POSIX entry point of the report — it shows what each commit cost and writes the three exports.
# Reads no YAML. Finds python3, then hands the arguments to the Python entry point, which checks the
# interpreter floor. A missing or too-old interpreter is a configuration failure: exit 1 with the fix on
# the first line, never a silent pass. (Declared libraries are preflighted by the Python side, from the
# plugin's requirements file.)
here=$(dirname "$0")
if ! command -v python3 >/dev/null 2>&1; then
  echo "BROKEN: const-change-cost needs python3 — fix: install Python 3.12 or newer (https://www.python.org/downloads/)" >&2
  echo "BROKEN: the report could not run — nothing was shown or written" >&2
  exit 1
fi
exec python3 "$here/cost-report.py" "$@"
