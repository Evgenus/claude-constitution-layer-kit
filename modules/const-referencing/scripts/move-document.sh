#!/bin/sh
# const-referencing: POSIX entry point of the mover — it moves a document and repairs the links. Reads no YAML.
# Finds python3, then hands stdin and arguments to the Python entry point, which checks
# the interpreter floor. A missing or too-old interpreter is a configuration failure:
# exit 1 with the fix on the first line, never a silent pass. (Declared libraries are
# preflighted by the Python side, from the plugin's requirements file.)
here=$(dirname "$0")
if ! command -v python3 >/dev/null 2>&1; then
  echo "BROKEN: const-referencing needs python3 — fix: install Python 3.12 or newer (https://www.python.org/downloads/)" >&2
  echo "BROKEN: the move could not run — nothing was changed" >&2
  exit 1
fi
exec python3 "$here/move-document.py" "$@"
