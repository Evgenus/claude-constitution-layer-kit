#!/bin/sh
# const-meta-types: entry point of the write-time guard. POSIX shell; reads no YAML.
# Finds the Python runtime and PyYAML, then hands over to check-governed-document.py
# with the same arguments and stdin. A missing runtime is a configuration failure:
# exit 1 with the install command, never a silent pass.
here=$(dirname "$0")
if ! command -v python3 >/dev/null 2>&1; then
  echo "BROKEN: const-meta-types needs python3 — install Python 3 (https://www.python.org/downloads/) — until then Markdown writes pass unchecked" >&2
  echo "BROKEN: the check could not run — 0 documents examined" >&2
  exit 1
fi
if ! python3 -c 'import yaml' >/dev/null 2>&1; then
  echo "BROKEN: const-meta-types needs PyYAML — run: python3 -m pip install pyyaml — until then Markdown writes pass unchecked" >&2
  echo "BROKEN: the check could not run — 0 documents examined" >&2
  exit 1
fi
exec python3 "$here/check-governed-document.py" "$@"
