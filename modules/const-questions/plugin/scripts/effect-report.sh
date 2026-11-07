#!/bin/sh
# const-questions: POSIX entry point of the effect report. Reads no YAML.
# Finds python3, then hands the arguments to the Python entry point, which checks the interpreter
# floor. A missing or too-old interpreter is a configuration failure: exit 1 with the fix on the first
# line, never a silent report.
here=$(dirname "$0")
if ! command -v python3 >/dev/null 2>&1; then
  echo "BROKEN: const-questions needs python3 — fix: install Python 3.12 or newer (https://www.python.org/downloads/)" >&2
  echo "BROKEN: the report could not run — no rule counted" >&2
  exit 1
fi
exec python3 "$here/effect-report.py" "$@"
