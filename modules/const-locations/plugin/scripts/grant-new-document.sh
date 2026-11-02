#!/bin/sh
# const-locations: POSIX entry point of the grant — the hook that answers allow for the plugin's own create command. Reads no YAML.
# Finds python3, then hands the arguments to the Python entry point, which checks the
# interpreter floor. A missing or too-old interpreter is a configuration failure: exit 1
# with the fix on the first line, never a silent pass. (Declared libraries are preflighted
# by the Python side, from the plugin's requirements file.)
here=$(dirname "$0")
if ! command -v python3 >/dev/null 2>&1; then
  echo "BROKEN: const-locations needs python3 — fix: install Python 3.12 or newer (https://www.python.org/downloads/)" >&2
  echo "BROKEN: the command was not granted — the platform asks for it as for any other command" >&2
  exit 1
fi
exec python3 "$here/grant-new-document.py" "$@"
